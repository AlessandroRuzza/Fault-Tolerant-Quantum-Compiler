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
    std::string path = "../qasms/qft_20.qasm";
    const auto print_usage = [&](const char* executable) {
        std::cout << "Usage: " << executable
                  << " --circuit [circuit_name|circuit_name.qasm|full_path_to_qasm] "
                  << "[--strategy [" << Mapping::available_mapping_strategies() << "]]\n"
                  << "   or: " << executable << " --help\n";
    };

    const auto resolve_circuit_path = [&](const std::string& circuit_arg) {
        std::filesystem::path candidate(circuit_arg);

        if (!candidate.has_extension()) {
            candidate += ".qasm";
        }

        if (!candidate.has_parent_path() && !candidate.is_absolute()) {
            std::filesystem::path root(PROJECT_ROOT);
            candidate = root / "qasms" / candidate;
        }

        return candidate.string();
    };

    if (argc > 1) {
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--help") {
                print_usage(argv[0]);
                return 0;
            }

            if (arg == "--circuit") {
                if (i + 1 >= argc) {
                    std::cerr << "Missing value for --circuit\n";
                    print_usage(argv[0]);
                    return 1;
                }
                path = resolve_circuit_path(argv[++i]);
                continue;
            }

            if (arg == "--strategy") {
                if (i + 1 >= argc) {
                    std::cerr << "Missing value for --strategy\n";
                    print_usage(argv[0]);
                    return 1;
                }

                const std::string strategy_name = argv[++i];
                if (!Mapping::set_mapping_strategy(strategy_name)) {
                    std::cerr << "Invalid mapping strategy '" << strategy_name
                              << "'. Use one of ["
                              << Mapping::available_mapping_strategies() << "]\n";
                    return 1;
                }

                std::cout << "Using "
                          << Mapping::current_mapping_strategy_name()
                          << " mapping strategy\n";
                continue;
            }

            std::cerr << "Unknown option '" << arg << "'\n";
            print_usage(argv[0]);
            return 1;
        }
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

    std::filesystem::path original_name = std::filesystem::path(path).stem();
    std::string output_path = "universal_set_qasms/" + original_name.string() + "_universal.qasm";
    circuit.write_qasm_file(output_path);

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
