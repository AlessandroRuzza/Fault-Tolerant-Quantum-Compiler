#pragma once

#include <string>
#include <vector>
#include <cstdint>

namespace qasm {

struct Gate {
    std::string name; // gate name, e.g. "cx", "h", "t"
    std::vector<uint32_t> qubits; // targets/controls in textual order
};

// Parse a QASM file and return a vector of gates.
// Throws std::runtime_error on I/O errors.
std::vector<Gate> parse_qasm_file(const std::string &path);

} // namespace qasm
