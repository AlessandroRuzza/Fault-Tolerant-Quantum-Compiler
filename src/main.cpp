#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"

#include <iostream>

int main(int argc, char **argv) {
    const char *path = "../example.qasm";
    if (argc > 1) path = argv[1];
    circuit::Circuit circuit = circuit::Circuit();
    try {
        circuit.parse_qasm_file(path);
        auto gates = circuit.getGates();
        for (size_t i = 0; i < gates.size(); ++i) {
            const auto &g = gates[i];
            std::cout << g.id << ": " << g.to_string() << "\n";
        }
    } catch (const std::exception &e) {
        std::cerr << "error: " << e.what() << std::endl;
        return 2;
    }

    std::cout << "------- LAYERING ---------" << std::endl;
    circuit::LayeredCircuit layeredCircuit = circuit::LayeredCircuit(circuit);
    layeredCircuit.print_layered();

    std::cout << "------- MAPPING ---------" << std::endl;
    std::vector<std::vector<circuit::gate_count>> gatesCount = circuit.getGatesCountPerQubit();
    circuit.printCountPerQubit();
    circuit.write_qasm_file("universal_set_qasms/semplified.qasm");

    //Graph g = Graph::from_json("../graph_description_rectangular.json");
    //g.print();

    return 0;
}
