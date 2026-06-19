#!/usr/bin/env python3
"""Plot per-circuit comparison between our runs and WISQ, from TWO separate CSVs.

Same output as plot_wisq_comparison.py (one figure per circuit: routing steps and
wall-clock time for best config / worst config / WISQ, plus two cross-circuit
summary figures) — but the data comes from two files joined on `circuit`:

  1. WISQ_CSV  — a WISQ-only table as produced by extract_wisq.py
                 (columns: circuit, n_qubits, wisq_x, wisq_y, wisq_routing_steps,
                  wisq_duration_s, wisq_status, ...). One row per circuit.
  2. RUNS_CSV  — our benchmark runs CSV (e.g. data/old_results/.../*_runs.csv;
                 columns: circuit, graph_x, graph_y, routing_strategy, ...,
                 routing_steps, status, duration_seconds, ...). Many rows per
                 circuit (one per config); best/worst are picked from these.

Only circuits present in BOTH files (with a successful WISQ result and at least
one successful run) are plotted.

Best/worst are chosen by our routing_steps (tiebreak: duration_seconds).
Plots are saved to data/results/wisq_plots2/.

Usage:
    python scripts/plot_wisq_comparison2.py data/best_wisq_per_circuit.csv \
        data/old_results/old_results_11june/t_prop_circuits_runs.csv
    python scripts/plot_wisq_comparison2.py WISQ_CSV RUNS_CSV --output data/results/wisq_plots2
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "results" / "wisq_plots2"

# Runs-CSV column names (our execution).
RUNS_STEPS = "routing_steps"
RUNS_TIME = "duration_seconds"
RUNS_X = "graph_x"
RUNS_Y = "graph_y"
RUNS_STATUS = "status"
RUNS_MIN_STEPS = "min_routing_steps"
RUNS_PARALLELISM = "max_parallelism"
RUNS_DENSITY = "cnot_interaction_density"

# CNOT interaction-graph characterization metrics (columns added to the runs CSV
# by the "Add more circuit metrics to csv output" change). Each becomes an
# optimality-vs-metric scatter, the same way density already was.
# (runs-CSV column, x-axis label, title phrase, filename slug). The density entry
# keeps the legacy "circuit_density" slug so its filename does not change.
CNOT_GRAPH_METRIC_SPECS = [
    (RUNS_DENSITY, "circuit density (unique CNOT pairs / max pairs)", "Circuit Density", "circuit_density"),
    ("cnot_graph_modularity", "CNOT graph modularity (community structure)", "CNOT Graph Modularity", "cnot_graph_modularity"),
    ("cnot_graph_diameter", "CNOT graph diameter (max hop distance)", "CNOT Graph Diameter", "cnot_graph_diameter"),
    ("cnot_graph_avg_shortest_path", "CNOT graph avg shortest path (hops)", "CNOT Graph Avg Shortest Path", "cnot_graph_avg_shortest_path"),
    ("max_cnot_degree", "max CNOT degree (busiest qubit)", "Max CNOT Degree", "max_cnot_degree"),
    ("min_cnot_degree", "min CNOT degree (over qubits with a CNOT)", "Min CNOT Degree", "min_cnot_degree"),
    ("avg_cnot_degree", "avg CNOT degree", "Avg CNOT Degree", "avg_cnot_degree"),
    ("cnot_degree_gini", "CNOT degree Gini (degree inequality)", "CNOT Degree Gini", "cnot_degree_gini"),
    ("cnot_pair_rep_gini", "CNOT pair-repetition Gini (interaction skew)", "CNOT Pair-Repetition Gini", "cnot_pair_rep_gini"),
    ("cnot_edge_weight_stddev", "CNOT edge-weight stddev (adjacency std)", "CNOT Edge-Weight Stddev", "cnot_edge_weight_stddev"),
    ("cnot_graph_clustering_coeff", "CNOT graph clustering coefficient", "CNOT Graph Clustering Coeff", "cnot_graph_clustering_coeff"),
]

# Config fields used for the best/worst bar label, mapped to the runs-CSV names.
CONFIG_LABEL_FIELDS = [
    ("mapping_type", {"gaussian": "gauss", "magic_aware": "magic", "homogeneous": "homo"}),
    ("gaussian_strategy", {"coarse": "coarse", "fine": "fine"}),
    ("safe_passage_strategy", {"cube": "cube", "connectivity": "conn", "passage_no_subgraphs": "pass"}),
    ("routing_strategy", {"naive": "naive", "congestion": "cong"}),
    ("t_routing_mode", {"normal_t_routing": "nT", "smart_t_routing": "sT"}),
    ("border_distance_percentage", {}),
]


def to_float(v) -> float | None:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def circuit_family(name: str) -> str:
    """Group key for a circuit: strip the trailing size token.
    qft_n50 -> qft, vqe_su2_n100 -> vqe_su2, qft_20 -> qft, adder_n64_transpiled -> adder."""
    base = re.sub(r"_n\d+.*$", "", name)   # drop _n<size> (and any suffix like _transpiled)
    base = re.sub(r"_\d+$", "", base)       # drop a bare _<size> (e.g. qft_20)
    return base or name


def config_label(row: dict) -> str:
    parts = []
    for field, abbrev in CONFIG_LABEL_FIELDS:
        val = (row.get(field) or "").strip()
        if not val:
            continue
        parts.append(abbrev.get(val, val))
    return "/".join(parts) if parts else "?"


def load_wisq(path: Path) -> dict[str, dict]:
    """circuit -> wisq row (success only, numeric wisq_routing_steps). One per circuit."""
    by_circuit: dict[str, dict] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            status = (row.get("wisq_status") or "").strip()
            if status and status != "success":
                continue
            if to_float(row.get("wisq_routing_steps")) is None:
                continue
            by_circuit[row["circuit"].strip()] = row
    return by_circuit


def load_runs(path: Path) -> dict[str, list[dict]]:
    """circuit -> list of our run rows (status=success, numeric routing_steps)."""
    by_circuit: dict[str, list[dict]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if (row.get(RUNS_STATUS) or "").strip() != "success":
                continue
            if to_float(row.get(RUNS_STEPS)) is None:
                continue
            by_circuit.setdefault(row["circuit"].strip(), []).append(row)
    return by_circuit


def pick_best_worst(rows: list[dict]) -> tuple[dict, dict]:
    """Return (best, worst) by routing_steps, tiebreak duration_seconds."""
    def sort_key(r: dict):
        steps = to_float(r.get(RUNS_STEPS)) or float("inf")
        dur = to_float(r.get(RUNS_TIME)) or float("inf")
        return (steps, dur)

    sorted_rows = sorted(rows, key=sort_key)
    return sorted_rows[0], sorted_rows[-1]


def plot_circuit(circuit: str, runs: list[dict], wisq: dict, out_dir: Path) -> None:
    best, worst = pick_best_worst(runs)

    wisq_steps = to_float(wisq.get("wisq_routing_steps"))
    wisq_time = to_float(wisq.get("wisq_duration_s"))
    grid = f"{wisq.get('wisq_x', '?')}x{wisq.get('wisq_y', '?')}"

    best_steps = to_float(best.get(RUNS_STEPS))
    worst_steps = to_float(worst.get(RUNS_STEPS))
    best_time = to_float(best.get(RUNS_TIME))
    worst_time = to_float(worst.get(RUNS_TIME))

    best_label = config_label(best)
    worst_label = config_label(worst)

    labels = [f"best\n({best_label})", f"worst\n({worst_label})", "WISQ"]
    colors = ["#2196F3", "#FF9800", "#E53935"]

    steps_vals = [best_steps, worst_steps, wisq_steps]
    time_vals = [best_time, worst_time, wisq_time]

    # Grid size per bar: ours uses graph_x×graph_y, WISQ uses wisq_x×wisq_y.
    def grid_str(row: dict, xkey: str, ykey: str) -> str:
        x, y = str(row.get(xkey, "")).strip(), str(row.get(ykey, "")).strip()
        return f"{x}×{y}" if x and y else ""

    grids = [
        grid_str(best, RUNS_X, RUNS_Y),
        grid_str(worst, RUNS_X, RUNS_Y),
        grid_str(wisq, "wisq_x", "wisq_y"),
    ]

    fig, (ax_steps, ax_time) = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle(f"{circuit}  —  WISQ grid {grid}", fontsize=13, fontweight="bold")

    def pct_label(val: float | None, ref: float | None) -> str:
        if val is None or ref is None or ref == 0:
            return ""
        pct = (val - ref) / ref * 100
        if abs(pct) < 0.05:
            return "0%"
        return f"{pct:+.1f}%"

    def annotate_bars(ax, bars, vals, ref_val, fmt_val):
        max_val = max(v for v in vals if v is not None)
        y_pad = max_val * 0.02
        for bar, val in zip(bars, vals):
            if val is None:
                continue
            x = bar.get_x() + bar.get_width() / 2
            y = bar.get_height()
            ax.text(x, y + y_pad, fmt_val(val),
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
            pct = pct_label(val, ref_val)
            if pct:
                color = "#388E3C" if val < ref_val else ("#E53935" if val > ref_val else "gray")
                ax.text(x, y + y_pad * 5, pct,
                        ha="center", va="bottom", fontsize=9, color=color)

    def label_grids(ax, bars, vals):
        for bar, val, g in zip(bars, vals, grids):
            if val is None or not g:
                continue
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, g,
                    ha="center", va="center", fontsize=9, fontweight="bold",
                    color="white")

    # ── routing steps ──
    bars = ax_steps.bar(labels, steps_vals, color=colors, width=0.5, edgecolor="white")
    ax_steps.set_title("Routing steps")
    ax_steps.set_ylabel("steps")
    ax_steps.set_ylim(0, max(v for v in steps_vals if v is not None) * 1.35)
    annotate_bars(ax_steps, bars, steps_vals, best_steps, lambda v: str(int(v)))
    label_grids(ax_steps, bars, steps_vals)

    # ── time ──
    bars2 = ax_time.bar(labels, time_vals, color=colors, width=0.5, edgecolor="white")
    ax_time.set_title("Wall-clock time")
    ax_time.set_ylabel("seconds")
    max_t = max((v for v in time_vals if v is not None), default=1)
    ax_time.set_ylim(0, max_t * 1.35)
    annotate_bars(ax_time, bars2, time_vals, best_time, lambda v: f"{v:.2f}s")
    label_grids(ax_time, bars2, time_vals)

    n_configs = len(runs)
    fig.text(0.5, 0.01,
             f"Based on {n_configs} run(s). Best/worst by routing steps (tiebreak: time).",
             ha="center", fontsize=8, color="gray")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out_path = out_dir / f"{circuit}_wisq_comparison.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def plot_summary(joined: dict[str, tuple[list[dict], dict]], out_dir: Path, metric: str,
                 family: str | None = None) -> None:
    """One overview figure: grouped bars (ours-best vs WISQ).

    family=None covers all circuits (summary_*.png); otherwise only circuits of
    that family are shown (summary_<family>_*.png).
    """
    if metric == "steps":
        my_key, wisq_key = RUNS_STEPS, "wisq_routing_steps"
        ylabel, title, fname = "routing steps", "Routing steps: ours (best) vs WISQ", "summary_routing_steps.png"
    else:
        my_key, wisq_key = RUNS_TIME, "wisq_duration_s"
        ylabel, title, fname = "seconds", "Wall-clock time: ours (best) vs WISQ", "summary_time.png"

    if family is not None:
        fname = fname.replace("summary_", f"summary_{family}_", 1)
        title = f"[{family}] {title}"

    entries = []
    for circuit, (runs, wisq) in joined.items():
        if family is not None and circuit_family(circuit) != family:
            continue
        best, _ = pick_best_worst(runs)
        mine = to_float(best.get(my_key))
        wisq_val = to_float(wisq.get(wisq_key))
        if mine is None or wisq_val is None:
            continue
        nq = to_float(wisq.get("n_qubits")) or 0.0
        entries.append((circuit, nq, mine, wisq_val))

    # A per-family chart needs at least 2 circuits to be a meaningful trend.
    if family is not None and len(entries) < 2:
        return
    if not entries:
        print(f"  (no data for summary '{metric}')")
        return

    entries.sort(key=lambda e: (e[1], e[0]))
    circuits = [e[0] for e in entries]
    mine_vals = [e[2] for e in entries]
    wisq_vals = [e[3] for e in entries]

    EPS = 1e-9
    ours_wins = sum(1 for m, w in zip(mine_vals, wisq_vals) if m < w - EPS)
    ties = sum(1 for m, w in zip(mine_vals, wisq_vals) if abs(m - w) <= EPS)
    wisq_wins = sum(1 for m, w in zip(mine_vals, wisq_vals) if m > w + EPS)
    total = len(circuits)

    x = np.arange(len(circuits))
    width = 0.4

    fig, ax = plt.subplots(figsize=(max(8, len(circuits) * 0.5), 6))
    ax.bar(x - width / 2, mine_vals, width, label="ours (best)", color="#2196F3")
    ax.bar(x + width / 2, wisq_vals, width, label="WISQ", color="#E53935")

    summary = (f"ours wins: {ours_wins}   ties: {ties}   WISQ wins: {wisq_wins}"
               f"   (of {total})")
    ax.text(0.5, 0.97, summary, transform=ax.transAxes, ha="center", va="top",
            fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))

    allv = mine_vals + wisq_vals
    if min(allv) > 0 and max(allv) / min(allv) > 50:
        ax.set_yscale("log")
        ylabel += " (log scale)"

    ax.set_xticks(x)
    ax.set_xticklabels(circuits, rotation=90, fontsize=8)
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title}  ({len(circuits)} circuits)", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    plt.tight_layout()
    out_path = out_dir / fname
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def plot_optimality(joined: dict[str, tuple[list[dict], dict]], out_dir: Path) -> None:
    """Two scatter figures of our routing optimality, coloured by circuit family.

    optimality = min_routing_steps / routing_steps (layering-depth lower bound
    over the steps actually taken): 1 is perfect, smaller is further from optimal.

      * vs max_parallelism      -- the worst-case floor is the y = 1/x curve, so
        every point sits between y = 1/x (worst) and y = 1 (perfect).
      * vs each CNOT interaction-graph metric (density, modularity, diameter, avg
        shortest path, degree statistics, Gini coefficients, edge-weight stddev,
        clustering) -- whether more tangled interaction graphs route further from
        optimal. See CNOT_GRAPH_METRIC_SPECS.

    Needs the min_routing_steps / max_parallelism columns plus the relevant CNOT
    interaction-graph column in the runs CSV; rows missing them are skipped.
    """
    specs = [
        (RUNS_PARALLELISM, "max parallelism (avg gates / layer)",
         "Routing Optimality vs Max Parallelism", "optimality_vs_max_parallelism.png", True),
    ]
    specs += [
        (col, xlabel, f"Routing Optimality vs {title}", f"optimality_vs_{slug}.png", False)
        for col, xlabel, title, slug in CNOT_GRAPH_METRIC_SPECS
    ]
    for x_key, xlabel, title, fname, worst_case_curve in specs:
        by_family: dict[str, list[tuple[float, float]]] = {}
        for circuit, (runs, _wisq) in joined.items():
            fam = circuit_family(circuit)
            for r in runs:
                steps = to_float(r.get(RUNS_STEPS))
                min_steps = to_float(r.get(RUNS_MIN_STEPS))
                x = to_float(r.get(x_key))
                if steps is None or min_steps is None or x is None or steps <= 0:
                    continue
                by_family.setdefault(fam, []).append((x, min_steps / steps))

        if not by_family:
            print(f"  (no rows with {RUNS_MIN_STEPS} + {x_key}; skipping {fname})")
            continue

        families = sorted(by_family)
        cmap = plt.get_cmap("tab20", max(1, len(families)))
        fig, ax = plt.subplots(figsize=(9, 6))
        n_points = 0
        for i, fam in enumerate(families):
            pts = by_family[fam]
            n_points += len(pts)
            ax.scatter([p[0] for p in pts], [p[1] for p in pts],
                       label=f"{fam} (n={len(pts)})", alpha=0.7, s=28, color=cmap(i))

        # y = 1: perfect routing (ceiling).
        ax.axhline(1.0, color="#2A9D8F", linestyle="--", linewidth=1.0,
                   label="optimality = 1 (perfect)", zorder=1)
        # y = 1/x: minimum achievable optimality (fully serial). Only the
        # parallelism axis has this closed-form floor.
        if worst_case_curve:
            xs_all = [p[0] for pts in by_family.values() for p in pts]
            x_min = max(1e-9, min(xs_all))
            x_max = max(xs_all)
            if x_max > x_min:
                xs = np.linspace(x_min, x_max, 200)
                ax.plot(xs, 1.0 / xs, color="#E76F51", linestyle=":", linewidth=1.2,
                        label="optimality = 1/max_parallelism (worst)", zorder=1)

        ax.set_ylim(0.0, 1.05)
        ax.set_title(f"{title}  (n={n_points})", fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("optimality (min_routing_steps / routing_steps)")
        ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1.0))
        ax.grid(True, linestyle=":", alpha=0.4)
        plt.tight_layout()
        out_path = out_dir / fname
        plt.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"  saved: {out_path}")


def plot_optimality_bars(joined: dict[str, tuple[list[dict], dict]], out_dir: Path) -> None:
    """Grouped bar charts: routing optimality of ours (blue) vs WISQ (red), one
    bar pair per circuit, with circuits ordered along the x-axis by a circuit
    metric. One figure per metric in CNOT_GRAPH_METRIC_SPECS.

    optimality = min_routing_steps / routing_steps (layering-depth lower bound
    over the steps actually taken; 1 = perfect, smaller = further from optimal).
    min_routing_steps is the circuit's dependency depth — a router-/mapping-
    independent lower bound — so it is the same numerator for both sides:

        ours optimality = min_routing_steps / our best routing_steps
        WISQ optimality = min_routing_steps / wisq_routing_steps

    Higher is better. No binning/aggregation: every circuit keeps its own bar
    pair; circuits that share a metric value simply sit next to each other (the
    x tick shows the metric value, so equal values read as one bin of bars).
    """
    for col, xlabel, title, slug in CNOT_GRAPH_METRIC_SPECS:
        entries = []
        for circuit, (runs, wisq) in joined.items():
            best, _ = pick_best_worst(runs)
            min_steps = to_float(best.get(RUNS_MIN_STEPS))
            my_steps = to_float(best.get(RUNS_STEPS))
            wisq_steps = to_float(wisq.get("wisq_routing_steps"))
            x = to_float(best.get(col))
            if None in (min_steps, my_steps, wisq_steps, x):
                continue
            if min_steps <= 0 or my_steps <= 0 or wisq_steps <= 0:
                continue
            entries.append((circuit, x, min_steps / my_steps, min_steps / wisq_steps))

        fname = f"optimality_bars_vs_{slug}.png"
        if not entries:
            print(f"  (no rows with {RUNS_MIN_STEPS}/{RUNS_STEPS}/wisq_routing_steps + {col}; skipping {fname})")
            continue

        # Order left->right by the metric value (then circuit name); equal values
        # end up adjacent, forming a visual bin.
        entries.sort(key=lambda e: (e[1], e[0]))
        circuits = [e[0] for e in entries]
        xvals = [e[1] for e in entries]
        mine_opt = [e[2] for e in entries]
        wisq_opt = [e[3] for e in entries]

        EPS = 1e-9
        ours_wins = sum(1 for m, w in zip(mine_opt, wisq_opt) if m > w + EPS)
        ties = sum(1 for m, w in zip(mine_opt, wisq_opt) if abs(m - w) <= EPS)
        wisq_wins = sum(1 for m, w in zip(mine_opt, wisq_opt) if m < w - EPS)
        total = len(circuits)

        x = np.arange(len(circuits))
        width = 0.4
        fig, ax = plt.subplots(figsize=(max(8, len(circuits) * 0.5), 6))
        ax.bar(x - width / 2, mine_opt, width, label="ours (best)", color="#2196F3")
        ax.bar(x + width / 2, wisq_opt, width, label="WISQ", color="#E53935")

        summary = (f"ours wins: {ours_wins}   ties: {ties}   WISQ wins: {wisq_wins}"
                   f"   (of {total})")
        ax.text(0.5, 0.97, summary, transform=ax.transAxes, ha="center", va="top",
                fontsize=11, fontweight="bold",
                bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))

        # y = 1: perfect routing (one step per layer).
        ax.axhline(1.0, color="#2A9D8F", linestyle="--", linewidth=1.0,
                   label="optimality = 1 (perfect)", zorder=1)

        # x tick = metric value (primary) with the circuit underneath for identity.
        ax.set_xticks(x)
        ax.set_xticklabels([f"{xv:g}\n{c}" for xv, c in zip(xvals, circuits)],
                           rotation=90, fontsize=7)
        ax.set_ylim(0.0, max(1.05, max(mine_opt + wisq_opt) * 1.08))
        ax.set_xlabel(xlabel)
        ax.set_ylabel("optimality (min_routing_steps / routing_steps)")
        ax.set_title(f"Routing Optimality: ours vs WISQ — ordered by {title}  ({total} circuits)",
                     fontweight="bold")
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.4)
        plt.tight_layout()
        out_path = out_dir / fname
        plt.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"  saved: {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plot our runs vs WISQ (joined from a WISQ CSV and a runs CSV), one figure per circuit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("wisq_csv", help="WISQ-only CSV (e.g. data/best_wisq_per_circuit.csv from extract_wisq.py)")
    parser.add_argument("runs_csv", help="Our benchmark runs CSV (e.g. *_runs.csv)")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT_DIR),
                        help=f"Output directory for PNGs (default: {DEFAULT_OUTPUT_DIR})")
    args = parser.parse_args()

    wisq_path = Path(args.wisq_csv)
    runs_path = Path(args.runs_csv)
    for p in (wisq_path, runs_path):
        if not p.exists():
            print(f"ERROR: input file not found: {p}", file=sys.stderr)
            return 1

    wisq_by_circuit = load_wisq(wisq_path)
    runs_by_circuit = load_runs(runs_path)
    if not wisq_by_circuit:
        print("No successful WISQ rows found in the WISQ CSV.", file=sys.stderr)
        return 1
    if not runs_by_circuit:
        print("No successful runs found in the runs CSV.", file=sys.stderr)
        return 1

    # Join on circuit: keep only those present (successfully) in both files.
    joined: dict[str, tuple[list[dict], dict]] = {}
    for circuit, runs in runs_by_circuit.items():
        wisq = wisq_by_circuit.get(circuit)
        if wisq is not None:
            joined[circuit] = (runs, wisq)

    missing = sorted(set(runs_by_circuit) - set(wisq_by_circuit))
    if missing:
        print(f"Note: {len(missing)} circuit(s) in runs CSV have no WISQ result and are skipped: "
              f"{', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}", file=sys.stderr)

    if not joined:
        print("No circuits in common between the two CSVs.", file=sys.stderr)
        return 1

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Plotting {len(joined)} circuit(s) → {out_dir}")
    for circuit, (runs, wisq) in sorted(joined.items()):
        plot_circuit(circuit, runs, wisq, out_dir)

    plot_summary(joined, out_dir, "steps")
    plot_summary(joined, out_dir, "time")

    # Routing-optimality scatters (ours), coloured by circuit family.
    plot_optimality(joined, out_dir)

    # Routing-optimality grouped bar charts: ours (blue) vs WISQ (red) per
    # circuit, one figure per metric, x-ordered by that metric.
    plot_optimality_bars(joined, out_dir)

    # Per-family overview figures (same as the summaries, restricted to each
    # family: qft, qaoa, vqe_su2, ...). Families with a single circuit are skipped.
    families = sorted({circuit_family(c) for c in joined})
    for fam in families:
        plot_summary(joined, out_dir, "steps", family=fam)
        plot_summary(joined, out_dir, "time", family=fam)

    return 0


if __name__ == "__main__":
    sys.exit(main())
