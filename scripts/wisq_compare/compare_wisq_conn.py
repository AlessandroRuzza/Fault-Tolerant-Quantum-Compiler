#!/usr/bin/env python3
"""compare_wisq_conn.py — connectivity vs WISQ at WISQ's native grid MINUS a margin.

Goal: show how `safe_passage_strategy = connectivity` competes with WISQ when our
compiler is forced onto a grid that is SMALLER than the one WISQ uses for itself.

Per circuit, per parameter combination (the bench cartesian expansion):
  1. WISQ keeps its OWN native square_sparse_layout grid (side = 2*ceil(sqrt(n))+3,
     the same grid compare_wisq_2 --wisq-native gives it). That side is the reference.
  2. Our compiler starts on a SQUARE grid of side  (wisq_native_side - SHRINK)  per
     side (default SHRINK=4). If it FAILS (any non-zero exit / no routing result —
     typically safe_passage cannot be established on so small a grid) the side is
     grown by +1 and retried, until it SUCCEEDS or a safety cap (--max-grow) is hit.
This yields, per (circuit, combination), the smallest WISQ-minus-margin grid on which
connectivity succeeds.

Then, per circuit, across all its combinations, the winner is the combination that
succeeded on the SMALLEST grid (area x*y; ties -> fewer routing steps; further ties
-> less time). WISQ is run once on its native grid and compared against the winner.

The extra columns vs compare_wisq_2's bench CSV are:
  * dim_diff_side  = wisq_x - my_x  (how many fewer rows/cols per side connectivity
                     used than WISQ; SHRINK if no grow was needed, less if it grew,
                     negative if connectivity needed MORE than WISQ).
  * grow_steps     = how many +1 grows from the (wisq_native_side - SHRINK) start.
plot_wisq_comparison.py reads dim_diff_side to chart the footprint gap.

Usage:
    python scripts/wisq_compare/compare_wisq_conn.py --bench config/<conn_sweep>.json \
        --output benchmarks/results/<name>_wisqconn.csv --workers 28 \
        --shrink 4 --mr_timeout 600
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import json
import sys
import tempfile
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Reuse the WISQ runner, native-arch builder, graph/qasm readers, CSV schema and row
# formatters from compare_wisq_2, plus the grid-grow compiler helper from compare_wisq3.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_wisq_2 as cw2  # noqa: E402
import compare_wisq3 as cw3   # noqa: E402

DEFAULT_BINARY = cw2.DEFAULT_BINARY

# compare_wisq_2's bench columns + the two footprint-gap columns this script adds.
CONN_CSV_COLUMNS = cw2.BENCH_CSV_COLUMNS + ["dim_diff_side", "grow_steps"]

_csv_write_lock = threading.Lock()


def grow_to_success(circuit: str, cfg: dict, binary: Path, start_side: int,
                    max_grow: int, attempt_timeout: float | None):
    """Smallest SQUARE grid >= start_side on which (circuit, cfg) succeeds.

    Grows the side by +1 on every failure (both dimensions together, so the grid
    stays square, matching WISQ's square native layout). Returns
    (result_dict, None) on success or (None, reason) on failure, where
    result_dict = {"side", "grow_steps", "mine"}.
    """
    side = max(1, start_side)
    grow = 0
    while True:
        ok, mine = cw3.run_compiler_at(circuit, cfg, binary, side, side, attempt_timeout)
        if ok:
            return {"side": side, "grow_steps": grow, "mine": mine}, None
        if grow >= max_grow:
            return None, f"no success within {max_grow} grow steps (last tried {side}x{side})"
        side += 1
        grow += 1


def process_circuit(circuit: str, combos: list[dict], binary: Path, arch_dir: Path,
                    shrink: int, mr_timeout: int, max_grow: int,
                    attempt_timeout: float | None, run_id: int,
                    wisq_parity: bool = False, parity: int = 0):
    """Grow each combo from (wisq_native_side - shrink), pick the best, run WISQ native.

    Returns (winning_cfg, result_dict) for a CSV row, or (None, reason) if the qubit
    count is unknown or no combo of this circuit ever succeeded.
    """
    # Qubit count from the INPUT qasm (available before any run); same value
    # compare_wisq_2 --wisq-native uses to size both sides.
    n_in, _has_t = cw2._input_qasm_qubits_and_t(circuit)
    if not n_in:
        return None, f"cannot determine qubit count for {circuit} (missing/empty qasm)"

    wisq_side0 = cw2.wisq_native_side(n_in)
    start_side = max(1, wisq_side0 - shrink)

    best_cfg = None
    best_res = None
    best_key = None
    n_success = 0

    for cfg in combos:
        res, reason = grow_to_success(circuit, cfg, binary, start_side,
                                      max_grow, attempt_timeout)
        if res is None:
            print(f"    [{circuit}] combo failed: {reason}", file=sys.stderr)
            continue
        n_success += 1
        mine = res["mine"]
        area = mine["width"] * mine["height"]
        dur = mine["duration_seconds"] if mine["duration_seconds"] is not None else float("inf")
        key = (area, mine["routing_steps"], dur)  # smallest grid -> fewest steps -> least time
        if best_key is None or key < best_key:
            best_key = key
            best_cfg = cfg
            best_res = res
        print(f"    [{circuit}] combo ok: {mine['width']}x{mine['height']} "
              f"(start {start_side}, +{res['grow_steps']} grow, steps {mine['routing_steps']})",
              file=sys.stderr)

    if best_cfg is None:
        return None, f"no combination succeeded (start {start_side}, max-grow {max_grow})"

    # Re-run the winner at its winning side so qasm_graphs/<circuit>.graph and the
    # universal QASM on disk correspond to the winning mapping (later combos
    # overwrote them). The mapper is deterministic, so this reproduces.
    win_side = best_res["side"]
    ok, mine = cw3.run_compiler_at(circuit, best_cfg, binary, win_side, win_side, attempt_timeout)
    if not ok:
        return None, f"winning combo did not reproduce at {win_side}x{win_side}"

    n_qubits = cw2.count_qasm_qubits(circuit) or mine.get("num_qubits") or n_in
    if wisq_parity:
        # WISQ on OUR (shrunk) grid: build its arch from the winning mapping's grid +
        # magic positions (qasm_graphs/<circuit>.graph, just rewritten above). cw2's
        # MAX_GROW_STEPS (set to --wisq-max-grow in main) caps WISQ-side growth, so with
        # cap 0 WISQ is HELD at our grid and FAILS where its sparse sub-lattice cannot
        # hold n_qubits (enough_space=False -> too-small arch -> WISQ errors/fails).
        graph = cw2.read_graph(circuit)
        built = cw2.build_wisq_arch(graph["width"], graph["height"],
                                    graph["magic_states"], n_qubits, parity)
    else:
        # WISQ runs on its OWN native square_sparse_layout grid (cw2._wisq_native set in
        # main()). native_built reports that grid; the actual WISQ run sizes itself from
        # the universal-QASM qubit count.
        built = cw2.native_built(n_qubits)
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
        "grow_steps": best_res["grow_steps"],
        "dim_diff_side": built["arch"]["width"] - mine["width"],
    }
    print(f"  [{circuit}] WINNER {mine['width']}x{mine['height']} vs WISQ "
          f"{built['arch']['width']}x{built['arch']['height']} "
          f"(diff {result['dim_diff_side']}/side, of {n_success} ok combos) "
          f"mine={mine['routing_steps']} wisq={wisq['routing_steps']} "
          f"status={wisq['status']}", file=sys.stderr)
    return best_cfg, result


def make_conn_row(circuit: str, cfg: dict, result: dict, parity: int) -> dict:
    """compare_wisq_2 base row + the two footprint-gap columns."""
    row = {**cw2.make_row_base(circuit, result, parity), **cw2.cfg_fields(cfg)}
    row["dim_diff_side"] = result["dim_diff_side"]
    row["grow_steps"] = result["grow_steps"]
    return row


def make_conn_error_row(circuit: str, cfg: dict, parity: int) -> dict:
    row = {**cw2.make_error_row_base(circuit, parity), **cw2.cfg_fields(cfg)}
    row["dim_diff_side"] = ""
    row["grow_steps"] = ""
    return row


def load_done_circuits(path: Path) -> set[str]:
    """Circuits to SKIP on resume: those with a genuine result row.

    A circuit counts as done only if it has a row where our compiler produced a grid
    (my_routing_steps is non-empty). Pure error rows (status=error, no grid — e.g. the
    missing-qasm failures) are NOT counted, so a resubmit retries them instead of
    skipping forever."""
    if not path.exists():
        return set()
    done: set[str] = set()
    try:
        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                if row.get("circuit") and str(row.get("my_routing_steps", "")).strip():
                    done.add(row["circuit"])
    except Exception:
        pass
    return done


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Connectivity vs WISQ at WISQ's native grid minus a per-side margin.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--bench", required=True,
                        help="Sweep config (JSON). Expanded to all parameter combinations.")
    parser.add_argument("--output", "-o", default=None,
                        help="CSV output path (rows appended; resume-safe per circuit).")
    parser.add_argument("--binary", default=str(DEFAULT_BINARY),
                        help=f"Compiler binary (default: {DEFAULT_BINARY})")
    parser.add_argument("--shrink", type=int, default=4,
                        help="Per-side margin subtracted from WISQ's native side for "
                             "OUR starting grid (default: 4).")
    parser.add_argument("--mr_timeout", type=int, default=300,
                        help="WISQ mapping/routing timeout in seconds (default: 300)")
    parser.add_argument("--max-grow", type=int, default=100,
                        help="Safety cap on grid-grow steps per combination (default: 100)")
    parser.add_argument("--attempt-timeout", type=float, default=None,
                        help="Per-attempt timeout (s) for our compiler; a timed-out "
                             "attempt counts as a failure and grows the grid (default: none)")
    parser.add_argument("--parity", type=int, choices=(0, 1), default=cw2.PARITY,
                        help="Data-qubit sub-lattice parity for the WISQ arch (default: 0)")
    parser.add_argument("--wisq-grid", choices=("native", "parity"), default="native",
                        help="native (default): WISQ runs on its OWN square_sparse_layout "
                             "grid (our grid forced smaller). parity: WISQ is forced onto "
                             "OUR (shrunk) grid via build_wisq_arch, to MEASURE whether WISQ "
                             "can route at the same reduced dimension.")
    parser.add_argument("--wisq-max-grow", type=int, default=0,
                        help="In --wisq-grid parity, cap on WISQ-side grid growth when its "
                             "sparse sub-lattice cannot hold n qubits (default 0 = hold WISQ "
                             "at OUR grid; WISQ FAILS where it does not fit).")
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

    # WISQ grid mode.
    #  native: WISQ keeps its own square_sparse_layout grid (our grid forced smaller).
    #          Mirrors compare_wisq_2 --wisq-native. This is the original comparison.
    #  parity: WISQ is forced onto OUR (shrunk) grid via build_wisq_arch, with WISQ-side
    #          growth capped (--wisq-max-grow, default 0) so we can MEASURE whether WISQ
    #          can place/route on native-K at all instead of letting it grow back.
    wisq_parity = (args.wisq_grid == "parity")
    cw2._wisq_native = not wisq_parity
    if wisq_parity:
        cw2.MAX_GROW_STEPS = args.wisq_max_grow
        print(f"WISQ forced onto OUR (shrunk) grid [parity], WISQ-side grow cap = "
              f"{args.wisq_max_grow}.", file=sys.stderr)

    if args.wisq_workers is not None and args.wisq_workers < args.workers:
        cw2._wisq_semaphore = threading.Semaphore(args.wisq_workers)
        print(f"WISQ concurrency limited to {args.wisq_workers}.", file=sys.stderr)

    binary = Path(args.binary)
    if not binary.exists():
        print(f"ERROR: compiler binary not found: {binary}", file=sys.stderr)
        return 1

    arch_dir = (Path(args.keep_arch_dir) if args.keep_arch_dir
                else Path(tempfile.mkdtemp(prefix="wisqconn_arch_")))
    arch_dir.mkdir(parents=True, exist_ok=True)

    # Expand to all (circuit, combination) configs, then group by circuit (order kept).
    bench_source = json.loads(Path(args.bench).read_text())
    expanded = [c for c in cw2.expand_config_variants(bench_source) if c.get("circuit")]
    by_circuit: "OrderedDict[str, list[dict]]" = OrderedDict()
    for cfg in expanded:
        by_circuit.setdefault(cfg["circuit"], []).append(cfg)

    circuits = list(by_circuit.keys())
    print(f"Expanded to {len(expanded)} combinations over {len(circuits)} circuits "
          f"(WISQ native; our start = wisq_native_side - {args.shrink}).", file=sys.stderr)
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
        writer = csv.DictWriter(csv_file, fieldnames=CONN_CSV_COLUMNS)
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
                circuit, combos, binary, arch_dir, args.shrink,
                args.mr_timeout, args.max_grow, args.attempt_timeout, run_id=i,
                wisq_parity=wisq_parity, parity=args.parity,
            )
            if cfg is None:
                print(f"  ERROR [{circuit}]: {result}", file=sys.stderr)
                row = make_conn_error_row(circuit, combos[0], args.parity)
            else:
                row = make_conn_row(circuit, cfg, result, args.parity)
        except (RuntimeError, FileNotFoundError) as e:
            print(f"  ERROR [{circuit}]: {e}", file=sys.stderr)
            row = make_conn_error_row(circuit, combos[0], args.parity)
        return {k: row.get(k, "") for k in CONN_CSV_COLUMNS}

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
              f"my_grid={my_grid} wisq_grid={wisq_grid} diff={row['dim_diff_side']}/side "
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
