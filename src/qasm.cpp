#include "qasm.hpp"

namespace qasm {

static std::string trim(const std::string &s) {
    size_t a = s.find_first_not_of(" \t\r\n");
    if (a == std::string::npos) return "";
    size_t b = s.find_last_not_of(" \t\r\n");
    return s.substr(a, b - a + 1);
}

std::vector<Gate> parse_qasm_file(const std::string &path) {
    std::ifstream ifs(path);
    if (!ifs) throw std::runtime_error("failed to open file: " + path);

    std::vector<Gate> gates;
    std::string line;

    // regex to match gate lines like: name q[0];  or cx q[0],q[1];
    // capture gate name and the rest of the operands
    std::regex gate_re(R"(^\s*([a-zA-Z]+)\s+([^;]+);)" );
    std::regex qubit_re(R"((?:([a-zA-Z_]\w*)\s*\[\s*(\d+)\s*\]))");

    while (std::getline(ifs, line)) {
        auto s = trim(line);
        if (s.empty()) continue;
        // skip OpenQASM header and include lines and comments
        if (s.rfind("//", 0) == 0) continue;
        if (s.rfind("OPENQASM", 0) == 0) continue;
        if (s.rfind("include", 0) == 0) continue;
        if (s.rfind("qreg", 0) == 0) continue;
        if (s.rfind("creg", 0) == 0) continue;

        std::smatch m;
        if (std::regex_search(s, m, gate_re)) {
            Gate g;
            g.name = m[1].str();
            std::string operands = m[2].str();

            // find all qubit occurrences in operands
            auto begin = std::sregex_iterator(operands.begin(), operands.end(), qubit_re);
            auto end = std::sregex_iterator();
            for (auto it = begin; it != end; ++it) {
                std::smatch qm = *it;
                // qm[1] is register name (ignored for now), qm[2] is index
                unsigned idx = static_cast<unsigned>(std::stoul(qm[2].str()));
                g.qubits.push_back(idx);
            }

            // If no explicit q[...] matches (e.g., operations on single implicit qubit), try to parse comma-separated ints
            if (g.qubits.empty()) {
                // attempt to parse numbers in operands
                std::regex num_re(R"((\d+))");
                auto nb = std::sregex_iterator(operands.begin(), operands.end(), num_re);
                for (auto it = nb; it != end; ++it) {
                    g.qubits.push_back(static_cast<unsigned>(std::stoul((*it)[1].str())));
                }
            }

            // Translate certain gates into sequences when reading QASM:
            // - "tdg" is translated into seven consecutive "t" gates on the same qubit(s).
            // - "x" is translated into the sequence: h t t t t h applied to the same qubit(s).
            {
                std::string lname = g.name;
                for (char &c : lname) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));

                if (lname == "tdg") {
                    for (int i = 0; i < 7; ++i) {
                        Gate tg;
                        tg.name = "t";
                        tg.qubits = g.qubits;
                        gates.push_back(std::move(tg));
                    }
                } else if (lname == "x") {
                    Gate h1; h1.name = "h"; h1.qubits = g.qubits; gates.push_back(h1);
                    for (int i = 0; i < 4; ++i) {
                        Gate tg; tg.name = "t"; tg.qubits = g.qubits; gates.push_back(tg);
                    }
                    Gate h2; h2.name = "h"; h2.qubits = g.qubits; gates.push_back(h2);
                } else if (lname == "z") {
                    for (int i = 0; i < 4; ++i) {
                        Gate tg; tg.name = "t"; tg.qubits = g.qubits; gates.push_back(tg);
                    }
                } else if (lname == "y") {
                    Gate h1; h1.name = "h"; h1.qubits = g.qubits; gates.push_back(h1);
                    for (int i = 0; i < 4; ++i) {
                        Gate tg; tg.name = "t"; tg.qubits = g.qubits; gates.push_back(tg);
                    }
                    Gate h2; h2.name = "h"; h2.qubits = g.qubits; gates.push_back(h2);
                    for (int i = 0; i < 4; ++i) {
                        Gate tg; tg.name = "t"; tg.qubits = g.qubits; gates.push_back(tg);
                    }
                } else {
                    gates.push_back(std::move(g));
                }
            }
        }
        // otherwise ignore unknown lines
    }

    return gates;
}

} // namespace qasm