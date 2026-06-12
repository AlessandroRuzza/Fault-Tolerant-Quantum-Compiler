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
#include <csignal>
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
    int resolved_number_of_magic_states = -1;
};

// ---------------------------------------------------------------------------
// Partial best-so-far state for the benchmark worker's timeout handler.
//
// The repetition loop keeps the best result in local `best_*` variables and
// only writes the worker result file once the whole loop finishes. If the
// benchmark runner's `timeout` kills the worker mid-loop (SIGTERM), every
// completed repetition would otherwise be discarded. We mirror the best-so-far
// here, in plain integer scalars that are safe to read from a signal handler,
// so the worker can persist the best completed repetition before exiting.
//
// Only integer scalars (sig_atomic_t) are used so the handler that consumes
// them stays async-signal-safe. non_routed is stored as fixed-point
// micro-units (value * 1e6; -1 = unknown) to avoid floating point in the
// handler while preserving the exact value the success path would record.
// ---------------------------------------------------------------------------
inline volatile std::sig_atomic_t g_partial_has_result = 0;
inline volatile std::sig_atomic_t g_partial_routing_steps = 0;
inline volatile std::sig_atomic_t g_partial_completed_repetitions = 0;
inline volatile std::sig_atomic_t g_partial_resolved_graph_x = -1;
inline volatile std::sig_atomic_t g_partial_resolved_graph_y = -1;
inline volatile std::sig_atomic_t g_partial_num_qubits = -1;
inline volatile std::sig_atomic_t g_partial_max_interaction_degree = -1;
inline volatile std::sig_atomic_t g_partial_resolved_n_magic = -1;
inline volatile std::sig_atomic_t g_partial_non_routed_micro = -1;

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
    double base_gaussian_weight, double gaussian_confidence, double external_weight,
    int x, int y, int dimension_offset, std::string graph_path,
    std::string magic_state_placement_strategy, int number_of_magic_states,
    double number_of_magic_states_multiplier,
    double border_distance_percentage, std::string routing_strategy,
    std::string t_routing_mode, int patience_threshold,
    bool use_layer_cache,
    bool metrics_only, int repetition_count,
    bool use_layer_cache_explicit = false,
    double cnot_formula_scale = 1.0,
    double mapped_formula_scale = 1.0) {

    // Clear any stale partial state (a worker process runs exactly one
    // one_execution, but resetting keeps the timeout handler honest).
    g_partial_has_result = 0;
    g_partial_routing_steps = 0;
    g_partial_completed_repetitions = 0;
    g_partial_non_routed_micro = -1;

    double circ_time_seconds = 0.0;
    double graph_time_seconds = 0.0;
    double mapping_time_seconds = 0.0;
    double routing_time_seconds = 0.0;
    double total_mr_time_seconds = 0.0;
    double total_time_seconds = 0.0;

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

    // Layer the circuit right after parsing — needed both for the structural
    // metrics (computed immediately, below) and as a baseline for any later
    // mapping-dependent metrics. This LayeredCircuit is used only for metrics;
    // each mapping/routing repetition builds its own (the router may mutate it).
    std::cout << "\n------- LAYERING ---------" << std::endl;
    LayeredCircuit metrics_layered(circuit, LAYERING_LOOKAHEAD);
    if (PRINT_LAYER) metrics_layered.print_layered();

    // Structural metrics: everything that doesn't need a mapping. The struct
    // is kept around so add_path_length_metrics can fill the remaining fields
    // after mapping completes.
    CircuitMetrics metrics = compute_structural_metrics(metrics_layered);

    // --metrics-only: no mapping/routing — write the (structural-only) CSV and exit.
    // Path-length fields stay at 0.
    if (metrics_only) {
        write_metrics_csv(metrics, path);
        return benchmarkResult{0, 0};
    }

    std::cout << "Setting up circuit with " << qubitsNumber << " qubits." << std::endl;

    // The layer routing cache only pays off when layers repeat heavily;
    // otherwise lookup overhead dominates. Auto-select from the reuse ratio.
    if (!use_layer_cache_explicit) {
        use_layer_cache = metrics.layer_reuse_ratio > 0.94;
        std::cout << "Layer cache auto-set to " << (use_layer_cache ? "true" : "false")
                  << " (layer_reuse_ratio = " << metrics.layer_reuse_ratio << ")\n";
    }

    // Resolve number_of_magic_states. Precedence:
    //   fractional multiplier (0<f<1) -> round(qubits * f)
    //   -1 sentinel                   -> max_t_in_layer (proportional to circuit)
    //   explicit positive int        -> used as-is
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
    } else if (number_of_magic_states == -1) {
        number_of_magic_states = metrics.max_t_in_layer;
        std::cout << "number_of_magic_states proportional: " << number_of_magic_states
                  << " (max_t_in_layer)\n";
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
            // Auto-size: base heuristic grid plus a signed delta from config.
            // dimension_offset < 0 => smaller/harder grid, > 0 => larger/easier.
            x = compute_dimensions(circuit.getNumQubits(), safe_passage_strategy, number_of_magic_states, type, border_distance_percentage, max_deg) + dimension_offset;
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
    if (graph_template.get_magic_state_ids().empty() && metrics.num_t_tdg > 0) {
        std::cerr << "Error: graph has no magic states.\n";
        throw std::runtime_error("Error: graph has no magic states");
    }

    const int resolved_graph_x = graph_template.getMaxX() + 1;
    const int resolved_graph_y = graph_template.getMaxY() + 1;
    std::cout << "resolved graph dimensions: " << resolved_graph_x << "x" << resolved_graph_y << "\n";

    // Auto-formula block: -1 sentinels for cnot_high, cnot_low, mapped.
    // Formulas are per (gaussian_strategy, safe_passage, circuit_family, dim).
    // Circuit family is detected from the filename: qft / qaoa / rest.
    {
        const std::string circ_stem = std::filesystem::path(path).stem().string();
        std::string circ_lower = circ_stem;
        std::transform(circ_lower.begin(), circ_lower.end(), circ_lower.begin(), ::tolower);
        const bool is_qft  = circ_lower.find("qft")  != std::string::npos;
        const bool is_qaoa = circ_lower.find("qaoa") != std::string::npos;
        const bool is_cube = (safe_passage_strategy == "cube");
        const bool is_fine = (gaussian_strategy == "fine");
        const double d = static_cast<double>(resolved_graph_x);

        // cnot_high formulas — dim-dependent where R²>0.24 and Δ>1pp across dim range,
        // constant elsewhere (QFT always flat; QAOA fine flat; QAOA coarse moderate).
        if (cnot_high == -1.0) {
            if (is_fine && !is_cube) {
                // fine/noncube  qft:const  qaoa:const  rest:R²=0.51 Δ=7pp
                if      (is_qft)  cnot_high = 0.35;
                else if (is_qaoa) cnot_high = 0.7;
                else              cnot_high = std::max(0.3, 0.29 * d - 1.2);
            } else if (!is_fine && !is_cube) {
                // coarse/noncube  qft:const  qaoa:R²=0.26 Δ=1.4pp  rest:R²=0.55 Δ=8.6pp
                if      (is_qft)  cnot_high = 0.5;
                else if (is_qaoa) cnot_high = std::max(0.3, 0.07 * d - 0.3);
                else              cnot_high = std::max(0.3, 0.36 * d - 2.1);
            } else if (is_fine && is_cube) {
                // fine/cube  qft:const  qaoa:const  rest:R²=0.37 Δ=7pp
                if      (is_qft)  cnot_high = 0.5;
                else if (is_qaoa) cnot_high = 5.0;
                else              cnot_high = std::max(0.3, 0.26 * d - 5.7);
            } else {
                // coarse/cube  qft:const  qaoa:R²=0.24 Δ=8pp  rest:R²=0.57 Δ=15pp
                if      (is_qft)  cnot_high = 1.0;
                else if (is_qaoa) cnot_high = std::max(0.5, 0.40 * d - 3.8);
                else              cnot_high = std::max(0.5, 0.56 * d - 13.9);
            }
            if (cnot_low == -1.0) cnot_low = 0.0;
            cnot_high *= cnot_formula_scale;
            std::cout << "cnot_high (auto): " << cnot_high
                      << "  cnot_low (auto): " << cnot_low
                      << "  cnot_formula_scale: " << cnot_formula_scale << "\n";
        }

        if (mapped_gaussian_weight == -1.0) {
            if (is_fine && !is_cube) {
                // fine/noncube
                if (is_qft)       mapped_gaussian_weight = 5.0;
                else if (is_qaoa) mapped_gaussian_weight = 3.5;
                else              mapped_gaussian_weight = std::max(0.0, 0.07 * d);
            } else if (!is_fine && !is_cube) {
                // coarse/noncube
                if (is_qft)       mapped_gaussian_weight = 0.18 * d + 3.0;
                else if (is_qaoa) mapped_gaussian_weight = 4.0;
                else              mapped_gaussian_weight = std::max(0.0, 0.12 * d);
            } else if (is_fine && is_cube) {
                // fine/cube
                if (is_qft)       mapped_gaussian_weight = std::max(0.0, 0.34 * d - 3.9);
                else if (is_qaoa) mapped_gaussian_weight = 0.6;
                else              mapped_gaussian_weight = 0.0;
            } else {
                // coarse/cube
                if (is_qft)       mapped_gaussian_weight = std::max(0.0, 0.28 * d - 3.3);
                else if (is_qaoa) mapped_gaussian_weight = std::max(0.0, 0.14 * d - 1.8);
                else              mapped_gaussian_weight = std::max(0.0, 0.08 * d - 0.93);
            }
            mapped_gaussian_weight *= mapped_formula_scale;
            std::cout << "mapped_gaussian_weight (auto): " << mapped_gaussian_weight
                      << "  mapped_formula_scale: " << mapped_formula_scale << "\n";
        }
    }

    // Publish the now-resolved circuit/graph facts so a timeout mid-loop still
    // records dimensions alongside the best completed repetition.
    g_partial_resolved_graph_x = resolved_graph_x;
    g_partial_resolved_graph_y = resolved_graph_y;
    g_partial_num_qubits = qubitsNumber;
    g_partial_max_interaction_degree = max_deg;
    g_partial_resolved_n_magic = number_of_magic_states;

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
    double max_parallelism = -1;
    
    if (repetition_count < 1) {
        repetition_count = 1;
    }

    constexpr bool print_reps = true;

    for (int repetition = 0; repetition < repetition_count; ++repetition) {
        if(print_reps) std::cout << "\n------- MAPPING & ROUTING #" << repetition+1 << " ---------" << std::endl;
        
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

        const auto routing_start = std::chrono::steady_clock::now();

        auto layeredCircuit = std::make_unique<LayeredCircuit>(circuit, LAYERING_LOOKAHEAD); //Lookahead only 2 layers
        if(max_parallelism < 0){
            const int num_layers = layeredCircuit->getNumLayers();
            max_parallelism = num_layers > 0
            ? static_cast<double>(layeredCircuit->getNumGates()) / num_layers
            : 0.0;
        }

        // pathStrategyPtr / tGateRoutingStrategyPtr are declared here so they outlive routerPtr (holds raw pointers into them).
        std::unique_ptr<IPathStrategy> pathStrategyPtr;
        std::unique_ptr<ITGateRoutingStrategy> tGateRoutingStrategyPtr;
        std::unique_ptr<IQubitRouter> routerPtr;
        auto route_metrics = std::make_unique<CircuitMetrics>();
        std::unordered_map<size_t, Routing>* cache_ptr = use_layer_cache ? &route_metrics->layer_routing_cache : nullptr;


        if (routing_strategy == "boost") {
#if FTOQC_HAS_BOOST_ROUTER
            routerPtr = std::make_unique<Boost_QubitRouter>(*mapping, *layeredCircuit, *graph);
#else
            throw std::runtime_error(
                "Routing strategy 'boost' requires Boost support, but this binary was built without Boost."
            );
#endif
        } else if (routing_strategy == "packing") {
            // Tunables overridable via env for parameter sweeps (same pattern as
            // FTQC_BFS_DENSITY_THRESHOLD in gaussian_mapping.cpp). Defaults are
            // the tuned values; env is only for re-deriving them post-hoc.
            // Tuned on qft/qaoa/randomcircuit n50-n100 sweep (2026-06): L=4
            // dominant across all k; k flat at L=4 with k=2 best and cheapest.
            int packing_candidates = 2;
            int packing_lookahead = 4;
            if (const char* env = std::getenv("FTQC_PACKING_CANDIDATES")) {
                try { packing_candidates = std::stoi(env); } catch (...) {}
            }
            if (const char* env = std::getenv("FTQC_PACKING_LOOKAHEAD")) {
                try { packing_lookahead = std::stoi(env); } catch (...) {}
            }
            routerPtr = std::make_unique<PackingQubitRouter>(
                *mapping, *layeredCircuit, *graph, packing_candidates, packing_lookahead);
        } else {
            constexpr float CONGESTION_PENALTY_SCALE = 0.35f;
            constexpr CongestionUpdatePolicy CONGESTION_UPDATE_POLICY = CongestionUpdatePolicy::STATIC_GLOBAL;
            // "naive_critical" shares the naive shortest-path strategy but orders
            // each layer's gates by criticality (dependency-chain tail) instead of
            // by route length. "naive_kpaths" also shares it, but considers up to
            // k_paths candidate paths per gate and picks the one that interferes
            // least with the rest of the layer (better per-step packing).
            GateOrdering gate_ordering = GateOrdering::PATH_LENGTH;
            if (routing_strategy == "naive" || routing_strategy == "naive_critical") {
                pathStrategyPtr = std::make_unique<NaiveShortestPath>(*graph);
                if (routing_strategy == "naive_critical") {
                    gate_ordering = GateOrdering::CRITICALITY;
                }
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
                cache_ptr,
                gate_ordering
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
            std::cout << "NEW BEST! #" << repetition << std::endl;
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

            // Mirror the new best into the partial state read by the worker's
            // timeout handler. Order matters: publish the values, then flip
            // has_result last so the handler never sees a half-updated best.
            g_partial_routing_steps = best_routing_steps;
            g_partial_non_routed_micro = best_non_routed_layer_pct >= 0.0
                ? static_cast<std::sig_atomic_t>(best_non_routed_layer_pct * 1e6 + 0.5)
                : -1;
            g_partial_has_result = 1;
        }

        // Count every completed repetition (not just the improving ones) so the
        // saved partial reports how far the loop actually got.
        g_partial_completed_repetitions = repetition + 1;

        if(print_reps) {
            std::cout << "Routing steps: " << routing_steps << "\n";
            std::cout << "Achieved avg parallelism: " << avg_parallelism << " / " << max_parallelism << "\n";
            std::cout << "Non-routed layer %: " << non_routed_layer_pct << "\n";
        }
    }

    if (!best_router || !best_mapping || !best_graph || !best_layered) {
        throw std::runtime_error("Mapping/routing repetitions produced no result.");
    }

    if (PRINT_MAPPING_GRAPH) best_graph->print_rectangular();

    // Fill in the mapping-dependent metrics (path lengths) using the best
    // repetition's mapping/graph, then update the CSV in a single write.
    add_path_length_metrics(metrics, metrics_layered, *best_mapping, *best_graph);
    write_metrics_csv(metrics, path);

    std::cout << "\n----- MAPPING RECAP -----\n";
    std::cout << "Circuit name: " << original_name.string() << "\n";
    std::cout << "Graph size: " << resolved_graph_x << " x " << resolved_graph_y << "\n";
    std::cout << "Qubits: " << qubitsNumber << "\n";
    std::cout << "Mapping type: " << type << "\n";
    std::cout << "Mapping produced: " << (best_mapping ? "yes" : "no") << "\n";
    std::cout << "Repetitions: " << repetition_count << "\n";
    std::cout << "Safe passage strategy: " << (safe_passage_strategy.empty() ? "(none)" : safe_passage_strategy) << "\n";

    std::cout << "\n------- ROUTING ---------" << std::endl;

    if (PRINT_ROUTING) best_router->print_routing_steps();

    std::cout << "\nTotal routing steps (" << routing_strategy << "): " << best_routing_steps << "\n";
    std::cout << "Achieved avg parallelism (" << routing_strategy << "): " << best_avg_parallelism << " / " << max_parallelism << "\n";
    std::cout << "Average non-routed % (" << routing_strategy << "): " << best_non_routed_layer_pct << "%\n\n";

    total_mr_time_seconds = mapping_time_seconds + routing_time_seconds;
    total_time_seconds = total_mr_time_seconds + circ_time_seconds + graph_time_seconds;
    std::cout << "Circuit time:    " << circ_time_seconds << " s\n";
    std::cout << "Graph init time: " << graph_time_seconds << " s\n";
    std::cout << "Mapping time:    " << mapping_time_seconds << " s\n";
    std::cout << "Routing time:    " << routing_time_seconds << " s\n";
    std::cout << "Total mapping + routing time: " << total_mr_time_seconds << " s\n\n";
    std::cout << "Total time: " << total_time_seconds << " s\n\n";
    
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
        best_non_routed_layer_pct,
        number_of_magic_states
    };
}
