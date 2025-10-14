#ifndef QASM_HPP
#define QASM_HPP

#include <string>
#include <vector>
#include <cstdint>
#include <fstream>
#include <sstream>
#include <iostream>
#include <regex>
#include <cctype>
#include <stdexcept>



namespace qasm {

struct Gate {
    std::string name; // gate name, e.g. "cx", "h", "t"
    std::vector<uint32_t> qubits; // targets/controls in textual order
};

// Parse a QASM file and return a vector of gates.
// Throws std::runtime_error on I/O errors.
std::vector<Gate> parse_qasm_file(const std::string &path);

} // namespace qasm

#endif // QASM_HPP