OPENQASM 2.0;
include "qelib1.inc";

// Allocate 20 quantum bits and 20 classical bits
qreg q[20];
creg c[20];

// ==========================================
// BLOCK 1: Initialization & First Entanglement
// ==========================================
// LAYER 1: Full Superposition (20 parallel operations)
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
h q[5];
h q[6];
h q[7];
h q[8];
h q[9];
h q[10];
h q[11];
h q[12];
h q[13];
h q[14];
h q[15];
h q[16];
h q[17];
h q[18];
h q[19];
barrier q;

// LAYER 2: Even-Odd Entanglement (10 parallel two-qubit operations)
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];
cx q[8], q[9];
cx q[10], q[11];
cx q[12], q[13];
cx q[14], q[15];
cx q[16], q[17];
cx q[18], q[19];
barrier q;

// LAYER 3: Parallel S and X gates
s q[0];
x q[1];
s q[2];
x q[3];
s q[4];
x q[5];
s q[6];
x q[7];
s q[8];
x q[9];
s q[10];
x q[11];
s q[12];
x q[13];
s q[14];
x q[15];
s q[16];
x q[17];
s q[18];
x q[19];
barrier q;

// LAYER 4: Odd-Even Entanglement (9 parallel operations, q[0] and q[19] idle)
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];
cx q[7], q[8];
cx q[9], q[10];
cx q[11], q[12];
cx q[13], q[14];
cx q[15], q[16];
cx q[17], q[18];
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
y q[8];
z q[9];
y q[10];
z q[11];
y q[12];
z q[13];
y q[14];
z q[15];
y q[16];
z q[17];
y q[18];
z q[19];
barrier q;

// LAYER 6: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];
cx q[8], q[9];
cx q[10], q[11];
cx q[12], q[13];
cx q[14], q[15];
cx q[16], q[17];
cx q[18], q[19];
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
h q[8];
h q[9];
h q[10];
h q[11];
h q[12];
h q[13];
h q[14];
h q[15];
h q[16];
h q[17];
h q[18];
h q[19];
barrier q;

// LAYER 8: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];
cx q[7], q[8];
cx q[9], q[10];
cx q[11], q[12];
cx q[13], q[14];
cx q[15], q[16];
cx q[17], q[18];
barrier q;

// ==========================================
// BLOCK 3: Asymmetric Single-Qubit Parallelism
// ==========================================
// LAYER 9: Mixed Single-Qubit Gates
x q[0];
y q[1];
z q[2];
s q[3];
h q[4];
x q[5];
y q[6];
z q[7];
s q[8];
h q[9];
x q[10];
y q[11];
z q[12];
s q[13];
h q[14];
x q[15];
y q[16];
z q[17];
s q[18];
h q[19];
barrier q;

// LAYER 10: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];
cx q[8], q[9];
cx q[10], q[11];
cx q[12], q[13];
cx q[14], q[15];
cx q[16], q[17];
cx q[18], q[19];
barrier q;

// LAYER 11: Inverted Mixed Gates
h q[0];
s q[1];
z q[2];
y q[3];
x q[4];
h q[5];
s q[6];
z q[7];
y q[8];
x q[9];
h q[10];
s q[11];
z q[12];
y q[13];
x q[14];
h q[15];
s q[16];
z q[17];
y q[18];
x q[19];
barrier q;

// LAYER 12: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];
cx q[7], q[8];
cx q[9], q[10];
cx q[11], q[12];
cx q[13], q[14];
cx q[15], q[16];
cx q[17], q[18];
barrier q;

// ==========================================
// BLOCK 4: Final Phase Scrubbing & Readout Prep
// ==========================================
// LAYER 13: Full Pauli-X Flip (Global bit-flip)
x q[0];
x q[1];
x q[2];
x q[3];
x q[4];
x q[5];
x q[6];
x q[7];
x q[8];
x q[9];
x q[10];
x q[11];
x q[12];
x q[13];
x q[14];
x q[15];
x q[16];
x q[17];
x q[18];
x q[19];
barrier q;

// LAYER 14: Even-Odd Entanglement
cx q[0], q[1];
cx q[2], q[3];
cx q[4], q[5];
cx q[6], q[7];
cx q[8], q[9];
cx q[10], q[11];
cx q[12], q[13];
cx q[14], q[15];
cx q[16], q[17];
cx q[18], q[19];
barrier q;

// LAYER 15: Final Global Phase Adjustment
s q[0];
s q[1];
s q[2];
s q[3];
s q[4];
s q[5];
s q[6];
s q[7];
s q[8];
s q[9];
s q[10];
s q[11];
s q[12];
s q[13];
s q[14];
s q[15];
s q[16];
s q[17];
s q[18];
s q[19];
barrier q;

// LAYER 16: Odd-Even Entanglement
cx q[1], q[2];
cx q[3], q[4];
cx q[5], q[6];
cx q[7], q[8];
cx q[9], q[10];
cx q[11], q[12];
cx q[13], q[14];
cx q[15], q[16];
cx q[17], q[18];
barrier q;

// ==========================================
// LAYER 17: Parallel Measurement (20 operations)
// ==========================================
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
measure q[7] -> c[7];
measure q[8] -> c[8];
measure q[9] -> c[9];
measure q[10] -> c[10];
measure q[11] -> c[11];
measure q[12] -> c[12];
measure q[13] -> c[13];
measure q[14] -> c[14];
measure q[15] -> c[15];
measure q[16] -> c[16];
measure q[17] -> c[17];
measure q[18] -> c[18];
measure q[19] -> c[19];