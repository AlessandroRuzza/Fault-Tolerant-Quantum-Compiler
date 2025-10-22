# utils.py
def create_circuit_from_qasm(qasm_file: str):
    """Load a .qasm file into a QuantumCircuit."""
    # Read small header to detect QASM version
    with open(qasm_file, "r") as f:
        header = f.read(64)

    if "OPENQASM 3" in header:
        # Requires: pip install qiskit-qasm3-import
        import qiskit.qasm3 as qasm3
        return qasm3.load(qasm_file)  # -> QuantumCircuit
    else:
        # QASM 2 (default). qelib1.inc handled via legacy include path.
        import qiskit.qasm2 as qasm2
        return qasm2.load(
            qasm_file,
            include_path=qasm2.LEGACY_INCLUDE_PATH,
            strict=False
        )



def save_circuit_as_png(circuit, filename):
    """Save a QuantumCircuit as a PNG image."""
    circuit.draw(output='mpl', filename=filename)


if __name__ == "__main__":
    qasm_file = "universal_set_qasms/semplified.qasm"
    output_file = "circuit_images/circuit.png"
    circuit = create_circuit_from_qasm(qasm_file)
    save_circuit_as_png(circuit, output_file)
