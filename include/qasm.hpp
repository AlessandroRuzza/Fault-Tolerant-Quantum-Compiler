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
    int id;
    std::string name; // gate name, e.g. "cx", "h", "t"
    std::vector<uint32_t> qubits; // targets/controls in textual order

    std::string to_string() const {
        std::ostringstream oss;
        oss << "(" << name << " ";
        for (size_t j = 0; j < qubits.size(); ++j) {
            if (j) oss << ",";
            oss << qubits[j];
        }
        oss << ")";
        return oss.str();
    }

    bool operator==(const Gate& other) const {
        return id == other.id && name == other.name && qubits == other.qubits;
    }
};

class Circuit {
protected:
    std::vector<Gate> gates; 

public:
    Circuit() {}
    Circuit(const Circuit& c) : gates(c.gates) {}

    const std::vector<Gate>& getGates() const { return gates; }
    
    // Parse a QASM file and return a vector of gates.
    // Throws std::runtime_error on I/O errors.
    void parse_qasm_file(const std::string &path);
};


} // namespace qasm

namespace std {
template<>
struct hash<qasm::Gate> {
    std::size_t operator()(const qasm::Gate& g) const {
        hash<int> hi = hash<int>();
        hash<std::string> hs = hash<std::string>();
        // Combine hashes of all relevant members
        return hi(g.id) + hs(g.name);
    }
};
}

#endif // QASM_HPP