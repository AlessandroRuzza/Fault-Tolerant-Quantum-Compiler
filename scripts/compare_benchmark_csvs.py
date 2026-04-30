#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


SUCCESS_STATUSES = {"success", "ok", "ok_no_routing_metric"}
IDENTITY_KEYS = (
    "circuit",
    "graph_x",
    "graph_y",
    "mapping_type",
    "magic_aware_strategy",
    "gaussian_strategy",
    "size_moltiplier",
    "gaussian_confidence",
    "safe_passage_strategy",
    "magic_state_placement_strategy",
    "border_distance_percentage",
    "number_of_magic_states",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two benchmark CSV files on shared benchmark cases."
    )
    parser.add_argument("baseline_csv", type=Path, help="Baseline CSV path.")
    parser.add_argument("candidate_csv", type=Path, help="Candidate CSV path.")
    parser.add_argument(
        "--baseline-label",
        default="baseline",
        help="Display label for the baseline CSV.",
    )
    parser.add_argument(
        "--candidate-label",
        default="candidate",
        help="Display label for the candidate CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional markdown output path.",
    )
    parser.add_argument(
        "--examples",
        type=int,
        default=12,
        help="Number of example rows to include for status flips and routing deltas.",
    )
    return parser.parse_args()


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_status(value: object) -> str:
    return normalize_text(value).lower()


def is_success(row: dict[str, str]) -> bool:
    return normalize_status(row.get("status")) in SUCCESS_STATUSES


def to_float(value: object) -> float | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    if math.isnan(result):
        return None
    return result


def to_int(value: object) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        numeric = to_float(text)
        if numeric is None:
            return None
        return int(numeric)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        for row_index, row in enumerate(reader):
            entry = dict(row)
            entry["_row_index"] = str(row_index)
            rows.append(entry)
        return rows


def identity_key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(normalize_text(row.get(key)) for key in IDENTITY_KEYS)


def sort_key(row: dict[str, str]) -> tuple[int, int]:
    run_id = to_int(row.get("run_id"))
    row_index = to_int(row.get("_row_index"))
    return (
        run_id if run_id is not None else 10**12,
        row_index if row_index is not None else 10**12,
    )


def group_rows(rows: list[dict[str, str]]) -> dict[tuple[str, ...], list[dict[str, str]]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[identity_key(row)].append(row)
    for key in grouped:
        grouped[key].sort(key=sort_key)
    return grouped


def build_pairs(
    baseline_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, str]],
) -> tuple[
    list[tuple[tuple[str, ...], dict[str, str], dict[str, str]]],
    list[tuple[tuple[str, ...], dict[str, str]]],
    list[tuple[tuple[str, ...], dict[str, str]]],
]:
    baseline_grouped = group_rows(baseline_rows)
    candidate_grouped = group_rows(candidate_rows)

    shared_pairs: list[tuple[tuple[str, ...], dict[str, str], dict[str, str]]] = []
    baseline_only: list[tuple[tuple[str, ...], dict[str, str]]] = []
    candidate_only: list[tuple[tuple[str, ...], dict[str, str]]] = []

    for key in sorted(set(baseline_grouped) | set(candidate_grouped)):
        baseline_group = baseline_grouped.get(key, [])
        candidate_group = candidate_grouped.get(key, [])
        pair_count = min(len(baseline_group), len(candidate_group))

        for index in range(pair_count):
            shared_pairs.append((key, baseline_group[index], candidate_group[index]))

        for extra in baseline_group[pair_count:]:
            baseline_only.append((key, extra))

        for extra in candidate_group[pair_count:]:
            candidate_only.append((key, extra))

    return shared_pairs, baseline_only, candidate_only


def success_rate(rows: list[dict[str, str]]) -> float | None:
    if not rows:
        return None
    return 100.0 * sum(1 for row in rows if is_success(row)) / len(rows)


def median_routing(rows: list[dict[str, str]]) -> float | None:
    values = [
        value
        for row in rows
        if is_success(row)
        for value in [to_float(row.get("routing_steps"))]
        if value is not None
    ]
    if not values:
        return None
    return float(statistics.median(values))


def median_duration(rows: list[dict[str, str]]) -> float | None:
    values = [
        value
        for row in rows
        for value in [to_float(row.get("duration_seconds"))]
        if value is not None
    ]
    if not values:
        return None
    return float(statistics.median(values))


def format_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def md_cell(value: object) -> str:
    text = normalize_text(value)
    if not text:
        return "-"
    return text.replace("|", "\\|").replace("\n", "<br>")


def label_safe_placement(key: tuple[str, ...]) -> str:
    safe = key[6] or "unknown"
    placement = key[7] or "unknown"
    return f"{safe} / {placement}"


def short_case_label(key: tuple[str, ...]) -> str:
    circuit, graph_x, graph_y = key[0], key[1], key[2]
    mapping = key[3]
    mapping_detail = key[4] if mapping == "magic_aware" else key[5] if mapping == "gaussian" else ""
    safe = key[6]
    placement = key[7]
    border = key[8]
    magic_states = key[9]
    mapping_text = f"{mapping}:{mapping_detail}" if mapping_detail else mapping
    return (
        f"{circuit} | {graph_x}x{graph_y} | {mapping_text} | "
        f"{safe} | {placement} | border={border} | magic={magic_states}"
    )


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, float | None | int]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[label_safe_placement(identity_key(row))].append(row)

    summary: dict[str, dict[str, float | None | int]] = {}
    for label, subset in grouped.items():
        summary[label] = {
            "count": len(subset),
            "success_rate": success_rate(subset),
            "median_routing": median_routing(subset),
            "median_duration": median_duration(subset),
        }
    return dict(sorted(summary.items()))


def build_markdown(
    baseline_path: Path,
    candidate_path: Path,
    baseline_label: str,
    candidate_label: str,
    baseline_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, str]],
    shared_pairs: list[tuple[tuple[str, ...], dict[str, str], dict[str, str]]],
    baseline_only: list[tuple[tuple[str, ...], dict[str, str]]],
    candidate_only: list[tuple[tuple[str, ...], dict[str, str]]],
    example_limit: int,
) -> str:
    status_transitions: Counter[tuple[str, str]] = Counter()
    status_transitions_by_safe: Counter[tuple[str, str, str]] = Counter()
    routing_deltas: list[tuple[float, tuple[str, ...], dict[str, str], dict[str, str]]] = []
    routing_deltas_by_safe: dict[str, list[float]] = defaultdict(list)
    flip_examples: list[tuple[tuple[str, ...], dict[str, str], dict[str, str]]] = []

    for key, baseline_row, candidate_row in shared_pairs:
        baseline_status = normalize_status(baseline_row.get("status")) or "unknown"
        candidate_status = normalize_status(candidate_row.get("status")) or "unknown"
        status_transitions[(baseline_status, candidate_status)] += 1
        status_transitions_by_safe[(key[6] or "unknown", baseline_status, candidate_status)] += 1

        if baseline_status != candidate_status and len(flip_examples) < example_limit:
            flip_examples.append((key, baseline_row, candidate_row))

        baseline_routing = to_float(baseline_row.get("routing_steps"))
        candidate_routing = to_float(candidate_row.get("routing_steps"))
        if (
            is_success(baseline_row)
            and is_success(candidate_row)
            and baseline_routing is not None
            and candidate_routing is not None
        ):
            delta = candidate_routing - baseline_routing
            if delta != 0:
                routing_deltas.append((delta, key, baseline_row, candidate_row))
                routing_deltas_by_safe[key[6] or "unknown"].append(delta)

    routing_deltas.sort(key=lambda item: (abs(item[0]), item[0]), reverse=True)

    baseline_summary = summarize_rows(baseline_rows)
    candidate_summary = summarize_rows(candidate_rows)
    safe_labels = sorted(set(baseline_summary) | set(candidate_summary))

    lines: list[str] = []
    lines.append("# Benchmark CSV Comparison")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- {baseline_label}: `{baseline_path}`")
    lines.append(f"- {candidate_label}: `{candidate_path}`")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Rows in {baseline_label}: {len(baseline_rows)}")
    lines.append(f"- Rows in {candidate_label}: {len(candidate_rows)}")
    lines.append(f"- Shared comparable rows: {len(shared_pairs)}")
    lines.append(f"- Rows only in {baseline_label}: {len(baseline_only)}")
    lines.append(f"- Rows only in {candidate_label}: {len(candidate_only)}")
    lines.append("")
    lines.append("## Success And Routing By Safe Passage / Placement")
    lines.append("")
    lines.append(
        "| case group | "
        f"{baseline_label} success % | {candidate_label} success % | "
        f"{baseline_label} median routing | {candidate_label} median routing | "
        f"{baseline_label} median duration | {candidate_label} median duration |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for label in safe_labels:
        baseline_stats = baseline_summary.get(label, {})
        candidate_stats = candidate_summary.get(label, {})
        lines.append(
            f"| {label} | "
            f"{format_float(baseline_stats.get('success_rate'))} | "
            f"{format_float(candidate_stats.get('success_rate'))} | "
            f"{format_float(baseline_stats.get('median_routing'))} | "
            f"{format_float(candidate_stats.get('median_routing'))} | "
            f"{format_float(baseline_stats.get('median_duration'))} | "
            f"{format_float(candidate_stats.get('median_duration'))} |"
        )
    lines.append("")
    lines.append("## Status Transitions")
    lines.append("")
    lines.append(f"| {baseline_label} -> {candidate_label} | count |")
    lines.append("| --- | ---: |")
    for (baseline_status, candidate_status), count in sorted(
        status_transitions.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        lines.append(f"| `{baseline_status}` -> `{candidate_status}` | {count} |")
    lines.append("")
    lines.append("### Status Transitions By Safe Passage")
    lines.append("")
    lines.append("| safe passage | transition | count |")
    lines.append("| --- | --- | ---: |")
    for (safe, baseline_status, candidate_status), count in sorted(
        status_transitions_by_safe.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        lines.append(
            f"| `{safe}` | `{baseline_status}` -> `{candidate_status}` | {count} |"
        )
    lines.append("")
    lines.append("## Routing Delta On Shared Successful Cases")
    lines.append("")
    if routing_deltas:
        lines.append(
            f"`candidate routing - baseline routing` over shared rows where both runs succeeded."
        )
        lines.append("")
        lines.append("| safe passage | compared cases with delta | median delta | min delta | max delta |")
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for safe, values in sorted(routing_deltas_by_safe.items()):
            lines.append(
                f"| `{safe}` | {len(values)} | "
                f"{format_float(statistics.median(values))} | "
                f"{format_float(min(values))} | "
                f"{format_float(max(values))} |"
            )
        lines.append("")
        lines.append("### Largest Routing Deltas")
        lines.append("")
        lines.append(
            "| case | baseline status / routing | candidate status / routing | delta |"
        )
        lines.append("| --- | --- | --- | ---: |")
        for delta, key, baseline_row, candidate_row in routing_deltas[:example_limit]:
            lines.append(
                f"| {md_cell(short_case_label(key))} | "
                f"`{normalize_status(baseline_row.get('status'))}` / "
                f"`{normalize_text(baseline_row.get('routing_steps')) or '-'}` | "
                f"`{normalize_status(candidate_row.get('status'))}` / "
                f"`{normalize_text(candidate_row.get('routing_steps')) or '-'}` | "
                f"{format_float(delta)} |"
            )
    else:
        lines.append("No routing deltas on shared successful rows.")
    lines.append("")
    lines.append("## Example Status Flips")
    lines.append("")
    if flip_examples:
        lines.append(
            "| case | baseline status | candidate status | baseline error excerpt | candidate error excerpt |"
        )
        lines.append("| --- | --- | --- | --- | --- |")
        for key, baseline_row, candidate_row in flip_examples:
            baseline_error = normalize_text(baseline_row.get("error_excerpt")) or "-"
            candidate_error = normalize_text(candidate_row.get("error_excerpt")) or "-"
            lines.append(
                f"| {md_cell(short_case_label(key))} | "
                f"`{normalize_status(baseline_row.get('status'))}` | "
                f"`{normalize_status(candidate_row.get('status'))}` | "
                f"{md_cell(baseline_error)} | {md_cell(candidate_error)} |"
            )
    else:
        lines.append("No status flips found.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    baseline_rows = load_rows(args.baseline_csv)
    candidate_rows = load_rows(args.candidate_csv)
    shared_pairs, baseline_only, candidate_only = build_pairs(baseline_rows, candidate_rows)

    markdown = build_markdown(
        args.baseline_csv,
        args.candidate_csv,
        args.baseline_label,
        args.candidate_label,
        baseline_rows,
        candidate_rows,
        shared_pairs,
        baseline_only,
        candidate_only,
        args.examples,
    )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown + "\n", encoding="utf-8")
        print(f"Wrote comparison report to {args.output}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
