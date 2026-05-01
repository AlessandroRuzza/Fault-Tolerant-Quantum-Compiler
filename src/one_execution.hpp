#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"
#include "maxHeap.hpp"
#include "mapping.hpp"
#include "routing.hpp"
#include "boost_router.hpp"
#include "defines.hpp"
#include "compute_dimensions.hpp"
#include "helpers.hpp"

#include <memory>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <limits>
#include <unordered_set>

using namespace std;

struct benchmarkResult {
    int routing_steps = 0;
    double avg_parallelism = 1;
    int resolved_graph_x = -1;
    int resolved_graph_y = -1;
};

namespace {
void clear_visualization_outputs() {
    namespace fs = std::filesystem;

    if (!benchmark_artifacts_enabled()) {
        return;
    }

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
    double base_gaussian_weight, double size_moltiplier, double gaussian_confidence, int x, int y, std::string graph_path,
    std::string magic_state_placement_strategy, int number_of_magic_states,
    double number_of_magic_states_multiplier,
    double border_distance_percentage, std::string routing_strategy,
    std::string t_routing_mode, int patience_threshold) {


    //----------circuit------------

    Circuit circuit = Circuit();

    try {
        circuit.parse_qasm_file(path);
        auto gates = circuit.getGates();
        if (PRINT_PARSING)
            for (size_t i = 0; i < gates.size(); ++i) {
                const auto &g = gates[i];
                std::cout << g.id << ": " << g.to_string() << "\n";
            }
    } catch (const std::exception &e) {
        std::cerr << "Error: " << e.what() << std::endl;
        throw std::runtime_error("Error parsing QASM file");
    }

    if (PRINT_CIRCUIT) circuit.print_qubit_heap();

    int qubitsNumber = circuit.getNumQubits();

    if (qubitsNumber == 0){
        std::cout << "no routable gates\n";
        return benchmarkResult{0, 0};
    }


    std::cout << "Setting up circuit with " << qubitsNumber << " qubits." << std::endl;

    if (number_of_magic_states_multiplier > 0.0) {
        number_of_magic_states = static_cast<int>(std::round(static_cast<double>(qubitsNumber) * number_of_magic_states_multiplier));
        if (!std::isfinite(number_of_magic_states) || number_of_magic_states <= 0.0) {
            throw std::runtime_error("Resolved number_of_magic_states must be > 0");
        }

        if (number_of_magic_states < 1) {
            number_of_magic_states = 1;
        }


        std::cout
            << "Resolved number_of_magic_states from multiplier: "
            << qubitsNumber << " * " << number_of_magic_states_multiplier
            << " -> " << number_of_magic_states << "\n";
    }

    std::filesystem::path original_name = std::filesystem::path(path).stem();
    std::string output_path = "universal_set_qasms/" + original_name.string() + "_universal.qasm";
    if (benchmark_artifacts_enabled()) {
        circuit.write_qasm_file(output_path);
    }

    //---------------graph----------------

    const bool use_generated_graph = graph_path.empty();
    
    if (use_generated_graph) {
        if (x == -1 || y == -1){
            x = compute_dimensions(circuit.getNumQubits(), safe_passage_strategy, number_of_magic_states, type, border_distance_percentage);
            y = x;
        }
        std::cout << "Creating rectangular graph with dimensions " << x << "x" << y << "...\n";
    } else {
        std::cout << "Loading graph from " << graph_path << "...\n";
    }


    int safe_passage_ignore_outer_layers = 0;
    if (magic_state_placement_strategy == "center_circle" &&
        number_of_magic_states > 2*x + 2*y - 5) {
        
        safe_passage_ignore_outer_layers = 1;
        border_distance_percentage = 0.0;
        std::cout << "Safe passage will ignore outer layer of graph due to large number of magic states with center_circle placement strategy.\n";
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

    const int resolved_graph_x = graph.getMaxX() + 1;
    const int resolved_graph_y = graph.getMaxY() + 1;
    std::cout << "resolved graph dimensions: " << resolved_graph_x << "x" << resolved_graph_y << "\n";


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
        size_moltiplier,
        gaussian_confidence,
        circuit.getNumQubits()*2,
        safe_passage_ignore_outer_layers
    );

    const auto mapping_start = std::chrono::steady_clock::now();
    mapping.map();
    const auto mapping_end = std::chrono::steady_clock::now();
    const double mapping_time_seconds =
        std::chrono::duration<double>(mapping_end - mapping_start).count();

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
    LayeredCircuit layeredCircuit = LayeredCircuit(circuit, LAYERING_LOOKAHEAD); //Lookahead only 2 layers
    if (PRINT_LAYER) layeredCircuit.print_layered();


    std::cout << "------- ROUTING ---------" << std::endl;
    // pathStrategyPtr / tGateRoutingStrategyPtr are declared here so they outlive routerPtr
    // (QubitRouter holds raw pointers into them).
    std::unique_ptr<IPathStrategy> pathStrategyPtr;
    std::unique_ptr<ITGateRoutingStrategy> tGateRoutingStrategyPtr;
    std::unique_ptr<IQubitRouter> routerPtr;

    if (routing_strategy == "boost") {
        routerPtr = std::make_unique<Boost_QubitRouter>(mapping, layeredCircuit, graph);
    } else {
        constexpr float CONGESTION_PENALTY_SCALE = 0.35f;
        constexpr CongestionUpdatePolicy CONGESTION_UPDATE_POLICY = CongestionUpdatePolicy::STATIC_GLOBAL;
        if (routing_strategy == "naive") {
            pathStrategyPtr = std::make_unique<NaiveShortestPath>(graph);
        } else { // default to congestion-aware
            pathStrategyPtr = std::make_unique<CongestionAwareShortestPath>(graph, CONGESTION_PENALTY_SCALE, CONGESTION_UPDATE_POLICY);
        }
        if (t_routing_mode == "smart_t_routing") {
            tGateRoutingStrategyPtr = std::make_unique<SmartTGateRouting>(patience_threshold);
        } else {
            tGateRoutingStrategyPtr = std::make_unique<NormalTGateRouting>();
        }
        routerPtr = std::make_unique<QubitRouter>(
            mapping,
            layeredCircuit,
            graph,
            pathStrategyPtr.get(),
            tGateRoutingStrategyPtr.get()
        );
    }

    const auto routing_start = std::chrono::steady_clock::now();
    routerPtr->route_circuit();
    const auto routing_end = std::chrono::steady_clock::now();
    const double routing_time_seconds =
        std::chrono::duration<double>(routing_end - routing_start).count();

    if (PRINT_ROUTING) routerPtr->print_routing_steps();
    std::cout << "\nTotal routing steps (" << routing_strategy << "): " << routerPtr->get_routing_length() << "\n";

    double avg_parallelism = double(circuit.getNumGates()) / routerPtr->get_routing_length();
    std::cout << "Average Parallelism (" << routing_strategy << "): " << avg_parallelism << "\n\n";

    const double total_time_seconds = mapping_time_seconds + routing_time_seconds;
    std::cout << "Mapping time: " << mapping_time_seconds << " s\n";
    std::cout << "Routing time: " << routing_time_seconds << " s\n";
    std::cout << "Total mapping + routing time: " << total_time_seconds << " s\n\n";

    return benchmarkResult{
        router.get_routing_length(),
        avg_parallelism,
        resolved_graph_x,
        resolved_graph_y
    };
}
