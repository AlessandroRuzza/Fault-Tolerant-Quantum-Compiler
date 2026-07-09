#!/usr/bin/env python3
"""Consolidate one or more WISQ-comparison CSVs into two best-per-circuit CSVs.

Each input is a CSV produced by compare_wisq_parity.py (columns: circuit, ...,
my_routing_steps, wisq_routing_steps, wisq_status, ratio_wisq_over_mine, ...).
For every circuit, this picks — independently — the single best result across
ALL inputs for:

  1. OUR compiler: lowest my_routing_steps (tiebreak: lowest my_duration_s).
     Output keeps circuit identity, all config columns, and every my_* column;
     wisq_* columns and the ratio are dropped.
  2. WISQ:         lowest wisq_routing_steps (tiebreak: lowest wisq_duration_s).
     Output keeps ONLY WISQ-relevant columns (circuit, n_qubits, every wisq_*
     column, grid_grown_for_wisq); our execution/config columns are dropped.
  3. OUR compiler by space-time volume: lowest my_V = my_x * my_y *
     my_routing_steps (tiebreak: lowest my_duration_s). Same columns as (1)
     plus a computed my_V column.
  4. WISQ by space-time volume: lowest wisq_V = wisq_x * wisq_y *
     wisq_routing_steps (tiebreak: lowest wisq_duration_s). Same columns as (2)
     plus a computed wisq_V column.

All outputs get a `source_file` column for provenance. Because the picks are
independent, the best rows for a circuit may come from different input files.

A row counts for a side only when its rank value (routing steps, or every
factor of the volume product) parses as a number. Input files lacking the
required columns are skipped with a warning.

Output CSVs are ALWAYS written inside the repository's data/ directory.

Inputs under any old_results/ directory are rejected: only current results
(data/results/) are valid sources.

Usage:
    python scripts/wisq_compare/extract_best_per_circuit.py data/results/*wisq*.csv
    python scripts/wisq_compare/extract_best_per_circuit.py data/results/*_wisq.csv \
        --ours-output best_ours_per_circuit.csv --wisq-output best_wisq_per_circuit.csv \
        --volume-ours-output best_volume_ours_per_circuit.csv \
        --volume-wisq-output best_volume_wisq_per_circuit.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # scripts/wisq_compare/ -> root
DATA_DIR = REPO_ROOT / "data"

CIRCUIT_COL = "circuit"


def is_wisq_column(col: str) -> bool:
    """Columns kept in the WISQ output: circuit identity, circuit size, and
    anything describing WISQ. Everything about OUR execution/config is dropped."""
    return (
        col == CIRCUIT_COL
        or col == "n_qubits"
        or col == "grid_grown_for_wisq"
        or col.startswith("wisq")
    )


def is_ours_column(col: str) -> bool:
    """Columns kept in the OURS output: circuit identity plus everything that is
    NOT WISQ-specific. Config columns (gaussian_strategy, routing_strategy, ...)
    stay because they say which variant produced the best result."""
    return (
        col == CIRCUIT_COL
        or not (
            col.startswith("wisq")
            or col == "grid_grown_for_wisq"
            or col == "ratio_wisq_over_mine"
        )
    )


def to_float(value: str | None):
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def steps_rank(rank_col: str):
    """Rank by a single routing-steps column."""
    def rank(row: dict):
        return to_float(row.get(rank_col))
    return rank


def volume_rank(x_col: str, y_col: str, steps_col: str, out_col: str):
    """Rank by space-time volume x * y * routing_steps. Stores the computed
    volume in row[out_col] so it lands in the output CSV."""
    def rank(row: dict):
        x = to_float(row.get(x_col))
        y = to_float(row.get(y_col))
        steps = to_float(row.get(steps_col))
        if x is None or y is None or steps is None:
            return None
        volume = x * y * steps
        row[out_col] = int(volume)
        return volume
    return rank


class BestPicker:
    """Tracks the best row per circuit for one side (ours or wisq)."""

    def __init__(self, name: str, rank_cols: list[str], rank_fn, tiebreak_col: str,
                 keep_col, extra_cols: list[str] | None = None) -> None:
        self.name = name
        self.rank_cols = rank_cols      # input columns required for ranking
        self.rank_fn = rank_fn          # row -> float | None
        self.tiebreak_col = tiebreak_col
        self.keep_col = keep_col
        self.extra_cols = extra_cols or []  # computed columns appended to output
        # best[circuit] = (rank, tiebreak, row_dict)
        self.best: dict[str, tuple[float, float, dict]] = {}
        self.field_order: list[str] = []

    def has_required(self, header: list[str]) -> bool:
        return all(col in header for col in self.rank_cols)

    def observe_header(self, header: list[str]) -> None:
        for col in header:
            if self.keep_col(col) and col not in self.field_order:
                self.field_order.append(col)
        for col in self.extra_cols:
            if col not in self.field_order:
                self.field_order.append(col)

    def offer(self, circuit: str, row: dict) -> bool:
        rank = self.rank_fn(row)
        if rank is None:
            return False  # no result on this side → cannot rank/include
        tiebreak = to_float(row.get(self.tiebreak_col))
        tiebreak = tiebreak if tiebreak is not None else float("inf")
        key = (rank, tiebreak)
        cur = self.best.get(circuit)
        if cur is None or key < (cur[0], cur[1]):
            self.best[circuit] = (rank, tiebreak, row)
            return True
        return False

    def write(self, out_name: str) -> Path | None:
        if not self.best:
            print(f"No rows with a {self.name} result found in the given inputs.",
                  file=sys.stderr)
            return None
        fields = list(self.field_order)
        if "source_file" not in fields:
            fields.append("source_file")
        out_path = DATA_DIR / Path(out_name).name
        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for circuit in sorted(self.best):
                writer.writerow(self.best[circuit][2])
        print(f"Wrote {len(self.best)} circuit(s) to {out_path}")
        return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="One or more WISQ-comparison CSV files.")
    parser.add_argument("--ours-output", default="best_ours_per_circuit.csv",
                        help="Output CSV name for OUR best results. Always written "
                             "inside data/ (any directory part is ignored). "
                             "Default: best_ours_per_circuit.csv")
    parser.add_argument("--wisq-output", default="best_wisq_per_circuit.csv",
                        help="Output CSV name for WISQ best results. Always written "
                             "inside data/ (any directory part is ignored). "
                             "Default: best_wisq_per_circuit.csv")
    parser.add_argument("--volume-ours-output", default="best_volume_ours_per_circuit.csv",
                        help="Output CSV name for OUR best-by-volume results. "
                             "Default: best_volume_ours_per_circuit.csv")
    parser.add_argument("--volume-wisq-output", default="best_volume_wisq_per_circuit.csv",
                        help="Output CSV name for WISQ best-by-volume results. "
                             "Default: best_volume_wisq_per_circuit.csv")
    args = parser.parse_args()

    pickers = [
        (BestPicker("OURS", ["my_routing_steps"],
                    steps_rank("my_routing_steps"),
                    "my_duration_s", is_ours_column),
         args.ours_output),
        (BestPicker("WISQ", ["wisq_routing_steps"],
                    steps_rank("wisq_routing_steps"),
                    "wisq_duration_s", is_wisq_column),
         args.wisq_output),
        (BestPicker("OURS volume", ["my_x", "my_y", "my_routing_steps"],
                    volume_rank("my_x", "my_y", "my_routing_steps", "my_V"),
                    "my_duration_s", is_ours_column, extra_cols=["my_V"]),
         args.volume_ours_output),
        (BestPicker("WISQ volume", ["wisq_x", "wisq_y", "wisq_routing_steps"],
                    volume_rank("wisq_x", "wisq_y", "wisq_routing_steps", "wisq_V"),
                    "wisq_duration_s", is_wisq_column, extra_cols=["wisq_V"]),
         args.volume_wisq_output),
    ]

    for raw in args.inputs:
        path = Path(raw)
        if any(part.startswith("old_results") for part in path.resolve().parts):
            print(f"[skip] {path}: old_results/ inputs are not allowed "
                  f"(use data/results/ only)", file=sys.stderr)
            continue
        if not path.exists():
            print(f"[skip] not found: {path}", file=sys.stderr)
            continue

        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []
            if CIRCUIT_COL not in header:
                print(f"[skip] {path.name}: missing required column {CIRCUIT_COL}",
                      file=sys.stderr)
                continue
            active = [p for p, _ in pickers if p.has_required(header)]
            if not active:
                print(f"[skip] {path.name}: has no rankable columns", file=sys.stderr)
                continue

            for picker in active:
                picker.observe_header(header)

            kept = {p.name: 0 for p in active}
            for row in reader:
                circuit = (row.get(CIRCUIT_COL) or "").strip()
                if not circuit:
                    continue
                row = dict(row)
                row["source_file"] = path.name
                for picker in active:
                    if picker.offer(circuit, row):
                        kept[picker.name] += 1
            summary = ", ".join(f"{n} {name}" for name, n in kept.items())
            print(f"[read] {path.name}: circuit(s) updated: {summary}", file=sys.stderr)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    written = [picker.write(out_name) for picker, out_name in pickers]
    return 0 if any(written) else 1


if __name__ == "__main__":
    raise SystemExit(main())
