#!/usr/bin/env python3
"""Plots from the best-per-circuit CSVs produced by extract_best_per_circuit.py.

Inputs (defaults point at data/):
  * OURS / WISQ by routing steps:      best_ours_per_circuit.csv, best_wisq_per_circuit.csv
  * OURS / WISQ by space-time volume:  best_volume_ours_per_circuit.csv, best_volume_wisq_per_circuit.csv
  * a runs CSV (default data/results/wisq_compare_runs.csv) supplying the
    per-circuit metrics min_cnot_degree and min_routing_steps (both are circuit
    properties, independent of config, so any row of the circuit works).

For BOTH metrics — routing steps and space-time volume V = x*y*steps — the same
code produces (metric = "steps" | "volume"):

  * ratio_<metric>_vs_min_cnot_degree.png — scatter of ratio = WISQ / ours vs
    min CNOT degree, coloured by circuit family (tiny families fold into
    "other"). ratio > 1 means we win.
  * ratio_bars_<metric>.png — geometric-mean ratio per min-CNOT-degree bin,
    one bar per bin with the circuit count on top, plus a win/tie/loss box.

Plus, steps only (volume has no closed-form lower bound):

  * optimality_vs_min_cnot_degree.png — scatter of
    optimality = min_routing_steps / routing_steps (1 = perfect) vs min CNOT
    degree, ours vs WISQ as two series.

Only circuits present in both sides of a pair (and, for the x-axis, in the runs
CSV with the needed metric) are plotted.

Usage:
    python scripts/plots/plot_best_per_circuit.py
    python scripts/plots/plot_best_per_circuit.py --runs-csv data/results/wisq_compare_runs.csv \
        --output data/results/best_per_circuit_plots
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

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # scripts/plots/ -> root
DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT_DIR = DATA_DIR / "results" / "best_per_circuit_plots"
DEFAULT_RUNS_CSV = DATA_DIR / "results" / "wisq_compare_runs.csv"

OURS_COLOR = "#2196F3"
WISQ_COLOR = "#E53935"
REF_LINE_COLOR = "#2A9D8F"

MIN_DEGREE_COL = "min_cnot_degree"
MIN_STEPS_COL = "min_routing_steps"
X_LABEL = "min CNOT degree (over qubits with a CNOT)"
MIN_FAMILY_SIZE = 3  # scatter: families with fewer circuits fold into "other"

# (metric key, ours value column, wisq value column, human name).
# The value columns live in the corresponding best-per-circuit CSVs.
METRIC_SPECS = {
    "steps": ("my_routing_steps", "wisq_routing_steps", "routing steps"),
    "volume": ("my_V", "wisq_V", "volume (x·y·steps)"),
}


def to_float(v) -> float | None:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def circuit_family(name: str) -> str:
    """Group key for a circuit: strip the trailing size token.
    qft_n50 -> qft, vqe_su2_n100 -> vqe_su2, qft_20 -> qft."""
    base = re.sub(r"_n\d+.*$", "", name)
    base = re.sub(r"_\d+$", "", base)
    return base or name


def load_by_circuit(path: Path) -> dict[str, dict]:
    """circuit -> row. Best-per-circuit CSVs have exactly one row per circuit."""
    with path.open(newline="") as f:
        return {row["circuit"].strip(): row for row in csv.DictReader(f)
                if (row.get("circuit") or "").strip()}


def load_circuit_metrics(path: Path) -> dict[str, dict[str, float]]:
    """circuit -> {min_cnot_degree, min_routing_steps} from a runs CSV.

    min_cnot_degree is a pure circuit property (first row wins). min_routing_steps
    (dependency depth) can differ across rows of the same circuit — commute-enabled
    configs re-layer the circuit and lower the depth — so take the MINIMUM across
    rows: the tightest lower bound seen, keeping optimality = min/steps <= ~1."""
    metrics: dict[str, dict[str, float]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            circuit = (row.get("circuit") or "").strip()
            if not circuit:
                continue
            degree = to_float(row.get(MIN_DEGREE_COL))
            min_steps = to_float(row.get(MIN_STEPS_COL))
            if degree is None or min_steps is None:
                continue
            cur = metrics.get(circuit)
            if cur is None:
                metrics[circuit] = {MIN_DEGREE_COL: degree, MIN_STEPS_COL: min_steps}
            else:
                cur[MIN_STEPS_COL] = min(cur[MIN_STEPS_COL], min_steps)
    return metrics


def join_metric(ours: dict[str, dict], wisq: dict[str, dict],
                metrics: dict[str, dict[str, float]], metric: str):
    """[(circuit, min_cnot_degree, our_value, wisq_value)] for circuits present
    everywhere with positive values."""
    ours_col, wisq_col, _ = METRIC_SPECS[metric]
    entries = []
    for circuit, our_row in ours.items():
        wisq_row = wisq.get(circuit)
        m = metrics.get(circuit)
        if wisq_row is None or m is None:
            continue
        mine = to_float(our_row.get(ours_col))
        theirs = to_float(wisq_row.get(wisq_col))
        if mine is None or theirs is None or mine <= 0 or theirs <= 0:
            continue
        entries.append((circuit, m[MIN_DEGREE_COL], mine, theirs))
    return entries


def win_loss_box(ax, ratios: list[float]) -> None:
    """Win/tie/loss summary box. ratio = WISQ / ours, so ratio > 1 = we win."""
    EPS = 1e-9
    wins = sum(1 for r in ratios if r > 1 + EPS)
    ties = sum(1 for r in ratios if abs(r - 1) <= EPS)
    losses = sum(1 for r in ratios if r < 1 - EPS)
    ax.text(0.5, 0.97,
            f"ours wins: {wins}   ties: {ties}   WISQ wins: {losses}   (of {len(ratios)})",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))


def maybe_log_y(ax, values: list[float], ylabel: str) -> str:
    if min(values) > 0 and max(values) / min(values) > 20:
        ax.set_yscale("log")
        return ylabel + " (log scale)"
    return ylabel


def plot_ratio_scatter(entries, metric: str, out_dir: Path) -> None:
    """Scatter: ratio = WISQ / ours vs min CNOT degree, coloured by family."""
    _, _, metric_name = METRIC_SPECS[metric]
    by_family: dict[str, list[tuple[float, float]]] = {}
    for circuit, degree, mine, theirs in entries:
        by_family.setdefault(circuit_family(circuit), []).append((degree, theirs / mine))

    # Fold tiny families into "other": tab20 has 20 hues, and one dot per
    # family is legend noise — colors must not cycle.
    folded: dict[str, list[tuple[float, float]]] = {}
    for fam, pts in by_family.items():
        folded.setdefault(fam if len(pts) >= MIN_FAMILY_SIZE else "other", []).extend(pts)
    by_family = folded

    families = sorted(f for f in by_family if f != "other")
    if "other" in by_family:
        families.append("other")  # gray, last in the legend
    cmap = plt.get_cmap("tab20", max(1, len(families)))
    fig, ax = plt.subplots(figsize=(9, 6))
    all_ratios = []
    for i, fam in enumerate(families):
        pts = by_family[fam]
        all_ratios += [p[1] for p in pts]
        color = "#9E9E9E" if fam == "other" else cmap(i)
        ax.scatter([p[0] for p in pts], [p[1] for p in pts],
                   label=f"{fam} (n={len(pts)})", alpha=0.7, s=28, color=color)

    ax.axhline(1.0, color=REF_LINE_COLOR, linestyle="--", linewidth=1.0,
               label="ratio = 1 (parity)", zorder=1)
    ylabel = maybe_log_y(ax, all_ratios, "ratio (WISQ / ours)")
    win_loss_box(ax, all_ratios)
    ax.set_title(f"WISQ/ours {metric_name} ratio vs Min CNOT Degree — >1 = we win"
                 f"  (n={len(entries)})", fontweight="bold")
    ax.set_xlabel(X_LABEL)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    ax.grid(True, linestyle=":", alpha=0.4)
    plt.tight_layout()
    out_path = out_dir / f"ratio_{metric}_vs_min_cnot_degree.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def degree_bin(degree: float) -> str:
    """Bin label for a min CNOT degree. Small degrees each get their own bin
    (that is where most circuits sit); larger degrees are range-binned."""
    d = int(degree)
    if d <= 4:
        return str(d)
    for lo, hi in ((5, 9), (10, 19), (20, 49), (50, 99)):
        if lo <= d <= hi:
            return f"{lo}–{hi}"
    return "100+"


DEGREE_BIN_ORDER = ["0", "1", "2", "3", "4", "5–9", "10–19",
                    "20–49", "50–99", "100+"]


def plot_ratio_bars(entries, metric: str, out_dir: Path) -> None:
    """Geometric-mean ratio per min-CNOT-degree bin, one bar per bin with the
    circuit count on top. ratio = WISQ / ours; >1 (blue) = we win on average
    in that bin, <1 (red) = we lose. Geometric mean because ratios are
    multiplicative (2x win should cancel a 2x loss)."""
    _, _, metric_name = METRIC_SPECS[metric]
    by_bin: dict[str, list[float]] = {}
    for _circuit, degree, mine, theirs in entries:
        by_bin.setdefault(degree_bin(degree), []).append(theirs / mine)

    bins = [b for b in DEGREE_BIN_ORDER if b in by_bin]
    gmeans = [float(np.exp(np.mean(np.log(by_bin[b])))) for b in bins]
    counts = [len(by_bin[b]) for b in bins]

    x = np.arange(len(bins))
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [OURS_COLOR if g > 1 else (WISQ_COLOR if g < 1 else "#9E9E9E") for g in gmeans]
    bars = ax.bar(x, gmeans, 0.6, color=colors)
    for bar, n in zip(bars, counts):
        ax.annotate(f"n={n}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, color="#555555")

    ax.axhline(1.0, color=REF_LINE_COLOR, linestyle="--", linewidth=1.0, zorder=1)
    win_loss_box(ax, [r for rs in by_bin.values() for r in rs])
    ax.set_xticks(x)
    ax.set_xticklabels(bins)
    ax.set_ylim(0, max(gmeans) * 1.25)
    ax.set_xlabel(X_LABEL)
    ax.set_ylabel("geometric mean ratio (WISQ / ours)")
    ax.set_title(f"WISQ/ours {metric_name} ratio by Min CNOT Degree — >1 = we win"
                 f"  ({len(entries)} circuits)", fontweight="bold")
    handles = [plt.Rectangle((0, 0), 1, 1, color=OURS_COLOR),
               plt.Rectangle((0, 0), 1, 1, color=WISQ_COLOR)]
    ax.legend(handles, ["we win on average (ratio > 1)", "WISQ wins on average (ratio < 1)"],
              fontsize=9, loc="lower right")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.tight_layout()
    out_path = out_dir / f"ratio_bars_{metric}.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def plot_optimality_scatter(ours: dict[str, dict], wisq: dict[str, dict],
                            metrics: dict[str, dict[str, float]], out_dir: Path) -> None:
    """Scatter: optimality = min_routing_steps / routing_steps vs min CNOT degree,
    ours vs WISQ as two series. 1 = perfect (steps = dependency depth); the lower
    bound is router-independent so it is the same numerator for both sides."""
    pts_ours, pts_wisq = [], []
    for circuit, our_row in ours.items():
        wisq_row = wisq.get(circuit)
        m = metrics.get(circuit)
        if wisq_row is None or m is None:
            continue
        min_steps = m[MIN_STEPS_COL]
        mine = to_float(our_row.get("my_routing_steps"))
        theirs = to_float(wisq_row.get("wisq_routing_steps"))
        if min_steps <= 0 or mine is None or theirs is None or mine <= 0 or theirs <= 0:
            continue
        pts_ours.append((m[MIN_DEGREE_COL], min_steps / mine))
        pts_wisq.append((m[MIN_DEGREE_COL], min_steps / theirs))

    if not pts_ours:
        print("  (no circuits with min_routing_steps + min_cnot_degree; skipping optimality plot)")
        return

    over = [y for _, y in pts_ours + pts_wisq if y > 1.0]
    if over:
        # steps below every depth bound seen in the runs CSV → the winning config
        # re-layered the circuit (commute) more than any run recorded there.
        print(f"  note: {len(over)} point(s) above optimality 1 "
              f"(best steps beat all recorded min_routing_steps; max {max(over):.3f})")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter([p[0] for p in pts_ours], [p[1] for p in pts_ours],
               label=f"ours (n={len(pts_ours)})", alpha=0.7, s=28, color=OURS_COLOR)
    ax.scatter([p[0] for p in pts_wisq], [p[1] for p in pts_wisq],
               label=f"WISQ (n={len(pts_wisq)})", alpha=0.7, s=28, color=WISQ_COLOR,
               marker="^")
    ax.axhline(1.0, color=REF_LINE_COLOR, linestyle="--", linewidth=1.0,
               label="optimality = 1 (perfect)", zorder=1)
    y_top = max([1.0] + [y for _, y in pts_ours + pts_wisq]) * 1.05
    ax.set_ylim(0.0, y_top)
    ax.set_title(f"Routing Optimality vs Min CNOT Degree — ours vs WISQ  (n={len(pts_ours)})",
                 fontweight="bold")
    ax.set_xlabel(X_LABEL)
    ax.set_ylabel("optimality (min_routing_steps / routing_steps)")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.4)
    plt.tight_layout()
    out_path = out_dir / "optimality_vs_min_cnot_degree.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ours-csv", default=str(DATA_DIR / "best_ours_per_circuit.csv"))
    parser.add_argument("--wisq-csv", default=str(DATA_DIR / "best_wisq_per_circuit.csv"))
    parser.add_argument("--volume-ours-csv", default=str(DATA_DIR / "best_volume_ours_per_circuit.csv"))
    parser.add_argument("--volume-wisq-csv", default=str(DATA_DIR / "best_volume_wisq_per_circuit.csv"))
    parser.add_argument("--runs-csv", default=str(DEFAULT_RUNS_CSV),
                        help="Runs CSV supplying min_cnot_degree / min_routing_steps per circuit "
                             f"(default: {DEFAULT_RUNS_CSV})")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT_DIR),
                        help=f"Output directory for PNGs (default: {DEFAULT_OUTPUT_DIR})")
    args = parser.parse_args()

    paths = {name: Path(p) for name, p in [
        ("ours", args.ours_csv), ("wisq", args.wisq_csv),
        ("volume_ours", args.volume_ours_csv), ("volume_wisq", args.volume_wisq_csv),
        ("runs", args.runs_csv),
    ]}
    for name, p in paths.items():
        if not p.exists():
            print(f"ERROR: {name} CSV not found: {p}", file=sys.stderr)
            return 1

    metrics = load_circuit_metrics(paths["runs"])
    if not metrics:
        print(f"ERROR: no rows with {MIN_DEGREE_COL} + {MIN_STEPS_COL} in {paths['runs']}",
              file=sys.stderr)
        return 1
    print(f"Circuit metrics for {len(metrics)} circuit(s) from {paths['runs'].name}")

    pairs = {
        "steps": (load_by_circuit(paths["ours"]), load_by_circuit(paths["wisq"])),
        "volume": (load_by_circuit(paths["volume_ours"]), load_by_circuit(paths["volume_wisq"])),
    }

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    for metric, (ours, wisq) in pairs.items():
        entries = join_metric(ours, wisq, metrics, metric)
        if not entries:
            print(f"  (no joined circuits for metric '{metric}'; skipping)")
            continue
        print(f"[{metric}] {len(entries)} circuit(s) joined")
        plot_ratio_scatter(entries, metric, out_dir)
        plot_ratio_bars(entries, metric, out_dir)

    plot_optimality_scatter(*pairs["steps"], metrics, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
