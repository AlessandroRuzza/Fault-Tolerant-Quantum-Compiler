#!/usr/bin/env python3
"""
Generate three separate PNG reports per circuit from a benchmark runs CSV.

  {circuit}_metrics.png    — horizontal bar chart: each metric's percentile
                             rank among all circuits that have metrics data
  {circuit}_top15_steps.png — top-15 configurations by routing steps
  {circuit}_top15_time.png  — top-15 configurations by execution time

Usage (from project root):
  python3 scripts/circuit_report.py <runs_csv> [options]

Examples:
  python3 scripts/circuit_report.py benchmarks/results/best_params_benchmark_runs.csv
  python3 scripts/circuit_report.py benchmarks/results/best_params_benchmark_runs.csv \\
      --circuits t_test qft_20
  python3 scripts/circuit_report.py benchmarks/results/my_run.csv \\
      --metrics benchmarks/results/cache_metrics/all_circuits_cache_metrics.csv \\
      --out     benchmarks/results/my_reports
"""

import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_METRICS = "benchmarks/results/cache_metrics/all_circuits_cache_metrics.csv"
DEFAULT_OUT     = "benchmarks/results/circuit_reports"

# ---------------------------------------------------------------------------
# Metric display names and grouping
# ---------------------------------------------------------------------------
METRIC_GROUPS = {
    "Gate structure": [
        ("total_routable_gates",      "Total gates"),
        ("num_logical_qubits",        "Logical qubits"),
        ("num_cnot",                  "CNOT count"),
        ("num_t_tdg",                 "T / Tdg count"),
        ("num_other_gates",           "Other gates"),
        ("t_count_ratio",             "T-gate ratio"),
        ("cnot_ratio",                "CNOT ratio"),
        ("other_gate_ratio",          "Other gate ratio"),
    ],
    "CNOT structure": [
        ("num_unique_cnot_pairs",     "Unique CNOT pairs"),
        ("max_cnot_pair_repetition",  "Max CNOT pair rep."),
        ("avg_cnot_pair_repetition",  "Avg CNOT pair rep."),
        ("cnot_interaction_density",  "CNOT interaction density"),
        ("max_cnot_degree",           "Max CNOT degree"),
    ],
    "T-gate structure": [
        ("t_qubit_diversity",         "T-qubit diversity"),
        ("t_depth",                   "T-depth"),
        ("t_layer_ratio",             "T-layer ratio"),
        ("avg_t_per_layer",           "Avg T per layer"),
        ("max_t_in_layer",            "Max T in layer"),
    ],
    "Layer structure": [
        ("total_layers",              "Total layers"),
        ("num_unique_layers",         "Unique layers"),
        ("layer_reuse_ratio",         "Layer reuse ratio"),
        ("depth_width_ratio",         "Depth / width ratio"),
        ("avg_layer_size",            "Avg layer size"),
        ("max_layer_size",            "Max layer size"),
        ("avg_cnot_per_layer",        "Avg CNOTs per layer"),
        ("max_cnot_in_layer",         "Max CNOTs in layer"),
        ("cnot_depth",                "CNOT depth"),
        ("layer_congestion_score",    "Layer congestion score"),
        ("max_repeated_seq_len",      "Max repeated seq. length"),
    ],
    "Path length": [
        ("avg_estimated_path_length", "Avg estimated path length"),
        ("max_estimated_path_length", "Max estimated path length"),
        ("path_length_stddev",        "Path length std dev"),
    ],
}

# Flat ordered list of (key, label) for iteration
METRIC_KEYS_ORDERED = [
    (key, label)
    for group_items in METRIC_GROUPS.values()
    for key, label in group_items
]

# Group colour palette (one per group)
GROUP_COLORS = {
    "Gate structure":   "#4e79a7",
    "CNOT structure":   "#f28e2b",
    "T-gate structure": "#e15759",
    "Layer structure":  "#76b7b2",
    "Path length":      "#59a14f",
}

# Config columns for the top-15 tables
CONFIG_COLS = [
    ("routing_steps",                   "Steps"),
    ("duration_seconds",                "Time (s)"),
    ("mapping_type",                    "Mapping"),
    ("safe_passage_strategy",           "Safe passage"),
    ("routing_strategy",                "Routing"),
    ("magic_state_placement_strategy",  "Magic placement"),
    ("number_of_magic_states",          "N magic"),
    ("border_distance_percentage",      "Border %"),
    ("t_routing_mode",                  "T-routing"),
    ("use_layer_cache",                 "Cache"),
    ("gaussian_strategy",               "Gaussian"),
    ("magic_aware_strategy",            "MA strategy"),
]

# Value abbreviations to keep table readable
VALUE_ABBREV = {
    "smart_t_routing":    "smart",
    "normal_t_routing":   "normal",
    "passage_no_subgraphs": "no_subgr.",
    "center_circle":      "ctr_circle",
    "magic_aware":        "magic_aw.",
}

COL_HEADER  = "#2c3e50"
COL_ALT     = "#f0f4f8"
COL_WHITE   = "#ffffff"
COLS_TOP3   = ["#fff3cd", "#e9ecef", "#ffe8d6"]  # gold, silver, bronze


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_runs(path: str) -> list:
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("status") != "success":
                continue
            try:
                row["routing_steps"]    = int(row["routing_steps"])
                row["duration_seconds"] = float(row.get("duration_seconds") or 0)
            except (ValueError, TypeError):
                continue
            if row["routing_steps"] <= 0:
                continue
            rows.append(row)
    return rows


def load_metrics(path: str) -> dict:
    data = {}
    try:
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                data[row["circuit"]] = row
    except FileNotFoundError:
        print(f"  Warning: metrics file not found: {path}")
    return data


def compute_rankings(metrics_by_circuit: dict) -> dict:
    """
    Returns {circuit: {metric_key: (value, rank, pct_lower, n_total)}}.
    rank=1 → highest value.  pct_lower = % of other circuits with a strictly
    lower value (i.e. how much this circuit "beats" the others for that metric).
    """
    circuits = list(metrics_by_circuit.keys())
    n = len(circuits)
    rankings: dict = defaultdict(dict)

    all_keys = [k for k, _ in METRIC_KEYS_ORDERED]

    for key in all_keys:
        vals = {}
        for c in circuits:
            try:
                vals[c] = float(metrics_by_circuit[c].get(key) or 0)
            except (ValueError, TypeError):
                vals[c] = 0.0

        sorted_desc = sorted(circuits, key=lambda c: vals[c], reverse=True)
        for rank0, c in enumerate(sorted_desc):
            v = vals[c]
            n_lower = sum(1 for c2 in circuits if c2 != c and vals[c2] < v)
            pct = n_lower / (n - 1) * 100 if n > 1 else 0.0
            rankings[c][key] = (v, rank0 + 1, pct, n)

    return rankings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ordinal(n: int) -> str:
    sfx = "th" if 11 <= (n % 100) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{sfx}"


def _fmt(val) -> str:
    try:
        f = float(val)
    except (ValueError, TypeError):
        return str(val)
    if f == int(f) and abs(f) < 1e9:
        return str(int(f))
    return f"{f:.4f}"


def _abbrev(v: str) -> str:
    return VALUE_ABBREV.get(str(v), str(v))


def _style_table_header(tbl, n_cols: int):
    for j in range(n_cols):
        c = tbl[0, j]
        c.set_facecolor(COL_HEADER)
        c.get_text().set_color("white")
        c.get_text().set_fontweight("bold")


def _style_table_rows(tbl, n_rows: int, n_cols: int):
    """Alternate rows; gold/silver/bronze for first three."""
    for i in range(1, n_rows + 1):
        if i <= 3:
            colour = COLS_TOP3[i - 1]
        else:
            colour = COL_ALT if i % 2 == 0 else COL_WHITE
        for j in range(n_cols):
            tbl[i, j].set_facecolor(colour)


# ---------------------------------------------------------------------------
# Plot 1: metrics bar chart
# ---------------------------------------------------------------------------

def save_metrics_figure(circuit: str, rankings: dict,
                        n_metrics_circuits: int, out_path: Path):

    circ_data = rankings.get(circuit, {})

    # Collect bars in group order
    bar_labels, bar_pcts, bar_colors, bar_vals, bar_ranks, bar_n = (
        [], [], [], [], [], []
    )
    group_boundaries = {}   # group_name -> (start_idx, end_idx) after appending

    idx = 0
    for group_name, items in METRIC_GROUPS.items():
        start = idx
        color = GROUP_COLORS[group_name]
        for key, label in items:
            if key not in circ_data:
                continue
            val, rank, pct, n_total = circ_data[key]
            bar_labels.append(label)
            bar_pcts.append(pct)
            bar_colors.append(color)
            bar_vals.append(val)
            bar_ranks.append(rank)
            bar_n.append(n_total)
            idx += 1
        if idx > start:
            group_boundaries[group_name] = (start, idx - 1)

    n_bars = len(bar_labels)

    if n_bars == 0:
        fig, ax = plt.subplots(figsize=(10, 3), facecolor="white")
        ax.axis("off")
        ax.text(0.5, 0.5,
                f"No metrics available for  '{circuit}'.\n"
                "Run:  python3 scripts/update_metrics.py",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=13, color="#888888")
        fig.suptitle(f"Circuit Metrics — {circuit}", fontsize=14,
                     fontweight="bold")
        fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return

    fig_height = max(8, n_bars * 0.42 + 2.5)
    fig, ax = plt.subplots(figsize=(15, fig_height), facecolor="white")

    y_pos = np.arange(n_bars)

    # Draw bars
    bars = ax.barh(y_pos, bar_pcts, color=bar_colors,
                   edgecolor="white", height=0.65, zorder=2)

    # Annotations: value + rank to the right of each bar
    for i in range(n_bars):
        pct  = bar_pcts[i]
        val  = _fmt(bar_vals[i])
        rank = bar_ranks[i]
        n_t  = bar_n[i]
        label = f"  {val}   ({_ordinal(rank)} / {n_t})"
        ax.text(min(pct + 1, 101), i, label,
                va="center", ha="left", fontsize=8, color="#333333")

    # Group separators and labels on the left
    for group_name, (start, end) in group_boundaries.items():
        mid = (start + end) / 2
        ax.text(-3, mid, group_name, va="center", ha="right",
                fontsize=8, color=GROUP_COLORS[group_name],
                fontweight="bold", style="italic")
        if start > 0:
            ax.axhline(y=start - 0.5, color="#cccccc", linewidth=0.8,
                       linestyle="--", zorder=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(bar_labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(-1, 130)
    ax.set_xlabel("% of circuits with a lower value  (higher = this circuit ranks higher)",
                  fontsize=9)
    ax.axvline(x=50, color="#aaaaaa", linestyle="--", linewidth=0.8, zorder=1)
    ax.text(50, -0.8, "50%", ha="center", va="top", fontsize=7.5, color="#888888")
    ax.grid(axis="x", color="#eeeeee", zorder=0)
    ax.set_axisbelow(True)

    # Legend for groups
    legend_patches = [
        mpatches.Patch(color=col, label=grp)
        for grp, col in GROUP_COLORS.items()
        if grp in group_boundaries
    ]
    ax.legend(handles=legend_patches, loc="lower right",
              fontsize=8, framealpha=0.8)

    title = f"Circuit Metrics — {circuit}"
    subtitle = (
        f"Comparing against {n_metrics_circuits} circuit(s) in the database"
        if n_metrics_circuits > 1
        else "⚠  Only 1 circuit in the metrics database — "
             "run  python3 scripts/update_metrics.py  for meaningful comparison"
    )
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    fig.text(0.5, 0.995, subtitle, ha="center", va="top",
             fontsize=8.5,
             color="#cc6600" if n_metrics_circuits <= 1 else "#555555",
             style="italic" if n_metrics_circuits <= 1 else "normal")

    fig.tight_layout(rect=[0, 0, 1, 0.99])
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 2 & 3: top-15 tables
# ---------------------------------------------------------------------------

def save_top15_figure(circuit: str, top_rows: list,
                      sort_col: str, title: str, out_path: Path):

    if not top_rows:
        fig, ax = plt.subplots(figsize=(10, 3), facecolor="white")
        ax.axis("off")
        ax.text(0.5, 0.5, "No data available.",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=13, color="#888888")
        fig.suptitle(title, fontsize=13, fontweight="bold")
        fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return

    # Put the sort column first; then the other metric; then config cols
    if sort_col == "routing_steps":
        ordered_cols = [
            ("routing_steps",  "Steps"),
            ("duration_seconds", "Time (s)"),
        ]
    else:
        ordered_cols = [
            ("duration_seconds", "Time (s)"),
            ("routing_steps",  "Steps"),
        ]
    rest = [(k, h) for k, h in CONFIG_COLS if k not in ("routing_steps", "duration_seconds")]
    ordered_cols += rest

    col_headers = ["#"] + [h for _, h in ordered_cols]
    n_cols = len(col_headers)

    cell_data = []
    for rank, row in enumerate(top_rows, start=1):
        cells = [str(rank)]
        for key, _ in ordered_cols:
            v = row.get(key, "")
            if key == "duration_seconds":
                try:
                    v = f"{float(v):.3f}"
                except (ValueError, TypeError):
                    pass
            elif key == "routing_steps":
                try:
                    v = str(int(v))
                except (ValueError, TypeError):
                    pass
            elif key == "use_layer_cache":
                v = "yes" if str(v).lower() == "true" else "no"
            elif key == "number_of_magic_states":
                # Prefer the runtime-resolved value (after multiplier or the
                # -1 proportional sentinel) when the CSV provides it.
                resolved = row.get("resolved_n_magic", "")
                if resolved not in ("", None):
                    v = resolved
            elif key == "magic_aware_strategy" and row.get("mapping_type") != "magic_aware":
                v = "—"
            elif key == "gaussian_strategy" and row.get("mapping_type") != "gaussian":
                v = "—"
            else:
                v = _abbrev(str(v))
            cells.append(str(v))
        cell_data.append(cells)

    n_rows = len(cell_data)

    fig, ax = plt.subplots(figsize=(24, max(4, n_rows * 0.52 + 1.8)),
                           facecolor="white")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

    tbl = ax.table(
        cellText=cell_data,
        colLabels=col_headers,
        cellLoc="center",
        loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.6)

    _style_table_header(tbl, n_cols)
    _style_table_rows(tbl, n_rows, n_cols)

    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Plot 4 & 5: global parameter frequency across best configs
# ---------------------------------------------------------------------------

FREQ_PARAMS = [
    ("mapping_type",                   "Mapping",         None),
    ("safe_passage_strategy",          "Safe passage",    None),
    ("routing_strategy",               "Routing",         None),
    ("t_routing_mode",                 "T-routing",       None),
    ("use_layer_cache",                "Cache",           None),
    ("magic_state_placement_strategy", "Magic placement", None),
    ("gaussian_strategy",              "Gaussian",        "gaussian"),
    ("magic_aware_strategy",           "MA strategy",     "magic_aware"),
]

FREQ_COLORS = [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
    "#59a14f", "#edc948", "#b07aa1", "#ff9da7", "#9c755f",
]


def save_param_frequency_figure(best_rows: list, sort_label: str, out_path: Path):
    """Bar-chart grid: for each parameter, how many times each value
    appears as the best configuration across all circuits."""
    if not best_rows:
        return

    from collections import Counter

    n_params = len(FREQ_PARAMS)
    ncols = 3
    nrows = (n_params + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(ncols * 6, nrows * 3.8),
                             facecolor="white")
    axes_flat = axes.flatten()

    for idx, (key, label, mapping_filter) in enumerate(FREQ_PARAMS):
        ax = axes_flat[idx]

        subset = best_rows
        if mapping_filter is not None:
            subset = [r for r in best_rows if r.get("mapping_type") == mapping_filter]

        counts = Counter()
        for r in subset:
            v = r.get(key, "")
            if key == "use_layer_cache":
                v = "yes" if str(v).lower() == "true" else "no"
            else:
                v = _abbrev(str(v)) if v else "—"
            counts[v] += 1

        if not counts:
            ax.axis("off")
            ax.set_title(label, fontsize=11, fontweight="bold")
            continue

        labels_sorted = sorted(counts.keys(), key=lambda x: -counts[x])
        values = [counts[l] for l in labels_sorted]
        colors = [FREQ_COLORS[i % len(FREQ_COLORS)] for i in range(len(labels_sorted))]

        bars = ax.bar(labels_sorted, values, color=colors,
                      edgecolor="white", zorder=2)
        ax.bar_label(bars, padding=3, fontsize=9, fontweight="bold")

        title = label
        if mapping_filter:
            title += f" (only {mapping_filter})"
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.set_ylabel("# circuits", fontsize=9)
        ax.set_ylim(0, max(values) * 1.25)
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=8)
        ax.grid(axis="y", color="#eeeeee", zorder=0)
        ax.set_axisbelow(True)

        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

    # Hide unused subplots
    for idx in range(n_params, len(axes_flat)):
        axes_flat[idx].axis("off")

    n = len(best_rows)
    fig.suptitle(
        f"Parameter frequency in best configs — sorted by {sort_label}  ({n} circuits)",
        fontsize=14, fontweight="bold", y=1.01,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Per-circuit entry point
# ---------------------------------------------------------------------------

def make_reports(circuit: str, runs: list, rankings: dict,
                 n_metrics_circuits: int, out_dir: Path):

    circ_runs = [r for r in runs if r["circuit"] == circuit]
    if not circ_runs:
        print(f"    Skip {circuit}: no successful runs")
        return

    top_steps = sorted(circ_runs, key=lambda r: (r["routing_steps"], r["duration_seconds"]))[:15]
    top_time  = sorted(circ_runs, key=lambda r: (r["duration_seconds"], r["routing_steps"]))[:15]

    save_metrics_figure(
        circuit, rankings, n_metrics_circuits,
        out_dir / f"{circuit}_metrics.png",
    )
    save_top15_figure(
        circuit, top_steps, "routing_steps",
        f"Top 15 Configurations — {circuit} — by Routing Steps  (lower = better)",
        out_dir / f"{circuit}_top15_steps.png",
    )
    save_top15_figure(
        circuit, top_time, "duration_seconds",
        f"Top 15 Configurations — {circuit} — by Execution Time  (lower = better)",
        out_dir / f"{circuit}_top15_time.png",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate per-circuit benchmark reports (3 PNG files each).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "runs",
        help="Path to benchmark runs CSV (required)",
    )
    parser.add_argument(
        "--metrics", default=DEFAULT_METRICS,
        help=f"Path to circuit metrics CSV  [default: {DEFAULT_METRICS}]",
    )
    parser.add_argument(
        "--out", default=DEFAULT_OUT,
        help=f"Output directory for PNG reports  [default: {DEFAULT_OUT}]",
    )
    parser.add_argument(
        "--circuits", nargs="*",
        help="Restrict to specific circuit names",
    )
    args = parser.parse_args()

    print(f"Loading runs    : {args.runs}")
    runs = load_runs(args.runs)
    print(f"  {len(runs):,} successful runs")

    print(f"Loading metrics : {args.metrics}")
    metrics_by_circuit = load_metrics(args.metrics)
    n_metrics = len(metrics_by_circuit)
    print(f"  {n_metrics} circuit(s) have metrics")

    rankings = compute_rankings(metrics_by_circuit)

    circuits = sorted(set(r["circuit"] for r in runs))
    if args.circuits:
        circuits = [c for c in circuits if c in args.circuits]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating reports for {len(circuits)} circuit(s) → {args.out}/")
    for circ in circuits:
        print(f"  {circ}")
        make_reports(circ, runs, rankings, n_metrics, out_dir)

    # Global frequency plots: best config per circuit (steps / time)
    print("\nGenerating global parameter frequency plots...")
    all_circ_runs = {c: [r for r in runs if r["circuit"] == c] for c in circuits}

    best_by_steps = [
        sorted(rows, key=lambda r: (r["routing_steps"], r["duration_seconds"]))[0]
        for rows in all_circ_runs.values() if rows
    ]
    best_by_time = [
        sorted(rows, key=lambda r: (r["duration_seconds"], r["routing_steps"]))[0]
        for rows in all_circ_runs.values() if rows
    ]

    save_param_frequency_figure(
        best_by_steps, "routing steps",
        out_dir / "param_frequency_steps.png",
    )
    save_param_frequency_figure(
        best_by_time, "execution time",
        out_dir / "param_frequency_time.png",
    )

    total = len(circuits) * 3 + 2
    print(f"\nDone — {total} files written to {args.out}/")


if __name__ == "__main__":
    main()
