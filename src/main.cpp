#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"
#include "maxHeap.hpp"
#include "mapping.hpp"
#include "routing.hpp"

#include <iostream>
#include <filesystem>

using namespace std;

int main(int argc, char **argv) {
    std::string path = "../qasms/example.qasm";
    if (argc > 1) {
        std::filesystem::path root(PROJECT_ROOT);        
        path = (root / "qasms" / (std::string(argv[1]) + ".qasm")).string();
    }
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

    circuit.print_qubit_heap();

    circuit.write_qasm_file("universal_set_qasms/semplified.qasm");

    std::cout << "------- MAPPING ---------" << std::endl;

    int x = 10, y = 11;

    Graph graph = Graph::create_rectangular_with_magic_states(x, y);

    graph.print_rectangular();

    FarthestFromMagicSelector farthest_from_magic_selector(graph);

    Mapping mapping(circuit, graph);

    int T_lower_bound = 2;
    int T_upper_bound = 5;
    int maximum_iterations = 100;
    mapping.magic_aware_mapping(T_lower_bound, T_upper_bound, maximum_iterations, farthest_from_magic_selector);

    //mapping.homogenous_mapping_rowmajor(x, y);

    graph.print_rectangular();


    std::cout << "------- LAYERING ---------" << std::endl;
    circuit::LayeredCircuit layeredCircuit = circuit::LayeredCircuit(circuit);
    layeredCircuit.print_layered();

    std::cout << "------- ROUTING ---------" << std::endl;
    NaiveShortestPath pathStrat(graph);
    QubitRouter router(mapping, layeredCircuit, graph, &pathStrat);
    router.route_circuit();
    
    std::cout << "-------- FINAL ROUTING RESULT -------------" << std::endl;
    router.print_routing_steps();
    graph.print_rectangular();

    return 0;
}







    //maxHeap testing
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
