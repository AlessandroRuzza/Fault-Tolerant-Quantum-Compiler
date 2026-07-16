#!/usr/bin/env python3
"""gridrun_dimension_sweep.py — OUR compiler only, swept over a range of grid sizes.

For every (circuit, combination) in the bench config, run our compiler at

    (x + k, y + k)   for k = 0 .. --dimensions-1

where (x, y) is the STARTING grid read VERBATIM from that combination's config (must be
positive integers). Each step grows BOTH sides by 1, so the starting aspect ratio is
preserved (12x13 -> 13x14 -> ...).

⚠ THE COMPILER TRANSPOSES THE AXES: config x=8,y=9 resolves to a 9x8 grid. Every CSV in
this repo records my_x/my_y parsed from "resolved graph dimensions", i.e. the RESOLVED
grid — so feeding those numbers back as x,y runs the MIRRORED grid. On a square grid that
is harmless; on a rectangular one it is not (bwt_n37 maps at 9x8 but raises
SafePassageException at 8x9). To reproduce a grid read from a CSV, request x=my_y, y=my_x.
This script therefore records BOTH: req_x/req_y (what we asked for, the resume key, always
known) and my_x/my_y (what the compiler resolved, empty when the run failed).

Unlike gridrun_minimum_our_dimension.py, nothing is searched and nothing is auto-sized:
the start is whatever the config says. Feed it the per-circuit MINIMUM grid (the smallest
grid on which the strategy does not fail, e.g. the connectivity minima in
benchmarks/results/our_mingrid_from_wisq3.csv) and the sweep walks upward from there.
Do NOT recompute that grid from a qubit count — read it from the CSV that recorded it.

WISQ is NOT run: this measures how OUR routing responds to grid size. Use
compare_wisq_parity.py (--offsets) when you want a WISQ comparison at each grid.

A failure at one dimension does NOT stop the sweep: the row is recorded with
status=failed and the next dimension is tried (small grids are expected to fail near the
bottom of the range).

Output: one CSV row per (circuit, combination, dimension). my_x/my_y hold the grid, so
resume is exact per (circuit, combination, grid) — an interrupted run picks up at the
dimension it died on.

Usage:
    python scripts/wisq_compare/gridrun_dimension_sweep.py \
        --bench config/dim_sweep_family_median_min.json \
        --output benchmarks/results/dim_sweep_family_median_min_dims.csv \
        --dimensions 30 --workers 28
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import json
import sys
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Reuse the heavy machinery from compare_wisq_parity (compiler runner, config expansion,
# qubit counting, CSV config schema). It is import-safe (guarded main).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_wisq_parity as cw2  # noqa: E402

DEFAULT_BINARY = cw2.DEFAULT_BINARY

# Circuit identity + the config columns + the swept grid + our result.
# req_x/req_y = requested (what went into the config); my_x/my_y = RESOLVED (what the
# compiler built) — they are transposes of each other, see the module docstring.
DIM_CSV_COLUMNS = (
    ["circuit", "n_qubits"]
    + cw2.CONFIG_FIELDS
    + ["dim_index", "req_x", "req_y", "my_x", "my_y",
       "my_routing_steps", "my_duration_s", "status"]
)

_csv_write_lock = threading.Lock()


def start_grid(cfg: dict) -> tuple[int, int] | None:
    """The (x, y) the sweep starts from — read verbatim from the config, never derived."""
    try:
        x, y = int(cfg["x"]), int(cfg["y"])
    except (KeyError, ValueError, TypeError):
        return None
    return (x, y) if x > 0 and y > 0 else None


def sweep_circuit(circuit: str, combos: list[dict], binary: Path, dimensions: int,
                  attempt_timeout: float | None, done: set[tuple]) -> list[dict]:
    """Run every combination of `circuit` at each of `dimensions` grids. One row each.

    Grids already in `done` are skipped WITHOUT running the compiler, so a resumed job
    costs nothing for the work it already did.

    One worker owns a circuit: our compiler always writes qasm_graphs/<circuit>.graph,
    so two workers on the same circuit would race on that fixed path.
    """
    rows: list[dict] = []
    n_qubits = cw2.count_qasm_qubits(circuit)

    for cfg in combos:
        fields = cw2.cfg_fields(cfg)
        start = start_grid(cfg)
        if start is None:
            print(f"    [{circuit}]: config has no positive integer x/y (the start grid)",
                  file=sys.stderr)
            continue
        x0, y0 = start

        for k in range(dimensions):
            x, y = x0 + k, y0 + k
            if dim_key(circuit, cfg, x, y) in done:
                continue
            ok, mine = cw2.run_compiler_at(circuit, cfg, binary, x, y, attempt_timeout)
            row = {
                "circuit": circuit,
                "n_qubits": n_qubits if n_qubits else "",
                **fields,
                "dim_index": k,
                "req_x": x,
                "req_y": y,
                "my_x": "",
                "my_y": "",
                "my_routing_steps": "",
                "my_duration_s": "",
                "status": "failed",
            }
            if ok:
                # The RESOLVED grid — the transpose of what we requested.
                row["my_x"] = mine["width"]
                row["my_y"] = mine["height"]
                row["my_routing_steps"] = mine["routing_steps"]
                row["my_duration_s"] = (f'{mine["duration_seconds"]:.6f}'
                                        if mine["duration_seconds"] is not None else "")
                row["status"] = "success"
                row["n_qubits"] = n_qubits or mine.get("num_qubits") or ""
            else:
                # Expected near the bottom of the range — keep sweeping upward.
                print(f"    [{circuit}] {x}x{y}: FAILED", file=sys.stderr)
            rows.append({c: row.get(c, "") for c in DIM_CSV_COLUMNS})

    return rows


def dim_key(circuit: str, cfg: dict, x: int, y: int) -> tuple:
    """Resume key, on the REQUESTED grid: my_x/my_y are empty on a failed row, so keying
    on them would re-run every failure forever."""
    fields = cw2.cfg_fields(cfg)
    return (circuit,) + tuple(str(fields[k]) for k in cw2.CONFIG_FIELDS) + (str(x), str(y))


def load_done_keys(path: Path) -> set[tuple]:
    """(circuit, config..., req_x, req_y) already present, whether it succeeded or failed.

    Rows without req_x predate this column: they used a different grid convention, so they
    are NOT recognised as done. Start such a run from a fresh CSV.
    """
    if not path.exists():
        return set()
    done: set[tuple] = set()
    try:
        with path.open(newline="") as f:
            for r in csv.DictReader(f):
                circ = (r.get("circuit") or "").strip()
                if not circ or not (r.get("req_x") or "").strip():
                    continue
                done.add((circ,)
                         + tuple(r.get(k, "") for k in cw2.CONFIG_FIELDS)
                         + (str(r.get("req_x", "")), str(r.get("req_y", ""))))
    except Exception:
        pass
    return done


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sweep OUR compiler over a range of grid sizes (no WISQ).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--bench", required=True,
                        help="Sweep config (JSON) whose per-case x,y is the STARTING grid.")
    parser.add_argument("--output", "-o", default=None,
                        help="CSV output path (appended; resume-safe per grid).")
    parser.add_argument("--binary", default=str(DEFAULT_BINARY),
                        help=f"Compiler binary (default: {DEFAULT_BINARY})")
    parser.add_argument("--dimensions", type=int, default=30,
                        help="How many grids to try, +1 per side each step (default: 30).")
    parser.add_argument("--attempt-timeout", type=float, default=None,
                        help="Per-run timeout (s); a timed-out run is recorded as failed.")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel workers, ONE circuit per worker (default: 1).")
    parser.add_argument("--process-count", type=int, default=1,
                        help="Total processes sharing one CSV (shard by circuit index).")
    parser.add_argument("--processor", type=int, default=0,
                        help="This process index (0-based).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the planned grids per circuit and exit.")
    args = parser.parse_args()

    if args.dimensions < 1:
        print("ERROR: --dimensions must be >= 1", file=sys.stderr)
        return 1

    binary = Path(args.binary)
    if not binary.exists():
        print(f"ERROR: compiler binary not found: {binary}", file=sys.stderr)
        return 1

    # Expand to all (circuit, combination) configs, then group by circuit (order kept).
    source = json.loads(Path(args.bench).read_text())
    expanded = [c for c in cw2.expand_config_variants(source) if c.get("circuit")]
    by_circuit: "OrderedDict[str, list[dict]]" = OrderedDict()
    for cfg in expanded:
        by_circuit.setdefault(cfg["circuit"], []).append(cfg)

    print(f"{len(expanded)} combinations over {len(by_circuit)} circuits "
          f"x {args.dimensions} dimensions = {len(expanded) * args.dimensions} runs.",
          file=sys.stderr)
    if args.dry_run:
        for c, combos in by_circuit.items():
            g = start_grid(combos[0])
            span = (f"{g[0]}x{g[1]} .. {g[0] + args.dimensions - 1}x{g[1] + args.dimensions - 1}"
                    if g else "NO VALID START GRID")
            print(f"  {c:<45} {len(combos)} combo  {span}")
        return 0

    output_path = Path(args.output) if args.output else None
    # Appending to a CSV with a different header would silently misalign every column
    # (the header is only written when the file is empty). Refuse instead.
    if output_path and output_path.exists() and output_path.stat().st_size > 0:
        with output_path.open(newline="") as f:
            header = next(csv.reader(f), [])
        if header != DIM_CSV_COLUMNS:
            print(f"ERROR: {output_path} has a different header — appending would misalign "
                  f"the columns.\n       Move it aside and start a fresh CSV.\n"
                  f"       missing: {[c for c in DIM_CSV_COLUMNS if c not in header]}",
                  file=sys.stderr)
            return 1
    done = load_done_keys(output_path) if output_path else set()
    if done:
        print(f"Resuming: {len(done)} (circuit, config, grid) rows already in CSV.",
              file=sys.stderr)

    # Shard by circuit index: a circuit is owned by exactly one process.
    circuits = [c for i, c in enumerate(by_circuit)
                if args.process_count <= 1 or i % args.process_count == args.processor]
    print(f"Circuits for this process: {len(circuits)}.", file=sys.stderr)

    csv_file = None
    writer = None
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        csv_file = output_path.open("a", newline="")
        writer = csv.DictWriter(csv_file, fieldnames=DIM_CSV_COLUMNS)
        with _csv_write_lock:
            fcntl.flock(csv_file, fcntl.LOCK_EX)
            try:
                if output_path.stat().st_size == 0:
                    writer.writeheader()
                    csv_file.flush()
            finally:
                fcntl.flock(csv_file, fcntl.LOCK_UN)

    completed = 0

    def _process(circuit: str) -> list[dict]:
        # Resume is per grid: a partial circuit picks up at the dimension it died on.
        return sweep_circuit(circuit, by_circuit[circuit], binary, args.dimensions,
                             args.attempt_timeout, done)

    def _write_rows(new_rows: list[dict]) -> None:
        nonlocal completed
        for row in new_rows:
            completed += 1
            if writer:
                with _csv_write_lock:
                    fcntl.flock(csv_file, fcntl.LOCK_EX)
                    try:
                        writer.writerow(row)
                        csv_file.flush()
                    finally:
                        fcntl.flock(csv_file, fcntl.LOCK_UN)
            grid = (f"{row['my_x']}x{row['my_y']}" if row["my_x"]
                    else f"req {row['req_x']}x{row['req_y']}")
            print(f"[{completed}] {row['circuit']:<32} {grid:<10} "
                  f"steps={row['my_routing_steps'] or '-':<8} {row['status']}",
                  file=sys.stderr)

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(_process, c): c for c in circuits}
            for fut in as_completed(futures):
                _write_rows(fut.result())
    else:
        for c in circuits:
            print(f"\n──── {c} ────", file=sys.stderr)
            _write_rows(_process(c))

    if csv_file:
        csv_file.close()
    if output_path:
        print(f"\nCSV written/appended to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
