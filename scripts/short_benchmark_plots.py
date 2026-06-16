#!/usr/bin/env python3
"""
Focused benchmark plots: overview + correlated-option heatmaps (routing steps
and duration, always both) + per-circuit boxplots + runtime curves.
"""

import argparse
import csv
import glob
import math
import os
import statistics
import warnings
from collections import Counter, defaultdict

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)


def _import_matplotlib():
    global plt, np
    import matplotlib.pyplot as plt
    import numpy as np


# ── constants ─────────────────────────────────────────────────────────────────

SUCCESS_STATUSES = {"ok", "ok_no_routing_metric", "success"}
TIMEOUT_STATUSES = {"timeout"}
DEFAULT_RESULTS_DIR = os.path.join("benchmarks", "results")
DEFAULT_CSV_GLOB = os.path.join(DEFAULT_RESULTS_DIR, "**", "*.csv")

STATUS_DISPLAY_LABELS = {
    "ok": "ok",
    "ok_no_routing_metric": "ok (no routing metric)",
    "success": "success",
    "failed": "failed",
    "timeout": "timeout",
    "interrupted": "interrupted (signal)",
}
STATUS_COLORS = {
    "ok": "#2A9D8F",
    "ok_no_routing_metric": "#2A9D8F",
    "success": "#2A9D8F",
    "failed": "#E76F51",
    "timeout": "#E9C46A",
    "interrupted": "#577590",
}
_EXTRA_STATUS_PALETTE = ["#264653", "#9B2226", "#005F73", "#CA6702",
                          "#0A9396", "#AE2012", "#BB3E03", "#94D2BD"]

# Correlated axis pairs: (row_key, col_key, row_label, col_label, filter_fn)
# filter_fn(row) -> bool; None means use all rows.
HEATMAP_PAIRS = [
    ("mapping_type_norm",         "safe_passage_norm",     "mapping type",       "safe passage",    None),
    ("routing_strategy_norm",     "safe_passage_norm",     "routing strategy",   "safe passage",    None),
    ("t_routing_mode_norm",       "mapping_type_norm",     "T routing mode",     "mapping type",    None),
    ("placement_detail",          "safe_passage_norm",     "magic placement",    "safe passage",    None),
    ("gaussian_strategy_norm",    "safe_passage_norm",     "gaussian strategy",  "safe passage",    lambda r: r.get("mapping_type_norm") == "gaussian"),
    ("magic_aware_strategy_norm", "safe_passage_norm",     "magic-aware strat",  "safe passage",    lambda r: r.get("mapping_type_norm") == "magic_aware"),
    ("gaussian_confidence_label", "safe_passage_norm",     "gaussian conf",      "safe passage",    lambda r: r.get("mapping_type_norm") == "gaussian"),
    ("use_layer_cache_norm",      "safe_passage_norm",     "layer cache",        "safe passage",    None),
]

# ── normalisation helpers ─────────────────────────────────────────────────────

def _normalize_text(value):
    return "" if value is None else str(value).strip().lower()

def _normalize_csv_text(value):
    return "" if value is None else str(value).strip()

def _normalize_fieldname(value):
    return "" if value is None else str(value).strip()

def _normalize_placement(value):
    p = _normalize_text(value)
    if p in {"rightrow", "right_row", "right-row"}:
        return "right_row"
    if p in {"centercircle", "center_circle", "center-circle"}:
        return "center_circle"
    return p

def _pick_first(row, *keys):
    for key in keys:
        v = row.get(key)
        if v is not None and not (isinstance(v, str) and v.strip() == ""):
            return v
    return None

def _to_float(value):
    if value is None:
        return None
    s = str(value).strip()
    try:
        return float(s)
    except ValueError:
        return None

def _to_int(value):
    if value is None:
        return None
    s = str(value).strip()
    try:
        return int(s)
    except ValueError:
        try:
            return int(float(s))
        except ValueError:
            return None

def _format_label(value):
    if value is None:
        return "n/a"
    if isinstance(value, str):
        parsed = _to_float(value)
        if parsed is None:
            return value.strip() or "n/a"
        value = parsed
    if math.isnan(value):
        return "n/a"
    return str(int(round(value))) if abs(value - round(value)) < 1e-9 else f"{value:.3g}"

def _format_gaussian_confidence_label(value):
    if value is None:
        return "n/a"
    if isinstance(value, str):
        parsed = _to_float(value)
        if parsed is None:
            return value.strip() or "n/a"
        value = parsed
    if math.isnan(value):
        return "n/a"
    if 0.0 < value < 1.0:
        return f"{value:.10f}".rstrip("0").rstrip(".")
    return _format_label(value)

def _classify_placement(row):
    p = _normalize_placement(row.get("placement"))
    if p == "right_row":
        return "right_row"
    b = row.get("border_pct_f")
    if p == "center_circle" and b is not None:
        if abs(b) < 1e-9:
            return "center_circle_0"
        if abs(b - 5.0) < 1e-9:
            return "center_circle_5"
    return None

def _placement_detail(row):
    p = _normalize_placement(row.get("placement"))
    if not p:
        return "unknown"
    if p == "center_circle":
        b = row.get("border_pct_f")
        if b is not None and not math.isnan(b):
            return f"center_circle({_format_label(b)}%)"
    return p

# ── data loading ──────────────────────────────────────────────────────────────

def load_raw_rows(files):
    rows, fieldnames, seen_fieldnames, accepted_files = [], [], set(), []
    for path in files:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue
            norm_fields, norm_to_orig = [], {}
            for field in reader.fieldnames:
                n = _normalize_fieldname(field)
                if not n or n in norm_to_orig:
                    continue
                norm_fields.append(n)
                norm_to_orig[n] = field
            if "status" not in norm_fields or (
                "run_id" not in norm_fields and "id" not in norm_fields
            ):
                continue
            accepted_files.append(path)
            for field in norm_fields:
                if field not in seen_fieldnames:
                    fieldnames.append(field)
                    seen_fieldnames.add(field)
            for raw in reader:
                row = {f: raw.get(norm_to_orig[f], "") for f in norm_fields}
                if "run_id" not in row and "id" in row:
                    row["run_id"] = row["id"]
                row["source_csv"] = path
                rows.append(row)
    return rows, fieldnames, accepted_files


def prepare_rows(raw_rows):
    rows = []
    for raw in raw_rows:
        r = dict(raw)
        r["circuit_name"] = os.path.basename(r.get("circuit", ""))
        r["placement"] = _normalize_placement(
            _pick_first(r, "magic_state_placement_strategy", "placement")
        )
        r["mapping_type_norm"]         = _normalize_text(r.get("mapping_type"))
        r["safe_passage_norm"]         = _normalize_text(r.get("safe_passage_strategy"))
        r["magic_aware_strategy_norm"] = _normalize_text(r.get("magic_aware_strategy"))
        r["gaussian_strategy_norm"]    = _normalize_text(r.get("gaussian_strategy"))
        r["routing_strategy_norm"]     = _normalize_text(r.get("routing_strategy"))
        r["t_routing_mode_norm"]       = _normalize_text(r.get("t_routing_mode"))
        r["use_layer_cache_norm"]      = _normalize_text(r.get("use_layer_cache"))
        r["x_i"] = _to_int(_pick_first(r, "graph_x", "x"))
        r["y_i"] = _to_int(_pick_first(r, "graph_y", "y"))
        r["border_pct_f"]            = _to_float(r.get("border_distance_percentage"))
        r["gaussian_confidence_f"]   = _to_float(r.get("gaussian_confidence"))
        r["gaussian_confidence_label"] = _format_gaussian_confidence_label(r["gaussian_confidence_f"]) if r["gaussian_confidence_f"] is not None else ""
        dur_s  = _to_float(r.get("duration_seconds"))
        dur_ms = _to_float(r.get("elapsed_ms"))
        r["duration_s_f"]    = dur_s if dur_s is not None else (dur_ms / 1000.0 if dur_ms is not None else None)
        r["routing_steps_f"] = _to_float(_pick_first(r, "routing_steps", "total_routing_steps"))
        r["non_routed_layer_pct_f"] = _to_float(r.get("non_routed_layer_pct"))
        r["avg_parallelism_f"] = _to_float(r.get("avg_parallelism"))
        r["exit_code_i"]     = _to_int(r.get("exit_code"))
        r["success"]         = _normalize_text(r.get("status")) in SUCCESS_STATUSES
        r["placement_variant"] = _classify_placement(r)
        r["placement_detail"]  = _placement_detail(r)
        rows.append(r)
    return rows


def register_extra_statuses(rows):
    for i, status in enumerate(sorted({
        _normalize_text(r.get("status"))
        for r in rows
        if r.get("status") and _normalize_text(r.get("status")) not in STATUS_COLORS
    })):
        STATUS_DISPLAY_LABELS[status] = status.replace("_", " ")
        STATUS_COLORS[status] = _EXTRA_STATUS_PALETTE[i % len(_EXTRA_STATUS_PALETTE)]


def exclude_timeouts(rows):
    return [r for r in rows if _normalize_text(r.get("status")) not in TIMEOUT_STATUSES]

# ── plot utilities ────────────────────────────────────────────────────────────

def _non_empty(values):
    return [v for v in values if v is not None and not math.isnan(v)]

def _label_n(label, n):
    return f"{label}\n(n={n})"

def _status_color(status):
    return STATUS_COLORS.get(status, "#577590")

def _annotate_bars(ax, bars, fmt="{:.0f}"):
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h, fmt.format(h),
                ha="center", va="bottom", fontsize=8)

def _save(fig, output_dir, filename, generated, dpi=160, subfolder=None):
    target = os.path.join(output_dir, subfolder) if subfolder else output_dir
    os.makedirs(target, exist_ok=True)
    path = os.path.join(target, filename)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    generated.append(path)

def _empty_plot(title, output_dir, filename, generated, message="No data", subfolder=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title(title, fontsize=14)
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes,
            fontsize=13, color="#64748B")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    _save(fig, output_dir, filename, generated, subfolder=subfolder)

def _record_skip(skipped, filename, reason):
    if skipped is not None:
        skipped.append({"filename": filename, "reason": reason})

def _iqr_filter(values):
    if not values:
        return []
    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [v for v in values if lo <= v <= hi] or values

# ── heatmap core ──────────────────────────────────────────────────────────────

def _axis_value(row, key):
    v = row.get(key)
    return str(v).strip() if v is not None and str(v).strip() else "unknown"

def _axis_sort_key(key, label):
    if key in {"gaussian_confidence_label", "magic_states_label"}:
        n = _to_float(label)
        if n is not None:
            return (0, n, label)
    return (1, str(label))

def _has_axis_value(row, key):
    v = row.get(key)
    if v is None:
        return False
    return bool(str(v).strip()) and str(v).strip().lower() != "unknown"

def _filter_heatmap(rows, row_key, col_key):
    return [r for r in rows if _has_axis_value(r, row_key) and _has_axis_value(r, col_key)]

def _make_heatmap(
    rows, row_key, col_key, value_fn,
    title, colorbar_label, filename,
    output_dir, generated, skipped=None,
    value_format="{:.2f}", subfolder=None,
):
    row_labels = sorted({_axis_value(r, row_key) for r in rows},
                        key=lambda lbl: _axis_sort_key(row_key, lbl))
    col_labels = sorted({_axis_value(r, col_key) for r in rows},
                        key=lambda lbl: _axis_sort_key(col_key, lbl))
    if not row_labels or not col_labels:
        _empty_plot(title, output_dir, filename, generated, subfolder=subfolder)
        return

    matrix = np.full((len(row_labels), len(col_labels)), np.nan, dtype=float)
    counts  = np.zeros((len(row_labels), len(col_labels)), dtype=int)
    ri = {k: i for i, k in enumerate(row_labels)}
    ci = {k: i for i, k in enumerate(col_labels)}

    grouped = defaultdict(list)
    for r in rows:
        grouped[(_axis_value(r, row_key), _axis_value(r, col_key))].append(r)

    for (rk, ck), subset in grouped.items():
        val = value_fn(subset)
        counts[ri[rk], ci[ck]] = len(subset)
        if val is not None:
            matrix[ri[rk], ci[ck]] = val

    fig, ax = plt.subplots(
        figsize=(max(7, len(col_labels) * 1.15), max(5, len(row_labels) * 0.9))
    )
    im = ax.imshow(np.ma.masked_invalid(matrix), cmap="viridis", aspect="auto")
    fig.colorbar(im, ax=ax).set_label(colorbar_label)
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=30, ha="right")
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.set_title(title)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val, n = matrix[i, j], counts[i, j]
            metric_text = "-" if np.isnan(val) else value_format.format(val)
            if np.isnan(val):
                color = "#999999"
            else:
                red, green, blue, _ = im.cmap(im.norm(val))
                lum = 0.2126 * red + 0.7152 * green + 0.0722 * blue
                color = "white" if lum < 0.45 else "#111111"
            ax.text(j, i, f"{metric_text}\nn={n}", ha="center", va="center",
                    color=color, fontsize=7, linespacing=0.9)

    _save(fig, output_dir, filename, generated, subfolder=subfolder)


def _plot_pair_heatmaps(
    rows_all, rows_routing, rows_duration, rows_non_routed, rows_avg,
    row_key, col_key, row_label, col_label,
    prefix, output_dir, generated, skipped=None, subfolder=None,
):
    """Emit five heatmaps (success rate, routing steps, duration, non-routed layer %, avg parallelism) for one axis pair."""

    def mean_routing(subset):
        vals = _non_empty([r["routing_steps_f"] for r in subset])
        return float(np.mean(vals)) if vals else None

    def mean_duration(subset):
        vals = _non_empty([r["duration_s_f"] for r in subset])
        return float(np.mean(vals)) if vals else None

    def mean_non_routed(subset):
        vals = _non_empty([r["non_routed_layer_pct_f"] for r in subset])
        return float(np.mean(vals)) if vals else None

    def mean_avg_parallelism(subset):
        vals = _non_empty([r["avg_parallelism_f"] for r in subset])
        return float(np.mean(vals)) if vals else None

    def success_rate(subset):
        return (100.0 * sum(r["success"] for r in subset) / len(subset)) if subset else None

    specs = [
        (rows_all,         "success_rate",    success_rate,    f"Success Rate: {row_label} × {col_label}",          "success rate (%)",            "{:.1f}"),
        (rows_routing,     "routing_steps",   mean_routing,    f"Routing Steps: {row_label} × {col_label}",         "mean routing steps",          "{:.0f}"),
        (rows_duration,    "duration",        mean_duration,   f"Duration (s): {row_label} × {col_label}",          "mean duration (s)",           "{:.2f}"),
        (rows_non_routed,  "non_routed_pct",  mean_non_routed, f"Non-routed Layer %: {row_label} × {col_label}",    "mean non-routed layer pct (%)", "{:.2f}"),
        (rows_avg,         "avg_parallelism", mean_avg_parallelism, f"Avg Parallelism: {row_label} × {col_label}",  "mean avg parallelism",          "{:.2f}"),
    ]
    for pool, tag, value_fn, title, cbar, fmt in specs:
        hm_rows = _filter_heatmap(pool, row_key, col_key)
        filename = f"{prefix}_{tag}__{row_key}_vs_{col_key}.png"
        if not hm_rows:
            _record_skip(skipped, filename, f"no rows with both {row_key} and {col_key}")
            continue
        _make_heatmap(
            hm_rows, row_key, col_key, value_fn,
            title, cbar, filename,
            output_dir, generated, skipped,
            value_format=fmt, subfolder=subfolder,
        )

# ── individual plot functions ─────────────────────────────────────────────────

def plot_overview(rows, output_dir, generated):
    status_counts = Counter(r["status"] for r in rows)
    circuits      = sorted({r["circuit_name"] for r in rows if r["circuit_name"]})
    cct_counts    = Counter(r["circuit_name"] for r in rows)

    success_rate_by_cct = {
        c: 100.0 * sum(1 for r in rows if r["circuit_name"] == c and r["success"]) / max(1, cct_counts[c])
        for c in circuits
    }
    routing_ok  = _non_empty([r["routing_steps_f"] for r in rows if r["success"]])
    duration_ok = _non_empty([r["duration_s_f"] for r in rows if r["success"]])

    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    axs = axs.flatten()

    # 0 — status counts
    s_keys = list(status_counts.keys())
    bars = axs[0].bar(s_keys, [status_counts[k] for k in s_keys],
                      color=[_status_color(k) for k in s_keys])
    axs[0].set_title("Runs by Status")
    axs[0].set_ylabel("count")
    _annotate_bars(axs[0], bars)

    # 1 — success rate by circuit
    bars = axs[1].bar(circuits, [success_rate_by_cct[c] for c in circuits], color="#43AA8B")
    axs[1].set_title("Success Rate by Circuit")
    axs[1].set_ylabel("%")
    axs[1].set_ylim(0, 108)
    axs[1].set_xticks(range(len(circuits)))
    axs[1].set_xticklabels([_label_n(c, cct_counts[c]) for c in circuits])
    axs[1].tick_params(axis="x", rotation=35)
    _annotate_bars(axs[1], bars, fmt="{:.1f}")

    # 2 — routing steps histogram
    if routing_ok:
        axs[2].hist(routing_ok, bins=min(20, max(6, int(len(routing_ok) ** 0.5))), color="#90BE6D")
    axs[2].set_title(f"Routing Steps Distribution (n={len(routing_ok)})")
    axs[2].set_xlabel("routing steps")

    # 3 — duration histogram
    if duration_ok:
        axs[3].hist(duration_ok, bins=min(20, max(6, int(len(duration_ok) ** 0.5))), color="#277DA1")
    axs[3].set_title(f"Duration Distribution (n={len(duration_ok)})")
    axs[3].set_xlabel("duration (s)")

    # 4 — routing steps by mapping type
    routing_by_map = defaultdict(list)
    for r in rows:
        if r["success"] and r["routing_steps_f"] is not None:
            routing_by_map[r["mapping_type_norm"] or "unknown"].append(r["routing_steps_f"])
    map_labels = sorted(routing_by_map)
    if map_labels:
        axs[4].boxplot([routing_by_map[k] for k in map_labels],
                       tick_labels=map_labels, showfliers=False)
    axs[4].set_title("Routing Steps by Mapping Type")
    axs[4].set_ylabel("routing steps")
    axs[4].tick_params(axis="x", rotation=20)

    # 5 — duration by mapping type
    dur_by_map = defaultdict(list)
    for r in rows:
        if r["duration_s_f"] is not None:
            dur_by_map[r["mapping_type_norm"] or "unknown"].append(r["duration_s_f"])
    if map_labels:
        axs[5].boxplot([dur_by_map.get(k, [0]) for k in map_labels],
                       tick_labels=map_labels, showfliers=False)
    axs[5].set_title("Duration by Mapping Type")
    axs[5].set_ylabel("duration (s)")
    axs[5].tick_params(axis="x", rotation=20)

    _save(fig, output_dir, "00_overview.png", generated)


def plot_boxplot(rows, cat_key, val_key, title, ylabel, filename,
                 output_dir, generated, skipped=None, min_pts=2):
    grouped = defaultdict(list)
    for r in rows:
        cat = str(r.get(cat_key) or "unknown")
        val = r.get(val_key)
        if val is None or (isinstance(val, float) and math.isnan(val)):
            continue
        grouped[cat].append(val)

    labels = [k for k in sorted(grouped) if len(grouped[k]) >= min_pts]
    if not labels:
        _record_skip(skipped, filename, f"no category with ≥{min_pts} values")
        return

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.1), 6.5))
    ax.boxplot(
        [grouped[k] for k in labels],
        tick_labels=[_label_n(k, len(grouped[k])) for k in labels],
        showfliers=False,
    )
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35)
    _save(fig, output_dir, filename, generated)


def plot_runtime_by_graph_nodes(rows, output_dir, generated, skipped=None):
    MAPPING_TYPES  = ("gaussian", "magic_aware", "homogeneous")
    SAFE_PASSAGES  = ("cube", "connectivity")
    colors     = {"gaussian": "#D55E00", "magic_aware": "#0072B2", "homogeneous": "#009E73"}
    linestyles = {"cube": "-", "connectivity": "--"}
    markers    = {"cube": "o", "connectivity": "s"}

    for safe_passage in SAFE_PASSAGES:
        filename = f"10_runtime_vs_graph_nodes_{safe_passage}.png"
        fig, ax = plt.subplots(figsize=(11, 6))
        has_data = False

        for mapping_type in MAPPING_TYPES:
            grouped = defaultdict(list)
            for r in rows:
                if _normalize_text(r.get("status")) not in (SUCCESS_STATUSES | TIMEOUT_STATUSES):
                    continue
                if r.get("mapping_type_norm") != mapping_type:
                    continue
                if r.get("safe_passage_norm") != safe_passage:
                    continue
                dur = r.get("duration_s_f")
                if dur is None or dur <= 0:
                    continue
                x_i, y_i = r.get("x_i"), r.get("y_i")
                if x_i is None or y_i is None:
                    continue
                grouped[x_i * y_i].append(dur)

            if not grouped:
                continue
            x_vals = sorted(grouped)
            y_vals = [statistics.median(grouped[x]) for x in x_vals]
            ax.plot(x_vals, y_vals,
                    color=colors[mapping_type],
                    linestyle=linestyles[safe_passage],
                    marker=markers[safe_passage],
                    markersize=5, linewidth=1.8, alpha=0.9,
                    label=f"{mapping_type}")
            has_data = True

        if not has_data:
            _record_skip(skipped, filename, f"no data for safe_passage={safe_passage}")
            plt.close(fig)
            continue

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("graph nodes (x × y)")
        ax.set_ylabel("median duration (s)")
        ax.set_title(f"Duration vs Graph Size — {safe_passage}")
        ax.grid(True, which="both", linestyle=":", alpha=0.6)
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=9, frameon=True)
        _save(fig, output_dir, filename, generated)

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Focused benchmark plots.")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--csv", help="Single CSV input file.")
    g.add_argument("--csv-glob", default=DEFAULT_CSV_GLOB,
                   help=f"Glob for CSV inputs (default: {DEFAULT_CSV_GLOB})")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    _import_matplotlib()
    plt.style.use("seaborn-v0_8-whitegrid")

    if args.csv:
        p = os.path.expanduser(args.csv)
        candidates = [p, p + ".csv",
                      os.path.join(DEFAULT_RESULTS_DIR, os.path.basename(p)),
                      os.path.join(DEFAULT_RESULTS_DIR, os.path.basename(p) + ".csv")]
        input_files = next((([c] for c in candidates if os.path.isfile(c))), [])
        if not input_files:
            raise FileNotFoundError(f"Cannot find CSV: {args.csv}")
        output_dir = args.output_dir or os.path.join(
            os.path.dirname(input_files[0]),
            os.path.splitext(os.path.basename(input_files[0]))[0] + "_short_plots",
        )
    else:
        input_files = sorted(glob.glob(args.csv_glob, recursive=True))
        output_dir = args.output_dir or os.path.join(DEFAULT_RESULTS_DIR, "short_plots")

    raw_rows, _, csv_files = load_raw_rows(input_files)
    if not raw_rows:
        raise RuntimeError("No valid rows found.")

    rows = prepare_rows(raw_rows)
    register_extra_statuses(rows)
    rows = exclude_timeouts(rows)

    rows_routing     = [r for r in rows if r["success"] and r["routing_steps_f"] is not None]
    rows_duration    = [r for r in rows if r["success"] and r["duration_s_f"] is not None]
    rows_non_routed  = [r for r in rows if r["success"] and r["non_routed_layer_pct_f"] is not None]
    rows_avg         = [r for r in rows if r["success"] and r["avg_parallelism_f"] is not None]

    generated, skipped = [], []

    # core
    plot_overview(rows, output_dir, generated)
    plot_boxplot(rows_routing, "circuit_name", "routing_steps_f",
                 "Routing Steps by Circuit (success only)", "routing steps",
                 "01_routing_by_circuit.png", output_dir, generated, skipped)
    plot_boxplot(rows, "circuit_name", "duration_s_f",
                 "Duration by Circuit", "duration (s)",
                 "02_duration_by_circuit.png", output_dir, generated, skipped)
    plot_boxplot(rows_non_routed, "circuit_name", "non_routed_layer_pct_f",
                 "Non-routed Layer % by Circuit (success only)", "non-routed layer pct (%)",
                 "03_non_routed_pct_by_circuit.png", output_dir, generated, skipped)
    plot_boxplot(rows_avg, "circuit_name", "avg_parallelism_f",
                 "Avg Parallelism by Circuit (success only)", "avg parallelism",
                 "04_avg_parallelism_by_circuit.png", output_dir, generated, skipped)

    # heatmaps for each correlated pair (success rate + routing + duration + non-routed % + avg parallelism)
    for idx, (row_key, col_key, row_label, col_label, filter_fn) in enumerate(HEATMAP_PAIRS, start=5):
        if filter_fn is not None:
            pair_all         = [r for r in rows if filter_fn(r)]
            pair_routing     = [r for r in rows_routing if filter_fn(r)]
            pair_duration    = [r for r in rows_duration if filter_fn(r)]
            pair_non_routed  = [r for r in rows_non_routed if filter_fn(r)]
            pair_avg         = [r for r in rows_avg if filter_fn(r)]
        else:
            pair_all, pair_routing, pair_duration, pair_non_routed, pair_avg = rows, rows_routing, rows_duration, rows_non_routed, rows_avg

        subfolder = f"pair_{idx:02d}_{row_key}"
        _plot_pair_heatmaps(
            pair_all, pair_routing, pair_duration, pair_non_routed, pair_avg,
            row_key, col_key, row_label, col_label,
            f"{idx:02d}", output_dir, generated, skipped, subfolder=subfolder,
        )

    # runtime curves
    plot_runtime_by_graph_nodes(rows, output_dir, generated, skipped)

    print(f"Generated {len(generated)} plots → {output_dir}")
    for path in generated:
        print(f"  {os.path.relpath(path, output_dir)}")
    if skipped:
        print(f"\nSkipped {len(skipped)}:")
        for item in skipped:
            print(f"  {item['filename']}: {item['reason']}")


if __name__ == "__main__":
    main()
