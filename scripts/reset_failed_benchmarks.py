#!/usr/bin/env python3
"""Reset safe_passage_failed entries in the expanded benchmark JSON so they re-run.

Usage:
    python3 scripts/reset_failed_benchmarks.py

Reads mapping_only_benchmark_runs.csv to find which (circuit, type, strategy,
bdp, ms) combos ended in safe_passage_failed, then marks them as executed=false
in mapping_only_benchmark_expanded.json so the next benchmark run picks them up.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "benchmarks" / "results" / "mapping_only_benchmark_runs.csv"
JSON_PATH = ROOT / "config" / "mapping_only_benchmark_expanded.json"


def main() -> None:
    failing_keys: set[tuple] = set()
    with CSV_PATH.open() as f:
        f.readline()  # header
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 29:
                continue
            status = parts[27]
            if status == "safe_passage_failed":
                circuit = parts[3]
                mtype = parts[7]
                strat = parts[18]
                bdp = float(parts[20])
                ms = float(parts[21])
                failing_keys.add((circuit, mtype, strat, bdp, ms))

    print(f"Found {len(failing_keys)} unique failing combos in CSV")

    with JSON_PATH.open() as f:
        data = json.load(f)

    reset_count = 0
    for entry in data:
        circuit = str(entry.get("circuit", ""))
        circuit_stem = os.path.splitext(os.path.basename(circuit))[0]
        mtype = str(entry.get("type", ""))
        strat = str(entry.get("safe_passage_strategy", ""))
        bdp = float(entry.get("border_distance_percentage", 0))
        ms = float(entry.get("number_of_magic_states", 0))
        if (circuit_stem, mtype, strat, bdp, ms) in failing_keys:
            entry["executed"] = False
            reset_count += 1

    print(f"Resetting {reset_count} entries → executed=false")
    with JSON_PATH.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Saved {JSON_PATH}")


if __name__ == "__main__":
    main()
