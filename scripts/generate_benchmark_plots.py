#!/usr/bin/env python3

import argparse
import csv
import glob
import math
import os
import statistics
import warnings
from collections import Counter, defaultdict
from datetime import datetime

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

def importMatplotlib():
    global plt, np, Line2D
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D


SUCCESS_STATUSES = {"ok", "ok_no_routing_metric", "success"}
REQUESTED_SAFE_PASSAGES = {"passage", "cube"}
REQUESTED_PLACEMENT_VARIANTS = ("right_row", "center_circle_0", "center_circle_5")
REQUESTED_GAUSSIAN_STRATEGIES = {"coarse", "fine"}
REQUESTED_MAGIC_AWARE_STRATEGIES = {"center", "distance", "random"}
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
EXIT_CODE_DISPLAY_LABELS = {
    124: "124 (timeout)",
    129: "129 (SIGHUP)",
    130: "130 (Ctrl+C)",
    143: "143 (SIGTERM)",
}


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_placement(value):
    placement = normalize_text(value)
    if placement in {"rightrow", "right_row", "right-row"}:
        return "right_row"
    if placement in {"centercircle", "center_circle", "center-circle"}:
        return "center_circle"
    return placement


def pick_first(row, *keys):
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return value
    return None


def classify_placement_variant(row):
    placement = normalize_placement(row.get("placement"))
    if placement == "right_row":
        return "right_row"

    border = row.get("border_pct_f")
    if placement == "center_circle" and border is not None:
        if abs(border - 0.0) < 1e-9:
            return "center_circle_0"
        if abs(border - 5.0) < 1e-9:
            return "center_circle_5"
    return None


def placement_variant_label(variant):
    if variant == "right_row":
        return "right_row"
    if variant == "center_circle_0":
        return "center_circle(0%)"
    if variant == "center_circle_5":
        return "center_circle(5%)"
    return variant


def status_display_label(status):
    return STATUS_DISPLAY_LABELS.get(status, status or "unknown")


def status_color(status):
    return STATUS_COLORS.get(status, "#577590")


def exit_code_display_label(exit_code):
    code = to_int(exit_code)
    if code is None:
        text = str(exit_code).strip() if exit_code is not None else ""
        return text or "unknown"
    return EXIT_CODE_DISPLAY_LABELS.get(code, str(code))


def exit_code_color(exit_code):
    code = to_int(exit_code)
    if code == 124:
        return status_color("timeout")
    if code in {129, 130, 143}:
        return status_color("interrupted")
    return "#F9844A"


def to_float(value):
    if value is None:
        return None
    value = str(value).strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def to_int(value):
    if value is None:
        return None
    value = str(value).strip()
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return int(float(value))
        except ValueError:
            return None


def format_number_label(value):
    if value is None:
        return "n/a"
    if isinstance(value, str):
        parsed = to_float(value)
        if parsed is None:
            text = value.strip()
            return text or "n/a"
        value = parsed
    if math.isnan(value):
        return "n/a"
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.3g}"


def placement_detail_label(row):
    placement = normalize_placement(row.get("placement"))
    if not placement:
        return "unknown"

    if placement == "center_circle":
        border = row.get("border_pct_f")
        if border is not None and not math.isnan(border):
            return f"center_circle({format_number_label(border)}%)"
    return placement


def gaussian_weight_tuple(row):
    keys = (
        "magic_high_f",
        "magic_low_f",
        "cnot_high_f",
        "cnot_low_f",
        "mapped_gaussian_weight_f",
        "base_gaussian_weight_f",
    )
    values = []
    for key in keys:
        value = row.get(key)
        if value is None or math.isnan(value):
            return None
        values.append(float(value))
    return tuple(values)


def gaussian_weight_combo_label(row):
    if row.get("mapping_type_norm") != "gaussian":
        return None
    combo = gaussian_weight_tuple(row)
    if combo is None:
        return None
    magic_high, magic_low, cnot_high, cnot_low, mapped_weight, base_weight = combo
    return (
        f"magic {format_number_label(magic_high)}/{format_number_label(magic_low)}\n"
        f"cnot {format_number_label(cnot_high)}/{format_number_label(cnot_low)}\n"
        f"gauss {format_number_label(mapped_weight)}/{format_number_label(base_weight)}"
    )


def load_rows(csv_glob):
    files = sorted(glob.glob(csv_glob, recursive=True))
    return load_rows_from_files(files)


def load_rows_from_files(files):
    rows = []

    for path in files:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue
            if "run_id" not in reader.fieldnames or "status" not in reader.fieldnames:
                continue

            for raw in reader:
                row = dict(raw)
                row["source_csv"] = path
                row["source_csv_name"] = os.path.basename(path)
                row["circuit_name"] = os.path.basename(row.get("circuit", ""))
                row["placement"] = normalize_placement(
                    pick_first(row, "magic_state_placement_strategy", "placement")
                )
                row["mapping_type_norm"] = normalize_text(row.get("mapping_type"))
                row["safe_passage_norm"] = normalize_text(row.get("safe_passage_strategy"))
                row["magic_aware_strategy_norm"] = normalize_text(row.get("magic_aware_strategy"))
                row["gaussian_strategy_norm"] = normalize_text(row.get("gaussian_strategy"))

                row["x_i"] = to_int(pick_first(row, "graph_x", "x"))
                row["y_i"] = to_int(pick_first(row, "graph_y", "y"))
                row["total_nodes_i"] = to_int(row.get("total_nodes"))
                row["magic_states_f"] = to_float(row.get("number_of_magic_states"))
                row["border_pct_f"] = to_float(row.get("border_distance_percentage"))
                row["magic_high_f"] = to_float(row.get("magic_high"))
                row["magic_low_f"] = to_float(row.get("magic_low"))
                row["cnot_high_f"] = to_float(row.get("cnot_high"))
                row["cnot_low_f"] = to_float(row.get("cnot_low"))
                row["mapped_gaussian_weight_f"] = to_float(row.get("mapped_gaussian_weight"))
                row["base_gaussian_weight_f"] = to_float(row.get("base_gaussian_weight"))
                duration_seconds = to_float(row.get("duration_seconds"))
                elapsed_ms = to_float(row.get("elapsed_ms"))
                if duration_seconds is not None:
                    row["duration_s_f"] = duration_seconds
                elif elapsed_ms is not None:
                    row["duration_s_f"] = elapsed_ms / 1000.0
                else:
                    row["duration_s_f"] = None
                row["routing_steps_f"] = to_float(pick_first(row, "routing_steps", "total_routing_steps"))
                row["interaction_pressure_f"] = to_float(row.get("interaction_pressure"))
                row["data_density_f"] = to_float(row.get("data_density"))
                row["overall_density_f"] = to_float(row.get("overall_density"))
                row["exit_code_i"] = to_int(row.get("exit_code"))
                row["success"] = normalize_text(row.get("status")) in SUCCESS_STATUSES

                if row["x_i"] is not None and row["y_i"] is not None:
                    row["grid_label"] = f"{row['x_i']}x{row['y_i']}"
                else:
                    row["grid_label"] = "unknown"
                row["placement_variant"] = classify_placement_variant(row)
                row["placement_detail"] = placement_detail_label(row)
                row["gaussian_weight_combo_label"] = gaussian_weight_combo_label(row)

                rows.append(row)

    return rows, files


def non_empty(values):
    return [v for v in values if v is not None and not math.isnan(v)]


def save_fig(fig, output_dir, filename, generated):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    generated.append(path)


def category_color_map(labels):
    cmap = plt.get_cmap("tab20", max(1, len(labels)))
    return {label: cmap(i) for i, label in enumerate(labels)}


def plot_overview_dashboard(rows, output_dir, generated):
    status_counts = Counter(r["status"] for r in rows)
    circuits = sorted({r["circuit_name"] for r in rows if r["circuit_name"]})
    circuit_counts = Counter(r["circuit_name"] for r in rows)
    success_by_circuit = {}
    for c in circuits:
        subset = [r for r in rows if r["circuit_name"] == c]
        if subset:
            success_by_circuit[c] = sum(1 for r in subset if r["success"]) / len(subset)

    duration_values = non_empty([r["duration_s_f"] for r in rows if r["success"]])
    routing_ok = non_empty([r["routing_steps_f"] for r in rows if r["success"]])

    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    axs = axs.flatten()

    labels = list(status_counts.keys())
    vals = [status_counts[k] for k in labels]
    axs[0].bar(labels, vals, color=["#3A7CA5", "#B94E48", "#D9A441"][: len(labels)])
    axs[0].set_title("Runs by Status")
    axs[0].set_ylabel("Count")

    axs[1].bar(circuits, [circuit_counts[c] for c in circuits], color="#577590")
    axs[1].set_title("Runs by Circuit")
    axs[1].tick_params(axis="x", rotation=35)

    axs[2].bar(circuits, [success_by_circuit.get(c, 0.0) * 100 for c in circuits], color="#43AA8B")
    axs[2].set_title("Success Rate by Circuit")
    axs[2].set_ylabel("%")
    axs[2].set_ylim(0, 105)
    axs[2].tick_params(axis="x", rotation=35)

    if duration_values:
        axs[3].hist(duration_values, bins=min(20, max(8, int(len(duration_values) ** 0.5))), color="#277DA1")
    axs[3].set_title("Duration Distribution (Successful Runs)")
    axs[3].set_xlabel("duration_seconds")

    if routing_ok:
        axs[4].hist(routing_ok, bins=min(20, max(8, int(len(routing_ok) ** 0.5))), color="#90BE6D")
    axs[4].set_title("Routing Steps (Successful Runs)")
    axs[4].set_xlabel("total_routing_steps")

    points = [
        (r["duration_s_f"], r["routing_steps_f"], r["status"])
        for r in rows
        if r["duration_s_f"] is not None and r["routing_steps_f"] is not None
    ]
    for status in sorted({p[2] for p in points}):
        subset = [p for p in points if p[2] == status]
        if not subset:
            continue
        axs[5].scatter(
            [p[0] for p in subset],
            [p[1] for p in subset],
            s=28,
            alpha=0.7,
            label=status_display_label(status),
            color=status_color(status),
        )
    axs[5].set_title("Duration vs Routing Steps")
    axs[5].set_xlabel("duration_seconds")
    axs[5].set_ylabel("routing_steps")
    axs[5].legend(fontsize=8)

    save_fig(fig, output_dir, "00_overview_dashboard.png", generated)


def plot_status_and_exit(rows, output_dir, generated):
    status_counts = Counter(r["status"] for r in rows)
    exit_counts = Counter(r["exit_code_i"] for r in rows if r["exit_code_i"] is not None)

    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    s_keys = list(status_counts.keys())
    s_labels = [status_display_label(k) for k in s_keys]
    s_vals = [status_counts[k] for k in s_keys]
    s_colors = [status_color(k) for k in s_keys]
    axs[0].bar(s_labels, s_vals, color=s_colors)
    axs[0].set_title("Status Counts")
    axs[0].set_ylabel("Count")
    axs[0].tick_params(axis="x", rotation=15)

    e_codes = sorted(exit_counts.keys())
    e_labels = [exit_code_display_label(code) for code in e_codes]
    e_vals = [exit_counts[code] for code in e_codes]
    e_colors = [exit_code_color(code) for code in e_codes]
    axs[1].bar(e_labels, e_vals, color=e_colors)
    axs[1].set_title("Exit Code Counts")
    axs[1].set_xlabel("exit_code")
    axs[1].tick_params(axis="x", rotation=15)

    save_fig(fig, output_dir, "01_status_and_exit_codes.png", generated)


def boxplot_by_category(rows, category_key, value_key, title, ylabel, filename, output_dir, generated, min_points=2):
    grouped = defaultdict(list)
    for r in rows:
        cat = r.get(category_key, "unknown")
        val = r.get(value_key)
        if cat is None:
            cat = "unknown"
        if val is None or (isinstance(val, float) and math.isnan(val)):
            continue
        grouped[str(cat)].append(val)

    labels = [k for k in sorted(grouped.keys()) if len(grouped[k]) >= min_points]
    if not labels:
        return

    values = [grouped[k] for k in labels]
    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 0.9), 6))
    ax.boxplot(values, tick_labels=labels, showfliers=False)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35)
    save_fig(fig, output_dir, filename, generated)


def scatter_plot(rows, x_key, y_key, color_key, title, xlabel, ylabel, filename, output_dir, generated):
    points = []
    for r in rows:
        x = r.get(x_key)
        y = r.get(y_key)
        if x is None or y is None:
            continue
        if isinstance(x, float) and math.isnan(x):
            continue
        if isinstance(y, float) and math.isnan(y):
            continue
        points.append((x, y, str(r.get(color_key, "unknown"))))

    if not points:
        return

    labels = sorted({p[2] for p in points})
    colors = category_color_map(labels)

    fig, ax = plt.subplots(figsize=(9, 6))
    for label in labels:
        subset = [p for p in points if p[2] == label]
        ax.scatter(
            [p[0] for p in subset],
            [p[1] for p in subset],
            label=label,
            alpha=0.7,
            s=28,
            color=colors[label],
        )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8)
    save_fig(fig, output_dir, filename, generated)


def plot_gaussian_weight_combinations(rows, output_dir, generated):
    gaussian_rows = []
    combo_labels = {}
    for row in rows:
        if row.get("mapping_type_norm") != "gaussian":
            continue
        combo = gaussian_weight_tuple(row)
        combo_label = row.get("gaussian_weight_combo_label")
        routing_steps = row.get("routing_steps_f")
        if combo is None or combo_label is None or routing_steps is None:
            continue
        strategy = row.get("gaussian_strategy_norm") or "unknown"
        gaussian_rows.append((combo, combo_label, routing_steps, strategy))
        combo_labels[combo_label] = combo

    if not gaussian_rows:
        return

    ordered_labels = [
        label for label, _ in sorted(combo_labels.items(), key=lambda item: item[1])
    ]
    value_groups = [
        [routing for _, label, routing, _ in gaussian_rows if label == combo_label]
        for combo_label in ordered_labels
    ]
    if not any(value_groups):
        return

    fig, ax = plt.subplots(figsize=(max(10, len(ordered_labels) * 3.4), 7))
    box = ax.boxplot(
        value_groups,
        tick_labels=ordered_labels,
        showfliers=False,
        patch_artist=True,
    )
    for patch in box["boxes"]:
        patch.set_facecolor("#D7EAF7")
        patch.set_edgecolor("#3A7CA5")
        patch.set_alpha(0.85)

    strategy_labels = sorted({strategy for _, _, _, strategy in gaussian_rows})
    colors = category_color_map(strategy_labels)
    if len(strategy_labels) == 1:
        strategy_offsets = {strategy_labels[0]: 0.0}
    else:
        offsets = np.linspace(-0.16, 0.16, len(strategy_labels))
        strategy_offsets = {label: offsets[idx] for idx, label in enumerate(strategy_labels)}

    shown_labels = set()
    for x_idx, combo_label in enumerate(ordered_labels, start=1):
        for strategy in strategy_labels:
            subset = [
                routing
                for _, label, routing, row_strategy in gaussian_rows
                if label == combo_label and row_strategy == strategy
            ]
            if not subset:
                continue
            x_values = np.full(len(subset), x_idx + strategy_offsets[strategy])
            if len(subset) > 1:
                x_values = x_values + np.linspace(-0.035, 0.035, len(subset))
            plot_label = strategy if strategy not in shown_labels else None
            shown_labels.add(strategy)
            ax.scatter(
                x_values,
                subset,
                s=28,
                alpha=0.75,
                color=colors[strategy],
                label=plot_label,
                zorder=3,
            )

    ax.set_title("Routing Steps by Gaussian Weight Combination (Gaussian Runs Only)")
    ax.set_xlabel("gaussian weight combinations")
    ax.set_ylabel("routing steps")
    ax.grid(True, axis="y", alpha=0.35)
    ax.tick_params(axis="x", labelrotation=0)
    if shown_labels:
        ax.legend(title="gaussian strategy", fontsize=8)

    save_fig(fig, output_dir, "21_box_gaussian_weight_combinations_vs_routing.png", generated)


def requested_x_key(row):
    circuit = row.get("circuit_name")
    x_i = row.get("x_i")
    y_i = row.get("y_i")
    if not circuit or x_i is None or y_i is None:
        return None
    explicit = row.get("circuit_graph_label")
    if explicit:
        label = str(explicit)
    else:
        label = f"{circuit}-{x_i}x{y_i}"
    return (str(circuit), int(x_i), int(y_i), label)


def requested_x_label(x_key):
    return x_key[3]


def aggregate_series_values(rows, build_series_key):
    grouped = defaultdict(list)
    x_keys = set()

    for row in rows:
        x_key = requested_x_key(row)
        if x_key is None:
            continue
        series_key = build_series_key(row)
        if series_key is None:
            continue
        grouped[(x_key, series_key)].append(row["routing_steps_f"])
        x_keys.add(x_key)

    if not x_keys:
        return None, None, None

    x_keys_sorted = sorted(x_keys, key=lambda item: (item[0], item[1], item[2]))
    x_labels = [requested_x_label(xk) for xk in x_keys_sorted]

    mean_by_pair = {}
    for key, values in grouped.items():
        mean_by_pair[key] = float(np.mean(values))

    return x_keys_sorted, x_labels, mean_by_pair


def requested_mapping_display_name(mapping_key):
    names = {
        "gaussian-coarse": "gaussian coarse",
        "gaussian-fine": "gaussian fine",
        "homogeneous": "homogeneous",
        "magic-aware-center": "magic-aware center",
        "magic-aware-distance": "magic-aware distance",
        "magic-aware-random": "magic-aware random",
    }
    return names.get(mapping_key, str(mapping_key))


def requested_mapping_colors(series_order):
    default_colors = {
        "gaussian-coarse": "#1d4ed8",
        "gaussian-fine": "#ea580c",
        "homogeneous": "#6b7280",
        "magic-aware-center": "#1d4ed8",
        "magic-aware-distance": "#7c3aed",
        "magic-aware-random": "#059669",
    }
    mapping_keys = []
    for mapping_key, _, _ in series_order:
        if mapping_key not in mapping_keys:
            mapping_keys.append(mapping_key)
    return {mapping_key: default_colors.get(mapping_key, "#334155") for mapping_key in mapping_keys}


def requested_placement_markers():
    return {
        "right_row": "o",
        "center_circle_0": "^",
        "center_circle_5": "s",
    }


def add_requested_group_guides(ax, x_keys_sorted):
    if not x_keys_sorted:
        return

    start = 0
    band_index = 0
    for idx in range(1, len(x_keys_sorted) + 1):
        is_group_end = idx == len(x_keys_sorted) or x_keys_sorted[idx][0] != x_keys_sorted[start][0]
        if not is_group_end:
            continue

        left = start - 0.5
        right = idx - 0.5
        if band_index % 2 == 0:
            ax.axvspan(left, right, color="#94a3b8", alpha=0.08, zorder=0)
        if idx < len(x_keys_sorted):
            ax.axvline(right, color="#94a3b8", linewidth=0.8, alpha=0.35, zorder=1)
        start = idx
        band_index += 1


def add_requested_legends(legend_ax, mapping_colors, placement_markers):
    mapping_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markersize=7,
            markerfacecolor=color,
            markeredgecolor=color,
            label=requested_mapping_display_name(mapping_key),
        )
        for mapping_key, color in mapping_colors.items()
    ]
    placement_handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            linestyle="None",
            markersize=7,
            markerfacecolor="white",
            markeredgecolor="#111827",
            color="#111827",
            label=placement_variant_label(placement_variant),
        )
        for placement_variant, marker in placement_markers.items()
    ]
    safe_passage_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markersize=7,
            markerfacecolor="#111827",
            markeredgecolor="#111827",
            color="#111827",
            label="cube (filled)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markersize=7,
            markerfacecolor="white",
            markeredgecolor="#111827",
            color="#111827",
            label="passage (hollow)",
        ),
    ]

    legend_ax.axis("off")
    legend_ax.text(
        0.02,
        0.98,
        "Encoding",
        transform=legend_ax.transAxes,
        ha="left",
        va="top",
        fontsize=11,
        fontweight="bold",
        color="#111827",
    )

    legend_mapping = legend_ax.legend(
        handles=mapping_handles,
        title="mapping",
        loc="upper left",
        bbox_to_anchor=(0.02, 0.90),
        bbox_transform=legend_ax.transAxes,
        ncols=1,
        frameon=False,
        fontsize=8,
        title_fontsize=9,
    )
    legend_ax.add_artist(legend_mapping)

    legend_placement = legend_ax.legend(
        handles=placement_handles,
        title="magic placement",
        loc="upper left",
        bbox_to_anchor=(0.02, 0.62),
        bbox_transform=legend_ax.transAxes,
        ncols=1,
        frameon=False,
        fontsize=8,
        title_fontsize=9,
    )
    legend_ax.add_artist(legend_placement)

    legend_safe = legend_ax.legend(
        handles=safe_passage_handles,
        title="safe passage",
        loc="upper left",
        bbox_to_anchor=(0.02, 0.30),
        bbox_transform=legend_ax.transAxes,
        ncols=1,
        frameon=False,
        fontsize=8,
        title_fontsize=9,
    )
    legend_ax.add_artist(legend_safe)
    return legend_mapping, legend_placement, legend_safe


def plot_requested_grouped_scatter(
    rows,
    build_series_key,
    series_order,
    title,
    filename,
    output_dir,
    generated,
):
    aggregated = aggregate_series_values(rows, build_series_key)
    if not aggregated[0]:
        return

    x_keys_sorted, x_labels, mean_by_pair = aggregated
    available_series = [
        series_key
        for series_key in series_order
        if any((x_key, series_key) in mean_by_pair for x_key in x_keys_sorted)
    ]
    if not available_series:
        return

    x_positions = np.arange(len(x_labels), dtype=float)
    mapping_colors = requested_mapping_colors(available_series)
    placement_markers = requested_placement_markers()

    fig_width = max(20, len(x_labels) * 0.85)
    fig, (legend_ax, ax) = plt.subplots(
        1,
        2,
        figsize=(fig_width, 8.8),
        gridspec_kw={"width_ratios": [3.2, max(14, len(x_labels) * 0.80)], "wspace": 0.02},
    )
    add_requested_group_guides(ax, x_keys_sorted)

    for series_key in available_series:
        mapping_key, safe_passage, placement_variant = series_key
        marker = placement_markers[placement_variant]
        color = mapping_colors[mapping_key]
        y_values = np.array(
            [mean_by_pair.get((x_key, series_key), np.nan) for x_key in x_keys_sorted],
            dtype=float,
        )
        mask = ~np.isnan(y_values)
        if not np.any(mask):
            continue

        ax.scatter(
            x_positions[mask],
            y_values[mask],
            marker=marker,
            s=44,
            linewidths=1.2,
            edgecolors=color,
            facecolors=color if safe_passage == "cube" else "white",
            alpha=0.95,
            zorder=3,
        )

    ax.set_title(title)
    ax.set_xlabel("circuit x graph dimensions")
    ax.set_ylabel("routing steps")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=60, ha="right", fontsize=8)
    ax.grid(True, axis="y", alpha=0.35)
    add_requested_legends(legend_ax, mapping_colors, placement_markers)
    fig.subplots_adjust(top=0.92, bottom=0.28, left=0.03, right=0.995)
    save_fig(fig, output_dir, filename, generated)


def build_series_key_requested_gaussian_vs_homogeneous(row):
    if row.get("routing_steps_f") is None:
        return None
    if row.get("safe_passage_norm") not in REQUESTED_SAFE_PASSAGES:
        return None
    placement_variant = row.get("placement_variant")
    if placement_variant not in REQUESTED_PLACEMENT_VARIANTS:
        return None

    mapping = row.get("mapping_type_norm")
    safe_passage = row.get("safe_passage_norm")

    if mapping == "gaussian":
        gaussian_strategy = row.get("gaussian_strategy_norm")
        if gaussian_strategy not in REQUESTED_GAUSSIAN_STRATEGIES:
            return None
        return (f"gaussian-{gaussian_strategy}", safe_passage, placement_variant)

    if mapping == "homogeneous":
        return ("homogeneous", safe_passage, placement_variant)

    return None


def build_series_key_requested_magicaware_vs_homogeneous(row):
    if row.get("routing_steps_f") is None:
        return None
    if row.get("safe_passage_norm") not in REQUESTED_SAFE_PASSAGES:
        return None
    placement_variant = row.get("placement_variant")
    if placement_variant not in REQUESTED_PLACEMENT_VARIANTS:
        return None

    mapping = row.get("mapping_type_norm")
    safe_passage = row.get("safe_passage_norm")

    if mapping == "homogeneous":
        return ("homogeneous", safe_passage, placement_variant)

    if mapping == "magic_aware":
        strategy = row.get("magic_aware_strategy_norm")
        if strategy not in REQUESTED_MAGIC_AWARE_STRATEGIES:
            return None
        return (f"magic-aware-{strategy}", safe_passage, placement_variant)

    return None


def build_series_key_requested_all_mappings(row):
    if row.get("routing_steps_f") is None:
        return None
    if row.get("safe_passage_norm") not in REQUESTED_SAFE_PASSAGES:
        return None
    placement_variant = row.get("placement_variant")
    if placement_variant not in REQUESTED_PLACEMENT_VARIANTS:
        return None

    mapping = row.get("mapping_type_norm")
    safe_passage = row.get("safe_passage_norm")

    if mapping == "homogeneous":
        return ("homogeneous", safe_passage, placement_variant)

    if mapping == "gaussian":
        gaussian_strategy = row.get("gaussian_strategy_norm")
        if gaussian_strategy not in REQUESTED_GAUSSIAN_STRATEGIES:
            return None
        return (f"gaussian-{gaussian_strategy}", safe_passage, placement_variant)

    if mapping == "magic_aware":
        strategy = row.get("magic_aware_strategy_norm")
        if strategy not in REQUESTED_MAGIC_AWARE_STRATEGIES:
            return None
        return (f"magic-aware-{strategy}", safe_passage, placement_variant)

    return None


def requested_series_order_gaussian_vs_homogeneous():
    ordered = []
    for placement_variant in REQUESTED_PLACEMENT_VARIANTS:
        for safe_passage in sorted(REQUESTED_SAFE_PASSAGES):
            ordered.append(("gaussian-coarse", safe_passage, placement_variant))
            ordered.append(("gaussian-fine", safe_passage, placement_variant))
            ordered.append(("homogeneous", safe_passage, placement_variant))
    return ordered


def requested_series_order_magicaware_vs_homogeneous():
    ordered = []
    for placement_variant in REQUESTED_PLACEMENT_VARIANTS:
        for safe_passage in sorted(REQUESTED_SAFE_PASSAGES):
            ordered.append(("homogeneous", safe_passage, placement_variant))
            ordered.append(("magic-aware-center", safe_passage, placement_variant))
            ordered.append(("magic-aware-distance", safe_passage, placement_variant))
            ordered.append(("magic-aware-random", safe_passage, placement_variant))
    return ordered


def requested_series_order_all_mappings():
    ordered = []
    for placement_variant in REQUESTED_PLACEMENT_VARIANTS:
        for safe_passage in sorted(REQUESTED_SAFE_PASSAGES):
            ordered.append(("homogeneous", safe_passage, placement_variant))
            ordered.append(("gaussian-coarse", safe_passage, placement_variant))
            ordered.append(("gaussian-fine", safe_passage, placement_variant))
            ordered.append(("magic-aware-center", safe_passage, placement_variant))
            ordered.append(("magic-aware-distance", safe_passage, placement_variant))
            ordered.append(("magic-aware-random", safe_passage, placement_variant))
    return ordered


def plot_requested_comparisons(rows_success_with_routing, output_dir, generated):
    plot_requested_grouped_scatter(
        rows_success_with_routing,
        build_series_key_requested_gaussian_vs_homogeneous,
        requested_series_order_gaussian_vs_homogeneous(),
        "Routing Steps by circuit-graph_dimensions: gaussian coarse/fine + homogeneous",
        "17_experiment_set_routing_gaussian_homogeneous.png",
        output_dir,
        generated,
    )
    plot_requested_grouped_scatter(
        rows_success_with_routing,
        build_series_key_requested_magicaware_vs_homogeneous,
        requested_series_order_magicaware_vs_homogeneous(),
        "Routing Steps by circuit-graph_dimensions: magic-aware center/distance/random + homogeneous",
        "18_experiment_set_routing_magicaware_homogeneous.png",
        output_dir,
        generated,
    )
    plot_requested_grouped_scatter(
        rows_success_with_routing,
        build_series_key_requested_all_mappings,
        requested_series_order_all_mappings(),
        "Routing Steps by circuit-graph_dimensions: homogeneous + gaussian + magic-aware",
        "22_experiment_set_routing_all_mappings.png",
        output_dir,
        generated,
    )


def make_pair_heatmap(
    rows,
    row_key,
    col_key,
    value_fn,
    title,
    colorbar_label,
    filename,
    output_dir,
    generated,
    value_format="{:.2f}",
):
    row_labels = sorted({str(r.get(row_key, "unknown")) for r in rows})
    col_labels = sorted({str(r.get(col_key, "unknown")) for r in rows})
    if not row_labels or not col_labels:
        return

    matrix = np.full((len(row_labels), len(col_labels)), np.nan, dtype=float)
    row_index = {k: i for i, k in enumerate(row_labels)}
    col_index = {k: j for j, k in enumerate(col_labels)}

    grouped = defaultdict(list)
    for r in rows:
        grouped[(str(r.get(row_key, "unknown")), str(r.get(col_key, "unknown")))].append(r)

    for (rk, ck), subset in grouped.items():
        val = value_fn(subset)
        if val is None:
            continue
        matrix[row_index[rk], col_index[ck]] = val

    fig, ax = plt.subplots(figsize=(max(7, len(col_labels) * 1.0), max(5, len(row_labels) * 0.8)))
    masked = np.ma.masked_invalid(matrix)
    im = ax.imshow(masked, cmap="viridis", aspect="auto")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(colorbar_label)

    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=30, ha="right")
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.set_title(title)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            text = "-" if np.isnan(val) else value_format.format(val)
            ax.text(j, i, text, ha="center", va="center", color="white" if not np.isnan(val) else "#999999", fontsize=8)

    save_fig(fig, output_dir, filename, generated)


def mean_of(values):
    values = non_empty(values)
    if not values:
        return None
    return float(np.mean(values))


def success_rate(subset):
    if not subset:
        return None
    return 100.0 * (sum(1 for r in subset if r["success"]) / len(subset))


def plot_summary_tables(rows, output_dir, generated):
    circuits = sorted({r["circuit_name"] for r in rows})
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))

    success_rates = []
    elapsed_median = []
    for c in circuits:
        subset = [r for r in rows if r["circuit_name"] == c]
        success_rates.append(success_rate(subset) or 0.0)
        duration_vals = non_empty([r["duration_s_f"] for r in subset])
        elapsed_median.append(float(np.median(duration_vals)) if duration_vals else 0.0)

    axs[0].barh(circuits, success_rates, color="#2A9D8F")
    axs[0].set_title("Success Rate by Circuit")
    axs[0].set_xlabel("%")
    axs[0].set_xlim(0, 100)

    axs[1].barh(circuits, elapsed_median, color="#577590")
    axs[1].set_title("Median Duration by Circuit")
    axs[1].set_xlabel("duration_seconds")

    save_fig(fig, output_dir, "02_circuit_summary_bars.png", generated)


def routing_combo_label(row):
    mapping = row.get("mapping_type_norm", "") or "unknown"
    if mapping == "gaussian":
        strategy = row.get("gaussian_strategy_norm", "") or "unknown"
        return f"gaussian:{strategy}"
    if mapping == "magic_aware":
        strategy = row.get("magic_aware_strategy_norm", "") or "unknown"
        return f"magic_aware:{strategy}"
    return mapping


def best_mapping_strategy_label(row):
    mapping = row.get("mapping_type_norm", "") or "unknown"
    if mapping == "gaussian":
        strategy = row.get("gaussian_strategy_norm", "") or "unknown"
        return f"gaussian ({strategy})"
    if mapping == "magic_aware":
        strategy = row.get("magic_aware_strategy_norm", "") or "unknown"
        return f"magic-aware ({strategy})"
    return mapping


def best_mapping_sort_key(row):
    return (
        row["routing_steps_f"],
        best_mapping_strategy_label(row),
        row.get("safe_passage_norm", ""),
        row.get("placement_detail", ""),
    )


def build_best_mapping_entries(inclusion_rows_by_group, candidate_rows_by_group):
    required_families = {"gaussian", "homogeneous", "magic_aware"}
    entries = []

    for x_key in sorted(inclusion_rows_by_group.keys(), key=lambda item: (item[0], item[1], item[2])):
        executed_rows = inclusion_rows_by_group[x_key]
        executed_families = {
            row.get("mapping_type_norm")
            for row in executed_rows
            if row.get("mapping_type_norm") in required_families
        }
        if not required_families.issubset(executed_families):
            continue

        successful_rows = candidate_rows_by_group.get(x_key, [])
        if not successful_rows:
            continue

        sorted_rows = sorted(successful_rows, key=best_mapping_sort_key)
        best_routing_steps = sorted_rows[0]["routing_steps_f"]
        seen_best_entries = set()

        for best_row in sorted_rows:
            if best_row["routing_steps_f"] != best_routing_steps:
                break
            entry_key = (
                best_mapping_strategy_label(best_row),
                best_row.get("safe_passage_norm", "") or "n/a",
                best_row.get("placement_detail", "") or "n/a",
            )
            if entry_key in seen_best_entries:
                continue
            seen_best_entries.add(entry_key)
            entries.append(
                {
                    "circuit_graph_label": requested_x_label(x_key),
                    "circuit": x_key[0],
                    "graph_x": x_key[1],
                    "graph_y": x_key[2],
                    "best_mapping": best_mapping_strategy_label(best_row),
                    "safe_passage": best_row.get("safe_passage_norm", "") or "n/a",
                    "magic_placement": best_row.get("placement_detail", "") or "n/a",
                    "routing_steps": best_row["routing_steps_f"],
                }
            )

    return entries


def best_mapping_table_entries(rows):
    executed_by_group = defaultdict(list)
    success_with_routing_by_group = defaultdict(list)

    for row in rows:
        x_key = requested_x_key(row)
        if x_key is None:
            continue
        executed_by_group[x_key].append(row)
        if row.get("success") and row.get("routing_steps_f") is not None:
            success_with_routing_by_group[x_key].append(row)

    return build_best_mapping_entries(executed_by_group, success_with_routing_by_group)


def best_mapping_table_entries_exit0_only(rows):
    exit0_by_group = defaultdict(list)
    exit0_with_routing_by_group = defaultdict(list)

    for row in rows:
        x_key = requested_x_key(row)
        if x_key is None:
            continue
        if row.get("exit_code_i") != 0:
            continue
        exit0_by_group[x_key].append(row)
        if row.get("routing_steps_f") is not None:
            exit0_with_routing_by_group[x_key].append(row)

    return build_best_mapping_entries(exit0_by_group, exit0_with_routing_by_group)


def write_best_mapping_table(entries, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, filename)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "circuit_graph_label",
                "circuit",
                "graph_x",
                "graph_y",
                "best_mapping",
                "safe_passage",
                "magic_placement",
                "routing_steps",
            ],
        )
        writer.writeheader()
        writer.writerows(entries)

    return entries, csv_path


def write_summary(rows, csv_files, output_dir, generated):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "summary.txt")

    status_counts = Counter(r["status"] for r in rows)
    success_count = sum(1 for r in rows if r["success"])
    success_pct = 100.0 * success_count / len(rows) if rows else 0.0
    duration_values = non_empty([r["duration_s_f"] for r in rows])
    routing_values_ok = non_empty([r["routing_steps_f"] for r in rows if r["success"]])

    combo_scores = defaultdict(list)
    for r in rows:
        if r["success"] and r["routing_steps_f"] is not None:
            key = (
                routing_combo_label(r),
                r.get("safe_passage_strategy", "unknown"),
                r.get("placement", "unknown"),
            )
            combo_scores[key].append(r["routing_steps_f"])

    best_combo_line = "n/a"
    if combo_scores:
        best_combo = min(combo_scores.items(), key=lambda kv: statistics.mean(kv[1]))
        best_combo_line = (
            f"{best_combo[0][0]} | {best_combo[0][1]} | {best_combo[0][2]} "
            f"(mean routing steps = {statistics.mean(best_combo[1]):.2f}, n={len(best_combo[1])})"
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write("Benchmark Plot Summary\n")
        f.write("======================\n\n")
        f.write(f"Generated at: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"CSV files scanned: {len(csv_files)}\n")
        f.write(f"Rows analyzed: {len(rows)}\n")
        f.write(f"Unique circuits: {len(set(r['circuit_name'] for r in rows))}\n\n")

        f.write("Status counts:\n")
        for k, v in status_counts.items():
            f.write(f"  - {status_display_label(k)}: {v}\n")
        f.write(f"Overall success rate: {success_pct:.2f}%\n\n")

        if duration_values:
            f.write(
                f"Duration s: min={min(duration_values):.2f}, "
                f"median={statistics.median(duration_values):.2f}, "
                f"max={max(duration_values):.2f}\n"
            )
        if routing_values_ok:
            f.write(
                f"Routing steps (successful): min={min(routing_values_ok):.2f}, "
                f"median={statistics.median(routing_values_ok):.2f}, "
                f"max={max(routing_values_ok):.2f}\n"
            )
        f.write(f"Best routing combo: {best_combo_line}\n\n")

        f.write("Generated plots:\n")
        for p in generated:
            f.write(f"  - {p}\n")


def write_report_markdown(
    output_dir,
    generated,
    best_mapping_entries,
    best_mapping_csv_path,
    best_mapping_exit0_entries,
    best_mapping_exit0_csv_path,
):
    report_path = os.path.join(output_dir, "report.md")
    by_name = {os.path.basename(p): p for p in generated}

    ordered = [
        ("00_overview_dashboard.png", "Overview dashboard"),
        ("01_status_and_exit_codes.png", "Run status and exit codes"),
        ("02_circuit_summary_bars.png", "Circuit-level summary"),
        ("03_box_routing_by_circuit.png", "Routing steps by circuit"),
        ("04_box_elapsed_by_circuit.png", "Duration by circuit"),
        ("05_box_routing_by_placement.png", "Routing by magic placement"),
        ("06_box_routing_by_safe_passage.png", "Routing by safe passage"),
        ("07_box_routing_by_magic_strategy.png", "Routing by magic-aware strategy"),
        ("08_scatter_elapsed_vs_routing_by_circuit.png", "Duration vs routing"),
        ("09_scatter_density_vs_routing.png", "Density vs routing"),
        ("10_scatter_magic_states_vs_routing.png", "Magic state parameter vs routing"),
        ("11_scatter_border_vs_routing_center_circle.png", "Border distance vs routing"),
        ("12_scatter_pressure_vs_elapsed.png", "Interaction pressure vs duration"),
        ("13_heatmap_success_safe_vs_placement.png", "Success heatmap: safe passage x placement"),
        ("14_heatmap_routing_safe_vs_placement.png", "Routing heatmap: safe passage x placement"),
        ("15_heatmap_routing_magic_vs_safe.png", "Routing heatmap: magic strategy x safe passage"),
        ("16_heatmap_success_by_grid_xy.png", "Success heatmap by grid size"),
        ("17_experiment_set_routing_gaussian_homogeneous.png", "Experiment set: gaussian + homogeneous"),
        ("18_experiment_set_routing_magicaware_homogeneous.png", "Experiment set: magic-aware + homogeneous"),
        ("19_box_routing_by_gaussian_strategy.png", "Routing by gaussian strategy"),
        ("20_heatmap_routing_gaussian_strategy_vs_placement.png", "Routing heatmap: gaussian strategy x placement"),
        ("21_box_gaussian_weight_combinations_vs_routing.png", "Routing by gaussian weight combinations"),
        ("22_experiment_set_routing_all_mappings.png", "Experiment set: all mappings"),
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Benchmark Charts\n\n")
        f.write("Generated plot set from benchmark CSV files.\n\n")
        f.write("See also `summary.txt` for aggregate metrics.\n\n")
        for filename, caption in ordered:
            if filename not in by_name:
                continue
            f.write(f"## {caption}\n\n")
            f.write(f"![{caption}]({filename})\n\n")

        if best_mapping_entries:
            csv_name = os.path.basename(best_mapping_csv_path)
            f.write("## Best Mapping Table\n\n")
            f.write(
                "Only circuit x graph-dimensions where `gaussian`, `homogeneous`, and "
                "`magic-aware` all appear in the runs. All configurations tied for the "
                "lowest routing steps are listed among successful runs with routing steps "
                "available.\n\n"
            )
            f.write(f"CSV export: `{csv_name}`\n\n")
            f.write("| circuit x dimensions | best mapping | safe passage | magic placement | routing steps |\n")
            f.write("| --- | --- | --- | --- | ---: |\n")
            for entry in best_mapping_entries:
                f.write(
                    f"| {entry['circuit_graph_label']} | {entry['best_mapping']} | "
                    f"{entry['safe_passage']} | {entry['magic_placement']} | "
                    f"{entry['routing_steps']:.0f} |\n"
                )
            f.write("\n")

        if best_mapping_exit0_entries:
            csv_name = os.path.basename(best_mapping_exit0_csv_path)
            f.write("## Best Mapping Table (All Families Exit Code 0)\n\n")
            f.write(
                "Only circuit x graph-dimensions where `gaussian`, `homogeneous`, and "
                "`magic-aware` all appear among runs with `exit_code = 0`. All configurations "
                "tied for the lowest routing steps are listed only from those "
                "`exit_code = 0` runs.\n\n"
            )
            f.write(f"CSV export: `{csv_name}`\n\n")
            f.write("| circuit x dimensions | best mapping | safe passage | magic placement | routing steps |\n")
            f.write("| --- | --- | --- | --- | ---: |\n")
            for entry in best_mapping_exit0_entries:
                f.write(
                    f"| {entry['circuit_graph_label']} | {entry['best_mapping']} | "
                    f"{entry['safe_passage']} | {entry['magic_placement']} | "
                    f"{entry['routing_steps']:.0f} |\n"
                )
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Generate benchmark plots from CSV results.")
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--csv",
        help="Single CSV input file. If set and --output-dir is omitted, plots are written to <csv_dir>/<csv_name>_plots/",
    )
    input_group.add_argument(
        "--csv-glob",
        default="benchmarks/results/**/*.csv",
        help="Glob for CSV inputs (default: benchmarks/results/**/*.csv)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for generated plots",
    )
    args = parser.parse_args()

    importMatplotlib()

    plt.style.use("seaborn-v0_8-whitegrid")

    if args.csv:
        csv_path = os.path.abspath(args.csv)
        rows, csv_files = load_rows_from_files([csv_path])
        output_dir = args.output_dir or os.path.join(
            os.path.dirname(csv_path),
            os.path.splitext(os.path.basename(csv_path))[0] + "_plots",
        )
    else:
        rows, csv_files = load_rows(args.csv_glob)
        output_dir = args.output_dir or "benchmarks/results/plots"

    if not rows:
        if args.csv:
            raise RuntimeError(f"No valid rows found in CSV: {args.csv}")
        raise RuntimeError(f"No valid rows found for glob: {args.csv_glob}")

    generated = []

    plot_overview_dashboard(rows, output_dir, generated)
    plot_status_and_exit(rows, output_dir, generated)
    plot_summary_tables(rows, output_dir, generated)

    rows_success_with_routing = [r for r in rows if r["success"] and r["routing_steps_f"] is not None]
    rows_gaussian_with_routing = [
        r for r in rows_success_with_routing if r["mapping_type_norm"] == "gaussian"
    ]
    rows_magicaware_with_routing = [
        r
        for r in rows_success_with_routing
        if r["mapping_type_norm"] == "magic_aware"
        and r["magic_aware_strategy_norm"] in REQUESTED_MAGIC_AWARE_STRATEGIES
    ]

    boxplot_by_category(
        rows_success_with_routing,
        "circuit_name",
        "routing_steps_f",
        "Routing Steps by Circuit (Success Only)",
        "routing steps",
        "03_box_routing_by_circuit.png",
        output_dir,
        generated,
    )
    boxplot_by_category(
        rows,
        "circuit_name",
        "duration_s_f",
        "Duration by Circuit",
        "duration_seconds",
        "04_box_elapsed_by_circuit.png",
        output_dir,
        generated,
    )
    boxplot_by_category(
        rows_success_with_routing,
        "placement",
        "routing_steps_f",
        "Routing Steps by Magic Placement",
        "routing steps",
        "05_box_routing_by_placement.png",
        output_dir,
        generated,
    )
    boxplot_by_category(
        rows_success_with_routing,
        "safe_passage_strategy",
        "routing_steps_f",
        "Routing Steps by Safe Passage Strategy",
        "routing steps",
        "06_box_routing_by_safe_passage.png",
        output_dir,
        generated,
    )
    boxplot_by_category(
        rows_magicaware_with_routing,
        "magic_aware_strategy",
        "routing_steps_f",
        "Routing Steps by Magic-Aware Strategy (Magic-Aware Runs Only)",
        "routing steps",
        "07_box_routing_by_magic_strategy.png",
        output_dir,
        generated,
    )
    boxplot_by_category(
        rows_gaussian_with_routing,
        "gaussian_strategy_norm",
        "routing_steps_f",
        "Routing Steps by Gaussian Strategy (Gaussian Runs Only)",
        "routing steps",
        "19_box_routing_by_gaussian_strategy.png",
        output_dir,
        generated,
    )

    scatter_plot(
        rows_success_with_routing,
        "duration_s_f",
        "routing_steps_f",
        "circuit_name",
        "Duration vs Routing Steps (by Circuit)",
        "duration_seconds",
        "routing steps",
        "08_scatter_elapsed_vs_routing_by_circuit.png",
        output_dir,
        generated,
    )
    scatter_plot(
        rows_success_with_routing,
        "data_density_f",
        "routing_steps_f",
        "placement",
        "Data Density vs Routing Steps (by Placement)",
        "data_density",
        "routing steps",
        "09_scatter_density_vs_routing.png",
        output_dir,
        generated,
    )
    scatter_plot(
        rows_success_with_routing,
        "magic_states_f",
        "routing_steps_f",
        "circuit_name",
        "Magic State Parameter vs Routing Steps",
        "number_of_magic_states",
        "routing steps",
        "10_scatter_magic_states_vs_routing.png",
        output_dir,
        generated,
    )

    center_circle_ok = [
        r for r in rows_success_with_routing
        if str(r.get("placement", "")) == "center_circle" and r.get("border_pct_f") is not None
    ]
    scatter_plot(
        center_circle_ok,
        "border_pct_f",
        "routing_steps_f",
        "safe_passage_strategy",
        "Border Distance vs Routing (Center Circle Only)",
        "border_distance_percentage",
        "routing steps",
        "11_scatter_border_vs_routing_center_circle.png",
        output_dir,
        generated,
    )

    scatter_plot(
        rows,
        "interaction_pressure_f",
        "duration_s_f",
        "status",
        "Interaction Pressure vs Duration",
        "interaction_pressure",
        "duration_seconds",
        "12_scatter_pressure_vs_elapsed.png",
        output_dir,
        generated,
    )

    make_pair_heatmap(
        rows,
        "safe_passage_strategy",
        "placement",
        success_rate,
        "Success Rate Heatmap",
        "success rate (%)",
        "13_heatmap_success_safe_vs_placement.png",
        output_dir,
        generated,
        value_format="{:.1f}",
    )
    make_pair_heatmap(
        rows_success_with_routing,
        "safe_passage_strategy",
        "placement",
        lambda subset: mean_of([r["routing_steps_f"] for r in subset]),
        "Mean Routing Steps Heatmap",
        "mean routing steps",
        "14_heatmap_routing_safe_vs_placement.png",
        output_dir,
        generated,
    )
    make_pair_heatmap(
        rows_magicaware_with_routing,
        "magic_aware_strategy",
        "safe_passage_strategy",
        lambda subset: mean_of([r["routing_steps_f"] for r in subset]),
        "Mean Routing by Magic-Aware Strategy and Safe Passage",
        "mean routing steps",
        "15_heatmap_routing_magic_vs_safe.png",
        output_dir,
        generated,
    )
    make_pair_heatmap(
        rows_gaussian_with_routing,
        "gaussian_strategy_norm",
        "placement_detail",
        lambda subset: mean_of([r["routing_steps_f"] for r in subset]),
        "Mean Routing by Gaussian Strategy and Placement",
        "mean routing steps",
        "20_heatmap_routing_gaussian_strategy_vs_placement.png",
        output_dir,
        generated,
    )
    make_pair_heatmap(
        rows,
        "y_i",
        "x_i",
        success_rate,
        "Success Rate by Grid Size (y rows vs x cols)",
        "success rate (%)",
        "16_heatmap_success_by_grid_xy.png",
        output_dir,
        generated,
        value_format="{:.0f}",
    )
    plot_requested_comparisons(rows_success_with_routing, output_dir, generated)
    plot_gaussian_weight_combinations(rows_gaussian_with_routing, output_dir, generated)

    best_mapping_entries = best_mapping_table_entries(rows)
    best_mapping_entries, best_mapping_csv_path = write_best_mapping_table(
        best_mapping_entries,
        output_dir,
        "best_mapping_by_circuit_dimension.csv",
    )
    best_mapping_exit0_entries = best_mapping_table_entries_exit0_only(rows)
    best_mapping_exit0_entries, best_mapping_exit0_csv_path = write_best_mapping_table(
        best_mapping_exit0_entries,
        output_dir,
        "best_mapping_by_circuit_dimension_all_families_exit0.csv",
    )
    write_summary(rows, csv_files, output_dir, generated)
    write_report_markdown(
        output_dir,
        generated,
        best_mapping_entries,
        best_mapping_csv_path,
        best_mapping_exit0_entries,
        best_mapping_exit0_csv_path,
    )
    print(f"Generated {len(generated)} plots in: {output_dir}")
    for path in generated:
        print(path)
    print(best_mapping_csv_path)
    print(best_mapping_exit0_csv_path)
    print(os.path.join(output_dir, "summary.txt"))


if __name__ == "__main__":
    main()
