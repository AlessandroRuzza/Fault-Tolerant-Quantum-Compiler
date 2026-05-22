#include "circuit.hpp"
#include "graph.hpp"
#include "layering.hpp"
#include "maxHeap.hpp"
#include "mapping.hpp"
#include "routing.hpp"

#ifndef FTOQC_HAS_BOOST_ROUTER
#define FTOQC_HAS_BOOST_ROUTER 0
#endif

#if FTOQC_HAS_BOOST_ROUTER
#include "boost_router.hpp"
#endif

#include "defines.hpp"
#include "compute_dimensions.hpp"
#include "helpers.hpp"
#include "circuit_metrics.hpp"

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
    int num_qubits = -1;
    int max_interaction_degree = -1;
    double non_routed_layer_pct = -1.0;
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
    double base_gaussian_weight, double size_moltiplier, double gaussian_confidence, double external_weight,
    int x, int y, std::string graph_path,
    std::string magic_state_placement_strategy, int number_of_magic_states,
    double number_of_magic_states_multiplier,
    double border_distance_percentage, std::string routing_strategy,
    std::string t_routing_mode, int patience_threshold,
    bool use_layer_cache,
    bool metrics_only, int repetition_count) {

    double circ_time_seconds = 0.0;
    double graph_time_seconds = 0.0;
    double mapping_time_seconds = 0.0;
    double routing_time_seconds = 0.0;
    double total_mr_time_seconds = 0.0;
    double total_time_seconds = 0.0;

    const auto actual_exec_start = std::chrono::steady_clock::now();

    //----------circuit------------

    const auto circ_init_start = std::chrono::steady_clock::now();
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

    
    
    const auto circ_init_end = std::chrono::steady_clock::now();
    circ_time_seconds += std::chrono::duration<double>(circ_init_end - circ_init_start).count();

    if (PRINT_CIRCUIT) circuit.print_qubit_heap();

    int qubitsNumber = circuit.getNumQubits();

    if (qubitsNumber == 0){
        std::cout << "no routable gates\n";
        return benchmarkResult{0, 0};
    }

    // --metrics-only: build layers from the parsed circuit, write CSV, then exit.
    // Path-length metrics are skipped (no mapping is performed).
    if (metrics_only) {
        LayeredCircuit layeredCircuit(circuit, LAYERING_LOOKAHEAD);
        compute_and_print_circuit_metrics(layeredCircuit, path, true);
        return benchmarkResult{0, 0};
    }

    std::cout << "Setting up circuit with " << qubitsNumber << " qubits." << std::endl;

    if (number_of_magic_states_multiplier > 0.0) {
        number_of_magic_states = static_cast<int>(std::round(static_cast<double>(qubitsNumber) * number_of_magic_states_multiplier));
        if (number_of_magic_states < 1) {
            number_of_magic_states = 1;
        }
        if (!std::isfinite(static_cast<double>(number_of_magic_states)) || number_of_magic_states <= 0) {
            throw std::runtime_error("Resolved number_of_magic_states must be > 0");
        }


        std::cout
            << "Resolved number_of_magic_states from multiplier: "
            << qubitsNumber << " * " << number_of_magic_states_multiplier
            << " -> " << number_of_magic_states << "\n";
    }

    std::filesystem::path original_name = std::filesystem::path(path).stem();
    std::filesystem::path output_path =
        std::filesystem::path(PROJECT_ROOT) /
        "universal_set_qasms" /
        (original_name.string() + "_universal.qasm");
    if (benchmark_artifacts_enabled() || WRITE_UNIVERSAL_QASM) {
        circuit.write_qasm_file(output_path.string());
    }

    //---------------graph----------------

    const auto graph_init_start = std::chrono::steady_clock::now();

    const bool use_generated_graph = graph_path.empty();
    const int max_deg = circuit.getMaxInteractionDegree();

    if (use_generated_graph) {
        if (x == 0 || y == 0) {
            x = compute_upper_dimensions(qubitsNumber, max_deg);
            y = x;
        } else if (x < 0 || y < 0){
            const int sentinel = (x < 0) ? x : y;
            const int offset = -sentinel - 1;
            x = compute_dimensions(circuit.getNumQubits(), safe_passage_strategy, number_of_magic_states, type, border_distance_percentage, max_deg) + offset;
            y = x;
        }
        std::cout << "Creating rectangular graph with dimensions " << x << "x" << y << "...\n";
    } else {
        std::cout << "Loading graph from " << graph_path << "...\n";
    }


    int safe_passage_ignore_outer_layers = std::max(1, static_cast<int>(std::min(x, y) / 2.5));

    Graph graph_template(
        use_generated_graph,
        100,
        number_of_magic_states,
        border_distance_percentage,
        magic_state_placement_strategy,
        x,
        y,
        graph_path
    );

    
    const auto graph_init_end = std::chrono::steady_clock::now();
    graph_time_seconds += std::chrono::duration<double>(graph_init_end - graph_init_start).count();

    if (graph_template.get_node_count() <= 0) {
        std::cerr << "Error: graph is empty or invalid.\n";
        throw std::runtime_error("Error: graph is empty or invalid");
    }
    if (graph_template.get_magic_state_ids().empty()) {
        std::cerr << "Error: graph has no magic states.\n";
        throw std::runtime_error("Error: graph has no magic states");
    }

    const int resolved_graph_x = graph_template.getMaxX() + 1;
    const int resolved_graph_y = graph_template.getMaxY() + 1;
    std::cout << "resolved graph dimensions: " << resolved_graph_x << "x" << resolved_graph_y << "\n";

    output_path = std::filesystem::path(PROJECT_ROOT) /
                "qasm_graphs" /
                (original_name.string() + ".graph");
    if (benchmark_artifacts_enabled() || WRITE_GRAPH_FOR_WISQ) {
        graph_template.write_file(output_path.string());
    }


    std::unique_ptr<Graph> best_graph;
    std::unique_ptr<Mapping> best_mapping;
    std::unique_ptr<LayeredCircuit> best_layered;
    std::unique_ptr<IQubitRouter> best_router;
    std::unique_ptr<IPathStrategy> best_path_strategy;
    std::unique_ptr<ITGateRoutingStrategy> best_t_gate_strategy;
    std::unique_ptr<CircuitMetrics> best_route_metrics;
    int best_routing_steps = std::numeric_limits<int>::max();
    double best_avg_parallelism = 0.0;
    double best_non_routed_layer_pct = -1.0;

    if (repetition_count < 1) {
        repetition_count = 1;
    }

    for (int repetition = 0; repetition < repetition_count; ++repetition) {
        std::cout << "\n------- MAPPING & ROUTING #" << repetition+1 << " ---------" << std::endl;
        
        auto graph = std::make_unique<Graph>(graph_template);

        const auto mapping_start = std::chrono::steady_clock::now();

        auto mapping = std::make_unique<Mapping>(
            circuit,
            *graph,
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
            external_weight,
            circuit.getNumQubits()*2,
            safe_passage_ignore_outer_layers
        );

        mapping->map();
        const auto mapping_end = std::chrono::steady_clock::now();
        mapping_time_seconds +=
            std::chrono::duration<double>(mapping_end - mapping_start).count();

        for (int qubit = 0; qubit < circuit.getQubitsVectorSize(); ++qubit) {
            if (circuit.getQubit(qubit) == nullptr) {
                continue;
            }
            if (mapping->get_mapped_node(qubit) < 0) {
                throw std::runtime_error(
                    "Incomplete mapping: qubit " + std::to_string(qubit) + " was not mapped."
                );
            }
        }

        auto layeredCircuit = std::make_unique<LayeredCircuit>(circuit, LAYERING_LOOKAHEAD); //Lookahead only 2 layers

        // pathStrategyPtr / tGateRoutingStrategyPtr are declared here so they outlive routerPtr
        // (QubitRouter holds raw pointers into them).
        std::unique_ptr<IPathStrategy> pathStrategyPtr;
        std::unique_ptr<ITGateRoutingStrategy> tGateRoutingStrategyPtr;
        std::unique_ptr<IQubitRouter> routerPtr;
        auto route_metrics = std::make_unique<CircuitMetrics>();
        std::unordered_map<size_t, Routing>* cache_ptr = use_layer_cache ? &route_metrics->layer_routing_cache : nullptr;

        const auto routing_start = std::chrono::steady_clock::now();

        if (routing_strategy == "boost") {
#if FTOQC_HAS_BOOST_ROUTER
            routerPtr = std::make_unique<Boost_QubitRouter>(*mapping, *layeredCircuit, *graph);
#else
            throw std::runtime_error(
                "Routing strategy 'boost' requires Boost support, but this binary was built without Boost."
            );
#endif
        } else {
            constexpr float CONGESTION_PENALTY_SCALE = 0.35f;
            constexpr CongestionUpdatePolicy CONGESTION_UPDATE_POLICY = CongestionUpdatePolicy::STATIC_GLOBAL;
            if (routing_strategy == "naive") {
                pathStrategyPtr = std::make_unique<NaiveShortestPath>(*graph);
            } else { // default to congestion-aware
                pathStrategyPtr = std::make_unique<CongestionAwareShortestPath>(
                    *graph,
                    CONGESTION_PENALTY_SCALE,
                    CONGESTION_UPDATE_POLICY
                );
            }
            if (t_routing_mode == "smart_t_routing") {
                tGateRoutingStrategyPtr = std::make_unique<SmartTGateRouting>(patience_threshold);
            } else {
                tGateRoutingStrategyPtr = std::make_unique<NormalTGateRouting>();
            }
            routerPtr = std::make_unique<QubitRouter>(
                *mapping,
                *layeredCircuit,
                *graph,
                pathStrategyPtr.get(),
                tGateRoutingStrategyPtr.get(),
                cache_ptr
            );
        }

        routerPtr->route_circuit();
        const auto routing_end = std::chrono::steady_clock::now();
        routing_time_seconds +=
            std::chrono::duration<double>(routing_end - routing_start).count();

        const int routing_steps = routerPtr->get_routing_length();
        const double avg_parallelism = routing_steps > 0
            ? static_cast<double>(circuit.getNumGates()) / routing_steps
            : 0.0;
        const double non_routed_layer_pct = routerPtr->get_non_routed_layer_percentage();

        if(PRINT_CIRCUIT_METRICS || PRINT_CACHE_METRICS)
            routerPtr->print_non_routed_histogram();

        if (routing_steps < best_routing_steps) {
            std::cout << "NEW BEST!" << std::endl;
            best_routing_steps = routing_steps;
            best_avg_parallelism = avg_parallelism;
            best_non_routed_layer_pct = non_routed_layer_pct;
            best_graph = std::move(graph);
            best_mapping = std::move(mapping);
            best_layered = std::move(layeredCircuit);
            best_router = std::move(routerPtr);
            best_path_strategy = std::move(pathStrategyPtr);
            best_t_gate_strategy = std::move(tGateRoutingStrategyPtr);
            best_route_metrics = std::move(route_metrics);
        }

        std::cout << "Routing steps: " << routing_steps << "\n";
        std::cout << "Avg parallelism: " << avg_parallelism << "\n";
        std::cout << "Non-routed layer %: " << non_routed_layer_pct << "\n";
    }

    const auto actual_exec_end = std::chrono::steady_clock::now();
    const auto actual_exec_time_seconds = std::chrono::duration<double>(actual_exec_end - actual_exec_start).count();

    if (!best_router || !best_mapping || !best_graph || !best_layered) {
        throw std::runtime_error("Mapping/routing repetitions produced no result.");
    }

    if (PRINT_MAPPING_GRAPH) best_graph->print_rectangular();

    std::cout << "\n------- LAYERING ---------" << std::endl;
    LayeredCircuit metrics_layered = LayeredCircuit(circuit, LAYERING_LOOKAHEAD); //Lookahead only 2 layers
    if (PRINT_LAYER) metrics_layered.print_layered();

    compute_and_print_circuit_metrics(
        metrics_layered,
        path,
        PRINT_CIRCUIT_METRICS,
        best_mapping.get(),
        best_graph.get()
    );

    // if(metrics.layer_reuse_ratio > 0.95){
    //     use_layer_cache = true;
    // }

    std::cout << "\n------- ROUTING ---------" << std::endl;

    if (PRINT_ROUTING) best_router->print_routing_steps();
    std::cout << "\nTotal routing steps (" << routing_strategy << "): " << best_routing_steps << "\n";

    std::cout << "Average Parallelism (" << routing_strategy << "): " << best_avg_parallelism << "\n\n";

    std::cout << "Average non-routed % (" << routing_strategy << "): " << best_non_routed_layer_pct << "%\n\n";

    total_mr_time_seconds = mapping_time_seconds + routing_time_seconds;
    total_time_seconds = total_mr_time_seconds + circ_time_seconds + graph_time_seconds;
    std::cout << "Circuit time:    " << circ_time_seconds << " s\n";
    std::cout << "Graph init time: " << graph_time_seconds << " s\n";
    std::cout << "Mapping time:    " << mapping_time_seconds << " s\n";
    std::cout << "Routing time:    " << routing_time_seconds << " s\n";
    std::cout << "Total mapping + routing time: " << total_mr_time_seconds << " s\n\n";
    std::cout << "Total time: " << total_time_seconds << " s\n\n";
    std::cout << "Total time (incl. instantiations and prints): " << actual_exec_time_seconds << " s\n\n";
    
    compute_and_print_circuit_metrics(
        *best_layered,
        path,
        PRINT_CIRCUIT_METRICS,
        best_mapping.get(),
        best_graph.get()
    );
    (void)best_layered;
    (void)best_path_strategy;
    (void)best_t_gate_strategy;
    (void)best_route_metrics;

    return benchmarkResult{
        best_routing_steps,
        best_avg_parallelism,
        resolved_graph_x,
        resolved_graph_y,
        qubitsNumber,
        max_deg,
        best_non_routed_layer_pct
    };
}
