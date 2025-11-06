#include "circuit.hpp"
#include <sstream>

namespace circuit {

static std::string trim(const std::string &s) {
    size_t a = s.find_first_not_of(" \t\r\n");
    if (a == std::string::npos) return "";
    size_t b = s.find_last_not_of(" \t\r\n");
    return s.substr(a, b - a + 1);
}


void Circuit::addGate(const Gate& gate, std::string gate_name, int globalID) {

    for (int j = 0; j < static_cast<int>(gate.qubits.size()); ++j) {
        int index = static_cast<int>(gate.qubits[j]);
        if (qubitsVector[index] == nullptr) {
            // Initialize qubit if not already done
            std::vector<int> cnot_counts(getQubitsVectorSize(), 0);
            Qubit* new_qubit = new Qubit(index, 0, cnot_counts); 
            setQubitHeapIndex(index, new_qubit);
            qubitsHeap.insert(new_qubit);
        }
    }
    if (gate_name == "t") {
        for (int j = 0; j < gate.qubits.size(); ++j) {
            incrementTCount(gate.qubits[j]);
        }
    } else if (gate_name == "cnot" || gate_name == "cx") {
        if (gate.qubits.size() < 2) return; // Invalid CNOT gate
        int control = gate.qubits[0];
        int target = gate.qubits[1];
        incrementCNOTCount(control, target);
    }

    Gate newgate;
    newgate.id = globalID;
    newgate.name = std::move(gate_name);
    newgate.qubits = gate.qubits;

    gates.push_back(std::move(newgate));

    

}




void Circuit::parse_qasm_file(const std::string &path) {
    std::ifstream ifs(path);
    if (!ifs) throw std::runtime_error("failed to open file: " + path);

    std::string line;

    // regex to match gate lines like: name q[0];  or cx q[0],q[1];
    // capture gate name and the rest of the operands
    std::regex gate_re(R"(^\s*([a-zA-Z]+)\s+([^;]+);)" );
    std::regex qubit_re(R"((?:([a-zA-Z_]\w*)\s*\[\s*(\d+)\s*\]))");

    int globalID = 0;
    while (std::getline(ifs, line)) {
        auto s = trim(line);
        
        if (s.empty()) continue;
        // skip OpenQASM header and include lines and comments
        if (s.rfind("//", 0) == 0) continue;
        if (s.rfind("OPENQASM", 0) == 0) continue;
        if (s.rfind("include", 0) == 0) continue;
        if (s.rfind("qreg", 0) == 0) {
            // Extract the number of qubits declared
            std::regex qreg_re(R"(^\s*qreg\s+[a-zA-Z_]\w*\s*\[\s*(\d+)\s*\];)");
            std::smatch m;
            if (std::regex_search(s, m, qreg_re)) {
                int num_qubits = static_cast<int>(std::stoul(m[1].str()));
                setupCircuit(num_qubits);
            }
            continue;
        }
        if (s.rfind("creg", 0) == 0) continue;

        std::smatch m;
        if (std::regex_search(s, m, gate_re)) {
            Gate gate;
            gate.id = globalID++;
            gate.name = m[1].str();
            std::string operands = m[2].str();

            // find all qubit occurrences in operands
            auto begin = std::sregex_iterator(operands.begin(), operands.end(), qubit_re);
            auto end = std::sregex_iterator();
            for (auto it = begin; it != end; ++it) {
                std::smatch qm = *it;
                // qm[1] is register name (ignored for now), qm[2] is index
                unsigned idx = static_cast<unsigned>(std::stoul(qm[2].str()));
                gate.qubits.push_back(idx);
            }

            // If no explicit q[...] matches (e.g., operations on single implicit qubit), try to parse comma-separated ints
            if (gate.qubits.empty()) {
                // attempt to parse numbers in operands
                std::regex num_re(R"((\d+))");
                auto nb = std::sregex_iterator(operands.begin(), operands.end(), num_re);
                for (auto it = nb; it != end; ++it) {
                    gate.qubits.push_back(static_cast<unsigned>(std::stoul((*it)[1].str())));
                }
            }

            // Translate certain gates into sequences when reading QASM:
            // - "tdg" is translated into seven consecutive "t" gates on the same qubit(s).
            // - "x" is translated into the sequence: h t t t t h applied to the same qubit(s).
            {
                std::string lname = gate.name;
                for (char &c : lname) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));

                if (lname == "tdg") {
                    for (int i = 0; i < 7; ++i) {
                        addGate(gate, "t", globalID++);
                    }
                } else if (lname == "x") {
                    addGate(gate, "h", globalID++);
                    for (int i = 0; i < 4; ++i) {
                        addGate(gate, "t", globalID++);
                    }
                    addGate(gate, "h", globalID++);
                } else if (lname == "z") {
                    for (int i = 0; i < 4; ++i) {
                        addGate(gate, "t", globalID++);
                    }
                } else if (lname == "y") {
                    addGate(gate, "h", globalID++);
                    for (int i = 0; i < 4; ++i) {
                        addGate(gate, "t", globalID++);
                    }
                    addGate(gate, "h", globalID++);
                    for (int i = 0; i < 4; ++i) {
                        addGate(gate, "t", globalID++);
                    }
                } else {
                   addGate(gate, gate.name, globalID++);
                }
            }
        }
        // otherwise ignore unknown lines
    }
}

void Circuit::write_qasm_file(const std::string& path) const {
    std::ofstream ofs("../"+path);
    if (!ofs) throw std::runtime_error("failed to open file for writing: " + path);

    // header minimal
    ofs << "OPENQASM 2.0;\n";
    ofs << "include \"qelib1.inc\";\n";

    // determina numero di qubit (max index + 1)
    int maxq = -1;
    for (const Gate& gate : gates) {
        for (int q : gate.qubits) {
            if (q > maxq) maxq = q;
        }
    }
    int nq = (maxq >= 0) ? (maxq + 1) : 0;
    if (nq > 0) ofs << "qreg q[" << nq << "];\n\n";

    // scrivi le istruzioni in ordine
    for (const Gate& gate : gates) {
        // nome gate
        ofs << gate.name;
        // operandi
        if (!gate.qubits.empty()) {
            ofs << " ";
            for (size_t i = 0; i < gate.qubits.size(); ++i) {
                if (i) ofs << ",";
                ofs << "q[" << gate.qubits[i] << "]";
            }
        }
        ofs << ";\n";
    }
    ofs.close();
}

} // namespace circuit