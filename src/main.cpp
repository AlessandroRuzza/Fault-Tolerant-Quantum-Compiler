#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"
#include "maxHeap.hpp"
#include "mapping.hpp"
#include "routing.hpp"
#include "defines.hpp"
#include "parsing.hpp"

#include <filesystem>
#include <iostream>

using namespace std;

int main(int argc, char **argv) {

    std::string path = "../qasms/example.qasm";
    std::string strategy = "distance_first";
    std::string type = "magic_aware";
    std::string config_path = "../config/compiler_config.json";

    apply_config_overrides(argc, argv, path, strategy, type, config_path);
    argument_parsing(argc, argv, path, strategy, type);

    std::cout << "path: " << path << std::endl;
    std::cout << "strategy: " << strategy << std::endl;
    std::cout << "type: " << type << std::endl;

    circuit::Circuit circuit = circuit::Circuit();

    try {
        circuit.parse_qasm_file(path);
        auto gates = circuit.getGates();
        for (size_t i = 0; i < gates.size(); ++i) {
            const auto &g = gates[i];
            if (PRINT_PARSING) std::cout << g.id << ": " << g.to_string() << "\n";
        }
    } catch (const std::exception &e) {
        std::cerr << "error: " << e.what() << std::endl;
        return 2;
    }

    if (PRINT_CIRCUIT) circuit.print_qubit_heap();

    std::filesystem::path original_name = std::filesystem::path(path).stem();
    std::string output_path = "universal_set_qasms/" + original_name.string() + "_universal.qasm";
    circuit.write_qasm_file(output_path);

    std::cout << "------- MAPPING ---------" << std::endl;

    int x = 4, y = 4;
    int maximum_iterations = 100;

    Graph graph = Graph::create_rectangular_with_magic_states(x, y);

    if (PRINT_MAPPING) graph.print_rectangular();

    Mapping mapping(circuit, graph, strategy, type, maximum_iterations);

    mapping.map();

    graph.print_rectangular();

    std::cout << "------- LAYERING ---------" << std::endl;
    circuit::LayeredCircuit layeredCircuit = circuit::LayeredCircuit(circuit);
    if (PRINT_LAYER) layeredCircuit.print_layered();

    std::cout << "------- ROUTING ---------" << std::endl;
    NaiveShortestPath pathStrat(graph);
    QubitRouter router(mapping, layeredCircuit, graph, &pathStrat);
    router.route_circuit();

    std::cout << "-------- FINAL ROUTING RESULT -------------" << std::endl;
    if (PRINT_ROUTING) router.print_routing_steps();
    std::cout << "\nTotal routing steps: " << router.get_routing_length() << "\n\n";

    return 0;
}

// maxHeap testing
//std::cout << "------- HEAP TEST ---------" << std::endl;

/* /* MaxHeap<int*> maxHeap(6);

int value = 10;
maxHeap.insert(&value);
maxHeap.print();
value = 10;
maxHeap.insert(&value);
maxHeap.print();
value = 15;
maxHeap.insert(&value);
value = 20;
maxHeap.insert(&value);
value = 5;
maxHeap.insert(&value);
// Build the heap from the array
//maxHeap.buildHeap();

// Print the max heap
maxHeap.print(); */

// Get the maximum value from the max heap
// cout << "Top value: " << maxHeap.top() << endl;

// Delete the root node of the max heap
// cout << "Popped value: " << maxHeap.pop() << endl;
// cout << "After popping: ";
// maxHeap.print();

// ----maxheap testing end----
//
