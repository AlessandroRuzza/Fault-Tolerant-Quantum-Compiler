#!/usr/bin/env python3
"""
Generate QASM circuits with MQT Bench, transpiled to a gate set the
Fault-Tolerant-Quantum-Compiler parser understands.

Why transpile?
  The compiler's QASM parser (src/circuit.cpp) only treats these as
  routing-relevant operations:
    - cx / cnot / cz / cphase  -> 2-qubit CNOT interactions
    - t / tdg                  -> magic-state (T) gates
  Everything else (h, rz, cp, sx, ...) is ignored. MQT Bench's INDEP
  level emits e.g. `cp(pi/2)` for QFT, which the parser would drop,
  leaving a circuit with no 2-qubit interactions. We therefore transpile
  every circuit to the basis {cx, u, t, tdg} so the CNOT interaction
  structure survives — matching the existing qasms/ files (cx + u).

Requires the local venv with mqt.bench installed:
  .venv-mqt/bin/python scripts/generate_mqt_circuits.py [options]

Examples:
  # default set, sizes 50/100/200/400, into qasms/
  .venv-mqt/bin/python scripts/generate_mqt_circuits.py

  # specific algorithms and sizes
  .venv-mqt/bin/python scripts/generate_mqt_circuits.py \
      --benchmarks qft qaoa graphstate grover \
      --sizes 64 128 256

  # list every algorithm MQT Bench can generate
  .venv-mqt/bin/python scripts/generate_mqt_circuits.py --list
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "qasms"

# Basis the compiler's parser understands (2-qubit interactions as cx,
# magic gates as t/tdg, everything else collapsed into single-qubit u).
TARGET_BASIS = ["cx", "u", "t", "tdg"]

# A spread of topologies useful for mapping/routing research:
#   qft/qftentangled -> all-to-all (dense interaction graph)
#   qaoa/graphstate  -> sparse / k-regular random graphs
#   ghz/wstate       -> chain / star
#   grover/dj/bv     -> algorithmic structure
#   *_adder/multiplier -> block-structured arithmetic
DEFAULT_BENCHMARKS = ["qft", "qaoa", "graphstate", "ghz", "grover", "wstate"]
DEFAULT_SIZES = [50, 100, 200, 400]


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--benchmarks", nargs="*", default=DEFAULT_BENCHMARKS,
                        help=f"Algorithm names (default: {DEFAULT_BENCHMARKS})")
    parser.add_argument("--sizes", nargs="*", type=int, default=DEFAULT_SIZES,
                        help=f"Qubit counts (default: {DEFAULT_SIZES})")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"Output dir (default: {DEFAULT_OUT})")
    parser.add_argument("--opt-level", type=int, default=1,
                        help="Qiskit transpile optimization level (default: 1)")
    parser.add_argument("--keep-measure", action="store_true",
                        help="Keep measurement/barrier lines (default: stripped)")
    parser.add_argument("--list", action="store_true",
                        help="List available benchmark names and exit")
    args = parser.parse_args()

    try:
        from mqt.bench import get_benchmark, BenchmarkLevel
        from mqt.bench.benchmarks import get_available_benchmark_names
        from qiskit import transpile
        from qiskit.qasm2 import dumps
    except ImportError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Run with the venv python: .venv-mqt/bin/python scripts/generate_mqt_circuits.py",
              file=sys.stderr)
        sys.exit(1)

    if args.list:
        for name in get_available_benchmark_names():
            print(name)
        return

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Output dir : {args.out}")
    print(f"Basis      : {TARGET_BASIS}")
    print(f"Benchmarks : {args.benchmarks}")
    print(f"Sizes      : {args.sizes}\n")

    ok, failed = 0, 0
    for bench in args.benchmarks:
        for n in args.sizes:
            label = f"{bench}_n{n}"
            try:
                qc = get_benchmark(benchmark=bench, level=BenchmarkLevel.INDEP,
                                   circuit_size=n)
                qc = transpile(qc, basis_gates=TARGET_BASIS,
                               optimization_level=args.opt_level)
                qasm = dumps(qc)

                if not args.keep_measure:
                    qasm = strip_measurements(qasm)

                counts = Counter(re.findall(r"^([a-z]+)", qasm, re.M))
                ncx = counts.get("cx", 0)
                if ncx == 0:
                    print(f"  SKIP {label}: 0 CNOT after transpile (no 2-qubit structure)")
                    failed += 1
                    continue

                out_path = args.out / f"{label}.qasm"
                out_path.write_text(qasm)
                print(f"  OK   {label:24} cx={ncx:6}  t={counts.get('t',0)+counts.get('tdg',0):5}")
                ok += 1
            except Exception as e:
                print(f"  FAIL {label}: {e}")
                failed += 1

    print(f"\nDone: {ok} generated, {failed} failed/skipped.")


def strip_measurements(qasm: str) -> str:
    """Remove measure/barrier/creg lines — the compiler ignores them and
    they bloat the file. Keep the qreg and gate lines."""
    kept = []
    for line in qasm.splitlines():
        s = line.strip()
        if s.startswith("measure") or s.startswith("barrier") or s.startswith("creg"):
            continue
        kept.append(line)
    return "\n".join(kept) + "\n"


if __name__ == "__main__":
    main()
