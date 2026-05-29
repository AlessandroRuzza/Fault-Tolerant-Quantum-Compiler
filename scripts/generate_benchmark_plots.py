#!/usr/bin/env python3

import argparse
import ctypes
import csv
import gc
import glob
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import warnings
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation


WRITE_REPORT_MD = False
HEATMAP_BATCH_SIZE = 50
DASHBOARD_OUTPUT_DPI = 150
DASHBOARD_SOURCE_PLOT_DPI = 300
AXIS_BARPLOT_OUTPUT_DPI = 300


try:
    _libc = ctypes.CDLL("libc.so.6")
    def _trim_heap():
        gc.collect()
        _libc.malloc_trim(0)
except OSError:
    def _trim_heap():
        gc.collect()

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

def importMatplotlib():
    global plt, np, Line2D, TwoSlopeNorm
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib.lines import Line2D


SUCCESS_STATUSES = {"ok", "ok_no_routing_metric", "success"}
TIMEOUT_STATUSES = {"timeout"}
REQUESTED_SAFE_PASSAGES = {"passage", "cube"}
REQUESTED_PLACEMENT_VARIANTS = ("right_row", "center_circle_0", "center_circle_5")
REQUESTED_GAUSSIAN_STRATEGIES = {"coarse", "fine"}
REQUESTED_MAGIC_AWARE_STRATEGIES = {"center", "distance", "random"}
RUNTIME_CURVE_MAPPING_TYPES = ("gaussian", "magic_aware", "homogeneous")
RUNTIME_CURVE_SAFE_PASSAGES = ("cube", "connectivity")
RUNTIME_CURVE_STATUSES = SUCCESS_STATUSES | TIMEOUT_STATUSES
RUNTIME_GROUPED_X_SPECS = (
    ("qubits", "#qubits", "qubits"),
    ("gates", "#gates", "gates"),
    ("graph_nodes", "graph size (#nodes = graph_x * graph_y)", "graph_nodes"),
)
RUNTIME_GROUPED_FACTOR_SPECS = (
    ("gaussian_confidence_f", "gaussian_confidence", "gaussian confidence", "gaussian_confidence"),
    ("safe_passage_norm", "safe_passage_strategy", "safe passage strategy", "safe_passage_strategy"),
)
HEATMAP_AXIS_SPECS = {
    "type": ("mapping_type_norm", "type"),
    "safe_passage": ("safe_passage_norm", "safe passage"),
    "placement_border": ("placement_detail", "magic placement x border distance"),
    "n_magic_states": ("magic_states_label", "n magic states"),
    "gaussian_strategy": ("gaussian_strategy_norm", "gaussian strategy"),
    "mapping_strategy": ("magic_aware_strategy_norm", "mapping strategy"),
    "routing_strategy": ("routing_strategy_norm", "routing strategy"),
    "t_routing_mode": ("t_routing_mode_norm", "t routing mode"),
    "gaussian_confidence": ("gaussian_confidence_label", "gaussian confidence"),
    "use_layer_cache": ("use_layer_cache_norm", "use layer cache"),
}

HEATMAP_METRIC_SPECS = (
    ("success_rate", "success", "Success heatmap", "all runs", "success rate (%)", "{:.1f}"),
    ("routing_steps", "routing_steps", "Routing heatmap", "success only", "mean routing steps", "{:.2f}"),
    ("execution_time", "execution_time", "Execution-time heatmap", "success only", "mean duration (s)", "{:.2f}"),
    ("non_routed_layer_pct", "non_routed_layer_pct", "Non-routed layer % heatmap", "success only", "mean non-routed layer pct (%)", "{:.2f}"),
)
AXIS_BARPLOT_METRIC_SPECS = (
    ("success_rate", "success", "Success Rate by", "all runs", "success rate (%)", "{:.1f}", "#2A9D8F"),
    ("routing_steps", "routing_steps", "Routing Steps by", "success only", "routing steps", "{:.2f}", "#577590"),
    ("execution_time", "execution_time", "Execution Time by", "success only", "duration (s)", "{:.2f}", "#E76F51"),
    ("non_routed_layer_pct", "non_routed_layer_pct", "Non-routed Layer % by", "success only", "non-routed layer pct (%)", "{:.2f}", "#E9C46A"),
)
PER_CIRCUIT_BARPLOT_DIR = "barplots_by_circuit"
HEATMAP_DIR = "heatmap"
TIME_ANALYSIS_DIR = "time_analysis"
# Gates the time_analysis/ subfolder: when False, save_fig drops any plot that
# would land there. Flipped on by --time in main().
INCLUDE_TIME_ANALYSIS = False
GAUSSIAN_RELATIVE_GAP_PLOT = "heatmap_best_gaussian_relative_weight_gaps.png"
GAUSSIAN_DIR = "gaussian_relative_weight_gaps"
# Config dimensions the --gaussian breakdown slices the relative-weight-gap
# heatmap over. (row field on the prepared rows, human label, folder/file slug).
GAUSSIAN_GAP_BREAKDOWN_DIMENSIONS = (
    ("gaussian_strategy_norm", "gaussian strategy", "gaussian_strategy"),
    ("safe_passage_norm", "safe passage", "safe_passage"),
    ("magic_states_label", "n magic states", "n_magic_states"),
    ("gaussian_confidence_label", "gaussian confidence", "gaussian_confidence"),
    ("placement", "magic state placement", "placement"),
)
HEATMAP_PAIR_GROUPS = (
    ("type", ("safe_passage", "placement_border", "n_magic_states")),
    ("gaussian_strategy", ("safe_passage", "placement_border", "n_magic_states")),
    ("mapping_strategy", ("safe_passage", "placement_border", "n_magic_states")),
    ("safe_passage", ("placement_border", "n_magic_states", "type", "gaussian_strategy", "mapping_strategy")),
    ("placement_border", ("safe_passage", "n_magic_states", "type", "gaussian_strategy", "mapping_strategy")),
    ("routing_strategy", ("safe_passage", "placement_border", "n_magic_states", "type", "gaussian_strategy", "mapping_strategy")),
    ("t_routing_mode", ("safe_passage", "placement_border", "n_magic_states", "type", "gaussian_strategy", "mapping_strategy")),
    ("gaussian_confidence", ("safe_passage", "placement_border", "n_magic_states", "type", "gaussian_strategy", "mapping_strategy", "routing_strategy", "t_routing_mode")),
    ("use_layer_cache", ("safe_passage", "placement_border", "n_magic_states", "type", "gaussian_strategy", "mapping_strategy", "routing_strategy", "t_routing_mode")),
)
HEATMAP_X_AXIS_SLUGS = tuple(axis_slug for axis_slug, _ in HEATMAP_PAIR_GROUPS)
HEATMAP_AXIS_FLAG_SPECS = (
    (("--type",), "plot_axis_type", "type", "type"),
    (("--safe-passage",), "plot_axis_safe_passage", "safe_passage", "safe passage"),
    (("--placement-border",), "plot_axis_placement_border", "placement_border", "magic placement x border distance"),
    (("--magic-states",), "plot_axis_magic_states", "n_magic_states", "n magic states"),
    (("--gaussian-strategy",), "plot_axis_gaussian_strategy", "gaussian_strategy", "gaussian strategy"),
    (("--mapping-strategy",), "plot_axis_mapping_strategy", "mapping_strategy", "mapping strategy"),
    (("--routing-strategy",), "plot_axis_routing_strategy", "routing_strategy", "routing strategy"),
    (("--t-routing-mode",), "plot_axis_t_routing_mode", "t_routing_mode", "t routing mode"),
    (("--confidence", "--gaussian-confidence"), "plot_axis_gaussian_confidence", "gaussian_confidence", "gaussian confidence"),
    (("--cache", "--use-layer-cache"), "plot_axis_use_layer_cache", "use_layer_cache", "use layer cache"),
)
DEFAULT_RESULTS_DIR = os.path.join("benchmarks", "results")
OBSOLETE_PLOT_FILENAMES = {
    "13_heatmap_success_safe_vs_placement.png",
    "23_heatmap_success_safe_vs_mapping_type.png",
    "08_scatter_elapsed_vs_routing_by_circuit.png",
    "10_scatter_magic_states_vs_routing.png",
    "11_scatter_border_vs_routing_center_circle.png",
    "16_heatmap_success_by_grid_xy.png",
    "48_heatmap_routing_strategy_vs_safe_passage.png",
    "49_heatmap_routing_strategy_vs_mapping_type.png",
    "50_heatmap_routing_strategy_vs_gaussian_strategy.png",
    "51_heatmap_t_routing_mode_vs_safe_passage.png",
    "52_heatmap_t_routing_mode_vs_mapping_type.png",
    "53_heatmap_t_routing_mode_vs_gaussian_strategy.png",
    "54_heatmap_success_routing_strategy_vs_safe_passage_excluding_timeouts.png",
    "55_heatmap_success_routing_strategy_vs_mapping_type_excluding_timeouts.png",
    "56_heatmap_success_routing_strategy_vs_gaussian_strategy_excluding_timeouts.png",
    "57_heatmap_success_t_routing_mode_vs_safe_passage_excluding_timeouts.png",
    "58_heatmap_success_t_routing_mode_vs_mapping_type_excluding_timeouts.png",
    "59_heatmap_success_t_routing_mode_vs_gaussian_strategy_excluding_timeouts.png",
    "60_heatmap_duration_routing_strategy_vs_safe_passage.png",
    "61_heatmap_duration_routing_strategy_vs_mapping_type.png",
    "62_heatmap_duration_routing_strategy_vs_gaussian_strategy.png",
    "63_heatmap_duration_t_routing_mode_vs_safe_passage.png",
    "64_heatmap_duration_t_routing_mode_vs_mapping_type.png",
    "65_heatmap_duration_t_routing_mode_vs_gaussian_strategy.png",
    "28_table_top_gaussian_weight_configs.png",
    "31_heatmap_best_gaussian_weight_value_counts.png",
    "32_runtime_vs_qubits_plus_gates_with_timeouts.png",
    "33_runtime_vs_qubits_with_timeouts.png",
    "34_runtime_vs_gates_with_timeouts.png",
    "35_runtime_vs_graph_nodes_with_timeouts.png",
    "best_gaussian_weight_value_counts.csv",
    "top_gaussian_weight_configs_readable.html",
}
OBSOLETE_PLOT_PREFIXES = (
    "29_table_top_gaussian_weight_configs_",
    "best_config_count_by_",
    "timeout_count_by_",
)


def heatmap_slug(axis_slug):
    return axis_slug


def build_requested_heatmap_items(start_index=48):
    items = []
    for col_axis, row_axes in HEATMAP_PAIR_GROUPS:
        col_key, col_label = HEATMAP_AXIS_SPECS[col_axis]
        subfolder = os.path.join(HEATMAP_DIR, heatmap_slug(col_axis))
        group_heatmap_items = []
        group_heatmap_items_no_out = []
        group_heatmap_items_median = []
        subfolder_index = 1
        for row_axis in row_axes:
            row_key, row_label = HEATMAP_AXIS_SPECS[row_axis]
            triplet_items = []
            triplet_items_no_out = []
            triplet_items_median = []
            for metric_slug, metric_filename_part, caption_prefix, sample_scope, colorbar_label, value_format in HEATMAP_METRIC_SPECS:
                filename = (
                    f"{subfolder_index:02d}_heatmap_{metric_filename_part}_"
                    f"{heatmap_slug(row_axis)}_vs_{heatmap_slug(col_axis)}.png"
                )
                spec = {
                    "kind": "heatmap",
                    "filename": filename,
                    "caption": f"{caption_prefix} ({sample_scope}): {row_label} x {col_label}",
                    "title": f"{caption_prefix} ({sample_scope}): {row_label} x {col_label}",
                    "row_key": row_key,
                    "col_key": col_key,
                    "row_label": row_label,
                    "col_label": col_label,
                    "metric": metric_slug,
                    "sample_scope": sample_scope,
                    "colorbar_label": colorbar_label,
                    "value_format": value_format,
                    "no_outliers": False,
                    "axis_slug": col_axis,
                    "subfolder": subfolder,
                }
                items.append(spec)
                triplet_items.append(spec)
                group_heatmap_items.append(spec)
                subfolder_index += 1

                no_out_scope = f"{sample_scope}, no outliers"
                no_out_filename = (
                    f"{subfolder_index:02d}_heatmap_{metric_filename_part}_"
                    f"{heatmap_slug(row_axis)}_vs_{heatmap_slug(col_axis)}_no_out.png"
                )
                no_out_spec = {
                    "kind": "heatmap",
                    "filename": no_out_filename,
                    "caption": f"{caption_prefix} ({no_out_scope}): {row_label} x {col_label}",
                    "title": f"{caption_prefix} ({no_out_scope}): {row_label} x {col_label}",
                    "row_key": row_key,
                    "col_key": col_key,
                    "row_label": row_label,
                    "col_label": col_label,
                    "metric": metric_slug,
                    "sample_scope": no_out_scope,
                    "colorbar_label": f"{colorbar_label} (no outliers)",
                    "value_format": value_format,
                    "no_outliers": True,
                    "axis_slug": col_axis,
                    "subfolder": subfolder,
                }
                items.append(no_out_spec)
                triplet_items_no_out.append(no_out_spec)
                group_heatmap_items_no_out.append(no_out_spec)
                subfolder_index += 1

                median_scope = f"{sample_scope}, median"
                median_filename = (
                    f"{subfolder_index:02d}_heatmap_{metric_filename_part}_"
                    f"{heatmap_slug(row_axis)}_vs_{heatmap_slug(col_axis)}_median.png"
                )
                median_spec = {
                    "kind": "heatmap",
                    "filename": median_filename,
                    "caption": f"{caption_prefix} ({median_scope}): {row_label} x {col_label}",
                    "title": f"{caption_prefix} ({median_scope}): {row_label} x {col_label}",
                    "row_key": row_key,
                    "col_key": col_key,
                    "row_label": row_label,
                    "col_label": col_label,
                    "metric": metric_slug,
                    "sample_scope": median_scope,
                    "colorbar_label": f"{colorbar_label} (median)",
                    "value_format": value_format,
                    "median": True,
                    "axis_slug": col_axis,
                    "subfolder": subfolder,
                }
                items.append(median_spec)
                triplet_items_median.append(median_spec)
                group_heatmap_items_median.append(median_spec)
                subfolder_index += 1

            triplet_dashboard = {
                "kind": "triplet_dashboard",
                "filename": f"{subfolder_index:02d}_dashboard_{heatmap_slug(row_axis)}_vs_{heatmap_slug(col_axis)}.png",
                "caption": f"Dashboard: {row_label} x {col_label}",
                "title": f"{row_label} x {col_label}",
                "source_items": triplet_items,
                "columns": len(HEATMAP_METRIC_SPECS),
                "panel_title_mode": "metric",
                "panel_width": 6.4,
                "panel_height": 5.0,
                "dpi": DASHBOARD_OUTPUT_DPI,
                "axis_slug": col_axis,
                "subfolder": subfolder,
            }
            items.append(triplet_dashboard)
            subfolder_index += 1

            triplet_dashboard_no_out = {
                "kind": "triplet_dashboard",
                "filename": f"{subfolder_index:02d}_dashboard_{heatmap_slug(row_axis)}_vs_{heatmap_slug(col_axis)}_no_out.png",
                "caption": f"Dashboard (no outliers): {row_label} x {col_label}",
                "title": f"{row_label} x {col_label} (no outliers)",
                "source_items": triplet_items_no_out,
                "columns": len(HEATMAP_METRIC_SPECS),
                "panel_title_mode": "metric",
                "panel_width": 6.4,
                "panel_height": 5.0,
                "dpi": DASHBOARD_OUTPUT_DPI,
                "axis_slug": col_axis,
                "subfolder": subfolder,
            }
            items.append(triplet_dashboard_no_out)
            subfolder_index += 1

            triplet_dashboard_median = {
                "kind": "triplet_dashboard",
                "filename": f"{subfolder_index:02d}_dashboard_{heatmap_slug(row_axis)}_vs_{heatmap_slug(col_axis)}_median.png",
                "caption": f"Dashboard (median): {row_label} x {col_label}",
                "title": f"{row_label} x {col_label} (median)",
                "source_items": triplet_items_median,
                "columns": len(HEATMAP_METRIC_SPECS),
                "panel_title_mode": "metric",
                "panel_width": 6.4,
                "panel_height": 5.0,
                "dpi": DASHBOARD_OUTPUT_DPI,
                "axis_slug": col_axis,
                "subfolder": subfolder,
            }
            items.append(triplet_dashboard_median)
            subfolder_index += 1

        items.append(
            {
                "kind": "x_axis_dashboard",
                "filename": f"{subfolder_index:02d}_dashboard_x_{heatmap_slug(col_axis)}.png",
                "caption": f"Dashboard: all y axes x {col_label}",
                "title": f"All y axes x {col_label}",
                "source_items": group_heatmap_items,
                "columns": len(HEATMAP_METRIC_SPECS),
                "panel_title_mode": "axis_and_metric",
                "panel_width": 6.4,
                "panel_height": 5.0,
                "dpi": DASHBOARD_OUTPUT_DPI,
                "axis_slug": col_axis,
                "subfolder": subfolder,
            }
        )
        subfolder_index += 1

        items.append(
            {
                "kind": "x_axis_dashboard",
                "filename": f"{subfolder_index:02d}_dashboard_x_{heatmap_slug(col_axis)}_no_out.png",
                "caption": f"Dashboard (no outliers): all y axes x {col_label}",
                "title": f"All y axes x {col_label} (no outliers)",
                "source_items": group_heatmap_items_no_out,
                "columns": len(HEATMAP_METRIC_SPECS),
                "panel_title_mode": "axis_and_metric",
                "panel_width": 6.4,
                "panel_height": 5.0,
                "dpi": DASHBOARD_OUTPUT_DPI,
                "axis_slug": col_axis,
                "subfolder": subfolder,
            }
        )
        subfolder_index += 1

        items.append(
            {
                "kind": "x_axis_dashboard",
                "filename": f"{subfolder_index:02d}_dashboard_x_{heatmap_slug(col_axis)}_median.png",
                "caption": f"Dashboard (median): all y axes x {col_label}",
                "title": f"All y axes x {col_label} (median)",
                "source_items": group_heatmap_items_median,
                "columns": len(HEATMAP_METRIC_SPECS),
                "panel_title_mode": "axis_and_metric",
                "panel_width": 6.4,
                "panel_height": 5.0,
                "dpi": DASHBOARD_OUTPUT_DPI,
                "axis_slug": col_axis,
                "subfolder": subfolder,
            }
        )
        subfolder_index += 1

        for metric_slug, metric_filename_part, caption_prefix, sample_scope, ylabel, value_format, color in AXIS_BARPLOT_METRIC_SPECS:
            items.append(
                {
                    "kind": "axis_barplot",
                    "filename": f"{subfolder_index:02d}_barplot_{metric_filename_part}_by_{heatmap_slug(col_axis)}.png",
                    "caption": f"{caption_prefix} {col_label} ({sample_scope})",
                    "title": f"{caption_prefix} {col_label} ({sample_scope})",
                    "axis_key": col_key,
                    "metric": metric_slug,
                    "ylabel": ylabel,
                    "value_format": value_format,
                    "color": color,
                    "axis_slug": col_axis,
                    "subfolder": subfolder,
                }
            )
            subfolder_index += 1

        items.append(
            {
                "kind": "best_config_count",
                "filename": f"{subfolder_index:02d}_best_config_count_by_{heatmap_slug(col_axis)}.png",
                "caption": f"Best routing config count by {col_label}",
                "title": f"Best routing config count by {col_label}",
                "axis_slug": col_axis,
                "axis_key": col_key,
                "axis_label": col_label,
                "subfolder": subfolder,
            }
        )
        subfolder_index += 1

        items.append(
            {
                "kind": "best_config_count_non_routed",
                "filename": f"{subfolder_index:02d}_best_non_routed_count_by_{heatmap_slug(col_axis)}.png",
                "caption": f"Best non-routed layer % config count by {col_label}",
                "title": f"Best non-routed layer % config count by {col_label}",
                "axis_slug": col_axis,
                "axis_key": col_key,
                "axis_label": col_label,
                "subfolder": subfolder,
            }
        )
        subfolder_index += 1

        items.append(
            {
                "kind": "timeout_count",
                "filename": f"{subfolder_index:02d}_timeout_count_by_{heatmap_slug(col_axis)}.png",
                "caption": f"Timeout count by {col_label}",
                "title": f"Timeout count by {col_label}",
                "axis_slug": col_axis,
                "axis_key": col_key,
                "axis_label": col_label,
                "subfolder": subfolder,
            }
        )
        subfolder_index += 1

        items.append(
            {
                "kind": "circuit_table",
                "filename": f"{subfolder_index:02d}_circuit_table_x_{heatmap_slug(col_axis)}.png",
                "caption": f"Circuits tested by {col_label}",
                "title": f"Circuits tested by {col_label}",
                "axis_slug": col_axis,
                "col_key": col_key,
                "col_label": col_label,
                "subfolder": subfolder,
            }
        )
        subfolder_index += 1
    return items


REQUESTED_HEATMAP_ITEMS = build_requested_heatmap_items()
REQUESTED_HEATMAP_SPECS = [
    item for item in REQUESTED_HEATMAP_ITEMS if item["kind"] == "heatmap"
]


def filter_heatmap_items_by_axes(items, axis_slugs=None):
    if not axis_slugs:
        return list(items)
    axis_set = set(axis_slugs)
    return [item for item in items if item.get("axis_slug") in axis_set]


def selected_heatmap_axis_slugs(args):
    selected = set()
    worker_axes = getattr(args, "worker_heatmap_axes", "") or ""
    selected.update(axis.strip() for axis in worker_axes.split(",") if axis.strip())
    for _flags, dest, axis_slug, _label in HEATMAP_AXIS_FLAG_SPECS:
        if getattr(args, dest, False):
            selected.add(axis_slug)
    return [axis_slug for axis_slug in HEATMAP_X_AXIS_SLUGS if axis_slug in selected]


REPORT_PLOTS = [
    ("00_overview_dashboard.png", "Overview dashboard"),
    ("01_status_and_exit_codes.png", "Run status and exit codes"),
    ("02_circuit_summary_bars.png", "Circuit-level summary"),
    ("03_box_routing_by_circuit.png", "Routing steps by circuit"),
    ("04_box_elapsed_by_circuit.png", "Duration by circuit"),
    ("05_box_non_routed_pct_by_circuit.png", "Non-routed layer % by circuit"),
    ("47_box_elapsed_by_gaussian_strategy.png", "Duration by gaussian strategy"),
    ("21_box_gaussian_weight_combinations_vs_routing.png", "Routing by gaussian weight combinations"),
    ("31_heatmap_best_gaussian_relative_weight_gaps.png", "Relative distances between best gaussian weights"),
    ("09_scatter_density_vs_routing.png", "Density vs routing"),
    ("12_scatter_pressure_vs_elapsed.png", "Interaction pressure vs duration"),
    (
        "32_runtime_vs_qubits_plus_gates_cube_with_timeouts.png",
        "Duration vs qubits plus gates: cube median points",
    ),
    (
        "32_runtime_vs_qubits_plus_gates_connectivity_with_timeouts.png",
        "Duration vs qubits plus gates: connectivity median points",
    ),
    (
        "33_runtime_vs_qubits_cube_with_timeouts.png",
        "Duration vs qubits: cube median points",
    ),
    (
        "33_runtime_vs_qubits_connectivity_with_timeouts.png",
        "Duration vs qubits: connectivity median points",
    ),
    (
        "34_runtime_vs_gates_cube_with_timeouts.png",
        "Duration vs gates: cube median points",
    ),
    (
        "34_runtime_vs_gates_connectivity_with_timeouts.png",
        "Duration vs gates: connectivity median points",
    ),
    (
        "35_runtime_vs_graph_nodes_cube_with_timeouts.png",
        "Duration vs graph size: cube median points",
    ),
    (
        "35_runtime_vs_graph_nodes_connectivity_with_timeouts.png",
        "Duration vs graph size: connectivity median points",
    ),
    ("37_runtime_vs_qubits_by_gaussian_confidence.png", "Duration vs qubits by gaussian confidence"),
    ("38_runtime_vs_qubits_by_safe_passage_strategy.png", "Duration vs qubits by safe passage"),
    ("40_runtime_vs_gates_by_gaussian_confidence.png", "Duration vs gates by gaussian confidence"),
    ("41_runtime_vs_gates_by_safe_passage_strategy.png", "Duration vs gates by safe passage"),
    ("43_runtime_vs_graph_nodes_by_gaussian_confidence.png", "Duration vs graph size by gaussian confidence"),
    ("44_runtime_vs_graph_nodes_by_safe_passage_strategy.png", "Duration vs graph size by safe passage"),
    ("17_experiment_set_routing_gaussian_homogeneous.png", "Experiment set: gaussian + homogeneous"),
    ("18_experiment_set_routing_magicaware_homogeneous.png", "Experiment set: magic-aware + homogeneous"),
    ("22_experiment_set_routing_all_mappings.png", "Experiment set: all mappings"),
] + [(item["filename"], item["caption"]) for item in REQUESTED_HEATMAP_ITEMS]
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
_EXTRA_STATUS_PALETTE = [
    "#264653",
    "#9B2226",
    "#005F73",
    "#CA6702",
    "#0A9396",
    "#AE2012",
    "#BB3E03",
    "#94D2BD",
]


def register_extra_statuses(rows):
    seen = sorted({
        normalize_text(row.get("status"))
        for row in rows
        if row.get("status") and normalize_text(row.get("status")) not in STATUS_COLORS
    })
    for i, status in enumerate(seen):
        STATUS_DISPLAY_LABELS[status] = status.replace("_", " ")
        STATUS_COLORS[status] = _EXTRA_STATUS_PALETTE[i % len(_EXTRA_STATUS_PALETTE)]


EXIT_CODE_DISPLAY_LABELS = {
    124: "124 (timeout)",
    129: "129 (SIGHUP)",
    130: "130 (Ctrl+C)",
    143: "143 (SIGTERM)",
}
DISTINCT_IGNORED_COLUMNS = {
    "routing_steps",
    "total_routing_steps",
    "timeout_reached",
    "status",
    "exit_code",
    "duration_seconds",
    "elapsed_ms",
    "error_excerpt",
    "id",
    "run_id",
    "run_date",
    "run_datetime",
    "log_file",
}
DISTINCT_SOURCE_COLUMNS = ("source_csv", "source_csv_name")
DISTINCT_IDENTITY_ALIASES = {
    "graph_x": ("graph_x", "x"),
    "graph_y": ("graph_y", "y"),
    "magic_state_placement_strategy": ("magic_state_placement_strategy", "placement"),
}
DISTINCT_NUMERIC_FIELDS = {
    "graph_x",
    "graph_y",
    "x",
    "y",
    "total_nodes",
    "magic_high",
    "magic_low",
    "cnot_high",
    "cnot_low",
    "mapped_gaussian_weight",
    "base_gaussian_weight",
    "external_weight",
    "gaussian_confidence",
    "border_distance_percentage",
    "number_of_magic_states",
    "routing_steps",
    "total_routing_steps",
    "interaction_pressure",
    "data_density",
    "overall_density",
}


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_csv_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_csv_fieldname(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_distinct_decimal(value):
    text = normalize_csv_text(value)
    if text == "":
        return ""

    try:
        decimal_value = Decimal(text)
    except InvalidOperation:
        return text

    if decimal_value.is_nan():
        return "nan"
    if decimal_value == 0:
        return "0"

    normalized = format(decimal_value.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def normalize_distinct_value(fieldname, value):
    text = normalize_csv_text(value)
    if text == "":
        return ""
    if fieldname in DISTINCT_NUMERIC_FIELDS:
        return normalize_distinct_decimal(text)
    if fieldname == "status":
        return text.lower()
    return text


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


def format_gaussian_confidence_label(value):
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
    if 0.0 < value < 1.0:
        return f"{value:.10f}".rstrip("0").rstrip(".")
    return format_number_label(value)


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
    required_keys = (
        "magic_high_f",
        "magic_low_f",
        "cnot_high_f",
        "cnot_low_f",
        "mapped_gaussian_weight_f",
        "base_gaussian_weight_f",
    )
    values = []
    for key in required_keys:
        value = row.get(key)
        if value is None or math.isnan(value):
            return None
        values.append(float(value))
    external_weight = row.get("external_weight_f")
    if external_weight is None or math.isnan(external_weight):
        values.append(None)
    else:
        values.append(float(external_weight))
    return tuple(values)


def gaussian_weight_sort_key(combo):
    return tuple(-math.inf if value is None else value for value in combo)


def gaussian_weight_combo_label(row):
    if row.get("mapping_type_norm") != "gaussian":
        return None
    combo = gaussian_weight_tuple(row)
    if combo is None:
        return None
    magic_high, magic_low, cnot_high, cnot_low, mapped_weight, base_weight, external_weight = combo
    return (
        f"magic {format_number_label(magic_high)}/{format_number_label(magic_low)}\n"
        f"cnot {format_number_label(cnot_high)}/{format_number_label(cnot_low)}\n"
        f"gauss {format_number_label(mapped_weight)}/{format_number_label(base_weight)}\n"
        f"ext {format_number_label(external_weight)}"
    )


def load_rows(csv_glob):
    files = sorted(glob.glob(csv_glob, recursive=True))
    return load_rows_from_files(files)


def add_unique_path(paths, path):
    normalized = os.path.abspath(path)
    if normalized not in paths:
        paths.append(normalized)


def resolve_csv_input_path(csv_arg):
    requested = os.path.expanduser(csv_arg)
    explicit_candidates = []
    recursive_matches = []

    add_unique_path(explicit_candidates, requested)
    if os.path.splitext(requested)[1] == "":
        add_unique_path(explicit_candidates, requested + ".csv")

    if os.path.dirname(requested) == "":
        add_unique_path(explicit_candidates, os.path.join(DEFAULT_RESULTS_DIR, requested))
        if os.path.splitext(requested)[1] == "":
            add_unique_path(explicit_candidates, os.path.join(DEFAULT_RESULTS_DIR, requested + ".csv"))

        recursive_patterns = [
            os.path.join(DEFAULT_RESULTS_DIR, "**", requested),
        ]
        if os.path.splitext(requested)[1] == "":
            recursive_patterns.append(os.path.join(DEFAULT_RESULTS_DIR, "**", requested + ".csv"))

        for pattern in recursive_patterns:
            for match in sorted(glob.glob(pattern, recursive=True)):
                if os.path.isfile(match):
                    add_unique_path(recursive_matches, match)

    explicit_existing = [path for path in explicit_candidates if os.path.isfile(path)]
    if explicit_existing:
        return explicit_existing[0]

    if len(recursive_matches) == 1:
        return recursive_matches[0]

    if len(recursive_matches) > 1:
        matches = "\n  - ".join(recursive_matches)
        raise RuntimeError(
            "Ambiguous CSV input for --csv. Multiple matches found:\n"
            f"  - {matches}"
        )

    attempted = "\n  - ".join(explicit_candidates)
    raise FileNotFoundError(
        "Could not resolve CSV input for --csv. Tried:\n"
        f"  - {attempted}"
    )


def default_output_dir_for_single_csv(csv_path, distinct):
    suffix = "_merge_plots" if distinct else "_plots"
    return os.path.join(
        os.path.dirname(csv_path),
        os.path.splitext(os.path.basename(csv_path))[0] + suffix,
    )


def default_output_dir_for_glob(distinct):
    if distinct:
        return os.path.join(DEFAULT_RESULTS_DIR, "merge_plots")
    return os.path.join(DEFAULT_RESULTS_DIR, "plots")


def filter_distinct_input_files(files):
    results_dir = os.path.abspath(DEFAULT_RESULTS_DIR)
    filtered = []
    seen = set()
    for path in files:
        normalized = os.path.abspath(path)
        if os.path.dirname(normalized) != results_dir:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        filtered.append(normalized)
    return filtered


def load_raw_rows_from_files(files):
    rows = []
    fieldnames = []
    seen_fieldnames = set()
    accepted_files = []

    for path in files:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue

            normalized_fieldnames = []
            normalized_to_original = {}
            for fieldname in reader.fieldnames:
                normalized = normalize_csv_fieldname(fieldname)
                if not normalized or normalized in normalized_to_original:
                    continue
                normalized_fieldnames.append(normalized)
                normalized_to_original[normalized] = fieldname

            if (
                "status" not in normalized_fieldnames
                or ("run_id" not in normalized_fieldnames and "id" not in normalized_fieldnames)
            ):
                continue

            accepted_files.append(path)
            for fieldname in normalized_fieldnames:
                if fieldname in seen_fieldnames:
                    continue
                fieldnames.append(fieldname)
                seen_fieldnames.add(fieldname)

            for fieldname in DISTINCT_SOURCE_COLUMNS:
                if fieldname in seen_fieldnames:
                    continue
                fieldnames.append(fieldname)
                seen_fieldnames.add(fieldname)

            for row_index, raw in enumerate(reader):
                row = {
                    fieldname: raw.get(normalized_to_original[fieldname], "")
                    for fieldname in normalized_fieldnames
                }
                if "run_id" not in row and "id" in row:
                    row["run_id"] = row.get("id", "")
                row["source_csv"] = path
                row["source_csv_name"] = os.path.basename(path)
                row["_merge_order"] = len(rows)
                row["_source_row_index"] = row_index
                rows.append(row)

    return rows, fieldnames, accepted_files


def distinct_identity_fieldnames(fieldnames):
    identity_fields = []
    alias_fieldnames = set()

    for canonical_name, aliases in DISTINCT_IDENTITY_ALIASES.items():
        if any(alias in fieldnames for alias in aliases):
            identity_fields.append(canonical_name)
            alias_fieldnames.update(aliases)

    for fieldname in fieldnames:
        if fieldname in DISTINCT_IGNORED_COLUMNS:
            continue
        if fieldname in DISTINCT_SOURCE_COLUMNS:
            continue
        if fieldname.startswith("_"):
            continue
        if fieldname in alias_fieldnames:
            continue
        identity_fields.append(fieldname)

    return identity_fields


def distinct_identity_value(row, fieldname):
    aliases = DISTINCT_IDENTITY_ALIASES.get(fieldname)
    if aliases is not None:
        return pick_first(row, *aliases)
    return row.get(fieldname)


def distinct_identity_key(row, identity_fields):
    return tuple(
        normalize_distinct_value(fieldname, distinct_identity_value(row, fieldname))
        for fieldname in identity_fields
    )


def distinct_result_signature(row):
    return (
        normalize_distinct_value("status", row.get("status")),
        normalize_distinct_value("routing_steps", pick_first(row, "routing_steps", "total_routing_steps")),
    )


def csv_output_fieldnames(fieldnames):
    return [fieldname for fieldname in fieldnames if not fieldname.startswith("_")]


def write_csv_rows(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({fieldname: row.get(fieldname, "") for fieldname in fieldnames})


def merge_rows_distinct(raw_rows, fieldnames, output_dir, merged_file_count):
    identity_fields = distinct_identity_fieldnames(fieldnames)
    grouped_rows = defaultdict(list)
    for row in raw_rows:
        grouped_rows[distinct_identity_key(row, identity_fields)].append(row)

    merged_rows = []
    conflicting_rows = []
    exact_duplicates_removed = 0
    repeated_configuration_groups = 0
    same_result_duplicate_groups = 0
    different_result_duplicate_groups = 0
    conflicting_groups = 0

    # Keep one representative per (configuration, status, routing_steps) pair.
    for group_rows in grouped_rows.values():
        if len(group_rows) > 1:
            repeated_configuration_groups += 1

        result_signature_counts = Counter(distinct_result_signature(row) for row in group_rows)
        if any(count > 1 for count in result_signature_counts.values()):
            same_result_duplicate_groups += 1
        if len(result_signature_counts) > 1:
            different_result_duplicate_groups += 1

        unique_variants = {}
        ordered_variants = []
        for row in group_rows:
            result_signature = distinct_result_signature(row)
            if result_signature in unique_variants:
                exact_duplicates_removed += 1
                continue
            unique_variants[result_signature] = row
            ordered_variants.append(row)

        merged_rows.extend(ordered_variants)
        if len(ordered_variants) > 1:
            conflicting_groups += 1
            conflicting_rows.extend(ordered_variants)

    output_fieldnames = csv_output_fieldnames(fieldnames)
    merged_csv_path = os.path.join(output_dir, f"merged_distinct_{merged_file_count}.csv")
    duplicates_csv_path = os.path.join(output_dir, "merging_duplicates.csv")
    write_csv_rows(merged_csv_path, output_fieldnames, merged_rows)
    write_csv_rows(duplicates_csv_path, output_fieldnames, conflicting_rows)

    return merged_rows, {
        "merged_csv_path": merged_csv_path,
        "duplicates_csv_path": duplicates_csv_path,
        "identity_fields": identity_fields,
        "input_rows": len(raw_rows),
        "merged_rows": len(merged_rows),
        "repeated_configuration_groups": repeated_configuration_groups,
        "same_result_duplicate_groups": same_result_duplicate_groups,
        "different_result_duplicate_groups": different_result_duplicate_groups,
        "duplicate_rows_removed": exact_duplicates_removed,
        "conflicting_groups": conflicting_groups,
        "conflicting_rows": len(conflicting_rows),
    }


# Raw CSV columns we can drop after prepare_rows_for_analysis because:
#  - they are never read by any plot/aggregation (mid_*, lower_*, log_file, ...)
#  - OR they only feed a derived field on the row (e.g. duration_seconds → duration_s_f)
# Dropping these halves the per-row dict footprint on huge CSVs.
_DROP_RAW_FIELDS_AFTER_PREP = (
    # never used anywhere
    "mid_x", "mid_y", "mid_duration_seconds", "mid_routing_steps", "mid_status",
    "lower_x", "lower_y", "lower_duration_seconds", "lower_routing_steps", "lower_status",
    "mid_non_routed_layer_pct", "lower_non_routed_layer_pct",
    "t_states_proportional", "resolved_n_magic",
    "log_file", "error_excerpt", "run_date", "run_datetime",
    "timeout_reached",
    # only used to derive _f / _i fields in prepare_rows_for_analysis
    "duration_seconds", "elapsed_ms",
    "number_of_magic_states",
    "border_distance_percentage",
    "magic_high", "magic_low", "cnot_high", "cnot_low",
    "mapped_gaussian_weight", "base_gaussian_weight", "external_weight",
    "gaussian_confidence",
    "non_routed_layer_pct",
    "interaction_pressure", "data_density", "overall_density",
    "exit_code",
    "total_nodes",
    "graph_x", "graph_y", "x", "y",
)


def prepare_rows_for_analysis(raw_rows):
    # Mutate raw_rows in place to avoid temporarily doubling the dict count
    # (and the working set) on huge CSVs.
    for row in raw_rows:
        row["circuit_name"] = os.path.basename(row.get("circuit", ""))
        row["placement"] = normalize_placement(
            pick_first(row, "magic_state_placement_strategy", "placement")
        )
        row["mapping_type_norm"] = normalize_text(row.get("mapping_type"))
        row["safe_passage_norm"] = normalize_text(row.get("safe_passage_strategy"))
        row["magic_aware_strategy_norm"] = normalize_text(row.get("magic_aware_strategy"))
        row["gaussian_strategy_norm"] = normalize_text(row.get("gaussian_strategy"))
        row["routing_strategy_norm"] = normalize_text(row.get("routing_strategy"))
        row["t_routing_mode_norm"] = normalize_text(row.get("t_routing_mode"))
        row["use_layer_cache_norm"] = normalize_text(row.get("use_layer_cache"))
        row["x_i"] = to_int(pick_first(row, "graph_x", "x"))
        row["y_i"] = to_int(pick_first(row, "graph_y", "y"))
        row["total_nodes_i"] = to_int(row.get("total_nodes"))
        row["magic_states_f"] = to_float(row.get("number_of_magic_states"))
        if row["magic_states_f"] is not None:
            row["magic_states_label"] = format_number_label(row["magic_states_f"])
        else:
            row["magic_states_label"] = ""
        row["border_pct_f"] = to_float(row.get("border_distance_percentage"))
        row["magic_high_f"] = to_float(row.get("magic_high"))
        row["magic_low_f"] = to_float(row.get("magic_low"))
        row["cnot_high_f"] = to_float(row.get("cnot_high"))
        row["cnot_low_f"] = to_float(row.get("cnot_low"))
        row["mapped_gaussian_weight_f"] = to_float(row.get("mapped_gaussian_weight"))
        row["base_gaussian_weight_f"] = to_float(row.get("base_gaussian_weight"))
        row["external_weight_f"] = to_float(row.get("external_weight"))
        row["gaussian_confidence_f"] = to_float(row.get("gaussian_confidence"))
        if row["gaussian_confidence_f"] is not None:
            row["gaussian_confidence_label"] = format_gaussian_confidence_label(row["gaussian_confidence_f"])
        else:
            row["gaussian_confidence_label"] = ""
        duration_seconds = to_float(row.get("duration_seconds"))
        elapsed_ms = to_float(row.get("elapsed_ms"))
        if duration_seconds is not None:
            row["duration_s_f"] = duration_seconds
        elif elapsed_ms is not None:
            row["duration_s_f"] = elapsed_ms / 1000.0
        else:
            row["duration_s_f"] = None
        row["routing_steps_f"] = to_float(pick_first(row, "routing_steps", "total_routing_steps"))
        row["non_routed_layer_pct_f"] = to_float(row.get("non_routed_layer_pct"))
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
        for _drop_key in _DROP_RAW_FIELDS_AFTER_PREP:
            row.pop(_drop_key, None)

    return raw_rows


def load_rows_from_files(files):
    raw_rows, _, accepted_files = load_raw_rows_from_files(files)
    return prepare_rows_for_analysis(raw_rows), accepted_files


def non_empty(values):
    return [v for v in values if v is not None and not math.isnan(v)]


def strip_plot_number(filename):
    """Drop a leading NN_ index from a plot filename for the on-disk name."""
    return re.sub(r"^\d+_", "", filename)


def default_plot_subfolder(filename):
    output_name = strip_plot_number(filename)
    if output_name.lower().endswith(".png"):
        return TIME_ANALYSIS_DIR
    return None


def save_fig(fig, output_dir, filename, generated, dpi=160, tight=True, subfolder=None):
    if subfolder is None:
        subfolder = default_plot_subfolder(filename)
    if subfolder == TIME_ANALYSIS_DIR and not INCLUDE_TIME_ANALYSIS:
        # --time was not passed: drop the figure without writing it to disk.
        fig.clear()
        plt.close(fig)
        plt.close("all")
        _trim_heap()
        return
    if subfolder:
        target_dir = os.path.join(output_dir, subfolder)
    else:
        target_dir = output_dir
    os.makedirs(target_dir, exist_ok=True)
    in_heatmap = subfolder and (subfolder == HEATMAP_DIR or subfolder.startswith(HEATMAP_DIR + os.sep))
    disk_name = filename if in_heatmap else strip_plot_number(filename)
    path = os.path.join(target_dir, disk_name)
    if tight:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            fig.tight_layout()
    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches="tight" if tight else None,
        pad_inches=0.2 if tight else 0.1,
    )
    fig.clear()
    plt.close(fig)
    plt.close("all")
    _trim_heap()
    generated.append(path)


def record_skipped_plot(skipped, filename, reason):
    if skipped is None:
        return
    skipped.append({"filename": strip_plot_number(filename), "reason": reason})


def save_empty_plot(title, output_dir, filename, generated, message="No data", subfolder=None, ylabel=None, dpi=None):
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.set_title(title, fontsize=14, pad=14)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=13,
        color="#64748B",
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    save_fig(
        fig,
        output_dir,
        filename,
        generated,
        dpi=dpi if dpi is not None else 160,
        subfolder=subfolder,
    )


def compact_labels(labels, limit=8):
    labels = [str(label) for label in labels if str(label).strip()]
    if not labels:
        return "none"
    if len(labels) <= limit:
        return ", ".join(labels)
    return ", ".join(labels[:limit]) + f", ... (+{len(labels) - limit} more)"


def remove_obsolete_plots(output_dir):
    filenames = set(OBSOLETE_PLOT_FILENAMES)
    if os.path.isdir(output_dir):
        for filename in os.listdir(output_dir):
            if filename.lower().endswith(".png"):
                filenames.add(filename)
            if any(filename.startswith(prefix) for prefix in OBSOLETE_PLOT_PREFIXES):
                filenames.add(filename)
            if filename.lower().endswith(".png") and "_heatmap_" in filename:
                filenames.add(filename)
            if filename.lower().endswith(".png") and re.match(r"\d+_dashboard_", filename.lower()):
                filenames.add(filename)
            if filename.lower().endswith(".png") and re.match(r"\d+_barplot_", filename.lower()):
                filenames.add(filename)
            if filename.lower().endswith(".png") and re.match(r"\d+_best_config_count_", filename.lower()):
                filenames.add(filename)

    for filename in filenames:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            continue
        try:
            os.remove(path)
        except OSError as exc:
            warnings.warn(f"Could not remove obsolete plot {path}: {exc}")


def clear_per_circuit_barplot_dir(output_dir):
    target_dir = os.path.join(output_dir, PER_CIRCUIT_BARPLOT_DIR)
    if not os.path.isdir(target_dir):
        return

    for root, dirs, files in os.walk(target_dir, topdown=False):
        for filename in files:
            if not filename.lower().endswith(".png"):
                continue
            path = os.path.join(root, filename)
            try:
                os.remove(path)
            except OSError as exc:
                warnings.warn(f"Could not remove obsolete per-circuit barplot {path}: {exc}")
        for dirname in dirs:
            path = os.path.join(root, dirname)
            try:
                if not os.listdir(path):
                    os.rmdir(path)
            except OSError:
                pass


def clear_plot_tree(target_dir, warning_label):
    if not os.path.isdir(target_dir):
        return
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for filename in files:
            if not filename.lower().endswith(".png"):
                continue
            path = os.path.join(root, filename)
            try:
                os.remove(path)
            except OSError as exc:
                warnings.warn(f"Could not remove obsolete {warning_label} plot {path}: {exc}")
        for dirname in dirs:
            path = os.path.join(root, dirname)
            try:
                if not os.listdir(path):
                    os.rmdir(path)
            except OSError:
                pass


def clear_heatmap_dir(output_dir, axis_slugs=None):
    if axis_slugs:
        for axis_slug in axis_slugs:
            clear_plot_tree(
                os.path.join(output_dir, HEATMAP_DIR, heatmap_slug(axis_slug)),
                "heatmap",
            )
        return
    clear_plot_tree(os.path.join(output_dir, HEATMAP_DIR), "heatmap")


def category_color_map(labels):
    cmap = plt.get_cmap("tab20", max(1, len(labels)))
    return {label: cmap(i) for i, label in enumerate(labels)}


def label_with_sample_count(label, count):
    return f"{label}\n(n={count})"


def legend_label_with_sample_count(label, count):
    return f"{label} (n={count})"


def is_timeout(row):
    return normalize_text(row.get("status")) in TIMEOUT_STATUSES


def exclude_timeout_rows(rows):
    return [row for row in rows if not is_timeout(row)]


def annotate_bars(ax, bars, fmt="{:.0f}"):
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=8,
        )


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
    bars = axs[0].bar(labels, vals, color=["#3A7CA5", "#B94E48", "#D9A441"][: len(labels)])
    axs[0].set_title("Runs by Status")
    axs[0].set_ylabel("Count")
    annotate_bars(axs[0], bars)

    qasm_cache = {}
    qubit_points = []
    for r in rows:
        circuit = r.get("circuit") or r.get("circuit_name")
        duration = r.get("duration_s_f")
        if duration is None:
            continue
        metrics = qasm_metrics_for_circuit(circuit, qasm_cache)
        if metrics is None:
            continue
        qubit_points.append((duration, metrics["qubits"], r["status"]))
    _SCATTER_CAP_Q = 50000
    for status in sorted({p[2] for p in qubit_points}):
        subset = [p for p in qubit_points if p[2] == status]
        if not subset:
            continue
        display_subset = subset
        if len(subset) > _SCATTER_CAP_Q:
            step = max(1, len(subset) // _SCATTER_CAP_Q)
            display_subset = subset[::step]
        axs[1].scatter(
            [p[0] for p in display_subset],
            [p[1] for p in display_subset],
            s=28,
            alpha=0.7,
            label=legend_label_with_sample_count(status_display_label(status), len(subset)),
            color=status_color(status),
        )
    axs[1].set_title(f"Duration vs #Qubits (n={len(qubit_points)})")
    axs[1].set_xlabel("duration_seconds")
    axs[1].set_ylabel("#qubits")
    axs[1].legend(fontsize=8, loc="upper right")

    circuit_sample_labels = [label_with_sample_count(c, circuit_counts[c]) for c in circuits]
    bars = axs[2].bar(circuits, [success_by_circuit.get(c, 0.0) * 100 for c in circuits], color="#43AA8B")
    axs[2].set_title("Success Rate by Circuit")
    axs[2].set_ylabel("%")
    axs[2].set_ylim(0, 105)
    axs[2].set_xticks(range(len(circuits)))
    axs[2].set_xticklabels(circuit_sample_labels)
    axs[2].tick_params(axis="x", rotation=35)
    annotate_bars(axs[2], bars, fmt="{:.1f}")

    if duration_values:
        axs[3].hist(duration_values, bins=min(20, max(8, int(len(duration_values) ** 0.5))), color="#277DA1")
    axs[3].set_title(f"Duration Distribution (Successful Runs, n={len(duration_values)})")
    axs[3].set_xlabel("duration_seconds")

    if routing_ok:
        axs[4].hist(routing_ok, bins=min(20, max(8, int(len(routing_ok) ** 0.5))), color="#90BE6D")
    axs[4].set_title(f"Routing Steps (Successful Runs, n={len(routing_ok)})")
    axs[4].set_xlabel("total_routing_steps")

    points = [
        (r["duration_s_f"], r["routing_steps_f"], r["status"])
        for r in rows
        if r["duration_s_f"] is not None and r["routing_steps_f"] is not None
    ]
    total_points = len(points)
    # Downsample to keep the scatter plot from exploding memory on huge runs.
    _SCATTER_CAP = 50000
    for status in sorted({p[2] for p in points}):
        subset = [p for p in points if p[2] == status]
        if not subset:
            continue
        display_subset = subset
        if len(subset) > _SCATTER_CAP:
            step = max(1, len(subset) // _SCATTER_CAP)
            display_subset = subset[::step]
        axs[5].scatter(
            [p[0] for p in display_subset],
            [p[1] for p in display_subset],
            s=28,
            alpha=0.7,
            label=legend_label_with_sample_count(status_display_label(status), len(subset)),
            color=status_color(status),
        )
    axs[5].set_title(f"Duration vs Routing Steps (n={total_points})")
    axs[5].set_xlabel("duration_seconds")
    axs[5].set_ylabel("routing_steps")
    axs[5].legend(fontsize=8, loc="upper right")

    save_fig(fig, output_dir, "00_overview_dashboard.png", generated, dpi=DASHBOARD_OUTPUT_DPI)


def plot_status_and_exit(rows, output_dir, generated):
    status_counts = Counter(r["status"] for r in rows)
    exit_counts = Counter(r["exit_code_i"] for r in rows if r["exit_code_i"] is not None)

    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    s_keys = list(status_counts.keys())
    s_labels = [status_display_label(k) for k in s_keys]
    s_vals = [status_counts[k] for k in s_keys]
    s_colors = [status_color(k) for k in s_keys]
    bars = axs[0].bar(s_labels, s_vals, color=s_colors)
    axs[0].set_title("Status Counts")
    axs[0].set_ylabel("Count")
    axs[0].tick_params(axis="x", rotation=15)
    annotate_bars(axs[0], bars)

    e_codes = sorted(exit_counts.keys())
    e_labels = [exit_code_display_label(code) for code in e_codes]
    e_vals = [exit_counts[code] for code in e_codes]
    e_colors = [exit_code_color(code) for code in e_codes]
    bars = axs[1].bar(e_labels, e_vals, color=e_colors)
    axs[1].set_title("Exit Code Counts")
    axs[1].set_xlabel("exit_code")
    axs[1].tick_params(axis="x", rotation=15)
    annotate_bars(axs[1], bars)

    save_fig(fig, output_dir, "01_status_and_exit_codes.png", generated)


def boxplot_by_category(
    rows,
    category_key,
    value_key,
    title,
    ylabel,
    filename,
    output_dir,
    generated,
    skipped=None,
    min_points=2,
):
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
        if grouped:
            categories = compact_labels(sorted(grouped.keys()))
            reason = (
                f"no category has at least {min_points} valid {value_key} values; "
                f"available categories: {categories}"
            )
        else:
            reason = f"no rows with valid numeric {value_key}"
        record_skipped_plot(skipped, filename, reason)
        return

    values = [grouped[k] for k in labels]
    display_labels = [label_with_sample_count(label, len(grouped[label])) for label in labels]
    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.0), 6.5))
    ax.boxplot(values, tick_labels=display_labels, showfliers=False)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35)
    save_fig(fig, output_dir, filename, generated)


def plot_elapsed_by_gaussian_strategy(rows, output_dir, generated, skipped=None):
    filename = "47_box_elapsed_by_gaussian_strategy.png"
    strategy_order = ("coarse", "fine")
    grouped = {strategy: [] for strategy in strategy_order}
    status_counts = {
        strategy: {"success": 0, "timeout": 0, "failed": 0, "other": 0}
        for strategy in strategy_order
    }

    for row in rows:
        if row.get("mapping_type_norm") != "gaussian":
            continue
        strategy = row.get("gaussian_strategy_norm")
        if strategy not in grouped:
            continue

        status = normalize_text(row.get("status"))
        if status in status_counts[strategy]:
            status_counts[strategy][status] += 1
        else:
            status_counts[strategy]["other"] += 1

        duration = row.get("duration_s_f")
        if not row.get("success") or duration is None or duration <= 0:
            continue
        grouped[strategy].append(duration)

    labels = [strategy for strategy in strategy_order if grouped[strategy]]
    if not labels:
        record_skipped_plot(
            skipped,
            filename,
            "no successful gaussian coarse/fine rows with positive duration_seconds",
        )
        return

    values = [grouped[strategy] for strategy in labels]
    display_labels = []
    for strategy in labels:
        durations = grouped[strategy]
        median = statistics.median(durations)
        display_labels.append(f"{strategy}\n(n={len(durations)}, median={median:.3g}s)")

    fig, ax = plt.subplots(figsize=(10, 7))
    box = ax.boxplot(
        values,
        tick_labels=display_labels,
        showmeans=True,
        patch_artist=True,
        meanprops={
            "marker": "o",
            "markerfacecolor": "#2A9D8F",
            "markeredgecolor": "#1B625A",
            "markersize": 6,
        },
        medianprops={"color": "#E76F51", "linewidth": 1.8},
        boxprops={"linewidth": 1.4},
        whiskerprops={"linewidth": 1.4},
        capprops={"linewidth": 1.4},
    )
    colors = category_color_map(labels)
    for patch, strategy in zip(box["boxes"], labels):
        patch.set_facecolor(colors[strategy])
        patch.set_alpha(0.45)

    summary_lines = []
    for strategy in labels:
        counts = status_counts[strategy]
        summary_lines.append(
            f"{strategy}: success={counts['success']}, "
            f"timeout={counts['timeout']}, failed={counts['failed']}"
        )
    ax.text(
        0.02,
        0.98,
        "\n".join(summary_lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        bbox={"facecolor": "white", "edgecolor": "#CCCCCC", "alpha": 0.85},
    )

    ax.set_title("Execution Time by Gaussian Strategy (Successful Gaussian Runs Only)")
    ax.set_ylabel("execution time (seconds, log scale)")
    ax.set_yscale("log")
    ax.grid(True, axis="y", alpha=0.35)
    save_fig(fig, output_dir, filename, generated)


def scatter_plot(
    rows,
    x_key,
    y_key,
    color_key,
    title,
    xlabel,
    ylabel,
    filename,
    output_dir,
    generated,
    skipped=None,
):
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
        record_skipped_plot(
            skipped,
            filename,
            f"no rows with valid numeric {x_key} and {y_key}",
        )
        return

    labels = sorted({p[2] for p in points})
    colors = category_color_map(labels)

    fig, ax = plt.subplots(figsize=(9, 6))
    for label in labels:
        subset = [p for p in points if p[2] == label]
        ax.scatter(
            [p[0] for p in subset],
            [p[1] for p in subset],
            label=legend_label_with_sample_count(label, len(subset)),
            alpha=0.7,
            s=28,
            color=colors[label],
        )

    ax.set_title(f"{title} (n={len(points)})")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    save_fig(fig, output_dir, filename, generated)


def plot_gaussian_weight_combinations(rows, output_dir, generated, skipped=None):
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
        record_skipped_plot(
            skipped,
            "21_box_gaussian_weight_combinations_vs_routing.png",
            "no gaussian rows with complete gaussian weights and routing_steps",
        )
        return

    ordered_labels = [
        label for label, _ in sorted(combo_labels.items(), key=lambda item: gaussian_weight_sort_key(item[1]))
    ]
    value_groups = [
        [routing for _, label, routing, _ in gaussian_rows if label == combo_label]
        for combo_label in ordered_labels
    ]
    if not any(value_groups):
        record_skipped_plot(
            skipped,
            "21_box_gaussian_weight_combinations_vs_routing.png",
            "gaussian weight combinations were found, but no routing_steps values were plottable",
        )
        return

    display_labels = [
        label_with_sample_count(label, len(values))
        for label, values in zip(ordered_labels, value_groups)
    ]
    fig, ax = plt.subplots(figsize=(max(10, len(ordered_labels) * 3.4), 7))
    box = ax.boxplot(
        value_groups,
        tick_labels=display_labels,
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
        ax.legend(title="gaussian strategy", fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1.0))

    save_fig(fig, output_dir, "21_box_gaussian_weight_combinations_vs_routing.png", generated)


def gaussian_weight_config_label(config, multiline=False, verbose=False):
    magic_high, magic_low, cnot_high, cnot_low, mapped_weight, base_weight, external_weight = config
    separator = "\n" if multiline else " | "
    if verbose:
        return separator.join(
            [
                f"magic H/L {format_number_label(magic_high)}/{format_number_label(magic_low)}",
                f"CNOT H/L {format_number_label(cnot_high)}/{format_number_label(cnot_low)}",
                f"gauss map/base {format_number_label(mapped_weight)}/{format_number_label(base_weight)}",
                f"external {format_number_label(external_weight)}",
            ]
        )
    return separator.join(
        [
            f"M {format_number_label(magic_high)}/{format_number_label(magic_low)}",
            f"C {format_number_label(cnot_high)}/{format_number_label(cnot_low)}",
            f"G {format_number_label(mapped_weight)}/{format_number_label(base_weight)}",
            f"E {format_number_label(external_weight)}",
        ]
    )


def top_gaussian_weight_config_entries(rows, top_n=3):
    grouped = defaultdict(lambda: defaultdict(list))

    for row in rows:
        if row.get("mapping_type_norm") != "gaussian":
            continue
        if not row.get("success") or row.get("routing_steps_f") is None:
            continue
        x_key = requested_x_key(row)
        combo = gaussian_weight_tuple(row)
        if x_key is None or combo is None:
            continue
        grouped[x_key][combo].append(row)

    entries = []
    grouped_ranked_entries = []
    for x_key in sorted(grouped.keys(), key=lambda item: (item[0], item[1], item[2])):
        config_metrics = []
        for combo, config_rows in grouped[x_key].items():
            routing_values = [row["routing_steps_f"] for row in config_rows]
            duration_values = [
                row["duration_s_f"]
                for row in config_rows
                if row.get("duration_s_f") is not None
            ]
            best_routing = min(routing_values)
            best_rows = [
                row for row in config_rows
                if row.get("routing_steps_f") == best_routing
            ]
            best_duration_values = [
                row["duration_s_f"]
                for row in best_rows
                if row.get("duration_s_f") is not None
            ]
            config_metrics.append(
                {
                    "combo": combo,
                    "best_routing_steps": best_routing,
                    "mean_routing_steps": float(np.mean(routing_values)),
                    "median_routing_steps": float(np.median(routing_values)),
                    "sample_count": len(config_rows),
                    "best_run_count": len(best_rows),
                    "best_duration_seconds": min(best_duration_values) if best_duration_values else None,
                    "mean_duration_seconds": float(np.mean(duration_values)) if duration_values else None,
                }
            )

        if not config_metrics:
            continue

        config_metrics.sort(
            key=lambda item: (
                item["best_routing_steps"],
                item["mean_routing_steps"],
                item["best_duration_seconds"] if item["best_duration_seconds"] is not None else math.inf,
                gaussian_weight_sort_key(item["combo"]),
            )
        )
        best_routing = config_metrics[0]["best_routing_steps"]
        tied_best_config_count = sum(
            1 for item in config_metrics
            if item["best_routing_steps"] == best_routing
        )
        ranked_entries = []

        for rank, metric in enumerate(config_metrics[:top_n], start=1):
            combo = metric["combo"]
            magic_high, magic_low, cnot_high, cnot_low, mapped_weight, base_weight, external_weight = combo
            entry = {
                "circuit_graph_label": requested_x_label(x_key),
                "circuit": x_key[0],
                "graph_x": x_key[1],
                "graph_y": x_key[2],
                "rank": rank,
                "configs_tied_for_best_routing": tied_best_config_count,
                "best_routing_steps": metric["best_routing_steps"],
                "mean_routing_steps": metric["mean_routing_steps"],
                "median_routing_steps": metric["median_routing_steps"],
                "sample_count": metric["sample_count"],
                "best_run_count": metric["best_run_count"],
                "best_duration_seconds": metric["best_duration_seconds"],
                "mean_duration_seconds": metric["mean_duration_seconds"],
                "magic_high": magic_high,
                "magic_low": magic_low,
                "cnot_high": cnot_high,
                "cnot_low": cnot_low,
                "mapped_gaussian_weight": mapped_weight,
                "base_gaussian_weight": base_weight,
                "external_weight": external_weight,
                "weight_config": gaussian_weight_config_label(combo),
            }
            entries.append(entry)
            ranked_entries.append(entry)

        grouped_ranked_entries.append(
            {
                "x_key": x_key,
                "label": requested_x_label(x_key),
                "best_routing_steps": best_routing,
                "configs_tied_for_best_routing": tied_best_config_count,
                "entries": ranked_entries,
            }
        )

    return entries, grouped_ranked_entries


def write_top_gaussian_weight_config_table(entries, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, filename)
    fieldnames = [
        "circuit_graph_label",
        "circuit",
        "graph_x",
        "graph_y",
        "rank",
        "configs_tied_for_best_routing",
        "best_routing_steps",
        "mean_routing_steps",
        "median_routing_steps",
        "sample_count",
        "best_run_count",
        "best_duration_seconds",
        "mean_duration_seconds",
        "magic_high",
        "magic_low",
        "cnot_high",
        "cnot_low",
        "mapped_gaussian_weight",
        "base_gaussian_weight",
        "external_weight",
        "weight_config",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

    return entries, csv_path


def best_gaussian_weight_profile_entries(top_gaussian_weight_entries):
    best_entries = [
        entry for entry in top_gaussian_weight_entries
        if entry.get("rank") == 1
    ]
    return sorted(
        best_entries,
        key=lambda entry: (
            entry["circuit"],
            entry["graph_x"],
            entry["graph_y"],
        ),
    )


def write_best_gaussian_weight_profile_table(entries, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, filename)
    fieldnames = [
        "circuit_graph_label",
        "circuit",
        "graph_x",
        "graph_y",
        "best_routing_steps",
        "mean_routing_steps",
        "configs_tied_for_best_routing",
        "sample_count",
        "magic_high",
        "magic_low",
        "cnot_high",
        "cnot_low",
        "mapped_gaussian_weight",
        "base_gaussian_weight",
        "external_weight",
        "weight_config",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow({field: entry.get(field, "") for field in fieldnames})
    return entries, csv_path


def plot_best_gaussian_weight_profile_heatmap(entries, output_dir, generated, skipped=None):
    filename = "30_heatmap_best_gaussian_weight_profiles.png"
    if not entries:
        record_skipped_plot(
            skipped,
            filename,
            "no ranked gaussian weight configurations available",
        )
        return

    weight_columns = [
        ("magic\nhigh", "magic_high"),
        ("magic\nlow", "magic_low"),
        ("CNOT\nhigh", "cnot_high"),
        ("CNOT\nlow", "cnot_low"),
        ("gauss\nmapped", "mapped_gaussian_weight"),
        ("gauss\nbase", "base_gaussian_weight"),
        ("external\nweight", "external_weight"),
    ]
    data = np.zeros((len(entries), len(weight_columns)), dtype=float)
    masked = np.zeros((len(entries), len(weight_columns)), dtype=bool)
    for row_idx, entry in enumerate(entries):
        for col_idx, (_, field) in enumerate(weight_columns):
            value = entry.get(field)
            if value is None:
                masked[row_idx, col_idx] = True
            else:
                data[row_idx, col_idx] = float(value)
    row_labels = [
        (
            f"{entry['circuit']} {entry['graph_x']}x{entry['graph_y']}"
            f"   r={format_number_label(entry['best_routing_steps'])}"
            f"   ties={entry['configs_tied_for_best_routing']}"
        )
        for entry in entries
    ]

    fig_height = max(11, 1.8 + len(entries) * 0.31)
    fig, ax = plt.subplots(figsize=(13.5, fig_height))
    fig.subplots_adjust(left=0.42, right=0.92, top=0.93, bottom=0.06)
    image = ax.imshow(np.ma.array(data, mask=masked), aspect="auto", cmap="YlGnBu")

    ax.set_title(
        "Best Gaussian Weight Profile per Circuit x Dimension",
        fontsize=15,
        pad=18,
    )
    ax.set_xticks(range(len(weight_columns)))
    ax.set_xticklabels([label for label, _ in weight_columns], fontsize=9)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(entries)))
    ax.set_yticklabels(row_labels, fontsize=7.2)
    ax.tick_params(axis="both", length=0)
    ax.tick_params(axis="x", labeltop=True, labelbottom=False, pad=8)
    ax.set_xticks(np.arange(-0.5, len(weight_columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(entries), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)

    norm = image.norm
    for row_idx, entry in enumerate(entries):
        for col_idx, (_, field) in enumerate(weight_columns):
            value = entry.get(field)
            if value is None:
                ax.text(
                    col_idx,
                    row_idx,
                    "—",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="#475569",
                )
                continue
            value = float(value)
            text_color = "white" if norm(value) > 0.58 else "#0F172A"
            ax.text(
                col_idx,
                row_idx,
                format_number_label(value),
                ha="center",
                va="center",
                fontsize=8,
                color=text_color,
                fontweight="bold",
            )

    for row_idx in range(1, len(entries)):
        if entries[row_idx]["circuit"] != entries[row_idx - 1]["circuit"]:
            ax.axhline(row_idx - 0.5, color="#0F172A", linewidth=1.1)

    cbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label("weight value", fontsize=9)

    save_fig(fig, output_dir, filename, generated)


def gaussian_weight_value_count_entries(best_profile_entries):
    weight_columns = [
        ("magic high", "magic_high"),
        ("magic low", "magic_low"),
        ("CNOT high", "cnot_high"),
        ("CNOT low", "cnot_low"),
        ("gauss mapped", "mapped_gaussian_weight"),
        ("gauss base", "base_gaussian_weight"),
        ("external weight", "external_weight"),
    ]
    values = sorted(
        {
            float(entry[field])
            for entry in best_profile_entries
            for _, field in weight_columns
            if entry.get(field) is not None
        }
    )
    counts = Counter()
    for entry in best_profile_entries:
        for label, field in weight_columns:
            if entry.get(field) is None:
                continue
            counts[(label, float(entry[field]))] += 1

    total = len(best_profile_entries)
    entries = []
    for label, field in weight_columns:
        for value in values:
            count = counts[(label, value)]
            entries.append(
                {
                    "weight_parameter": label,
                    "weight_value": value,
                    "best_count": count,
                    "best_percentage": (100.0 * count / total) if total else 0.0,
                }
            )
    return entries


def write_gaussian_weight_value_count_table(entries, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, filename)
    fieldnames = [
        "weight_parameter",
        "weight_value",
        "best_count",
        "best_percentage",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    return entries, csv_path


def plot_gaussian_weight_value_count_heatmap(entries, output_dir, generated, skipped=None):
    filename = "31_heatmap_best_gaussian_weight_value_counts.png"
    if not entries:
        record_skipped_plot(
            skipped,
            filename,
            "no best gaussian weight profile rows available",
        )
        return

    row_labels = []
    for entry in entries:
        label = entry["weight_parameter"]
        if label not in row_labels:
            row_labels.append(label)

    values = sorted({float(entry["weight_value"]) for entry in entries})
    counts_by_pair = {
        (entry["weight_parameter"], float(entry["weight_value"])): int(entry["best_count"])
        for entry in entries
    }
    matrix = np.array(
        [
            [counts_by_pair.get((label, value), 0) for value in values]
            for label in row_labels
        ],
        dtype=float,
    )

    fig_width = max(9, 1.1 + len(values) * 0.62)
    fig, ax = plt.subplots(figsize=(fig_width, 4.8))
    fig.subplots_adjust(left=0.18, right=0.92, top=0.82, bottom=0.16)
    image = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", vmin=0)
    total_profiles = int(np.max(np.sum(matrix, axis=1))) if matrix.size else 0

    ax.set_title(
        f"How Often Each Gaussian Weight Value Is Best (n={total_profiles})",
        fontsize=14,
        pad=18,
    )
    ax.set_xlabel("weight value")
    ax.set_ylabel("weight parameter")
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels([format_number_label(value) for value in values], fontsize=9)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=9)
    ax.set_xticks(np.arange(-0.5, len(values), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(row_labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.3)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(axis="both", length=0)

    max_count = float(np.max(matrix)) if matrix.size else 0.0
    for row_idx, label in enumerate(row_labels):
        for col_idx, value in enumerate(values):
            count = counts_by_pair.get((label, value), 0)
            if count == 0:
                display = ""
                text_color = "#64748B"
            else:
                display = str(count)
                text_color = "white" if max_count and count / max_count > 0.55 else "#0F172A"
            ax.text(
                col_idx,
                row_idx,
                display,
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                fontweight="bold" if count else "normal",
            )

    cbar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.025)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label("best count", fontsize=9)

    save_fig(fig, output_dir, filename, generated)


def gaussian_relative_weight_gap_entries(best_profile_entries):
    weight_columns = [
        ("magic high", "magic_high"),
        ("magic low", "magic_low"),
        ("CNOT high", "cnot_high"),
        ("CNOT low", "cnot_low"),
        ("gauss mapped", "mapped_gaussian_weight"),
        ("gauss base", "base_gaussian_weight"),
        ("external weight", "external_weight"),
    ]
    entries = []

    for row_label, row_field in weight_columns:
        for col_label, col_field in weight_columns:
            gaps = [
                float(entry[row_field]) - float(entry[col_field])
                for entry in best_profile_entries
                if entry.get(row_field) is not None and entry.get(col_field) is not None
            ]
            abs_gaps = [abs(gap) for gap in gaps]
            total = len(gaps)
            row_greater = sum(1 for gap in gaps if gap > 0)
            row_less = sum(1 for gap in gaps if gap < 0)
            equal = sum(1 for gap in gaps if gap == 0)
            entries.append(
                {
                    "row_weight_parameter": row_label,
                    "column_weight_parameter": col_label,
                    "mean_signed_gap": float(np.mean(gaps)) if gaps else 0.0,
                    "median_signed_gap": statistics.median(gaps) if gaps else 0.0,
                    "mean_abs_gap": float(np.mean(abs_gaps)) if abs_gaps else 0.0,
                    "median_abs_gap": statistics.median(abs_gaps) if abs_gaps else 0.0,
                    "row_greater_count": row_greater,
                    "row_less_count": row_less,
                    "equal_count": equal,
                    "row_greater_percentage": (100.0 * row_greater / total) if total else 0.0,
                }
            )

    return entries


def write_gaussian_relative_weight_gap_table(entries, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, filename)
    fieldnames = [
        "row_weight_parameter",
        "column_weight_parameter",
        "mean_signed_gap",
        "median_signed_gap",
        "mean_abs_gap",
        "median_abs_gap",
        "row_greater_count",
        "row_less_count",
        "equal_count",
        "row_greater_percentage",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

    return entries, csv_path


def plot_gaussian_relative_weight_gap_heatmap(
    entries, output_dir, generated, skipped=None, filename=None, slice_label=None
):
    if filename is None:
        filename = GAUSSIAN_RELATIVE_GAP_PLOT
    if not entries:
        record_skipped_plot(
            skipped,
            filename,
            f"no best gaussian weight profile rows available"
            + (f" for {slice_label}" if slice_label else ""),
        )
        return

    labels = []
    for entry in entries:
        label = entry["row_weight_parameter"]
        if label not in labels:
            labels.append(label)

    by_pair = {
        (entry["row_weight_parameter"], entry["column_weight_parameter"]): entry
        for entry in entries
    }
    signed = np.array(
        [
            [by_pair[(row_label, col_label)]["mean_signed_gap"] for col_label in labels]
            for row_label in labels
        ],
        dtype=float,
    )
    total_profiles = max(
        [
            by_pair[(label, label)]["equal_count"]
            for label in labels
        ],
        default=0,
    )

    fig, ax = plt.subplots(figsize=(7.5, 6.8), constrained_layout=False)
    fig.subplots_adjust(left=0.16, right=0.9, top=0.76, bottom=0.17)
    title = "Relative Distances Between Weights in Best Gaussian Configurations"
    if slice_label:
        title += f"\n{slice_label}"
    title += f" (n={total_profiles})"
    fig.suptitle(
        title,
        fontsize=15,
        y=0.96,
    )
    fig.text(
        0.5,
        0.88,
        "Each cell compares the row weight with the column weight. The absolute values of the weights are not counted.",
        ha="center",
        va="center",
        fontsize=9,
        color="#475569",
    )

    max_signed = float(np.max(np.abs(signed))) if signed.size else 1.0
    signed_norm = TwoSlopeNorm(vmin=-max_signed, vcenter=0, vmax=max_signed)
    image = ax.imshow(signed, cmap="RdBu_r", norm=signed_norm)

    ax.set_title("Mean Signed Gap", fontsize=12, pad=12)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.25)
    ax.tick_params(axis="both", length=0)
    ax.tick_params(which="minor", bottom=False, left=False)

    max_value = float(np.max(np.abs(signed))) if signed.size else 0.0
    for row_idx in range(signed.shape[0]):
        for col_idx in range(signed.shape[1]):
            value = signed[row_idx, col_idx]
            if row_idx == col_idx:
                text = "-"
                color = "#64748B"
            else:
                text = f"{value:+.2f}"
                color = "white" if max_value and abs(value) / max_value > 0.55 else "#0F172A"
            ax.text(
                col_idx,
                row_idx,
                text,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold" if row_idx != col_idx else "normal",
                color=color,
            )

    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.035)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label("row - column", fontsize=9)

    path = os.path.join(output_dir, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.25)
    fig.clf()
    plt.close(fig)
    generated.append(path)


def gaussian_gap_value_slug(value):
    text = re.sub(r"[^a-z0-9]+", "_", normalize_text(str(value)).lower()).strip("_")
    return text or "unknown"


# Weight fields displayed (in order) by the gaussian-weights summary dashboard.
_GAUSSIAN_SUMMARY_WEIGHT_FIELDS = (
    ("magic\nhigh", "magic_high"),
    ("magic\nlow", "magic_low"),
    ("CNOT\nhigh", "cnot_high"),
    ("CNOT\nlow", "cnot_low"),
    ("gauss\nmapped", "mapped_gaussian_weight"),
    ("gauss\nbase", "base_gaussian_weight"),
    ("external\nweight", "external_weight"),
)


def _gaussian_best_profile_by_metric(rows, metric_field):
    """For each (circuit, graph_x, graph_y), pick the gaussian-weight config that
    minimizes metric_field (success rows only), with tie-break on mean(metric),
    duration, combo. Returns list of dicts with the weight values per group."""
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if row.get("mapping_type_norm") != "gaussian":
            continue
        if not row.get("success") or row.get(metric_field) is None:
            continue
        x_key = requested_x_key(row)
        combo = gaussian_weight_tuple(row)
        if x_key is None or combo is None:
            continue
        grouped[x_key][combo].append(row)

    best_entries = []
    for x_key in sorted(grouped.keys(), key=lambda item: (item[0], item[1], item[2])):
        config_metrics = []
        for combo, config_rows in grouped[x_key].items():
            metric_values = [r[metric_field] for r in config_rows]
            best_metric = min(metric_values)
            best_rows_subset = [r for r in config_rows if r.get(metric_field) == best_metric]
            best_duration_values = [
                r["duration_s_f"] for r in best_rows_subset if r.get("duration_s_f") is not None
            ]
            config_metrics.append({
                "combo": combo,
                "best_metric": best_metric,
                "mean_metric": float(np.mean(metric_values)),
                "best_duration_seconds": min(best_duration_values) if best_duration_values else None,
            })
        if not config_metrics:
            continue
        config_metrics.sort(key=lambda item: (
            item["best_metric"],
            item["mean_metric"],
            item["best_duration_seconds"] if item["best_duration_seconds"] is not None else math.inf,
            gaussian_weight_sort_key(item["combo"]),
        ))
        magic_high, magic_low, cnot_high, cnot_low, mapped_weight, base_weight, external_weight = config_metrics[0]["combo"]
        best_entries.append({
            "magic_high": magic_high,
            "magic_low": magic_low,
            "cnot_high": cnot_high,
            "cnot_low": cnot_low,
            "mapped_gaussian_weight": mapped_weight,
            "base_gaussian_weight": base_weight,
            "external_weight": external_weight,
        })
    return best_entries


def _gaussian_weight_profile_means_normalized(rows_subset, metric_field="routing_steps_f"):
    """For a row subset: compute the per-best-config means of the weights,
    then normalize so gauss_base == 1.0. Best config is the one minimizing
    metric_field per (circuit, x, y). Returns (sample_count, dict[field] -> float)
    or (0, None) if no usable best entries exist."""
    best_entries = _gaussian_best_profile_by_metric(rows_subset, metric_field)
    if not best_entries:
        return 0, None
    means = {}
    for _, field in _GAUSSIAN_SUMMARY_WEIGHT_FIELDS:
        vals = [float(e[field]) for e in best_entries if e.get(field) is not None]
        means[field] = float(np.mean(vals)) if vals else None
    base = means.get("base_gaussian_weight")
    if base is None:
        return len(best_entries), None
    normalized = {
        field: (means[field] - base + 1.0) if means[field] is not None else None
        for _, field in _GAUSSIAN_SUMMARY_WEIGHT_FIELDS
    }
    return len(best_entries), normalized


def _plot_gaussian_weight_summary_for_metric(
    rows, output_dir, generated, skipped, metric_field, filename, title_suffix
):
    """Render one summary heatmap; rows = OVERALL + per-dimension slices; cells
    are mean weight value with gauss_base normalized to 1, where 'best' for each
    (circuit, x, y) is chosen by minimizing metric_field."""
    sections = []  # list of (group_label_or_None, row_label, sample_count, values_dict)

    overall_count, overall_vals = _gaussian_weight_profile_means_normalized(rows, metric_field)
    if overall_vals is not None:
        sections.append((None, "OVERALL", overall_count, overall_vals))

    for field, display_name, _slug in GAUSSIAN_GAP_BREAKDOWN_DIMENSIONS:
        values = sorted(
            {
                row.get(field)
                for row in rows
                if row.get("mapping_type_norm") == "gaussian"
                and row.get(field) not in (None, "")
            },
            key=str,
        )
        first_in_group = True
        for value in values:
            subset = [r for r in rows if r.get(field) == value]
            cnt, vals = _gaussian_weight_profile_means_normalized(subset, metric_field)
            if vals is None:
                continue
            sections.append((display_name if first_in_group else "", f"{display_name} = {value}", cnt, vals))
            first_in_group = False

    if not sections:
        record_skipped_plot(skipped, filename, "no gaussian best entries available")
        return

    n_rows = len(sections)
    n_cols = len(_GAUSSIAN_SUMMARY_WEIGHT_FIELDS)
    data = np.zeros((n_rows, n_cols), dtype=float)
    masked = np.zeros((n_rows, n_cols), dtype=bool)
    row_labels = []
    for i, (_group, row_label, sample_count, vals) in enumerate(sections):
        row_labels.append(f"{row_label}   (n={sample_count})")
        for j, (_, field) in enumerate(_GAUSSIAN_SUMMARY_WEIGHT_FIELDS):
            v = vals.get(field)
            if v is None:
                masked[i, j] = True
            else:
                data[i, j] = v

    if (~masked).any():
        observed_min = float(np.min(data[~masked]))
        observed_max = float(np.max(data[~masked]))
    else:
        observed_min, observed_max = 0.5, 1.5
    span = max(abs(observed_max - 1.0), abs(1.0 - observed_min), 0.1)
    vmin, vmax = 1.0 - span, 1.0 + span
    norm = TwoSlopeNorm(vmin=vmin, vcenter=1.0, vmax=vmax)

    fig_height = max(5.0, 0.42 * n_rows + 2.4)
    fig, ax = plt.subplots(figsize=(12.8, fig_height))
    masked_data = np.ma.array(data, mask=masked)
    image = ax.imshow(masked_data, aspect="auto", cmap="RdBu_r", norm=norm)

    ax.set_title(
        f"Best Gaussian Weights Summary — {title_suffix} (gauss_base = 1)",
        fontsize=14, pad=14,
    )
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels([lbl for lbl, _ in _GAUSSIAN_SUMMARY_WEIGHT_FIELDS], fontsize=10)
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", labeltop=True, labelbottom=False, pad=6)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=9)
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(axis="both", length=0)

    for i in range(n_rows):
        for j in range(n_cols):
            if masked[i, j]:
                ax.text(j, i, "—", ha="center", va="center", fontsize=9, color="#475569")
                continue
            v = data[i, j]
            text_color = "white" if (norm(v) > 0.78 or norm(v) < 0.22) else "#0F172A"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9,
                    color=text_color, fontweight="bold")

    for i, (group, _row_label, _cnt, _vals) in enumerate(sections):
        if i == 0:
            continue
        if group is None:
            continue
        if group != "":
            ax.axhline(i - 0.5, color="#0F172A", linewidth=1.1)

    cbar = fig.colorbar(image, ax=ax, fraction=0.04, pad=0.02)
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label("value (gauss_base = 1)", fontsize=9)

    save_fig(fig, output_dir, filename, generated, subfolder=GAUSSIAN_DIR)


def plot_gaussian_weight_summary_dashboard(rows, output_dir, generated, skipped=None):
    """Generate the two gaussian-weight summary heatmaps: one optimizing for
    routing_steps, one for non_routed_layer_pct. Both go under GAUSSIAN_DIR/."""
    target_dir = os.path.join(output_dir, GAUSSIAN_DIR)
    clear_plot_tree(target_dir, "gaussian weight summary")
    _plot_gaussian_weight_summary_for_metric(
        rows, output_dir, generated, skipped,
        metric_field="routing_steps_f",
        filename="gaussian_weight_summary_by_routing.png",
        title_suffix="by routing_steps",
    )
    _plot_gaussian_weight_summary_for_metric(
        rows, output_dir, generated, skipped,
        metric_field="non_routed_layer_pct_f",
        filename="gaussian_weight_summary_by_non_routed.png",
        title_suffix="by non_routed_layer_pct",
    )


def plot_gaussian_relative_weight_gap_breakdown(rows, output_dir, generated, skipped=None, batch_size=50):
    target_dir = os.path.join(output_dir, GAUSSIAN_DIR)
    clear_plot_tree(target_dir, "gaussian relative weight gap")

    # Build the full task list first so we can batch + report progress like
    # plot_axis_barplots_by_circuit does (and trim the heap between batches).
    tasks = []
    for field, display_name, dim_slug in GAUSSIAN_GAP_BREAKDOWN_DIMENSIONS:
        values = sorted(
            {
                row.get(field)
                for row in rows
                if row.get("mapping_type_norm") == "gaussian"
                and row.get(field) not in (None, "")
            },
            key=str,
        )
        for value in values:
            value_slug = gaussian_gap_value_slug(value)
            filename = os.path.join(
                dim_slug,
                f"heatmap_best_gaussian_relative_weight_gaps_{dim_slug}_{value_slug}.png",
            )
            tasks.append((field, display_name, value, filename))

    total = len(tasks)
    if not total:
        return
    batches = [(s, min(s + batch_size, total)) for s in range(0, total, batch_size)]
    print(
        f"Generating {total} gaussian-gap breakdown plots in {len(batches)} batches of up to {batch_size}",
        flush=True,
    )
    for batch_idx, (start, end) in enumerate(batches, 1):
        for field, display_name, value, filename in tasks[start:end]:
            slice_rows = [r for r in rows if r.get(field) == value]
            top_entries, _ = top_gaussian_weight_config_entries(slice_rows, top_n=3)
            best_entries = best_gaussian_weight_profile_entries(top_entries)
            gap_entries = gaussian_relative_weight_gap_entries(best_entries)
            del slice_rows, top_entries, best_entries
            plot_gaussian_relative_weight_gap_heatmap(
                gap_entries,
                target_dir,
                generated,
                skipped,
                filename=filename,
                slice_label=f"{display_name} = {value}",
            )
        _trim_heap()
        print(f"[gaussian-gap batch {batch_idx}/{len(batches)}] items {start}:{end} done", flush=True)


def plot_top_gaussian_weight_config_table(grouped_ranked_entries, output_dir, generated, skipped=None):
    filename = "28_table_top_gaussian_weight_configs.png"
    if not grouped_ranked_entries:
        record_skipped_plot(
            skipped,
            filename,
            "no gaussian successful rows with complete weight configurations",
        )
        return

    headers = ["circuit x dim", "best\nrouting", "# cfg\nsame best", "1st config", "2nd config", "3rd config"]
    table_rows = []
    for group in grouped_ranked_entries:
        cells = [
            group["label"],
            format_number_label(group["best_routing_steps"]),
            str(group["configs_tied_for_best_routing"]),
        ]
        for entry in group["entries"][:3]:
            cell = (
                f"routing {format_number_label(entry['best_routing_steps'])}"
                f" (avg {entry['mean_routing_steps']:.1f}, n={entry['sample_count']})\n"
                f"{gaussian_weight_config_label((entry['magic_high'], entry['magic_low'], entry['cnot_high'], entry['cnot_low'], entry['mapped_gaussian_weight'], entry['base_gaussian_weight'], entry.get('external_weight')), multiline=True, verbose=True)}"
            )
            cells.append(cell)
        while len(cells) < len(headers):
            cells.append("")
        table_rows.append(cells)

    fig_height = max(9, 1.0 + len(table_rows) * 0.43)
    fig, ax = plt.subplots(figsize=(22, fig_height))
    fig.subplots_adjust(top=0.90, bottom=0.02, left=0.01, right=0.99)
    ax.axis("off")
    fig.suptitle(
        "Top Gaussian Weight Configurations by Circuit x Graph Dimensions",
        fontsize=15,
        y=0.985,
    )
    table = ax.table(
        cellText=table_rows,
        colLabels=headers,
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.22, 0.06, 0.08, 0.21, 0.21, 0.21],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1.0, 2.25)

    for (row_idx, col_idx), cell in table.get_celld().items():
        cell.set_edgecolor("#CBD5E1")
        cell.set_linewidth(0.55)
        if row_idx == 0:
            cell.set_facecolor("#E2E8F0")
            cell.set_text_props(weight="bold", color="#0F172A")
            continue
        cell.set_facecolor("#F8FAFC" if row_idx % 2 == 0 else "white")
        if col_idx in {1, 2}:
            cell.set_text_props(ha="center")

    save_fig(fig, output_dir, filename, generated)


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
    count_by_pair = {}
    for key, values in grouped.items():
        mean_by_pair[key] = float(np.mean(values))
        count_by_pair[key] = len(values)

    return x_keys_sorted, x_labels, mean_by_pair, count_by_pair


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
    skipped=None,
):
    aggregated = aggregate_series_values(rows, build_series_key)
    if not aggregated[0]:
        record_skipped_plot(
            skipped,
            filename,
            "no successful rows with routing_steps matched the requested mapping/safe-passage/placement filters",
        )
        return

    x_keys_sorted, x_labels, mean_by_pair, count_by_pair = aggregated
    available_series = [
        series_key
        for series_key in series_order
        if any((x_key, series_key) in mean_by_pair for x_key in x_keys_sorted)
    ]
    if not available_series:
        record_skipped_plot(
            skipped,
            filename,
            "requested series were defined, but none have plottable routing_steps values",
        )
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
        x_keys_masked = [x_key for x_key, keep in zip(x_keys_sorted, mask) if keep]
        for x_pos, y_val, x_key in zip(x_positions[mask], y_values[mask], x_keys_masked):
            sample_count = count_by_pair.get((x_key, series_key), 0)
            ax.annotate(
                f"n={sample_count}",
                (x_pos, y_val),
                textcoords="offset points",
                xytext=(0, 4),
                ha="center",
                va="bottom",
                fontsize=5,
                color=color,
                alpha=0.85,
                zorder=4,
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


def plot_requested_comparisons(rows_success_with_routing, output_dir, generated, skipped=None):
    plot_requested_grouped_scatter(
        rows_success_with_routing,
        build_series_key_requested_gaussian_vs_homogeneous,
        requested_series_order_gaussian_vs_homogeneous(),
        "Routing Steps by circuit-graph_dimensions: gaussian coarse/fine + homogeneous",
        "17_experiment_set_routing_gaussian_homogeneous.png",
        output_dir,
        generated,
        skipped,
    )
    plot_requested_grouped_scatter(
        rows_success_with_routing,
        build_series_key_requested_magicaware_vs_homogeneous,
        requested_series_order_magicaware_vs_homogeneous(),
        "Routing Steps by circuit-graph_dimensions: magic-aware center/distance/random + homogeneous",
        "18_experiment_set_routing_magicaware_homogeneous.png",
        output_dir,
        generated,
        skipped,
    )
    plot_requested_grouped_scatter(
        rows_success_with_routing,
        build_series_key_requested_all_mappings,
        requested_series_order_all_mappings(),
        "Routing Steps by circuit-graph_dimensions: homogeneous + gaussian + magic-aware",
        "22_experiment_set_routing_all_mappings.png",
        output_dir,
        generated,
        skipped,
    )


def make_pair_heatmap(
    rows,
    row_key,
    col_key,
    value_fn,
    value_label_suffix,
    title,
    colorbar_label,
    filename,
    output_dir,
    generated,
    skipped=None,
    value_format="{:.2f}",
    subset_transform=None,
    subfolder=None,
    removed_counts=None,
):
    row_labels = sorted(
        {heatmap_axis_value(r, row_key) for r in rows},
        key=lambda label: heatmap_axis_sort_key(row_key, label),
    )
    col_labels = sorted(
        {heatmap_axis_value(r, col_key) for r in rows},
        key=lambda label: heatmap_axis_sort_key(col_key, label),
    )
    if not row_labels or not col_labels:
        save_empty_plot(
            title,
            output_dir,
            filename,
            generated,
            message=f"No data for {row_key} x {col_key}",
            subfolder=subfolder,
            dpi=DASHBOARD_SOURCE_PLOT_DPI,
        )
        return

    matrix = np.full((len(row_labels), len(col_labels)), np.nan, dtype=float)
    count_matrix = np.zeros((len(row_labels), len(col_labels)), dtype=int)
    row_index = {k: i for i, k in enumerate(row_labels)}
    col_index = {k: j for j, k in enumerate(col_labels)}

    grouped = defaultdict(list)
    for r in rows:
        grouped[(heatmap_axis_value(r, row_key), heatmap_axis_value(r, col_key))].append(r)

    for (rk, ck), subset in grouped.items():
        metric_subset = subset_transform(subset) if subset_transform is not None else subset
        val = value_fn(metric_subset)
        count_matrix[row_index[rk], col_index[ck]] = len(metric_subset)
        if val is None:
            continue
        matrix[row_index[rk], col_index[ck]] = val

    fig, ax = plt.subplots(figsize=(max(7, len(col_labels) * 1.15), max(5, len(row_labels) * 0.9)))
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
            sample_count = count_matrix[i, j]
            metric_text = "-" if np.isnan(val) else value_format.format(val)
            rk = row_labels[i]
            ck = col_labels[j]
            removed = removed_counts.get((rk, ck), 0) if removed_counts else 0
            removed_text = f"\n(-{removed})" if removed > 0 else ""
            if value_label_suffix:
                text = f"{metric_text}\n{value_label_suffix}\nn={sample_count}{removed_text}"
            else:
                text = f"{metric_text}\nn={sample_count}{removed_text}"
            if np.isnan(val):
                color = "#999999"
            else:
                red, green, blue, _ = im.cmap(im.norm(val))
                luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
                color = "white" if luminance < 0.45 else "#111111"
            ax.text(j, i, text, ha="center", va="center", color=color, fontsize=7, linespacing=0.9)

    save_fig(fig, output_dir, filename, generated, dpi=DASHBOARD_SOURCE_PLOT_DPI, subfolder=subfolder)


def heatmap_metric_display_label(metric, sample_scope=None):
    metric_titles = {
        "success_rate": "success rate",
        "routing_steps": "routing steps",
        "execution_time": "execution time",
        "non_routed_layer_pct": "non-routed layer %",
    }
    label = metric_titles.get(metric, str(metric))
    if sample_scope:
        return f"{label}\n({sample_scope})"
    return label


def dashboard_panel_title(item, mode="metric"):
    if item.get("kind") == "heatmap":
        metric_label = heatmap_metric_display_label(
            item.get("metric"),
            item.get("sample_scope"),
        )
        if mode == "axis_and_metric":
            return f"{item.get('row_label', item.get('row_key', 'axis'))}\n{metric_label}"
        return metric_label
    return item.get("title") or item.get("caption") or item["filename"]


def dashboard_font(ImageFont, size, bold=False):
    font_names = (
        ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        if bold
        else ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    )
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def centered_multiline_text(draw, xy, text, font, fill):
    x, y, width = xy
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=4, align="center")
    text_width = bbox[2] - bbox[0]
    draw.multiline_text(
        (x + (width - text_width) / 2, y),
        text,
        font=font,
        fill=fill,
        spacing=4,
        align="center",
    )


def plot_image_dashboard(
    source_items,
    title,
    filename,
    output_dir,
    generated,
    skipped=None,
    columns=3,
    panel_title_mode="metric",
    panel_width=6.2,
    panel_height=5.3,
    dpi=DASHBOARD_OUTPUT_DPI,
    subfolder=None,
):
    from PIL import Image, ImageDraw, ImageFont

    if not source_items:
        save_empty_plot(
            title,
            output_dir,
            filename,
            generated,
            message="No source plots",
            subfolder=subfolder,
            dpi=dpi,
        )
        return

    skipped_by_name = {
        item["filename"]: item["reason"]
        for item in (skipped or [])
    }
    source_panels = []
    for item in source_items:
        source_subfolder = item.get("subfolder")
        in_heatmap = source_subfolder and (source_subfolder == HEATMAP_DIR or source_subfolder.startswith(HEATMAP_DIR + os.sep))
        source_name = item["filename"] if in_heatmap else strip_plot_number(item["filename"])
        source_path = (
            os.path.join(output_dir, source_subfolder, source_name)
            if source_subfolder
            else os.path.join(output_dir, source_name)
        )
        if os.path.isfile(source_path):
            source_panels.append((item, source_path, None))
        else:
            reason = skipped_by_name.get(item["filename"], "source plot was not generated")
            source_panels.append((item, None, reason))

    columns = max(1, min(columns, len(source_panels)))
    row_count = int(math.ceil(len(source_panels) / columns))
    panel_pixel_width = int(max(900, panel_width * dpi))
    placeholder_height = int(panel_pixel_width * 0.72)
    title_height = 74
    outer_pad = 34
    gap = 28
    header_height = 92
    resampling = getattr(Image, "Resampling", Image).LANCZOS

    # Pass 1: collect panel metadata (title, path, missing_reason, pixel height)
    # without keeping any images in memory.
    panel_meta = []
    for item, source_path, missing_reason in source_panels:
        panel_title = dashboard_panel_title(item, panel_title_mode)
        if source_path is None:
            panel_meta.append((panel_title, None, missing_reason, placeholder_height))
            continue
        with Image.open(source_path) as img:
            orig_w, orig_h = img.size
        scale = panel_pixel_width / orig_w
        target_height = max(1, int(round(orig_h * scale)))
        panel_meta.append((panel_title, source_path, None, target_height))

    row_heights = []
    for row_index in range(row_count):
        start = row_index * columns
        end = min(start + columns, len(panel_meta))
        row_heights.append(title_height + max(m[3] for m in panel_meta[start:end]))

    canvas_width = outer_pad * 2 + columns * panel_pixel_width + (columns - 1) * gap
    canvas_height = outer_pad * 2 + header_height + sum(row_heights) + (row_count - 1) * gap
    canvas = Image.new("RGBA", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    header_font = dashboard_font(ImageFont, 38, bold=True)
    panel_font = dashboard_font(ImageFont, 24, bold=True)
    small_font = dashboard_font(ImageFont, 22)

    centered_multiline_text(
        draw,
        (outer_pad, outer_pad, canvas_width - outer_pad * 2),
        title,
        header_font,
        "#111827",
    )

    # Pass 2: load one panel at a time, composite, immediately free.
    y = outer_pad + header_height
    for row_index, row_height in enumerate(row_heights):
        for col_index in range(columns):
            panel_index = row_index * columns + col_index
            if panel_index >= len(panel_meta):
                continue

            panel_title, source_path, missing_reason, image_height = panel_meta[panel_index]
            x = outer_pad + col_index * (panel_pixel_width + gap)
            centered_multiline_text(draw, (x, y, panel_pixel_width), panel_title, panel_font, "#111827")
            image_y = y + title_height
            if source_path is None:
                bottom = image_y + image_height
                draw.rectangle(
                    (x, image_y, x + panel_pixel_width, bottom),
                    fill="#F8FAFC",
                    outline="#CBD5E1",
                    width=2,
                )
                centered_multiline_text(
                    draw,
                    (x + 20, image_y + image_height / 2 - 34, panel_pixel_width - 40),
                    f"Skipped\n{missing_reason}",
                    small_font,
                    "#64748B",
                )
            else:
                with Image.open(source_path) as original:
                    img_rgba = original.convert("RGBA")
                resized = img_rgba.resize((panel_pixel_width, image_height), resampling)
                img_rgba.close()
                del img_rgba
                canvas.alpha_composite(resized, (x, image_y))
                resized.close()
                del resized

        y += row_height + gap

    target_dir = os.path.join(output_dir, subfolder) if subfolder else output_dir
    os.makedirs(target_dir, exist_ok=True)
    in_heatmap = subfolder and (subfolder == HEATMAP_DIR or subfolder.startswith(HEATMAP_DIR + os.sep))
    disk_name = filename if in_heatmap else strip_plot_number(filename)
    path = os.path.join(target_dir, disk_name)
    canvas.convert("RGB").save(path, "PNG", optimize=True)
    canvas.close()
    del canvas
    generated.append(path)


def axis_boxplot_values(rows, metric):
    if metric == "success_rate":
        return [100.0 if row["success"] else 0.0 for row in rows]
    if metric == "routing_steps":
        return non_empty([row["routing_steps_f"] for row in rows])
    if metric == "execution_time":
        return non_empty([row["duration_s_f"] for row in rows])
    if metric == "non_routed_layer_pct":
        return non_empty([row["non_routed_layer_pct_f"] for row in rows])
    raise ValueError(f"Unknown axis boxplot metric: {metric}")


def axis_mean_label(metric, mean_value, value_format):
    text = value_format.format(mean_value)
    if metric == "success_rate":
        text = f"{text}%"
    elif metric == "execution_time":
        text = f"{text}s"
    return f"mean={text}"


def axis_metric_value_text(metric, value, value_format):
    text = value_format.format(value)
    if metric == "success_rate":
        return f"{text}%"
    if metric == "execution_time":
        return f"{text}s"
    return text


def boxplot_non_outlier_values(values):
    if not values:
        return []
    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    visible = [value for value in values if lower_bound <= value <= upper_bound]
    return visible or values


def boxplot_whisker_limits(value_groups):
    lows = []
    highs = []
    for values in value_groups:
        if not values:
            continue
        visible = boxplot_non_outlier_values(values)
        lows.append(min(visible))
        highs.append(max(visible))

    if not lows or not highs:
        return 0.0, 1.0

    y_min = min(lows)
    y_max = max(highs)
    y_span = y_max - y_min
    if abs(y_span) < 1e-9:
        y_span = max(1.0, abs(y_max) * 0.15)
    return min(0.0, y_min - y_span * 0.08), y_max + y_span * 0.18


def plot_axis_barplot(
    rows,
    axis_key,
    metric,
    title,
    ylabel,
    filename,
    output_dir,
    generated,
    skipped=None,
    value_format="{:.2f}",
    color="#577590",
    subfolder=None,
    align=False,
):
    grouped = defaultdict(list)
    for row in rows:
        if not has_heatmap_axis_value(row, axis_key):
            continue
        grouped[heatmap_axis_value(row, axis_key)].append(row)

    removed_per_bar = {}
    if align and metric != "success_rate" and len(grouped) > 1:
        base_fields = heatmap_base_config_fields(axis_key, axis_key)
        bar_configs = {
            label: {
                tuple(heatmap_axis_value(r, f) for f in base_fields)
                for r in bar_rows
            }
            for label, bar_rows in grouped.items()
        }
        common = set.intersection(*bar_configs.values())
        for label, configs in bar_configs.items():
            removed_per_bar[label] = len(configs) - len(common)
        grouped = {
            label: [r for r in bar_rows if tuple(heatmap_axis_value(r, f) for f in base_fields) in common]
            for label, bar_rows in grouped.items()
        }

    labels = sorted(
        grouped.keys(),
        key=lambda label: heatmap_axis_sort_key(axis_key, label),
    )
    value_groups = []
    valid_labels = []
    for label in labels:
        values = axis_boxplot_values(grouped[label], metric)
        if not values:
            continue
        valid_labels.append(label)
        value_groups.append(values)

    if not valid_labels:
        save_empty_plot(
            title,
            output_dir,
            filename,
            generated,
            message=f"No data for {axis_key}",
            subfolder=subfolder,
            ylabel=ylabel,
            dpi=AXIS_BARPLOT_OUTPUT_DPI,
        )
        return

    display_labels = [
        label_with_sample_count(label, len(values))
        + (f"\n(-{removed_per_bar[label]})" if removed_per_bar.get(label, 0) > 0 else "")
        for label, values in zip(valid_labels, value_groups)
    ]
    means = [float(np.mean(values)) for values in value_groups]
    if metric == "success_rate":
        means_no_outliers = means
    else:
        means_no_outliers = [
            float(np.mean(boxplot_non_outlier_values(values)))
            for values in value_groups
        ]
    medians = [float(np.median(values)) for values in value_groups]

    fig, ax = plt.subplots(figsize=(max(10.5, len(valid_labels) * 2.05), 8.4))
    box = ax.boxplot(
        value_groups,
        tick_labels=display_labels,
        showfliers=False,
        showmeans=False,
        patch_artist=True,
        widths=0.5,
        boxprops={"facecolor": "white", "edgecolor": "black", "linewidth": 2.0},
        whiskerprops={"color": "black", "linewidth": 2.0},
        capprops={"color": "black", "linewidth": 2.0},
        medianprops={"color": "#FF7F0E", "linewidth": 2.4},
    )
    for patch in box["boxes"]:
        patch.set_facecolor("white")
        patch.set_edgecolor("black")

    if metric == "success_rate":
        y_min, y_max = -4.0, 112.0
    else:
        y_min, y_max = boxplot_whisker_limits(value_groups)
    ax.set_ylim(y_min, y_max)
    text_offset = (y_max - y_min) * 0.035
    any_mean_line = False
    any_mean_no_outliers_line = False

    for x_position, (mean_value, mean_no_outliers, median_value) in enumerate(
        zip(means, means_no_outliers, medians),
        start=1,
    ):
        raw_mean_is_distinct = not math.isclose(
            mean_value,
            mean_no_outliers,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
        mean_in_view = y_min <= mean_value <= y_max
        mean_no_outliers_in_view = y_min <= mean_no_outliers <= y_max
        if raw_mean_is_distinct and mean_in_view:
            ax.hlines(
                mean_value,
                x_position - 0.25,
                x_position + 0.25,
                color="#D62728",
                linewidth=2.6,
                linestyle="--",
                zorder=4,
            )
            any_mean_line = True
        elif raw_mean_is_distinct:
            mean_in_view = False

        if mean_no_outliers_in_view:
            ax.hlines(
                mean_no_outliers,
                x_position - 0.25,
                x_position + 0.25,
                color="#1F77B4",
                linewidth=2.4,
                linestyle=":",
                zorder=4,
            )
            any_mean_no_outliers_line = True

        median_label = axis_metric_value_text(metric, median_value, value_format)
        mean_no_outliers_label = axis_metric_value_text(metric, mean_no_outliers, value_format)
        summary_label = (
            f"median={median_label}\n"
            f"mean(no out)={mean_no_outliers_label}"
        )
        summary_y_anchor = max(
            median_value,
            mean_no_outliers if mean_no_outliers_in_view else median_value,
        )
        summary_y = min(summary_y_anchor + text_offset, y_max - text_offset * 0.4)
        ax.text(
            x_position,
            summary_y,
            summary_label,
            ha="center",
            va="bottom",
            fontsize=10,
            color="#111111",
            fontweight="bold",
            bbox={"facecolor": "white", "edgecolor": "#BBBBBB", "alpha": 0.9, "pad": 2.5},
        )

        if raw_mean_is_distinct and mean_in_view:
            mean_y = max(mean_value - text_offset * 1.25, y_min + text_offset * 0.5)
            ax.text(
                x_position,
                mean_y,
                axis_mean_label(metric, mean_value, value_format),
                ha="center",
                va="top",
                fontsize=8,
                color="#D62728",
            )
        elif raw_mean_is_distinct:
            ax.text(
                x_position,
                0.03,
                axis_mean_label(metric, mean_value, value_format),
                ha="center",
                va="bottom",
                fontsize=8,
                color="#D62728",
                fontweight="bold",
                transform=ax.get_xaxis_transform(),
                bbox={"facecolor": "white", "edgecolor": "#BBBBBB", "alpha": 0.9, "pad": 2.0},
            )

    ax.set_title(title, fontsize=18, pad=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.tick_params(axis="x", rotation=35, labelsize=12)
    ax.tick_params(axis="y", labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(True, axis="both", color="#CFCFCF", linewidth=1.15, alpha=0.85)
    legend_handles = []
    if any_mean_line:
        legend_handles.append(
            Line2D([0], [0], color="#D62728", linewidth=2.6, linestyle="--", label="mean")
        )
    if any_mean_no_outliers_line:
        legend_handles.append(
            Line2D([0], [0], color="#1F77B4", linewidth=2.4, linestyle=":", label="mean(no out)")
        )
    legend_handles.append(Line2D([0], [0], color="#FF7F0E", linewidth=2.4, label="median"))
    ax.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        frameon=True,
        fontsize=10,
    )

    save_fig(fig, output_dir, filename, generated, dpi=AXIS_BARPLOT_OUTPUT_DPI, subfolder=subfolder)


def heatmap_x_axis_slugs():
    return list(HEATMAP_X_AXIS_SLUGS)


def safe_filename_component(value, default="unknown"):
    text = str(value).strip()
    if not text:
        text = default
    text = os.path.basename(text)
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("._")
    return text or default


def plot_axis_barplots_by_circuit(
    rows,
    rows_success_with_routing,
    output_dir,
    generated,
    skipped=None,
    batch_size=50,
    align=False,
    axis_slugs=None,
):
    axis_slugs = set(axis_slugs or [])
    rows_success_with_duration = [
        row for row in rows if row["success"] and row["duration_s_f"] is not None
    ]
    rows_success_with_non_routed = [
        row for row in rows if row["success"] and row["non_routed_layer_pct_f"] is not None
    ]
    rows_by_metric = {
        "success_rate": rows,
        "routing_steps": rows_success_with_routing,
        "execution_time": rows_success_with_duration,
        "non_routed_layer_pct": rows_success_with_non_routed,
    }
    circuits = sorted({row["circuit_name"] for row in rows if row["circuit_name"]})

    tasks = []
    for axis_slug in heatmap_x_axis_slugs():
        if axis_slugs and axis_slug not in axis_slugs:
            continue
        axis_key, axis_label = HEATMAP_AXIS_SPECS[axis_slug]
        subfolder = os.path.join(PER_CIRCUIT_BARPLOT_DIR, heatmap_slug(axis_slug))
        for circuit in circuits:
            circuit_slug = safe_filename_component(circuit)
            for (
                metric_slug,
                metric_filename_part,
                caption_prefix,
                sample_scope,
                ylabel,
                value_format,
                color,
            ) in AXIS_BARPLOT_METRIC_SPECS:
                metric_rows = [
                    row for row in rows_by_metric[metric_slug]
                    if row.get("circuit_name") == circuit
                ]
                filename = (
                    f"barplot_{metric_filename_part}_by_"
                    f"{heatmap_slug(axis_slug)}_{circuit_slug}.png"
                )
                title = f"{caption_prefix} {axis_label} ({sample_scope}) - {circuit}"
                tasks.append(
                    (metric_rows, axis_key, metric_slug, title, ylabel,
                     filename, value_format, color, subfolder)
                )

    total = len(tasks)
    if not total:
        return
    batches = [(s, min(s + batch_size, total)) for s in range(0, total, batch_size)]
    print(
        f"Generating {total} per-circuit barplots in {len(batches)} batches of up to {batch_size}",
        flush=True,
    )
    for batch_idx, (start, end) in enumerate(batches, 1):
        for (
            metric_rows, axis_key, metric_slug, title, ylabel,
            filename, value_format, color, subfolder,
        ) in tasks[start:end]:
            plot_axis_barplot(
                metric_rows,
                axis_key,
                metric_slug,
                title,
                ylabel,
                filename,
                output_dir,
                generated,
                skipped,
                value_format=value_format,
                color=color,
                subfolder=subfolder,
                align=align,
            )
        _trim_heap()
        print(f"[barplot batch {batch_idx}/{len(batches)}] items {start}:{end} done", flush=True)


def mean_of(values):
    values = non_empty(values)
    if not values:
        return None
    return float(np.mean(values))


def median_of(values):
    values = non_empty(values)
    if not values:
        return None
    return float(np.median(values))


def success_rate(subset):
    if not subset:
        return None
    return 100.0 * (sum(1 for r in subset if r["success"]) / len(subset))


def timeout_count(subset):
    if not subset:
        return 0.0
    return float(sum(1 for row in subset if is_timeout(row)))


def heatmap_axis_value(row, key):
    value = row.get(key)
    if value is None:
        return "unknown"
    text = str(value).strip()
    return text or "unknown"


def heatmap_axis_sort_key(key, label):
    if key in {"magic_states_label", "gaussian_confidence_label", "x_i", "y_i", "graph_nodes"}:
        numeric = to_float(label)
        if numeric is not None:
            return (0, numeric, label)
    return (1, str(label))


def has_heatmap_axis_value(row, key):
    value = row.get(key)
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and text.lower() != "unknown"


def filter_heatmap_rows(rows, row_key, col_key):
    return [
        row
        for row in rows
        if has_heatmap_axis_value(row, row_key) and has_heatmap_axis_value(row, col_key)
    ]


def heatmap_base_config_fields(row_key, col_key):
    # A "configuration" is the set of independent sweep knobs (the candidate
    # heatmap axes) plus the circuit. Derived columns (e.g. grid size) are
    # intentionally excluded so they don't make otherwise-identical configs
    # look different across the two varied axes.
    identity = {field for field, _label in HEATMAP_AXIS_SPECS.values()}
    identity.add("circuit_name")
    return sorted(identity - {row_key, col_key})


def align_rows_to_common_configs(rows, row_key, col_key):
    # Keep only configurations present in *every* populated cell of the heatmap,
    # so all cells aggregate over the same set of base configs. Without this, a
    # config that fails (and is dropped) in one cell but survives in another
    # makes per-cell means/medians incomparable.
    # Returns (aligned_rows, removed_per_cell) where removed_per_cell maps
    # (row_val, col_val) -> number of configs dropped from that cell.
    base_fields = heatmap_base_config_fields(row_key, col_key)
    base_keys = [
        tuple(heatmap_axis_value(row, field) for field in base_fields)
        for row in rows
    ]
    cell_configs = defaultdict(set)
    for row, base_key in zip(rows, base_keys):
        cell = (heatmap_axis_value(row, row_key), heatmap_axis_value(row, col_key))
        cell_configs[cell].add(base_key)
    no_removed = {cell: 0 for cell in cell_configs}
    if len(cell_configs) <= 1:
        return rows, no_removed
    common = set.intersection(*cell_configs.values())
    if not common:
        return rows, no_removed
    aligned = [row for row, base_key in zip(rows, base_keys) if base_key in common]
    removed_per_cell = {cell: len(configs) - len(common) for cell, configs in cell_configs.items()}
    return aligned, removed_per_cell


def project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def add_candidate_path(paths, path):
    normalized = os.path.abspath(os.path.expanduser(path))
    if normalized not in paths:
        paths.append(normalized)


def resolve_qasm_path(circuit_value):
    circuit = normalize_csv_text(circuit_value)
    if not circuit:
        return None

    root = project_root()
    candidates = []
    add_candidate_path(candidates, circuit)
    if os.path.splitext(circuit)[1] == "":
        add_candidate_path(candidates, circuit + ".qasm")

    basename = os.path.basename(circuit)
    stem, ext = os.path.splitext(basename)
    qasm_filename = basename if ext else stem + ".qasm"
    qasm_stem = stem if ext else basename

    add_candidate_path(candidates, os.path.join(root, "qasms", qasm_filename))
    add_candidate_path(candidates, os.path.join(root, "universal_set_qasms", qasm_filename))
    add_candidate_path(
        candidates,
        os.path.join(root, "universal_set_qasms", f"{qasm_stem}_universal.qasm"),
    )

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def resolve_universal_qasm_path(circuit_value):
    circuit = normalize_csv_text(circuit_value)
    if not circuit:
        return None

    root = project_root()
    basename = os.path.basename(circuit)
    stem, ext = os.path.splitext(basename)
    qasm_filename = basename if ext else stem + ".qasm"
    qasm_stem = stem if ext else basename

    candidates = []
    add_candidate_path(candidates, os.path.join(root, "universal_set_qasms", f"{qasm_stem}_universal.qasm"))
    add_candidate_path(candidates, os.path.join(root, "universal_set_qasms", qasm_filename))

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def parse_qasm_qubits_and_gates(path):
    qubits = 0
    gates = 0
    in_gate_definition = False
    brace_depth = 0
    qreg_re = re.compile(r"^qreg\s+[A-Za-z_]\w*\s*\[\s*(\d+)\s*\]\s*;")
    operation_re = re.compile(r"^[A-Za-z_]\w*(?:\([^)]*\))?\s+[^;]+;")

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.split("//", 1)[0].strip()
            if not line:
                continue

            if in_gate_definition:
                brace_depth += line.count("{") - line.count("}")
                if brace_depth <= 0:
                    in_gate_definition = False
                    brace_depth = 0
                continue

            if re.match(r"^gate\b", line):
                brace_depth = line.count("{") - line.count("}")
                in_gate_definition = brace_depth > 0
                continue

            qreg_match = qreg_re.match(line)
            if qreg_match:
                qubits += int(qreg_match.group(1))
                continue

            if line.startswith(("OPENQASM", "include", "creg", "barrier", "measure")):
                continue

            if operation_re.match(line):
                gates += 1

    if qubits <= 0:
        raise ValueError(f"Unable to determine qubit count for {path}")
    return qubits, gates


def qasm_metrics_for_circuit(circuit, cache):
    circuit_name = os.path.splitext(os.path.basename(normalize_csv_text(circuit)))[0]
    if not circuit_name:
        return None
    if circuit_name in cache:
        return cache[circuit_name]

    qasm_path = resolve_qasm_path(circuit)
    if qasm_path is None:
        qasm_path = resolve_qasm_path(circuit_name)
    if qasm_path is None:
        cache[circuit_name] = None
        return None

    qubits, _ = parse_qasm_qubits_and_gates(qasm_path)
    universal_qasm_path = resolve_universal_qasm_path(circuit)
    if universal_qasm_path is None:
        universal_qasm_path = resolve_universal_qasm_path(circuit_name)

    gates = None
    gate_count_source = ""
    if universal_qasm_path is not None:
        _, gates = parse_qasm_qubits_and_gates(universal_qasm_path)
        gate_count_source = os.path.relpath(universal_qasm_path, project_root())

    cache[circuit_name] = {
        "qubits": qubits,
        "gates": gates,
        "gate_count_source": gate_count_source,
    }
    return cache[circuit_name]


def runtime_curve_display_name(mapping_type):
    names = {
        "gaussian": "Gaussian",
        "magic_aware": "Magic-aware",
        "homogeneous": "Homogeneous",
    }
    return names.get(mapping_type, str(mapping_type))


def graph_node_count(row):
    total_nodes = row.get("total_nodes_i")
    if total_nodes is not None and total_nodes > 0:
        return total_nodes
    x_i = row.get("x_i")
    y_i = row.get("y_i")
    if x_i is None or y_i is None:
        return None
    if x_i <= 0 or y_i <= 0:
        return None
    return x_i * y_i


def aggregate_runtime_qubits_plus_gates(rows):
    qasm_cache = {}
    grouped = defaultdict(list)

    for row in rows:
        mapping_type = row.get("mapping_type_norm")
        safe_passage = row.get("safe_passage_norm")
        status = normalize_text(row.get("status"))
        duration = row.get("duration_s_f")
        if mapping_type not in RUNTIME_CURVE_MAPPING_TYPES:
            continue
        if safe_passage not in RUNTIME_CURVE_SAFE_PASSAGES:
            continue
        if status not in RUNTIME_CURVE_STATUSES:
            continue
        if duration is None:
            continue

        circuit = row.get("circuit") or row.get("circuit_name")
        metrics = qasm_metrics_for_circuit(circuit, qasm_cache)
        if metrics is None:
            continue
        qubits = metrics["qubits"]
        gates = metrics["gates"]
        gate_count_source = metrics["gate_count_source"]
        graph_nodes = graph_node_count(row)
        if graph_nodes is None:
            continue
        graph_x = row.get("x_i")
        graph_y = row.get("y_i")
        circuit_name = os.path.splitext(os.path.basename(normalize_csv_text(circuit)))[0]
        grouped[
            (
                mapping_type,
                safe_passage,
                circuit_name,
                qubits,
                gates,
                gate_count_source,
                graph_x,
                graph_y,
                graph_nodes,
            )
        ].append(row)

    aggregate = []
    for (
        mapping_type,
        safe_passage,
        circuit_name,
        qubits,
        gates,
        gate_count_source,
        graph_x,
        graph_y,
        graph_nodes,
    ), group_rows in grouped.items():
        durations = [row["duration_s_f"] for row in group_rows if row.get("duration_s_f") is not None]
        if not durations:
            continue
        statuses = [normalize_text(row.get("status")) for row in group_rows]
        aggregate.append(
            {
                "curve": f"{runtime_curve_display_name(mapping_type)} + {safe_passage}",
                "mapping_type": mapping_type,
                "safe_passage_strategy": safe_passage,
                "circuit": circuit_name,
                "qubits": qubits,
                "gates": gates,
                "qubits_plus_gates": qubits + gates if gates is not None else None,
                "gate_count_source": gate_count_source,
                "graph_x": graph_x,
                "graph_y": graph_y,
                "graph_nodes": graph_nodes,
                "duration_seconds_median": statistics.median(durations),
                "duration_seconds_min": min(durations),
                "duration_seconds_max": max(durations),
                "sample_count": len(group_rows),
                "success_count": sum(status in SUCCESS_STATUSES for status in statuses),
                "timeout_count": sum(status in TIMEOUT_STATUSES for status in statuses),
            }
        )

    aggregate.sort(
        key=lambda row: (
            row["qubits_plus_gates"] if row["qubits_plus_gates"] is not None else math.inf,
            row["graph_nodes"],
            row["mapping_type"],
            row["safe_passage_strategy"],
            row["circuit"],
        )
    )
    return aggregate


def write_runtime_qubits_plus_gates_csv(entries, output_dir):
    csv_path = os.path.join(output_dir, "helpers", "runtime_vs_qubits_plus_gates_with_timeouts.csv")
    fieldnames = [
        "curve",
        "mapping_type",
        "safe_passage_strategy",
        "circuit",
        "qubits",
        "gates",
        "qubits_plus_gates",
        "gate_count_source",
        "graph_x",
        "graph_y",
        "graph_nodes",
        "duration_seconds_median",
        "duration_seconds_min",
        "duration_seconds_max",
        "sample_count",
        "success_count",
        "timeout_count",
    ]
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    return csv_path


def collapse_runtime_entries_by_x(entries, x_key):
    grouped = defaultdict(list)
    for entry in entries:
        x_value = entry.get(x_key)
        if x_value is None:
            continue
        grouped[(entry["mapping_type"], entry["safe_passage_strategy"], x_value)].append(entry)

    collapsed = []
    for (mapping_type, safe_passage, x_value), group_entries in grouped.items():
        durations = [entry["duration_seconds_median"] for entry in group_entries]
        collapsed.append(
            {
                x_key: x_value,
                "mapping_type": mapping_type,
                "safe_passage_strategy": safe_passage,
                "duration_seconds_median": statistics.median(durations),
                "timeout_count": sum(entry["timeout_count"] for entry in group_entries),
            }
        )
    return collapsed


def plot_runtime_entries(
    entries,
    output_dir,
    generated,
    filename,
    x_key,
    x_label,
    title,
    collapse_same_x=False,
    connect_points=False,
    jitter_duplicate_x=False,
    safe_passage_filter=None,
):
    if safe_passage_filter is None:
        safe_passages = RUNTIME_CURVE_SAFE_PASSAGES
    else:
        safe_passages = (safe_passage_filter,)

    plot_entries = [
        entry
        for entry in entries
        if entry.get("safe_passage_strategy") in safe_passages
    ]
    plot_entries = collapse_runtime_entries_by_x(plot_entries, x_key) if collapse_same_x else plot_entries
    colors = {
        "gaussian": "#D55E00",
        "magic_aware": "#0072B2",
        "homogeneous": "#009E73",
    }
    linestyles = {"cube": "-", "connectivity": "--"}
    markers = {"cube": "o", "connectivity": "s"}

    fig, ax = plt.subplots(figsize=(13, 7.5))
    legend_handles = []
    timeout_points = []
    series_pairs = [
        (mapping_type, safe_passage)
        for mapping_type in RUNTIME_CURVE_MAPPING_TYPES
        for safe_passage in safe_passages
    ]
    series_center = (len(series_pairs) - 1) / 2.0

    for series_index, (mapping_type, safe_passage) in enumerate(series_pairs):
        points = [
            entry
            for entry in plot_entries
            if entry["mapping_type"] == mapping_type
            and entry["safe_passage_strategy"] == safe_passage
            and entry.get(x_key) is not None
            and entry.get(x_key) > 0
        ]
        if not points:
            continue
        points.sort(key=lambda entry: (entry[x_key], entry.get("circuit", "")))

        x_values = [entry[x_key] for entry in points]
        if jitter_duplicate_x:
            grouped_indices = defaultdict(list)
            for idx, x_value in enumerate(x_values):
                grouped_indices[x_value].append(idx)
            series_shift = (series_index - series_center) * 0.018
            jittered = list(x_values)
            for x_value, indices in grouped_indices.items():
                count = len(indices)
                for position, idx in enumerate(indices):
                    within_shift = 0.0
                    if count > 1:
                        within_shift = (position - (count - 1) / 2.0) * 0.012
                    jittered[idx] = x_value * math.exp(series_shift + within_shift)
            x_values = jittered

        y_values = [entry["duration_seconds_median"] for entry in points]
        color = colors[mapping_type]
        linestyle = linestyles[safe_passage] if connect_points else "None"
        marker = markers[safe_passage]
        if safe_passage_filter is None:
            label = f"{runtime_curve_display_name(mapping_type)} / {safe_passage}"
        else:
            label = runtime_curve_display_name(mapping_type)

        ax.plot(
            x_values,
            y_values,
            color=color,
            linestyle=linestyle,
            marker=marker,
            markersize=5,
            linewidth=1.9 if connect_points else 0,
            alpha=0.92,
            label=label,
        )
        legend_handles.append(
            Line2D(
                [0],
                [0],
                color=color,
                linestyle=linestyles[safe_passage] if connect_points else "None",
                marker=marker,
                label=label,
            )
        )

        for entry, x_value in zip(points, x_values):
            if entry["timeout_count"] > 0:
                timeout_points.append((entry, color, x_value))

    for entry, color, x_value in timeout_points:
        ax.scatter(
            [x_value],
            [entry["duration_seconds_median"]],
            marker="X",
            s=78,
            color=color,
            edgecolor="black",
            linewidth=0.6,
            zorder=5,
        )

    timeout_y_values = [
        entry["duration_seconds_median"]
        for entry in plot_entries
        if entry["timeout_count"] > 0 and entry["duration_seconds_median"] > 0
    ]
    if timeout_y_values:
        timeout_level = statistics.median(timeout_y_values)
        ax.axhline(timeout_level, color="#777777", linestyle=":", linewidth=1.2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(x_label)
    ax.set_ylabel("execution time (seconds)")
    ax.set_title(title)
    ax.grid(True, which="both", linestyle=":", linewidth=0.65, alpha=0.7)

    if timeout_points:
        timeout_label = "group includes timeout" if collapse_same_x else "point includes timeout"
        legend_handles.append(
            Line2D(
                [0],
                [0],
                color="#333333",
                linestyle="",
                marker="X",
                markersize=8,
                label=timeout_label,
            )
        )
    ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=9, ncols=2, frameon=True)

    save_fig(fig, output_dir, filename, generated)


def plot_runtime_qubits_plus_gates(rows, output_dir, generated, skipped=None):
    filename = "32_runtime_vs_qubits_plus_gates_cube_with_timeouts.png"
    entries = aggregate_runtime_qubits_plus_gates(rows)
    if not entries:
        record_skipped_plot(
            skipped,
            filename,
            "no rows matched gaussian/magic-aware/homogeneous with cube/connectivity and duration data",
        )
        return None

    write_runtime_qubits_plus_gates_csv(entries, output_dir)
    runtime_plot_specs = [
        (
            "32_runtime_vs_qubits_plus_gates",
            "qubits_plus_gates",
            "#qubits + #gates",
            "Median execution time vs #qubits + #gates",
            False,
            False,
            True,
        ),
        (
            "33_runtime_vs_qubits",
            "qubits",
            "#qubits",
            "Median execution time vs #qubits",
            False,
            False,
            True,
        ),
        (
            "34_runtime_vs_gates",
            "gates",
            "#gates",
            "Median execution time vs #gates",
            False,
            False,
            True,
        ),
        (
            "35_runtime_vs_graph_nodes",
            "graph_nodes",
            "graph size (#nodes = graph_x * graph_y)",
            "Median execution time vs graph size",
            False,
            False,
            True,
        ),
    ]
    for (
        basename,
        x_key,
        x_label,
        title,
        connect_points,
        jitter_duplicate_x,
        collapse_same_x,
    ) in runtime_plot_specs:
        for safe_passage in RUNTIME_CURVE_SAFE_PASSAGES:
            plot_runtime_entries(
                entries,
                output_dir,
                generated,
                f"{basename}_{safe_passage}_with_timeouts.png",
                x_key,
                x_label,
                f"{title}: gaussian, magic-aware, homogeneous ({safe_passage})",
                collapse_same_x=collapse_same_x,
                connect_points=connect_points,
                jitter_duplicate_x=jitter_duplicate_x,
                safe_passage_filter=safe_passage,
            )
    return entries


def runtime_group_value(row, factor_key):
    value = row.get(factor_key)
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None

    if factor_key == "gaussian_confidence_f":
        return format_gaussian_confidence_label(value), float(value)
    if factor_key.endswith("_f"):
        return format_number_label(value), float(value)

    text = str(value).strip()
    if not text:
        return None
    return text, text


def runtime_measurement_entries(rows):
    qasm_cache = {}
    entries = []

    for row in rows:
        status = normalize_text(row.get("status"))
        duration = row.get("duration_s_f")
        if status not in RUNTIME_CURVE_STATUSES:
            continue
        if duration is None or duration <= 0:
            continue

        circuit = row.get("circuit") or row.get("circuit_name")
        metrics = qasm_metrics_for_circuit(circuit, qasm_cache)
        if metrics is None:
            continue

        graph_nodes = graph_node_count(row)
        if graph_nodes is None:
            continue

        entry = {
            "circuit": os.path.splitext(os.path.basename(normalize_csv_text(circuit)))[0],
            "mapping_type": row.get("mapping_type_norm"),
            "qubits": metrics["qubits"],
            "gates": metrics["gates"],
            "graph_nodes": graph_nodes,
            "duration_seconds": duration,
            "status": status,
        }

        for factor_key, _, _, _ in RUNTIME_GROUPED_FACTOR_SPECS:
            group_value = runtime_group_value(row, factor_key)
            if group_value is None:
                continue
            entry[f"{factor_key}_label"] = group_value[0]
            entry[f"{factor_key}_sort"] = group_value[1]

        entries.append(entry)

    return entries


def aggregate_runtime_grouped(entries, x_key, factor_key, exclude_mapping_types=None):
    if exclude_mapping_types is None:
        exclude_mapping_types = set()

    grouped = defaultdict(list)
    for entry in entries:
        if entry.get("mapping_type") in exclude_mapping_types:
            continue
        x_value = entry.get(x_key)
        group_label = entry.get(f"{factor_key}_label")
        group_sort = entry.get(f"{factor_key}_sort")
        if x_value is None or group_label is None:
            continue
        if isinstance(x_value, float) and math.isnan(x_value):
            continue
        if x_value <= 0:
            continue
        grouped[(group_label, group_sort, x_value)].append(entry)

    aggregate = []
    for (group_label, group_sort, x_value), group_entries in grouped.items():
        durations = [entry["duration_seconds"] for entry in group_entries]
        aggregate.append(
            {
                "group_label": group_label,
                "group_sort": group_sort,
                "x_value": x_value,
                "duration_seconds_median": statistics.median(durations),
                "duration_seconds_min": min(durations),
                "duration_seconds_max": max(durations),
                "sample_count": len(group_entries),
                "success_count": sum(entry["status"] in SUCCESS_STATUSES for entry in group_entries),
                "timeout_count": sum(entry["status"] in TIMEOUT_STATUSES for entry in group_entries),
            }
        )

    aggregate.sort(key=lambda item: (str(type(item["group_sort"])), item["group_sort"], item["x_value"]))
    return aggregate


def aggregate_homogeneous_baseline(entries, x_key):
    grouped = defaultdict(list)
    for entry in entries:
        if entry.get("mapping_type") != "homogeneous":
            continue
        x_value = entry.get(x_key)
        if x_value is None:
            continue
        if isinstance(x_value, float) and math.isnan(x_value):
            continue
        if x_value <= 0:
            continue
        grouped[x_value].append(entry)

    aggregate = []
    for x_value, group_entries in grouped.items():
        durations = [entry["duration_seconds"] for entry in group_entries]
        aggregate.append(
            {
                "x_value": x_value,
                "duration_seconds_median": statistics.median(durations),
                "duration_seconds_min": min(durations),
                "duration_seconds_max": max(durations),
                "sample_count": len(group_entries),
                "success_count": sum(entry["status"] in SUCCESS_STATUSES for entry in group_entries),
                "timeout_count": sum(entry["status"] in TIMEOUT_STATUSES for entry in group_entries),
            }
        )

    aggregate.sort(key=lambda item: item["x_value"])
    return aggregate


def runtime_group_sort_key(value):
    if isinstance(value, (int, float)):
        return (0, float(value))
    return (1, str(value))


def write_runtime_grouped_factors_csv(all_entries, output_dir):
    csv_path = os.path.join(output_dir, "helpers", "runtime_grouped_factors.csv")
    fieldnames = [
        "plot_filename",
        "series_type",
        "x_axis",
        "group_by",
        "group_value",
        "x_value",
        "duration_seconds_median",
        "duration_seconds_min",
        "duration_seconds_max",
        "sample_count",
        "success_count",
        "timeout_count",
    ]
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_entries)
    return csv_path


def plot_runtime_grouped_entries(
    aggregate,
    output_dir,
    generated,
    filename,
    x_label,
    group_label,
    title,
    skipped=None,
    baseline=None,
):
    if baseline is None:
        baseline = []

    plot_entries = [
        entry
        for entry in aggregate
        if entry["x_value"] > 0 and entry["duration_seconds_median"] > 0
    ]
    baseline_entries = [
        entry
        for entry in baseline
        if entry["x_value"] > 0 and entry["duration_seconds_median"] > 0
    ]

    if not plot_entries and not baseline_entries:
        record_skipped_plot(
            skipped,
            filename,
            "no rows with positive x values and duration_seconds for this grouping",
        )
        return

    groups = sorted(
        {entry["group_label"] for entry in plot_entries},
        key=lambda label: runtime_group_sort_key(
            next(entry["group_sort"] for entry in plot_entries if entry["group_label"] == label)
        ),
    )
    colors = category_color_map(groups)

    fig, ax = plt.subplots(figsize=(12, 7))
    for group in groups:
        points = [entry for entry in plot_entries if entry["group_label"] == group]
        points.sort(key=lambda item: item["x_value"])
        sample_count = sum(entry["sample_count"] for entry in points)
        ax.plot(
            [entry["x_value"] for entry in points],
            [entry["duration_seconds_median"] for entry in points],
            marker="o",
            linewidth=1.8,
            markersize=5,
            alpha=0.9,
            color=colors[group],
            label=legend_label_with_sample_count(group, sample_count),
        )

        timeout_points = [entry for entry in points if entry["timeout_count"] > 0]
        if timeout_points:
            ax.scatter(
                [entry["x_value"] for entry in timeout_points],
                [entry["duration_seconds_median"] for entry in timeout_points],
                marker="X",
                s=82,
                color=colors[group],
                edgecolor="black",
                linewidth=0.6,
                zorder=5,
            )

    if baseline_entries:
        baseline_entries.sort(key=lambda item: item["x_value"])
        baseline_sample_count = sum(entry["sample_count"] for entry in baseline_entries)
        ax.plot(
            [entry["x_value"] for entry in baseline_entries],
            [entry["duration_seconds_median"] for entry in baseline_entries],
            color="#111111",
            linestyle="--",
            marker="D",
            linewidth=2.2,
            markersize=5,
            alpha=0.95,
            label=legend_label_with_sample_count("Homogeneous baseline", baseline_sample_count),
            zorder=6,
        )

        timeout_points = [entry for entry in baseline_entries if entry["timeout_count"] > 0]
        if timeout_points:
            ax.scatter(
                [entry["x_value"] for entry in timeout_points],
                [entry["duration_seconds_median"] for entry in timeout_points],
                marker="X",
                s=88,
                color="#111111",
                edgecolor="white",
                linewidth=0.6,
                zorder=7,
            )

    if any(entry["timeout_count"] > 0 for entry in plot_entries + baseline_entries):
        ax.scatter([], [], marker="X", s=82, color="#333333", label="point includes timeout")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(x_label)
    ax.set_ylabel("execution time (seconds)")
    ax.set_title(f"{title} grouped by {group_label}")
    ax.grid(True, which="both", linestyle=":", linewidth=0.65, alpha=0.7)
    ax.legend(fontsize=8, frameon=True, loc="upper left", bbox_to_anchor=(1.02, 1.0))
    save_fig(fig, output_dir, filename, generated)


def plot_runtime_grouped_factors(rows, output_dir, generated, skipped=None):
    entries = runtime_measurement_entries(rows)
    if not entries:
        record_skipped_plot(
            skipped,
            "36_runtime_vs_qubits_by_gaussian_confidence.png",
            "no rows with duration data and resolvable QASM metrics",
        )
        return None

    csv_entries = []
    plot_index = 36
    for x_key, x_label, x_slug in RUNTIME_GROUPED_X_SPECS:
        baseline = aggregate_homogeneous_baseline(entries, x_key)
        for factor_key, factor_csv_name, factor_label, factor_slug in RUNTIME_GROUPED_FACTOR_SPECS:
            filename = f"{plot_index:02d}_runtime_vs_{x_slug}_by_{factor_slug}.png"
            aggregate = aggregate_runtime_grouped(
                entries,
                x_key,
                factor_key,
                exclude_mapping_types={"homogeneous"},
            )
            for aggregate_entry in aggregate:
                csv_entries.append(
                    {
                        "plot_filename": filename,
                        "series_type": "grouped_factor",
                        "x_axis": x_key,
                        "group_by": factor_csv_name,
                        "group_value": aggregate_entry["group_label"],
                        "x_value": aggregate_entry["x_value"],
                        "duration_seconds_median": aggregate_entry["duration_seconds_median"],
                        "duration_seconds_min": aggregate_entry["duration_seconds_min"],
                        "duration_seconds_max": aggregate_entry["duration_seconds_max"],
                        "sample_count": aggregate_entry["sample_count"],
                        "success_count": aggregate_entry["success_count"],
                        "timeout_count": aggregate_entry["timeout_count"],
                    }
                )
            for baseline_entry in baseline:
                csv_entries.append(
                    {
                        "plot_filename": filename,
                        "series_type": "homogeneous_baseline",
                        "x_axis": x_key,
                        "group_by": factor_csv_name,
                        "group_value": "homogeneous",
                        "x_value": baseline_entry["x_value"],
                        "duration_seconds_median": baseline_entry["duration_seconds_median"],
                        "duration_seconds_min": baseline_entry["duration_seconds_min"],
                        "duration_seconds_max": baseline_entry["duration_seconds_max"],
                        "sample_count": baseline_entry["sample_count"],
                        "success_count": baseline_entry["success_count"],
                        "timeout_count": baseline_entry["timeout_count"],
                    }
                )
            plot_runtime_grouped_entries(
                aggregate,
                output_dir,
                generated,
                filename,
                x_label,
                factor_label,
                f"Median execution time vs {x_label}",
                skipped,
                baseline,
            )
            plot_index += 1

    return write_runtime_grouped_factors_csv(csv_entries, output_dir)


def plot_gaussian_confidence_safe_passage_routing_heatmap(rows, output_dir, generated, skipped=None):
    heatmap_rows = [
        row
        for row in rows
        if row.get("mapping_type_norm") == "gaussian"
        and row.get("safe_passage_norm") in {"connectivity", "cube"}
        and row.get("gaussian_confidence_label")
        and row.get("success")
        and row.get("routing_steps_f") is not None
    ]

    make_pair_heatmap(
        heatmap_rows,
        "safe_passage_norm",
        "gaussian_confidence_label",
        lambda subset: mean_of([r["routing_steps_f"] for r in subset]),
        "",
        "Mean Routing Steps by Safe Passage and Gaussian Confidence",
        "mean routing steps",
        "45_heatmap_routing_safe_passage_vs_gaussian_confidence.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.0f}",
    )
    make_pair_heatmap(
        heatmap_rows,
        "safe_passage_norm",
        "gaussian_confidence_label",
        lambda subset: mean_of(boxplot_non_outlier_values([r["routing_steps_f"] for r in subset])),
        "no out",
        "Mean Routing Steps by Safe Passage and Gaussian Confidence (no outliers)",
        "mean routing steps (no outliers)",
        "45_heatmap_routing_safe_passage_vs_gaussian_confidence_no_out.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.0f}",
    )


def heatmap_mean_value(metric, subset):
    values = axis_boxplot_values(subset, metric)
    if not values:
        return None
    return float(np.mean(values))


def heatmap_mean_no_outliers(metric, subset):
    values = axis_boxplot_values(subset, metric)
    if not values:
        return None
    if metric == "success_rate":
        return float(np.mean(values))
    visible = boxplot_non_outlier_values(values)
    if not visible:
        return None
    return float(np.mean(visible))


def heatmap_median_value(metric, subset):
    values = axis_boxplot_values(subset, metric)
    if not values:
        return None
    return float(np.median(values))


def requested_heatmap_value_fn(metric):
    return lambda subset: heatmap_mean_value(metric, subset)


def requested_heatmap_value_fn_no_outliers(metric):
    return lambda subset: heatmap_mean_no_outliers(metric, subset)


def requested_heatmap_value_fn_median(metric):
    return lambda subset: heatmap_median_value(metric, subset)


def plot_circuit_coverage_table(rows, col_key, col_label, title, filename, output_dir, generated, skipped=None, subfolder=None):
    col_values = sorted(
        {heatmap_axis_value(r, col_key) for r in rows if has_heatmap_axis_value(r, col_key)},
        key=lambda label: heatmap_axis_sort_key(col_key, label),
    )
    if not col_values:
        save_empty_plot(title, output_dir, filename, generated, message=f"No data for {col_key}", subfolder=subfolder)
        return

    circuits_by_col = {}
    for cv in col_values:
        labels = sorted({
            r.get("circuit_graph_label", "")
            for r in rows
            if heatmap_axis_value(r, col_key) == cv and r.get("circuit_graph_label", "").strip()
        })
        circuits_by_col[cv] = labels

    max_rows = max((len(v) for v in circuits_by_col.values()), default=0)
    if max_rows == 0:
        save_empty_plot(title, output_dir, filename, generated, message="No circuit data", subfolder=subfolder)
        return

    table_data = [
        [circuits_by_col[cv][i] if i < len(circuits_by_col[cv]) else "" for cv in col_values]
        for i in range(max_rows)
    ]

    n_cols = len(col_values)
    cell_w = 2.8
    cell_h = 0.32
    fig_width = max(6, n_cols * cell_w + 0.5)
    fig_height = max(3, (max_rows + 1) * cell_h + 1.2)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")
    ax.set_title(title, pad=10, fontsize=10, fontweight="bold")

    tbl = ax.table(cellText=table_data, colLabels=col_values, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7)
    tbl.auto_set_column_width(col=list(range(n_cols)))

    for j in range(n_cols):
        cell = tbl[0, j]
        cell.set_facecolor("#2A9D8F")
        cell.set_text_props(color="white", fontweight="bold")
    for i in range(1, max_rows + 1):
        bg = "#f5f5f5" if i % 2 == 0 else "white"
        for j in range(n_cols):
            tbl[i, j].set_facecolor(bg)

    save_fig(fig, output_dir, filename, generated, subfolder=subfolder)


def _process_single_heatmap_item(
    item,
    rows,
    heatmap_rows_by_metric,
    axis_boxplot_rows_by_metric,
    output_dir,
    generated,
    skipped,
    align=False,
):
    if item["kind"] == "heatmap":
        metric_rows = heatmap_rows_by_metric[item["metric"]]
        heatmap_rows = filter_heatmap_rows(metric_rows, item["row_key"], item["col_key"])
        removed_counts = None
        if align and item["metric"] != "success_rate":
            heatmap_rows, removed_counts = align_rows_to_common_configs(
                heatmap_rows, item["row_key"], item["col_key"]
            )
        if item.get("median"):
            value_fn = requested_heatmap_value_fn_median(item["metric"])
            value_label_suffix = "mediana"
        elif item.get("no_outliers"):
            value_fn = requested_heatmap_value_fn_no_outliers(item["metric"])
            value_label_suffix = "no out"
        else:
            value_fn = requested_heatmap_value_fn(item["metric"])
            value_label_suffix = ""

        make_pair_heatmap(
            heatmap_rows,
            item["row_key"],
            item["col_key"],
            value_fn,
            value_label_suffix,
            item["title"],
            item["colorbar_label"],
            item["filename"],
            output_dir,
            generated,
            skipped,
            value_format=item["value_format"],
            subfolder=item.get("subfolder"),
            removed_counts=removed_counts,
        )
        return

    if item["kind"] in {"triplet_dashboard", "x_axis_dashboard"}:
        plot_image_dashboard(
            item["source_items"],
            item["title"],
            item["filename"],
            output_dir,
            generated,
            skipped,
            columns=item.get("columns", 3),
            panel_title_mode=item.get("panel_title_mode", "metric"),
            panel_width=item.get("panel_width", 6.2),
            panel_height=item.get("panel_height", 5.3),
            dpi=item.get("dpi", DASHBOARD_OUTPUT_DPI),
            subfolder=item.get("subfolder"),
        )
        return

    if item["kind"] == "axis_barplot":
        metric_rows = axis_boxplot_rows_by_metric[item["metric"]]
        plot_axis_barplot(
            metric_rows,
            item["axis_key"],
            item["metric"],
            item["title"],
            item["ylabel"],
            item["filename"],
            output_dir,
            generated,
            skipped,
            value_format=item["value_format"],
            color=item["color"],
            subfolder=item.get("subfolder"),
            align=align,
        )
        return

    if item["kind"] == "circuit_table":
        plot_circuit_coverage_table(
            rows,
            item["col_key"],
            item["col_label"],
            item["title"],
            item["filename"],
            output_dir,
            generated,
            skipped,
            subfolder=item.get("subfolder"),
        )


def _build_heatmap_rows_by_metric(rows, rows_success_with_routing):
    rows_success_with_duration = [
        row for row in rows if row["success"] and row["duration_s_f"] is not None
    ]
    rows_success_with_non_routed = [
        row for row in rows if row["success"] and row["non_routed_layer_pct_f"] is not None
    ]
    heatmap_rows_by_metric = {
        "success_rate": rows,
        "routing_steps": rows_success_with_routing,
        "execution_time": rows_success_with_duration,
        "non_routed_layer_pct": rows_success_with_non_routed,
    }
    axis_boxplot_rows_by_metric = dict(heatmap_rows_by_metric)
    return heatmap_rows_by_metric, axis_boxplot_rows_by_metric


def run_heatmap_worker(args):
    """Subprocess entry point: process REQUESTED_HEATMAP_ITEMS[start:end] and exit."""
    importMatplotlib()
    plt.style.use("seaborn-v0_8-whitegrid")

    start, end = (int(x) for x in args.worker_heatmap_batch.split(":"))
    heatmap_items = filter_heatmap_items_by_axes(
        REQUESTED_HEATMAP_ITEMS,
        selected_heatmap_axis_slugs(args),
    )
    raw_rows, _, _ = load_raw_rows_from_files([args.worker_csv])
    rows_all = prepare_rows_for_analysis(raw_rows)
    del raw_rows
    register_extra_statuses(rows_all)
    rows_no_timeout = exclude_timeout_rows(rows_all)
    rows_success_with_routing = [
        r for r in rows_no_timeout if r["success"] and r["routing_steps_f"] is not None
    ]
    rows_with_duration = [r for r in rows_no_timeout if r["duration_s_f"] is not None]
    heatmap_rows_by_metric, axis_boxplot_rows_by_metric = _build_heatmap_rows_by_metric(
        rows_no_timeout, rows_success_with_routing
    )

    _DASHBOARD_KINDS = {"triplet_dashboard", "x_axis_dashboard"}
    phase = getattr(args, "worker_heatmap_phase", "source")
    generated = []
    skipped = []
    items_slice = [
        item for item in heatmap_items[start:end]
        if (item["kind"] in _DASHBOARD_KINDS) == (phase == "dashboard")
    ]
    for item in items_slice:
        _process_single_heatmap_item(
            item,
            rows_no_timeout,
            heatmap_rows_by_metric,
            axis_boxplot_rows_by_metric,
            args.worker_output_dir,
            generated,
            skipped,
            align=args.align,
        )

    with open(args.worker_result, "w") as f:
        json.dump({"generated": generated, "skipped": skipped}, f)


def _launch_heatmap_batch(
    batch_idx,
    start,
    end,
    csv_path,
    output_dir,
    align=False,
    phase="source",
    axis_slugs=None,
    items_batch=None,
):
    """Spawn a heatmap worker subprocess for items [start:end] and return its handle."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        result_path = f.name
    cmd = [
        sys.executable,
        os.path.abspath(__file__),
        "--worker-heatmap-batch", f"{start}:{end}",
        "--worker-heatmap-phase", phase,
        "--worker-csv", csv_path,
        "--worker-output-dir", output_dir,
        "--worker-result", result_path,
    ]
    if axis_slugs:
        cmd.extend(["--worker-heatmap-axes", ",".join(axis_slugs)])
    if align:
        cmd.append("--align")
    proc = subprocess.Popen(cmd)
    return {
        "batch_idx": batch_idx,
        "start": start,
        "end": end,
        "items": list(items_batch or []),
        "result_path": result_path,
        "proc": proc,
    }


def _collect_heatmap_batch(entry, total_batches, generated, skipped):
    """Gather results of a finished heatmap worker subprocess."""
    batch_idx = entry["batch_idx"]
    start, end = entry["start"], entry["end"]
    result_path = entry["result_path"]
    returncode = entry["proc"].returncode
    try:
        if returncode == 0:
            with open(result_path) as f:
                result = json.load(f)
            generated.extend(result.get("generated", []))
            skipped.extend(result.get("skipped", []))
            print(f"[heatmap batch {batch_idx}/{total_batches}] items {start}:{end} done", flush=True)
        else:
            print(f"[batch {batch_idx}] failed with exit {returncode}", flush=True)
            for item in entry.get("items") or REQUESTED_HEATMAP_ITEMS[start:end]:
                record_skipped_plot(
                    skipped, item["filename"], f"subprocess batch failed (exit {returncode})"
                )
    finally:
        try:
            os.unlink(result_path)
        except OSError:
            pass


def plot_requested_heatmaps(
    rows,
    rows_success_with_routing,
    rows_with_duration,
    output_dir,
    generated,
    skipped=None,
    csv_path=None,
    batch_size=HEATMAP_BATCH_SIZE,
    parallel=1,
    align=False,
    heatmap_items=None,
    axis_slugs=None,
):
    """Orchestrate heatmap generation via subprocess batches to release memory between batches."""
    heatmap_items = list(REQUESTED_HEATMAP_ITEMS if heatmap_items is None else heatmap_items)
    axis_slugs = list(axis_slugs or [])
    if csv_path is None:
        # Fallback: in-process generation (slower but no subprocess).
        heatmap_rows_by_metric, axis_boxplot_rows_by_metric = _build_heatmap_rows_by_metric(
            rows, rows_success_with_routing
        )
        for idx, item in enumerate(heatmap_items):
            _process_single_heatmap_item(
                item,
                rows,
                heatmap_rows_by_metric,
                axis_boxplot_rows_by_metric,
                output_dir,
                generated,
                skipped,
                align=align,
            )
            if (idx + 1) % 10 == 0:
                _trim_heap()
        return

    _DASHBOARD_KINDS = {"triplet_dashboard", "x_axis_dashboard"}
    total = len(heatmap_items)
    if not total:
        return
    batches = [(s, min(s + batch_size, total)) for s in range(0, total, batch_size)]
    total_batches = len(batches)
    parallel = max(1, parallel)

    # Phase 1: source items (heatmaps, barplots, etc.) — exclude dashboard kinds so they
    # don't run before their source images are on disk.
    # Phase 2: dashboard items — run only after all phase-1 batches are complete.
    dashboard_batch_indices = {
        i for i, (s, e) in enumerate(batches)
        if any(item["kind"] in _DASHBOARD_KINDS for item in heatmap_items[s:e])
    }

    n_source_items = sum(1 for it in heatmap_items if it["kind"] not in _DASHBOARD_KINDS)
    n_dash_items = total - n_source_items
    print(
        f"Generating {total} heatmap items in {total_batches} subprocess batches of up to "
        f"{batch_size} ({parallel} in parallel) — "
        f"{n_source_items} source items then {n_dash_items} dashboard items",
        flush=True,
    )
    if skipped is None:
        skipped = []

    def _run_batches(phase):
        running = []
        next_batch = 0
        while next_batch < total_batches or running:
            while next_batch < total_batches and len(running) < parallel:
                if phase == "source" or next_batch in dashboard_batch_indices:
                    start, end = batches[next_batch]
                    running.append(
                        _launch_heatmap_batch(
                            next_batch + 1, start, end, csv_path, output_dir,
                            align=align,
                            phase=phase,
                            axis_slugs=axis_slugs,
                            items_batch=heatmap_items[start:end],
                        )
                    )
                next_batch += 1
            still_running = []
            for entry in running:
                if entry["proc"].poll() is None:
                    still_running.append(entry)
                else:
                    _collect_heatmap_batch(entry, total_batches, generated, skipped)
            running = still_running
            if running and (next_batch >= total_batches or len(running) >= parallel):
                time.sleep(0.2)

    _run_batches("source")
    if dashboard_batch_indices:
        print(
            f"Phase 2: generating {n_dash_items} dashboard items "
            f"({len(dashboard_batch_indices)} batches)",
            flush=True,
        )
        _run_batches("dashboard")


def plot_summary_tables(rows, output_dir, generated):
    circuits = sorted({r["circuit_name"] for r in rows})
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))

    success_rates = []
    elapsed_median = []
    success_sample_counts = []
    duration_sample_counts = []
    for c in circuits:
        subset = [r for r in rows if r["circuit_name"] == c]
        success_sample_counts.append(len(subset))
        success_rates.append(success_rate(subset) or 0.0)
        duration_vals = non_empty([r["duration_s_f"] for r in subset])
        duration_sample_counts.append(len(duration_vals))
        elapsed_median.append(float(np.median(duration_vals)) if duration_vals else 0.0)

    y_positions = np.arange(len(circuits))
    axs[0].barh(y_positions, success_rates, color="#2A9D8F")
    axs[0].set_title("Success Rate by Circuit")
    axs[0].set_xlabel("%")
    axs[0].set_xlim(0, 100)
    axs[0].set_yticks(y_positions)
    axs[0].set_yticklabels(
        [
            label_with_sample_count(circuit, sample_count)
            for circuit, sample_count in zip(circuits, success_sample_counts)
        ]
    )

    axs[1].barh(y_positions, elapsed_median, color="#577590")
    axs[1].set_title("Median Duration by Circuit")
    axs[1].set_xlabel("duration_seconds")
    axs[1].set_yticks(y_positions)
    axs[1].set_yticklabels(
        [
            label_with_sample_count(circuit, sample_count)
            for circuit, sample_count in zip(circuits, duration_sample_counts)
        ]
    )

    save_fig(fig, output_dir, "02_circuit_summary_bars.png", generated)


def plot_best_config_counts_by_heatmap_axis(
    rows_success_with_routing,
    output_dir,
    generated,
    skipped=None,
    heatmap_items=None,
):
    csv_rows = []
    heatmap_items = REQUESTED_HEATMAP_ITEMS if heatmap_items is None else heatmap_items
    best_count_items = [
        item for item in heatmap_items if item.get("kind") == "best_config_count"
    ]

    for item in best_count_items:
        axis_slug = item["axis_slug"]
        axis_key = item["axis_key"]
        axis_label = item["axis_label"]
        subfolder = item.get("subfolder", f"heatmap_{axis_slug}")
        by_circuit = defaultdict(lambda: defaultdict(list))

        for row in rows_success_with_routing:
            circuit_name = row.get("circuit_name")
            if not circuit_name:
                continue
            if not has_heatmap_axis_value(row, axis_key):
                continue
            axis_value = heatmap_axis_value(row, axis_key)
            routing_steps = row.get("routing_steps_f")
            if routing_steps is None or (isinstance(routing_steps, float) and math.isnan(routing_steps)):
                continue
            by_circuit[circuit_name][axis_value].append(routing_steps)

        counts = Counter()
        strict_counts = Counter()
        circuit_count = 0
        for values_by_axis in by_circuit.values():
            min_by_axis = {
                axis_value: min(values)
                for axis_value, values in values_by_axis.items()
                if values
            }
            if not min_by_axis:
                continue
            best_value = min(min_by_axis.values())
            best_axis_values = [
                axis_value for axis_value, value in min_by_axis.items()
                if math.isclose(value, best_value, rel_tol=1e-9, abs_tol=1e-9)
            ]
            is_sole_best = len(best_axis_values) == 1
            for axis_value in best_axis_values:
                counts[axis_value] += 1
                if is_sole_best:
                    strict_counts[axis_value] += 1
            circuit_count += 1

        filename = item["filename"]
        if not counts:
            save_empty_plot(
                item["title"],
                output_dir,
                filename,
                generated,
                message=f"No data for {axis_label}",
                subfolder=subfolder,
                ylabel="best-count",
            )
            continue

        labels = sorted(
            counts.keys(),
            key=lambda label: heatmap_axis_sort_key(axis_key, label),
        )
        strict_vals = [strict_counts.get(label, 0) for label in labels]
        tied_vals = [counts[label] - strict_counts.get(label, 0) for label in labels]
        fig, ax = plt.subplots(figsize=(max(8.5, len(labels) * 1.2), 6.5))
        bars_strict = ax.bar(labels, strict_vals, color="#577590", label="strict best (sole winner)")
        bars_tied = ax.bar(labels, tied_vals, bottom=strict_vals, color="#A8C5D8", label="tied best")
        ax.set_title(
            f"Best routing config count by {axis_label} (n circuits={circuit_count})\n"
            "lower routing steps wins; stacked: strict (sole) vs tied"
        )
        ax.set_ylabel("best-count")
        ax.tick_params(axis="x", rotation=35)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=9, frameon=True)
        for i, label in enumerate(labels):
            total = counts[label]
            strict = strict_counts.get(label, 0)
            ax.text(
                i, total + 0.15, f"{total}\n({strict})",
                ha="center", va="bottom", fontsize=8, color="#333333",
            )

        save_fig(fig, output_dir, filename, generated, subfolder=subfolder)

        for label in labels:
            count = counts[label]
            strict = strict_counts.get(label, 0)
            csv_rows.append(
                {
                    "axis": axis_slug,
                    "axis_label": axis_label,
                    "axis_value": label,
                    "best_count": count,
                    "strict_best_count": strict,
                    "circuits": circuit_count,
                    "best_share": (count / circuit_count) if circuit_count else 0.0,
                    "strict_best_share": (strict / circuit_count) if circuit_count else 0.0,
                }
            )

    if not csv_rows:
        return None

    csv_rows.sort(key=lambda row: (row["axis"], row["best_count"] * -1, row["axis_value"]))
    csv_path = os.path.join(output_dir, "csv", "best_config_counts_by_heatmap_axis.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "axis",
                "axis_label",
                "axis_value",
                "best_count",
                "strict_best_count",
                "circuits",
                "best_share",
                "strict_best_share",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    return csv_path


def plot_best_non_routed_config_counts_by_heatmap_axis(
    rows_success_with_non_routed,
    output_dir,
    generated,
    skipped=None,
    heatmap_items=None,
):
    csv_rows = []
    heatmap_items = REQUESTED_HEATMAP_ITEMS if heatmap_items is None else heatmap_items
    items = [
        item for item in heatmap_items if item.get("kind") == "best_config_count_non_routed"
    ]

    for item in items:
        axis_slug = item["axis_slug"]
        axis_key = item["axis_key"]
        axis_label = item["axis_label"]
        subfolder = item.get("subfolder", f"heatmap_{axis_slug}")
        by_circuit = defaultdict(lambda: defaultdict(list))

        for row in rows_success_with_non_routed:
            circuit_name = row.get("circuit_name")
            if not circuit_name:
                continue
            if not has_heatmap_axis_value(row, axis_key):
                continue
            axis_value = heatmap_axis_value(row, axis_key)
            non_routed_pct = row.get("non_routed_layer_pct_f")
            if non_routed_pct is None or (isinstance(non_routed_pct, float) and math.isnan(non_routed_pct)):
                continue
            by_circuit[circuit_name][axis_value].append(non_routed_pct)

        counts = Counter()
        strict_counts = Counter()
        circuit_count = 0
        for values_by_axis in by_circuit.values():
            min_by_axis = {
                axis_value: min(values)
                for axis_value, values in values_by_axis.items()
                if values
            }
            if not min_by_axis:
                continue
            best_value = min(min_by_axis.values())
            best_axis_values = [
                axis_value for axis_value, value in min_by_axis.items()
                if math.isclose(value, best_value, rel_tol=1e-9, abs_tol=1e-9)
            ]
            is_sole_best = len(best_axis_values) == 1
            for axis_value in best_axis_values:
                counts[axis_value] += 1
                if is_sole_best:
                    strict_counts[axis_value] += 1
            circuit_count += 1

        filename = item["filename"]
        if not counts:
            save_empty_plot(
                item["title"],
                output_dir,
                filename,
                generated,
                message=f"No data for {axis_label}",
                subfolder=subfolder,
                ylabel="best-count",
            )
            continue

        labels = sorted(
            counts.keys(),
            key=lambda label: heatmap_axis_sort_key(axis_key, label),
        )
        strict_vals = [strict_counts.get(label, 0) for label in labels]
        tied_vals = [counts[label] - strict_counts.get(label, 0) for label in labels]
        fig, ax = plt.subplots(figsize=(max(8.5, len(labels) * 1.2), 6.5))
        ax.bar(labels, strict_vals, color="#577590", label="strict best (sole winner)")
        ax.bar(labels, tied_vals, bottom=strict_vals, color="#A8C5D8", label="tied best")
        ax.set_title(
            f"Best non-routed layer % config count by {axis_label} (n circuits={circuit_count})\n"
            "lower non-routed layer % wins; stacked: strict (sole) vs tied"
        )
        ax.set_ylabel("best-count")
        ax.tick_params(axis="x", rotation=35)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=9, frameon=True)
        for i, label in enumerate(labels):
            total = counts[label]
            strict = strict_counts.get(label, 0)
            ax.text(
                i, total + 0.15, f"{total}\n({strict})",
                ha="center", va="bottom", fontsize=8, color="#333333",
            )

        save_fig(fig, output_dir, filename, generated, subfolder=subfolder)

        for label in labels:
            count = counts[label]
            strict = strict_counts.get(label, 0)
            csv_rows.append(
                {
                    "axis": axis_slug,
                    "axis_label": axis_label,
                    "axis_value": label,
                    "best_count": count,
                    "strict_best_count": strict,
                    "circuits": circuit_count,
                    "best_share": (count / circuit_count) if circuit_count else 0.0,
                    "strict_best_share": (strict / circuit_count) if circuit_count else 0.0,
                }
            )

    if not csv_rows:
        return None

    csv_rows.sort(key=lambda row: (row["axis"], row["best_count"] * -1, row["axis_value"]))
    csv_path = os.path.join(output_dir, "csv", "best_non_routed_config_counts_by_heatmap_axis.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "axis",
                "axis_label",
                "axis_value",
                "best_count",
                "strict_best_count",
                "circuits",
                "best_share",
                "strict_best_share",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    return csv_path


def plot_timeout_counts_by_heatmap_axis(rows, output_dir, generated, skipped=None, heatmap_items=None):
    csv_rows = []
    heatmap_items = REQUESTED_HEATMAP_ITEMS if heatmap_items is None else heatmap_items
    timeout_count_items = [
        item for item in heatmap_items if item.get("kind") == "timeout_count"
    ]

    for item in timeout_count_items:
        axis_slug = item["axis_slug"]
        axis_key = item["axis_key"]
        axis_label = item["axis_label"]
        subfolder = item.get("subfolder", f"heatmap_{axis_slug}")

        counts = Counter()
        totals = Counter()
        for row in rows:
            if not has_heatmap_axis_value(row, axis_key):
                continue
            axis_value = heatmap_axis_value(row, axis_key)
            totals[axis_value] += 1
            if is_timeout(row):
                counts[axis_value] += 1

        filename = item["filename"]
        if not totals:
            save_empty_plot(
                item["title"],
                output_dir,
                filename,
                generated,
                message=f"No data for {axis_label}",
                subfolder=subfolder,
                ylabel="timeout count",
            )
            continue

        labels = sorted(
            totals.keys(),
            key=lambda label: heatmap_axis_sort_key(axis_key, label),
        )
        values = [counts.get(label, 0) for label in labels]
        total_runs = sum(totals.values())
        fig, ax = plt.subplots(figsize=(max(8.5, len(labels) * 1.2), 6.5))
        bars = ax.bar(labels, values, color="#E9C46A")
        ax.set_title(
            f"Timeout count by {axis_label} (n runs={total_runs})"
        )
        ax.set_ylabel("timeout count")
        ax.tick_params(axis="x", rotation=35)
        annotate_bars(ax, bars, fmt="{:.0f}")
        save_fig(fig, output_dir, filename, generated, subfolder=subfolder)

        for label in labels:
            count = counts.get(label, 0)
            total = totals[label]
            csv_rows.append(
                {
                    "axis": axis_slug,
                    "axis_label": axis_label,
                    "axis_value": label,
                    "timeout_count": count,
                    "total_runs": total,
                    "timeout_rate": (count / total) if total else 0.0,
                }
            )

    if not csv_rows:
        return None

    csv_rows.sort(key=lambda row: (row["axis"], row["timeout_count"] * -1, row["axis_value"]))
    csv_path = os.path.join(output_dir, "csv", "timeout_counts_by_heatmap_axis.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["axis", "axis_label", "axis_value", "timeout_count", "total_runs", "timeout_rate"],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    return csv_path


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


def best_gaussian_execution_entries(rows):
    grouped = defaultdict(list)

    for row in rows:
        if row.get("mapping_type_norm") != "gaussian":
            continue
        if not row.get("success") or row.get("routing_steps_f") is None:
            continue
        x_key = requested_x_key(row)
        if x_key is None:
            continue
        grouped[x_key].append(row)

    entries = []
    for x_key in sorted(grouped.keys(), key=lambda item: (item[0], item[1], item[2])):
        candidates = grouped[x_key]
        sorted_candidates = sorted(
            candidates,
            key=lambda row: (
                row["routing_steps_f"],
                row["duration_s_f"] if row.get("duration_s_f") is not None else math.inf,
                to_int(row.get("run_id")) if to_int(row.get("run_id")) is not None else math.inf,
            ),
        )
        best = sorted_candidates[0]
        best_routing_steps = best["routing_steps_f"]
        tied_best_count = sum(
            1 for row in candidates if row.get("routing_steps_f") == best_routing_steps
        )

        entries.append(
            {
                "circuit_graph_label": requested_x_label(x_key),
                "circuit": x_key[0],
                "graph_x": x_key[1],
                "graph_y": x_key[2],
                "run_id": best.get("run_id", ""),
                "routing_steps": best_routing_steps,
                "duration_seconds": best.get("duration_s_f"),
                "tied_best_count": tied_best_count,
                "safe_passage": best.get("safe_passage_norm", "") or "n/a",
                "magic_placement": best.get("placement_detail", "") or "n/a",
                "border_distance_percentage": best.get("border_pct_f"),
                "number_of_magic_states": best.get("magic_states_f"),
                "gaussian_strategy": best.get("gaussian_strategy_norm", "") or "n/a",
                "magic_high": best.get("magic_high_f"),
                "magic_low": best.get("magic_low_f"),
                "cnot_high": best.get("cnot_high_f"),
                "cnot_low": best.get("cnot_low_f"),
                "mapped_gaussian_weight": best.get("mapped_gaussian_weight_f"),
                "base_gaussian_weight": best.get("base_gaussian_weight_f"),
                "external_weight": best.get("external_weight_f"),
                "routing_strategy": best.get("routing_strategy", "") or "n/a",
            }
        )

    return entries


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


def write_best_gaussian_execution_table(entries, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, filename)
    fieldnames = [
        "circuit_graph_label",
        "circuit",
        "graph_x",
        "graph_y",
        "run_id",
        "routing_steps",
        "duration_seconds",
        "tied_best_count",
        "safe_passage",
        "magic_placement",
        "border_distance_percentage",
        "number_of_magic_states",
        "gaussian_strategy",
        "magic_high",
        "magic_low",
        "cnot_high",
        "cnot_low",
        "mapped_gaussian_weight",
        "base_gaussian_weight",
        "external_weight",
        "routing_strategy",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

    return entries, csv_path


def write_summary(rows, csv_files, output_dir, generated, skipped=None, distinct_info=None):
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
        if csv_files:
            f.write("CSV files used:\n")
            for csv_file in csv_files:
                f.write(f"  - {csv_file}\n")
            f.write("\n")
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

        if distinct_info is not None:
            f.write("Distinct merge:\n")
            f.write(f"  - merged csv: {distinct_info['merged_csv_path']}\n")
            f.write(f"  - duplicates csv: {distinct_info['duplicates_csv_path']}\n")
            f.write(f"  - input rows: {distinct_info['input_rows']}\n")
            f.write(f"  - merged rows: {distinct_info['merged_rows']}\n")
            f.write(f"  - repeated configurations: {distinct_info['repeated_configuration_groups']}\n")
            f.write(f"  - repeated configurations with same result: {distinct_info['same_result_duplicate_groups']}\n")
            f.write(f"  - repeated configurations with different results: {distinct_info['different_result_duplicate_groups']}\n")
            f.write(f"  - exact duplicates removed: {distinct_info['duplicate_rows_removed']}\n")
            f.write(f"  - conflicting configurations: {distinct_info['conflicting_groups']}\n")
            f.write(f"  - rows written to duplicates csv: {distinct_info['conflicting_rows']}\n\n")

        if skipped:
            f.write("---\n\nSkipped plots:\n")
            for item in skipped:
                f.write(f"  - {item['filename']}: {item['reason']}\n")


def write_report_markdown(
    output_dir,
    generated,
    skipped,
    top_gaussian_weight_entries,
    top_gaussian_weight_csv_path,
    best_gaussian_weight_profile_entries,
    best_gaussian_weight_profile_csv_path,
    gaussian_relative_weight_gap_entries,
    gaussian_relative_weight_gap_csv_path,
    best_gaussian_execution_entries,
    best_gaussian_execution_csv_path,
    best_mapping_entries,
    best_mapping_csv_path,
    best_mapping_exit0_entries,
    best_mapping_exit0_csv_path,
):
    report_path = os.path.join(output_dir, "report.md")
    by_name = {
        strip_plot_number(os.path.basename(p)): os.path.relpath(p, output_dir).replace(os.sep, "/")
        for p in generated
    }
    skipped_by_name = {item["filename"]: item["reason"] for item in (skipped or [])}

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Benchmark Charts\n\n")
        f.write("Generated plot set from benchmark CSV files.\n\n")
        f.write("See also `summary.txt` for aggregate metrics.\n\n")
        for filename, caption in REPORT_PLOTS:
            output_name = strip_plot_number(filename)
            if output_name not in by_name:
                continue
            f.write(f"## {caption}\n\n")
            f.write(f"![{caption}]({by_name[output_name]})\n\n")

        if skipped_by_name:
            f.write("## Skipped Plots\n\n")
            for filename, caption in REPORT_PLOTS:
                output_name = strip_plot_number(filename)
                if output_name not in skipped_by_name:
                    continue
                f.write(f"- `{output_name}` ({caption}): {skipped_by_name[output_name]}\n")
            f.write("\n")

        if top_gaussian_weight_entries:
            csv_name = os.path.basename(top_gaussian_weight_csv_path)
            profile_csv_name = os.path.basename(best_gaussian_weight_profile_csv_path)
            relative_gap_csv_name = os.path.basename(gaussian_relative_weight_gap_csv_path)
            f.write("## Top Gaussian Weight Configurations\n\n")
            f.write(
                "Top 3 gaussian weight configurations per `circuit x graph-dimensions`. "
                "Each configuration is ranked by its best observed `routing_steps`, then "
                "by mean routing steps across the successful runs that used the same "
                "weight tuple.\n\n"
            )
            if best_gaussian_weight_profile_entries:
                f.write(
                    f"Readable best-profile CSV export: `{profile_csv_name}`\n\n"
                )
            if gaussian_relative_weight_gap_entries:
                f.write(
                    f"Relative weight-gap CSV export: `{relative_gap_csv_name}`\n\n"
                )
            f.write(f"CSV export: `{csv_name}`\n\n")

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
        help=(
            "Single CSV input file. Accepts a full path, a CSV filename, or a stem without "
            "the .csv extension. If set and --output-dir is omitted, plots are written to "
            "<csv_dir>/<csv_name>_plots."
        ),
    )
    input_group.add_argument(
        "--distinct",
        action="store_true",
        help=(
            "Analyze every CSV directly inside benchmarks/results, merging duplicate executions "
            "by configuration only. Rows with the same configuration but different status or "
            "routing_steps are all kept and exported to merging_duplicates.csv."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for generated plots",
    )
    parser.add_argument(
        "--heatmap",
        action="store_true",
        help="Also generate the heatmap group under heatmap/.",
    )
    parser.add_argument(
        "--time",
        action="store_true",
        help=(
            "Also generate the time_analysis/ folder (overview dashboard, runtime "
            "scatters, status/circuit summary, box plots). Off by default."
        ),
    )
    axis_group = parser.add_argument_group("heatmap x-axis filters")
    for flags, dest, _axis_slug, label in HEATMAP_AXIS_FLAG_SPECS:
        axis_group.add_argument(
            *flags,
            dest=dest,
            action="store_true",
            help=(
                f"Generate heatmap/dashboard/barplot items for x-axis '{label}' only; "
                "can be combined with other x-axis filters and implies --heatmap."
            ),
        )
    parser.add_argument(
        "--circuit",
        action="store_true",
        help="Also generate the per-circuit barplots under barplots_by_circuit/.",
    )
    parser.add_argument(
        "--gaussian",
        action="store_true",
        help=(
            "Also generate per-configuration gaussian relative-weight-gap heatmaps "
            f"under {GAUSSIAN_DIR}/ (one slice per gaussian strategy, safe passage, "
            "n magic states, confidence, placement value)."
        ),
    )
    parser.add_argument("--worker-heatmap-batch", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--worker-heatmap-phase", default="source", choices=["source", "dashboard"], help=argparse.SUPPRESS)
    parser.add_argument("--worker-csv", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--worker-output-dir", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--worker-result", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--worker-heatmap-axes", default="", help=argparse.SUPPRESS)
    parser.add_argument(
        "--no-subprocess-heatmaps",
        action="store_true",
        help="Disable subprocess batching for heatmap generation (slower memory release).",
    )
    parser.add_argument(
        "--heatmap-batch-size",
        type=int,
        default=HEATMAP_BATCH_SIZE,
        help=f"Number of heatmap items processed per subprocess batch (default: {HEATMAP_BATCH_SIZE}).",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of heatmap subprocess batches to run concurrently (default: 1).",
    )
    parser.add_argument(
        "--align",
        action="store_true",
        help=(
            "Align heatmap/barplot cells to the configs common to every populated cell "
            "(non-success metrics only). When omitted, each cell aggregates over all its "
            "own configs."
        ),
    )
    args = parser.parse_args()

    global INCLUDE_TIME_ANALYSIS
    INCLUDE_TIME_ANALYSIS = bool(args.time)

    if args.worker_heatmap_batch is not None:
        run_heatmap_worker(args)
        return

    selected_heatmap_axes = selected_heatmap_axis_slugs(args)
    selected_heatmap_items = filter_heatmap_items_by_axes(
        REQUESTED_HEATMAP_ITEMS,
        selected_heatmap_axes,
    )

    if not args.csv and not args.distinct:
        print("No input specified. Pass --csv for one file or --distinct for the benchmarks/results CSVs.")
        return

    importMatplotlib()

    plt.style.use("seaborn-v0_8-whitegrid")

    if args.csv:
        csv_path = resolve_csv_input_path(args.csv)
        input_files = [csv_path]
        output_dir = args.output_dir or default_output_dir_for_single_csv(csv_path, args.distinct)
    else:
        input_files = filter_distinct_input_files(
            sorted(glob.glob(os.path.join(DEFAULT_RESULTS_DIR, "*.csv")))
        )
        output_dir = args.output_dir or default_output_dir_for_glob(args.distinct)

    raw_rows, raw_fieldnames, csv_files = load_raw_rows_from_files(input_files)

    if not raw_rows:
        if args.csv:
            raise RuntimeError(f"No valid rows found in CSV: {args.csv}")
        raise RuntimeError(f"No valid rows found under {DEFAULT_RESULTS_DIR}")

    distinct_info = None
    if args.distinct:
        raw_rows, distinct_info = merge_rows_distinct(
            raw_rows,
            raw_fieldnames,
            output_dir,
            len(csv_files),
        )

    rows = prepare_rows_for_analysis(raw_rows)
    del raw_rows
    _trim_heap()
    register_extra_statuses(rows)
    rows_no_timeout = exclude_timeout_rows(rows)
    remove_obsolete_plots(output_dir)
    clear_per_circuit_barplot_dir(output_dir)

    generated = []
    skipped = []

    analysis_start = len(generated)

    # Row subsets needed by heatmap/gaussian/etc. downstream — always computed.
    rows_success_with_routing = [
        r for r in rows_no_timeout if r["success"] and r["routing_steps_f"] is not None
    ]
    rows_with_duration = [r for r in rows_no_timeout if r["duration_s_f"] is not None]
    rows_success_with_non_routed = [
        r for r in rows_no_timeout if r["success"] and r["non_routed_layer_pct_f"] is not None
    ]

    if INCLUDE_TIME_ANALYSIS:
        rows_gaussian_with_routing = [
            r for r in rows_success_with_routing if r["mapping_type_norm"] == "gaussian"
        ]
        rows_magicaware_with_routing = [
            r
            for r in rows_success_with_routing
            if r["mapping_type_norm"] == "magic_aware"
            and r["magic_aware_strategy_norm"] in REQUESTED_MAGIC_AWARE_STRATEGIES
        ]
        plot_overview_dashboard(rows_no_timeout, output_dir, generated)
        plot_status_and_exit(rows, output_dir, generated)
        plot_summary_tables(rows_no_timeout, output_dir, generated)
        boxplot_by_category(
            rows_success_with_routing,
            "circuit_name",
            "routing_steps_f",
            "Routing Steps by Circuit (Success Only)",
            "routing steps",
            "03_box_routing_by_circuit.png",
            output_dir,
            generated,
            skipped,
        )
        boxplot_by_category(
            rows_no_timeout,
            "circuit_name",
            "duration_s_f",
            "Duration by Circuit",
            "duration_seconds",
            "04_box_elapsed_by_circuit.png",
            output_dir,
            generated,
            skipped,
        )
        boxplot_by_category(
            rows_success_with_non_routed,
            "circuit_name",
            "non_routed_layer_pct_f",
            "Non-routed Layer % by Circuit (Success Only)",
            "non-routed layer pct (%)",
            "05_box_non_routed_pct_by_circuit.png",
            output_dir,
            generated,
            skipped,
        )
        plot_elapsed_by_gaussian_strategy(rows_no_timeout, output_dir, generated, skipped)
        plot_gaussian_weight_combinations(rows_gaussian_with_routing, output_dir, generated, skipped)
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
            skipped,
        )
        scatter_plot(
            rows_no_timeout,
            "interaction_pressure_f",
            "duration_s_f",
            "status",
            "Interaction Pressure vs Duration",
            "interaction_pressure",
            "duration_seconds",
            "12_scatter_pressure_vs_elapsed.png",
            output_dir,
            generated,
            skipped,
        )
        plot_runtime_qubits_plus_gates(rows_no_timeout, output_dir, generated, skipped)
        plot_runtime_grouped_factors(
            rows_no_timeout,
            output_dir,
            generated,
            skipped,
        )
        plot_requested_comparisons(rows_success_with_routing, output_dir, generated, skipped)
        print(f"[analysis plots] {len(generated) - analysis_start} done", flush=True)
    else:
        print("[analysis plots] skipped (pass --time to generate time_analysis/)", flush=True)
    if args.heatmap or selected_heatmap_axes:
        clear_heatmap_dir(output_dir)
        heatmap_csv_path = (
            os.path.abspath(input_files[0])
            if (
                not args.no_subprocess_heatmaps
                and not args.distinct
                and len(input_files) == 1
            )
            else None
        )
        plot_requested_heatmaps(
            rows_no_timeout,
            rows_success_with_routing,
            rows_with_duration,
            output_dir,
            generated,
            skipped,
            csv_path=heatmap_csv_path,
            batch_size=args.heatmap_batch_size,
            parallel=args.parallel,
            align=args.align,
            heatmap_items=selected_heatmap_items,
            axis_slugs=selected_heatmap_axes,
        )
        plot_best_config_counts_by_heatmap_axis(
            rows_success_with_routing,
            output_dir,
            generated,
            skipped,
            heatmap_items=selected_heatmap_items,
        )
        plot_best_non_routed_config_counts_by_heatmap_axis(
            rows_success_with_non_routed,
            output_dir,
            generated,
            skipped,
            heatmap_items=selected_heatmap_items,
        )
        plot_timeout_counts_by_heatmap_axis(
            rows,
            output_dir,
            generated,
            skipped,
            heatmap_items=selected_heatmap_items,
        )
    if args.circuit:
        plot_axis_barplots_by_circuit(
            rows_no_timeout,
            rows_success_with_routing,
            output_dir,
            generated,
            skipped,
            batch_size=args.heatmap_batch_size,
            align=args.align,
            axis_slugs=selected_heatmap_axes,
        )
    if args.gaussian:
        plot_gaussian_weight_summary_dashboard(rows, output_dir, generated, skipped)
    top_gaussian_weight_entries, top_gaussian_weight_groups = top_gaussian_weight_config_entries(
        rows,
        top_n=3,
    )
    top_gaussian_weight_entries, top_gaussian_weight_csv_path = write_top_gaussian_weight_config_table(
        top_gaussian_weight_entries,
        os.path.join(output_dir, "helpers"),
        "top_gaussian_weight_configs_by_circuit_dimension.csv",
    )
    best_gaussian_weight_profile_rows = best_gaussian_weight_profile_entries(
        top_gaussian_weight_entries,
    )
    best_gaussian_weight_profile_rows, best_gaussian_weight_profile_csv_path = write_best_gaussian_weight_profile_table(
        best_gaussian_weight_profile_rows,
        os.path.join(output_dir, "helpers"),
        "best_gaussian_weight_profile_by_circuit_dimension.csv",
    )
    gaussian_relative_weight_gap_rows = gaussian_relative_weight_gap_entries(
        best_gaussian_weight_profile_rows,
    )
    gaussian_relative_weight_gap_rows, gaussian_relative_weight_gap_csv_path = write_gaussian_relative_weight_gap_table(
        gaussian_relative_weight_gap_rows,
        os.path.join(output_dir, "helpers"),
        "best_gaussian_relative_weight_gaps.csv",
    )
    gaussian_best_entries = best_gaussian_execution_entries(rows)
    gaussian_best_entries, gaussian_best_csv_path = write_best_gaussian_execution_table(
        gaussian_best_entries,
        os.path.join(output_dir, "csv"),
        "best_gaussian_execution_by_circuit_dimension.csv",
    )
    best_mapping_entries = best_mapping_table_entries(rows)
    best_mapping_entries, best_mapping_csv_path = write_best_mapping_table(
        best_mapping_entries,
        os.path.join(output_dir, "csv"),
        "best_mapping_by_circuit_dimension.csv",
    )
    best_mapping_exit0_entries = best_mapping_table_entries_exit0_only(rows)
    best_mapping_exit0_entries, best_mapping_exit0_csv_path = write_best_mapping_table(
        best_mapping_exit0_entries,
        os.path.join(output_dir, "csv"),
        "best_mapping_by_circuit_dimension_all_families_exit0.csv",
    )
    write_summary(rows, csv_files, output_dir, generated, skipped, distinct_info=distinct_info)
    if WRITE_REPORT_MD:
        write_report_markdown(
            output_dir,
            generated,
            skipped,
            top_gaussian_weight_entries,
            top_gaussian_weight_csv_path,
            best_gaussian_weight_profile_rows,
            best_gaussian_weight_profile_csv_path,
            gaussian_relative_weight_gap_rows,
            gaussian_relative_weight_gap_csv_path,
            gaussian_best_entries,
            gaussian_best_csv_path,
            best_mapping_entries,
            best_mapping_csv_path,
            best_mapping_exit0_entries,
            best_mapping_exit0_csv_path,
        )
    skipped_msg = f", {len(skipped)} skipped" if skipped else ""
    print(f"Created {len(generated)} plots{skipped_msg} in: {output_dir}")


if __name__ == "__main__":
    main()
