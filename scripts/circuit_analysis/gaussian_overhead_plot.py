#!/usr/bin/env python3
"""
Show which circuit characteristics drive gaussian's routing performance.

Performance = routing overhead = routing_steps / total_layers
(1.0 = ideal, no inflation; higher = more routing steps per ideal layer).

The runs CSV may contain several configurations per circuit (e.g. different
safe-passage / routing / weight bundles). A "configuration" is the unique
combination of the tuning-parameter columns that vary across the CSV.

Output layout (in --out-dir):

  <metric>/<metric>_vs_overhead_deg<N>.png   one subfolder per characteristic;
                                   inside, for each polynomial degree N in 1..5,
                                   a trend curve PER configuration (no scatter
                                   points, one legend entry per config).
  overhead_correlations_<config>.png   (root) for EACH configuration, a ranked
                                   bar chart of Spearman(overhead, characteristic).
  overhead_correlations_combined.png   (root) a single ranking pooling all
                                   configurations together.

Usage:
  python3 scripts/circuit_analysis/gaussian_overhead_plot.py <runs_csv> \
      [--metrics <csv>] [--out-dir <dir>]
"""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_METRICS = PROJECT_ROOT / "benchmarks" / "results" / "cache_metrics" / "all_circuits_cache_metrics.csv"

# Columns of the metrics CSV that are not circuit characteristics to plot.
# total_layers is excluded because it is the denominator of the overhead.
SKIP_METRICS = {"circuit", "layer_size_distribution", "top5_layer_frequencies", "total_layers"}

# Tuning-parameter columns of the runs CSV (used to define a configuration).
PARAM_COLS = [
    "mapping_type", "magic_aware_strategy", "gaussian_strategy", "magic_high", "magic_low",
    "cnot_high", "cnot_low", "mapped_gaussian_weight", "base_gaussian_weight", "external_weight",
    "gaussian_confidence", "safe_passage_strategy", "magic_state_placement_strategy",
    "border_distance_percentage", "number_of_magic_states", "routing_strategy",
    "t_routing_mode", "use_layer_cache",
]
SHORT = {
    "mapping_type": "type", "magic_aware_strategy": "ma", "gaussian_strategy": "gstrat",
    "magic_high": "mH", "magic_low": "mL", "cnot_high": "cH", "cnot_low": "cL",
    "mapped_gaussian_weight": "map", "base_gaussian_weight": "base", "external_weight": "ext",
    "gaussian_confidence": "conf", "magic_state_placement_strategy": "place",
    "border_distance_percentage": "bd", "number_of_magic_states": "nmagic",
    "t_routing_mode": "trout", "use_layer_cache": "cache",
}

# Nice English axis labels for the characteristics (fallback: raw column name).
LABELS = {
    "max_cnot_degree": "Max CNOT degree", "avg_cnot_degree": "Avg CNOT degree",
    "min_cnot_degree": "Min CNOT degree", "cnot_interaction_density": "Interaction density",
    "density": "Density (fill ratio)", "avg_cnot_per_layer": "Avg CNOT / layer",
    "max_cnot_in_layer": "Max CNOT in layer", "depth_width_ratio": "Depth / width ratio",
    "num_logical_qubits": "Qubits", "cnot_graph_modularity": "Modularity",
    "cnot_degree_gini": "CNOT degree Gini", "cnot_pair_rep_gini": "Pair-rep Gini",
    "cnot_graph_diameter": "Graph diameter", "cnot_graph_avg_shortest_path": "Avg shortest path",
    "cnot_graph_clustering_coeff": "Clustering coeff", "cnot_edge_weight_stddev": "Edge weight stddev",
    "t_count_ratio": "T-count ratio", "cnot_ratio": "CNOT ratio", "other_gate_ratio": "Other-gate ratio",
    "layer_reuse_ratio": "Layer reuse", "num_cnot": "CNOT count", "num_t_tdg": "T/Tdg count",
    "total_routable_gates": "Total gates", "num_unique_cnot_pairs": "Unique CNOT pairs",
    "avg_cnot_pair_repetition": "Avg pair repetition", "max_cnot_pair_repetition": "Max pair repetition",
    "avg_layer_size": "Avg layer size", "max_layer_size": "Max layer size",
    "layer_congestion_score": "Layer congestion", "max_repeated_seq_len": "Max repeated seq",
    "t_depth": "T-depth", "cnot_depth": "CNOT depth", "t_layer_ratio": "T-layer ratio",
    "avg_t_per_layer": "Avg T / layer", "max_t_in_layer": "Max T in layer",
    "t_qubit_diversity": "T-qubit diversity", "num_other_gates": "Other gates count",
    "num_unique_layers": "Unique layers", "avg_estimated_path_length": "Avg path length",
    "max_estimated_path_length": "Max path length", "path_length_stddev": "Path length stddev",
}


def lab(k):
    return LABELS.get(k, k)


def config_label(cfg, cfg_cols):
    """Readable legend label: bare value for strategy columns, short=value for the rest."""
    parts = []
    for c, v in zip(cfg_cols, cfg):
        if c in ("safe_passage_strategy", "routing_strategy", "gaussian_strategy",
                 "magic_aware_strategy", "mapping_type"):
            parts.append(str(v))
        else:
            parts.append(f"{SHORT.get(c, c)}={v}")
    return " / ".join(parts)


def config_slug(cfg, cfg_cols):
    d = dict(zip(cfg_cols, cfg))
    base = "_".join(str(d.get(c, "")) for c in ("safe_passage_strategy", "routing_strategy") if c in d)
    if not base:
        base = "_".join(str(x) for x in cfg)
    return re.sub(r"[^0-9A-Za-z._-]+", "_", base).strip("_")


def load(runs_csv, metrics_csv):
    rows = list(csv.DictReader(open(runs_csv)))
    if not rows:
        return None

    # configuration = combination of the tuning-param columns that vary
    present = [c for c in PARAM_COLS if c in rows[0]]
    cfg_cols = [c for c in present if len({r[c] for r in rows}) > 1]

    # best (min) routing_steps per (config, circuit)
    steps = defaultdict(lambda: defaultdict(lambda: 10**18))
    for r in rows:
        if r.get("status") != "success" or not r.get("routing_steps", "").strip():
            continue
        cfg = tuple(r[c] for c in cfg_cols)
        steps[cfg][r["circuit"]] = min(steps[cfg][r["circuit"]], int(float(r["routing_steps"])))

    metrics = {r["circuit"]: r for r in csv.DictReader(open(metrics_csv))}

    def g(c, k):
        try:
            return float(metrics[c][k])
        except (KeyError, ValueError, TypeError):
            return None

    # overhead[config][circuit] and metric columns
    header = next(iter(metrics.values())).keys() if metrics else []
    metric_keys = [k for k in header if k not in SKIP_METRICS]

    overhead = defaultdict(dict)
    metvals = {}
    for cfg, per_circ in steps.items():
        for c, s in per_circ.items():
            tl = g(c, "total_layers")
            if not tl or tl <= 0:
                continue
            overhead[cfg][c] = s / tl
            if c not in metvals:
                metvals[c] = {k: g(c, k) for k in metric_keys}

    configs = sorted(overhead.keys())
    usable = []
    for k in metric_keys:
        vals = [metvals[c][k] for c in metvals if metvals[c][k] is not None]
        if len(vals) >= 5 and len(set(vals)) > 1:
            usable.append(k)
    return {"cfg_cols": cfg_cols, "configs": configs, "overhead": overhead,
            "metvals": metvals, "metrics": usable}


def plot_trend(d, key, degree, out_path):
    configs, cfg_cols = d["configs"], d["cfg_cols"]
    cmap = plt.get_cmap("tab10")

    # common x-range across all configs for comparable curves
    all_x = [d["metvals"][c][key] for c in d["metvals"] if d["metvals"][c][key] is not None]
    if len(all_x) < 2:
        return
    xr = np.linspace(min(all_x), max(all_x), 200)

    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor="white")
    ax.axhline(1.0, color="#888", ls="--", lw=1.2, zorder=1, label="overhead = 1 (ideal)")

    plotted = False
    for i, cfg in enumerate(configs):
        pts = [(d["metvals"][c][key], ov) for c, ov in d["overhead"][cfg].items()
               if d["metvals"].get(c, {}).get(key) is not None]
        xs = np.array([p[0] for p in pts], float)
        ys = np.array([p[1] for p in pts], float)
        # need strictly more points than the polynomial order and ≥2 distinct x
        if len(xs) <= degree or len(set(xs)) < 2:
            continue
        with np.errstate(all="ignore"):
            coeffs = np.polyfit(xs, ys, degree)
        sp, _ = stats.spearmanr(xs, ys)
        ax.plot(xr, np.polyval(coeffs, xr), color=cmap(i % 10), lw=2.4, zorder=3,
                label=f"{config_label(cfg, cfg_cols)}   (ρ={sp:+.2f})")
        plotted = True

    if not plotted:
        plt.close(fig)
        return

    # keep y on a sensible range (high-degree fits can shoot off-screen)
    ys_all = [ov for cfg in configs for ov in d["overhead"][cfg].values()]
    if ys_all:
        ax.set_ylim(min(0.9, min(ys_all)), max(ys_all) * 1.15)

    deg_name = {1: "linear", 2: "quadratic", 3: "cubic", 4: "quartic", 5: "quintic"}.get(degree, f"degree {degree}")
    ax.set_xlabel(lab(key), fontsize=11)
    ax.set_ylabel("Routing overhead = routing_steps / total_layers", fontsize=11)
    ax.set_title(f"Gaussian routing overhead vs {lab(key)}\n"
                 f"{deg_name} trend (degree {degree}), one curve per configuration",
                 fontsize=12, fontweight="bold")
    ax.grid(alpha=0.25, zorder=0)
    ax.legend(fontsize=8, loc="best", title="Configuration")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_correlation_ranking(d, pairs, subtitle, out_path):
    """pairs: list of (circuit, overhead) — may pool several configurations."""
    rows = []
    for k in d["metrics"]:
        pts = [(d["metvals"][c][k], ov) for (c, ov) in pairs
               if d["metvals"].get(c, {}).get(k) is not None]
        if len(pts) < 5:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if len(set(xs)) < 2:
            continue
        sp, _ = stats.spearmanr(xs, ys)
        if np.isnan(sp):
            continue
        rows.append((lab(k), sp))
    if not rows:
        return
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
    ax.set_xlabel("Spearman( overhead , characteristic )", fontsize=11)
    ax.set_title("Correlation of each circuit characteristic with gaussian routing overhead\n"
                 f"{subtitle}", fontsize=11, fontweight="bold")
    # legend explaining the colours
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#e15759", label="more overhead (positive)"),
                       Patch(color="#4e79a7", label="less overhead (negative)")],
              loc="lower right", fontsize=8.5)
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

    d = load(args.runs_csv, args.metrics)
    if not d or not d["configs"]:
        print("ERROR: no data (check runs CSV and metrics).")
        return

    print(f"Configurations: {len(d['configs'])} | characteristics: {len(d['metrics'])}")
    for cfg in d["configs"]:
        print(f"  - {config_label(cfg, d['cfg_cols'])}  ({len(d['overhead'][cfg])} circuits)")

    # correlation rankings stay in the root out-dir
    for cfg in d["configs"]:
        pairs = list(d["overhead"][cfg].items())
        plot_correlation_ranking(d, pairs, f"config: {config_label(cfg, d['cfg_cols'])}",
                                 out_dir / f"overhead_correlations_{config_slug(cfg, d['cfg_cols'])}.png")
    # one combined ranking pooling all configurations
    combined = [(c, ov) for cfg in d["configs"] for c, ov in d["overhead"][cfg].items()]
    plot_correlation_ranking(d, combined, "combined (all configurations pooled)",
                             out_dir / "overhead_correlations_combined.png")

    # trend curves: one subfolder per characteristic, the 5 degrees inside
    degrees = [1, 2, 3, 4, 5]
    for k in d["metrics"]:
        sub = out_dir / k
        sub.mkdir(parents=True, exist_ok=True)
        for deg in degrees:
            plot_trend(d, k, deg, sub / f"{k}_vs_overhead_deg{deg}.png")
    print(f"Wrote {len(d['configs'])} per-config + 1 combined ranking (root), "
          f"and {len(d['metrics'])} characteristic folders x {len(degrees)} degrees to {out_dir}/")


if __name__ == "__main__":
    main()
