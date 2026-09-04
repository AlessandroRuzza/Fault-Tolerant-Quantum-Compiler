#!/usr/bin/env python3
"""Generate QASM circuits with MQT Bench, for feeding to scripts/build_test_set.py.

MQT Bench is a generator, not a download: it builds each circuit on demand at the
size you ask for. This script writes one .qasm per (benchmark, qubit count) into a
directory that `build_test_set.py --source` then reads like any other suite.

By default it generates only the algorithms this repository does not already have
somewhere — `qasms/` covers ghz, graphstate, qft, qaoa, vqe_*, wstate and friends,
and duplicating them into a *test* set would defeat the point of holding it apart
from the circuits the compiler is tuned on.

    scripts/gen_mqt_bench.py --out MQTBench --sizes 5,10,20,40,60,80,100,125
    scripts/gen_mqt_bench.py --list

Needs `pip install mqt.bench` — on the generating machine only. The output is
plain OpenQASM 2, so the cluster never needs mqt.bench installed.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "MQTBench"

# Families already in qasms/ or reachable from QASMBench: generating them again
# would put development circuits into the test set.
ALREADY_HAVE = {
    "bv", "ghz", "graphstate", "grover", "hhl", "multiplier", "qaoa", "qft",
    "randomcircuit", "vqe_real_amp", "vqe_su2", "vqe_two_local", "wstate",
}

DEFAULT_SIZES = [5, 10, 20, 30, 40, 60, 80, 100, 125]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate MQT Bench circuits as OpenQASM 2 files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--out", type=Path, default=DEFAULT_OUT,
                   help="directory to write the circuits into")
    p.add_argument("--sizes", default=",".join(str(n) for n in DEFAULT_SIZES),
                   help="comma-separated qubit counts to ask for")
    p.add_argument("--benchmarks", default=None,
                   help="comma-separated names (default: everything this repo "
                        "does not already have)")
    p.add_argument("--all", action="store_true",
                   help="include the families the repo already has")
    p.add_argument("--level", choices=["alg", "indep"], default="indep",
                   help="MQT abstraction level. 'indep' is target-independent, "
                        "already decomposed into a standard gate set, which is what "
                        "WISQ's qiskit front-end can read; 'alg' keeps high-level "
                        "gates that often fail to translate")
    p.add_argument("--no-decompose", action="store_true",
                   help="export MQT's circuit as it comes. Off by default because "
                        "MQT emits composite instructions (gate_Carry, gate_Sum, "
                        "circuit_1049) that QASM 2 records as opaque gate "
                        "definitions; qiskit reads them back as opaque, and WISQ's "
                        "BasisTranslator then refuses the circuit. Flattening into "
                        "{rz, h, x, cx} — the very basis WISQ translates to — is "
                        "what makes the arithmetic families convertible at all")
    p.add_argument("--force", action="store_true",
                   help="regenerate circuits whose file already exists")
    p.add_argument("--list", action="store_true",
                   help="print what would be generated and exit")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        from mqt.bench import BenchmarkLevel, get_benchmark
        from mqt.bench.benchmarks import get_available_benchmark_names
    except ImportError:
        raise SystemExit("mqt.bench is not installed — `pip install mqt.bench`")

    from qiskit import qasm2, transpile

    # The basis WISQ's own front-end targets, so flattening here changes nothing
    # about what WISQ will do with the circuit.
    FLAT_BASIS = ["rz", "h", "x", "cx"]

    available = sorted(get_available_benchmark_names())
    if args.benchmarks:
        wanted = [b.strip() for b in args.benchmarks.split(",") if b.strip()]
        unknown = [b for b in wanted if b not in available]
        if unknown:
            raise SystemExit(f"unknown benchmark(s): {', '.join(unknown)}\n"
                             f"available: {', '.join(available)}")
    elif args.all:
        wanted = available
    else:
        wanted = [b for b in available if b not in ALREADY_HAVE]

    sizes = [int(n) for n in args.sizes.split(",") if n.strip()]
    level = BenchmarkLevel.ALG if args.level == "alg" else BenchmarkLevel.INDEP

    if args.list:
        print(f"{len(wanted)} benchmarks x {len(sizes)} sizes = "
              f"{len(wanted) * len(sizes)} circuits at most")
        print(f"sizes     : {', '.join(str(n) for n in sizes)}")
        print(f"benchmarks: {', '.join(wanted)}")
        skipped = sorted(set(available) - set(wanted))
        if skipped:
            print(f"skipped   : {', '.join(skipped)}")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    log_path = args.out / "_generation_log.csv"
    rows: list[dict] = []
    written = 0

    for name in wanted:
        for size in sizes:
            stem = f"{name}_n{size}"
            target = args.out / f"{stem}.qasm"
            if target.exists() and not args.force:
                print(f"  exists  {stem}", flush=True)
                continue

            row = {"circuit": stem, "benchmark": name, "size": size,
                   "status": "", "qubits": "", "gates": "", "error": ""}
            try:
                circuit = get_benchmark(benchmark=name, level=level, circuit_size=size)
                if not args.no_decompose:
                    circuit = transpile(circuit, basis_gates=FLAT_BASIS,
                                        optimization_level=0)
                # Not every circuit survives the trip to OpenQASM 2: the dynamic
                # families carry mid-circuit control flow that QASM 2 cannot express.
                text = qasm2.dumps(circuit)
            except Exception as exc:
                row["status"] = "failed"
                row["error"] = f"{type(exc).__name__}: {exc}"[:200]
                print(f"  FAILED  {stem}: {row['error']}", flush=True)
                rows.append(row)
                continue

            target.write_text(text)
            row["status"] = "ok"
            row["qubits"] = circuit.num_qubits
            row["gates"] = sum(circuit.count_ops().values())
            written += 1
            print(f"  ok      {stem}  {row['qubits']}q  {row['gates']} gates",
                  flush=True)
            rows.append(row)

    # Merge with what earlier passes recorded: sizes are usually filled in over
    # several runs (the constrained families only accept multiples of 13, 17, ...),
    # and a fresh log each time would erase the history of what was tried.
    failed = sum(1 for r in rows if r["status"] == "failed")

    if rows:
        merged = {}
        if log_path.exists():
            with log_path.open(newline="") as fh:
                for row in csv.DictReader(fh):
                    merged[row["circuit"]] = row
        for row in rows:
            merged[row["circuit"]] = row
        rows = list(merged.values())

        with log_path.open("w", newline="") as fh:
            writer = csv.DictWriter(
                fh, fieldnames=["circuit", "benchmark", "size", "status",
                                "qubits", "gates", "error"])
            writer.writeheader()
            writer.writerows(sorted(rows, key=lambda r: r["circuit"]))

    total = len(list(args.out.glob("*.qasm")))
    print(f"\nwritten {written}, failed {failed}; {args.out} now holds {total} circuits")
    print(f"log: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
