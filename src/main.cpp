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
    std::string magic_aware_strategy = "distance";
    std::string type = "magic_aware";
    std::string gaussian_strategy = "fine";
    std::string safe_passage_strategy = "passage";
    double magic_high = 1.5;
    double magic_low = 0.5;
    double cnot_high = 1.5;
    double cnot_low = 0.5;
    double mapped_gaussian_weight = 0.8;
    double base_gaussian_weight = 1.0;
    std::string config_path = "../config/compiler_config.json";
    std::string graph_path = "";
    int x = 10;
    int y = 11;
    int maximum_iterations = 100;

    apply_config_overrides(
        argc,
        argv,
        path,
        magic_aware_strategy,
        type,
        gaussian_strategy,
        safe_passage_strategy,
        magic_high,
        magic_low,
        cnot_high,
        cnot_low,
        mapped_gaussian_weight,
        base_gaussian_weight,
        config_path,
        x,
        y,
        graph_path
    );
    argument_parsing(
        argc,
        argv,
        path,
        magic_aware_strategy,
        type,
        gaussian_strategy,
        safe_passage_strategy,
        magic_high,
        magic_low,
        cnot_high,
        cnot_low,
        mapped_gaussian_weight,
        base_gaussian_weight,
        x,
        y,
        graph_path
    );

    std::cout << "circuit path: " << path << std::endl;
    std::cout << "magic aware strategy: " << magic_aware_strategy << std::endl;
    std::cout << "type: " << type << std::endl;
    std::cout << "gaussian strategy: " << gaussian_strategy << std::endl;
    std::cout << "MAGIC_HIGH: " << magic_high << std::endl;
    std::cout << "MAGIC_LOW: " << magic_low << std::endl;
    std::cout << "CNOT_HIGH: " << cnot_high << std::endl;
    std::cout << "CNOT_LOW: " << cnot_low << std::endl;
    std::cout << "MAPPED_GAUSSIAN_WEIGHT: " << mapped_gaussian_weight << std::endl;
    std::cout << "BASE_GAUSSIAN_WEIGHT: " << base_gaussian_weight << std::endl;
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
        graph = Graph::create_rectangular_with_magic_states(y, x, 10, 0.0);
    } else {
        std::cout << "Loading graph from " << graph_path << "...\n";
        graph = Graph::from_json(graph_path);
    }

    if (graph.get_node_count() <= 0) {
        std::cerr << "error: graph is empty or invalid.\n";
        return 2;
    }
    if (graph.get_magic_state_ids().empty()) {
        std::cerr << "error: graph has no magic states.\n";
        return 2;
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

    Mapping mapping(
        circuit,
        graph,
        magic_aware_strategy,
        type,
        gaussian_strategy,
        safe_passage_strategy,
        magic_high,
        magic_low,
        cnot_high,
        cnot_low,
        mapped_gaussian_weight,
        base_gaussian_weight,
        maximum_iterations
    );

    mapping.map();

    for (int qubit = 0; qubit < circuit.getQubitsVectorSize(); ++qubit) {
        if (circuit.getQubit(qubit) == nullptr) {
            continue;
        }
        if (mapping.get_mapped_node(qubit) < 0) {
            throw std::runtime_error(
                "Incomplete mapping: qubit " + std::to_string(qubit) + " was not mapped."
            );
        }
    }

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
