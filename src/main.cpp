#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"
#include "maxHeap.hpp"
#include "mapping.hpp"
#include "routing.hpp"
#include "defines.hpp"

#include <iostream>
#include <filesystem>

using namespace std;




void argument_parsing(int argc, char **argv, std::string& path, std::string& strategy, std::string& type); 


int main(int argc, char **argv) {

    std::string path = "../qasms/example.qasm";
    std::string strategy = "distance_first";
    std::string type = "magic_aware";

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



void argument_parsing(int argc, char **argv, std::string& path, std::string& strategy, std::string& type) {
    const auto print_usage = [&](const char* executable) {
        std::cout << "Usage: " << executable
                  << " --circuit [circuit_name|circuit_name.qasm|full_path_to_qasm] "
                  << "[--strategy [" << Mapping::available_mapping_strategies() << "]]\n"
                  << "[--type [" << Mapping::available_mapping_types() << "]]\n"
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

        path = candidate.string();
    };

    if (argc > 1) {
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--help") {
                print_usage(argv[0]);
                exit(0);
            }

            if (arg == "--circuit") {
                if (i + 1 >= argc) {
                    std::cerr << "Missing value for --circuit\n";
                    print_usage(argv[0]);
                    throw std::runtime_error("Missing value for --circuit");
                }
                resolve_circuit_path(argv[++i]);
                continue;
            }

            if (arg == "--strategy") {
                if (i + 1 >= argc) {
                    std::cerr << "Missing value for --strategy\n";
                    print_usage(argv[0]);
                    throw std::runtime_error("Missing value for --strategy");
                }

                strategy = argv[++i];
                const std::vector<std::string> valid_strategies = Mapping::get_available_mapping_strategies();
                if (std::find(valid_strategies.begin(), valid_strategies.end(), strategy) == valid_strategies.end()) {
                    std::cerr << "Invalid mapping strategy: " << strategy << "\n";
                    print_usage(argv[0]);
                    throw std::runtime_error("Invalid mapping strategy: " + strategy);
                }
                continue;


            }

            if (arg == "--type") {
                if (i + 1 >= argc) {
                    std::cerr << "Missing value for --type\n";
                    print_usage(argv[0]);
                    throw std::runtime_error("Missing value for --type");
                }
                type = argv[++i];
                const std::vector<std::string> valid_types = Mapping::get_available_mapping_types();
                if (std::find(valid_types.begin(), valid_types.end(), type) == valid_types.end()) {
                    std::cerr << "Invalid mapping type: " << type << "\n";
                    print_usage(argv[0]);
                    throw std::runtime_error("Invalid mapping type: " + type);
                }
                continue;

            }

            std::cerr << "Unknown option '" << arg << "'\n";
            print_usage(argv[0]);
            throw std::runtime_error("Unknown option: " + arg);
        }
    }
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
