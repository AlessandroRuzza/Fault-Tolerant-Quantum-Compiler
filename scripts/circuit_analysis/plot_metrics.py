#!/usr/bin/env python3
"""
Plot circuit metrics from all_circuits_cache_metrics.csv (no pandas).

Two views, selectable via flags (default: produce both):

  --dashboard   one 10-panel overview figure (cache_metrics_dashboard.png):
                complexity, gate composition, layer reuse, layer size,
                congestion, path length, CNOT connectivity, T-gates, repetition.

  --per-param   one bar chart per numeric column, circuits sorted ascending,
                with a human-readable title/subtitle  (<column_name>.png).

Usage:
  python3 scripts/circuit_analysis/plot_metrics.py [--csv <path>] [--out-dir <path>]
                                                   [--dashboard] [--per-param]
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CSV = (
    PROJECT_ROOT / "benchmarks" / "results" / "cache_metrics"
    / "all_circuits_cache_metrics.csv"
)
DEFAULT_OUT = DEFAULT_CSV.parent / "plots"

SKIP_COLUMNS = {"circuit", "layer_size_distribution", "top5_layer_frequencies"}

# Human-readable title and subtitle for each column (per-param view).
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
    "avg_cnot_degree":            ("Avg CNOT degree",
                                   "Average number of distinct CX partners per qubit"),
    "cnot_degree_gini":           ("CNOT degree Gini",
                                   "Inequality of the per-qubit CX degree distribution [0=uniform, 1=star]"),
    "cnot_graph_modularity":      ("CNOT graph modularity",
                                   "Community structure of the CX interaction graph [0=none, ~1=clustered]"),
    "cnot_pair_rep_gini":         ("CNOT pair-repetition Gini",
                                   "Inequality of per-pair CX repetition counts [0=all pairs equal, 1=few hotspots]"),
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
    "density":                    ("Density (circuit fill)",
                                   "total_gates / (num_qubits × total_layers) — fraction of qubit×layer slots occupied  [0–1]"),
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


def load_csv(path: Path) -> list:
    """Parse the CSV: numeric columns -> float (None if unparseable),
    identity/text columns kept as strings."""
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            parsed = {}
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


# ---------------------------------------------------------------------------
# Dashboard view (9 panels)
# ---------------------------------------------------------------------------
def plot_dashboard(data: list, out_path: Path) -> None:
    n = len(data)
    circuits = [d["circuit"] for d in data]

    def col(name):
        return [d[name] for d in data]

    fig = plt.figure(figsize=(24, 14))

    ax1 = plt.subplot(3, 4, 1)
    qubits = col("num_logical_qubits")
    gates = [g / 10 for g in col("total_routable_gates")]
    layers = col("total_layers")
    x = np.arange(n); w = 0.25
    ax1.bar(x - w, qubits, w, label="Qubits", alpha=0.8)
    ax1.bar(x, gates, w, label="Gates (÷10)", alpha=0.8)
    ax1.bar(x + w, layers, w, label="Layers", alpha=0.8)
    ax1.set_ylabel("Count"); ax1.set_title("Circuit Complexity Overview", fontweight="bold")
    ax1.set_xticks(x); ax1.set_xticklabels([c[:12] for c in circuits], rotation=45, ha="right", fontsize=8)
    ax1.legend(); ax1.grid(axis="y", alpha=0.3)

    ax2 = plt.subplot(3, 4, 2)
    sc = ax2.scatter(col("cnot_ratio"), col("t_count_ratio"), s=100, alpha=0.6,
                     c=col("total_routable_gates"), cmap="viridis")
    ax2.set_xlabel("CNOT Ratio"); ax2.set_ylabel("T-count Ratio")
    ax2.set_title("Gate Composition", fontweight="bold")
    plt.colorbar(sc, ax=ax2, label="Total Gates"); ax2.grid(alpha=0.3)

    ax3 = plt.subplot(3, 4, 3)
    reuse = col("layer_reuse_ratio")
    colors = plt.cm.RdYlGn(np.array(reuse) / max(reuse) if max(reuse) > 0 else np.array(reuse))
    ax3.barh(range(n), reuse, color=colors)
    ax3.set_yticks(range(n)); ax3.set_yticklabels([c[:12] for c in circuits], fontsize=8)
    ax3.set_xlabel("Layer Reuse Ratio"); ax3.set_title("Layer Reuse Potential", fontweight="bold")
    ax3.grid(axis="x", alpha=0.3)

    ax4 = plt.subplot(3, 4, 4)
    congestion = col("layer_congestion_score")
    sc = ax4.scatter(col("avg_layer_size"), col("max_layer_size"),
                     s=np.array(col("total_routable_gates")) * 0.5, alpha=0.6,
                     c=congestion, cmap="coolwarm")
    ax4.set_xlabel("Avg Layer Size"); ax4.set_ylabel("Max Layer Size")
    ax4.set_title("Layer Size Distribution", fontweight="bold")
    plt.colorbar(sc, ax=ax4, label="Congestion"); ax4.grid(alpha=0.3)

    ax5 = plt.subplot(3, 4, 5)
    idx = sorted(range(n), key=lambda i: congestion[i])
    sc_c = [congestion[i] for i in idx]
    colors = plt.cm.Spectral(np.array(sc_c) / max(sc_c) if max(sc_c) > 0 else np.array(sc_c))
    ax5.barh(range(n), sc_c, color=colors)
    ax5.set_yticks(range(n)); ax5.set_yticklabels([circuits[i][:12] for i in idx], fontsize=8)
    ax5.set_xlabel("Congestion Score"); ax5.set_title("Layer Congestion (lower=balanced)", fontweight="bold")
    ax5.grid(axis="x", alpha=0.3)

    ax6 = plt.subplot(3, 4, 6)
    sc = ax6.scatter(col("avg_estimated_path_length"), col("max_estimated_path_length"),
                     s=np.array(qubits) * 10, alpha=0.6, c=col("num_cnot"), cmap="plasma")
    ax6.set_xlabel("Avg Path Length"); ax6.set_ylabel("Max Path Length")
    ax6.set_title("Routing Path Metrics", fontweight="bold")
    plt.colorbar(sc, ax=ax6, label="CNOT Gates"); ax6.grid(alpha=0.3)

    ax7 = plt.subplot(3, 4, 7)
    sc = ax7.scatter(col("num_unique_cnot_pairs"), col("avg_cnot_pair_repetition"),
                     s=np.array(col("num_cnot")) * 0.3, alpha=0.6, c=qubits, cmap="coolwarm")
    ax7.set_xlabel("Unique CNOT Pairs"); ax7.set_ylabel("Avg Pair Repetition")
    ax7.set_title("CNOT Connectivity", fontweight="bold")
    plt.colorbar(sc, ax=ax7, label="Qubits"); ax7.grid(alpha=0.3)

    ax8 = plt.subplot(3, 4, 8)
    ax8.bar(range(n), col("num_t_tdg"), alpha=0.7, color="steelblue")
    ax8t = ax8.twinx()
    ax8t.plot(range(n), col("avg_t_per_layer"), "ro-", linewidth=2, markersize=6)
    ax8.set_ylabel("Total T gates", color="steelblue"); ax8t.set_ylabel("Avg T per layer", color="red")
    ax8.set_title("T-gate Distribution", fontweight="bold")
    ax8.set_xticks(range(n)); ax8.set_xticklabels([c[:10] for c in circuits], rotation=45, ha="right", fontsize=8)
    ax8.grid(axis="y", alpha=0.3)

    ax9 = plt.subplot(3, 4, 9)
    rep_len = col("max_repeated_seq_len")
    mx = max(rep_len) if rep_len else 1
    colors = plt.cm.YlOrRd(np.array(rep_len) / mx if mx > 0 else np.array(rep_len))
    ax9.barh(range(n), rep_len, color=colors)
    ax9.set_yticks(range(n)); ax9.set_yticklabels([c[:12] for c in circuits], fontsize=8)
    ax9.set_xlabel("Max Repeated Seq Length"); ax9.set_title("Layer Pattern Repetition", fontweight="bold")
    ax9.grid(axis="x", alpha=0.3)

    ax10 = plt.subplot(3, 4, 10)
    dens = col("density")
    idx = sorted(range(n), key=lambda i: dens[i])
    dens_s = [dens[i] for i in idx]
    colors = plt.cm.viridis(np.array(dens_s) / max(dens_s) if max(dens_s) > 0 else np.array(dens_s))
    ax10.barh(range(n), dens_s, color=colors)
    ax10.set_yticks(range(n)); ax10.set_yticklabels([circuits[i][:12] for i in idx], fontsize=8)
    ax10.set_xlabel("Density = gates/(qubits×layers)")
    ax10.set_title("Circuit Density (fill ratio)", fontweight="bold")
    ax10.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  dashboard -> {out_path}")


# ---------------------------------------------------------------------------
# Per-parameter view (one bar chart per column)
# ---------------------------------------------------------------------------
def plot_column(rows: list, col: str, out_path: Path) -> None:
    valid = [(r["circuit"], r[col]) for r in rows if r[col] is not None]
    if not valid:
        return
    valid.sort(key=lambda x: x[1])
    labels = [x[0] for x in valid]
    values = np.array([x[1] for x in valid], dtype=float)

    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 0.48), 5.5))
    norm = plt.Normalize(vmin=values.min(), vmax=values.max())
    bars = ax.bar(range(len(labels)), values, color=cm.viridis(norm(values)), edgecolor="none")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=8)
    ax.set_ylabel(col, fontsize=9)
    ax.grid(axis="y", alpha=0.3, linewidth=0.6)
    ax.set_xlim(-0.6, len(labels) - 0.4)

    if col in COLUMN_DESCRIPTIONS:
        short_title, subtitle = COLUMN_DESCRIPTIONS[col]
        ax.set_title(f"{short_title}\n", fontsize=12, fontweight="bold")
        fig.text(0.5, 0.97, subtitle, ha="center", va="top", fontsize=8,
                 style="italic", color="#444444", transform=fig.transFigure, wrap=True)
    else:
        ax.set_title(col, fontsize=12, fontweight="bold")

    if values.max() != values.min():
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{v:.2g}", ha="center", va="bottom", fontsize=6)

    sm = cm.ScalarMappable(cmap="viridis", norm=norm); sm.set_array([])
    fig.colorbar(sm, ax=ax, shrink=0.7, label=col)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--dashboard", action="store_true", help="only the 9-panel overview")
    p.add_argument("--per-param", action="store_true", help="only the per-column bar charts")
    args = p.parse_args()

    if not args.csv.exists():
        print(f"ERROR: CSV not found at {args.csv}", file=sys.stderr)
        print("Run: python3 scripts/circuit_analysis/update_metrics.py", file=sys.stderr)
        sys.exit(1)

    # No flag => do both.
    do_dash = args.dashboard or not (args.dashboard or args.per_param)
    do_param = args.per_param or not (args.dashboard or args.per_param)

    rows = load_csv(args.csv)
    if not rows:
        print("ERROR: CSV is empty", file=sys.stderr)
        sys.exit(1)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Loaded {len(rows)} circuits. Output: {args.out_dir}")

    if do_dash:
        plot_dashboard(rows, args.out_dir / "cache_metrics_dashboard.png")

    if do_param:
        numeric_cols = [c for c in rows[0] if c not in SKIP_COLUMNS and rows[0][c] is not None]
        for c in numeric_cols:
            plot_column(rows, c, args.out_dir / f"{c}.png")
        print(f"  per-param -> {len(numeric_cols)} charts in {args.out_dir}")

    print("Done.")


if __name__ == "__main__":
    main()
