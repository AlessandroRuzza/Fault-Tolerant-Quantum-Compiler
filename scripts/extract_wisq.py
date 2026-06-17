#!/usr/bin/env python3
"""Consolidate one or more WISQ-comparison CSVs into a best-WISQ-per-circuit CSV.

Each input is a CSV produced by compare_wisq_2.py (columns: circuit, ...,
my_routing_steps, wisq_routing_steps, wisq_status, ratio_wisq_over_mine, ...).
For every circuit, this picks the single best WISQ result across ALL inputs —
"best" meaning the lowest wisq_routing_steps (tiebreak: lowest wisq_duration_s) —
among the rows that actually have a WISQ result.

The output keeps ONLY WISQ-relevant columns (circuit, n_qubits, every wisq_*
column, grid_grown_for_wisq) plus a `source_file` column for provenance. All the
columns describing OUR execution/config (type, gaussian_strategy,
safe_passage_strategy, routing_strategy, magic_aware_strategy, parity, my_x,
my_y, my_routing_steps, my_duration_s, ratio_wisq_over_mine, ...) are dropped —
they are noise for a WISQ-focused table.

A row "has a WISQ result" when wisq_routing_steps parses as a number. Input files
that lack the required columns are skipped with a warning.

The output CSV is ALWAYS written inside the repository's data/ directory.

Usage:
    python scripts/extract_wisq.py data/results/best_gaussian_all_circuits_packing_wisq.csv
    python scripts/extract_wisq.py data/results/*wisq*.csv
    python scripts/extract_wisq.py data/results/*wisq*.csv --output best_wisq_per_circuit.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

CIRCUIT_COL = "circuit"
RANK_COL = "wisq_routing_steps"        # primary: lower is better (WISQ's own steps)
TIEBREAK_COL = "wisq_duration_s"       # secondary: lower is better
WISQ_REQUIRED_COL = "wisq_routing_steps"  # row must have this to count as "with WISQ"


def is_wisq_column(col: str) -> bool:
    """Columns kept in the output: circuit identity, circuit size, and anything
    describing WISQ. Everything about OUR execution/config is dropped."""
    return (
        col == CIRCUIT_COL
        or col == "n_qubits"
        or col == "grid_grown_for_wisq"
        or col.startswith("wisq")
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="One or more WISQ-comparison CSV files.")
    parser.add_argument("--output", "-o", default="best_wisq_per_circuit.csv",
                        help="Output CSV name. Always written inside data/ "
                             "(any directory part is ignored). "
                             "Default: best_wisq_per_circuit.csv")
    args = parser.parse_args()

    # best_by_circuit[circuit] = (rank, tiebreak, row_dict)
    best_by_circuit: dict[str, tuple[float, float, dict]] = {}
    # Preserve the column order of the first usable input, then append any extras.
    field_order: list[str] = []

    for raw in args.inputs:
        path = Path(raw)
        if not path.exists():
            print(f"[skip] not found: {path}", file=sys.stderr)
            continue

        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []
            if CIRCUIT_COL not in header or WISQ_REQUIRED_COL not in header:
                print(f"[skip] {path.name}: missing required columns "
                      f"({CIRCUIT_COL}/{WISQ_REQUIRED_COL})", file=sys.stderr)
                continue

            # Keep only WISQ-relevant columns, in first-seen order.
            for col in header:
                if is_wisq_column(col) and col not in field_order:
                    field_order.append(col)

            kept = 0
            for row in reader:
                circuit = (row.get(CIRCUIT_COL) or "").strip()
                if not circuit:
                    continue
                rank = to_float(row.get(RANK_COL))
                if rank is None:
                    continue  # no WISQ result on this row → cannot rank/include
                tiebreak = to_float(row.get(TIEBREAK_COL))
                tiebreak = tiebreak if tiebreak is not None else float("inf")

                row = dict(row)
                row["source_file"] = path.name

                key = (rank, tiebreak)
                cur = best_by_circuit.get(circuit)
                if cur is None or key < (cur[0], cur[1]):
                    best_by_circuit[circuit] = (rank, tiebreak, row)
                    kept += 1
            print(f"[read] {path.name}: {kept} circuit(s) updated", file=sys.stderr)

    if not best_by_circuit:
        print("No rows with a WISQ result found in the given inputs.", file=sys.stderr)
        return 1

    if "source_file" not in field_order:
        field_order.append("source_file")

    # Output always inside data/ — ignore any directory component of --output.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / Path(args.output).name

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_order, extrasaction="ignore")
        writer.writeheader()
        for circuit in sorted(best_by_circuit):
            writer.writerow(best_by_circuit[circuit][2])

    print(f"Wrote {len(best_by_circuit)} circuit(s) to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
