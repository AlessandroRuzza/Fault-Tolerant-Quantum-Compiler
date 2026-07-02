#!/usr/bin/env python3
"""compare_random.py — random/cube vs WISQ and random vs cube, ALL at WISQ's native grid.

Why this script exists
-----------------------
The WISQ-native baseline (WISQ on its own square_sparse_layout grid,
side = 2*ceil(sqrt(n))+3) depends ONLY on the circuit, not on which of OUR
strategies it is paired with. It is therefore already computed and stored in
benchmarks/results/connectivity_summary_all_wisq.csv (that file was produced with
compare_wisq_2 --wisq-native, so my_x == wisq_x == native side per row). We reuse
that WISQ column verbatim — WISQ does NOT need to be re-run.

So to add a `random` baseline and a same-grid `random vs cube` comparison we only
have to run OUR compiler at the native grid for the two strategies. No WISQ runs.

Two subcommands
---------------
  run     For every (circuit, combo) in a bench config, run OUR compiler forced onto
          WISQ's RECORDED grid — wisq_x/wisq_y read verbatim from the baseline CSV
          (--grid-from) — and record routing steps. This guarantees the dimension
          equals WISQ's by construction (do NOT recompute it: the input-qasm qubit
          count and WISQ's universal-qasm count disagree for ~8 circuits, so a
          recomputed side would be wrong, e.g. bv_n280 37 vs 29, bigadder_n18 7 vs 13).
          Writes an "ours-only" CSV (no WISQ). Resume- and cluster-shard-safe.

  report  Join the ours-only CSV to the WISQ-native baseline and emit two comparisons
          as Markdown + merged CSV:
            * <strategy> vs WISQ   (both at the native grid)
            * random vs cube        (both at the native grid)
          A row's strategy is `random` when type==random, else `cube`
          (safe_passage_strategy==cube). Lower routing_steps = better.

Typical use
-----------
  # 1. (cluster) run both strategies at the native grid, no WISQ:
  python scripts/wisq_compare/compare_random.py run \
      --bench config/random_cube_native.json \
      -o benchmarks/results/random_cube_native_ours.csv --workers 28

  # 2. build the reports, reusing the existing WISQ-native column:
  python scripts/wisq_compare/compare_random.py report \
      --ours benchmarks/results/random_cube_native_ours.csv \
      --wisq-baseline benchmarks/results/connectivity_summary_all_wisq.csv \
      --out-dir results/
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import json
import math
import sys
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_wisq_2 as cw2  # noqa: E402
import compare_wisq_mingrid as cw3   # noqa: E402  (run_compiler_at: explicit-grid runner)

DEFAULT_BINARY = cw2.DEFAULT_BINARY
DEFAULT_BASELINE = cw2.REPO_ROOT / "benchmarks" / "results" / "connectivity_summary_all_wisq.csv"

# Ours-only CSV: circuit identity + the config knobs + OUR result at the native grid.
OURS_COLUMNS = (
    ["circuit", "n_qubits"]
    + cw2.CONFIG_FIELDS
    + ["my_x", "my_y", "my_routing_steps", "my_duration_s", "status", "safe_passage_fallback"]
)

_csv_write_lock = threading.Lock()


def strategy_of(row: dict) -> str:
    """`random` if the mapping type is random, else `cube` (the gaussian+cube baseline)."""
    return "random" if str(row.get("type", "")).strip() == "random" else "cube"


# ── run: OUR compiler at WISQ's RECORDED grid, no WISQ ────────────────────────────

def load_grid_map(path: Path) -> dict[str, tuple[int, int]]:
    """circuit -> (wisq_x, wisq_y): WISQ's ACTUAL grid, read verbatim from a baseline
    CSV. We force our compiler onto exactly this grid, so the dimension matches WISQ
    by construction (do NOT recompute it from a qubit count — the input-qasm count and
    WISQ's universal-qasm count disagree for ~8 circuits, e.g. bv_n280, bigadder_n18)."""
    m: dict[str, tuple[int, int]] = {}
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            try:
                m[r["circuit"]] = (int(r["wisq_x"]), int(r["wisq_y"]))
            except (KeyError, ValueError, TypeError):
                continue
    return m


def run_combo(circuit: str, cfg: dict, binary: Path, grid: tuple[int, int]) -> dict:
    """Run OUR compiler for one (circuit, cfg) forced onto WISQ's recorded grid `grid`.

    Mirrors compare_wisq_2.run_compiler's cube→connectivity fallback: a cube run can
    fail to MAP on the (tight) WISQ grid; we retry once at the SAME grid with the
    connectivity config so the dimension is preserved. WISQ is never invoked here.
    """
    x, y = grid
    n_in, _ = cw2._input_qasm_qubits_and_t(circuit)
    row = {
        "circuit": circuit,
        "n_qubits": cw2.count_qasm_qubits(circuit) or n_in or "",
        **cw2.cfg_fields(cfg),
        "my_x": x, "my_y": y, "my_routing_steps": "", "my_duration_s": "",
        "status": "error", "safe_passage_fallback": "",
    }
    ok, mine = cw3.run_compiler_at(circuit, cfg, binary, x, y, None)
    fb = ""
    if not ok and cfg.get("safe_passage_strategy") == "cube":
        ok, mine = cw3.run_compiler_at(
            circuit, {**cfg, **cw2.CONNECTIVITY_FALLBACK_OVERRIDES}, binary, x, y, None)
        fb = "connectivity" if ok else "connectivity(failed)"
    if ok:
        row.update({
            "my_x": mine["width"], "my_y": mine["height"],
            "my_routing_steps": mine["routing_steps"],
            "my_duration_s": (f'{mine["duration_seconds"]:.6f}'
                              if mine["duration_seconds"] is not None else ""),
            "status": "success", "safe_passage_fallback": fb,
        })
        if not row["n_qubits"]:
            row["n_qubits"] = mine.get("num_qubits") or ""
    else:
        row["safe_passage_fallback"] = fb
        print(f"  ERROR [{circuit}/{strategy_of(row)}]: no routing result at {x}x{y}",
              file=sys.stderr)
    return {k: row.get(k, "") for k in OURS_COLUMNS}


def load_done_keys(path: Path) -> set[tuple]:
    """(circuit, type, safe_passage_strategy) pairs already present with a result."""
    if not path.exists():
        return set()
    done: set[tuple] = set()
    try:
        with path.open(newline="") as f:
            for r in csv.DictReader(f):
                if str(r.get("my_routing_steps", "")).strip():
                    done.add((r["circuit"], r.get("type", ""), r.get("safe_passage_strategy", "")))
    except Exception:
        pass
    return done


def cmd_run(args: argparse.Namespace) -> int:
    binary = Path(args.binary)
    if not binary.exists():
        print(f"ERROR: compiler binary not found: {binary}", file=sys.stderr)
        return 1

    grid_map = load_grid_map(Path(args.grid_from))
    print(f"Loaded {len(grid_map)} circuit grids from {Path(args.grid_from).name} "
          f"(forcing our compiler onto WISQ's recorded grid).", file=sys.stderr)

    source = json.loads(Path(args.bench).read_text())
    combos = [c for c in cw2.expand_config_variants(source) if c.get("circuit")]
    # Group by circuit so a worker owns a circuit (the compiler writes a fixed graph path).
    by_circuit: "OrderedDict[str, list[dict]]" = OrderedDict()
    for cfg in combos:
        by_circuit.setdefault(cfg["circuit"], []).append(cfg)
    circuits = list(by_circuit.keys())
    missing = [c for c in circuits if c not in grid_map]
    if missing:
        print(f"WARNING: {len(missing)} circuits have no WISQ grid in "
              f"{Path(args.grid_from).name} and will be SKIPPED: {missing[:10]}",
              file=sys.stderr)
        circuits = [c for c in circuits if c in grid_map]
    print(f"Expanded to {len(combos)} (circuit, combo) over {len(circuits)} circuits "
          f"with a known WISQ grid (our compiler forced to that grid; no WISQ runs).",
          file=sys.stderr)
    if args.dry_run:
        for c in circuits:
            strategies = ", ".join(strategy_of(x) for x in by_circuit[c])
            print(f"  {c}  grid={grid_map[c][0]}x{grid_map[c][1]}: {strategies}")
        return 0

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_keys(out_path)
    if done:
        print(f"Resuming: {len(done)} (circuit, strategy) results already present.", file=sys.stderr)

    todo = [
        (i, c) for i, c in enumerate(circuits)
        if args.process_count <= 1 or i % args.process_count == args.processor
    ]
    print(f"Circuits for this process: {len(todo)}.", file=sys.stderr)

    csv_file = out_path.open("a", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=OURS_COLUMNS)
    with _csv_write_lock:
        fcntl.flock(csv_file, fcntl.LOCK_EX)
        try:
            if out_path.stat().st_size == 0:
                writer.writeheader()
                csv_file.flush()
        finally:
            fcntl.flock(csv_file, fcntl.LOCK_UN)

    completed = 0

    def _emit(row: dict) -> None:
        nonlocal completed
        completed += 1
        with _csv_write_lock:
            fcntl.flock(csv_file, fcntl.LOCK_EX)
            try:
                writer.writerow(row)
                csv_file.flush()
            finally:
                fcntl.flock(csv_file, fcntl.LOCK_UN)
        print(f"[{completed}] {row['circuit']:30s} {strategy_of(row):7s} "
              f"grid={row['my_x']}x{row['my_y']} steps={row['my_routing_steps']} "
              f"status={row['status']}", file=sys.stderr)

    def _process(circuit: str) -> list[dict]:
        out = []
        for cfg in by_circuit[circuit]:
            key = (circuit, cfg.get("type", ""), cfg.get("safe_passage_strategy", ""))
            if key in done:
                continue
            out.append(run_combo(circuit, cfg, binary, grid_map[circuit]))
        return out

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(_process, c): c for _, c in todo}
            for fut in as_completed(futures):
                for row in fut.result():
                    _emit(row)
    else:
        for _, c in todo:
            for row in _process(c):
                _emit(row)

    csv_file.close()
    print(f"\nOurs-only CSV written/appended to {out_path}")
    return 0


# ── report: join to the WISQ-native baseline, emit comparisons ────────────────────

def _int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def load_ours(path: Path) -> dict[tuple, dict]:
    """(circuit, strategy) -> row, keeping the last successful result per key."""
    out: dict[tuple, dict] = {}
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            out[(r["circuit"], strategy_of(r))] = r
    return out


def load_wisq_baseline(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            out[r["circuit"]] = r
    return out


def _verdict(mine: int | None, other: int | None) -> str:
    if mine is None or other is None:
        return "n/a"
    if mine < other:
        return "WIN"      # we use fewer routing steps
    if mine > other:
        return "LOSS"
    return "TIE"


def build_comparison(rows: list[dict], a_label: str, b_label: str) -> tuple[list[dict], dict]:
    """rows: each {circuit, n_qubits, grid, a_steps, b_steps, a_status, b_status}.
    Returns (per-circuit rows with verdict+ratio, summary counts)."""
    out = []
    counts = {"WIN": 0, "LOSS": 0, "TIE": 0, "n/a": 0}
    for r in rows:
        v = _verdict(r["a_steps"], r["b_steps"])
        counts[v] += 1
        ratio = (r["b_steps"] / r["a_steps"]) if (r["a_steps"] and r["b_steps"]) else None
        out.append({**r, "verdict": v, f"{b_label}_over_{a_label}": ratio})
    return out, counts


def render_md(title: str, a_label: str, b_label: str, rows: list[dict], counts: dict,
              note: str) -> str:
    n = len(rows)
    decided = counts["WIN"] + counts["LOSS"] + counts["TIE"]
    ratios = [r[f"{b_label}_over_{a_label}"] for r in rows if r[f"{b_label}_over_{a_label}"]]
    geomean = (math.exp(sum(math.log(x) for x in ratios) / len(ratios)) if ratios else None)
    lines = [
        f"# {title}",
        "",
        note,
        "",
        f"- Circuits: **{n}**  (decided: {decided}, n/a: {counts['n/a']})",
        f"- `{a_label}` WIN (fewer routing steps): **{counts['WIN']}**  "
        f"LOSS: **{counts['LOSS']}**  TIE: **{counts['TIE']}**",
        (f"- Geomean `{b_label}/{a_label}` routing-step ratio (>1 ⇒ {a_label} better): "
         f"**{geomean:.3f}**" if geomean else "- Geomean ratio: n/a"),
        "",
        f"| circuit | n_qubits | grid | {a_label} steps | {b_label} steps | "
        f"{b_label}/{a_label} | verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda x: (x["n_qubits"] or 0, x["circuit"])):
        ratio = r[f"{b_label}_over_{a_label}"]
        lines.append(
            f"| {r['circuit']} | {r['n_qubits'] or ''} | {r['grid']} | "
            f"{r['a_steps'] if r['a_steps'] is not None else ''} | "
            f"{r['b_steps'] if r['b_steps'] is not None else ''} | "
            f"{ratio:.3f} | {r['verdict']} |" if ratio is not None else
            f"| {r['circuit']} | {r['n_qubits'] or ''} | {r['grid']} | "
            f"{r['a_steps'] if r['a_steps'] is not None else ''} | "
            f"{r['b_steps'] if r['b_steps'] is not None else ''} |  | {r['verdict']} |"
        )
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    cols = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def cmd_report(args: argparse.Namespace) -> int:
    ours = load_ours(Path(args.ours))
    wisq = load_wisq_baseline(Path(args.wisq_baseline))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    circuits = sorted({c for (c, _) in ours})
    rnd_vs_wisq, cube_vs_wisq, rnd_vs_cube = [], [], []
    mismatched_grid = []

    for c in circuits:
        rnd = ours.get((c, "random"))
        cube = ours.get((c, "cube"))
        w = wisq.get(c)
        n = _int((rnd or cube or {}).get("n_qubits")) or (_int(w.get("n_qubits")) if w else None)
        # WISQ's recorded grid is authoritative; our runs were forced onto it.
        wx = _int(w.get("wisq_x")) if w else None
        wy = _int(w.get("wisq_y")) if w else None
        grid = f"{wx}x{wy}" if wx else "?"

        r_steps = _int(rnd["my_routing_steps"]) if rnd else None
        c_steps = _int(cube["my_routing_steps"]) if cube else None
        w_steps = _int(w["wisq_routing_steps"]) if w else None
        w_status = w.get("wisq_status", "") if w else "missing"

        # Sanity: our forced grid must equal WISQ's recorded grid (else not same-grid).
        for tag, side in (("random", rnd), ("cube", cube)):
            if side and wx is not None and _int(side.get("my_x")) != wx:
                mismatched_grid.append((c, tag, side.get("my_x"), wx))

        if rnd is not None and w is not None:
            rnd_vs_wisq.append({"circuit": c, "n_qubits": n, "grid": grid,
                                "a_steps": r_steps, "b_steps": w_steps,
                                "wisq_status": w_status})
        if cube is not None and w is not None:
            cube_vs_wisq.append({"circuit": c, "n_qubits": n, "grid": grid,
                                 "a_steps": c_steps, "b_steps": w_steps,
                                 "wisq_status": w_status})
        if rnd is not None and cube is not None:
            rnd_vs_cube.append({"circuit": c, "n_qubits": n, "grid": grid,
                                "a_steps": r_steps, "b_steps": c_steps})

    artifacts = []
    note_native = ("Both sides evaluated on WISQ's own grid (wisq_x/wisq_y), reused "
                   f"verbatim from `{Path(args.wisq_baseline).name}` — our compiler was "
                   "forced onto exactly that grid, WISQ was NOT re-run (its native grid "
                   "is strategy-independent). Lower routing_steps is better.")

    if rnd_vs_wisq:
        rows, counts = build_comparison(rnd_vs_wisq, "random", "wisq")
        (out_dir / "random_vs_wisq_results.md").write_text(
            render_md("random vs WISQ (WISQ grid)", "random", "wisq", rows, counts, note_native))
        write_csv(out_dir / "random_vs_wisq.csv", rows)
        artifacts += ["random_vs_wisq_results.md", "random_vs_wisq.csv"]

    if rnd_vs_cube:
        rows, counts = build_comparison(rnd_vs_cube, "random", "cube")
        (out_dir / "random_vs_cube_results.md").write_text(
            render_md("random vs cube (WISQ grid)", "random", "cube", rows, counts,
                      "Both run by OUR compiler on WISQ's grid (same grid per circuit). "
                      "Lower routing_steps is better."))
        write_csv(out_dir / "random_vs_cube.csv", rows)
        artifacts += ["random_vs_cube_results.md", "random_vs_cube.csv"]

    if cube_vs_wisq:  # bonus: cube re-measured at WISQ's grid vs WISQ
        rows, counts = build_comparison(cube_vs_wisq, "cube", "wisq")
        (out_dir / "cube_native_vs_wisq_results.md").write_text(
            render_md("cube vs WISQ (WISQ grid)", "cube", "wisq", rows, counts, note_native))
        artifacts += ["cube_native_vs_wisq_results.md"]

    if mismatched_grid:
        print(f"WARNING: {len(mismatched_grid)} (circuit, strategy) ran on a grid that "
              f"differs from WISQ's recorded grid (not same-grid), e.g. "
              f"{mismatched_grid[:5]}", file=sys.stderr)

    print("Wrote:")
    for a in artifacts:
        print(f"  {out_dir / a}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="Run OUR compiler at WISQ's recorded grid (no WISQ).")
    pr.add_argument("--bench", required=True, help="Sweep config (JSON).")
    pr.add_argument("--output", "-o", required=True, help="Ours-only CSV (append/resume).")
    pr.add_argument("--grid-from", default=str(DEFAULT_BASELINE),
                    help="Baseline CSV providing WISQ's grid (wisq_x/wisq_y) per circuit; "
                         f"our compiler is forced onto it (default: {DEFAULT_BASELINE.name}).")
    pr.add_argument("--binary", default=str(DEFAULT_BINARY))
    pr.add_argument("--workers", type=int, default=1)
    pr.add_argument("--process-count", type=int, default=1)
    pr.add_argument("--processor", type=int, default=0)
    pr.add_argument("--dry-run", action="store_true")
    pr.set_defaults(func=cmd_run)

    pp = sub.add_parser("report", help="Join to WISQ-native baseline, emit comparisons.")
    pp.add_argument("--ours", required=True, help="Ours-only CSV from `run`.")
    pp.add_argument("--wisq-baseline", default=str(DEFAULT_BASELINE),
                    help=f"WISQ-native baseline CSV (default: {DEFAULT_BASELINE.name})")
    pp.add_argument("--out-dir", default="results")
    pp.set_defaults(func=cmd_report)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
