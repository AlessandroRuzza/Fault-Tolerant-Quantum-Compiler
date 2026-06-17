#!/usr/bin/env python3
"""
Generate 1-D Transverse-Field Ising Model (TFIM) circuits as QASM, transpiled to
the gate set the Fault-Tolerant-Quantum-Compiler parser understands.

MQT Bench (the version in .venv-mqt) does not expose an "ising" benchmark, but
the existing qasms/ising_n*.qasm files are plain 1-D nearest-neighbour TFIM
Trotter circuits: per Trotter step, RZZ on every chain bond (in an even/odd
"brick" order) plus RX on every qubit, after an initial layer of H. Structurally,
for the router this is a CHAIN interaction graph (cx between neighbours, no T
gates). e.g. ising_n26: 50 cx = 2 x 25 bonds (one step); ising_n420: 838 cx.

This reproduces that pattern for arbitrary qubit counts, transpiling to the same
basis {cx, u, t, tdg} and stripping measurements, exactly like
generate_mqt_circuits.py. Files are named ising_n<N>.qasm.

Requires the local venv (qiskit):
  .venv-mqt/bin/python scripts/generate_ising_circuits.py --sizes 5 10 20 ...

Examples:
  # the sizes used for the WISQ scaling study
  .venv-mqt/bin/python scripts/generate_ising_circuits.py \
      --sizes 5 10 20 30 40 50 60 70 80 90 100 125 150 175 200 300 400

  # a deeper circuit (more Trotter steps)
  .venv-mqt/bin/python scripts/generate_ising_circuits.py --sizes 50 100 --reps 3
"""

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "qasms"

# Same basis as generate_mqt_circuits.py: 2-qubit interactions become cx, magic
# gates t/tdg, every other single-qubit rotation collapses into u.
TARGET_BASIS = ["cx", "u", "t", "tdg"]

DEFAULT_SIZES = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 125, 150, 175, 200, 300, 400]

# Trotter angles. Arbitrary and irrelevant to routing (the parser ignores rz/rx/h);
# kept generic so the circuit is a faithful TFIM rather than a degenerate one.
J_DT = 0.5    # ZZ coupling * timestep
HX_DT = 1.0   # transverse field * timestep


def build_tfim(n: int, reps: int):
    """1-D nearest-neighbour TFIM Trotter circuit on n qubits, `reps` steps."""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n)
    qc.h(range(n))  # initial layer of Hadamards (matches existing ising files)
    for _ in range(reps):
        # RZZ on chain bonds, even bonds then odd bonds (brick pattern). Each
        # RZZ transpiles to cx-rz-cx, so this is exactly the chain cx structure.
        for i in range(0, n - 1, 2):
            qc.rzz(2.0 * J_DT, i, i + 1)
        for i in range(1, n - 1, 2):
            qc.rzz(2.0 * J_DT, i, i + 1)
        # Transverse field
        for q in range(n):
            qc.rx(2.0 * HX_DT, q)
    return qc


def strip_measurements(qasm: str) -> str:
    """Remove measure/barrier/creg lines (the compiler ignores them)."""
    kept = []
    for line in qasm.splitlines():
        s = line.strip()
        if s.startswith("measure") or s.startswith("barrier") or s.startswith("creg"):
            continue
        kept.append(line)
    return "\n".join(kept) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--sizes", nargs="*", type=int, default=DEFAULT_SIZES,
                        help=f"Qubit counts (default: {DEFAULT_SIZES})")
    parser.add_argument("--reps", type=int, default=1,
                        help="Number of Trotter steps (default: 1, matching existing ising_n*)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"Output dir (default: {DEFAULT_OUT})")
    parser.add_argument("--opt-level", type=int, default=1,
                        help="Qiskit transpile optimization level (default: 1)")
    parser.add_argument("--keep-measure", action="store_true",
                        help="Keep measurement/barrier lines (default: stripped)")
    args = parser.parse_args()

    try:
        from qiskit import transpile
        from qiskit.qasm2 import dumps
    except ImportError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Run with the venv python: .venv-mqt/bin/python scripts/generate_ising_circuits.py",
              file=sys.stderr)
        sys.exit(1)

    if args.reps < 1:
        print("ERROR: --reps must be >= 1", file=sys.stderr)
        sys.exit(1)

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Output dir : {args.out}")
    print(f"Basis      : {TARGET_BASIS}")
    print(f"Reps       : {args.reps}")
    print(f"Sizes      : {args.sizes}\n")

    ok, failed = 0, 0
    for n in args.sizes:
        label = f"ising_n{n}"
        try:
            if n < 2:
                print(f"  SKIP {label}: need >= 2 qubits for a chain bond")
                failed += 1
                continue
            qc = build_tfim(n, args.reps)
            qc = transpile(qc, basis_gates=TARGET_BASIS, optimization_level=args.opt_level)
            qasm = dumps(qc)
            if not args.keep_measure:
                qasm = strip_measurements(qasm)

            counts = Counter(re.findall(r"^([a-z]+)", qasm, re.M))
            ncx = counts.get("cx", 0)
            if ncx == 0:
                print(f"  SKIP {label}: 0 CNOT after transpile")
                failed += 1
                continue

            out_path = args.out / f"{label}.qasm"
            out_path.write_text(qasm)
            print(f"  OK   {label:14} cx={ncx:6}  t={counts.get('t',0)+counts.get('tdg',0):5}")
            ok += 1
        except Exception as e:
            print(f"  FAIL {label}: {e}")
            failed += 1

    print(f"\nDone: {ok} generated, {failed} failed/skipped.")


if __name__ == "__main__":
    main()
