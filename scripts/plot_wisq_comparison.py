#!/usr/bin/env python3
"""Plot per-circuit comparison between best config, worst config, and WISQ.

Reads a CSV produced by compare_wisq_2.py (--bench or single-run mode) and
generates one figure per circuit. Each figure has two subplots:
  - Left:  routing steps  (mine best / mine worst / wisq)
  - Right: wall-clock time (my_duration_s / my_duration_s / wisq_duration_s)

Best/worst are chosen by my_routing_steps (tiebreak: my_duration_s).
Plots are saved to data/results/wisq_plots/.

Usage:
    python scripts/plot_wisq_comparison.py --input data/results/wisq_3circ_out.csv
    python scripts/plot_wisq_comparison.py --input data/results/wisq_3circ_out.csv \
        --output data/results/wisq_plots
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
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "results" / "wisq_plots"

CONFIG_LABEL_FIELDS = [
    ("type", {"gaussian": "gauss", "magic_aware": "magic", "homogeneous": "homo"}),
    ("gaussian_strategy", {"coarse": "coarse", "fine": "fine"}),
    ("safe_passage_strategy", {"cube": "cube", "connectivity": "conn", "passage_no_subgraphs": "pass"}),
    ("routing_strategy", {"naive": "naive", "congestion": "cong"}),
    ("t_routing_mode", {"normal_t_routing": "nT", "smart_t_routing": "sT"}),
    ("border_distance_percentage", {}),
]


def to_float(v: str) -> float | None:
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


def grid_area(x, y) -> float | None:
    """Physical-qubit footprint = grid cells (x*y). None if either dim is missing."""
    xf, yf = to_float(x), to_float(y)
    if xf is None or yf is None:
        return None
    return xf * yf


def wisq_extra_qubit_pct(our_x, our_y, wisq_x, wisq_y) -> float | None:
    """How many more physical qubits (grid area x*y) WISQ used than ours, in %.
    (wisq_area - our_area) / our_area * 100. None if a dimension is missing."""
    our_area = grid_area(our_x, our_y)
    wisq_area = grid_area(wisq_x, wisq_y)
    if not our_area or wisq_area is None:
        return None
    return 100.0 * (wisq_area - our_area) / our_area


def config_label(row: dict) -> str:
    parts = []
    for field, abbrev in CONFIG_LABEL_FIELDS:
        val = row.get(field, "").strip()
        if not val:
            continue
        val = abbrev.get(val, val)
        parts.append(val)
    return "/".join(parts) if parts else "?"


def load_rows(path: Path) -> dict[str, list[dict]]:
    """Load CSV, keep only rows with wisq_status=success and valid numeric fields."""
    by_circuit: dict[str, list[dict]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("wisq_status", "").strip() != "success":
                continue
            if to_float(row.get("my_routing_steps")) is None:
                continue
            if to_float(row.get("wisq_routing_steps")) is None:
                continue
            circuit = row["circuit"]
            by_circuit.setdefault(circuit, []).append(row)
    return by_circuit


def pick_best_worst(rows: list[dict]) -> tuple[dict, dict]:
    """Return (best, worst) by my_routing_steps, tiebreak my_duration_s."""
    def sort_key(r: dict):
        steps = to_float(r["my_routing_steps"]) or float("inf")
        dur = to_float(r.get("my_duration_s")) or float("inf")
        return (steps, dur)

    sorted_rows = sorted(rows, key=sort_key)
    return sorted_rows[0], sorted_rows[-1]


def plot_circuit(circuit: str, rows: list[dict], out_dir: Path) -> None:
    best, worst = pick_best_worst(rows)

    wisq_steps = to_float(best["wisq_routing_steps"])
    wisq_time = to_float(best.get("wisq_duration_s"))
    grid = f"{best.get('wisq_x', '?')}x{best.get('wisq_y', '?')}"

    best_steps = to_float(best["my_routing_steps"])
    worst_steps = to_float(worst["my_routing_steps"])
    best_time = to_float(best.get("my_duration_s"))
    worst_time = to_float(worst.get("my_duration_s"))

    best_label = config_label(best)
    worst_label = config_label(worst)

    labels = [f"best\n({best_label})", f"worst\n({worst_label})", "WISQ"]
    colors = ["#2196F3", "#FF9800", "#E53935"]

    steps_vals = [best_steps, worst_steps, wisq_steps]
    time_vals = [best_time, worst_time, wisq_time]

    # Grid size per bar: ours (best/worst) use my_x×my_y, WISQ uses wisq_x×wisq_y.
    # Drawn inside each bar so a larger WISQ grid is immediately visible.
    def grid_str(row: dict, xkey: str, ykey: str) -> str:
        x, y = str(row.get(xkey, "")).strip(), str(row.get(ykey, "")).strip()
        return f"{x}×{y}" if x and y else ""

    grids = [
        grid_str(best, "my_x", "my_y"),
        grid_str(worst, "my_x", "my_y"),
        grid_str(best, "wisq_x", "wisq_y"),
    ]

    fig, (ax_steps, ax_time) = plt.subplots(1, 2, figsize=(11, 5))
    fig.suptitle(f"{circuit}  —  grid {grid}", fontsize=13, fontweight="bold")

    def pct_label(val: float | None, ref: float | None) -> str:
        """Return '+X%' / '-X%' / '0%' relative to ref. Empty string if missing."""
        if val is None or ref is None or ref == 0:
            return ""
        pct = (val - ref) / ref * 100
        if abs(pct) < 0.05:
            return "0%"
        return f"{pct:+.1f}%"

    def annotate_bars(ax, bars, vals, ref_val, fmt_val):
        """Draw value label + percentage-vs-best below it for each bar."""
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
        """Write the grid size centred inside each bar (white text on the bar)."""
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

    # number of configs shown as footnote
    n_configs = len(rows)
    fig.text(0.5, 0.01,
             f"Based on {n_configs} config(s). Best/worst by routing steps (tiebreak: time).",
             ha="center", fontsize=8, color="gray")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out_path = out_dir / f"{circuit}_wisq_comparison.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def plot_summary(by_circuit: dict[str, list[dict]], out_dir: Path, metric: str,
                 family: str | None = None) -> None:
    """One overview figure: grouped bars (ours-best vs WISQ).

    metric = "steps" -> routing steps; metric = "time" -> wall-clock seconds.
    Only circuits where both our best config and WISQ have a valid value are shown.
    family=None covers all circuits (summary_*.png); otherwise only circuits of
    that family are shown (summary_<family>_*.png).
    """
    if metric == "steps":
        my_key, wisq_key = "my_routing_steps", "wisq_routing_steps"
        ylabel, title, fname = "routing steps", "Routing steps: ours (best) vs WISQ", "summary_routing_steps.png"
    else:
        my_key, wisq_key = "my_duration_s", "wisq_duration_s"
        ylabel, title, fname = "seconds", "Wall-clock time: ours (best) vs WISQ", "summary_time.png"

    if family is not None:
        fname = fname.replace("summary_", f"summary_{family}_", 1)
        title = f"[{family}] {title}"

    # One point per circuit: our best config (by routing steps, tiebreak time).
    entries = []
    for circuit, rows in by_circuit.items():
        if family is not None and circuit_family(circuit) != family:
            continue
        best, _ = pick_best_worst(rows)
        mine = to_float(best.get(my_key))
        wisq = to_float(best.get(wisq_key))
        if mine is None or wisq is None:
            continue
        nq = to_float(best.get("n_qubits")) or 0.0
        qpct = wisq_extra_qubit_pct(best.get("my_x"), best.get("my_y"),
                                    best.get("wisq_x"), best.get("wisq_y"))
        entries.append((circuit, nq, mine, wisq, qpct))

    # A per-family chart needs at least 2 circuits to be a meaningful trend.
    if family is not None and len(entries) < 2:
        return
    if not entries:
        print(f"  (no data for summary '{metric}')")
        return

    # Sort by qubit count, then name, for a natural left-to-right progression.
    entries.sort(key=lambda e: (e[1], e[0]))
    circuits = [e[0] for e in entries]
    mine_vals = [e[2] for e in entries]
    wisq_vals = [e[3] for e in entries]
    qpcts = [e[4] for e in entries]

    # Win/tie/loss tally (lower is better for both metrics).
    EPS = 1e-9
    ours_wins = sum(1 for m, w in zip(mine_vals, wisq_vals) if m < w - EPS)
    ties = sum(1 for m, w in zip(mine_vals, wisq_vals) if abs(m - w) <= EPS)
    wisq_wins = sum(1 for m, w in zip(mine_vals, wisq_vals) if m > w + EPS)
    total = len(circuits)

    x = np.arange(len(circuits))
    width = 0.4

    fig, ax = plt.subplots(figsize=(max(8, len(circuits) * 0.5), 6))
    ax.bar(x - width / 2, mine_vals, width, label="ours (best)", color="#2196F3")
    wisq_bars = ax.bar(x + width / 2, wisq_vals, width, label="WISQ", color="#E53935")

    # Per-family chart only: above each WISQ bar, the % of extra physical qubits
    # (grid area x*y) WISQ used vs our best config for that circuit.
    if family is not None:
        for bar, qpct in zip(wisq_bars, qpcts):
            if qpct is None:
                continue
            ax.annotate(f"{qpct:+.0f}%",
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 2), textcoords="offset points",
                        ha="center", va="bottom", fontsize=7, color="#555555")

    # Win summary box (ours beats WISQ = strictly lower value).
    summary = (f"ours wins: {ours_wins}   ties: {ties}   WISQ wins: {wisq_wins}"
               f"   (of {total})")
    ax.text(0.5, 0.97, summary, transform=ax.transAxes, ha="center", va="top",
            fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))

    # Log scale when the values span a wide range and are all positive.
    allv = mine_vals + wisq_vals
    if min(allv) > 0 and max(allv) / min(allv) > 50:
        ax.set_yscale("log")
        ylabel += " (log scale)"

    ax.set_xticks(x)
    ax.set_xticklabels(circuits, rotation=90, fontsize=8)
    ax.set_ylabel(ylabel)
    title_full = f"{title}  ({len(circuits)} circuits)"
    if family is not None:
        title_full += "\n(% over WISQ bars = extra physical qubits, grid x·y, vs ours)"
    ax.set_title(title_full, fontweight="bold", fontsize=10 if family is not None else 12)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    plt.tight_layout()
    out_path = out_dir / fname
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plot best/worst config vs WISQ, one figure per circuit."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="CSV produced by compare_wisq_2.py",
    )
    parser.add_argument(
        "--output", "-o", default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory for PNGs (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    by_circuit = load_rows(in_path)
    if not by_circuit:
        print("No successful rows found in the CSV.", file=sys.stderr)
        return 1

    print(f"Plotting {len(by_circuit)} circuit(s) → {out_dir}")
    for circuit, rows in sorted(by_circuit.items()):
        plot_circuit(circuit, rows, out_dir)

    # Two cross-circuit overview figures: routing steps and time.
    plot_summary(by_circuit, out_dir, "steps")
    plot_summary(by_circuit, out_dir, "time")

    # Per-family overview figures (same as the summaries, restricted to each
    # family: qft, qaoa, vqe_su2, ...). Families with a single circuit are skipped.
    families = sorted({circuit_family(c) for c in by_circuit})
    for fam in families:
        plot_summary(by_circuit, out_dir, "steps", family=fam)
        plot_summary(by_circuit, out_dir, "time", family=fam)

    return 0


if __name__ == "__main__":
    sys.exit(main())
