#!/usr/bin/env python3
"""Run WISQ's converter with two upstream crashes guarded.

`wisq --mode opt --target_gateset CLIFFORDT` divides the approximation budget
over the circuit's `rz` gates:

    approximation_per_angle = approximation_epsilon / (num_rz * ERROR_BUDGET)

so a circuit that holds **no rotation at all** — every QASMBench circuit whose
gates are already Clifford, e.g. `cat_state_n4` — dies with ZeroDivisionError
before it writes anything. Such a circuit needs no rotation synthesis: the
translation into Clifford+T is the basis translation alone.

The second guard is for `--opt_timeout 0` (pure conversion, no GUOQ): upstream
then does `shutil.move(transpiled_path, output_path)`, and when the circuit
needed no transpilation at all `transpiled_path` **is the input file**, so the
move would carry the source circuit out of QASMBench. Handing back a copy in
the scratch directory keeps the input where it is.

Nothing else changes: circuits with rotations take exactly the upstream path
(same BasisTranslator, same QualtranRS, same epsilon per angle).

Usage — same arguments as `wisq`:

    python3 scripts/wisq_zero_rz_shim.py circuit.qasm --mode opt ...
"""

from __future__ import annotations

import os
import shutil
import sys
from time import time_ns


def install_patch() -> None:
    import wisq.guoq as guoq

    def transpile_if_needed(input_path, target_gateset, scratch_dir,
                            approximation_epsilon=0):
        circuit = guoq.QuantumCircuit.from_qasm_file(input_path)

        gates = set(circuit.count_ops().keys())
        if all(gate in guoq.GATE_SETS[target_gateset] for gate in gates):
            # Upstream returns input_path here; hand back a copy so a later
            # shutil.move cannot consume the source circuit.
            copied = os.path.join(
                scratch_dir, f"asis_{time_ns()}_" + os.path.basename(input_path)
            )
            shutil.copyfile(input_path, copied)
            return (0, copied)

        approximation = 0
        if target_gateset == guoq.CLIFFORDT:
            pm = guoq.PassManager([
                guoq.BasisTranslator(equivalence_library=guoq.sel,
                                     target_basis=guoq.GATE_SETS["NAM"])
            ])
            nam_circuit = pm.run(circuit)
            num_rz = nam_circuit.count_ops().get("rz", 0)

            if num_rz == 0:
                # No angle to approximate: NAM minus rz is {h, x, cx}, already
                # inside Clifford+T. No epsilon is spent, hence approximation 0.
                transpiled = nam_circuit
            else:
                approximation_per_angle = (
                    approximation_epsilon / (num_rz * guoq.ERROR_BUDGET)
                )
                approximation = approximation_epsilon / guoq.ERROR_BUDGET
                transpiled = guoq.PassManager(
                    [guoq.QualtranRS(approximation_per_angle)]
                ).run(nam_circuit)
        else:
            transpiled = guoq.PassManager([
                guoq.BasisTranslator(equivalence_library=guoq.sel,
                                     target_basis=guoq.GATE_SETS[target_gateset])
            ]).run(circuit)

        output_path = os.path.join(
            scratch_dir, f"transpiled_{time_ns()}_" + os.path.basename(input_path)
        )
        guoq.qasm2.dump(transpiled, output_path)
        return (approximation, output_path)

    guoq.transpile_if_needed = transpile_if_needed


def main() -> int:
    install_patch()
    import wisq

    sys.argv[0] = "wisq"
    return wisq.main() or 0


if __name__ == "__main__":
    sys.exit(main())
