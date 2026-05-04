#!/usr/bin/env python3

import argparse
import csv
import glob
import math
import os
import re
import statistics
import warnings
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

def importMatplotlib():
    global plt, np, Line2D, TwoSlopeNorm
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
    ("size_moltiplier_f", "size_moltiplier", "size multiplier", "size_moltiplier"),
    ("gaussian_confidence_f", "gaussian_confidence", "gaussian confidence", "gaussian_confidence"),
    ("safe_passage_norm", "safe_passage_strategy", "safe passage strategy", "safe_passage_strategy"),
)
DEFAULT_RESULTS_DIR = os.path.join("benchmarks", "results")
DEFAULT_CSV_GLOB = os.path.join(DEFAULT_RESULTS_DIR, "**", "*.csv")
OBSOLETE_PLOT_FILENAMES = {
    "13_heatmap_success_safe_vs_placement.png",
    "23_heatmap_success_safe_vs_mapping_type.png",
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
)
REPORT_PLOTS = [
    ("00_overview_dashboard.png", "Overview dashboard"),
    ("01_status_and_exit_codes.png", "Run status and exit codes"),
    ("02_circuit_summary_bars.png", "Circuit-level summary"),
    ("03_box_routing_by_circuit.png", "Routing steps by circuit"),
    ("04_box_elapsed_by_circuit.png", "Duration by circuit"),
    ("05_box_routing_by_placement.png", "Routing by magic placement"),
    ("06_box_routing_by_safe_passage.png", "Routing by safe passage"),
    ("07_box_routing_by_magic_strategy.png", "Routing by magic-aware strategy"),
    ("08_scatter_elapsed_vs_routing_by_circuit.png", "Duration vs routing"),
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
    ("36_runtime_vs_qubits_by_size_moltiplier.png", "Duration vs qubits by size multiplier"),
    ("37_runtime_vs_qubits_by_gaussian_confidence.png", "Duration vs qubits by gaussian confidence"),
    ("38_runtime_vs_qubits_by_safe_passage_strategy.png", "Duration vs qubits by safe passage"),
    ("39_runtime_vs_gates_by_size_moltiplier.png", "Duration vs gates by size multiplier"),
    ("40_runtime_vs_gates_by_gaussian_confidence.png", "Duration vs gates by gaussian confidence"),
    ("41_runtime_vs_gates_by_safe_passage_strategy.png", "Duration vs gates by safe passage"),
    ("42_runtime_vs_graph_nodes_by_size_moltiplier.png", "Duration vs graph size by size multiplier"),
    ("43_runtime_vs_graph_nodes_by_gaussian_confidence.png", "Duration vs graph size by gaussian confidence"),
    ("44_runtime_vs_graph_nodes_by_safe_passage_strategy.png", "Duration vs graph size by safe passage"),
    (
        "45_heatmap_routing_safe_passage_vs_gaussian_confidence.png",
        "Routing heatmap: safe passage x gaussian confidence",
    ),
    (
        "46_heatmap_routing_gaussian_confidence_vs_size_moltiplier.png",
        "Routing heatmap: gaussian confidence x size multiplier",
    ),
    ("09_scatter_density_vs_routing.png", "Density vs routing"),
    ("10_scatter_magic_states_vs_routing.png", "Magic state parameter vs routing"),
    ("11_scatter_border_vs_routing_center_circle.png", "Border distance vs routing"),
    ("12_scatter_pressure_vs_elapsed.png", "Interaction pressure vs duration"),
    (
        "13_heatmap_success_safe_vs_placement_excluding_timeouts.png",
        "Success heatmap: safe passage x placement (timeouts excluded)",
    ),
    ("14_heatmap_routing_safe_vs_placement.png", "Routing heatmap: safe passage x placement"),
    (
        "25_heatmap_timeout_safe_vs_placement.png",
        "Timeout heatmap: safe passage x placement",
    ),
    (
        "23_heatmap_success_safe_vs_mapping_type_excluding_timeouts.png",
        "Success heatmap: safe passage x mapping type (timeouts excluded)",
    ),
    ("24_heatmap_routing_safe_vs_mapping_type.png", "Routing heatmap: safe passage x mapping type"),
    (
        "26_heatmap_timeout_safe_vs_mapping_type.png",
        "Timeout heatmap: safe passage x mapping type",
    ),
    ("15_heatmap_routing_magic_vs_safe.png", "Routing heatmap: magic strategy x safe passage"),
    ("16_heatmap_success_by_grid_xy.png", "Success heatmap by grid size"),
    ("17_experiment_set_routing_gaussian_homogeneous.png", "Experiment set: gaussian + homogeneous"),
    ("18_experiment_set_routing_magicaware_homogeneous.png", "Experiment set: magic-aware + homogeneous"),
    ("19_box_routing_by_gaussian_strategy.png", "Routing by gaussian strategy"),
    ("47_box_elapsed_by_gaussian_strategy.png", "Duration by gaussian strategy"),
    ("20_heatmap_routing_gaussian_strategy_vs_placement.png", "Routing heatmap: gaussian strategy x placement"),
    ("21_box_gaussian_weight_combinations_vs_routing.png", "Routing by gaussian weight combinations"),
    ("30_heatmap_best_gaussian_weight_profiles.png", "Best gaussian weight profile map"),
    ("31_heatmap_best_gaussian_relative_weight_gaps.png", "Best gaussian relative weight gaps"),
    ("22_experiment_set_routing_all_mappings.png", "Experiment set: all mappings"),
]
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
DISTINCT_IGNORED_COLUMNS = {
    "routing_steps",
    "total_routing_steps",
    "timeout_reached",
    "status",
    "exit_code",
    "duration_seconds",
    "elapsed_ms",
    "error_excerpt",
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

            if "run_id" not in normalized_fieldnames or "status" not in normalized_fieldnames:
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


def prepare_rows_for_analysis(raw_rows):
    rows = []

    for raw in raw_rows:
        row = dict(raw)
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
        row["size_moltiplier_f"] = to_float(row.get("size_moltiplier"))
        if row["size_moltiplier_f"] is not None:
            row["size_moltiplier_label"] = format_number_label(row["size_moltiplier_f"])
        else:
            row["size_moltiplier_label"] = ""
        row["gaussian_confidence_f"] = to_float(row.get("gaussian_confidence"))
        if row["gaussian_confidence_f"] is not None:
            row["gaussian_confidence_label"] = format_number_label(row["gaussian_confidence_f"])
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

    return rows


def load_rows_from_files(files):
    raw_rows, _, accepted_files = load_raw_rows_from_files(files)
    return prepare_rows_for_analysis(raw_rows), accepted_files


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


def record_skipped_plot(skipped, filename, reason):
    if skipped is None:
        return
    skipped.append({"filename": filename, "reason": reason})


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
            if any(filename.startswith(prefix) for prefix in OBSOLETE_PLOT_PREFIXES):
                filenames.add(filename)

    for filename in filenames:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            continue
        try:
            os.remove(path)
        except OSError as exc:
            warnings.warn(f"Could not remove obsolete plot {path}: {exc}")


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

    bars = axs[1].bar(circuits, [circuit_counts[c] for c in circuits], color="#577590")
    axs[1].set_title("Runs by Circuit")
    axs[1].tick_params(axis="x", rotation=35)
    annotate_bars(axs[1], bars)

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
    for status in sorted({p[2] for p in points}):
        subset = [p for p in points if p[2] == status]
        if not subset:
            continue
        axs[5].scatter(
            [p[0] for p in subset],
            [p[1] for p in subset],
            s=28,
            alpha=0.7,
            label=legend_label_with_sample_count(status_display_label(status), len(subset)),
            color=status_color(status),
        )
    axs[5].set_title(f"Duration vs Routing Steps (n={len(points)})")
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
    ax.legend(fontsize=8)
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
        label for label, _ in sorted(combo_labels.items(), key=lambda item: item[1])
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
        ax.legend(title="gaussian strategy", fontsize=8)

    save_fig(fig, output_dir, "21_box_gaussian_weight_combinations_vs_routing.png", generated)


def gaussian_weight_config_label(config, multiline=False, verbose=False):
    magic_high, magic_low, cnot_high, cnot_low, mapped_weight, base_weight = config
    separator = "\n" if multiline else " | "
    if verbose:
        return separator.join(
            [
                f"magic H/L {format_number_label(magic_high)}/{format_number_label(magic_low)}",
                f"CNOT H/L {format_number_label(cnot_high)}/{format_number_label(cnot_low)}",
                f"gauss map/base {format_number_label(mapped_weight)}/{format_number_label(base_weight)}",
            ]
        )
    return separator.join(
        [
            f"M {format_number_label(magic_high)}/{format_number_label(magic_low)}",
            f"C {format_number_label(cnot_high)}/{format_number_label(cnot_low)}",
            f"G {format_number_label(mapped_weight)}/{format_number_label(base_weight)}",
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
                item["combo"],
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
            magic_high, magic_low, cnot_high, cnot_low, mapped_weight, base_weight = combo
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
    ]
    data = np.array(
        [
            [float(entry[field]) for _, field in weight_columns]
            for entry in entries
        ],
        dtype=float,
    )
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
    image = ax.imshow(data, aspect="auto", cmap="YlGnBu")

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
            value = float(entry[field])
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
    ]
    values = sorted(
        {
            float(entry[field])
            for entry in best_profile_entries
            for _, field in weight_columns
        }
    )
    counts = Counter()
    for entry in best_profile_entries:
        for label, field in weight_columns:
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
    ]
    entries = []

    for row_label, row_field in weight_columns:
        for col_label, col_field in weight_columns:
            gaps = [
                float(entry[row_field]) - float(entry[col_field])
                for entry in best_profile_entries
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


def plot_gaussian_relative_weight_gap_heatmap(entries, output_dir, generated, skipped=None):
    filename = "31_heatmap_best_gaussian_relative_weight_gaps.png"
    if not entries:
        record_skipped_plot(
            skipped,
            filename,
            "no best gaussian weight profile rows available",
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
    absolute = np.array(
        [
            [by_pair[(row_label, col_label)]["mean_abs_gap"] for col_label in labels]
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

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.8), constrained_layout=False)
    fig.subplots_adjust(left=0.13, right=0.94, top=0.76, bottom=0.17, wspace=0.34)
    fig.suptitle(
        f"Relative Distances Between Weights in Best Gaussian Configurations (n={total_profiles})",
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
    max_abs_gap = float(np.max(absolute)) if absolute.size else 1.0
    signed_norm = TwoSlopeNorm(vmin=-max_signed, vcenter=0, vmax=max_signed)
    images = [
        axes[0].imshow(signed, cmap="RdBu_r", norm=signed_norm),
        axes[1].imshow(absolute, cmap="YlGnBu", vmin=0, vmax=max_abs_gap),
    ]
    titles = ["Mean Signed Gap", "Mean Absolute Distance"]
    colorbar_labels = ["row - column", "|row - column|"]

    for ax_idx, ax in enumerate(axes):
        matrix = signed if ax_idx == 0 else absolute
        ax.set_title(titles[ax_idx], fontsize=12, pad=12)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8.5)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=8.5)
        ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=1.25)
        ax.tick_params(axis="both", length=0)
        ax.tick_params(which="minor", bottom=False, left=False)

        max_value = float(np.max(np.abs(matrix))) if matrix.size else 0.0
        for row_idx in range(matrix.shape[0]):
            for col_idx in range(matrix.shape[1]):
                value = matrix[row_idx, col_idx]
                if row_idx == col_idx:
                    text = "-"
                    color = "#64748B"
                else:
                    text = f"{value:+.2f}" if ax_idx == 0 else f"{value:.2f}".rstrip("0").rstrip(".")
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

        cbar = fig.colorbar(images[ax_idx], ax=ax, fraction=0.046, pad=0.035)
        cbar.ax.tick_params(labelsize=8)
        cbar.set_label(colorbar_labels[ax_idx], fontsize=9)

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    generated.append(path)


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
                f"{gaussian_weight_config_label((entry['magic_high'], entry['magic_low'], entry['cnot_high'], entry['cnot_low'], entry['mapped_gaussian_weight'], entry['base_gaussian_weight']), multiline=True, verbose=True)}"
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
    title,
    colorbar_label,
    filename,
    output_dir,
    generated,
    skipped=None,
    value_format="{:.2f}",
    subset_transform=None,
):
    row_labels = sorted({heatmap_axis_value(r, row_key) for r in rows})
    col_labels = sorted({heatmap_axis_value(r, col_key) for r in rows})
    if not row_labels or not col_labels:
        record_skipped_plot(
            skipped,
            filename,
            f"no rows available for heatmap axes {row_key} x {col_key}",
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
            text = f"{metric_text}\nn={sample_count}"
            if np.isnan(val):
                color = "#999999"
            else:
                red, green, blue, _ = im.cmap(im.norm(val))
                luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
                color = "white" if luminance < 0.45 else "#111111"
            ax.text(j, i, text, ha="center", va="center", color=color, fontsize=7, linespacing=0.9)

    save_fig(fig, output_dir, filename, generated)


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
    csv_path = os.path.join(output_dir, "32_runtime_vs_qubits_plus_gates_with_timeouts.csv")
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
    os.makedirs(output_dir, exist_ok=True)
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
    ax.legend(handles=legend_handles, loc="best", fontsize=9, ncols=2, frameon=True)

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
    csv_path = os.path.join(output_dir, "36_runtime_grouped_factors.csv")
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
    os.makedirs(output_dir, exist_ok=True)
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
    ax.legend(fontsize=8, frameon=True)
    save_fig(fig, output_dir, filename, generated)


def plot_runtime_grouped_factors(rows, output_dir, generated, skipped=None):
    entries = runtime_measurement_entries(rows)
    if not entries:
        record_skipped_plot(
            skipped,
            "36_runtime_vs_qubits_by_size_moltiplier.png",
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
        lambda subset: median_of([r["routing_steps_f"] for r in subset]),
        "Median Routing Steps by Safe Passage and Gaussian Confidence",
        "median routing steps",
        "45_heatmap_routing_safe_passage_vs_gaussian_confidence.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.0f}",
    )


def plot_gaussian_confidence_size_moltiplier_routing_heatmap(rows, output_dir, generated, skipped=None):
    heatmap_rows = [
        row
        for row in rows
        if row.get("mapping_type_norm") == "gaussian"
        and row.get("gaussian_confidence_label")
        and row.get("size_moltiplier_label")
        and row.get("success")
        and row.get("routing_steps_f") is not None
    ]

    make_pair_heatmap(
        heatmap_rows,
        "gaussian_confidence_label",
        "size_moltiplier_label",
        lambda subset: median_of([r["routing_steps_f"] for r in subset]),
        "Median Routing Steps by Gaussian Confidence and Size Multiplier",
        "median routing steps",
        "46_heatmap_routing_gaussian_confidence_vs_size_moltiplier.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.0f}",
    )


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

        f.write("Generated plots:\n")
        for p in generated:
            f.write(f"  - {p}\n")

        if skipped:
            f.write("\nSkipped plots:\n")
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
    by_name = {os.path.basename(p): p for p in generated}
    skipped_by_name = {item["filename"]: item["reason"] for item in (skipped or [])}

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Benchmark Charts\n\n")
        f.write("Generated plot set from benchmark CSV files.\n\n")
        f.write("See also `summary.txt` for aggregate metrics.\n\n")
        for filename, caption in REPORT_PLOTS:
            if filename not in by_name:
                continue
            f.write(f"## {caption}\n\n")
            f.write(f"![{caption}]({filename})\n\n")

        if skipped_by_name:
            f.write("## Skipped Plots\n\n")
            for filename, caption in REPORT_PLOTS:
                if filename not in skipped_by_name:
                    continue
                f.write(f"- `{filename}` ({caption}): {skipped_by_name[filename]}\n")
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
            "<csv_dir>/<csv_name>_plots or <csv_name>_merge_plots when --distinct is used."
        ),
    )
    input_group.add_argument(
        "--csv-glob",
        default=DEFAULT_CSV_GLOB,
        help=(
            "Glob for CSV inputs (default: benchmarks/results/**/*.csv). "
            "With --distinct, only CSV files directly inside benchmarks/results are used."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for generated plots",
    )
    parser.add_argument(
        "--distinct",
        action="store_true",
        help=(
            "When loading multiple CSV rows, merge duplicate executions by configuration only. "
            "Rows with the same configuration but different status or routing_steps are all kept "
            "and exported to merging_duplicates.csv."
        ),
    )
    args = parser.parse_args()

    importMatplotlib()

    plt.style.use("seaborn-v0_8-whitegrid")

    if args.csv:
        csv_path = resolve_csv_input_path(args.csv)
        input_files = [csv_path]
        output_dir = args.output_dir or default_output_dir_for_single_csv(csv_path, args.distinct)
    else:
        input_files = sorted(glob.glob(args.csv_glob, recursive=True))
        if args.distinct:
            input_files = filter_distinct_input_files(input_files)
        output_dir = args.output_dir or default_output_dir_for_glob(args.distinct)

    raw_rows, raw_fieldnames, csv_files = load_raw_rows_from_files(input_files)

    if not raw_rows:
        if args.csv:
            raise RuntimeError(f"No valid rows found in CSV: {args.csv}")
        raise RuntimeError(f"No valid rows found for glob: {args.csv_glob}")

    distinct_info = None
    if args.distinct:
        raw_rows, distinct_info = merge_rows_distinct(
            raw_rows,
            raw_fieldnames,
            output_dir,
            len(csv_files),
        )

    rows = prepare_rows_for_analysis(raw_rows)
    remove_obsolete_plots(output_dir)

    generated = []
    skipped = []

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
        skipped,
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
        skipped,
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
        skipped,
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
        skipped,
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
        skipped,
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
        skipped,
    )
    plot_elapsed_by_gaussian_strategy(rows, output_dir, generated, skipped)

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
        skipped,
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
        skipped,
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
        skipped,
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
        skipped,
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
        skipped,
    )

    plot_runtime_qubits_plus_gates(rows, output_dir, generated, skipped)
    runtime_grouped_factors_csv_path = plot_runtime_grouped_factors(rows, output_dir, generated, skipped)
    plot_gaussian_confidence_safe_passage_routing_heatmap(rows, output_dir, generated, skipped)
    plot_gaussian_confidence_size_moltiplier_routing_heatmap(rows, output_dir, generated, skipped)

    make_pair_heatmap(
        rows,
        "safe_passage_strategy",
        "placement",
        success_rate,
        "Success Rate Heatmap (Timeouts Excluded)",
        "success rate (%)",
        "13_heatmap_success_safe_vs_placement_excluding_timeouts.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.1f}",
        subset_transform=exclude_timeout_rows,
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
        skipped,
    )
    make_pair_heatmap(
        rows,
        "safe_passage_strategy",
        "placement",
        timeout_count,
        "Timeout Heatmap by Safe Passage and Placement",
        "timeout count",
        "25_heatmap_timeout_safe_vs_placement.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.0f}",
    )
    make_pair_heatmap(
        rows,
        "safe_passage_strategy",
        "mapping_type_norm",
        success_rate,
        "Success Rate Heatmap by Safe Passage and Mapping Type (Timeouts Excluded)",
        "success rate (%)",
        "23_heatmap_success_safe_vs_mapping_type_excluding_timeouts.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.1f}",
        subset_transform=exclude_timeout_rows,
    )
    make_pair_heatmap(
        rows_success_with_routing,
        "safe_passage_strategy",
        "mapping_type_norm",
        lambda subset: mean_of([r["routing_steps_f"] for r in subset]),
        "Mean Routing Steps Heatmap by Safe Passage and Mapping Type",
        "mean routing steps",
        "24_heatmap_routing_safe_vs_mapping_type.png",
        output_dir,
        generated,
        skipped,
    )
    make_pair_heatmap(
        rows,
        "safe_passage_strategy",
        "mapping_type_norm",
        timeout_count,
        "Timeout Heatmap by Safe Passage and Mapping Type",
        "timeout count",
        "26_heatmap_timeout_safe_vs_mapping_type.png",
        output_dir,
        generated,
        skipped,
        value_format="{:.0f}",
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
        skipped,
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
        skipped,
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
        skipped,
        value_format="{:.0f}",
    )
    plot_requested_comparisons(rows_success_with_routing, output_dir, generated, skipped)
    plot_gaussian_weight_combinations(rows_gaussian_with_routing, output_dir, generated, skipped)
    top_gaussian_weight_entries, top_gaussian_weight_groups = top_gaussian_weight_config_entries(
        rows,
        top_n=3,
    )
    top_gaussian_weight_entries, top_gaussian_weight_csv_path = write_top_gaussian_weight_config_table(
        top_gaussian_weight_entries,
        output_dir,
        "top_gaussian_weight_configs_by_circuit_dimension.csv",
    )
    best_gaussian_weight_profile_rows = best_gaussian_weight_profile_entries(
        top_gaussian_weight_entries,
    )
    best_gaussian_weight_profile_rows, best_gaussian_weight_profile_csv_path = write_best_gaussian_weight_profile_table(
        best_gaussian_weight_profile_rows,
        output_dir,
        "best_gaussian_weight_profile_by_circuit_dimension.csv",
    )
    plot_best_gaussian_weight_profile_heatmap(
        best_gaussian_weight_profile_rows,
        output_dir,
        generated,
        skipped,
    )
    gaussian_relative_weight_gap_rows = gaussian_relative_weight_gap_entries(
        best_gaussian_weight_profile_rows,
    )
    gaussian_relative_weight_gap_rows, gaussian_relative_weight_gap_csv_path = write_gaussian_relative_weight_gap_table(
        gaussian_relative_weight_gap_rows,
        output_dir,
        "best_gaussian_relative_weight_gaps.csv",
    )
    plot_gaussian_relative_weight_gap_heatmap(
        gaussian_relative_weight_gap_rows,
        output_dir,
        generated,
        skipped,
    )

    gaussian_best_entries = best_gaussian_execution_entries(rows)
    gaussian_best_entries, gaussian_best_csv_path = write_best_gaussian_execution_table(
        gaussian_best_entries,
        output_dir,
        "best_gaussian_execution_by_circuit_dimension.csv",
    )
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
    write_summary(rows, csv_files, output_dir, generated, skipped, distinct_info=distinct_info)
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
    print(f"Generated {len(generated)} plots in: {output_dir}")
    if skipped:
        print(f"Skipped {len(skipped)} plots:")
        for item in skipped:
            print(f"{item['filename']}: {item['reason']}")
    for path in generated:
        print(path)
    print(best_gaussian_weight_profile_csv_path)
    print(gaussian_relative_weight_gap_csv_path)
    print(top_gaussian_weight_csv_path)
    print(gaussian_best_csv_path)
    print(best_mapping_csv_path)
    print(best_mapping_exit0_csv_path)
    if runtime_grouped_factors_csv_path is not None:
        print(runtime_grouped_factors_csv_path)
    if distinct_info is not None:
        print(
            "Repeated configurations found: "
            f"{distinct_info['repeated_configuration_groups']}"
        )
        print(
            "Repeated configurations with same result: "
            f"{distinct_info['same_result_duplicate_groups']}"
        )
        print(
            "Repeated configurations with different results: "
            f"{distinct_info['different_result_duplicate_groups']}"
        )
        print(f"Exact duplicate rows removed: {distinct_info['duplicate_rows_removed']}")
        print("CSV files used to build merged csv:")
        for csv_file in csv_files:
            print(csv_file)
        print(distinct_info["merged_csv_path"])
        print(distinct_info["duplicates_csv_path"])
    print(os.path.join(output_dir, "summary.txt"))


if __name__ == "__main__":
    main()
