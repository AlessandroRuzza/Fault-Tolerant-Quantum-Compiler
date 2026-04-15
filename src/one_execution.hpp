#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"
#include "maxHeap.hpp"
#include "mapping.hpp"
#include "routing.hpp"
#include "defines.hpp"

#include <memory>
#include <filesystem>
#include <iostream>
#include <unordered_set>

using namespace std;

struct benchmarkResult {
    int routing_steps = 0;
    double avg_parallelism = 1;
};

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

benchmarkResult one_execution(std::string path, std::string magic_aware_strategy, std::string type, 
    std::string gaussian_strategy, std::string safe_passage_strategy, double magic_high, 
    double magic_low, double cnot_high, double cnot_low, double mapped_gaussian_weight, 
    double base_gaussian_weight, int x, int y, std::string graph_path, 
    std::string magic_state_placement_strategy, int number_of_magic_states, 
    double border_distance_percentage, int maximum_iterations, std::string routing_strategy) {


    const bool use_generated_graph = graph_path.empty();
    
    if (use_generated_graph) {
        std::cout << "Creating rectangular graph with dimensions " << x << "x" << y << "...\n";
    } else {
        std::cout << "Loading graph from " << graph_path << "...\n";
    }

    Graph graph(
        use_generated_graph,
        100,
        number_of_magic_states,
        border_distance_percentage,
        magic_state_placement_strategy,
        x,
        y,
        graph_path
    );

    if (graph.get_node_count() <= 0) {
        std::cerr << "Error: graph is empty or invalid.\n";
        throw std::runtime_error("Error: graph is empty or invalid");
    }
    if (graph.get_magic_state_ids().empty()) {
        std::cerr << "Error: graph has no magic states.\n";
        throw std::runtime_error("Error: graph has no magic states");
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
        std::cerr << "Error: " << e.what() << std::endl;
        throw std::runtime_error("Error parsing QASM file");
    }

    if (PRINT_CIRCUIT) circuit.print_qubit_heap();

    std::filesystem::path original_name = std::filesystem::path(path).stem();
    std::string output_path = "universal_set_qasms/" + original_name.string() + "_universal.qasm";
    circuit.write_qasm_file(output_path);

    std::cout << "------- MAPPING ---------" << std::endl;


    if (PRINT_MAPPING_GRAPH) graph.print_rectangular();

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

    if (PRINT_MAPPING_GRAPH) graph.print_rectangular();

    std::cout << "------- LAYERING ---------" << std::endl;
    LayeredCircuit layeredCircuit = LayeredCircuit(circuit, 2); //Lookahead only 2 layers
    if (PRINT_LAYER) layeredCircuit.print_layered();


    std::cout << "------- ROUTING ---------" << std::endl;
    constexpr float CONGESTION_PENALTY_SCALE = 0.35f;
    constexpr CongestionUpdatePolicy CONGESTION_UPDATE_POLICY = CongestionUpdatePolicy::STATIC_GLOBAL;
    std::unique_ptr<IPathStrategy> pathStrategyPtr;
    if (routing_strategy == "naive") {
        pathStrategyPtr = std::make_unique<NaiveShortestPath>(graph);
    } else { // default to congestion-aware
        pathStrategyPtr = std::make_unique<CongestionAwareShortestPath>(graph, CONGESTION_PENALTY_SCALE, CONGESTION_UPDATE_POLICY);
    }
    NaiveShortestPath pathStrat(graph);
    QubitRouter router(mapping, layeredCircuit, graph, &pathStrat);
    router.route_circuit();    
    if (PRINT_ROUTING) router.print_routing_steps();
    std::cout << "\nTotal routing steps (" << routing_strategy << "): " << router.get_routing_length() << "\n";
    
    double avg_parallelism = circuit.getNumGates() / router.get_routing_length();
    std::cout << "\nAverage Parallelism (" << routing_strategy << "): " << avg_parallelism << "\n\n";

    return benchmarkResult{router.get_routing_length(), avg_parallelism};
}
