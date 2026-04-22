OPENQASM 2.0;
include "qelib1.inc";

qreg q[8];
creg c[8];

// ==========================================
// BLOCK 1: Initialization & First Entanglement
// ==========================================
// LAYER 1: Fullsuperposition
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
h q[5];
h q[6];
h q[7];

barrier q;

// LAYER 2: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];

barrier q;

// LAYER 3: Parallels and X gates
s q[0];
x q[1];
s q[2];
x q[3];
s q[4];
x q[5];
s q[6];
x q[7];

barrier q;

// LAYER 4: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];

barrier q;

// ==========================================
// BLOCK 2: Pauli Mixing & Deepening
// ==========================================
// LAYER 5: Parallel Y and Z gates
y q[0];
z q[1];
y q[2];
z q[3];
y q[4];
z q[5];
y q[6];
z q[7];

barrier q;

// LAYER 6: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];

barrier q;

// LAYER 7: Full Basis Change (Hadamards)
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
h q[5];
h q[6];
h q[7];

barrier q;

// LAYER 8: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];

barrier q;

// ==========================================
// BLOCK 3: Asymmetric single-Qubit Parallelism
// ==========================================
// LAYER 9: Mixed single-Qubit Gates
x q[0];
y q[1];
z q[2];
s q[3];
h q[4];
x q[5];
y q[6];
z q[7];

barrier q;

// LAYER 10: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];

barrier q;

// LAYER 11: Inverted Mixed Gates
z q[0];
y q[1];
x q[2];
h q[3];
s q[4];
z q[5];
y q[6];
x q[7];

barrier q;

// LAYER 12: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];

barrier q;

// ==========================================
// BLOCK 4:high-Frequencys-Gatescrubbing
// ==========================================
// LAYER 13:s-Gates andhadamards
s q[0];
s q[1];
h q[2];
h q[3];
s q[4];
s q[5];
h q[6];
h q[7];

barrier q;

// LAYER 14: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];

barrier q;

// LAYER 15: Alternatings and X
x q[0];
s q[1];
x q[2];
s q[3];
x q[4];
s q[5];
x q[6];
s q[7];

barrier q;

// LAYER 16: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];

barrier q;

// ==========================================
// BLOCK 5: Final Mixing & Readout Preparation
// ==========================================
// LAYER 17: Full Pauli-X Flip
x q[0];
x q[1];
x q[2];
x q[3];
x q[4];
x q[5];
x q[6];
x q[7];

barrier q;


// LAYER 18: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];

barrier q;


// LAYER 19: Fullhadamard Change to X-Basis
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
h q[5];
h q[6];
h q[7];

barrier q;


// LAYER 20: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];

barrier q;


// LAYER 21: Final Phase Adjustment
s q[0];
s q[1];
s q[2];
s q[3];
s q[4];
s q[5];
s q[6];
s q[7];

barrier q;


// ==========================================
// LAYER 22: Parallel Measurement
// ==========================================
measure q[0] -> c[0];

measure q[1] -> c[1];

measure q[2] -> c[2];

measure q[3] -> c[3];

measure q[4] -> c[4];

measure q[5] -> c[5];

measure q[6] -> c[6];

measure q[7] -> c[7];
