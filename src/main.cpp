#include "qasm.hpp"
#include "graph.hpp"

#include <iostream>

int main(int argc, char **argv) {

    const char *path = "../example.qasm";
    if (argc > 1) path = argv[1];
    try {
        qasm::Circuit circuit = qasm::Circuit();
        circuit.parse_qasm_file(path);
        auto gates = circuit.getGates();
        for (size_t i = 0; i < gates.size(); ++i) {
            const auto &g = gates[i];
            std::cout << i << ": " << g.name << " ";
            for (size_t j = 0; j < g.qubits.size(); ++j) {
                if (j) std::cout << ",";
                std::cout << g.qubits[j];
            }
            std::cout << "\n";
        }
    } catch (const std::exception &e) {
        std::cerr << "error: " << e.what() << std::endl;
        return 2;
    }


    Graph g = Graph::from_json("../graph_description_rectangular.json");
    //g.print();


    return 0;
}
