#!/usr/bin/env python3
"""
Create a simplified, fixed-width CSV view from a benchmark CSV.
Output is written under project_root/tmp by default.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a benchmark CSV to a readable CSV.")
    parser.add_argument("input_csv", type=Path, help="Input CSV path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output CSV path. Default: project_root/tmp/<input>_readable.csv",
    )
    return parser.parse_args()


def normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def pick_value(row: dict[str, str], *candidates: str) -> str:
    for key in candidates:
        value = (row.get(key) or "").strip()
        if value:
            return value

    normalized_lookup = {
        normalize_key(key): (value or "").strip() for key, value in row.items() if key
    }
    for key in candidates:
        value = normalized_lookup.get(normalize_key(key), "")
        if value:
            return value
    return ""


def build_dimensions(row: dict[str, str]) -> str:
    dimensions = pick_value(row, "graph_dimensions", "dimensions", "graph dimensions")
    if dimensions:
        return dimensions

    graph_x = pick_value(row, "graph_x", "x", "graph x")
    graph_y = pick_value(row, "graph_y", "y", "graph y")
    if graph_x and graph_y:
        return f"{graph_x}x{graph_y}"
    return ""


def resolve_input_csv(raw_input: Path, project_root: Path) -> Path:
    """Resolve flexible input names to an existing CSV file path.

    Supports:
    - exact paths
    - paths without .csv suffix
    - bare file stems (e.g. 'ex1_runs') searched in common project folders
    """
    candidates: list[Path] = []
    seen: set[Path] = set()

    def add_candidate(path: Path) -> None:
        normalized = path.resolve()
        if normalized in seen:
            return
        seen.add(normalized)
        candidates.append(path)

    # 1) User-provided path (as-is and with .csv suffix)
    add_candidate(raw_input)
    if raw_input.suffix.lower() != ".csv":
        add_candidate(raw_input.with_suffix(".csv"))

    # 2) Common folders under project root
    for base in (
        project_root,
        project_root / "benchmarks",
        project_root / "benchmarks" / "results",
    ):
        add_candidate(base / raw_input)
        if raw_input.suffix.lower() != ".csv":
            add_candidate(base / raw_input.with_suffix(".csv"))

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return raw_input


def compute_column_widths(
    rows: list[dict[str, str]], fields: list[str]
) -> list[int]:
    widths = [len(field) for field in fields]
    for row in rows:
        for index, field in enumerate(fields):
            value = row.get(field, "") or ""
            widths[index] = max(widths[index], len(value))
    return widths


def write_aligned_csv(
    out_handle, fields: list[str], rows: list[dict[str, str]], widths: list[int]
) -> None:
    def format_row(values: list[str]) -> str:
        padded = (value.ljust(width) for value, width in zip(values, widths))
        return ", ".join(padded)

    out_handle.write(format_row(fields) + "\n")
    for row in rows:
        values = [(row.get(field, "") or "") for field in fields]
        out_handle.write(format_row(values) + "\n")


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    input_csv = resolve_input_csv(args.input_csv, project_root)
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV non trovato: {input_csv}")

    tmp_dir = project_root / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    output_csv = args.output or (tmp_dir / f"{input_csv.stem}_readable.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    output_fields = [
        "circuit",
        "dimensions",
        "mapping_type",
        "magic_aware_strategy",
        "gaussian_strategy",
        "size_moltiplier",
        "gaussian_confidence",
        "safe_passage_strategy",
        "magic_state_placement_strategy",
        "border_distance_percentage",
        "number_of_magic_states",
        "routing_strategy",
        "t_routing_mode",
        "routing_steps",
        "time_duration",
        "error_excerpt",
    ]

    rows_written = 0
    rows: list[dict[str, str]] = []
    with input_csv.open("r", newline="", encoding="utf-8") as in_handle:
        reader = csv.DictReader(in_handle)
        if not reader.fieldnames:
            raise ValueError("Il CSV in input non contiene intestazione.")

        for row in reader:
            rows.append(
                {
                    "circuit": pick_value(row, "circuit"),
                    "dimensions": build_dimensions(row),
                    "mapping_type": pick_value(row, "mapping_type", "mapping type"),
                    "magic_aware_strategy": pick_value(
                        row,
                        "magic_aware_strategy",
                        "magic aware strategy",
                        "macig_awarestrategy",
                        "macig awarestrategy",
                    ),
                    "gaussian_strategy": pick_value(
                        row, "gaussian_strategy", "gaussian strategy"
                    ),
                    "size_moltiplier": pick_value(
                        row, "size_moltiplier", "SIZE_MOLTIPLIER", "size_multiplier"
                    ),
                    "gaussian_confidence": pick_value(
                        row, "gaussian_confidence", "GAUSSIAN_CONFIDENCE"
                    ),
                    "safe_passage_strategy": pick_value(
                        row,
                        "safe_passage_strategy",
                        "safe passage strategy",
                        "safe passage startegy",
                    ),
                    "magic_state_placement_strategy": pick_value(
                        row,
                        "magic_state_placement_strategy",
                        "magic state placement strategy",
                    ),
                    "border_distance_percentage": pick_value(
                        row, "border_distance_percentage", "border distance percentage"
                    ),
                    "number_of_magic_states": pick_value(
                        row,
                        "number_of_magic_states",
                        "number of magic states",
                        "number of magi cstates",
                    ),
                    "routing_strategy": pick_value(
                        row,
                        "routing_strategy",
                        "routing strategy",
                    ),
                    "t_routing_mode": pick_value(
                        row,
                        "t_routing_mode",
                        "t-routing-mode",
                        "t routing mode",
                    ),
                    "routing_steps": pick_value(row, "routing_steps", "routing steps"),
                    "time_duration": pick_value(
                        row,
                        "time_duration",
                        "time duration",
                        "duration_seconds",
                        "duration seconds",
                    ),
                    "error_excerpt": pick_value(row, "error_excerpt", "error excerpt"),
                }
            )
            rows_written += 1

    widths = compute_column_widths(rows, output_fields)
    with output_csv.open("w", newline="", encoding="utf-8") as out_handle:
        write_aligned_csv(out_handle, output_fields, rows, widths)

    print(f"Input: {input_csv}")
    print(f"Output: {output_csv}")
    print(f"Rows written: {rows_written}")


if __name__ == "__main__":
    main()
