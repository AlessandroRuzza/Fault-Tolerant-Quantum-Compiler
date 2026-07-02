#!/usr/bin/env python3
"""compare_wisq_minsearch.py — find WISQ's MINIMUM grid by a bounded upward scan,
then run our compiler on that exact grid under every bench combination.

Per circuit:
  1. SCAN candidate square sides s = 2*ceil(sqrt(n))-1, 2*ceil(sqrt(n)), ...,
     2*ceil(sqrt(n))+2, in order. At each candidate side s:
       a. our compiler runs at exactly (s, s) with the fixed ARCH-SEARCH config
          (connectivity + packing, border_distance_percentage = 5) and writes
          qasm_graphs/<circuit>.graph — the magic-state positions WISQ will use;
       b. a WISQ arch is built at EXACT s x s (our magic positions + even/even
          data slots, NO auto-grow). If the sub-lattice has fewer slots than the
          circuit's qubits the candidate fails without launching WISQ;
       c. WISQ runs on that arch. The candidate SUCCEEDS iff WISQ produces a
          routing result (a WISQ timeout or failure = candidate fails, so a low
          --mr_timeout inflates the "minimum" side).
     The scan starts at 2*ceil(sqrt(n))-1, the first side whose even/even
     sub-lattice can hold n qubits at all; the first succeeding side is WISQ's
     minimum. If EVERY side up to 2*ceil(sqrt(n))+2 fails, the minimum is taken
     to be WISQ's native side 2*ceil(sqrt(n))+3 — WISQ compiles there by
     construction on its own default square_sparse_layout — and WISQ is run on
     that native layout to obtain the routing steps (flagged
     wisq_native_fallback=True in the CSV).
  2. Run OUR compiler at the found minimum (s*, s*) — exact grid, never grown —
     once per bench parameter combination (e.g. connectivity|cube x
     packing|naive_critical from data/config/all_circuits_4_variants.json; the
     combos' own x/y are ignored). A combo that fails at s* still gets a row
     (my_* empty, my_status=failed) so the WISQ result is never lost.

Output: one CSV row per (circuit, combination). The wisq_* columns repeat the s*
search result on every row of the circuit (wisq_x = wisq_y = s*). Columns =
compare_wisq_2's bench schema + my_status + search_probes +
wisq_native_fallback, so extract/plot tooling keyed on the shared columns keeps
working.

Resume: rows are appended per combo; on restart, a circuit whose CSV rows already
carry a successful WISQ result reuses that s* (no re-search, no WISQ re-run) and
only the missing combos are executed.

Usage:
    python scripts/wisq_compare/compare_wisq_minsearch.py \
        --bench data/config/all_circuits_4_variants.json \
        --output data/results/<name>_wisqmin.csv --workers 8 --mr_timeout 600
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import json
import math
import subprocess
import sys
import tempfile
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Reuse the WISQ runner, arch helpers, graph/qasm readers, CSV schema and row
# formatters from compare_wisq_2, plus the exact-grid compiler helper from
# compare_wisq_mingrid.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_wisq_2 as cw2  # noqa: E402
import compare_wisq_mingrid as cwm  # noqa: E402

DEFAULT_BINARY = cw2.DEFAULT_BINARY

MINSEARCH_CSV_COLUMNS = cw2.BENCH_CSV_COLUMNS + ["my_status", "search_probes",
                                                 "wisq_native_fallback"]

# Config used ONLY to generate the arch (magic positions + data slots) fed to WISQ
# during the minimum-side search: the pesi_tunati CONNECTIVITY optimum with
# border_distance_percentage lowered to 5 (fits magic states on tighter grids) and
# packing routing. The final per-combo runs come from --bench, not from this.
ARCH_SEARCH_CONFIG = {
    "type": "gaussian",
    "gaussian_strategy": "fine",
    "safe_passage_strategy": "connectivity",
    "MagicStatePlacementStrategy": "center_circle",
    "border_distance_percentage": 5.0,
    "BFS_DENSITY_THRESHOLD": 0.7,
    "MAGIC_HIGH": 0.0,
    "MAGIC_LOW": 0.0,
    "CNOT_HIGH": 8.0,
    "CNOT_LOW": 0.0,
    "MAPPED_GAUSSIAN_WEIGHT": 20.0,
    "BASE_GAUSSIAN_WEIGHT": 1.0,
    "EXTERNAL_WEIGHT": -15.0,
    "GAUSSIAN_SIGMA": 0.7,
    "number_of_magic_states": -1,
    "routing_strategy": "packing",
    "t-routing-mode": "smart_t_routing",
    "patience_threshold": 3,
    "use_layer_cache": True,
    "repetition": 1,
    "timeout": 600,
    "timeout_reached": False,
}

_csv_write_lock = threading.Lock()


def search_lower_bound(n: int) -> int:
    """Smallest side whose even/even sub-lattice has >= n cells (before magic):
    ceil(s/2)^2 >= n  ->  s = 2*ceil(sqrt(n)) - 1."""
    return max(1, 2 * math.ceil(math.sqrt(n)) - 1)


def build_exact_arch(width: int, height: int, magic_flat: list[int], parity: int) -> dict:
    """WISQ arch at EXACT width x height — no growing, unlike cw2.build_wisq_arch."""
    magic_set = set(int(m) for m in magic_flat)
    slots = cw2.sublattice_slots(width, height, magic_set, parity)
    return {
        "width": width,
        "height": height,
        "alg_qubits": slots,
        "magic_states": sorted(magic_set),
    }


def probe_side(circuit: str, search_cfg: dict, binary: Path, side: int, parity: int,
               arch_dir: Path, mr_timeout: int, attempt_timeout: float | None,
               run_id: int) -> dict:
    """Test one candidate side: our arch-search run, exact arch, WISQ.

    Returns {"ok": bool, "why": str, ...}; on ok also "wisq", "n_slots", "n_qubits".
    """
    ok, _mine = cwm.run_compiler_at(circuit, search_cfg, binary, side, side,
                                    attempt_timeout)
    if not ok:
        return {"ok": False, "why": "arch-gen mapping failed"}

    graph = cw2.read_graph(circuit)
    n_qubits = cw2.count_qasm_qubits(circuit) or (_mine or {}).get("num_qubits")
    arch = build_exact_arch(graph["width"], graph["height"],
                            graph["magic_states"], parity)
    n_slots = len(arch["alg_qubits"])
    if n_qubits is not None and n_slots < n_qubits:
        return {"ok": False,
                "why": f"only {n_slots} slots for {n_qubits} qubits"}

    arch_path = arch_dir / f"{circuit}_{run_id}_s{side}_minsearch.arch"
    cw2.write_arch_file(arch, arch_path)
    try:
        wisq = cw2._run_wisq_with_limit(circuit, arch_path, mr_timeout)
    finally:
        arch_path.unlink(missing_ok=True)

    if wisq["status"] == "success" and wisq["routing_steps"] is not None:
        return {"ok": True, "why": "", "wisq": wisq,
                "n_slots": n_slots, "n_qubits": n_qubits}
    return {"ok": False, "why": f"wisq {wisq['status']}"}


def run_wisq_native_layout(circuit: str, mr_timeout: int) -> dict:
    """cw2.run_wisq, but on WISQ's OWN default square_sparse_layout (the native
    arch WISQ sizes itself). Used only by the native-side fallback. Honors the
    --wisq-workers concurrency cap."""
    qasm = cw2.UNIVERSAL_QASMS_DIR / f"{circuit}_universal.qasm"
    if not qasm.exists():
        raise FileNotFoundError(f"missing universal QASM: {qasm}")

    def _run() -> dict:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            out_path = Path(tmp.name)
        cmd = [
            str(cw2.WISQ), str(qasm),
            "--mode", "scmr",
            "-arch", "square_sparse_layout",
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
        return {"routing_steps": routing_steps, "duration_seconds": duration,
                "status": status, "exit_code": proc.returncode}

    if cw2._wisq_semaphore is not None:
        with cw2._wisq_semaphore:
            return _run()
    return _run()


def search_wisq_min_side(circuit: str, search_cfg: dict, binary: Path, parity: int,
                         arch_dir: Path, mr_timeout: int,
                         attempt_timeout: float | None, run_id: int):
    """Scan sides 2*ceil(sqrt(n))-1 .. 2*ceil(sqrt(n))+2 upward; first success is
    the minimum. All fail -> native side 2*ceil(sqrt(n))+3 (WISQ compiles there
    by construction on square_sparse_layout), run on the native layout.

    Returns ({"side", "wisq", "n_slots", "n_qubits", "search_probes",
    "native_fallback"}, None) or (None, reason).
    """
    n_in, _has_t = cw2._input_qasm_qubits_and_t(circuit)
    if not n_in:
        return None, f"cannot determine qubit count for {circuit} (missing/empty qasm)"

    lo = search_lower_bound(n_in)               # 2*ceil(sqrt(n)) - 1
    native = cw2.wisq_native_side(n_in)         # 2*ceil(sqrt(n)) + 3
    probes = 0
    for side in range(lo, native):              # lo .. native-1 (= 2*ceil(sqrt(n))+2)
        probes += 1
        r = probe_side(circuit, search_cfg, binary, side, parity, arch_dir,
                       mr_timeout, attempt_timeout, run_id)
        print(f"    [{circuit}] probe {side}x{side}: "
              f"{'OK' if r['ok'] else 'fail (' + r['why'] + ')'}", file=sys.stderr)
        if r["ok"]:
            return {"side": side, "wisq": r["wisq"], "n_slots": r["n_slots"],
                    "n_qubits": r["n_qubits"], "search_probes": probes,
                    "native_fallback": False}, None

    # Every side below native failed: the minimum is the native side by
    # construction. Run WISQ on its own square_sparse_layout to get the steps.
    print(f"    [{circuit}] all sides < {native} failed; native fallback "
          f"{native}x{native} (square_sparse_layout).", file=sys.stderr)
    if not (cw2.UNIVERSAL_QASMS_DIR / f"{circuit}_universal.qasm").exists():
        # No probe ever got past our compiler: generate the universal QASM once.
        cwm.run_compiler_at(circuit, search_cfg, binary, native, native,
                            attempt_timeout)
    wisq = run_wisq_native_layout(circuit, mr_timeout)
    n_q = cw2.count_qasm_qubits(circuit) or n_in
    built = cw2.native_built(n_q)
    return {"side": built["arch"]["width"], "wisq": wisq,
            "n_slots": built["n_slots"], "n_qubits": n_q,
            "search_probes": probes, "native_fallback": True}, None


def make_combo_row(circuit: str, cfg: dict, found: dict, parity: int,
                   mine: dict | None) -> dict:
    """One CSV row: our run (or its failure) at s* + the shared WISQ s* result."""
    side = found["side"]
    wisq = found["wisq"]
    row = {
        "circuit": circuit,
        "n_qubits": found["n_qubits"] if found["n_qubits"] is not None else "",
        "parity": parity,
        "wisq_x": side,
        "wisq_y": side,
        "wisq_routing_steps": wisq["routing_steps"],
        "wisq_duration_s": f"{wisq['duration_seconds']:.6f}",
        "wisq_n_slots": found["n_slots"],
        "grid_grown_for_wisq": "false",
        "wisq_status": wisq["status"],
        "safe_passage_fallback": "",
        "search_probes": found["search_probes"],
        "wisq_native_fallback": found.get("native_fallback", ""),
        **cw2.cfg_fields(cfg),
    }
    if mine is None:
        row.update({"my_x": "", "my_y": "", "my_routing_steps": "",
                    "my_duration_s": "", "ratio_wisq_over_mine": "",
                    "my_status": "failed"})
    else:
        ratio = None
        if wisq["routing_steps"] and mine["routing_steps"]:
            ratio = wisq["routing_steps"] / mine["routing_steps"]
        row.update({
            "my_x": mine["width"], "my_y": mine["height"],
            "my_routing_steps": mine["routing_steps"],
            "my_duration_s": (f"{mine['duration_seconds']:.6f}"
                              if mine["duration_seconds"] is not None else ""),
            "ratio_wisq_over_mine": f"{ratio:.4f}" if ratio is not None else "",
            "my_status": "success",
        })
    return {k: row.get(k, "") for k in MINSEARCH_CSV_COLUMNS}


def make_search_error_row(circuit: str, cfg: dict, parity: int) -> dict:
    row = {**cw2.make_error_row_base(circuit, parity), **cw2.cfg_fields(cfg)}
    row["wisq_status"] = "search_failed"
    row["my_status"] = ""
    row["search_probes"] = ""
    row["wisq_native_fallback"] = ""
    return {k: row.get(k, "") for k in MINSEARCH_CSV_COLUMNS}


def process_circuit(circuit: str, combos: list[dict], binary: Path, arch_dir: Path,
                    parity: int, mr_timeout: int,
                    attempt_timeout: float | None, run_id: int,
                    search_cfg: dict, prior: dict | None) -> list[dict]:
    """Search (or reuse) WISQ's minimum side, then run every combo at exactly it."""
    if prior is not None:
        found = prior
        print(f"  [{circuit}] reusing s*={found['side']} from existing CSV rows.",
              file=sys.stderr)
    else:
        found, reason = search_wisq_min_side(
            circuit, search_cfg, binary, parity, arch_dir,
            mr_timeout, attempt_timeout, run_id)
        if found is None:
            print(f"  ERROR [{circuit}]: {reason}", file=sys.stderr)
            return [make_search_error_row(circuit, cfg, parity) for cfg in combos]
        print(f"  [{circuit}] WISQ minimum side s*={found['side']} "
              f"({found['search_probes']} probes"
              f"{', native fallback' if found['native_fallback'] else ''}, "
              f"wisq={found['wisq']['routing_steps']} steps).", file=sys.stderr)

    side = found["side"]
    rows = []
    for cfg in combos:
        ok, mine = cwm.run_compiler_at(circuit, cfg, binary, side, side,
                                       attempt_timeout)
        if not ok:
            fields = cw2.cfg_fields(cfg)
            print(f"    [{circuit}] combo "
                  f"{fields['safe_passage_strategy']}/{fields['routing_strategy']} "
                  f"FAILED at {side}x{side}.", file=sys.stderr)
            rows.append(make_combo_row(circuit, cfg, found, parity, None))
        else:
            rows.append(make_combo_row(circuit, cfg, found, parity, mine))
    return rows


def load_prior(path: Path):
    """Existing CSV -> (done (circuit, config...) keys, circuit -> reusable s* info).

    A circuit's s* is reusable when any of its rows has wisq_status=success with
    grid and routing steps present — the search is then skipped entirely.
    """
    done_keys: set[tuple] = set()
    wisq_by_circuit: dict[str, dict] = {}
    if not path or not path.exists():
        return done_keys, wisq_by_circuit
    try:
        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                circ = (row.get("circuit") or "").strip()
                if not circ:
                    continue
                done_keys.add((circ,) + tuple(row.get(k, "")
                                              for k in cw2.CONFIG_FIELDS))
                if circ in wisq_by_circuit or row.get("wisq_status") != "success":
                    continue
                try:
                    wisq_by_circuit[circ] = {
                        "side": int(row["wisq_x"]),
                        "wisq": {
                            "routing_steps": int(row["wisq_routing_steps"]),
                            "duration_seconds": float(row["wisq_duration_s"] or 0.0),
                            "status": "success",
                            "exit_code": 0,
                        },
                        "n_slots": (int(row["wisq_n_slots"])
                                    if str(row.get("wisq_n_slots", "")).strip() else ""),
                        "n_qubits": (int(row["n_qubits"])
                                     if str(row.get("n_qubits", "")).strip() else None),
                        "search_probes": row.get("search_probes", ""),
                        "native_fallback": row.get("wisq_native_fallback", ""),
                    }
                except (KeyError, ValueError, TypeError):
                    pass
    except Exception:
        pass
    return done_keys, wisq_by_circuit


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Binary-search WISQ's minimum grid, then run our compiler on it "
                    "under every bench combination.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--bench", required=True,
                        help="Sweep config (JSON), expanded to all parameter "
                             "combinations; their x/y are ignored (s* is used).")
    parser.add_argument("--output", "-o", default=None,
                        help="CSV output path (rows appended; resume-safe per combo, "
                             "s* reused per circuit).")
    parser.add_argument("--binary", default=str(DEFAULT_BINARY),
                        help=f"Compiler binary (default: {DEFAULT_BINARY})")
    parser.add_argument("--search-config", default=None,
                        help="JSON file whose fields OVERRIDE the built-in arch-search "
                             "config (connectivity+packing, border 5).")
    parser.add_argument("--mr_timeout", type=int, default=300,
                        help="WISQ mapping/routing timeout in seconds (default: 300). "
                             "A WISQ timeout fails the candidate side, so too low a "
                             "value inflates the found minimum.")
    parser.add_argument("--attempt-timeout", type=float, default=None,
                        help="Per-attempt timeout (s) for OUR compiler runs; a timed-out "
                             "run counts as a failure (default: none).")
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
                        help="Print circuits, combo counts and search bounds, then exit.")
    args = parser.parse_args()

    if args.wisq_workers is not None and args.wisq_workers < args.workers:
        cw2._wisq_semaphore = threading.Semaphore(args.wisq_workers)
        print(f"WISQ concurrency limited to {args.wisq_workers}.", file=sys.stderr)

    binary = Path(args.binary)
    if not binary.exists():
        print(f"ERROR: compiler binary not found: {binary}", file=sys.stderr)
        return 1

    search_cfg = dict(ARCH_SEARCH_CONFIG)
    if args.search_config:
        overrides = json.loads(Path(args.search_config).read_text())
        search_cfg.update(overrides)
        print(f"Arch-search config overridden by {args.search_config}.", file=sys.stderr)

    arch_dir = (Path(args.keep_arch_dir) if args.keep_arch_dir
                else Path(tempfile.mkdtemp(prefix="wisqmin_arch_")))
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
            n_in, _ = cw2._input_qasm_qubits_and_t(c)
            if n_in:
                native = cw2.wisq_native_side(n_in)
                bounds = (f"scan [{search_lower_bound(n_in)}, {native - 1}], "
                          f"fallback {native}")
            else:
                bounds = "NO INPUT QASM"
            print(f"  {c}: {len(by_circuit[c])} combinations, {bounds}")
        return 0

    output_path = Path(args.output) if args.output else None
    done_keys, prior_wisq = load_prior(output_path) if output_path else (set(), {})
    if done_keys:
        print(f"Resuming: {len(done_keys)} combos already in CSV "
              f"({len(prior_wisq)} circuits with reusable s*).", file=sys.stderr)

    # Drop already-done combos; drop fully-done circuits; shard the rest by index.
    pending: "OrderedDict[str, list[dict]]" = OrderedDict()
    for c in circuits:
        todo_combos = [cfg for cfg in by_circuit[c]
                       if cw2.cfg_key(c, cfg) not in done_keys]
        if todo_combos:
            pending[c] = todo_combos
    todo = [
        (i, c) for i, c in enumerate(pending.keys())
        if args.process_count <= 1 or i % args.process_count == args.processor
    ]
    n_combos = sum(len(pending[c]) for _, c in todo)
    print(f"Circuits to run: {len(todo)} ({n_combos} combos).", file=sys.stderr)

    csv_file = None
    writer = None
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        csv_file = output_path.open("a", newline="")
        writer = csv.DictWriter(csv_file, fieldnames=MINSEARCH_CSV_COLUMNS)
        with _csv_write_lock:
            fcntl.flock(csv_file, fcntl.LOCK_EX)
            try:
                if output_path.stat().st_size == 0:
                    writer.writeheader()
                    csv_file.flush()
            finally:
                fcntl.flock(csv_file, fcntl.LOCK_UN)

    completed = 0

    def _process(i: int, circuit: str) -> list[dict]:
        combos = pending[circuit]
        try:
            return process_circuit(
                circuit, combos, binary, arch_dir, args.parity,
                args.mr_timeout, args.attempt_timeout,
                run_id=i, search_cfg=search_cfg,
                prior=prior_wisq.get(circuit),
            )
        except (RuntimeError, FileNotFoundError) as e:
            print(f"  ERROR [{circuit}]: {e}", file=sys.stderr)
            return [make_search_error_row(circuit, cfg, args.parity) for cfg in combos]

    def _write_rows(rows: list[dict]) -> None:
        nonlocal completed
        completed += 1
        if writer:
            with _csv_write_lock:
                fcntl.flock(csv_file, fcntl.LOCK_EX)
                try:
                    for row in rows:
                        writer.writerow(row)
                    csv_file.flush()
                finally:
                    fcntl.flock(csv_file, fcntl.LOCK_UN)
        for row in rows:
            my_grid = f"{row['my_x']}x{row['my_y']}" if row.get("my_x") else "?"
            wisq_grid = f"{row['wisq_x']}x{row['wisq_y']}" if row.get("wisq_x") else "?"
            print(f"[{completed}/{len(todo)}] {row['circuit']} "
                  f"{row['safe_passage_strategy']}/{row['routing_strategy']} "
                  f"my_grid={my_grid} wisq_grid={wisq_grid} "
                  f"mine={row['my_routing_steps']} wisq={row['wisq_routing_steps']} "
                  f"ratio={row['ratio_wisq_over_mine']} my_status={row['my_status']} "
                  f"wisq_status={row['wisq_status']}", file=sys.stderr)

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(_process, i, c): c for i, c in todo}
            for fut in as_completed(futures):
                _write_rows(fut.result())
    else:
        for i, c in todo:
            print(f"\n──── {c} ({len(pending[c])} combos) ────", file=sys.stderr)
            _write_rows(_process(i, c))

    if csv_file:
        csv_file.close()
    if output_path:
        print(f"\nCSV written/appended to {output_path}")

    if not args.keep_arch_dir:
        for p in arch_dir.glob("*_minsearch.arch"):
            p.unlink(missing_ok=True)
        try:
            arch_dir.rmdir()
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
