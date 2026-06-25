#!/usr/bin/env python3
"""analyze_optimal_dimension.py — find OUR optimal grid side per circuit and fit a
formula side*(n), from a dimension sweep of our own compiler (no WISQ).

Input: one or more `<bench>_runs.csv` produced by the C++ benchmark on a config whose
only swept axis is `dimension_offset` (x=y=-1 auto-size + offset). See
data/config/dim_opt_cube.json and data/config/dim_opt_connectivity.json. Each row is a
single (circuit, grid) run of OUR compiler with `graph_x`, `routing_steps`,
`non_routed_layer_pct`, `status`, `safe_passage_strategy`.

The idea (the user's framing): routing_steps falls as the grid grows and flattens to a
plateau; a bigger grid past the knee buys almost nothing, and a smaller grid is cheaper
(fewer physical qubits). So per circuit we want the smallest grid that is already within
a tolerance `eps` of the plateau — the elbow. We then fit elbow_side as a function of the
qubit count n, separately per safe_passage strategy (cube / connectivity).

Per circuit, per strategy:
  curve(graph_x) = min routing_steps over successful runs at that grid.
  plateau        = min routing_steps over the swept range (proxy for the large-grid asymptote).
  max_drop       = (steps@smallest_grid - plateau) / steps@smallest_grid   (grid sensitivity).
  elbow(eps)     = smallest graph_x with routing_steps <= plateau*(1+eps).
  clipped        = elbow lands on the largest swept grid AND the curve is still descending
                   there -> the sweep did not reach the plateau, so elbow is a LOWER bound
                   (extend dimension_offset upward and re-run for those circuits).

Circuits split into:
  flat       (max_drop < --flat-threshold): grid does not help; elbow ~ min feasible grid.
  sensitive  (otherwise):                   grid genuinely reduces routing_steps.

Fit (least squares) of  side*(n) = a*sqrt(n) + b  for each strategy and each eps, on
  - ALL circuits          (operational: the formula must size every circuit), and
  - sensitive-only        (the meaningful elbow, undiluted by flat families), and
  - an UPPER ENVELOPE     (per-n high quantile of the elbow, so the formula does not
                           starve the hardest circuit at each n).
Each fit is also re-expressed as  c*ceil(sqrt(n)) + k  to compare with WISQ's native
side = 2*ceil(sqrt(n)) + 3.

Outputs (under --output-dir):
  <strategy>_elbow_per_circuit.csv   one row per circuit (n, min feasible, plateau,
                                     max_drop, sensitive, clipped, elbow@each eps,
                                     non_routed@elbow).
  optimal_dimension_report.md        the fitted formulas, R^2, per-family summary, and
                                     the recommended side*(n) per strategy.

Usage:
  python scripts/analyze_optimal_dimension.py \
      benchmarks/results/dim_opt_cube_runs.csv \
      benchmarks/results/dim_opt_connectivity_runs.csv \
      --output-dir metric_analysis_outcomes/optimal_dimension
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UNIVERSAL_QASMS_DIR = REPO_ROOT / "universal_set_qasms"
QASMS_DIR = REPO_ROOT / "qasms"

_CX_RE = re.compile(r"\bcx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\]\s*;")
_T_RE = re.compile(r"\b(?:t|tdg)\s+q\[(\d+)\]\s*;")
_QREG_RE = re.compile(r"qreg\s+\w+\[(\d+)\]")


# ── qubit-count sourcing ──────────────────────────────────────────────────────────

def _distinct_qubits(path: Path) -> int | None:
    """Distinct qubits used in cx/t/tdg gates (== the count the grid auto-sizer uses);
    falls back to the qreg declaration if no two-qubit/T gate is present."""
    if not path.exists():
        return None
    text = path.read_text()
    qubits: set[int] = set()
    for line in text.splitlines():
        m = _CX_RE.search(line)
        if m:
            qubits.add(int(m.group(1)))
            qubits.add(int(m.group(2)))
            continue
        m = _T_RE.search(line)
        if m:
            qubits.add(int(m.group(1)))
    if qubits:
        return len(qubits)
    qm = _QREG_RE.search(text)
    return int(qm.group(1)) if qm else None


def build_qubit_map(qubits_csv: list[Path]) -> dict[str, int]:
    """circuit -> n. A --qubits-csv reference (columns circuit + n_qubits/num_qubits)
    overrides; otherwise n is computed lazily from the universal/input QASM in resolve_n."""
    n_by_circuit: dict[str, int] = {}
    for ref in qubits_csv:
        if not ref.exists():
            print(f"  WARNING: --qubits-csv not found: {ref}", file=sys.stderr)
            continue
        with ref.open(newline="") as f:
            reader = csv.DictReader(f)
            col = next((c for c in ("n_qubits", "num_qubits", "num_logical_qubits")
                        if c in (reader.fieldnames or [])), None)
            if col is None:
                print(f"  WARNING: no qubit column in {ref}", file=sys.stderr)
                continue
            for row in reader:
                c = row.get("circuit")
                v = row.get(col, "")
                if c and str(v).strip():
                    try:
                        n_by_circuit[c] = int(float(v))
                    except ValueError:
                        pass
    return n_by_circuit


def resolve_n(circuit: str, ref_map: dict[str, int]) -> int | None:
    if circuit in ref_map:
        return ref_map[circuit]
    n = _distinct_qubits(UNIVERSAL_QASMS_DIR / f"{circuit}_universal.qasm")
    if n is not None:
        return n
    return _distinct_qubits(QASMS_DIR / f"{Path(circuit).stem}.qasm")


# ── curve loading ─────────────────────────────────────────────────────────────────

def load_curves(csv_paths: list[Path]):
    """Returns strat -> circuit -> {graph_x: min routing_steps} and a parallel
    strat -> circuit -> {graph_x: non_routed_layer_pct} (min routing_steps wins ties)."""
    steps = defaultdict(lambda: defaultdict(dict))
    nonrouted = defaultdict(lambda: defaultdict(dict))
    n_rows = n_ok = 0
    for path in csv_paths:
        if not path.exists():
            print(f"  WARNING: input not found: {path}", file=sys.stderr)
            continue
        with path.open(newline="") as f:
            for r in csv.DictReader(f):
                n_rows += 1
                if r.get("status") != "success":
                    continue
                try:
                    gx = int(r["graph_x"])
                    st = int(r["routing_steps"])
                except (ValueError, KeyError, TypeError):
                    continue
                strat = r.get("safe_passage_strategy") or "unknown"
                c = r["circuit"]
                cur = steps[strat][c]
                if gx not in cur or st < cur[gx]:
                    cur[gx] = st
                    try:
                        nonrouted[strat][c][gx] = float(r.get("non_routed_layer_pct", "") or "nan")
                    except ValueError:
                        nonrouted[strat][c][gx] = float("nan")
                n_ok += 1
    print(f"Loaded {n_rows} rows ({n_ok} successful) from {len(csv_paths)} file(s).",
          file=sys.stderr)
    return steps, nonrouted


# ── elbow per circuit ─────────────────────────────────────────────────────────────

def elbow_for_curve(curve: dict[int, int], eps: float) -> tuple[int, bool]:
    """Smallest grid side within (1+eps) of the plateau. Returns (elbow_side, clipped)."""
    gxs = sorted(curve)
    plateau = min(curve[g] for g in gxs)
    thr = plateau * (1 + eps)
    elbow = next(g for g in gxs if curve[g] <= thr)
    # clipped: the band is first reached only at the top grid, and steps are still
    # strictly falling between the two largest grids -> plateau not reached.
    clipped = (elbow == gxs[-1] and len(gxs) >= 2 and curve[gxs[-1]] < curve[gxs[-2]])
    return elbow, clipped


def analyze_strategy(steps, nonrouted, ref_map, eps_list, flat_threshold):
    """Per-circuit elbow records for one strategy."""
    records = []
    for circuit, curve in steps.items():
        if len(curve) < 2:
            continue
        n = resolve_n(circuit, ref_map)
        if not n:
            print(f"  WARNING: no qubit count for {circuit}; skipped.", file=sys.stderr)
            continue
        gxs = sorted(curve)
        plateau = min(curve[g] for g in gxs)
        steps_at_floor = curve[gxs[0]]
        max_drop = (steps_at_floor - plateau) / steps_at_floor if steps_at_floor > 0 else 0.0
        sensitive = max_drop >= flat_threshold
        rec = {
            "circuit": circuit,
            "n": n,
            "min_feasible_side": gxs[0],
            "max_swept_side": gxs[-1],
            "plateau_steps": plateau,
            "steps_at_min_grid": steps_at_floor,
            "max_drop_pct": round(max_drop * 100, 2),
            "sensitive": sensitive,
        }
        for eps in eps_list:
            elbow, clipped = elbow_for_curve(curve, eps)
            tag = f"{int(eps*100)}"
            rec[f"elbow_e{tag}"] = elbow
            rec[f"clipped_e{tag}"] = clipped
            nr = nonrouted[circuit].get(elbow, float("nan"))
            rec[f"nonrouted_e{tag}"] = round(nr, 3) if nr == nr else ""
        records.append(rec)
    records.sort(key=lambda r: r["n"])
    return records


# ── fitting ───────────────────────────────────────────────────────────────────────

def fit_sqrt(points: list[tuple[float, float]]):
    """Least squares side = a*sqrt(n) + b over (n, side). Returns (a, b, r2, N)."""
    if len(points) < 2:
        return None
    xs = [math.sqrt(n) for n, _ in points]
    ys = [s for _, s in points]
    N = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = N * sxx - sx * sx
    if denom == 0:
        return None
    a = (N * sxy - sx * sy) / denom
    b = (sy - a * sx) / N
    ybar = sy / N
    ss_tot = sum((y - ybar) ** 2 for y in ys)
    ss_res = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot else 1.0
    return a, b, r2, N


def envelope_points(records, eps_tag, quantile):
    """Per distinct n, the `quantile` of the elbow across circuits at that n."""
    by_n = defaultdict(list)
    for r in records:
        by_n[r["n"]].append(r[f"elbow_e{eps_tag}"])
    pts = []
    for n, vals in by_n.items():
        vals.sort()
        idx = min(len(vals) - 1, int(math.ceil(quantile * len(vals)) - 1))
        idx = max(0, idx)
        pts.append((n, vals[idx]))
    return pts


def fmt_fit(fit, eps=None):
    if fit is None:
        return "n/a (too few points)"
    a, b, r2, N = fit
    c = a / 2.0  # coefficient on ceil(sqrt(n)) ~ a*sqrt(n) = (a/2)*(2*sqrt(n))
    sign = "+" if b >= 0 else "-"
    return (f"side*(n) = {a:.3f}*sqrt(n) {sign} {abs(b):.2f}"
            f"   [~{a:.2f}*ceil(sqrt(n)) {sign} {abs(b):.1f}]   R^2={r2:.3f}  (N={N})")


# ── family summary ────────────────────────────────────────────────────────────────

def family_of(circuit: str) -> str:
    m = re.match(r"([a-zA-Z_]+?)(?:_?n?\d+)", circuit)
    return m.group(1).rstrip("_") if m else circuit


# ── report ────────────────────────────────────────────────────────────────────────

def write_report(out_dir: Path, per_strategy, eps_list, quantile, flat_threshold):
    lines = []
    lines.append("# Formula della dimensione ottima (solo nostro codice)\n")
    lines.append(
        "Ginocchio dei `routing_steps` vs lato-griglia per circuito, poi fit "
        "`side*(n) = a·√n + b` per strategia. `eps` = quanto degrado di routing_steps "
        "accetti rispetto al plateau in cambio di una griglia più piccola "
        "(eps piccolo → griglia più grande, più vicina al minimo step).\n")
    lines.append(f"- Riferimento WISQ-native: `side = 2·⌈√n⌉ + 3`.\n")
    lines.append(f"- `flat` = circuiti dove il grid non aiuta (max_drop < {flat_threshold*100:.0f}%): "
                 "il loro ottimo è la griglia minima fattibile.\n")
    lines.append(f"- Envelope = per ogni n, il {quantile*100:.0f}° percentile del ginocchio "
                 "(formula che non affama il circuito più duro a quel n).\n")

    for strat, records in per_strategy.items():
        if not records:
            continue
        n_sens = sum(1 for r in records if r["sensitive"])
        n_clip = sum(1 for r in records if any(r.get(f"clipped_e{int(e*100)}") for e in eps_list))
        lines.append(f"\n## {strat}  ({len(records)} circuiti, {n_sens} grid-sensitive, "
                     f"{len(records)-n_sens} flat)\n")
        if n_clip:
            lines.append(f"> ⚠ {n_clip} circuiti hanno il ginocchio sul lato massimo sweepato "
                         "(curva ancora in discesa): per quelli la formula è un **lower bound**, "
                         "estendi `dimension_offset` verso l'alto e rilancia.\n")
        lines.append("\n| eps | fit (tutti) | fit (solo sensitive) | fit (envelope) |")
        lines.append("|-----|-------------|----------------------|----------------|")
        for eps in eps_list:
            tag = int(eps * 100)
            all_pts = [(r["n"], r[f"elbow_e{tag}"]) for r in records]
            sens_pts = [(r["n"], r[f"elbow_e{tag}"]) for r in records if r["sensitive"]]
            env_pts = envelope_points(records, tag, quantile)
            lines.append(f"| {tag}% | {fmt_fit(fit_sqrt(all_pts))} "
                         f"| {fmt_fit(fit_sqrt(sens_pts))} "
                         f"| {fmt_fit(fit_sqrt(env_pts))} |")

        # Per-family elbow (at the middle eps) to show where the grid really matters.
        mid_eps = eps_list[len(eps_list) // 2]
        tag = int(mid_eps * 100)
        fam = defaultdict(list)
        for r in records:
            fam[family_of(r["circuit"])].append(r)
        lines.append(f"\n### Per famiglia (eps={tag}%, solo famiglie grid-sensitive)\n")
        lines.append("| family | n circ | n range | max_drop med | elbow/√n med |")
        lines.append("|--------|--------|---------|--------------|--------------|")
        for f, rs in sorted(fam.items()):
            if not any(r["sensitive"] for r in rs):
                continue
            ns = [r["n"] for r in rs]
            drops = sorted(r["max_drop_pct"] for r in rs)
            ratios = sorted(r[f"elbow_e{tag}"] / math.sqrt(r["n"]) for r in rs)
            med = lambda v: v[len(v)//2]
            lines.append(f"| {f} | {len(rs)} | {min(ns)}–{max(ns)} "
                         f"| {med(drops):.0f}% | {med(ratios):.2f} |")

    report = "\n".join(lines) + "\n"
    (out_dir / "optimal_dimension_report.md").write_text(report)
    return report


def write_per_circuit_csv(out_dir: Path, strat: str, records, eps_list):
    if not records:
        return
    cols = ["circuit", "n", "min_feasible_side", "max_swept_side",
            "steps_at_min_grid", "plateau_steps", "max_drop_pct", "sensitive"]
    for eps in eps_list:
        tag = int(eps * 100)
        cols += [f"elbow_e{tag}", f"clipped_e{tag}", f"nonrouted_e{tag}"]
    path = out_dir / f"{strat}_elbow_per_circuit.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k, "") for k in cols})
    print(f"  wrote {path}", file=sys.stderr)


# ── main ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs_csv", nargs="+", help="One or more <bench>_runs.csv files.")
    ap.add_argument("--output-dir", default="metric_analysis_outcomes/optimal_dimension",
                    help="Directory for the report + per-circuit CSVs.")
    ap.add_argument("--eps", type=float, nargs="+", default=[0.02, 0.05, 0.10],
                    help="Tolerance(s) to the plateau for the elbow (default 0.02 0.05 0.10).")
    ap.add_argument("--flat-threshold", type=float, default=0.05,
                    help="Below this max_drop a circuit is 'flat' (grid does not help). Default 0.05.")
    ap.add_argument("--quantile", type=float, default=0.90,
                    help="Per-n quantile for the envelope fit (default 0.90).")
    ap.add_argument("--qubits-csv", nargs="*", default=[],
                    help="Optional CSV(s) with circuit + n_qubits to override qubit counting.")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_map = build_qubit_map([Path(p) for p in args.qubits_csv])
    steps, nonrouted = load_curves([Path(p) for p in args.runs_csv])
    if not steps:
        print("No usable rows.", file=sys.stderr)
        return 1

    per_strategy = {}
    for strat in sorted(steps):
        records = analyze_strategy(steps[strat], nonrouted[strat], ref_map,
                                   args.eps, args.flat_threshold)
        per_strategy[strat] = records
        write_per_circuit_csv(out_dir, strat, records, args.eps)

    report = write_report(out_dir, per_strategy, args.eps, args.quantile, args.flat_threshold)
    print("\n" + report)
    print(f"Report + CSVs in {out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
