#!/usr/bin/env python3
"""
Show which circuit characteristics drive gaussian's routing performance.

Performance = routing optimality = total_layers / routing_steps
(1.0 = ideal; lower = more routing steps per ideal layer, i.e. worse).

The runs CSV may contain several configurations per circuit (e.g. different
safe-passage / routing / weight bundles). A "configuration" is the unique
combination of the tuning-parameter columns that vary across the CSV.

Output layout (in --out-dir):

  <metric>/<metric>_vs_optimality_deg<N>.<fmt>  one subfolder per characteristic;
                                   inside, for each polynomial degree N in 1..5,
                                   a trend curve PER configuration plus the
                                   per-circuit scatter (one colour per config,
                                   legend = connectivity / routing).
  optimality_correlations_<config>.<fmt>  (root) for EACH configuration, a ranked
                                   bar chart of Spearman(optimality, characteristic).
  optimality_correlations_combined.<fmt>  (root) a single ranking pooling all
                                   configurations together.

--format sets <fmt>: pdf (default, vector -- use this for figures that go into
the paper) or png (raster, handier when eyeballing the whole output tree).

A WISQ baseline curve (dashed black) is added to every trend plot by joining
data/best_wisq_per_circuit.csv (circuit, wisq_routing_steps) against the same
total_layers metric; pass --wisq-csv to point elsewhere or a nonexistent path
to omit it.

--routing <strategy> keeps a single router: the router then disappears from the
legend (it is named once in the title) and the WISQ baseline is switched off, so
each plot shows exactly the remaining configurations.
--no-rankings skips the optimality_correlations_*.png ranking charts and emits
only the per-characteristic trend plots.
--no-legend drops the legend from the trend plots only (ranking charts keep it).
--simple_text uses minimal text on the trend plots: y='Routing optimality',
x=the characteristic name only, title='Routing optimality vs <name> (<fit> fit)'.
--no_title generates the trend plots with no title at all.
--fit chooses the trend fit: poly (degrees 1..5, may wiggle), monotone (isotonic +
PCHIP, guaranteed monotone), decay (saturating exponential), log (a + b·ln x),
binned (PCHIP through equal-count bin medians), power (log-log power law), wls
(density-weighted log), or all. binned/power/wls track the sparse tail better.

Usage:
  python3 scripts/circuit_analysis/gaussian_overhead_plot.py <runs_csv> \
      [--schema runs|wisq] [--routing <strategy>] [--metrics <csv>] \
      [--wisq-csv <csv>] [--out-dir <dir>] [--format pdf|png]
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
from scipy.interpolate import PchipInterpolator
from scipy.optimize import curve_fit

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

# Column schemas of the runs CSV, selected with --schema. The two CSV families
# name the same quantities differently:
#   runs : benchmark CSVs (data/results/*_runs.csv)           -> routing_steps / status
#   wisq : WISQ-comparison CSVs (data/results/single_config/) -> my_routing_steps / my_status
# "steps" is the routing-steps column, "status" the success flag (ignored when the
# column is absent), "extra_params" the tuning-parameter columns specific to that
# family (added on top of PARAM_COLS).
SCHEMAS = {
    "runs": {"steps": "routing_steps", "status": "status", "extra_params": []},
    "wisq": {"steps": "my_routing_steps", "status": "my_status",
             "extra_params": ["type", "MagicStatePlacementStrategy"]},
}

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
    "MagicStatePlacementStrategy": "place",
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


def metric_dirname(k):
    """Folder name for a characteristic: the exact label shown in the ranking
    charts (lab), with '/' — the only path-illegal character in those labels —
    replaced by '-' (e.g. 'Avg CNOT / layer' -> 'Avg CNOT - layer')."""
    return lab(k).replace("/", "-").strip()


def config_label(cfg, cfg_cols):
    """Readable legend label: bare value for strategy columns, short=value for the rest."""
    if cfg == WISQ_CFG:
        return "WISQ"
    parts = []
    for c, v in zip(cfg_cols, cfg):
        if c in ("safe_passage_strategy", "routing_strategy", "gaussian_strategy",
                 "magic_aware_strategy", "mapping_type", "type"):
            parts.append(str(v))
        else:
            parts.append(f"{SHORT.get(c, c)}={v}")
    return " / ".join(parts)


def config_conn_route(cfg, cfg_cols, const_params, hide_routing=False):
    """Legend label: only the connectivity (safe_passage) and routing strategy.

    Values are taken from the varying columns if present, otherwise from the
    constant-parameter values, so the label is correct even when one of the two
    does not vary across the CSV (e.g. single-configuration CSVs).

    hide_routing drops the router from the label: with --routing every curve
    shares the same one, so it is stated once in the title instead.
    """
    if cfg == WISQ_CFG:
        return "WISQ"
    d = dict(const_params or {})
    d.update(dict(zip(cfg_cols, cfg)))
    conn = d.get("safe_passage_strategy", "?")
    if hide_routing:
        return conn
    return f"{conn} / {d.get('routing_strategy', '?')}"


def config_slug(cfg, cfg_cols, const_params=None):
    if cfg == WISQ_CFG:
        return WISQ_CFG
    # constant params complete the slug for single-configuration CSVs, where
    # nothing varies and cfg_cols is empty (slug would otherwise be blank).
    d = dict(const_params or {})
    d.update(dict(zip(cfg_cols, cfg)))
    base = "_".join(str(d[c]) for c in ("safe_passage_strategy", "routing_strategy") if c in d)
    if not base:
        base = "_".join(str(x) for x in cfg)
    return re.sub(r"[^0-9A-Za-z._-]+", "_", base).strip("_") or "config"


def load(runs_csv, metrics_csv, wisq_csv=None, schema="runs", routing=None):
    rows = list(csv.DictReader(open(runs_csv)))
    if not rows:
        return None

    sch = SCHEMAS[schema]
    steps_col, status_col = sch["steps"], sch["status"]
    if steps_col not in rows[0]:
        print(f"ERROR: column '{steps_col}' (schema '{schema}') not found in {runs_csv}.\n"
              f"       Available columns: {', '.join(rows[0].keys())}\n"
              f"       Try a different --schema (choices: {', '.join(SCHEMAS)}).")
        return None
    has_status = status_col in rows[0]

    # --routing: keep a single router. It then no longer varies, so it drops out
    # of cfg_cols into const_params and is hidden from the legend (hide_routing);
    # the WISQ baseline is dropped too, leaving exactly the kept configurations.
    if routing is not None:
        if "routing_strategy" not in rows[0]:
            print(f"ERROR: --routing given but column 'routing_strategy' is not in {runs_csv}.")
            return None
        available = sorted({r["routing_strategy"] for r in rows})
        rows = [r for r in rows if r["routing_strategy"] == routing]
        if not rows:
            print(f"ERROR: no rows with routing_strategy='{routing}'.\n"
                  f"       Available routers: {', '.join(available)}")
            return None
        wisq_csv = None

    # configuration = combination of the tuning-param columns that vary
    param_cols = PARAM_COLS + [c for c in sch["extra_params"] if c not in PARAM_COLS]
    present = [c for c in param_cols if c in rows[0]]
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
        if has_status and r.get(status_col) != "success":
            continue
        if not (r.get(steps_col) or "").strip():
            continue
        circuit = r["circuit"]
        cfg = tuple(r[c] for c in cfg_cols)
        steps[cfg][circuit] = min(steps[cfg][circuit], int(float(r[steps_col])))

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
            "optimality": optimality, "metvals": metvals, "metrics": usable,
            "routing_filter": routing, "hide_routing": routing is not None}


def _pava(y):
    """Pool-adjacent-violators: least-squares non-decreasing isotonic fit of y."""
    y = np.asarray(y, float)
    vals, cnts = [], []
    for v in y:
        c = 1
        while vals and vals[-1] > v:                 # violation -> merge blocks
            pv, pc = vals.pop(), cnts.pop()
            v = (v * c + pv * pc) / (c + pc)
            c += pc
        vals.append(v)
        cnts.append(c)
    out = np.empty(len(y))
    idx = 0
    for v, c in zip(vals, cnts):
        out[idx:idx + c] = v
        idx += c
    return out


def fit_curve(xs, ys, method, degree, grid, bins=10):
    """Return (gx, gy) for the requested trend fit, or None if it can't be fit.

    poly     : ordinary least-squares polynomial of the given degree (may wiggle).
    monotone : isotonic regression (direction from Spearman sign) smoothed with a
               shape-preserving PCHIP spline -> guaranteed monotone, smooth.
    decay    : saturating exponential y = c + a*exp(-b*x') fit (x' = x rescaled to
               [0,1]); monotone by construction, works for rising or falling data.
    log      : logarithmic fit y = a + b*ln(x - xmin + 1) (the shift keeps the
               argument >= 1, so zero/negative x are fine); monotone in x.

    The next three tackle the "dense low-x cluster dominates, sparse tail ignored"
    problem, so the curve tracks the whole x-range rather than the crowded side:
    binned   : split x into `bins` equal-count groups, take the per-group MEDIAN of
               x and y, and PCHIP through those points -> every x-region weighs the
               same and the median ignores the vertical scatter (robust central
               trend).
    power    : power law y = a*x'^b (x' = x - xmin + 1), fit as a line in log-log
               space, so it minimises relative error and follows the tail better.
    wls      : the `log` fit but weighted least squares with weights ~ 1/local
               x-density, so a lone tail point counts as much as the dense cluster.
    """
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    if len(set(xs)) < 2:
        return None

    if method == "poly":
        if len(xs) <= degree:
            return None
        with np.errstate(all="ignore"):
            coeffs = np.polyfit(xs, ys, degree)
        return grid, np.polyval(coeffs, grid)

    if method == "monotone":
        if len(xs) < 3:
            return None
        sp, _ = stats.spearmanr(xs, ys)
        if np.isnan(sp):
            return None
        increasing = sp >= 0
        order = np.argsort(xs)
        sx, sy = xs[order], ys[order]
        z = _pava(sy if increasing else -sy)
        if not increasing:
            z = -z
        ux, inv = np.unique(sx, return_inverse=True)
        uy = np.array([z[inv == j].mean() for j in range(len(ux))])
        if len(ux) < 2:
            return None
        f = PchipInterpolator(ux, uy, extrapolate=False)   # shape-preserving
        g = grid[(grid >= ux[0]) & (grid <= ux[-1])]
        return g, f(g)

    if method == "decay":
        if len(xs) < 4:
            return None
        xmin, xmax = xs.min(), xs.max()
        xn = (xs - xmin) / (xmax - xmin)
        c0 = ys[np.argmax(xs)]
        a0 = ys[np.argmin(xs)] - c0
        model = lambda t, a, b, c: c + a * np.exp(-b * t)
        try:
            popt, _ = curve_fit(model, xn, ys, p0=[a0, 2.0, c0],
                                bounds=([-np.inf, 1e-3, -np.inf], [np.inf, 50.0, np.inf]),
                                maxfev=10000)
        except (RuntimeError, ValueError):
            return None
        g = grid[(grid >= xmin) & (grid <= xmax)]
        return g, model((g - xmin) / (xmax - xmin), *popt)

    if method == "log":
        if len(xs) < 3:
            return None
        xmin, xmax = xs.min(), xs.max()
        lx = np.log(xs - xmin + 1.0)              # shift so argument >= 1
        if len(set(lx)) < 2:
            return None
        coeffs = np.polyfit(lx, ys, 1)            # y = b*ln(x-xmin+1) + a, monotone
        g = grid[(grid >= xmin) & (grid <= xmax)]
        return g, np.polyval(coeffs, np.log(g - xmin + 1.0))

    if method == "binned":
        if len(xs) < 6:
            return None
        k = max(2, min(bins, len(xs) // 3))       # >= 3 points per bin
        order = np.argsort(xs)
        sx, sy = xs[order], ys[order]
        groups = np.array_split(np.arange(len(sx)), k)
        bx = np.array([np.median(sx[gi]) for gi in groups])
        by = np.array([np.median(sy[gi]) for gi in groups])
        ux, idx = np.unique(bx, return_index=True)   # PCHIP needs strictly increasing x
        uy = by[idx]
        if len(ux) < 2:
            return None
        f = PchipInterpolator(ux, uy, extrapolate=False)
        g = grid[(grid >= ux[0]) & (grid <= ux[-1])]
        return g, f(g)

    if method == "power":
        if len(xs) < 3:
            return None
        xmin, xmax = xs.min(), xs.max()
        xp = xs - xmin + 1.0                       # shift so x' >= 1 (handles x <= 0)
        pos = ys > 0                               # log-log needs positive y
        if pos.sum() < 3 or len(set(xp[pos])) < 2:
            return None
        b, la = np.polyfit(np.log(xp[pos]), np.log(ys[pos]), 1)   # ln y = b ln x' + ln a
        g = grid[(grid >= xmin) & (grid <= xmax)]
        return g, np.exp(la) * (g - xmin + 1.0) ** b

    if method == "wls":
        if len(xs) < 3:
            return None
        xmin, xmax = xs.min(), xs.max()
        lx = np.log(xs - xmin + 1.0)
        if len(set(lx)) < 2:
            return None
        h = (xmax - xmin) / 20.0 or 1.0
        dens = np.array([np.count_nonzero(np.abs(xs - xi) <= h) for xi in xs], float)
        w = 1.0 / np.sqrt(dens)                    # down-weight crowded x-regions
        coeffs = np.polyfit(lx, ys, 1, w=w)
        g = grid[(grid >= xmin) & (grid <= xmax)]
        return g, np.polyval(coeffs, np.log(g - xmin + 1.0))

    return None


# Human-readable description of each fit method, used in plot titles.
FIT_DESC = {
    "monotone": "monotone fit (isotonic + PCHIP)",
    "decay": "saturating-exponential fit",
    "log": "logarithmic fit (a + b·ln x)",
    "binned": "binned-median fit (equal-count bins)",
    "power": "power-law fit (y = a·xᵇ)",
    "wls": "density-weighted logarithmic fit",
}
# Short version of the same, used in the --simple_text single-line title.
FIT_SHORT = {
    "monotone": "monotone fit", "decay": "exponential fit", "log": "logarithmic fit",
    "binned": "binned-median fit", "power": "power-law fit", "wls": "weighted-log fit",
}

# --paper_dim target: the exact footprint of Figure 6 (fig:winrate-budget) in the
# paper. Width = 0.8 * columnwidth (IEEEtran 10pt conference => columnwidth =
# 252.0 TeX pt = 3.487 in); aspect = 244.8/288 from the winrate_budget.pdf box.
# Include the produced PDF at width=0.8\linewidth (or its natural size) so LaTeX
# does NOT rescale it and the text keeps the point sizes set here.
PAPER_COL_IN = 252.0 / 72.27          # IEEEtran column width in inches
PAPER_FIG_W = 0.8 * PAPER_COL_IN      # 2.790 in
PAPER_FIG_H = PAPER_FIG_W * (244.8 / 288.0)   # 2.372 in


def plot_trend(d, key, method, out_path, degree=None):
    configs, cfg_cols = d["configs"], d["cfg_cols"]
    cmap = plt.get_cmap("tab10")

    # common x-range across all configs for comparable curves
    all_x = [d["metvals"][c][key] for c in d["metvals"] if d["metvals"][c][key] is not None]
    if len(all_x) < 2:
        return
    xr = np.linspace(min(all_x), max(all_x), 200)

    # --paper_dim: Figure-6 physical size and paper-scale fonts/line widths, so the
    # PDF drops into the paper at 1:1 with correctly sized text.
    paper = d.get("paper_dim")
    if paper:
        figsize = (PAPER_FIG_W, PAPER_FIG_H)
        fs_label, fs_title, fs_tick, fs_leg = 7, 8, 7, 6.5
        lw, lw_wisq, msize, ah_lw, dpi = 1.2, 1.5, 8, 0.8, 300
    else:
        figsize = (10, 6.5)
        fs_label, fs_title, fs_tick, fs_leg = 11, 12, None, 8.5
        lw, lw_wisq, msize, ah_lw, dpi = 2.4, 2.8, 22, 1.2, 130

    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.axhline(1.0, color="#888", ls="--", lw=ah_lw, zorder=1, label="optimality = 1 (ideal)")

    plotted = False
    for i, cfg in enumerate(configs):
        pts = [(d["metvals"][c][key], ov) for c, ov in d["optimality"][cfg].items()
               if d["metvals"].get(c, {}).get(key) is not None]
        xs = np.array([p[0] for p in pts], float)
        ys = np.array([p[1] for p in pts], float)
        is_wisq = cfg == WISQ_CFG
        color = "black" if is_wisq else cmap(i % 10)
        # per-circuit scatter (one colour per configuration), no legend entry of its own
        if len(xs):
            ax.scatter(xs, ys, s=msize, color=color, alpha=0.35, zorder=2,
                       marker="^" if is_wisq else "o", linewidths=0)
        fit = fit_curve(xs, ys, method, degree, xr, bins=d.get("bins", 10))
        if fit is None:
            continue
        gx, gy = fit
        ax.plot(gx, gy, color=color, lw=lw_wisq if is_wisq else lw,
                ls="--" if is_wisq else "-", zorder=4 if is_wisq else 3,
                label=config_conn_route(cfg, cfg_cols, d["const_params"], d["hide_routing"]))
        plotted = True

    if not plotted:
        plt.close(fig)
        return

    # optimality is in (0, 1]; clamp the view (high-degree fits can shoot off-screen)
    ys_all = [ov for cfg in configs for ov in d["optimality"][cfg].values()]
    if ys_all:
        ax.set_ylim(max(0.0, min(ys_all) - 0.05), 1.05)

    if method == "poly":
        deg_name = {1: "linear", 2: "quadratic", 3: "cubic", 4: "quartic",
                    5: "quintic"}.get(degree, f"degree {degree}")
        trend_desc = f"{deg_name} trend (degree {degree})"
        fit_short = f"{deg_name} fit"
    else:
        trend_desc = FIT_DESC.get(method, method)
        fit_short = FIT_SHORT.get(method, f"{method} fit")

    if d.get("simple_text"):
        # minimal labels/title: axis names only (no formula), single-line title
        ax.set_xlabel(lab(key), fontsize=fs_label)
        ax.set_ylabel("Routing optimality", fontsize=fs_label)
        title = f"Routing optimality vs {lab(key)} ({fit_short})"
    else:
        ax.set_xlabel(f"{lab(key)}\n{formula(key)}", fontsize=fs_label)
        ax.set_ylabel("Routing optimality = total_layers / routing_steps", fontsize=fs_label)
        # with --routing every curve shares the router, so name it once here
        router_note = f"\nrouter: {d['routing_filter']}" if d["hide_routing"] else ""
        title = (f"Gaussian routing optimality vs {lab(key)}\n"
                 f"{trend_desc}, one curve per configuration{router_note}")
    if not d.get("no_title"):
        ax.set_title(title, fontsize=fs_title, fontweight="bold")
    if fs_tick is not None:
        ax.tick_params(labelsize=fs_tick)
    ax.grid(alpha=0.25, zorder=0)
    if not d.get("no_legend"):
        ax.legend(fontsize=fs_leg, loc="best",
                  title="connectivity" if d["hide_routing"] else "connectivity / routing")
    fig.tight_layout()
    # paper mode: keep the exact figsize (no tight bbox, which would crop and change
    # the physical dimensions); tight_layout fits the labels inside the fixed canvas.
    if paper:
        fig.savefig(out_path, dpi=dpi, facecolor="white")
    else:
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
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
    p.add_argument("--schema", choices=sorted(SCHEMAS), default="runs",
                   help="Column schema of the runs CSV: 'runs' = benchmark CSVs "
                        "(routing_steps/status, default), 'wisq' = WISQ-comparison CSVs "
                        "such as data/results/single_config/*.csv (my_routing_steps/my_status).")
    p.add_argument("--routing", default=None, metavar="STRATEGY",
                   help="Keep only rows with this routing_strategy (e.g. naive_critical). "
                        "The router is then dropped from the legend (stated in the title "
                        "instead) and the WISQ baseline is disabled, so the plots show "
                        "exactly the remaining configurations.")
    p.add_argument("--no-rankings", action="store_true",
                   help="Skip the correlation-ranking charts (optimality_correlations_*.png, "
                        "the per-characteristic Spearman 'table'); only the per-characteristic "
                        "trend plots are produced.")
    p.add_argument("--no-legend", action="store_true",
                   help="Drop the legend from the trend plots only (the ranking charts keep "
                        "their positive/negative colour legend).")
    p.add_argument("--simple_text", action="store_true",
                   help="Minimal text on the trend plots: y axis 'Routing optimality', "
                        "x axis the characteristic name only (no formula), and a single-line "
                        "title 'Routing optimality vs <characteristic> (<fit> fit)'.")
    p.add_argument("--no_title", action="store_true",
                   help="Generate the trend plots without any title (axes and legend kept).")
    p.add_argument("--paper_dim", action="store_true",
                   help="Size the trend plots to Figure 6 of the paper "
                        f"({PAPER_FIG_W:.2f}x{PAPER_FIG_H:.2f} in = 0.8*column, IEEEtran) with "
                        "paper-scale fonts, and save at the exact size (no tight-bbox crop) so "
                        "LaTeX does not rescale. Include it at width=0.8\\linewidth. Pair with "
                        "--simple_text / --no_title for a clean paper figure.")
    p.add_argument("--fit",
                   choices=["poly", "monotone", "decay", "log", "binned", "power", "wls", "all"],
                   default="poly",
                   help="Trend fit for the per-characteristic plots: 'poly' (default) = "
                        "polynomials of degree 1..5 (can wiggle); 'monotone' = isotonic + "
                        "PCHIP (guaranteed monotone); 'decay' = saturating exponential; "
                        "'log' = logarithmic y=a+b*ln(x); 'binned' = PCHIP through equal-count "
                        "bin medians (robust, tracks the whole range); 'power' = power law "
                        "y=a*x^b (log-log fit); 'wls' = density-weighted log fit; "
                        "'all' = produce every fit for comparison.")
    p.add_argument("--bins", type=int, default=10,
                   help="Number of equal-count bins for the 'binned' fit (default 10).")
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--format", choices=["pdf", "png"], default="pdf",
                   help="Output image format: 'pdf' (default) is vector and keeps text "
                        "and curves sharp at any zoom, as required for paper figures; "
                        "'png' is raster and easier to skim in bulk.")
    args = p.parse_args()

    out_dir = args.out_dir or (Path(args.runs_csv).resolve().parent / "gaussian_overhead_plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    d = load(args.runs_csv, args.metrics, args.wisq_csv, args.schema, args.routing)
    if not d or not d["configs"]:
        print("ERROR: no data (check runs CSV and metrics).")
        return
    d["no_legend"] = args.no_legend      # affects the trend plots only
    d["simple_text"] = args.simple_text  # minimal axis/title text on the trend plots
    d["no_title"] = args.no_title        # drop the title on the trend plots
    d["paper_dim"] = args.paper_dim      # Figure-6 size + paper-scale fonts
    d["bins"] = args.bins                # number of bins for the 'binned' fit

    print(f"Configurations: {len(d['configs'])} | characteristics: {len(d['metrics'])}")
    if d["routing_filter"]:
        print(f"Router filter: {d['routing_filter']} (WISQ baseline disabled)")
    for cfg in d["configs"]:
        line = config_conn_route(cfg, d["cfg_cols"], d["const_params"], d["hide_routing"])
        detail = config_label(cfg, d["cfg_cols"])   # varying params, empty if none vary
        if detail and detail != line:
            line += f"   [{detail}]"
        print(f"  - {line}  ({len(d['optimality'][cfg])} circuits)")

    # correlation rankings stay in the root out-dir (skipped with --no-rankings)
    if not args.no_rankings:
        for cfg in d["configs"]:
            pairs = list(d["optimality"][cfg].items())
            subtitle = f"config: {config_conn_route(cfg, d['cfg_cols'], d['const_params'], d['hide_routing'])}"
            if d["routing_filter"]:
                subtitle += f"   |   router: {d['routing_filter']}"
            plot_correlation_ranking(d, pairs, subtitle,
                                     out_dir / f"optimality_correlations_"
                                               f"{config_slug(cfg, d['cfg_cols'], d['const_params'])}"
                                               f".{args.format}")
        # one combined ranking pooling all configurations
        combined = [(c, ov) for cfg in d["configs"] for c, ov in d["optimality"][cfg].items()]
        plot_correlation_ranking(d, combined, "combined (all configurations pooled)",
                                 out_dir / f"optimality_correlations_combined.{args.format}")

    # trend curves: one subfolder per characteristic. Which curves go inside
    # depends on --fit (poly -> 5 degree files, monotone/decay -> 1 file each,
    # all -> every one, so the fits can be compared side by side).
    do_poly = args.fit in ("poly", "all")
    do_monotone = args.fit in ("monotone", "all")
    do_decay = args.fit in ("decay", "all")
    do_log = args.fit in ("log", "all")
    do_binned = args.fit in ("binned", "all")
    do_power = args.fit in ("power", "all")
    do_wls = args.fit in ("wls", "all")
    degrees = [1, 2, 3, 4, 5]
    for k in d["metrics"]:
        sub = out_dir / metric_dirname(k)   # folder named like the ranking-chart label
        sub.mkdir(parents=True, exist_ok=True)
        if do_poly:
            for deg in degrees:
                plot_trend(d, k, "poly", sub / f"{k}_vs_optimality_deg{deg}.{args.format}", degree=deg)
        if do_monotone:
            plot_trend(d, k, "monotone", sub / f"{k}_vs_optimality_monotone.{args.format}")
        if do_decay:
            plot_trend(d, k, "decay", sub / f"{k}_vs_optimality_decay.{args.format}")
        if do_log:
            plot_trend(d, k, "log", sub / f"{k}_vs_optimality_log.{args.format}")
        if do_binned:
            plot_trend(d, k, "binned", sub / f"{k}_vs_optimality_binned.{args.format}")
        if do_power:
            plot_trend(d, k, "power", sub / f"{k}_vs_optimality_power.{args.format}")
        if do_wls:
            plot_trend(d, k, "wls", sub / f"{k}_vs_optimality_wls.{args.format}")
    per_char = (5 * do_poly + do_monotone + do_decay + do_log
                + do_binned + do_power + do_wls)
    ranking_note = ("no rankings (--no-rankings), " if args.no_rankings
                    else f"{len(d['configs'])} per-config + 1 combined ranking (root), ")
    print(f"Wrote {ranking_note}"
          f"{len(d['metrics'])} characteristic folders x {per_char} trend plots "
          f"(--fit {args.fit}) to {out_dir}/")


if __name__ == "__main__":
    main()
