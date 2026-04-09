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
#include <unordered_set>

using namespace std;

namespace {
void clear_visualization_outputs() {
    namespace fs = std::filesystem;

    const fs::path visualization_dir = fs::path(PROJECT_ROOT) / "visualization";
    fs::create_directories(visualization_dir);

    const std::unordered_set<std::string> keep_entries = {
        "README.md",
        "graph_viewer.cpp"
    };

    for (const auto& entry : fs::directory_iterator(visualization_dir)) {
        const std::string name = entry.path().filename().string();
        if (keep_entries.find(name) != keep_entries.end()) {
            continue;
        }

        std::error_code ec;
        fs::remove_all(entry.path(), ec);
        if (ec) {
            std::cerr << "Warning: failed to remove visualization output "
                      << entry.path() << ": " << ec.message() << "\n";
        }
    }
}
} // namespace

int main(int argc, char **argv) {

    std::string path = "../qasms/example.qasm";
    std::string strategy = "distance";
    std::string type = "magic_aware";
    std::string safe_passage_strategy = "passage";
    std::string config_path = "../config/compiler_config.json";
    std::string graph_path = "";
    int x = 10;
    int y = 11;
    int maximum_iterations = 100;

    apply_config_overrides(argc, argv, path, strategy, type, safe_passage_strategy, config_path, x, y, graph_path);
    argument_parsing(argc, argv, path, strategy, type, safe_passage_strategy, x, y, graph_path);

    std::cout << "circuit path: " << path << std::endl;
    std::cout << "strategy: " << strategy << std::endl;
    std::cout << "type: " << type << std::endl;
    std::cout << "safe passage strategy: " << safe_passage_strategy << std::endl;
    if (!graph_path.empty()) {
        std::cout << "graph path: " << graph_path << std::endl;
    } else {
        std::cout << "graph dimensions: " << x << "x" << y << std::endl;
    }

    clear_visualization_outputs();

    Graph graph;

    if (graph_path.empty()) {
        std::cout << "Creating rectangular graph with dimensions " << x << "x" << y << "...\n";
        graph = Graph::create_rectangular_with_magic_states(y, x);
    } else {
        std::cout << "Loading graph from " << graph_path << "...\n";
        graph = Graph::from_json(graph_path);
    }

    Circuit circuit = Circuit();

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


    if (PRINT_MAPPING) graph.print_rectangular();

    Mapping mapping(circuit, graph, strategy, type, safe_passage_strategy, maximum_iterations);

    mapping.map();

    graph.print_rectangular();

    std::cout << "------- LAYERING ---------" << std::endl;
    LayeredCircuit layeredCircuit = LayeredCircuit(circuit);
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
