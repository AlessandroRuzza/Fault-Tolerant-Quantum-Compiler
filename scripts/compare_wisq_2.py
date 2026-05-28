#!/usr/bin/env python3
"""Compare our compiler vs WISQ at parity of grid dimensions and magic-state placement.

Pipeline, per circuit:
  1. Run our compiler with x=-1, y=-1 (auto dimensions) using the mapping config the
     user chose (type, gaussian_strategy, safe_passage_strategy, routing, ...). The
     compiler does its normal mapping + routing and writes qasm_graphs/<circuit>.graph
     (grid dimensions + magic-state positions) and the universal QASM.
  2. Build a WISQ architecture with:
       - the same grid dimensions,
       - the magic states at the SAME positions our mapper chose,
       - data-qubit slots = all cells of the same sub-lattice our compiler uses
         (even col AND even row), minus the magic-state cells.
     WISQ is then free to map the circuit's qubits onto any of these slots.
  3. If that sub-lattice has fewer slots than the circuit's qubits, grow the grid
     FOR WISQ ONLY (width +1, then height +1, alternating) until they fit. This
     breaks dimension parity, so it is a last resort and is flagged per row.
  4. Run WISQ (mapping + routing) on that architecture.
  5. Emit a side-by-side CSV and print a summary.

Why the even/even sub-lattice and not "all cells": in a surface code the empty cells
between qubits ARE the lattice-surgery routing corridors. WISQ (square_sparse_layout)
and our router both need them. A dense layout leaves no corridors and routing fails.
The even/even sub-lattice matches the slots our compiler exposes, giving true parity.

Bench mode (--bench):
  Accepts a sweep config (e.g. data/config/params_bench.json) and runs the full
  cartesian product of all parameter combinations, mirroring the C++ benchmark
  expansion logic. Results are written incrementally so the run can be interrupted
  and resumed without losing work.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import re
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BINARY = REPO_ROOT / "build" / "FaultTolerantQuantumCompiler"
DEFAULT_CONFIG = REPO_ROOT / "config" / "0_compiler_config.json"
QASM_GRAPHS_DIR = REPO_ROOT / "qasm_graphs"
UNIVERSAL_QASMS_DIR = REPO_ROOT / "universal_set_qasms"

_local_wisq = REPO_ROOT / ".env" / "bin" / "wisq"
WISQ = _local_wisq if _local_wisq.exists() else Path("wisq")

# Sub-lattice parity for data-qubit slots. Our compiler exports data qubits on
# even/even cells (0,2,4,...), so we mirror that for a fair, same-density comparison.
PARITY = 0  # 0 -> even coordinates, 1 -> odd coordinates

MAX_GROW_STEPS = 64  # safety cap on the WISQ-only grid enlargement loop

# Per-circuit locks: prevent two workers from writing qasm_graphs/<circuit>.graph
# simultaneously (the compiler always writes to that fixed path).
_circuit_locks: dict[str, threading.Lock] = {}
_circuit_locks_mutex = threading.Lock()
_csv_write_lock = threading.Lock()
# Semaphore limiting concurrent WISQ instances (set in main() via --wisq-workers).
_wisq_semaphore: threading.Semaphore | None = None
_active_wisq = 0
_active_wisq_lock = threading.Lock()


def _get_circuit_lock(circuit: str) -> threading.Lock:
    with _circuit_locks_mutex:
        if circuit not in _circuit_locks:
            _circuit_locks[circuit] = threading.Lock()
        return _circuit_locks[circuit]

# Config fields that vary across a bench sweep and are written as CSV columns.
CONFIG_FIELDS = [
    "type",
    "gaussian_strategy",
    "safe_passage_strategy",
    "routing_strategy",
    "t_routing_mode",
    "use_layer_cache",
    "MagicStatePlacementStrategy",
    "T_states_proportional",
    "number_of_magic_states",
    "border_distance_percentage",
    "magic_aware_strategy",
]


# ── our compiler ────────────────────────────────────────────────────────────────

def run_compiler(circuit: str, base_config: dict, binary: Path) -> dict:
    """Run our compiler once on `circuit` with x=-1/y=-1 and the given mapping config.

    Returns parsed routing_steps / qubits / grid dims / duration from stdout.
    The compiler also writes qasm_graphs/<circuit>.graph as a side effect.
    """
    cfg = dict(base_config)
    cfg["circuit"] = circuit
    cfg["x"] = -1
    cfg["y"] = -1

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
        json.dump(cfg, tmp, indent=2)
        cfg_path = Path(tmp.name)

    cmd = [str(binary), "--config", str(cfg_path)]
    print(f"  [compiler] {' '.join(cmd)}", file=sys.stderr)

    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.perf_counter() - t0
    cfg_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        print(proc.stdout[-2000:], file=sys.stderr)
        print(proc.stderr[-2000:], file=sys.stderr)
        raise RuntimeError(f"compiler failed for '{circuit}' (exit {proc.returncode})")

    out = proc.stdout

    steps_m = re.search(r"Total routing steps \([^)]*\):\s*(\d+)", out)
    qubits_m = re.search(r"(?m)^Qubits:\s*(\d+)", out)
    dims_m = re.search(r"resolved graph dimensions:\s*(\d+)x(\d+)", out)
    exec_m = re.search(r"Execution time:\s*([\d.]+)\s*seconds", out)

    return {
        "routing_steps": int(steps_m.group(1)) if steps_m else None,
        "num_qubits": int(qubits_m.group(1)) if qubits_m else None,
        "width": int(dims_m.group(1)) if dims_m else None,
        "height": int(dims_m.group(2)) if dims_m else None,
        "duration_seconds": float(exec_m.group(1)) if exec_m else duration,
    }


def read_graph(circuit: str) -> dict:
    """Read qasm_graphs/<circuit>.graph -> width, height, magic_states (flat indices)."""
    path = QASM_GRAPHS_DIR / f"{circuit}.graph"
    if not path.exists():
        raise FileNotFoundError(f"missing graph file: {path}")
    data = json.loads(path.read_text())
    return {
        "width": int(data["width"]),
        "height": int(data["height"]),
        "magic_states": [int(m) for m in data.get("magic_states", [])],
    }


def count_qasm_qubits(circuit: str) -> int | None:
    """Count distinct qubits appearing in cx/t/tdg gates of the universal QASM.

    This mirrors WISQ's extract_qubits_from_gates: it is the number of logical
    qubits WISQ must place, which drives the 'enough slots?' check.
    """
    path = UNIVERSAL_QASMS_DIR / f"{circuit}_universal.qasm"
    if not path.exists():
        return None
    qubits: set[int] = set()
    cx_re = re.compile(r"cx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\]\s*;")
    t_re = re.compile(r"(?:t|tdg)\s+q\[(\d+)\]\s*;")
    for line in path.read_text().splitlines():
        m = cx_re.search(line)
        if m:
            qubits.add(int(m.group(1)))
            qubits.add(int(m.group(2)))
            continue
        m = t_re.search(line)
        if m:
            qubits.add(int(m.group(1)))
    return len(qubits)


# ── WISQ architecture builder ────────────────────────────────────────────────────

def sublattice_slots(width: int, height: int, magic_set: set[int], parity: int) -> list[int]:
    """All even/even (or odd/odd) cells, as flat indices, excluding magic cells."""
    slots = []
    for row in range(height):
        if row % 2 != parity:
            continue
        for col in range(width):
            if col % 2 != parity:
                continue
            idx = row * width + col
            if idx not in magic_set:
                slots.append(idx)
    return slots


def build_wisq_arch(width: int, height: int, magic_flat: list[int],
                    n_qubits: int, parity: int) -> dict:
    """Build a WISQ arch dict. Grow the grid (WISQ-only) if slots < n_qubits.

    Magic states are kept as (col, row) coordinates and re-flattened whenever the
    width changes, so their physical position is preserved across growth.
    """
    magic_coords = [(m % width, m // width) for m in magic_flat]

    w, h = width, height
    grown = False
    grow_step = 0
    while True:
        magic_set = {row * w + col for col, row in magic_coords}
        slots = sublattice_slots(w, h, magic_set, parity)
        if n_qubits is None or len(slots) >= n_qubits:
            break
        if grow_step >= MAX_GROW_STEPS:
            break
        # Alternate: grow width first, then height.
        if grow_step % 2 == 0:
            w += 1
        else:
            h += 1
        grown = True
        grow_step += 1

    magic_set = {row * w + col for col, row in magic_coords}
    slots = sublattice_slots(w, h, magic_set, parity)

    return {
        "arch": {
            "width": w,
            "height": h,
            "alg_qubits": slots,
            "magic_states": sorted(magic_set),
        },
        "grown": grown,
        "enough_space": n_qubits is None or len(slots) >= n_qubits,
        "n_slots": len(slots),
    }


def write_arch_file(arch: dict, path: Path) -> None:
    # WISQ loads arch with ast.literal_eval; a JSON dict of ints/lists is a valid
    # Python literal, so json.dump is safe here.
    path.write_text(json.dumps(arch, indent=2))


# ── WISQ runner ──────────────────────────────────────────────────────────────────

def run_wisq(circuit: str, arch_path: Path, mr_timeout: int) -> dict:
    qasm = UNIVERSAL_QASMS_DIR / f"{circuit}_universal.qasm"
    if not qasm.exists():
        raise FileNotFoundError(f"missing universal QASM: {qasm}")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out_path = Path(tmp.name)

    cmd = [
        str(WISQ), str(qasm),
        "--mode", "scmr",
        "-arch", str(arch_path),
        "--output_path", str(out_path),
        "--mr_timeout", str(mr_timeout),
    ]
    print(f"  [wisq]     {' '.join(cmd)}", file=sys.stderr)

    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.perf_counter() - t0

    routing_steps = None
    status = "success" if proc.returncode == 0 else "failed"
    if proc.returncode == 124:
        status = "timeout"

    if proc.returncode == 0 and out_path.exists():
        try:
            data = json.loads(out_path.read_text())
            steps = data.get("steps")
            if steps == "timeout":
                status = "timeout"
            elif isinstance(steps, list):
                routing_steps = len(steps)
        except (json.JSONDecodeError, OSError):
            status = "bad_output"

    out_path.unlink(missing_ok=True)
    return {
        "routing_steps": routing_steps,
        "duration_seconds": duration,
        "status": status,
        "exit_code": proc.returncode,
    }


# ── bench config expansion ───────────────────────────────────────────────────────

def expand_config_variants(source: dict) -> list[dict]:
    """Port of the C++ expand_config_variants.

    Rules (applied recursively):
    - A field whose value is a list of objects → for each object, merge its fields
      into the current entry (removing the list field) and recurse. Only the first
      such field found is expanded per recursion level, matching the C++ behaviour.
    - After all object-lists are resolved, take the cartesian product of all
      remaining array-valued fields (scalar arrays).
    """
    results: list[dict] = []

    def expand_entry(entry: dict) -> None:
        # Handle the first array-of-objects found (e.g., magic_configs).
        for key in list(entry.keys()):
            value = entry[key]
            if isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
                base = {k: v for k, v in entry.items() if k != key}
                for obj_override in value:
                    expand_entry({**base, **obj_override})
                return

        # Cartesian product of all remaining (scalar) array-valued fields.
        keys = list(entry.keys())
        values_per_key = [
            v if isinstance(v, list) else [v]
            for v in entry.values()
        ]
        for combo in itertools.product(*values_per_key):
            results.append(dict(zip(keys, combo)))

    if isinstance(source, list):
        for item in source:
            expand_entry(item)
    else:
        expand_entry(source)
    return results


def cfg_fields(cfg: dict) -> dict:
    """Extract CONFIG_FIELDS values from an expanded config dict."""
    return {
        "type": cfg.get("type", ""),
        "gaussian_strategy": cfg.get("gaussian_strategy", ""),
        "safe_passage_strategy": cfg.get("safe_passage_strategy", ""),
        "routing_strategy": cfg.get("routing_strategy", ""),
        "t_routing_mode": cfg.get("t-routing-mode", ""),
        "use_layer_cache": cfg.get("use_layer_cache", ""),
        "MagicStatePlacementStrategy": cfg.get("MagicStatePlacementStrategy", ""),
        "T_states_proportional": cfg.get("T_states_proportional", ""),
        "number_of_magic_states": cfg.get("number_of_magic_states", ""),
        "border_distance_percentage": cfg.get("border_distance_percentage", ""),
        "magic_aware_strategy": cfg.get("magic_aware_strategy", ""),
    }


def cfg_key(circuit: str, cfg: dict) -> tuple:
    """Unique key for a (circuit, config) pair — used for resume dedup."""
    fields = cfg_fields(cfg)
    return (circuit,) + tuple(str(fields[k]) for k in CONFIG_FIELDS)


def load_done_keys_bench(path: Path) -> set[tuple]:
    """Read an existing bench CSV and return already-processed (circuit, config...) keys."""
    if not path.exists():
        return set()
    done: set[tuple] = set()
    try:
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row.get("circuit", ""),) + tuple(
                    row.get(k, "") for k in CONFIG_FIELDS
                )
                done.add(key)
    except Exception:
        pass
    return done


# ── CSV schemas ──────────────────────────────────────────────────────────────────

CSV_COLUMNS = [
    "circuit", "n_qubits", "parity",
    "my_x", "my_y", "my_routing_steps", "my_duration_s",
    "wisq_x", "wisq_y", "wisq_routing_steps", "wisq_duration_s",
    "wisq_n_slots", "grid_grown_for_wisq", "wisq_status",
    "ratio_wisq_over_mine",
]

BENCH_CSV_COLUMNS = (
    ["circuit", "n_qubits"]
    + CONFIG_FIELDS
    + [
        "parity",
        "my_x", "my_y", "my_routing_steps", "my_duration_s",
        "wisq_x", "wisq_y", "wisq_routing_steps", "wisq_duration_s",
        "wisq_n_slots", "grid_grown_for_wisq", "wisq_status",
        "ratio_wisq_over_mine",
    ]
)


# ── shared per-circuit logic ─────────────────────────────────────────────────────

def run_one(circuit: str, cfg: dict, binary: Path, arch_dir: Path,
            parity: int, mr_timeout: int, run_id: int | None = None) -> dict:
    """Run compiler + WISQ for one (circuit, cfg) pair. Returns a result dict.

    run_id makes the arch file path unique so parallel workers on the same
    circuit don't clobber each other's arch files.
    The compiler always writes qasm_graphs/<circuit>.graph, so we hold a
    per-circuit lock for the compiler + read_graph phase.
    """
    with _get_circuit_lock(circuit):
        mine = run_compiler(circuit, cfg, binary)
        graph = read_graph(circuit)

    n_qubits = count_qasm_qubits(circuit) or mine.get("num_qubits")

    built = build_wisq_arch(
        graph["width"], graph["height"], graph["magic_states"],
        n_qubits, parity,
    )
    suffix = f"_{run_id}" if run_id is not None else ""
    arch_path = arch_dir / f"{circuit}{suffix}_wisq2.arch"
    write_arch_file(built["arch"], arch_path)

    if not built["enough_space"]:
        print(f"  WARNING: only {built['n_slots']} slots for {n_qubits} qubits "
              f"after {MAX_GROW_STEPS} grow steps — WISQ will likely fail.",
              file=sys.stderr)
    elif built["grown"]:
        print(f"  NOTE: grid grown for WISQ to "
              f"{built['arch']['width']}x{built['arch']['height']} "
              f"(dimension parity broken).", file=sys.stderr)

    global _active_wisq
    if _wisq_semaphore is not None:
        with _wisq_semaphore:
            with _active_wisq_lock:
                _active_wisq += 1
            try:
                wisq = run_wisq(circuit, arch_path, mr_timeout)
            finally:
                with _active_wisq_lock:
                    _active_wisq -= 1
    else:
        wisq = run_wisq(circuit, arch_path, mr_timeout)
    arch_path.unlink(missing_ok=True)

    ratio = None
    if (wisq["routing_steps"] and mine["routing_steps"] and mine["routing_steps"] > 0):
        ratio = wisq["routing_steps"] / mine["routing_steps"]

    return {
        "n_qubits": n_qubits,
        "mine": mine,
        "built": built,
        "wisq": wisq,
        "ratio": ratio,
    }


def make_row_base(circuit: str, result: dict, parity: int) -> dict:
    mine = result["mine"]
    built = result["built"]
    wisq = result["wisq"]
    ratio = result["ratio"]
    return {
        "circuit": circuit,
        "n_qubits": result["n_qubits"],
        "parity": parity,
        "my_x": mine["width"],
        "my_y": mine["height"],
        "my_routing_steps": mine["routing_steps"],
        "my_duration_s": f"{mine['duration_seconds']:.6f}" if mine["duration_seconds"] is not None else "",
        "wisq_x": built["arch"]["width"],
        "wisq_y": built["arch"]["height"],
        "wisq_routing_steps": wisq["routing_steps"],
        "wisq_duration_s": f"{wisq['duration_seconds']:.6f}",
        "wisq_n_slots": built["n_slots"],
        "grid_grown_for_wisq": "true" if built["grown"] else "false",
        "wisq_status": wisq["status"],
        "ratio_wisq_over_mine": f"{ratio:.4f}" if ratio is not None else "",
    }


def make_error_row_base(circuit: str, parity: int) -> dict:
    return {
        "circuit": circuit, "n_qubits": "", "parity": parity,
        "my_x": "", "my_y": "", "my_routing_steps": "", "my_duration_s": "",
        "wisq_x": "", "wisq_y": "", "wisq_routing_steps": "", "wisq_duration_s": "",
        "wisq_n_slots": "", "grid_grown_for_wisq": "", "wisq_status": "error",
        "ratio_wisq_over_mine": "",
    }


# ── main ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare our compiler vs WISQ at parity of grid + magic placement."
    )

    # ── single-run mode ──
    parser.add_argument("--circuits", nargs="+", default=None,
                        help="Circuit names for single-run mode (e.g. qft_20 adder_n4)")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG),
                        help=f"Single-run compiler config (default: {DEFAULT_CONFIG})")

    # ── bench sweep mode ──
    parser.add_argument("--bench", default=None,
                        help="Sweep config path (e.g. data/config/params_bench.json). "
                             "Expands all parameter combinations and runs each one.")
    parser.add_argument("--dry-run", action="store_true",
                        help="With --bench: print the number of combinations and exit.")

    # ── shared options ──
    parser.add_argument("--binary", default=str(DEFAULT_BINARY),
                        help=f"Compiler binary (default: {DEFAULT_BINARY})")
    parser.add_argument("--mr_timeout", type=int, default=300,
                        help="WISQ mapping/routing timeout in seconds (default: 300)")
    parser.add_argument("--parity", type=int, choices=(0, 1), default=PARITY,
                        help="Data-qubit sub-lattice parity: 0=even, 1=odd (default: 0)")
    parser.add_argument("--output", "-o", default=None,
                        help="Write comparison CSV to this file (default: print summary only). "
                             "In bench mode, rows are appended incrementally so the run can "
                             "be interrupted and resumed.")
    parser.add_argument("--keep-arch-dir", default=None,
                        help="Directory to keep the generated WISQ arch files (default: temp, discarded)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of parallel workers (default: 1). Each worker runs one "
                             "(circuit, config) pair — compiler + WISQ — concurrently.")
    parser.add_argument("--wisq-workers", type=int, default=None,
                        help="Max concurrent WISQ instances (default: same as --workers). "
                             "Set lower than --workers to cap RAM usage: extra workers run "
                             "the compiler freely but queue before launching WISQ.")
    args = parser.parse_args()

    global _wisq_semaphore
    wisq_limit = args.wisq_workers if args.wisq_workers is not None else args.workers
    if wisq_limit < args.workers:
        _wisq_semaphore = threading.Semaphore(wisq_limit)
        print(f"WISQ concurrency limited to {wisq_limit} (workers={args.workers}).",
              file=sys.stderr)

    if args.bench is None and args.circuits is None:
        parser.error("Provide either --circuits (single-run) or --bench (sweep).")

    if args.bench is not None and args.circuits is not None:
        parser.error("--bench and --circuits are mutually exclusive.")

    binary = Path(args.binary)
    if not binary.exists():
        print(f"ERROR: compiler binary not found: {binary}\n"
              f"Build it first (e.g. `cmake --build build`).", file=sys.stderr)
        return 1

    arch_dir = (
        Path(args.keep_arch_dir)
        if args.keep_arch_dir
        else Path(tempfile.mkdtemp(prefix="wisq2_arch_"))
    )
    arch_dir.mkdir(parents=True, exist_ok=True)

    # ── bench sweep mode ─────────────────────────────────────────────────────────
    if args.bench is not None:
        bench_source = json.loads(Path(args.bench).read_text())
        expanded = expand_config_variants(bench_source)
        # Filter out entries without a circuit field.
        expanded = [c for c in expanded if c.get("circuit")]

        print(f"Expanded to {len(expanded)} configurations.", file=sys.stderr)

        if args.dry_run:
            print(f"Dry run: {len(expanded)} combinations would be processed.")
            return 0

        output_path = Path(args.output) if args.output else None

        # Resume support: skip (circuit, config) pairs already in the CSV.
        done_keys = load_done_keys_bench(output_path) if output_path else set()
        if done_keys:
            print(f"Resuming: {len(done_keys)} combinations already done, skipping.",
                  file=sys.stderr)

        csv_file = None
        writer = None
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            new_file = not output_path.exists() or output_path.stat().st_size == 0
            csv_file = output_path.open("a", newline="")
            writer = csv.DictWriter(csv_file, fieldnames=BENCH_CSV_COLUMNS)
            if new_file:
                writer.writeheader()
                csv_file.flush()

        # Build the list of (index, cfg) pairs that still need to run.
        todo = [
            (i, cfg) for i, cfg in enumerate(expanded)
            if cfg_key(cfg["circuit"], cfg) not in done_keys
        ]
        skipped = len(expanded) - len(todo)
        print(f"To run: {len(todo)}  (skipped {skipped} already done).", file=sys.stderr)

        rows: list[dict] = []
        completed = 0

        def _process(i: int, cfg: dict) -> dict:
            circuit = cfg["circuit"]
            try:
                result = run_one(circuit, cfg, binary, arch_dir,
                                 args.parity, args.mr_timeout, run_id=i)
                row = {**make_row_base(circuit, result, args.parity), **cfg_fields(cfg)}
            except (RuntimeError, FileNotFoundError) as e:
                print(f"  ERROR [{circuit}]: {e}", file=sys.stderr)
                row = {**make_error_row_base(circuit, args.parity), **cfg_fields(cfg)}
            return {k: row.get(k, "") for k in BENCH_CSV_COLUMNS}

        def _write_row(row: dict) -> None:
            nonlocal completed
            rows.append(row)
            completed += 1
            if writer:
                with _csv_write_lock:
                    writer.writerow(row)
                    csv_file.flush()
            print(f"  [{completed}/{len(todo)}] {row['circuit']} "
                  f"mine={row['my_routing_steps']} wisq={row['wisq_routing_steps']} "
                  f"ratio={row['ratio_wisq_over_mine']} status={row['wisq_status']}",
                  file=sys.stderr)

        if args.workers > 1:
            print(f"Running with {args.workers} parallel workers.", file=sys.stderr)
            _heartbeat_stop = threading.Event()

            def _heartbeat() -> None:
                while not _heartbeat_stop.wait(timeout=30):
                    with _active_wisq_lock:
                        n = _active_wisq
                    print(f"  [heartbeat] {completed}/{len(todo)} done, "
                          f"{n} WISQ running.", file=sys.stderr)

            threading.Thread(target=_heartbeat, daemon=True).start()

            with ThreadPoolExecutor(max_workers=args.workers) as executor:
                futures = {
                    executor.submit(_process, i, cfg): (i, cfg)
                    for i, cfg in todo
                }
                for fut in as_completed(futures):
                    _write_row(fut.result())

            _heartbeat_stop.set()
        else:
            for seq, (i, cfg) in enumerate(todo):
                print(f"\n──── [{seq+1}/{len(todo)}] {cfg['circuit']} ────",
                      file=sys.stderr)
                _write_row(_process(i, cfg))

        if csv_file:
            csv_file.close()

        if output_path:
            print(f"\nCSV written/appended to {output_path}")

        # Brief summary (last 20 rows to avoid flooding the terminal).
        print(f"\n=== Summary (last {min(20, len(rows))} of {len(rows)} new rows) ===")
        print(f"{'circuit':<28} {'type':>10} {'routing':>10} "
              f"{'mine':>6} {'wisq':>6} {'wisq/mine':>9} {'status':>9}")
        for r in rows[-20:]:
            print(f"{str(r['circuit']):<28} {str(r['type']):>10} "
                  f"{str(r['routing_strategy']):>10} "
                  f"{str(r['my_routing_steps']):>6} {str(r['wisq_routing_steps']):>6} "
                  f"{str(r['ratio_wisq_over_mine']):>9} {str(r['wisq_status']):>9}")

        if not args.keep_arch_dir:
            for p in arch_dir.glob("*_wisq2.arch"):
                p.unlink(missing_ok=True)
            try:
                arch_dir.rmdir()
            except OSError:
                pass

        return 0

    # ── single-run mode ──────────────────────────────────────────────────────────
    base_config = json.loads(Path(args.config).read_text())

    rows = []
    for circuit in args.circuits:
        print(f"\n──── {circuit} ────", file=sys.stderr)
        try:
            result = run_one(circuit, base_config, binary, arch_dir, args.parity, args.mr_timeout)
            rows.append(make_row_base(circuit, result, args.parity))
        except (RuntimeError, FileNotFoundError) as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            rows.append(make_error_row_base(circuit, args.parity))

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nCSV written to {out}")

    print("\n=== Summary (routing steps) ===")
    print(f"{'circuit':<28} {'qubits':>6} {'grid':>9} {'mine':>6} {'wisq':>6} "
          f"{'wisq/mine':>9} {'grown':>6} {'status':>9}")
    for r in rows:
        grid = f"{r['wisq_x']}x{r['wisq_y']}" if r["wisq_x"] != "" else "-"
        print(f"{r['circuit']:<28} {str(r['n_qubits']):>6} {grid:>9} "
              f"{str(r['my_routing_steps']):>6} {str(r['wisq_routing_steps']):>6} "
              f"{str(r['ratio_wisq_over_mine']):>9} {str(r['grid_grown_for_wisq']):>6} "
              f"{str(r['wisq_status']):>9}")

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
