#!/usr/bin/env python3
"""
Show which circuit characteristics drive gaussian's routing performance.

Performance = routing overhead = routing_steps / total_layers
(1.0 = ideal, no inflation; higher = more routing steps per ideal layer).

From a gaussian runs CSV it takes, per circuit, the best (lowest) routing_steps,
divides by total_layers (from the metrics CSV), then produces:

  overhead_vs_<metric>.png   one scatter per circuit characteristic (overhead
                             vs that metric) with trend line + Spearman/R^2.
  overhead_correlations.png  ranked |Spearman| of overhead against EVERY
                             numeric circuit characteristic.

Usage:
  python3 scripts/circuit_analysis/gaussian_overhead_plot.py <gaussian_runs_csv> \
      [--metrics <csv>] [--out-dir <dir>]
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_METRICS = PROJECT_ROOT / "benchmarks" / "results" / "cache_metrics" / "all_circuits_cache_metrics.csv"

# columns that are not circuit characteristics
SKIP_COLUMNS = {"circuit", "layer_size_distribution", "top5_layer_frequencies", "total_layers"}

# nice axis labels (fallback to raw column name)
LABELS = {
    "max_cnot_degree": "Max CNOT degree",
    "avg_cnot_degree": "Avg CNOT degree",
    "cnot_interaction_density": "Interaction density",
    "avg_cnot_per_layer": "Avg CNOT / layer",
    "max_cnot_in_layer": "Max CNOT in layer",
    "depth_width_ratio": "Depth / width ratio",
    "density": "Density (fill ratio)",
    "num_logical_qubits": "Qubits",
    "cnot_graph_modularity": "Modularity",
    "cnot_degree_gini": "CNOT degree Gini",
    "cnot_pair_rep_gini": "Pair-rep Gini",
    "t_count_ratio": "T-count ratio",
    "cnot_ratio": "CNOT ratio",
    "other_gate_ratio": "Other-gate ratio",
    "layer_reuse_ratio": "Layer reuse",
    "num_cnot": "CNOT count",
    "num_t_tdg": "T/Tdg count",
    "total_routable_gates": "Total gates",
    "num_unique_cnot_pairs": "Unique CNOT pairs",
    "avg_cnot_pair_repetition": "Avg pair repetition",
    "max_cnot_pair_repetition": "Max pair repetition",
    "avg_layer_size": "Avg layer size",
    "max_layer_size": "Max layer size",
    "layer_congestion_score": "Layer congestion",
    "max_repeated_seq_len": "Max repeated seq",
    "t_depth": "T-depth",
    "cnot_depth": "CNOT depth",
    "t_layer_ratio": "T-layer ratio",
    "avg_t_per_layer": "Avg T / layer",
    "max_t_in_layer": "Max T in layer",
    "t_qubit_diversity": "T-qubit diversity",
    "num_other_gates": "Other gates count",
    "num_unique_layers": "Unique layers",
    "avg_estimated_path_length": "Avg path length",
    "max_estimated_path_length": "Max path length",
    "path_length_stddev": "Path length stddev",
}


def lab(k):
    return LABELS.get(k, k)


def load(runs_csv, metrics_csv):
    best = defaultdict(lambda: 10**18)
    with open(runs_csv) as f:
        for r in csv.DictReader(f):
            if r.get("status") != "success" or not r.get("routing_steps", "").strip():
                continue
            if r.get("mapping_type") not in (None, "", "gaussian"):
                continue
            best[r["circuit"]] = min(best[r["circuit"]], int(float(r["routing_steps"])))

    metrics = {r["circuit"]: r for r in csv.DictReader(open(metrics_csv))}
    # numeric characteristic columns discovered from the header
    header = next(iter(metrics.values())).keys() if metrics else []
    metric_keys = [k for k in header if k not in SKIP_COLUMNS]

    def g(c, k):
        try:
            return float(metrics[c][k])
        except (KeyError, ValueError, TypeError):
            return None

    data = []
    for c, steps in best.items():
        if c not in metrics:
            continue
        tl = g(c, "total_layers")
        if not tl or tl <= 0:
            continue
        row = {"circuit": c, "overhead": steps / tl}
        for k in metric_keys:
            row[k] = g(c, k)
        data.append(row)

    # keep only metrics that are numeric for ≥5 circuits and not constant
    usable = []
    for k in metric_keys:
        vals = [d[k] for d in data if d[k] is not None]
        if len(vals) >= 5 and len(set(vals)) > 1:
            usable.append(k)
    return data, usable


def plot_scatter(data, key, out_path):
    pts = [(d[key], d["overhead"]) for d in data if d[key] is not None]
    xs = np.array([p[0] for p in pts], float)
    ys = np.array([p[1] for p in pts], float)

    fig, ax = plt.subplots(figsize=(9, 6), facecolor="white")
    ax.scatter(xs, ys, s=50, alpha=0.7, color="#4e79a7",
               edgecolor="white", linewidth=0.4, zorder=3)
    ax.axhline(1.0, color="#888", ls="--", lw=1.1, zorder=1,
               label="overhead = 1 (ideale)")

    b1, b0 = np.polyfit(xs, ys, 1)
    xx = np.linspace(xs.min(), xs.max(), 50)
    ax.plot(xx, b0 + b1 * xx, color="#e15759", lw=2.2, zorder=2, label="trend lineare")

    sp, _ = stats.spearmanr(xs, ys)
    ss_tot = ((ys - ys.mean()) ** 2).sum()
    r2 = 1 - ((ys - (b0 + b1 * xs)) ** 2).sum() / ss_tot if ss_tot > 0 else 0.0

    ax.set_xlabel(lab(key), fontsize=11)
    ax.set_ylabel("overhead = routing_steps / total_layers", fontsize=11)
    ax.set_title(f"Overhead di routing gaussian vs {lab(key)}", fontsize=12, fontweight="bold")
    ax.text(0.02, 0.97, f"Spearman = {sp:+.2f}   R²(lin) = {r2:.2f}   n = {len(xs)}",
            transform=ax.transAxes, va="top", fontsize=9.5,
            bbox=dict(boxstyle="round", fc="white", ec="#ccc"))
    ax.grid(alpha=0.25, zorder=0)
    ax.legend(fontsize=8.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_correlation_ranking(data, keys, out_path):
    rows = []
    for k in keys:
        xs = [d[k] for d in data if d[k] is not None]
        ys = [d["overhead"] for d in data if d[k] is not None]
        sp, _ = stats.spearmanr(xs, ys)
        if np.isnan(sp):
            continue
        rows.append((lab(k), sp))
    rows.sort(key=lambda r: abs(r[1]))

    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = ["#e15759" if v > 0 else "#4e79a7" for v in vals]

    fig, ax = plt.subplots(figsize=(9, max(5.5, len(labels) * 0.32)), facecolor="white")
    ax.barh(range(len(labels)), vals, color=colors, edgecolor="white", zorder=2)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.axvline(0, color="#444", lw=1)
    for i, v in enumerate(vals):
        ax.text(v + (0.02 if v >= 0 else -0.02), i, f"{v:+.2f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman( overhead , caratteristica )", fontsize=11)
    ax.set_title("Correlazione di ogni caratteristica del circuito con l'overhead di gaussian\n"
                 "(rosso = più overhead, blu = meno overhead)", fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.25, zorder=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs_csv")
    p.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()

    out_dir = args.out_dir or (Path(args.runs_csv).resolve().parent / "gaussian_overhead_plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    data, keys = load(args.runs_csv, args.metrics)
    if not data:
        print("ERROR: nessun dato (controlla runs CSV e metriche).")
        return
    ov = [d["overhead"] for d in data]
    print(f"Circuiti: {len(data)} | overhead: min={min(ov):.2f} mediana={np.median(ov):.2f} max={max(ov):.2f}")
    print(f"  a overhead 1.00 (ottimo): {sum(1 for o in ov if o <= 1.001)}/{len(data)}")
    print(f"Caratteristiche analizzate: {len(keys)}")

    plot_correlation_ranking(data, keys, out_dir / "overhead_correlations.png")
    for k in keys:
        plot_scatter(data, k, out_dir / f"overhead_vs_{k}.png")
    print(f"Scritti: overhead_correlations.png + {len(keys)} scatter in {out_dir}/")


if __name__ == "__main__":
    main()
