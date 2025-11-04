#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"
#include "maxHeap.hpp"
#include "mapping.hpp"

#include <iostream>

using namespace std;

int main(int argc, char **argv) {
    const char *path = "../qasms/example.qasm";
    if (argc > 1) path = argv[1];
    circuit::Circuit circuit = circuit::Circuit();
    try {
        circuit.parse_qasm_file(path);
        auto gates = circuit.getGates();
        for (size_t i = 0; i < gates.size(); ++i) {
            const auto &g = gates[i];
            //std::cout << g.id << ": " << g.to_string() << "\n";
        }
    } catch (const std::exception &e) {
        std::cerr << "error: " << e.what() << std::endl;
        return 2;
    }

    //circuit.write_qasm_file("universal_set_qasms/semplified.qasm");

    int x = 10, y = 11;

    Graph graph = Graph::create_rectangular_with_magic_states(x, y);

    graph.print_rectangular();

    Mapping mapping(circuit, graph);

    mapping.homogenous_mapping_rowmajor(x, y);

    graph.print_rectangular();
    

    // //maxHeap testing
    // MaxHeap<int> maxHeap(6);
    // vector<int> arr = {2, 3, 4, 5, 10, 15};

    // // Build the heap from the array
    // maxHeap.buildHeap(arr);

    // // Print the max heap
    // maxHeap.print();

    // // Insert a node into the heap
    // maxHeap.insert(9);
    // cout << "After inserting 9: " << endl;
    // maxHeap.print();

    // // Get the maximum value from the max heap
    // cout << "Top value: " << maxHeap.top() << endl;

    // // Delete the root node of the max heap
    // cout << "Popped value: " << maxHeap.pop() << endl;
    // cout << "After popping: ";
    // maxHeap.print();

    // // Delete a specific value from the max heap
    // maxHeap.deleteKey(5);
    // cout << "After deleting the node 5: ";
    // maxHeap.print();

    // //----maxheap testing end----

    

    //Graph g = Graph::from_json("../graph_description_rectangular.json");
    //g.print();

    //std::cout << "------- LAYERING ---------" << std::endl;
    //circuit::LayeredCircuit layeredCircuit = circuit::LayeredCircuit(circuit);
    //layeredCircuit.print_layered();


    return 0;
}


