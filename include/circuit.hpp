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
#include <unordered_map>
#include "maxHeap.hpp"

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

struct Qubit {
    int qubit_id;
    int T_count;

    //to replace with heap
    std::vector<int> CNOT_count;

    Qubit(int id, int c, const std::vector<int>& q) : qubit_id(id), T_count(c), CNOT_count(q) {}

    //to replace with heap
    int max_cnot_count() const {
        int max_count = 0;
        for (int count : CNOT_count) {
            if (count > max_count) {
                max_count = count;
            }
        }
        return max_count;
    }
};


class Circuit {
protected:
    std::vector<Gate> gates; 
    MaxHeap<Qubit> qubits;
    //maps qubit index to index in the heap
    std::vector<int> qubit_heap_indices;

public:

    Circuit () = default;

    Circuit(int num_qubits) {
        qubits = MaxHeap<Qubit>(num_qubits);
        initializeQubitHeapIndices(num_qubits);
    }

    //------------getters--------------


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


    inline int getTCount(int qubit_index) const {
        return qubits.getElementAt(getQubitHeapIndex(qubit_index)).T_count;
    }

    inline int getCNOTCount(int qubit1, int qubit2) const {
        return qubits.getElementAt(getQubitHeapIndex(qubit1)).CNOT_count[getQubitHeapIndex(qubit2)];
    }


    inline int getQubitHeapIndex(int qubit_index) const {
        return qubit_heap_indices[qubit_index];
    }



    //------------initializers/setters--------------


    inline void initializeQubitHeapIndices(int num_qubits) {
        qubit_heap_indices.clear();
        qubit_heap_indices.resize(num_qubits, -1);
    }


    inline void setQubitHeapIndex(int qubit_index, int heap_index) {
        qubit_heap_indices[qubit_index] = heap_index;
    }



    //----------incrementers----------

    inline void incrementTCount(int qubit_index) {

        qubits.getElementAt(getQubitHeapIndex(qubit_index)).T_count++;
    }

    inline void incrementCNOTCount(int control_qubit, int target_qubit) {
        qubits.getElementAt(getQubitHeapIndex(control_qubit)).CNOT_count[getQubitHeapIndex(target_qubit)]++;
        qubits.getElementAt(getQubitHeapIndex(target_qubit)).CNOT_count[getQubitHeapIndex(control_qubit)]++;
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