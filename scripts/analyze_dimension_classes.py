#!/usr/bin/env python3
"""
Part 2 analysis: pairwise parameter comparison across 3 dimension classes
(low / mid / high) for benchmarks executed with x=0 in dimensions.csv.

For each CSV row produced by a `0` run we have 3 measurements of the same
configuration at 3 different grid sizes:
  - main row    -> HIGH (max_x / max_y)
  - mid_*       -> MID  ((min+max)/2)
  - lower_*     -> LOW  (min_x / min_y)

For each (circuit, dim_class) group we hold every other parameter fixed and
compute, for each varying parameter:
  * mean relative %-difference on routing_steps
  * mean relative %-difference on duration_seconds
  * absolute Delta on success rate (success / total)

The same logic is then applied to "compound" parameters, i.e. pairs (or more)
of single parameters treated as one categorical variable. Compound pairs are
plug-and-play through `COMPOUND_PARAMS` below; today the list is intentionally
empty (the user still needs to decide correlations) but the machinery is
already in place.

Outputs:
  benchmarks/results/<bench>/dim_classes/best_config_per_dim.csv
  benchmarks/results/<bench>/dim_classes/pairwise_<param>_<dim>.csv
  benchmarks/results/<bench>/dim_classes/plots/*.png
"""

import argparse
import csv
import glob
import os
import statistics
import sys
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)


SUCCESS_STATUSES = {"ok", "ok_no_routing_metric", "success"}

DIM_CLASSES = ("low", "mid", "high")

# Per-dim-class field mapping: which CSV columns hold the routing_steps,
# duration, status and x/y for each dim class.
DIM_FIELDS: Dict[str, Dict[str, str]] = {
    "low":  {"steps": "lower_routing_steps", "duration": "lower_duration_seconds", "status": "lower_status", "x": "lower_x", "y": "lower_y"},
    "mid":  {"steps": "mid_routing_steps",   "duration": "mid_duration_seconds",   "status": "mid_status",   "x": "mid_x",   "y": "mid_y"},
    "high": {"steps": "routing_steps",       "duration": "duration_seconds",       "status": "status",       "x": "graph_x", "y": "graph_y"},
}

# Configurable list of single parameters to analyze. Each entry is a CSV
# column name; only parameters that actually vary in the data will produce
# pairwise comparisons.
SINGLE_PARAMS = [
    "mapping_type",
    "magic_aware_strategy",
    "gaussian_strategy",
    "safe_passage_strategy",
    "magic_state_placement_strategy",
    "border_distance_percentage",
    "number_of_magic_states",
    "routing_strategy",
    "t_routing_mode",
    "use_layer_cache",
    "size_moltiplier",
    "gaussian_confidence",
    "magic_high",
    "magic_low",
    "cnot_high",
    "cnot_low",
    "mapped_gaussian_weight",
    "base_gaussian_weight",
]

# Compound (correlated) parameters. Each entry is a tuple of CSV column names;
# their concatenated value becomes the categorical level. Empty for now.
# Example to enable later:
#   COMPOUND_PARAMS = [("mapping_type", "safe_passage_strategy")]
COMPOUND_PARAMS: List[Tuple[str, ...]] = []


# ---------- I/O ----------

def resolve_runs_csv(csv_arg: str) -> str:
    """Resolve --csv as one explicit CSV path."""
    if os.path.isfile(csv_arg):
        return csv_arg
    raise FileNotFoundError(f"No CSV found: {csv_arg}")


def distinct_runs_csvs() -> List[str]:
    """--distinct mode: every *_runs.csv directly under benchmarks/results."""
    pattern = os.path.join("benchmarks", "results", "*_runs.csv")
    matches = sorted(glob.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No CSV found under {pattern}")
    return matches


def read_rows(path: str) -> List[Dict[str, str]]:
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------- transformation ----------

def to_float(value: str) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def explode_by_dim(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """For each input row, emit up to 3 logical rows (one per dim class) with
    normalized fields: routing_steps_n, duration_n, status_n, dim_class, graph_x_n, graph_y_n.
    Configuration parameters (mapping_type, safe_passage_strategy, ...) are kept as-is.
    Rows with empty status for a given dim class are skipped (no measurement)."""
    exploded: List[Dict[str, str]] = []
    for row in rows:
        for dim_class, fields in DIM_FIELDS.items():
            status = (row.get(fields["status"]) or "").strip()
            if status == "":
                continue
            new = dict(row)
            new["dim_class"] = dim_class
            new["routing_steps_n"] = row.get(fields["steps"], "") or ""
            new["duration_n"] = row.get(fields["duration"], "") or ""
            new["status_n"] = status
            new["graph_x_n"] = row.get(fields["x"], "") or ""
            new["graph_y_n"] = row.get(fields["y"], "") or ""
            exploded.append(new)
    return exploded


# ---------- pairwise statistics ----------

def make_signature(row: Dict[str, str], exclude: Sequence[str]) -> Tuple:
    """Identity of a configuration ignoring the parameters under test plus
    the dim_class itself. Two rows with the same signature differ only on the
    excluded parameters (and on the measurements / metadata)."""
    keys_to_use = [k for k in SINGLE_PARAMS if k not in exclude]
    return tuple((k, (row.get(k) or "").strip()) for k in keys_to_use)


def relative_pct_diff(a: float, b: float) -> Optional[float]:
    """Symmetric relative %-difference (b vs a). None if a==0."""
    if a == 0:
        return None
    return (b - a) / a * 100.0


def pairwise_for_param(
    exploded_rows: List[Dict[str, str]],
    param: str,
    dim_class: str,
) -> Dict[Tuple[str, str], Dict[str, float]]:
    """For a given parameter name and dim_class, group rows by (circuit, signature)
    where signature ignores `param`, then for every pair of distinct param values
    inside the group compute the relative %-difference of routing_steps and duration,
    plus the success rate delta. Aggregate across all such pairs.

    For compound parameters, pass a tuple of column names as `param` together with
    a special marker handled by the caller — this helper only knows about a single
    column. Compound logic lives in `pairwise_for_compound`."""
    # filter to one dim class
    rows = [r for r in exploded_rows if r["dim_class"] == dim_class]
    # bucket by (circuit, signature_excluding_param)
    buckets: Dict[Tuple[str, Tuple], Dict[str, List[Dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        sig = make_signature(r, exclude=[param])
        circuit = (r.get("circuit") or "").strip()
        param_value = (r.get(param) or "").strip()
        if circuit == "" or param_value == "":
            continue
        buckets[(circuit, sig)][param_value].append(r)

    # pair_stats[(a, b)] -> list of (delta_steps_pct, delta_dur_pct, delta_success)
    pair_stats: Dict[Tuple[str, str], Dict[str, List[float]]] = defaultdict(
        lambda: {"steps_pct": [], "dur_pct": [], "success_delta": []}
    )

    for (_circuit, _sig), per_param_rows in buckets.items():
        values = sorted(per_param_rows.keys())
        if len(values) < 2:
            continue
        for i, a in enumerate(values):
            for b in values[i + 1:]:
                ra_list = per_param_rows[a]
                rb_list = per_param_rows[b]
                # mean success rate per side
                def succ_rate(group):
                    if not group:
                        return None
                    n_succ = sum(1 for x in group if x["status_n"] in SUCCESS_STATUSES)
                    return n_succ / len(group)
                sa = succ_rate(ra_list)
                sb = succ_rate(rb_list)
                if sa is not None and sb is not None:
                    pair_stats[(a, b)]["success_delta"].append(sb - sa)
                # mean steps / duration on success only
                def mean_metric(group, field):
                    vals = [to_float(x[field]) for x in group if x["status_n"] in SUCCESS_STATUSES]
                    vals = [v for v in vals if v is not None]
                    return statistics.mean(vals) if vals else None
                steps_a = mean_metric(ra_list, "routing_steps_n")
                steps_b = mean_metric(rb_list, "routing_steps_n")
                if steps_a is not None and steps_b is not None:
                    d = relative_pct_diff(steps_a, steps_b)
                    if d is not None:
                        pair_stats[(a, b)]["steps_pct"].append(d)
                dur_a = mean_metric(ra_list, "duration_n")
                dur_b = mean_metric(rb_list, "duration_n")
                if dur_a is not None and dur_b is not None:
                    d = relative_pct_diff(dur_a, dur_b)
                    if d is not None:
                        pair_stats[(a, b)]["dur_pct"].append(d)

    # aggregate
    out: Dict[Tuple[str, str], Dict[str, float]] = {}
    for pair, stats in pair_stats.items():
        out[pair] = {
            "steps_pct_mean": statistics.mean(stats["steps_pct"]) if stats["steps_pct"] else float("nan"),
            "dur_pct_mean":   statistics.mean(stats["dur_pct"])   if stats["dur_pct"]   else float("nan"),
            "success_delta_mean": statistics.mean(stats["success_delta"]) if stats["success_delta"] else float("nan"),
            "n_pairs_steps": len(stats["steps_pct"]),
            "n_pairs_dur":   len(stats["dur_pct"]),
            "n_pairs_success": len(stats["success_delta"]),
        }
    return out


def pairwise_for_compound(
    exploded_rows: List[Dict[str, str]],
    compound_keys: Tuple[str, ...],
    dim_class: str,
) -> Dict[Tuple[str, str], Dict[str, float]]:
    """Same logic as pairwise_for_param but the "parameter under test" is a
    tuple of columns whose values are concatenated with `+` into a single level."""
    rows = [r for r in exploded_rows if r["dim_class"] == dim_class]
    # virtual column
    for r in rows:
        r["_compound_n"] = "+".join((r.get(k) or "").strip() for k in compound_keys)
    return pairwise_for_param(rows, "_compound_n", dim_class)


# ---------- best config ----------

def best_config_per_dim(exploded_rows: List[Dict[str, str]]) -> Dict[str, Dict]:
    """For each dim_class, the best config is the one with the lowest mean
    routing_steps on successful runs (averaged across circuits). Ties broken by
    lowest mean duration. We use the full parameter signature (all SINGLE_PARAMS)
    as the configuration identity."""
    out: Dict[str, Dict] = {}
    for dim in DIM_CLASSES:
        rows = [r for r in exploded_rows if r["dim_class"] == dim and r["status_n"] in SUCCESS_STATUSES]
        per_config: Dict[Tuple, Dict[str, List[float]]] = defaultdict(lambda: {"steps": [], "dur": [], "succ_total": 0, "succ_ok": 0})
        # also count total per config (including failures) for success rate
        all_rows = [r for r in exploded_rows if r["dim_class"] == dim]
        per_config_total: Dict[Tuple, int] = defaultdict(int)
        per_config_ok: Dict[Tuple, int] = defaultdict(int)
        for r in all_rows:
            sig = tuple((k, (r.get(k) or "").strip()) for k in SINGLE_PARAMS)
            per_config_total[sig] += 1
            if r["status_n"] in SUCCESS_STATUSES:
                per_config_ok[sig] += 1
        for r in rows:
            sig = tuple((k, (r.get(k) or "").strip()) for k in SINGLE_PARAMS)
            v = to_float(r["routing_steps_n"])
            if v is not None:
                per_config[sig]["steps"].append(v)
            d = to_float(r["duration_n"])
            if d is not None:
                per_config[sig]["dur"].append(d)
        ranked = []
        for sig, vals in per_config.items():
            if not vals["steps"]:
                continue
            mean_steps = statistics.mean(vals["steps"])
            mean_dur = statistics.mean(vals["dur"]) if vals["dur"] else float("nan")
            total = per_config_total[sig]
            ok = per_config_ok[sig]
            ranked.append((mean_steps, mean_dur, ok / total if total else 0.0, sig, ok, total))
        ranked.sort(key=lambda x: (x[0], x[1]))
        out[dim] = {"ranked": ranked}
    return out


# ---------- output ----------

def write_pairwise_csv(path: str, param_name: str, dim: str, pairs: Dict[Tuple[str, str], Dict[str, float]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "parameter", "dim_class", "value_a", "value_b",
            "steps_pct_mean", "dur_pct_mean", "success_delta_mean",
            "n_pairs_steps", "n_pairs_dur", "n_pairs_success",
        ])
        for (a, b), stats in sorted(pairs.items()):
            w.writerow([
                param_name, dim, a, b,
                f"{stats['steps_pct_mean']:.3f}",
                f"{stats['dur_pct_mean']:.3f}",
                f"{stats['success_delta_mean']:.3f}",
                stats["n_pairs_steps"], stats["n_pairs_dur"], stats["n_pairs_success"],
            ])


def write_best_config_csv(path: str, best: Dict[str, Dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        header = ["dim_class", "rank", "mean_routing_steps", "mean_duration_s", "success_rate", "n_ok", "n_total"]
        header += [p for p in SINGLE_PARAMS]
        w.writerow(header)
        for dim in DIM_CLASSES:
            ranked = best.get(dim, {}).get("ranked", [])
            for rank, (mean_steps, mean_dur, succ_rate, sig, n_ok, n_total) in enumerate(ranked, start=1):
                row = [dim, rank, f"{mean_steps:.2f}", f"{mean_dur:.4f}", f"{succ_rate:.3f}", n_ok, n_total]
                sig_dict = dict(sig)
                row += [sig_dict.get(p, "") for p in SINGLE_PARAMS]
                w.writerow(row)


def plot_pairwise(path: str, param_name: str, dim: str, pairs: Dict[Tuple[str, str], Dict[str, float]]) -> None:
    """One simple bar plot per (param, dim, metric)."""
    if not pairs:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sorted_pairs = sorted(pairs.items(), key=lambda kv: kv[0])
    labels = [f"{a} vs {b}" for (a, b), _ in sorted_pairs]

    metrics = [
        ("steps_pct_mean", "% routing_steps (b - a) / a", "#577590"),
        ("dur_pct_mean",   "% duration (b - a) / a",     "#E76F51"),
        ("success_delta_mean", "Delta success rate (b - a)", "#2A9D8F"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(max(12, 0.6 * len(labels) * 3), 4.2))
    for ax, (key, ylabel, color) in zip(axes, metrics):
        values = [stats[key] for _, stats in sorted_pairs]
        ax.bar(range(len(labels)), values, color=color)
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
        ax.set_ylabel(ylabel)
        ax.set_title(f"{param_name} - {dim}")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------- main ----------

def analyze_one_csv(csv_path: str, output_root: str) -> None:
    rows = read_rows(csv_path)
    if not rows:
        print(f"[skip] {csv_path}: empty")
        return

    # Detect whether this CSV has multi-dimension data at all
    has_dim_data = any(
        (r.get("mid_status") or "").strip() or (r.get("lower_status") or "").strip()
        for r in rows
    )
    if not has_dim_data:
        print(f"[skip] {csv_path}: no mid/lower data (probably not a multi-dim run)")
        return

    exploded = explode_by_dim(rows)
    if not exploded:
        print(f"[skip] {csv_path}: no rows with valid dim class status")
        return

    bench_name = os.path.splitext(os.path.basename(csv_path))[0]
    out_dir = os.path.join(output_root, bench_name, "dim_classes")
    plots_dir = os.path.join(out_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    print(f"[run] {csv_path} -> {out_dir}")
    print(f"  exploded rows: {len(exploded)}")
    print(f"  per dim class: " + ", ".join(f"{d}={sum(1 for r in exploded if r['dim_class']==d)}" for d in DIM_CLASSES))

    # Single-parameter analysis
    for param in SINGLE_PARAMS:
        for dim in DIM_CLASSES:
            pairs = pairwise_for_param(exploded, param, dim)
            if not pairs:
                continue
            csv_out = os.path.join(out_dir, f"pairwise_{param}_{dim}.csv")
            write_pairwise_csv(csv_out, param, dim, pairs)
            plot_out = os.path.join(plots_dir, f"pairwise_{param}_{dim}.png")
            plot_pairwise(plot_out, param, dim, pairs)

    # Compound-parameter analysis (no-op when COMPOUND_PARAMS is empty)
    for compound in COMPOUND_PARAMS:
        cname = "+".join(compound)
        for dim in DIM_CLASSES:
            pairs = pairwise_for_compound(exploded, compound, dim)
            if not pairs:
                continue
            csv_out = os.path.join(out_dir, f"pairwise_compound_{cname}_{dim}.csv")
            write_pairwise_csv(csv_out, cname, dim, pairs)
            plot_out = os.path.join(plots_dir, f"pairwise_compound_{cname}_{dim}.png")
            plot_pairwise(plot_out, cname, dim, pairs)

    # Best config per dim_class
    best = best_config_per_dim(exploded)
    write_best_config_csv(os.path.join(out_dir, "best_config_per_dim.csv"), best)
    print(f"  best config table written: best_config_per_dim.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description="Part-2 analysis: pairwise param comparison across low/mid/high dimensions.")
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--csv", help="Path to one explicit *_runs.csv file")
    input_group.add_argument(
        "--distinct",
        action="store_true",
        help="Analyze every *_runs.csv directly under benchmarks/results.",
    )
    parser.add_argument(
        "--output-root",
        default=os.path.join("benchmarks", "results"),
        help="Directory under which to place <bench>/dim_classes/",
    )
    args = parser.parse_args()

    if not args.csv and not args.distinct:
        print("No input specified. Pass --csv for one file or --distinct for every *_runs.csv.")
        return 0

    try:
        csvs = [resolve_runs_csv(args.csv)] if args.csv else distinct_runs_csvs()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    for path in csvs:
        analyze_one_csv(path, args.output_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
