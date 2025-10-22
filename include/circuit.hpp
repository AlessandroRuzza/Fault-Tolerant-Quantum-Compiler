#ifndef CIRCUIT_HPP
#define CIRCUIT_HPP

#include <string>
#include <vector>
#include <cstdint>
#include <fstream>
#include <sstream>
#include <iostream>
#include <regex>
#include <cctype>
#include <stdexcept>

namespace circuit {

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

struct gate_count {
    std::string name;
    int count;
};

class Circuit {
protected:
    std::vector<Gate> gates; 

public:
    Circuit() {}
    Circuit(const Circuit& c) : gates(c.gates) {}

    inline const std::vector<Gate>& getGates() const { return gates; }

    inline const int getNumQubits() const {
        int max_qubit = -1;
        for (const Gate& gate : gates) {
            for (const int q : gate.qubits) {
                if (q > max_qubit) {
                    max_qubit = q;
                }
            }
        }
        return max_qubit + 1; // qubits are zero-indexed
    }

    inline const int getNumGates() const {
        return static_cast<int>(gates.size());
    }

    inline const std::unordered_map<std::string, int> getAllGatesCount() const {
        std::unordered_map<std::string, int> result;
        for (const Gate& gate : gates) {
            result[gate.name]++;
        }
        return result;
    }


    const std::vector<std::vector<gate_count>> getGatesCountPerQubit() const;

    const void printCountPerQubit() const {
        auto counts = getGatesCountPerQubit();
        for (size_t i = 0; i < counts.size(); ++i) {
            std::cout << "Qubit " << i << ":\n";
            for (const auto& gc : counts[i]) {
                std::cout << "  " << gc.name << ": " << gc.count << "\n";
            }
        }
    }


    // Parse a QASM file and return a vector of gates.
    // Throws std::runtime_error on I/O errors.
    void parse_qasm_file(const std::string &path);

    // Scrive il circuito su file in formato OPENQASM 2.0 (semplice)
    void write_qasm_file(const std::string& path) const;
};
} // namespace circuit

namespace std {
template<>
struct hash<circuit::Gate> {
    std::size_t operator()(const circuit::Gate& g) const {
        hash<int> hi = hash<int>();
        hash<std::string> hs = hash<std::string>();
        // Combine hashes of all relevant members
        return hi(g.id) + hs(g.name);
    }
};
}

#endif // CIRCUIT_HPP