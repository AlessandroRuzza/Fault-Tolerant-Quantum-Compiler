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
#include <cmath>
#include "maxHeap.hpp"
#include "qubit.hpp"
#include "defines.hpp"


namespace circuit {

struct Gate {
    int id;
    std::string name; // gate name, e.g. "cx", "h", "t"
    //vector of qubit indices the gate acts on
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
    MaxHeap<Qubit*> qubitsHeap;

    //maps qubit index to index in the heap
    std::vector<Qubit*> qubitsVector;

public:

    Circuit () = default;

    Circuit(int num_qubits) {
        setupCircuit(num_qubits);
    }

    inline void setupCircuit(int num_qubits) {
        std::cout << "Setting up circuit with " << num_qubits << " qubits." << std::endl;
        qubitsHeap = MaxHeap<Qubit*>(num_qubits);
        qubitsVector = std::vector<Qubit*>(num_qubits, nullptr);
    }

    //------------getters--------------



    const int getNumQubits() const {
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


    const std::unordered_map<std::string, int> getAllGatesCount() const {
        std::unordered_map<std::string, int> result;
        for (const Gate& gate : gates) {
            result[gate.name]++;
        }
        return result;
    }

    inline const int getHeapSize(){
        return qubitsHeap.getSize();
    }


    inline const int getQubitsVectorSize() {
        return qubitsVector.size();
    }

    inline const int getNumGates() const {
        return static_cast<int>(gates.size());
    }

    inline const std::vector<Gate>& getGates() const { return gates; }


    inline const int getTCount(int qubit_index) const {
        if (qubit_index < 0 || static_cast<size_t>(qubit_index) >= qubitsVector.size()) throw std::runtime_error("Invalid qubit index in getTCount");
        return qubitsVector[qubit_index]->getTCount();
    }

    inline const int getCNOTCount(int qubit_index1, int qubit_index2) const {
        if (qubit_index1 < 0 || static_cast<size_t>(qubit_index1) >= qubitsVector.size()) throw std::runtime_error("Invalid qubit1 index in getCNOTCount");
        if (qubit_index2 < 0 || static_cast<size_t>(qubit_index2) >= qubitsVector.size()) throw std::runtime_error("Invalid qubit2 index in getCNOTCount");
        return qubitsVector[qubit_index1]->getCNOTCount(getQubitHeapIndex(qubit_index2));
    }

    
    inline const int getQubitHeapIndex(int qubit_index) const {
        if (qubit_index < 0 || static_cast<size_t>(qubit_index) >= qubitsVector.size()) throw std::runtime_error("Invalid qubit index in getQubitHeapIndex");
        return qubitsVector[qubit_index]->getQubitID();
    }


    inline const Qubit* getQubit(int qubit_index) const {
        if (qubit_index < 0 || static_cast<size_t>(qubit_index) >= qubitsVector.size()) throw std::runtime_error("Invalid qubit index in getQubit");
        return qubitsVector[qubit_index];
    }

    inline Qubit* popFromHeap() {
        return qubitsHeap.pop();
    }

    // Calculate the mean number of T gates per qubit
    inline double getTMean() const {
        if (qubitsVector.empty()) return 0.0;
        
        int sum = 0;
        int count = 0;
        for (const auto* qubit : qubitsVector) {
            if (qubit != nullptr) {
                sum += qubit->getTCount();
                count++;
            }
        }
        return count > 0 ? static_cast<double>(sum) / count : 0.0;
    }

    // Calculate the standard deviation of T gates per qubit
    inline double getTStd() const {
        if (qubitsVector.empty()) return 0.0;
        
        double mean = getTMean();
        double sum_squared_diff = 0.0;
        int count = 0;
        
        for (const auto* qubit : qubitsVector) {
            if (qubit != nullptr) {
                double diff = qubit->getTCount() - mean;
                sum_squared_diff += diff * diff;
                count++;
            }
        }
        return count > 0 ? std::sqrt(sum_squared_diff / count) : 0.0;
    }

    //------------initializers/setters--------------


    inline void setQubitHeapIndex(int qubit_index, Qubit* qubit) {
        qubitsVector[qubit_index] = qubit;

    }


    //----------incrementers----------

    inline void incrementTCount(int qubit_index) {
        const int index = getQubitHeapIndex(qubit_index);
        if (index < 0 || static_cast<size_t>(qubit_index) >= qubitsVector.size()) throw std::runtime_error("Invalid qubit index in incrementTCount");
        qubitsVector[qubit_index]->incrementTCount();
        qubitsHeap.heapify(index);

    }

    inline void incrementCNOTCount(int control_qubit, int target_qubit) {
        const int control_index = getQubitHeapIndex(control_qubit);
        const int target_index = getQubitHeapIndex(target_qubit);
        if (control_index < 0 || target_index < 0) throw std::runtime_error("Invalid qubit index in incrementCNOTCount");
        if (control_index > static_cast<int>(qubitsVector.size()) || target_index > static_cast<int>(qubitsVector.size())) throw std::runtime_error("Invalid qubit index in incrementCNOTCount");
        qubitsVector[control_qubit]->incrementCNOTCount(target_index);
        qubitsVector[target_qubit]->incrementCNOTCount(control_index);
        qubitsHeap.heapify(control_index);
        qubitsHeap.heapify(target_index);
    }


    inline void print_qubit_heap() const{
        qubitsHeap.print();
    };



    // Parse a QASM file and return a vector of gates.
    // Throws std::runtime_error on I/O errors.
    void parse_qasm_file(const std::string &path);

    // Scrive il circuito su file in formato OPENQASM 2.0 (semplice)
    void write_qasm_file(const std::string& path) const;

    void addGate(const Gate& gate, std::string gate_name, int globalID);


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