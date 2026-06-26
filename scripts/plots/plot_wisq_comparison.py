#!/usr/bin/env python3
"""Plot per-circuit comparison between best config, worst config, and WISQ.

Reads a CSV produced by compare_wisq_2.py (--bench or single-run mode) and
generates one figure per circuit. Each figure has two subplots:
  - Left:  routing steps  (mine best / mine worst / wisq)
  - Right: wall-clock time (my_duration_s / my_duration_s / wisq_duration_s)

Best/worst are chosen by my_routing_steps (tiebreak: my_duration_s).
Plots are saved to data/results/wisq_plots/.

Usage:
    python scripts/plots/plot_wisq_comparison.py --input data/results/wisq_3circ_out.csv
    python scripts/plots/plot_wisq_comparison.py --input data/results/wisq_3circ_out.csv \
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

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # scripts/plots/ -> root
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "results" / "wisq_plots"

CONFIG_LABEL_FIELDS = [
    ("type", {"gaussian": "gauss", "magic_aware": "magic", "homogeneous": "homo"}),
    ("gaussian_strategy", {"coarse": "coarse", "fine": "fine"}),
    ("safe_passage_strategy", {"cube": "cube", "connectivity": "conn", "passage_no_subgraphs": "pass"}),
    ("routing_strategy", {"naive": "naive", "congestion": "cong"}),
    ("t_routing_mode", {"normal_t_routing": "nT", "smart_t_routing": "sT"}),
    ("border_distance_percentage", {}),
]

# Single-CSV column names (compare_wisq_2.py output).
MINE_STEPS = "my_routing_steps"
WISQ_STEPS = "wisq_routing_steps"
MIN_STEPS = "min_routing_steps"
PARALLELISM = "max_parallelism"
DENSITY = "cnot_interaction_density"

# CNOT interaction-graph characterization metrics. Each becomes an
# optimality-vs-metric scatter / grouped-bar chart, the same way density did.
# (CSV column, x-axis label, title phrase, filename slug). The density entry
# keeps the legacy "circuit_density" slug so its filename does not change.
CNOT_GRAPH_METRIC_SPECS = [
    (DENSITY, "circuit density (unique CNOT pairs / max pairs)", "Circuit Density", "circuit_density"),
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


def dim_diff_per_side(row: dict) -> float | None:
    """WISQ's grid side minus ours, per side (positive = OUR grid is smaller).

    Uses the dim_diff_side column written by compare_wisq_conn.py when present;
    otherwise falls back to wisq_x - my_x (square grids). None if unavailable."""
    v = to_float(row.get("dim_diff_side"))
    if v is not None:
        return v
    mx, wx = to_float(row.get("my_x")), to_float(row.get("wisq_x"))
    if mx is None or wx is None:
        return None
    return wx - mx


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
    my_grid = f"{best.get('my_x', '?')}x{best.get('my_y', '?')}"
    wisq_grid = f"{best.get('wisq_x', '?')}x{best.get('wisq_y', '?')}"
    dside = dim_diff_per_side(best)
    diff_str = f"  (WISQ {dside:+.0f}/side)" if dside is not None else ""

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
    fig.suptitle(f"{circuit}  —  ours {my_grid} vs WISQ {wisq_grid}{diff_str}",
                 fontsize=13, fontweight="bold")

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


def plot_family_grid_size(by_circuit: dict[str, list[dict]], out_dir: Path,
                          family: str) -> None:
    """Per-family line chart of the grid size (area x*y = physical-qubit footprint)
    used by ours (best config) vs WISQ, one point per circuit.

    Two lines (ours / WISQ), circuits sorted left->right by qubit count, so the
    grid footprints can be compared as the family scales up. Saved as
    grid_size_<family>.png. Families with fewer than 2 circuits are skipped.
    """
    entries = []
    for circuit, rows in by_circuit.items():
        if circuit_family(circuit) != family:
            continue
        best, _ = pick_best_worst(rows)
        our_area = grid_area(best.get("my_x"), best.get("my_y"))
        wisq_area = grid_area(best.get("wisq_x"), best.get("wisq_y"))
        if our_area is None or wisq_area is None:
            continue
        nq = to_float(best.get("n_qubits")) or 0.0
        our_dim = f"{str(best.get('my_x', '')).strip()}×{str(best.get('my_y', '')).strip()}"
        wisq_dim = f"{str(best.get('wisq_x', '')).strip()}×{str(best.get('wisq_y', '')).strip()}"
        entries.append((circuit, nq, our_area, wisq_area, our_dim, wisq_dim))

    # A per-family line needs at least 2 circuits to be a meaningful trend.
    if len(entries) < 2:
        return

    entries.sort(key=lambda e: (e[1], e[0]))
    circuits = [e[0] for e in entries]
    our_areas = [e[2] for e in entries]
    wisq_areas = [e[3] for e in entries]
    our_dims = [e[4] for e in entries]
    wisq_dims = [e[5] for e in entries]

    # Win/tie/loss tally (smaller grid footprint is better).
    EPS = 1e-9
    ours_wins = sum(1 for o, w in zip(our_areas, wisq_areas) if o < w - EPS)
    ties = sum(1 for o, w in zip(our_areas, wisq_areas) if abs(o - w) <= EPS)
    wisq_wins = sum(1 for o, w in zip(our_areas, wisq_areas) if o > w + EPS)
    total = len(circuits)

    x = np.arange(len(circuits))
    fig, ax = plt.subplots(figsize=(max(8, len(circuits) * 0.5), 6))
    ax.plot(x, our_areas, marker="o", color="#2196F3", label="ours (best)")
    ax.plot(x, wisq_areas, marker="s", color="#E53935", label="WISQ")

    # Above each point: the actual grid written as "x×y".
    for xi, area, dim in zip(x, our_areas, our_dims):
        ax.annotate(dim, (xi, area), xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7, color="#1565C0")
    for xi, area, dim in zip(x, wisq_areas, wisq_dims):
        ax.annotate(dim, (xi, area), xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7, color="#B71C1C")

    summary = (f"ours smaller: {ours_wins}   ties: {ties}   WISQ smaller: {wisq_wins}"
               f"   (of {total})")
    ax.text(0.5, 0.97, summary, transform=ax.transAxes, ha="center", va="top",
            fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))

    # Log scale when the values span a wide range and are all positive.
    allv = our_areas + wisq_areas
    if min(allv) > 0 and max(allv) / min(allv) > 50:
        ax.set_yscale("log")

    ax.set_xticks(x)
    ax.set_xticklabels(circuits, rotation=90, fontsize=8)
    ax.set_ylabel("grid size (physical qubits, area x·y)")
    ax.set_title(f"[{family}] Grid size: ours (best) vs WISQ  ({total} circuits)",
                 fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    plt.tight_layout()
    out_path = out_dir / f"grid_size_{family}.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")


def smallest_grid_entries(by_circuit: dict[str, list[dict]]) -> list[dict]:
    """Per circuit, the row whose OUR grid area (x*y) is smallest, with the
    grid-size comparison fields computed straight from that CSV row.

    Only rows where all four grid dims (my_x, my_y, wisq_x, wisq_y) are present
    are considered. Selection tiebreak when several rows share our minimal area:
    smaller WISQ area, then fewer routing steps, then less time. Returns one dict
    per circuit: {circuit, n_qubits, our_area, wisq_area, pct, ratio} where
        pct   = (wisq_area - our_area) / our_area * 100   (WISQ extra qubits, %)
        ratio = wisq_area / our_area                       (WISQ / ours, >0)
    """
    entries: list[dict] = []
    for circuit, rows in by_circuit.items():
        cand = []
        for r in rows:
            oa = grid_area(r.get("my_x"), r.get("my_y"))
            wa = grid_area(r.get("wisq_x"), r.get("wisq_y"))
            if oa is None or wa is None or oa <= 0:
                continue
            steps = to_float(r.get("my_routing_steps"))
            steps = steps if steps is not None else float("inf")
            dur = to_float(r.get("my_duration_s"))
            dur = dur if dur is not None else float("inf")
            cand.append((oa, wa, steps, dur, r))
        if not cand:
            continue
        cand.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        oa, wa, _, _, r = cand[0]
        entries.append({
            "circuit": circuit,
            "n_qubits": to_float(r.get("n_qubits")),
            "our_area": oa,
            "wisq_area": wa,
            "pct": (wa - oa) / oa * 100.0,
            "ratio": wa / oa,
        })
    return entries


def grid_size_stats(entries: list[dict]) -> dict:
    """All aggregate grid-size numbers, computed only from `entries` (CSV-derived).
    Returns {} if there is nothing to summarise."""
    if not entries:
        return {}
    pct = np.array([e["pct"] for e in entries], dtype=float)
    ratio = np.array([e["ratio"] for e in entries], dtype=float)
    our_tot = float(sum(e["our_area"] for e in entries))
    wisq_tot = float(sum(e["wisq_area"] for e in entries))
    EPS = 1e-9
    ours_smaller = sum(1 for e in entries if e["our_area"] < e["wisq_area"] - EPS)
    ties = sum(1 for e in entries if abs(e["our_area"] - e["wisq_area"]) <= EPS)
    wisq_smaller = sum(1 for e in entries if e["our_area"] > e["wisq_area"] + EPS)
    n = len(entries)
    return {
        "n": n,
        "mean_pct": float(np.mean(pct)),
        "median_pct": float(np.median(pct)),
        # geometric mean of the ratio (all areas > 0, so logs are finite).
        "geomean_ratio": float(np.exp(np.mean(np.log(ratio)))),
        "p25_pct": float(np.percentile(pct, 25)),
        "p75_pct": float(np.percentile(pct, 75)),
        "std_pct": float(np.std(pct, ddof=1)) if n > 1 else 0.0,
        "min_pct": float(np.min(pct)),
        "max_pct": float(np.max(pct)),
        "ours_smaller": ours_smaller,
        "ties": ties,
        "wisq_smaller": wisq_smaller,
        "our_total_qubits": our_tot,
        "wisq_total_qubits": wisq_tot,
        "total_qubits_saved": wisq_tot - our_tot,
    }


def plot_grid_overview(by_circuit: dict[str, list[dict]], out_dir: Path) -> None:
    """Single figure summarising the grid-size gap over ALL circuits.

    Boxplot + jittered points of the per-circuit % difference
    (wisq_area - our_area)/our_area*100, with mean and median lines, plus a stats
    box (mean, median, geomean ratio, IQR, min/max, win/tie/loss, total qubits).
    Every number comes from smallest_grid_entries / grid_size_stats (CSV only).
    """
    entries = smallest_grid_entries(by_circuit)
    s = grid_size_stats(entries)
    if not s:
        print("  (no rows with all grid dims; skipping grid overview)")
        return

    pcts = [e["pct"] for e in entries]

    fig, ax = plt.subplots(figsize=(7, 7))
    bp = ax.boxplot(pcts, vert=True, widths=0.5, showfliers=False,
                    patch_artist=True, medianprops=dict(color="#1565C0", linewidth=2))
    for box in bp["boxes"]:
        box.set(facecolor="#BBDEFB", edgecolor="#1565C0")

    # All circuits as jittered points so the distribution is visible.
    rng = np.random.default_rng(0)
    xj = 1 + (rng.random(len(pcts)) - 0.5) * 0.25
    ax.scatter(xj, pcts, s=18, color="#0D47A1", alpha=0.5, zorder=3)

    ax.axhline(s["mean_pct"], color="#388E3C", linestyle="--", linewidth=1.3,
               label=f"mean = {s['mean_pct']:+.1f}%")
    ax.axhline(s["median_pct"], color="#E53935", linestyle="-", linewidth=1.3,
               label=f"median = {s['median_pct']:+.1f}%")
    ax.axhline(0.0, color="gray", linestyle=":", linewidth=1.0)

    stats_txt = (
        f"circuits: {s['n']}\n"
        f"mean: {s['mean_pct']:+.1f}%   median: {s['median_pct']:+.1f}%\n"
        f"geomean ratio (WISQ/ours): ×{s['geomean_ratio']:.2f}\n"
        f"IQR: {s['p25_pct']:+.1f}% … {s['p75_pct']:+.1f}%   std: {s['std_pct']:.1f}%\n"
        f"min/max: {s['min_pct']:+.1f}% / {s['max_pct']:+.1f}%\n"
        f"ours smaller: {s['ours_smaller']}   ties: {s['ties']}   "
        f"WISQ smaller: {s['wisq_smaller']}\n"
        f"total qubits — ours: {s['our_total_qubits']:.0f}  "
        f"WISQ: {s['wisq_total_qubits']:.0f}  "
        f"saved: {s['total_qubits_saved']:.0f}"
    )
    ax.text(0.98, 0.02, stats_txt, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=9, family="monospace",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))

    ax.set_xticks([1])
    ax.set_xticklabels([f"all circuits (n={s['n']})"])
    ax.set_ylabel("WISQ extra grid area vs ours  (%)")
    ax.set_title("Grid-size gap over all circuits\n"
                 "(% = (wisq_area − our_area) / our_area · 100; >0 ⇒ WISQ bigger)",
                 fontweight="bold", fontsize=11)
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    plt.tight_layout()
    out_path = out_dir / "grid_overview.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")
    print(f"    [grid overview] n={s['n']} mean={s['mean_pct']:+.2f}% "
          f"median={s['median_pct']:+.2f}% geomean_ratio=x{s['geomean_ratio']:.3f} "
          f"ours_smaller={s['ours_smaller']} ties={s['ties']} "
          f"wisq_smaller={s['wisq_smaller']} qubits_saved={s['total_qubits_saved']:.0f}")


def plot_grid_pct_vs_qubits(by_circuit: dict[str, list[dict]], out_dir: Path) -> None:
    """Scatter of the per-circuit grid-size % difference vs qubit count, with a
    least-squares trend line (slope + Pearson r computed from the CSV points).
    Shows whether our footprint advantage grows or saturates with circuit size."""
    entries = [e for e in smallest_grid_entries(by_circuit) if e["n_qubits"] is not None]
    if len(entries) < 2:
        print("  (need ≥2 circuits with n_qubits; skipping grid % vs qubits)")
        return

    xs = np.array([e["n_qubits"] for e in entries], dtype=float)
    ys = np.array([e["pct"] for e in entries], dtype=float)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(xs, ys, s=30, color="#1565C0", alpha=0.7, label=f"circuits (n={len(xs)})")
    ax.axhline(0.0, color="gray", linestyle=":", linewidth=1.0)

    # Linear trend (degree-1 least squares) + Pearson correlation.
    slope, intercept = np.polyfit(xs, ys, 1)
    order = np.argsort(xs)
    ax.plot(xs[order], slope * xs[order] + intercept, color="#E53935", linewidth=1.6,
            label=f"trend: {slope:+.3f}%/qubit")
    r = float(np.corrcoef(xs, ys)[0, 1])

    ax.text(0.02, 0.98, f"slope = {slope:+.3f} %/qubit\nPearson r = {r:+.3f}",
            transform=ax.transAxes, ha="left", va="top", fontsize=9, family="monospace",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))

    ax.set_xlabel("circuit size (qubits)")
    ax.set_ylabel("WISQ extra grid area vs ours  (%)")
    ax.set_title("Grid-size gap vs circuit size", fontweight="bold")
    ax.legend(loc="upper right")
    ax.grid(True, linestyle=":", alpha=0.4)

    plt.tight_layout()
    out_path = out_dir / "grid_pct_vs_qubits.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")
    print(f"    [grid % vs qubits] slope={slope:+.4f}%/qubit pearson_r={r:+.4f}")


def plot_grid_pct_ccdf(by_circuit: dict[str, list[dict]], out_dir: Path) -> None:
    """Complementary CDF of the per-circuit grid-size % difference: for each
    threshold Y on the x-axis, the y-value is the fraction of circuits where WISQ
    uses ≥ Y% more grid area than ours. Reads e.g. "in 90% of circuits WISQ uses
    ≥ Y% more". Built directly from the CSV-derived percentages."""
    entries = smallest_grid_entries(by_circuit)
    if not entries:
        print("  (no rows with all grid dims; skipping grid % CCDF)")
        return

    pcts = np.sort(np.array([e["pct"] for e in entries], dtype=float))
    n = len(pcts)
    # survival[i] = fraction of circuits with pct >= pcts[i] = (n - i) / n
    survival = (n - np.arange(n)) / n

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.step(pcts, survival, where="post", color="#1565C0", linewidth=1.8)
    ax.scatter(pcts, survival, s=14, color="#0D47A1", alpha=0.6, zorder=3)
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=1.0)

    # Reference guide line at 90% of circuits (the example the user cares about).
    frac_ref = 0.90
    # largest threshold Y such that fraction(pct >= Y) >= 0.90 -> the 10th percentile.
    y_at_90 = float(np.percentile(pcts, 100 * (1 - frac_ref)))
    ax.axhline(frac_ref, color="#388E3C", linestyle="--", linewidth=1.0)
    ax.annotate(f"in 90% of circuits\nWISQ uses ≥ {y_at_90:+.1f}% more",
                xy=(y_at_90, frac_ref), xytext=(10, 20), textcoords="offset points",
                fontsize=9, color="#2E7D32",
                arrowprops=dict(arrowstyle="->", color="#2E7D32"))

    ax.set_xlabel("threshold Y: WISQ extra grid area vs ours  (%)")
    ax.set_ylabel("fraction of circuits with WISQ ≥ Y% bigger")
    ax.set_ylim(0, 1.02)
    ax.set_title(f"Grid-size gap — complementary CDF  (n={n})", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)

    plt.tight_layout()
    out_path = out_dir / "grid_pct_ccdf.png"
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  saved: {out_path}")
    print(f"    [grid % CCDF] n={n} 90%-of-circuits threshold={y_at_90:+.2f}%")


def plot_optimality(by_circuit: dict[str, list[dict]], out_dir: Path) -> None:
    """Scatter figures of our routing optimality, coloured by circuit family.

    optimality = min_routing_steps / my_routing_steps (layering-depth lower bound
    over the steps actually taken): 1 is perfect, smaller is further from optimal.

      * vs max_parallelism      -- the worst-case floor is the y = 1/x curve, so
        every point sits between y = 1/x (worst) and y = 1 (perfect).
      * vs each CNOT interaction-graph metric (density, modularity, diameter, avg
        shortest path, degree statistics, Gini coefficients, edge-weight stddev,
        clustering) -- whether more tangled interaction graphs route further from
        optimal. See CNOT_GRAPH_METRIC_SPECS.

    Needs the min_routing_steps / max_parallelism columns plus the relevant CNOT
    interaction-graph column in the CSV; rows missing them are skipped.
    """
    specs = [
        (PARALLELISM, "max parallelism (avg gates / layer)",
         "Routing Optimality vs Max Parallelism", "optimality_vs_max_parallelism.png", True),
    ]
    specs += [
        (col, xlabel, f"Routing Optimality vs {title}", f"optimality_vs_{slug}.png", False)
        for col, xlabel, title, slug in CNOT_GRAPH_METRIC_SPECS
    ]
    for x_key, xlabel, title, fname, worst_case_curve in specs:
        by_family: dict[str, list[tuple[float, float]]] = {}
        for circuit, rows in by_circuit.items():
            fam = circuit_family(circuit)
            for r in rows:
                steps = to_float(r.get(MINE_STEPS))
                min_steps = to_float(r.get(MIN_STEPS))
                x = to_float(r.get(x_key))
                if steps is None or min_steps is None or x is None or steps <= 0:
                    continue
                by_family.setdefault(fam, []).append((x, min_steps / steps))

        if not by_family:
            print(f"  (no rows with {MIN_STEPS} + {x_key}; skipping {fname})")
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


def plot_optimality_bars(by_circuit: dict[str, list[dict]], out_dir: Path) -> None:
    """Grouped bar charts: routing optimality of ours (blue) vs WISQ (red), one
    bar pair per circuit, with circuits ordered along the x-axis by a circuit
    metric. One figure per metric in CNOT_GRAPH_METRIC_SPECS.

    optimality = min_routing_steps / routing_steps (layering-depth lower bound
    over the steps actually taken; 1 = perfect, smaller = further from optimal).
    min_routing_steps is the circuit's dependency depth — a router-/mapping-
    independent lower bound — so it is the same numerator for both sides:

        ours optimality = min_routing_steps / our best my_routing_steps
        WISQ optimality = min_routing_steps / wisq_routing_steps

    Higher is better. No binning/aggregation: every circuit keeps its own bar
    pair; circuits that share a metric value simply sit next to each other (the
    x tick shows the metric value, so equal values read as one bin of bars).
    """
    for col, xlabel, title, slug in CNOT_GRAPH_METRIC_SPECS:
        entries = []
        for circuit, rows in by_circuit.items():
            best, _ = pick_best_worst(rows)
            min_steps = to_float(best.get(MIN_STEPS))
            my_steps = to_float(best.get(MINE_STEPS))
            wisq_steps = to_float(best.get(WISQ_STEPS))
            x = to_float(best.get(col))
            if None in (min_steps, my_steps, wisq_steps, x):
                continue
            if min_steps <= 0 or my_steps <= 0 or wisq_steps <= 0:
                continue
            entries.append((circuit, x, min_steps / my_steps, min_steps / wisq_steps))

        fname = f"optimality_bars_vs_{slug}.png"
        if not entries:
            print(f"  (no rows with {MIN_STEPS}/{MINE_STEPS}/{WISQ_STEPS} + {col}; skipping {fname})")
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


def plot_dim_diff(by_circuit: dict[str, list[dict]], out_dir: Path) -> None:
    """Bar chart of the per-side grid footprint gap vs WISQ, one bar per circuit.

    dim_diff_side = wisq_x - my_x (from compare_wisq_conn.py): how many fewer rows/
    cols per side our best config used than WISQ. Positive (green) = we are smaller
    than WISQ (the win); negative (red) = we needed a bigger grid. Circuits are
    ordered left->right by qubit count. Skipped if no circuit has the datum.
    """
    entries = []
    for circuit, rows in by_circuit.items():
        best, _ = pick_best_worst(rows)
        d = dim_diff_per_side(best)
        if d is None:
            continue
        nq = to_float(best.get("n_qubits")) or 0.0
        entries.append((circuit, nq, d))

    if not entries:
        print("  (no dim_diff_side / grid columns; skipping summary_dim_diff.png)")
        return

    entries.sort(key=lambda e: (e[1], e[0]))
    circuits = [e[0] for e in entries]
    diffs = [e[2] for e in entries]

    EPS = 1e-9
    smaller = sum(1 for d in diffs if d > EPS)     # we use a smaller grid than WISQ
    equal = sum(1 for d in diffs if abs(d) <= EPS)
    bigger = sum(1 for d in diffs if d < -EPS)
    total = len(diffs)
    mean_d = sum(diffs) / total

    colors = ["#2A9D8F" if d > EPS else ("#E53935" if d < -EPS else "#9E9E9E")
              for d in diffs]

    x = np.arange(len(circuits))
    fig, ax = plt.subplots(figsize=(max(8, len(circuits) * 0.5), 6))
    ax.bar(x, diffs, color=colors, width=0.7, edgecolor="white")
    ax.axhline(0.0, color="#333333", linewidth=0.8)
    ax.axhline(mean_d, color="#1565C0", linestyle="--", linewidth=1.0,
               label=f"mean = {mean_d:+.2f}/side")

    summary = (f"ours smaller: {smaller}   equal: {equal}   ours bigger: {bigger}"
               f"   (of {total})")
    ax.text(0.5, 0.97, summary, transform=ax.transAxes, ha="center", va="top",
            fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD"))

    ax.set_xticks(x)
    ax.set_xticklabels(circuits, rotation=90, fontsize=8)
    ax.set_ylabel("WISQ side − our side  (cells per side)")
    ax.set_title(f"Grid footprint gap vs WISQ: positive = ours is smaller  "
                 f"({total} circuits)", fontweight="bold")
    ax.legend(loc="upper left")
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    plt.tight_layout()
    out_path = out_dir / "summary_dim_diff.png"
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

    # Grid footprint gap vs WISQ (per side), one bar per circuit. Needs
    # dim_diff_side (compare_wisq_conn.py) or my_x/wisq_x in the CSV.
    plot_dim_diff(by_circuit, out_dir)
    # Aggregate grid-size gap over all circuits (ours vs WISQ). Per circuit the
    # smallest-grid config is used; all numbers come straight from the CSV.
    plot_grid_overview(by_circuit, out_dir)
    plot_grid_pct_vs_qubits(by_circuit, out_dir)
    plot_grid_pct_ccdf(by_circuit, out_dir)

    # Routing-optimality scatters (ours), coloured by circuit family.
    plot_optimality(by_circuit, out_dir)

    # Routing-optimality grouped bar charts: ours (blue) vs WISQ (red) per
    # circuit, one figure per metric, x-ordered by that metric.
    plot_optimality_bars(by_circuit, out_dir)

    # Per-family overview figures (same as the summaries, restricted to each
    # family: qft, qaoa, vqe_su2, ...). Families with a single circuit are skipped.
    families = sorted({circuit_family(c) for c in by_circuit})
    for fam in families:
        plot_summary(by_circuit, out_dir, "steps", family=fam)
        plot_summary(by_circuit, out_dir, "time", family=fam)
        # Per-family line chart of grid size (area x·y): ours vs WISQ.
        plot_family_grid_size(by_circuit, out_dir, fam)

    return 0


if __name__ == "__main__":
    sys.exit(main())
