#!/usr/bin/env python3
"""compare_offset.py — our compiler vs WISQ at PARITY of grid, swept over a set of
grid OFFSETS added to WISQ's native side.

Question this answers
---------------------
Is there a grid DIMENSION at which we beat WISQ at PARITY of dimension, or does
WISQ become more likely to win as the grid grows? For every circuit we evaluate a
SQUARE grid of side

    side(offset) = wisq_native_side(n) + offset          (offset >= 0, per side)

where wisq_native_side(n) = 2*ceil(sqrt(n)) + 3 is the side WISQ would pick for
itself (square_sparse_layout, all_sides magic). BOTH compilers are forced onto that
exact side, for each offset in --offsets, and we record routing steps for each.

Why "parity" WISQ and not square_sparse
---------------------------------------
WISQ's native square_sparse_layout sizes ITSELF from the qubit count — it cannot be
told to use a bigger grid. The only way to put WISQ on side = native+offset is to
hand it a custom arch at that side. We reuse compare_wisq_2.build_wisq_arch: WISQ
gets OUR mapping's magic-state positions + the even/even data sub-lattice on the
(native+offset) grid (cw2._wisq_native is left False). So both sides share the same
grid AND the same magic placement — true dimension parity at every offset. NOTE:
this means the offset=0 numbers are NOT the square_sparse `--wisq-native` baseline;
the sweep is internally consistent across offsets (same parity arch everywhere),
which is what the trend needs.

Two subcommands
---------------
  run     For every (circuit, offset): force OUR compiler onto (side, side), then
          run WISQ on the same (side, side) parity arch. One row per (circuit,
          offset). Resume- and cluster-shard-safe. Grouped by circuit so a single
          worker owns a circuit (the compiler writes a fixed qasm_graphs path).

  report  Aggregate the runs CSV per offset: WIN/LOSS/TIE counts (WIN = we use
          FEWER routing steps), geomean and median of wisq/mine, plus WISQ/our
          failure counts. The per-offset table is the answer: read the WIN column
          down the offsets to see whether our edge grows or decays with dimension.

Typical use (cluster, inside ftqc.sif via pbs/run_wisq_offset.pbs)
------------------------------------------------------------------
  python scripts/wisq_compare/compare_offset.py run \
      --bench config/offset_native_parity.json \
      --offsets 0,2,4,6,8 \
      -o benchmarks/results/offset_native_parity_runs.csv \
      --workers 28 --mr_timeout 600

  python scripts/wisq_compare/compare_offset.py report \
      --runs benchmarks/results/offset_native_parity_runs.csv \
      --out-dir results/
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import json
import math
import statistics
import sys
import threading
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_wisq_2 as cw2  # noqa: E402
import compare_wisq_mingrid as cw3   # noqa: E402  (run_compiler_at: explicit-grid runner)

DEFAULT_BINARY = cw2.DEFAULT_BINARY

# One row per (circuit, offset): circuit identity + the offset/grid + both results.
RUN_COLUMNS = [
    "circuit", "n_qubits", "offset", "side",
    "type", "safe_passage_strategy",
    "my_routing_steps", "my_duration_s",
    "wisq_x", "wisq_y", "wisq_routing_steps", "wisq_duration_s",
    "wisq_n_slots", "grid_grown_for_wisq", "wisq_status",
    "ratio_wisq_over_mine", "verdict",
    "safe_passage_fallback",
]

_csv_write_lock = threading.Lock()


def parse_offsets(spec: str) -> list[int]:
    """'0,2,4,6,8' -> [0, 2, 4, 6, 8]; sorted, de-duplicated, non-negative."""
    vals = sorted({int(p) for p in spec.split(",") if p.strip() != ""})
    if any(v < 0 for v in vals):
        raise ValueError(f"offsets must be >= 0 (grid grows from native), got {spec}")
    return vals


def _verdict(mine: int | None, wisq: int | None) -> str:
    if mine is None or wisq is None:
        return "n/a"
    if mine < wisq:
        return "WIN"      # we use FEWER routing steps
    if mine > wisq:
        return "LOSS"
    return "TIE"


# ── run: OUR compiler + WISQ both forced to side = native+offset ──────────────────

def run_one_offset(circuit: str, cfg: dict, binary: Path, n_qubits_in: int,
                   side: int, offset: int, arch_dir: Path, parity: int,
                   mr_timeout: int, attempt_timeout: float | None,
                   run_id: int) -> dict:
    """Run our compiler at (side, side), then WISQ on the same parity arch.

    Mirrors compare_random.run_combo's cube->connectivity mapping fallback: a cube
    run can fail to MAP even on a roomy grid; we retry once at the SAME side with the
    connectivity config so the dimension is preserved.
    """
    row = {
        "circuit": circuit,
        "n_qubits": "",
        "offset": offset,
        "side": side,
        "type": cfg.get("type", ""),
        "safe_passage_strategy": cfg.get("safe_passage_strategy", ""),
        "my_routing_steps": "", "my_duration_s": "",
        "wisq_x": "", "wisq_y": "", "wisq_routing_steps": "", "wisq_duration_s": "",
        "wisq_n_slots": "", "grid_grown_for_wisq": "", "wisq_status": "skipped",
        "ratio_wisq_over_mine": "", "verdict": "n/a",
        "safe_passage_fallback": "",
    }

    ok, mine = cw3.run_compiler_at(circuit, cfg, binary, side, side, attempt_timeout)
    fb = ""
    if not ok and cfg.get("safe_passage_strategy") == "cube":
        ok, mine = cw3.run_compiler_at(
            circuit, {**cfg, **cw2.CONNECTIVITY_FALLBACK_OVERRIDES}, binary,
            side, side, attempt_timeout)
        fb = "connectivity" if ok else "connectivity(failed)"
    row["safe_passage_fallback"] = fb

    if not ok:
        row["wisq_status"] = "our_compiler_failed"
        print(f"  ERROR [{circuit} off+{offset}]: our compiler produced no routing "
              f"result at {side}x{side}", file=sys.stderr)
        return {k: row.get(k, "") for k in RUN_COLUMNS}

    n_qubits = cw2.count_qasm_qubits(circuit) or mine.get("num_qubits") or n_qubits_in
    row["n_qubits"] = n_qubits
    row["my_routing_steps"] = mine["routing_steps"]
    row["my_duration_s"] = (f'{mine["duration_seconds"]:.6f}'
                            if mine["duration_seconds"] is not None else "")

    # WISQ on the SAME (side, side) grid: our magic positions + even/even slots.
    # cw2.MAX_GROW_STEPS (set in main) caps WISQ-side growth; with cap 0 the grid is
    # held at exactly side x side (it fits at native+offset, so no growth is needed).
    # A WISQ launch/parse failure must not abort the whole sweep: keep OUR result and
    # mark the WISQ side as errored so the (circuit, offset) row is still recorded.
    graph = cw2.read_graph(circuit)
    built = cw2.build_wisq_arch(graph["width"], graph["height"],
                                graph["magic_states"], n_qubits, parity)
    try:
        wisq = cw2.get_or_run_wisq(circuit, built, arch_dir, mr_timeout, run_id)
    except Exception as e:  # noqa: BLE001 — never let one WISQ run kill the sweep
        print(f"  ERROR [{circuit} off+{offset}]: WISQ run failed: {e}",
              file=sys.stderr)
        row.update({"wisq_x": built["arch"]["width"], "wisq_y": built["arch"]["height"],
                    "wisq_n_slots": built["n_slots"],
                    "grid_grown_for_wisq": "true" if built["grown"] else "false",
                    "wisq_status": "error"})
        return {k: row.get(k, "") for k in RUN_COLUMNS}

    w_steps = wisq["routing_steps"]
    row.update({
        "wisq_x": built["arch"]["width"], "wisq_y": built["arch"]["height"],
        "wisq_routing_steps": w_steps if w_steps is not None else "",
        "wisq_duration_s": f'{wisq["duration_seconds"]:.6f}',
        "wisq_n_slots": built["n_slots"],
        "grid_grown_for_wisq": "true" if built["grown"] else "false",
        "wisq_status": wisq["status"],
    })
    if w_steps and mine["routing_steps"]:
        row["ratio_wisq_over_mine"] = f'{w_steps / mine["routing_steps"]:.4f}'
    row["verdict"] = _verdict(mine["routing_steps"], w_steps)
    return {k: row.get(k, "") for k in RUN_COLUMNS}


def load_done_keys(path: Path) -> set[tuple]:
    """(circuit, offset) pairs already present with OUR routing result."""
    if not path.exists():
        return set()
    done: set[tuple] = set()
    try:
        with path.open(newline="") as f:
            for r in csv.DictReader(f):
                if str(r.get("my_routing_steps", "")).strip():
                    done.add((r["circuit"], str(r.get("offset", ""))))
    except Exception:
        pass
    return done


def cmd_run(args: argparse.Namespace) -> int:
    binary = Path(args.binary)
    if not binary.exists():
        print(f"ERROR: compiler binary not found: {binary}", file=sys.stderr)
        return 1

    offsets = parse_offsets(args.offsets)

    # WISQ is forced onto OUR parity grid (NOT square_sparse). Hold it at our side:
    # --wisq-max-grow 0 (default) means the grid never grows past native+offset.
    cw2._wisq_native = False
    cw2.MAX_GROW_STEPS = args.wisq_max_grow

    if args.wisq_workers is not None and args.wisq_workers < args.workers:
        cw2._wisq_semaphore = threading.Semaphore(args.wisq_workers)
        print(f"WISQ concurrency limited to {args.wisq_workers}.", file=sys.stderr)

    import tempfile
    arch_dir = (Path(args.keep_arch_dir) if args.keep_arch_dir
                else Path(tempfile.mkdtemp(prefix="offset_arch_")))
    arch_dir.mkdir(parents=True, exist_ok=True)

    source = json.loads(Path(args.bench).read_text())
    combos = [c for c in cw2.expand_config_variants(source) if c.get("circuit")]
    # One combo per circuit (first wins); group so a worker owns a circuit (the
    # compiler always writes qasm_graphs/<circuit>.graph).
    by_circuit: "OrderedDict[str, dict]" = OrderedDict()
    for cfg in combos:
        by_circuit.setdefault(cfg["circuit"], cfg)
    circuits = list(by_circuit.keys())
    print(f"{len(circuits)} circuits x {len(offsets)} offsets {offsets} "
          f"(both sides at native+offset; WISQ parity arch, grow cap "
          f"{args.wisq_max_grow}).", file=sys.stderr)

    if args.dry_run:
        for c in circuits:
            n, _ = cw2._input_qasm_qubits_and_t(c)
            base = cw2.wisq_native_side(n) if n else None
            sides = [base + o for o in offsets] if base else "?"
            print(f"  {c}  n={n} native={base} sides={sides}")
        return 0

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_keys(out_path)
    if done:
        print(f"Resuming: {len(done)} (circuit, offset) results already present.",
              file=sys.stderr)

    todo = [
        (i, c) for i, c in enumerate(circuits)
        if args.process_count <= 1 or i % args.process_count == args.processor
    ]
    print(f"Circuits for this process: {len(todo)}.", file=sys.stderr)

    csv_file = out_path.open("a", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=RUN_COLUMNS)
    with _csv_write_lock:
        fcntl.flock(csv_file, fcntl.LOCK_EX)
        try:
            if out_path.stat().st_size == 0:
                writer.writeheader()
                csv_file.flush()
        finally:
            fcntl.flock(csv_file, fcntl.LOCK_UN)

    completed = 0

    def _emit(row: dict) -> None:
        nonlocal completed
        completed += 1
        with _csv_write_lock:
            fcntl.flock(csv_file, fcntl.LOCK_EX)
            try:
                writer.writerow(row)
                csv_file.flush()
            finally:
                fcntl.flock(csv_file, fcntl.LOCK_UN)
        print(f"[{completed}] {row['circuit']:30s} off+{row['offset']:<2} "
              f"side={row['side']} mine={row['my_routing_steps']} "
              f"wisq={row['wisq_routing_steps']} -> {row['verdict']} "
              f"({row['wisq_status']})", file=sys.stderr)

    def _process(idx: int, circuit: str) -> list[dict]:
        cfg = by_circuit[circuit]
        n_in, _ = cw2._input_qasm_qubits_and_t(circuit)
        out: list[dict] = []
        if not n_in:
            for o in offsets:
                out.append({**{k: "" for k in RUN_COLUMNS}, "circuit": circuit,
                            "offset": o, "wisq_status": "no_qubit_count",
                            "verdict": "n/a"})
            return out
        base = cw2.wisq_native_side(n_in)
        for o in offsets:
            if (circuit, str(o)) in done:
                continue
            try:
                out.append(run_one_offset(
                    circuit, cfg, binary, n_in, base + o, o, arch_dir, args.parity,
                    args.mr_timeout, args.attempt_timeout, run_id=idx))
            except Exception as e:  # noqa: BLE001 — isolate per-(circuit,offset) failures
                print(f"  ERROR [{circuit} off+{o}]: {e}", file=sys.stderr)
                out.append({**{k: "" for k in RUN_COLUMNS}, "circuit": circuit,
                            "n_qubits": n_in, "offset": o, "side": base + o,
                            "wisq_status": "error", "verdict": "n/a"})
        return out

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(_process, i, c): c for i, c in todo}
            for fut in as_completed(futures):
                for row in fut.result():
                    _emit(row)
    else:
        for i, c in todo:
            for row in _process(i, c):
                _emit(row)

    csv_file.close()
    print(f"\nRuns CSV written/appended to {out_path}")

    if not args.keep_arch_dir:
        for p in arch_dir.glob("*_wisq2.arch"):
            p.unlink(missing_ok=True)
        try:
            arch_dir.rmdir()
        except OSError:
            pass
    return 0


# ── report: aggregate per offset ──────────────────────────────────────────────────

def _int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def cmd_report(args: argparse.Namespace) -> int:
    rows = list(csv.DictReader(Path(args.runs).open(newline="")))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    by_off: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        o = _int(r.get("offset"))
        if o is not None:
            by_off[o].append(r)

    lines = [
        "# Our compiler vs WISQ at PARITY of grid, swept over grid offsets",
        "",
        "Both compilers forced onto a square grid of side = `wisq_native_side(n) + "
        "offset` (per side). WISQ runs on a custom PARITY arch at that side (our "
        "magic positions + even/even data slots) — square_sparse cannot be resized, "
        "so this is the only way to put WISQ at the same dimension. `WIN` = we use "
        "FEWER routing steps. `geomean wisq/mine` > 1 ⇒ we are better on average.",
        "",
        "| offset (+/side) | circuits | WIN | LOSS | TIE | n/a | WISQ fail | "
        "geomean wisq/mine | median wisq/mine |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    summary_rows = []
    for o in sorted(by_off):
        rs = by_off[o]
        counts = {"WIN": 0, "LOSS": 0, "TIE": 0, "n/a": 0}
        ratios: list[float] = []
        wisq_fail = 0
        for r in rs:
            counts[r.get("verdict", "n/a") if r.get("verdict") in counts else "n/a"] += 1
            st = r.get("wisq_status", "")
            if st not in ("success", "", "skipped"):
                wisq_fail += 1
            try:
                ratios.append(float(r["ratio_wisq_over_mine"]))
            except (KeyError, ValueError):
                pass
        geomean = (math.exp(sum(math.log(x) for x in ratios) / len(ratios))
                   if ratios else None)
        median = statistics.median(ratios) if ratios else None
        lines.append(
            f"| +{o} | {len(rs)} | {counts['WIN']} | {counts['LOSS']} | "
            f"{counts['TIE']} | {counts['n/a']} | {wisq_fail} | "
            f"{geomean:.3f} | {median:.3f} |"
            if geomean is not None else
            f"| +{o} | {len(rs)} | {counts['WIN']} | {counts['LOSS']} | "
            f"{counts['TIE']} | {counts['n/a']} | {wisq_fail} |  |  |")
        summary_rows.append({
            "offset": o, "circuits": len(rs), **counts, "wisq_fail": wisq_fail,
            "geomean_wisq_over_mine": f"{geomean:.4f}" if geomean else "",
            "median_wisq_over_mine": f"{median:.4f}" if median else "",
        })

    lines += [
        "",
        "Read the WIN column down the offsets: a falling WIN count (and a geomean "
        "drifting toward / below 1.0) means WISQ catches up as the grid grows; a "
        "rising WIN count means extra dimension favours us.",
        "",
    ]
    md_path = out_dir / "offset_parity_vs_wisq_results.md"
    md_path.write_text("\n".join(lines) + "\n")

    csv_path = out_dir / "offset_parity_vs_wisq_summary.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()) if summary_rows
                           else ["offset"])
        w.writeheader()
        w.writerows(summary_rows)

    print(f"Wrote:\n  {md_path}\n  {csv_path}")
    # Echo the table so the answer is visible without opening the file.
    print("\n".join(lines))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="Run our compiler + WISQ at native+offset, per circuit/offset.")
    pr.add_argument("--bench", required=True, help="Single-combo sweep config (JSON).")
    pr.add_argument("--offsets", default="0,2,4,6,8",
                    help="Comma-separated per-side grid offsets added to "
                         "wisq_native_side(n) (default: 0,2,4,6,8).")
    pr.add_argument("--output", "-o", required=True, help="Runs CSV (append/resume).")
    pr.add_argument("--binary", default=str(DEFAULT_BINARY))
    pr.add_argument("--parity", type=int, choices=(0, 1), default=cw2.PARITY,
                    help="Data-qubit sub-lattice parity for the WISQ arch (default: 0).")
    pr.add_argument("--mr_timeout", type=int, default=300,
                    help="WISQ mapping/routing timeout in seconds (default: 300).")
    pr.add_argument("--attempt-timeout", type=float, default=None,
                    help="Per-attempt timeout (s) for our compiler (default: none).")
    pr.add_argument("--wisq-max-grow", type=int, default=0,
                    help="Cap on WISQ-side grid growth (default 0 = hold WISQ at our "
                         "native+offset grid; it fits there, so 0 keeps strict parity).")
    pr.add_argument("--workers", type=int, default=1)
    pr.add_argument("--wisq-workers", type=int, default=None,
                    help="Max concurrent WISQ instances (default: same as --workers).")
    pr.add_argument("--keep-arch-dir", default=None)
    pr.add_argument("--process-count", type=int, default=1)
    pr.add_argument("--processor", type=int, default=0)
    pr.add_argument("--dry-run", action="store_true")
    pr.set_defaults(func=cmd_run)

    pp = sub.add_parser("report", help="Aggregate the runs CSV per offset.")
    pp.add_argument("--runs", required=True, help="Runs CSV from `run`.")
    pp.add_argument("--out-dir", default="results")
    pp.set_defaults(func=cmd_report)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
