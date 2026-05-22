#!/usr/bin/env python3
"""
For every numeric column in all_circuits_cache_metrics.csv, produce one bar
chart with circuits sorted by that column's value (ascending).

Output: benchmarks/results/cache_metrics/plots/<column_name>.png

Usage:
  python3 scripts/plot_metrics_per_param.py [--csv <path>] [--out-dir <path>]
"""

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = (
    PROJECT_ROOT / "benchmarks" / "results" / "cache_metrics"
    / "all_circuits_cache_metrics.csv"
)
DEFAULT_OUT = DEFAULT_CSV.parent / "plots"

SKIP_COLUMNS = {"circuit", "layer_size_distribution", "top5_layer_frequencies"}

# Human-readable title and subtitle for each column.
# Format: (short title, explanation subtitle)
COLUMN_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    "total_routable_gates":       ("Total routable gates",
                                   "Number of gates that require physical routing (CX, T/Tdg, single-qubit)"),
    "num_logical_qubits":         ("Logical qubits",
                                   "Number of distinct qubits used by the circuit"),
    "num_cnot":                   ("CNOT count",
                                   "Total number of two-qubit CX gates"),
    "num_t_tdg":                  ("T/Tdg count",
                                   "Total number of T and Tdg (T-dagger) gates"),
    "num_other_gates":            ("Other gates count",
                                   "Gates that are neither CX nor T/Tdg (H, RZ, X, S, CCX, …)"),
    "t_count_ratio":              ("T-count ratio",
                                   "Fraction of total gates that are T/Tdg  [0–1]"),
    "cnot_ratio":                 ("CNOT ratio",
                                   "Fraction of total gates that are CX  [0–1]"),
    "other_gate_ratio":           ("Other-gate ratio",
                                   "Fraction of total gates that are neither CX nor T/Tdg  [0–1]"),
    "num_unique_cnot_pairs":      ("Unique CNOT qubit pairs",
                                   "Number of distinct (qi, qj) qubit pairs connected by at least one CX"),
    "max_cnot_pair_repetition":   ("Max CNOT pair repetition",
                                   "Maximum times the same (qi, qj) pair appears as a CX gate"),
    "avg_cnot_pair_repetition":   ("Avg CNOT pair repetition",
                                   "Average number of CX repetitions per unique qubit pair"),
    "cnot_interaction_density":   ("CNOT interaction density",
                                   "Fraction of all possible qubit pairs used in at least one CX  [0–1]"),
    "max_cnot_degree":            ("Max CNOT degree",
                                   "Highest number of distinct CX partners any single qubit has (hub qubit)"),
    "t_qubit_diversity":          ("T-qubit diversity",
                                   "Number of distinct qubits that receive at least one T/Tdg gate"),
    "total_layers":               ("Circuit depth (total layers)",
                                   "Number of layers after greedy layering — equals the circuit depth"),
    "num_unique_layers":          ("Unique layers",
                                   "Number of layers with a distinct gate-set fingerprint"),
    "layer_reuse_ratio":          ("Layer reuse ratio",
                                   "(total_layers − unique_layers) / total_layers — fraction of layers that repeat  [0–1]"),
    "depth_width_ratio":          ("Depth / width ratio",
                                   "total_layers / num_qubits — how 'tall' vs 'wide' the circuit is"),
    "avg_layer_size":             ("Avg layer size (gates/layer)",
                                   "Average number of gates executed in parallel per layer"),
    "max_layer_size":             ("Max layer size",
                                   "Peak number of gates in a single layer — maximum parallelism"),
    "avg_cnot_per_layer":         ("Avg CX gates per layer",
                                   "Average number of CX gates per layer"),
    "avg_t_per_layer":            ("Avg T/Tdg gates per layer",
                                   "Average number of T/Tdg gates per layer"),
    "max_t_in_layer":             ("Max T/Tdg in one layer",
                                   "Largest number of T/Tdg gates that appear in a single layer"),
    "max_cnot_in_layer":          ("Max CX in one layer",
                                   "Largest number of CX gates that appear in a single layer"),
    "t_depth":                    ("T-depth",
                                   "Number of layers that contain at least one T/Tdg gate"),
    "cnot_depth":                 ("CNOT depth",
                                   "Number of layers that contain at least one CX gate"),
    "t_layer_ratio":              ("T-layer ratio",
                                   "t_depth / total_layers — fraction of layers that contain T/Tdg gates  [0–1]"),
    "layer_congestion_score":     ("Layer size CV (parallelism variability)",
                                   "Coefficient of variation of layer sizes (std/mean) — high = uneven parallelism"),
    "max_repeated_seq_len":       ("Max repeated sequence length",
                                   "Longest consecutive block of layers that appears at least twice in the circuit"),
    "avg_estimated_path_length":  ("Avg estimated path length (post-mapping)",
                                   "Average Manhattan distance between mapped nodes of CX gate qubits — 0 if no mapping was run"),
    "max_estimated_path_length":  ("Max estimated path length (post-mapping)",
                                   "Maximum Manhattan distance between mapped nodes of any CX gate — 0 if no mapping was run"),
    "path_length_stddev":         ("Path length std-dev (post-mapping)",
                                   "Population std-dev of CX path lengths — measures routing heterogeneity; 0 if no mapping was run"),
}


def load_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            parsed: dict = {}
            for k, v in row.items():
                if k in SKIP_COLUMNS:
                    parsed[k] = v
                else:
                    try:
                        parsed[k] = float(v)
                    except (ValueError, TypeError):
                        parsed[k] = None
            rows.append(parsed)
    return rows


def plot_column(rows: list[dict], col: str, out_path: Path) -> None:
    valid = [(r["circuit"], r[col]) for r in rows if r[col] is not None]
    if not valid:
        print(f"  skip {col}: no valid data")
        return

    valid.sort(key=lambda x: x[1])
    labels = [x[0] for x in valid]
    values = np.array([x[1] for x in valid], dtype=float)

    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 0.48), 5.5))

    norm = plt.Normalize(vmin=values.min(), vmax=values.max())
    colors = cm.viridis(norm(values))
    bars = ax.bar(range(len(labels)), values, color=colors, edgecolor="none")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=8)
    ax.set_ylabel(col, fontsize=9)
    ax.grid(axis="y", alpha=0.3, linewidth=0.6)
    ax.set_xlim(-0.6, len(labels) - 0.4)

    # Title + subtitle from the descriptions table, falling back to the raw column name.
    if col in COLUMN_DESCRIPTIONS:
        short_title, subtitle = COLUMN_DESCRIPTIONS[col]
        ax.set_title(f"{short_title}\n", fontsize=12, fontweight="bold")
        fig.text(0.5, 0.97, subtitle, ha="center", va="top", fontsize=8,
                 style="italic", color="#444444",
                 transform=fig.transFigure, wrap=True)
    else:
        ax.set_title(col, fontsize=12, fontweight="bold")

    # Value labels on bars (only when there is meaningful variation).
    if values.max() != values.min():
        for bar, v in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{v:.2g}",
                ha="center", va="bottom", fontsize=6,
            )

    sm = cm.ScalarMappable(cmap="viridis", norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, shrink=0.7, label=col)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"ERROR: CSV not found at {args.csv}", file=sys.stderr)
        print("Run: python3 src/update_metrics.py", file=sys.stderr)
        sys.exit(1)

    rows = load_csv(args.csv)
    if not rows:
        print("ERROR: CSV is empty", file=sys.stderr)
        sys.exit(1)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    numeric_cols = [
        c for c in rows[0]
        if c not in SKIP_COLUMNS and rows[0][c] is not None
    ]

    print(f"Loaded {len(rows)} circuits, {len(numeric_cols)} numeric columns.")
    print(f"Output: {args.out_dir}\n")

    for col in numeric_cols:
        out_path = args.out_dir / f"{col}.png"
        print(f"  {col}")
        plot_column(rows, col, out_path)

    print(f"\nDone. {len(numeric_cols)} plots saved to {args.out_dir}")


if __name__ == "__main__":
    main()
