#!/usr/bin/env python3
"""
Show which circuit characteristics drive gaussian's routing performance.

Performance = routing optimality = total_layers / routing_steps
(1.0 = ideal; lower = more routing steps per ideal layer, i.e. worse).

The runs CSV may contain several configurations per circuit (e.g. different
safe-passage / routing / weight bundles). A "configuration" is the unique
combination of the tuning-parameter columns that vary across the CSV.

Output layout (in --out-dir):

  <metric>/<metric>_vs_optimality_deg<N>.png   one subfolder per characteristic;
                                   inside, for each polynomial degree N in 1..5,
                                   a trend curve PER configuration plus the
                                   per-circuit scatter (one colour per config,
                                   legend = connectivity / routing).
  optimality_correlations_<config>.png   (root) for EACH configuration, a ranked
                                   bar chart of Spearman(optimality, characteristic).
  optimality_correlations_combined.png   (root) a single ranking pooling all
                                   configurations together.

A WISQ baseline curve (dashed black) is added to every trend plot by joining
data/best_wisq_per_circuit.csv (circuit, wisq_routing_steps) against the same
total_layers metric; pass --wisq-csv to point elsewhere or a nonexistent path
to omit it.

Usage:
  python3 scripts/circuit_analysis/gaussian_overhead_plot.py <runs_csv> \
      [--metrics <csv>] [--wisq-csv <csv>] [--out-dir <dir>]
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
DEFAULT_WISQ_CSV = PROJECT_ROOT / "data" / "best_wisq_per_circuit.csv"
WISQ_CFG = "WISQ"  # pseudo-config key for the WISQ baseline curve (not a PARAM_COLS tuple)

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
# Circuit-structural columns that a runs CSV may already carry per-row (written
# by the benchmark itself). These are preferred over the external metrics CSV,
# which is a lazily-populated cache and can be missing many circuits (notably
# large ones) — falling back to it silently would join away most of the data.
ROW_METRIC_COLS = [
    "max_parallelism", "avg_parallelism", "min_routing_steps",
    "cnot_interaction_density", "cnot_graph_modularity", "cnot_graph_diameter",
    "cnot_graph_avg_shortest_path", "max_cnot_degree", "min_cnot_degree",
    "avg_cnot_degree", "cnot_degree_gini", "cnot_pair_rep_gini",
    "cnot_edge_weight_stddev", "cnot_graph_clustering_coeff",
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

# Short formula / definition of each characteristic (shown on the X axis of the
# trend plots and next to each characteristic in the correlation rankings).
# n = number of logical qubits; "gates" = total routable gates.
FORMULAS = {
    "total_routable_gates": "= #CNOT + #T/Tdg + #other",
    "num_logical_qubits": "= n (logical qubits)",
    "num_cnot": "= #CNOT gates",
    "num_t_tdg": "= #T + #Tdg gates",
    "num_other_gates": "= gates − #CNOT − #T/Tdg",
    "t_count_ratio": "= #T/Tdg / gates",
    "cnot_ratio": "= #CNOT / gates",
    "other_gate_ratio": "= #other / gates",
    "num_unique_cnot_pairs": "= #distinct CNOT qubit-pairs",
    "max_cnot_pair_repetition": "= max #CNOT on one pair",
    "avg_cnot_pair_repetition": "= #CNOT / #unique pairs",
    "cnot_interaction_density": "= #pairs / (n(n−1)/2)",
    "max_cnot_degree": "= max_q #CNOT partners",
    "min_cnot_degree": "= min_q #CNOT partners",
    "t_qubit_diversity": "= #qubits touched by a T/Tdg",
    "avg_cnot_degree": "= 2·#pairs / n",
    "cnot_degree_gini": "= Gini(degree distribution)",
    "cnot_graph_modularity": "= Louvain modularity Q",
    "cnot_pair_rep_gini": "= Gini(per-pair CNOT counts)",
    "cnot_graph_diameter": "= longest shortest-path",
    "cnot_graph_avg_shortest_path": "= mean shortest-path length",
    "cnot_edge_weight_stddev": "= std(per-pair CNOT counts)",
    "cnot_graph_clustering_coeff": "= mean local clustering coeff",
    "num_unique_layers": "= #distinct layer structures",
    "layer_reuse_ratio": "= (layers − unique) / layers",
    "depth_width_ratio": "= total_layers / n",
    "density": "= gates / (n × total_layers)",
    "avg_layer_size": "= gates / total_layers",
    "max_layer_size": "= max_layer #gates",
    "avg_cnot_per_layer": "= #CNOT / total_layers",
    "avg_t_per_layer": "= #T/Tdg / total_layers",
    "max_t_in_layer": "= max_layer #T/Tdg",
    "max_cnot_in_layer": "= max_layer #CNOT",
    "t_depth": "= #layers with ≥1 T/Tdg",
    "cnot_depth": "= #layers with ≥1 CNOT",
    "t_layer_ratio": "= t_depth / total_layers",
    "layer_congestion_score": "= std / mean of layer sizes",
    "max_repeated_seq_len": "= longest repeated layer run",
    "avg_estimated_path_length": "= mean grid Manhattan dist",
    "max_estimated_path_length": "= max grid Manhattan dist",
    "path_length_stddev": "= std(path lengths)",
}


def lab(k):
    return LABELS.get(k, k)


def formula(k):
    return FORMULAS.get(k, "")


def config_label(cfg, cfg_cols):
    """Readable legend label: bare value for strategy columns, short=value for the rest."""
    if cfg == WISQ_CFG:
        return "WISQ"
    parts = []
    for c, v in zip(cfg_cols, cfg):
        if c in ("safe_passage_strategy", "routing_strategy", "gaussian_strategy",
                 "magic_aware_strategy", "mapping_type"):
            parts.append(str(v))
        else:
            parts.append(f"{SHORT.get(c, c)}={v}")
    return " / ".join(parts)


def config_conn_route(cfg, cfg_cols, const_params):
    """Legend label: only the connectivity (safe_passage) and routing strategy.

    Values are taken from the varying columns if present, otherwise from the
    constant-parameter values, so the label is correct even when one of the two
    does not vary across the CSV.
    """
    d = dict(zip(cfg_cols, cfg))
    conn = d.get("safe_passage_strategy", const_params.get("safe_passage_strategy", "?"))
    route = d.get("routing_strategy", const_params.get("routing_strategy", "?"))
    return f"{conn} / {route}"


def config_slug(cfg, cfg_cols):
    if cfg == WISQ_CFG:
        return WISQ_CFG
    d = dict(zip(cfg_cols, cfg))
    base = "_".join(str(d.get(c, "")) for c in ("safe_passage_strategy", "routing_strategy") if c in d)
    if not base:
        base = "_".join(str(x) for x in cfg)
    return re.sub(r"[^0-9A-Za-z._-]+", "_", base).strip("_")


def load(runs_csv, metrics_csv, wisq_csv=None):
    rows = list(csv.DictReader(open(runs_csv)))
    if not rows:
        return None

    # configuration = combination of the tuning-param columns that vary
    present = [c for c in PARAM_COLS if c in rows[0]]
    cfg_cols = [c for c in present if len({r[c] for r in rows}) > 1]
    # constant params (present but not varying) — used to complete the conn/route label
    const_params = {c: rows[0][c] for c in present if c not in cfg_cols}

    # best (min) routing_steps per (config, circuit); also harvest any row-level
    # circuit-structural columns (see ROW_METRIC_COLS) as we go, since the runs
    # CSV usually covers every circuit while the metrics cache may not.
    steps = defaultdict(lambda: defaultdict(lambda: 10**18))
    row_metvals = {}
    row_min_routing_steps = {}
    for r in rows:
        if r.get("status") != "success" or not r.get("routing_steps", "").strip():
            continue
        circuit = r["circuit"]
        cfg = tuple(r[c] for c in cfg_cols)
        steps[cfg][circuit] = min(steps[cfg][circuit], int(float(r["routing_steps"])))

        vals = row_metvals.setdefault(circuit, {})
        for k in ROW_METRIC_COLS:
            if k in vals:
                continue
            try:
                vals[k] = float(r[k])
            except (KeyError, ValueError, TypeError):
                pass
        try:
            rms = float(r["min_routing_steps"])
            cur = row_min_routing_steps.get(circuit)
            row_min_routing_steps[circuit] = rms if cur is None else min(cur, rms)
        except (KeyError, ValueError, TypeError):
            pass

    metrics = {r["circuit"]: r for r in csv.DictReader(open(metrics_csv))}

    def g(c, k):
        if k in ROW_METRIC_COLS and c in row_metvals and k in row_metvals[c]:
            return row_metvals[c][k]
        try:
            return float(metrics[c][k])
        except (KeyError, ValueError, TypeError):
            return None

    # overhead[config][circuit] and metric columns: cache-CSV characteristics
    # plus any row-level ones the runs CSV itself supplies.
    header = next(iter(metrics.values())).keys() if metrics else []
    metric_keys = [k for k in header if k not in SKIP_METRICS]
    metric_keys += [k for k in ROW_METRIC_COLS if k not in metric_keys]

    optimality = defaultdict(dict)
    metvals = {}
    for cfg, per_circ in steps.items():
        for c, s in per_circ.items():
            # total_layers (external cache) is the exact ideal-layers count;
            # min_routing_steps (embedded in the runs CSV, so far more complete)
            # is the same dependency-depth lower bound used elsewhere as a
            # fallback when the cache doesn't have this circuit.
            tl = g(c, "total_layers") or row_min_routing_steps.get(c)
            if not tl or tl <= 0 or s <= 0:
                continue
            optimality[cfg][c] = tl / s   # total_layers / routing_steps  (<=1, 1=ideal)
            if c not in metvals:
                metvals[c] = {k: g(c, k) for k in metric_keys}

    # WISQ baseline: same total_layers/routing_steps optimality, but routing_steps
    # comes from a separate per-circuit CSV (WISQ has no PARAM_COLS of its own,
    # so it is folded in as one extra pseudo-configuration rather than a tuple).
    if wisq_csv is not None and Path(wisq_csv).exists():
        wisq_rows = list(csv.DictReader(open(wisq_csv)))
        for r in wisq_rows:
            c = (r.get("circuit") or "").strip()
            if not c:
                continue
            try:
                wisq_steps = float(r["wisq_routing_steps"])
            except (KeyError, ValueError, TypeError):
                continue
            tl = g(c, "total_layers") or row_min_routing_steps.get(c)
            if not tl or tl <= 0 or wisq_steps <= 0:
                continue
            optimality[WISQ_CFG][c] = tl / wisq_steps
            if c not in metvals:
                metvals[c] = {k: g(c, k) for k in metric_keys}

    configs = sorted(k for k in optimality if k != WISQ_CFG)
    if WISQ_CFG in optimality:
        configs.append(WISQ_CFG)
    usable = []
    for k in metric_keys:
        vals = [metvals[c][k] for c in metvals if metvals[c][k] is not None]
        if len(vals) >= 5 and len(set(vals)) > 1:
            usable.append(k)
    return {"cfg_cols": cfg_cols, "const_params": const_params, "configs": configs,
            "optimality": optimality, "metvals": metvals, "metrics": usable}


def plot_trend(d, key, degree, out_path):
    configs, cfg_cols = d["configs"], d["cfg_cols"]
    cmap = plt.get_cmap("tab10")

    # common x-range across all configs for comparable curves
    all_x = [d["metvals"][c][key] for c in d["metvals"] if d["metvals"][c][key] is not None]
    if len(all_x) < 2:
        return
    xr = np.linspace(min(all_x), max(all_x), 200)

    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor="white")
    ax.axhline(1.0, color="#888", ls="--", lw=1.2, zorder=1, label="optimality = 1 (ideal)")

    plotted = False
    for i, cfg in enumerate(configs):
        color = cmap(i % 10)
        pts = [(d["metvals"][c][key], ov) for c, ov in d["optimality"][cfg].items()
               if d["metvals"].get(c, {}).get(key) is not None]
        xs = np.array([p[0] for p in pts], float)
        ys = np.array([p[1] for p in pts], float)
        is_wisq = cfg == WISQ_CFG
        color = "black" if is_wisq else cmap(i % 10)
        if len(xs):
            ax.scatter(xs, ys, s=22, alpha=0.35, color=color, zorder=2,
                       marker="^" if is_wisq else "o", linewidths=0)
        # need strictly more points than the polynomial order and ≥2 distinct x
        if len(xs) <= degree or len(set(xs)) < 2:
            continue
        # per-circuit scatter (one colour per configuration), no legend entry of its own
        ax.scatter(xs, ys, s=22, color=color, alpha=0.5, edgecolors="none", zorder=2)
        with np.errstate(all="ignore"):
            coeffs = np.polyfit(xs, ys, degree)
        sp, _ = stats.spearmanr(xs, ys)
        ls = "--" if is_wisq else "-"
        ax.plot(xr, np.polyval(coeffs, xr), color=color, lw=2.8 if is_wisq else 2.4,
                ls=ls, zorder=4 if is_wisq else 3,
                label=f"{config_label(cfg, cfg_cols)}   (ρ={sp:+.2f})")
        plotted = True

    if not plotted:
        plt.close(fig)
        return

    # optimality is in (0, 1]; clamp the view (high-degree fits can shoot off-screen)
    ys_all = [ov for cfg in configs for ov in d["optimality"][cfg].values()]
    if ys_all:
        ax.set_ylim(max(0.0, min(ys_all) - 0.05), 1.05)

    deg_name = {1: "linear", 2: "quadratic", 3: "cubic", 4: "quartic", 5: "quintic"}.get(degree, f"degree {degree}")
    ax.set_xlabel(f"{lab(key)}\n{formula(key)}", fontsize=11)
    ax.set_ylabel("Routing optimality = total_layers / routing_steps", fontsize=11)
    ax.set_title(f"Gaussian routing optimality vs {lab(key)}\n"
                 f"{deg_name} trend (degree {degree}), one curve per configuration",
                 fontsize=12, fontweight="bold")
    ax.grid(alpha=0.25, zorder=0)
    ax.legend(fontsize=8.5, loc="best", title="connectivity / routing")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_correlation_ranking(d, pairs, subtitle, out_path):
    """pairs: list of (circuit, optimality) — may pool several configurations."""
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
        rows.append((k, sp))
    if not rows:
        return
    rows.sort(key=lambda r: abs(r[1]))
    keys = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    # each tick shows the characteristic name and, below it, its formula
    labels = [f"{lab(k)}\n{formula(k)}" for k in keys]
    colors = ["#e15759" if v > 0 else "#4e79a7" for v in vals]

    fig, ax = plt.subplots(figsize=(9.5, max(6.0, len(labels) * 0.5)), facecolor="white")
    ax.barh(range(len(labels)), vals, color=colors, edgecolor="white", zorder=2)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.axvline(0, color="#444", lw=1)
    for i, v in enumerate(vals):
        ax.text(v + (0.02 if v >= 0 else -0.02), i, f"{v:+.2f}",
                va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Spearman( optimality , characteristic )", fontsize=11)
    ax.set_title("Correlation of each circuit characteristic with gaussian routing optimality\n"
                 f"{subtitle}", fontsize=11, fontweight="bold")
    # legend explaining the colours
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#e15759", label="higher optimality (positive)"),
                       Patch(color="#4e79a7", label="lower optimality (negative)")],
              loc="lower right", fontsize=8.5)
    ax.grid(axis="x", alpha=0.25, zorder=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs_csv")
    p.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    p.add_argument("--wisq-csv", type=Path, default=DEFAULT_WISQ_CSV,
                    help="Per-circuit WISQ routing_steps CSV (circuit, wisq_routing_steps) "
                         f"added as an extra baseline curve (default: {DEFAULT_WISQ_CSV}). "
                         "Pass a nonexistent path to omit it.")
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()

    out_dir = args.out_dir or (Path(args.runs_csv).resolve().parent / "gaussian_overhead_plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    d = load(args.runs_csv, args.metrics, args.wisq_csv)
    if not d or not d["configs"]:
        print("ERROR: no data (check runs CSV and metrics).")
        return

    print(f"Configurations: {len(d['configs'])} | characteristics: {len(d['metrics'])}")
    for cfg in d["configs"]:
        print(f"  - {config_label(cfg, d['cfg_cols'])}  ({len(d['optimality'][cfg])} circuits)")

    # correlation rankings stay in the root out-dir
    for cfg in d["configs"]:
        pairs = list(d["optimality"][cfg].items())
        plot_correlation_ranking(d, pairs,
                                 f"config: {config_conn_route(cfg, d['cfg_cols'], d['const_params'])}",
                                 out_dir / f"optimality_correlations_{config_slug(cfg, d['cfg_cols'])}.png")
    # one combined ranking pooling all configurations
    combined = [(c, ov) for cfg in d["configs"] for c, ov in d["optimality"][cfg].items()]
    plot_correlation_ranking(d, combined, "combined (all configurations pooled)",
                             out_dir / "optimality_correlations_combined.png")

    # trend curves: one subfolder per characteristic, the 5 degrees inside
    degrees = [1, 2, 3, 4, 5]
    for k in d["metrics"]:
        sub = out_dir / k
        sub.mkdir(parents=True, exist_ok=True)
        for deg in degrees:
            plot_trend(d, k, deg, sub / f"{k}_vs_optimality_deg{deg}.png")
    print(f"Wrote {len(d['configs'])} per-config + 1 combined ranking (root), "
          f"and {len(d['metrics'])} characteristic folders x {len(degrees)} degrees to {out_dir}/")


if __name__ == "__main__":
    main()
