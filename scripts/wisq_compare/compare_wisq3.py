#!/usr/bin/env python3
"""compare_wisq3.py — like compare_wisq_2.py, but our compiler's grid is found by
a minimum-grid SEARCH instead of auto-sizing.

For every circuit and every parameter combination (the bench cartesian expansion):
  1. Start from the per-case MINIMUM grid given by the `x` and `y` fields of the
     config (must be positive integers).
  2. Run our compiler (mapping + routing). If it FAILS (any non-zero exit), grow
     the grid by +1 — alternating x, then y, then x, ... — and retry, until it
     SUCCEEDS or a safety cap (--max-grow) is hit.
This yields, per (circuit, combination), the smallest grid on which we succeed.

Then, per circuit, across all its combinations, the winner is the combination that
succeeded on the SMALLEST grid (area x*y; ties -> fewer routing steps; further
ties -> less time). WISQ is finally run "as usual" (same build_wisq_arch as
compare_wisq_2: our magic positions + even/even slots, growing only if needed)
STARTING from that winning minimum grid.

Output: one CSV row per circuit (the winning combination), same columns as
compare_wisq_2's bench CSV, so extract_wisq.py / plot_wisq_comparison*.py work on it.

Usage:
    python scripts/wisq_compare/compare_wisq3.py --bench data/config/<sweep>.json \
        --output data/results/<name>_wisq.csv --workers 8 --mr_timeout 600 --max-grow 100
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import json
import re
import subprocess
import sys
import tempfile
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Reuse all the heavy machinery from compare_wisq_2 (WISQ runner, arch builder,
# graph reader, CSV schema, row formatters). It is import-safe (guarded main).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_wisq_2 as cw2  # noqa: E402

DEFAULT_BINARY = cw2.DEFAULT_BINARY

# Parse the compiler's stdout (same fields compare_wisq_2.run_compiler extracts).
_STEPS_RE = re.compile(r"Total routing steps \([^)]*\):\s*(\d+)")
_QUBITS_RE = re.compile(r"(?m)^Qubits:\s*(\d+)")
_DIMS_RE = re.compile(r"resolved graph dimensions:\s*(\d+)x(\d+)")
_EXEC_RE = re.compile(r"Execution time:\s*([\d.]+)\s*seconds")

_csv_write_lock = threading.Lock()


def run_compiler_at(circuit: str, base_config: dict, binary: Path,
                    x: int, y: int, attempt_timeout: float | None):
    """Run our compiler on `circuit` forcing grid (x, y). Returns (ok, result).

    ok is False on any non-zero exit, a timeout, or missing routing_steps (so the
    caller can grow the grid). On success, result mirrors compare_wisq_2.run_compiler.
    """
    cfg = dict(base_config)
    cfg["circuit"] = circuit
    cfg["x"] = x
    cfg["y"] = y

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump(cfg, tmp, indent=2)
        cfg_path = Path(tmp.name)

    cmd = [str(binary), "--config", str(cfg_path)]
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=attempt_timeout)
    except subprocess.TimeoutExpired:
        cfg_path.unlink(missing_ok=True)
        return False, None
    duration = time.perf_counter() - t0
    cfg_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        return False, None

    out = proc.stdout
    steps_m = _STEPS_RE.search(out)
    if not steps_m:
        return False, None  # ran but produced no routing result -> treat as failure

    qubits_m = _QUBITS_RE.search(out)
    dims_m = _DIMS_RE.search(out)
    exec_m = _EXEC_RE.search(out)
    return True, {
        "routing_steps": int(steps_m.group(1)),
        "num_qubits": int(qubits_m.group(1)) if qubits_m else None,
        # For explicit positive x/y the compiler uses them verbatim, so the
        # resolved dims equal the requested grid; fall back to x/y just in case.
        "width": int(dims_m.group(1)) if dims_m else x,
        "height": int(dims_m.group(2)) if dims_m else y,
        "duration_seconds": float(exec_m.group(1)) if exec_m else duration,
    }


def search_min_grid(circuit: str, cfg: dict, binary: Path,
                    max_grow: int, attempt_timeout: float | None):
    """Smallest grid on which (circuit, cfg) succeeds, growing from cfg's x,y.

    Returns (result_dict, None) on success or (None, reason) on failure, where
    result_dict = {"x", "y", "grow_steps", "mine"}.
    """
    try:
        x0 = int(cfg["x"])
        y0 = int(cfg["y"])
    except (KeyError, ValueError, TypeError):
        return None, "config has no integer x/y (the minimum start)"
    if x0 <= 0 or y0 <= 0:
        return None, f"x/y must be positive integers (got {cfg.get('x')},{cfg.get('y')})"

    x, y = x0, y0
    grow = 0
    grow_x_next = True  # alternate: +1 x, then +1 y, then +1 x, ...
    while True:
        ok, mine = run_compiler_at(circuit, cfg, binary, x, y, attempt_timeout)
        if ok:
            return {"x": x, "y": y, "grow_steps": grow, "mine": mine}, None
        if grow >= max_grow:
            return None, f"no success within {max_grow} grow steps (last tried {x}x{y})"
        if grow_x_next:
            x += 1
        else:
            y += 1
        grow_x_next = not grow_x_next
        grow += 1


def process_circuit(circuit: str, combos: list[dict], binary: Path, arch_dir: Path,
                    parity: int, mr_timeout: int, max_grow: int,
                    attempt_timeout: float | None, run_id: int):
    """Search every combo's minimum grid, pick the best, then run WISQ from it.

    Returns (winning_cfg, result_dict) for a CSV row, or (None, reason) if no combo
    of this circuit ever succeeded.
    """
    best_cfg = None
    best_res = None
    best_key = None
    n_success = 0

    for cfg in combos:
        res, reason = search_min_grid(circuit, cfg, binary, max_grow, attempt_timeout)
        if res is None:
            print(f"    [{circuit}] combo failed: {reason}", file=sys.stderr)
            continue
        n_success += 1
        mine = res["mine"]
        area = mine["width"] * mine["height"]
        dur = mine["duration_seconds"] if mine["duration_seconds"] is not None else float("inf")
        # smallest grid (area) -> fewest routing steps -> least time
        key = (area, mine["routing_steps"], dur)
        if best_key is None or key < best_key:
            best_key = key
            best_cfg = cfg
            best_res = res
        print(f"    [{circuit}] combo ok: {mine['width']}x{mine['height']} "
              f"(area {area}, steps {mine['routing_steps']}, +{res['grow_steps']} grow)",
              file=sys.stderr)

    if best_cfg is None:
        return None, f"no combination succeeded within {max_grow} grow steps"

    # Re-run the winner at its winning grid so qasm_graphs/<circuit>.graph and the
    # universal QASM on disk correspond to the winning mapping (other combos ran
    # afterwards and overwrote them). The mapper is deterministic, so this reproduces.
    win_x, win_y = best_res["x"], best_res["y"]
    ok, mine = run_compiler_at(circuit, best_cfg, binary, win_x, win_y, attempt_timeout)
    if not ok:
        return None, f"winning combo did not reproduce at {win_x}x{win_y}"

    graph = cw2.read_graph(circuit)
    n_qubits = cw2.count_qasm_qubits(circuit) or mine.get("num_qubits")
    built = cw2.build_wisq_arch(
        graph["width"], graph["height"], graph["magic_states"], n_qubits, parity
    )
    wisq = cw2.get_or_run_wisq(circuit, built, arch_dir, mr_timeout, run_id)

    ratio = None
    if wisq["routing_steps"] and mine["routing_steps"] and mine["routing_steps"] > 0:
        ratio = wisq["routing_steps"] / mine["routing_steps"]

    result = {
        "n_qubits": n_qubits,
        "mine": mine,
        "built": built,
        "wisq": wisq,
        "ratio": ratio,
    }
    print(f"  [{circuit}] WINNER {mine['width']}x{mine['height']} (of {n_success} ok combos) "
          f"mine={mine['routing_steps']} wisq={wisq['routing_steps']} "
          f"status={wisq['status']}", file=sys.stderr)
    return best_cfg, result


def load_done_circuits(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    try:
        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                if row.get("circuit"):
                    done.add(row["circuit"])
    except Exception:
        pass
    return done


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare our compiler (minimum-grid search) vs WISQ.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--bench", required=True,
                        help="Sweep config (JSON) with per-case minimum x,y. "
                             "Expanded to all parameter combinations.")
    parser.add_argument("--output", "-o", default=None,
                        help="CSV output path (rows appended; resume-safe per circuit).")
    parser.add_argument("--binary", default=str(DEFAULT_BINARY),
                        help=f"Compiler binary (default: {DEFAULT_BINARY})")
    parser.add_argument("--mr_timeout", type=int, default=300,
                        help="WISQ mapping/routing timeout in seconds (default: 300)")
    parser.add_argument("--max-grow", type=int, default=100,
                        help="Safety cap on grid-grow steps per combination (default: 100)")
    parser.add_argument("--attempt-timeout", type=float, default=None,
                        help="Per-attempt timeout (s) for our compiler; a timed-out "
                             "attempt counts as a failure and grows the grid (default: none)")
    parser.add_argument("--parity", type=int, choices=(0, 1), default=cw2.PARITY,
                        help="Data-qubit sub-lattice parity for the WISQ arch (default: 0)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel workers, ONE circuit per worker (default: 1).")
    parser.add_argument("--wisq-workers", type=int, default=None,
                        help="Max concurrent WISQ instances (default: same as --workers).")
    parser.add_argument("--keep-arch-dir", default=None,
                        help="Directory to keep generated WISQ arch files (default: temp).")
    parser.add_argument("--process-count", type=int, default=1,
                        help="Total processes sharing one CSV (shard by circuit index).")
    parser.add_argument("--processor", type=int, default=0,
                        help="This process index (0-based).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print circuit/combination counts and exit.")
    args = parser.parse_args()

    if args.wisq_workers is not None and args.wisq_workers < args.workers:
        cw2._wisq_semaphore = threading.Semaphore(args.wisq_workers)
        print(f"WISQ concurrency limited to {args.wisq_workers}.", file=sys.stderr)

    binary = Path(args.binary)
    if not binary.exists():
        print(f"ERROR: compiler binary not found: {binary}", file=sys.stderr)
        return 1

    arch_dir = (Path(args.keep_arch_dir) if args.keep_arch_dir
                else Path(tempfile.mkdtemp(prefix="wisq3_arch_")))
    arch_dir.mkdir(parents=True, exist_ok=True)

    # Expand to all (circuit, combination) configs, then group by circuit (order kept).
    bench_source = json.loads(Path(args.bench).read_text())
    expanded = [c for c in cw2.expand_config_variants(bench_source) if c.get("circuit")]
    by_circuit: "OrderedDict[str, list[dict]]" = OrderedDict()
    for cfg in expanded:
        by_circuit.setdefault(cfg["circuit"], []).append(cfg)

    circuits = list(by_circuit.keys())
    print(f"Expanded to {len(expanded)} combinations over {len(circuits)} circuits.",
          file=sys.stderr)
    if args.dry_run:
        for c in circuits:
            print(f"  {c}: {len(by_circuit[c])} combinations")
        return 0

    output_path = Path(args.output) if args.output else None
    done = load_done_circuits(output_path) if output_path else set()
    if done:
        print(f"Resuming: {len(done)} circuits already in CSV, skipping.", file=sys.stderr)

    # Shard by circuit index (so multiple processes can share one CSV), skip done.
    todo = [
        (i, c) for i, c in enumerate(circuits)
        if c not in done and (args.process_count <= 1 or i % args.process_count == args.processor)
    ]
    print(f"Circuits to run: {len(todo)}.", file=sys.stderr)

    csv_file = None
    writer = None
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        csv_file = output_path.open("a", newline="")
        writer = csv.DictWriter(csv_file, fieldnames=cw2.BENCH_CSV_COLUMNS)
        with _csv_write_lock:
            fcntl.flock(csv_file, fcntl.LOCK_EX)
            try:
                if output_path.stat().st_size == 0:
                    writer.writeheader()
                    csv_file.flush()
            finally:
                fcntl.flock(csv_file, fcntl.LOCK_UN)

    completed = 0
    rows: list[dict] = []

    def _process(i: int, circuit: str) -> dict:
        combos = by_circuit[circuit]
        try:
            cfg, result = process_circuit(
                circuit, combos, binary, arch_dir, args.parity,
                args.mr_timeout, args.max_grow, args.attempt_timeout, run_id=i,
            )
            if cfg is None:
                print(f"  ERROR [{circuit}]: {result}", file=sys.stderr)
                row = {**cw2.make_error_row_base(circuit, args.parity),
                       **cw2.cfg_fields(combos[0])}
            else:
                row = {**cw2.make_row_base(circuit, result, args.parity),
                       **cw2.cfg_fields(cfg)}
        except (RuntimeError, FileNotFoundError) as e:
            print(f"  ERROR [{circuit}]: {e}", file=sys.stderr)
            row = {**cw2.make_error_row_base(circuit, args.parity),
                   **cw2.cfg_fields(combos[0])}
        return {k: row.get(k, "") for k in cw2.BENCH_CSV_COLUMNS}

    def _write_row(row: dict) -> None:
        nonlocal completed
        rows.append(row)
        completed += 1
        if writer:
            with _csv_write_lock:
                fcntl.flock(csv_file, fcntl.LOCK_EX)
                try:
                    writer.writerow(row)
                    csv_file.flush()
                finally:
                    fcntl.flock(csv_file, fcntl.LOCK_UN)
        my_grid = f"{row['my_x']}x{row['my_y']}" if row.get("my_x") else "?"
        wisq_grid = f"{row['wisq_x']}x{row['wisq_y']}" if row.get("wisq_x") else "?"
        print(f"[{completed}/{len(todo)}] {row['circuit']} "
              f"my_grid={my_grid} wisq_grid={wisq_grid} "
              f"mine={row['my_routing_steps']} wisq={row['wisq_routing_steps']} "
              f"ratio={row['ratio_wisq_over_mine']} status={row['wisq_status']}",
              file=sys.stderr)

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(_process, i, c): c for i, c in todo}
            for fut in as_completed(futures):
                _write_row(fut.result())
    else:
        for i, c in todo:
            print(f"\n──── {c} ({len(by_circuit[c])} combos) ────", file=sys.stderr)
            _write_row(_process(i, c))

    if csv_file:
        csv_file.close()
    if output_path:
        print(f"\nCSV written/appended to {output_path}")

    if not args.keep_arch_dir:
        for p in arch_dir.glob("*_wisq2.arch"):
            p.unlink(missing_ok=True)
        try:
            arch_dir.rmdir()
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
