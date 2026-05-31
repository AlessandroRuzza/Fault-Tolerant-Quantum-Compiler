#!/usr/bin/env python3
"""Analyze whether Gaussian weight profiles transfer across border percentages.

This is intentionally separate from generate_benchmark_plots.py: it is a focused
diagnostic for the fine/cube sweep where border percentage and weights are both
part of the tested configuration.
"""

import argparse
import csv
import math
import os
import statistics
from collections import Counter, defaultdict


SUCCESS_STATUSES = {"ok", "ok_no_routing_metric", "success"}
WEIGHT_FIELDS = (
    "magic_high",
    "magic_low",
    "cnot_high",
    "cnot_low",
    "mapped_gaussian_weight",
    "base_gaussian_weight",
    "external_weight",
)


def to_float(value):
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if math.isnan(value):
        return None
    return value


def to_int(value):
    value = to_float(value)
    if value is None:
        return None
    return int(value)


def format_number(value):
    if value is None:
        return ""
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.10g}"


def combo_label(combo):
    return (
        f"M {format_number(combo[0])}/{format_number(combo[1])} | "
        f"C {format_number(combo[2])}/{format_number(combo[3])} | "
        f"G {format_number(combo[4])}/{format_number(combo[5])} | "
        f"E {format_number(combo[6])}"
    )


def gaussian_sort_key(combo):
    return tuple(-math.inf if value is None else value for value in combo)


def x_key_from_row(row):
    graph_x = to_int(row.get("graph_x") or row.get("x"))
    graph_y = to_int(row.get("graph_y") or row.get("y"))
    circuit = os.path.basename((row.get("circuit") or "").strip())
    if not circuit or graph_x is None or graph_y is None:
        return None
    label = (row.get("circuit_graph_label") or "").strip()
    if not label:
        label = f"{circuit}-{graph_x}x{graph_y}"
    return circuit, graph_x, graph_y, label


def combo_from_row(row):
    values = []
    for field in WEIGHT_FIELDS:
        value = to_float(row.get(field))
        if value is None:
            return None
        values.append(value)
    return tuple(values)


def update_stats(stats, metric, duration):
    stats["count"] += 1
    stats["metric_sum"] += metric
    if metric < stats["best_metric"]:
        stats["best_metric"] = metric
        stats["best_duration"] = duration
    elif metric == stats["best_metric"] and duration is not None:
        if stats["best_duration"] is None or duration < stats["best_duration"]:
            stats["best_duration"] = duration


def new_stats():
    return {
        "count": 0,
        "metric_sum": 0.0,
        "best_metric": math.inf,
        "best_duration": None,
    }


def load_group_stats(path, metric_field):
    stats_by_key = defaultdict(new_stats)
    observed_borders = set()
    row_count = 0
    usable_count = 0

    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            row_count += 1
            if (row.get("mapping_type") or "").strip().lower() != "gaussian":
                continue
            if (row.get("status") or "").strip().lower() not in SUCCESS_STATUSES:
                continue
            metric = to_float(row.get(metric_field))
            if metric is None:
                continue
            x_key = x_key_from_row(row)
            combo = combo_from_row(row)
            border = to_float(row.get("border_distance_percentage"))
            if x_key is None or combo is None or border is None:
                continue
            duration = to_float(row.get("duration_seconds"))
            update_stats(stats_by_key[(x_key, border, combo)], metric, duration)
            observed_borders.add(border)
            usable_count += 1

    return stats_by_key, sorted(observed_borders), row_count, usable_count


def best_by_x_border(stats_by_key):
    grouped = defaultdict(list)
    for (x_key, border, combo), stats in stats_by_key.items():
        grouped[(x_key, border)].append((combo, stats))

    best = {}
    for key, entries in grouped.items():
        entries.sort(
            key=lambda item: (
                item[1]["best_metric"],
                item[1]["metric_sum"] / item[1]["count"],
                item[1]["best_duration"] if item[1]["best_duration"] is not None else math.inf,
                gaussian_sort_key(item[0]),
            )
        )
        combo, stats = entries[0]
        best[key] = combo, stats
    return best


def mean(values):
    return sum(values) / len(values) if values else None


def write_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def profile_summary_rows(best, borders):
    rows = []
    for border in borders:
        winners = [(x_key, combo, stats) for (x_key, b), (combo, stats) in best.items() if b == border]
        if not winners:
            continue
        combos = [combo for _x_key, combo, _stats in winners]
        means = [mean([combo[idx] for combo in combos]) for idx in range(len(WEIGHT_FIELDS))]
        base_mean = means[5]
        normalized = [(value - base_mean + 1.0) if value is not None and base_mean is not None else None for value in means]
        top_combo, top_count = Counter(combos).most_common(1)[0]
        row = {
            "border_percentage": format_number(border),
            "winner_group_count": len(winners),
            "unique_winner_combo_count": len(set(combos)),
            "top_winner_combo_count": top_count,
            "top_winner_combo_pct": top_count / len(winners),
            "top_winner_combo": combo_label(top_combo),
            "mean_best_metric": mean([stats["best_metric"] for _x_key, _combo, stats in winners]),
        }
        for field, value, norm_value in zip(WEIGHT_FIELDS, means, normalized):
            row[f"mean_{field}"] = value
            row[f"normalized_{field}"] = norm_value
        rows.append(row)
    return rows


def transfer_rows(stats_by_key, best, borders):
    per_dimension = []
    matrix_rows = []
    x_keys = sorted({x_key for x_key, _border in best.keys()}, key=lambda item: (item[0], item[1], item[2]))

    for source_border in borders:
        for target_border in borders:
            deltas = []
            relative_deltas = []
            source_metrics = []
            target_best_metrics = []
            missing = 0
            ties = 0
            wins = 0

            for x_key in x_keys:
                source = best.get((x_key, source_border))
                target = best.get((x_key, target_border))
                if source is None or target is None:
                    continue
                source_combo, _source_best_stats = source
                target_combo, target_best_stats = target
                transferred_stats = stats_by_key.get((x_key, target_border, source_combo))
                if transferred_stats is None:
                    missing += 1
                    continue

                transferred_metric = transferred_stats["best_metric"]
                target_metric = target_best_stats["best_metric"]
                delta = transferred_metric - target_metric
                rel_delta = delta / target_metric if target_metric not in (0, None) else (0.0 if delta == 0 else None)
                deltas.append(delta)
                source_metrics.append(transferred_metric)
                target_best_metrics.append(target_metric)
                if rel_delta is not None:
                    relative_deltas.append(rel_delta)
                if delta <= 1e-12:
                    ties += 1
                    if source_combo == target_combo:
                        wins += 1

                per_dimension.append(
                    {
                        "circuit_graph_label": x_key[3],
                        "circuit": x_key[0],
                        "graph_x": x_key[1],
                        "graph_y": x_key[2],
                        "source_border": format_number(source_border),
                        "target_border": format_number(target_border),
                        "source_combo": combo_label(source_combo),
                        "target_best_combo": combo_label(target_combo),
                        "transferred_metric": transferred_metric,
                        "target_best_metric": target_metric,
                        "delta_metric": delta,
                        "relative_delta_metric": rel_delta,
                        "same_combo_as_target_best": source_combo == target_combo,
                    }
                )

            matrix_rows.append(
                {
                    "source_border": format_number(source_border),
                    "target_border": format_number(target_border),
                    "paired_group_count": len(deltas),
                    "missing_group_count": missing,
                    "tie_or_win_count": ties,
                    "exact_same_combo_count": wins,
                    "tie_or_win_pct": ties / len(deltas) if deltas else None,
                    "mean_transferred_metric": mean(source_metrics),
                    "mean_target_best_metric": mean(target_best_metrics),
                    "mean_delta_metric": mean(deltas),
                    "median_delta_metric": statistics.median(deltas) if deltas else None,
                    "max_delta_metric": max(deltas) if deltas else None,
                    "mean_relative_delta_metric": mean(relative_deltas),
                    "median_relative_delta_metric": statistics.median(relative_deltas) if relative_deltas else None,
                }
            )

    return matrix_rows, per_dimension


def top_combo_rows(best, borders, top_n):
    rows = []
    for border in borders:
        counter = Counter(combo for (_x_key, b), (combo, _stats) in best.items() if b == border)
        total = sum(counter.values())
        for rank, (combo, count) in enumerate(counter.most_common(top_n), start=1):
            row = {
                "border_percentage": format_number(border),
                "rank": rank,
                "winner_count": count,
                "winner_pct": count / total if total else None,
                "weight_config": combo_label(combo),
            }
            for field, value in zip(WEIGHT_FIELDS, combo):
                row[field] = value
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        default="benchmarks/results/gaussian_weight_tuning_fine_cube_runs.csv",
        help="fine/cube benchmark CSV to analyze",
    )
    parser.add_argument(
        "--metric",
        default="non_routed_layer_pct",
        help="metric to minimize when selecting best configs",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmarks/results/gaussian_weight_tuning_fine_cube_runs_plots/percentage_weight_transfer",
        help="directory where diagnostic CSVs are written",
    )
    parser.add_argument("--top-n", type=int, default=20, help="top winner combos to list per border")
    args = parser.parse_args()

    stats_by_key, borders, row_count, usable_count = load_group_stats(args.csv, args.metric)
    best = best_by_x_border(stats_by_key)
    matrix, per_dimension = transfer_rows(stats_by_key, best, borders)
    profiles = profile_summary_rows(best, borders)
    top_combos = top_combo_rows(best, borders, args.top_n)

    write_csv(
        os.path.join(args.output_dir, "border_profile_summary.csv"),
        list(profiles[0].keys()) if profiles else ["border_percentage"],
        profiles,
    )
    write_csv(
        os.path.join(args.output_dir, "border_weight_transfer_matrix.csv"),
        list(matrix[0].keys()) if matrix else ["source_border", "target_border"],
        matrix,
    )
    write_csv(
        os.path.join(args.output_dir, "border_weight_transfer_by_dimension.csv"),
        list(per_dimension[0].keys()) if per_dimension else ["circuit_graph_label"],
        per_dimension,
    )
    write_csv(
        os.path.join(args.output_dir, "top_winner_combos_by_border.csv"),
        list(top_combos[0].keys()) if top_combos else ["border_percentage"],
        top_combos,
    )

    print(f"Input rows: {row_count}")
    print(f"Usable rows: {usable_count}")
    print(f"Borders: {', '.join(format_number(border) for border in borders)}")
    print(f"Grouped config cells: {len(stats_by_key)}")
    print(f"Best (dimension, border) cells: {len(best)}")
    print(f"Wrote: {args.output_dir}")


if __name__ == "__main__":
    main()
