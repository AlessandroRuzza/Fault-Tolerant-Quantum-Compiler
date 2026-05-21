#ifndef CIRCUIT_METRICS_HPP
#define CIRCUIT_METRICS_HPP

#include "circuit.hpp"
#include "layering.hpp"
#include "mapping.hpp"
#include "igraph.hpp"
#include "routing.hpp"

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

// Returns a numeric hash that identifies the gate set of a layer.
// Faster than a string-based fingerprint: no ostringstream, no heap string per gate.
inline size_t compute_layer_fingerprint(const Layer& layer) {
    // Compute a hash for each gate (name + sorted qubits), then sort the per-gate
    // hashes so the result is independent of the unordered_set iteration order.
    std::vector<size_t> gate_hashes;
    gate_hashes.reserve(layer.size());
    for (const Gate& g : layer) {
        size_t h = std::hash<std::string>{}(g.name);
        // Do NOT sort qubits: qubit order is semantically significant for two-qubit
        // gates (e.g. cx(0,1) and cx(1,0) are different gates).
        for (uint32_t q : g.qubits) {
            // hash_combine: avoids trivial XOR cancellation
            h ^= std::hash<uint32_t>{}(q) + 0x9e3779b9u + (h << 6) + (h >> 2);
        }
        gate_hashes.push_back(h);
    }
    std::sort(gate_hashes.begin(), gate_hashes.end());
    size_t result = 0;
    for (size_t h : gate_hashes) {
        result ^= h + 0x9e3779b9u + (result << 6) + (result >> 2);
    }
    return result;
}

struct CircuitMetrics {
    // Gate counts and ratios
    int total_gates = 0;
    int num_qubits = 0;
    int num_cnot = 0;
    int num_t_tdg = 0;
    int num_other_gates = 0;        // h, rz, x, s, sdg, ccx, ... (not cx/t/tdg)
    double t_ratio = 0.0;           // num_t_tdg / total_gates
    double cnot_ratio = 0.0;        // num_cnot / total_gates
    double other_gate_ratio = 0.0;  // num_other_gates / total_gates; t+cnot+other = 1

    // CNOT interaction graph (undirected, qubit-level)
    int num_unique_cnot_pairs = 0;
    int max_cnot_pair_rep = 0;
    double avg_cnot_pair_rep = 0.0;
    double cnot_interaction_density = 0.0;  // unique_pairs / (n*(n-1)/2)
    int max_cnot_degree = 0;                // max neighbours any qubit has in CNOT graph
    int t_qubit_diversity = 0;              // distinct qubits that receive a T/Tdg gate

    // Layer structure (depth, parallelism)
    int num_layers = 0;
    int num_unique_layers = 0;
    double layer_reuse_ratio = 0.0;
    double depth_width_ratio = 0.0;  // num_layers / num_qubits — tall vs wide
    double avg_layer_size = 0.0;
    int max_layer_size = 0;
    double avg_cnot_per_layer = 0.0;
    double avg_t_per_layer = 0.0;
    int max_t_in_layer = 0;
    int max_cnot_in_layer = 0;
    int t_depth = 0;                  // # layers with >=1 T/Tdg gate
    int cnot_depth = 0;               // # layers with >=1 CNOT
    double t_layer_ratio = 0.0;       // t_depth / num_layers
    double layer_congestion_score = 0.0;  // CV of layer sizes (std/mean)
    int max_repeated_seq_len = 0;

    // Path lengths (Manhattan distance between mapped nodes; post-mapping)
    double avg_estimated_path_length = 0.0;
    int max_estimated_path_length = 0;
    double path_length_stddev = 0.0;

    std::unordered_map<size_t, Routing> layer_routing_cache;
};

// Computes, prints, and optionally writes to CSV all circuit cache metrics.
// Call with write_csv=true on the first invocation (after mapping, before routing)
// and write_csv=false on the second invocation (final summary after routing).
// Pass mapping=nullptr / graph=nullptr to skip path-length metrics (fields = 0).
// Returns a CircuitMetrics struct with all computed metrics.
inline CircuitMetrics compute_and_print_circuit_metrics(
    const LayeredCircuit& layered,
    const std::string& circuit_path,
    bool write_csv,
    const Mapping* mapping = nullptr,
    const IGraph* graph = nullptr
) {
    namespace fs = std::filesystem;

    // ---- Gate-level metrics ----
    const std::vector<Gate>& gates = layered.getGates();
    const int total_gates  = layered.getNumGates();
    const int num_qubits   = layered.getNumQubits();
    const int num_layers   = layered.getNumLayers();

    int num_cnot = 0, num_t_tdg = 0;
    std::map<std::pair<int,int>, int> cnot_pair_counts;
    std::unordered_set<int> t_qubits;                     // qubits that receive a T/Tdg
    std::unordered_map<int, std::unordered_set<int>> cnot_adj;  // qubit -> partner qubits

    for (const Gate& g : gates) {
        if (g.name == "cx") {
            num_cnot++;
            if (g.qubits.size() >= 2) {
                const int q0 = static_cast<int>(g.qubits[0]);
                const int q1 = static_cast<int>(g.qubits[1]);
                cnot_pair_counts[{std::min(q0, q1), std::max(q0, q1)}]++;
                cnot_adj[q0].insert(q1);
                cnot_adj[q1].insert(q0);
            }
        } else if (g.name == "t" || g.name == "tdg") {
            num_t_tdg++;
            for (uint32_t q : g.qubits) t_qubits.insert(static_cast<int>(q));
        }
    }

    const int    num_other_gates  = std::max(0, total_gates - num_cnot - num_t_tdg);
    const double t_ratio          = total_gates > 0 ? static_cast<double>(num_t_tdg)        / total_gates : 0.0;
    const double cnot_ratio       = total_gates > 0 ? static_cast<double>(num_cnot)         / total_gates : 0.0;
    const double other_gate_ratio = total_gates > 0 ? static_cast<double>(num_other_gates)  / total_gates : 0.0;

    const int num_unique_cnot_pairs = static_cast<int>(cnot_pair_counts.size());
    double avg_cnot_pair_rep = 0.0;
    int    max_cnot_pair_rep = 0;
    if (!cnot_pair_counts.empty()) {
        int total_rep = 0;
        for (const std::pair<const std::pair<int,int>, int>& entry : cnot_pair_counts) {
            total_rep += entry.second;
            max_cnot_pair_rep = std::max(max_cnot_pair_rep, entry.second);
        }
        avg_cnot_pair_rep = static_cast<double>(total_rep) / cnot_pair_counts.size();
    }

    // Density of the undirected CNOT interaction graph: fraction of possible qubit pairs used
    double cnot_interaction_density = 0.0;
    if (num_qubits >= 2) {
        const double max_pairs = static_cast<double>(num_qubits) * (num_qubits - 1) / 2.0;
        cnot_interaction_density = static_cast<double>(num_unique_cnot_pairs) / max_pairs;
    }

    // Max degree in the CNOT interaction graph: predicts whether a single qubit
    // is a "hub" that talks to many others (mapping is harder).
    int max_cnot_degree = 0;
    for (const std::pair<const int, std::unordered_set<int>>& entry : cnot_adj) {
        max_cnot_degree = std::max(max_cnot_degree, static_cast<int>(entry.second.size()));
    }

    const int t_qubit_diversity = static_cast<int>(t_qubits.size());

    // ---- Layer fingerprints (numeric hash: gate name + sorted qubits) ----
    std::vector<size_t> layer_fps;
    std::vector<int>    layer_sizes;
    std::vector<int>    layer_cnot_counts;
    std::vector<int>    layer_t_counts;
    std::map<size_t, int> fp_counts;

    layer_fps.reserve(num_layers);
    layer_sizes.reserve(num_layers);
    layer_cnot_counts.reserve(num_layers);
    layer_t_counts.reserve(num_layers);

    for (int i = 0; i < num_layers; i++) {
        const Layer& layer = layered.getLayer(i);
        const int sz = static_cast<int>(layer.size());
        layer_sizes.push_back(sz);

        int lc = 0, lt = 0;
        for (const Gate& g : layer) {
            if (g.name == "cx")                  lc++;
            else if (g.name == "t" || g.name == "tdg") lt++;
        }
        layer_cnot_counts.push_back(lc);
        layer_t_counts.push_back(lt);

        size_t fp = compute_layer_fingerprint(layer);
        layer_fps.push_back(fp);
        fp_counts[fp]++;
    }

    const int num_unique_layers = static_cast<int>(fp_counts.size());
    const double layer_reuse_ratio = num_layers > 0
        ? static_cast<double>(num_layers - num_unique_layers) / num_layers
        : 0.0;

    double avg_layer_size    = 0.0;
    int    max_layer_size    = 0;
    double avg_cnot_per_layer = 0.0;
    double avg_t_per_layer    = 0.0;
    int    max_t_in_layer    = 0;
    int    max_cnot_in_layer = 0;
    int    t_depth           = 0;  // layers with at least one T/Tdg gate
    int    cnot_depth        = 0;  // layers with at least one CNOT

    if (num_layers > 0) {
        int total_sz = 0, total_cnot = 0, total_t = 0;
        for (int i = 0; i < num_layers; i++) {
            total_sz   += layer_sizes[i];
            total_cnot += layer_cnot_counts[i];
            total_t    += layer_t_counts[i];
            max_layer_size    = std::max(max_layer_size,    layer_sizes[i]);
            max_cnot_in_layer = std::max(max_cnot_in_layer, layer_cnot_counts[i]);
            max_t_in_layer    = std::max(max_t_in_layer,    layer_t_counts[i]);
            if (layer_t_counts[i]    > 0) t_depth++;
            if (layer_cnot_counts[i] > 0) cnot_depth++;
        }
        avg_layer_size    = static_cast<double>(total_sz)   / num_layers;
        avg_cnot_per_layer = static_cast<double>(total_cnot) / num_layers;
        avg_t_per_layer    = static_cast<double>(total_t)    / num_layers;
    }

    const double t_layer_ratio    = num_layers > 0 ? static_cast<double>(t_depth)   / num_layers : 0.0;
    const double depth_width_ratio = num_qubits  > 0 ? static_cast<double>(num_layers) / num_qubits : 0.0;

    // Layer size distribution
    std::map<int, int> size_dist;
    for (int sz : layer_sizes) size_dist[sz]++;

    // Layer congestion score: coefficient of variation of layer sizes
    double congestion_score = 0.0;
    if (num_layers > 0 && avg_layer_size > 0.0) {
        double var = 0.0;
        for (int sz : layer_sizes) {
            const double d = sz - avg_layer_size;
            var += d * d;
        }
        var /= num_layers;
        congestion_score = std::sqrt(var) / avg_layer_size;
    }

    // Longest repeated non-overlapping consecutive sequence of layers
    // O(n^2) with structural fingerprint comparison; capped at 500 layers for performance
    int max_rep_seq = 0;
    {
        const int n = std::min(static_cast<int>(layer_fps.size()), 500);
        for (int i = 0; i < n - 1; i++) {
            for (int j = i + 1; j < n; j++) {
                if (layer_fps[i] != layer_fps[j]) continue;
                int len = 1;
                // Extend while non-overlapping (i+len < j) and within bounds
                while (j + len < n && i + len < j &&
                       layer_fps[i + len] == layer_fps[j + len]) {
                    len++;
                }
                // Accept only if the two copies truly don't overlap
                if (j >= i + len) {
                    max_rep_seq = std::max(max_rep_seq, len);
                }
            }
        }
    }

    // Layers sorted by frequency (most frequent first)
    std::vector<std::pair<size_t, int>> fps_sorted(fp_counts.begin(), fp_counts.end());
    std::sort(fps_sorted.begin(), fps_sorted.end(),
              [](const std::pair<size_t,int>& a, const std::pair<size_t,int>& b) {
                  return a.second > b.second;
              });

    // Estimated path lengths for CNOT gates (Manhattan distance between mapped nodes).
    // Two-pass: collect distances, then mean + population stddev.
    // Skipped when mapping/graph are null (metrics-only mode with no mapping).
    std::vector<int> cnot_dists;
    int max_path_len = 0;
    if (mapping != nullptr && graph != nullptr) {
        cnot_dists.reserve(num_cnot);
        for (const Gate& g : gates) {
            if (g.name == "cx" && g.qubits.size() >= 2) {
                const int n0 = mapping->get_mapped_node(static_cast<int>(g.qubits[0]));
                const int n1 = mapping->get_mapped_node(static_cast<int>(g.qubits[1]));
                if (n0 >= 0 && n1 >= 0) {
                    const Node& nd0 = graph->get_node(n0);
                    const Node& nd1 = graph->get_node(n1);
                    const int dist = std::abs(nd0.coordX - nd1.coordX) +
                                     std::abs(nd0.coordY - nd1.coordY);
                    cnot_dists.push_back(dist);
                    max_path_len = std::max(max_path_len, dist);
                }
            }
        }
    }
    double avg_path_len = 0.0;
    double path_length_stddev = 0.0;
    if (!cnot_dists.empty()) {
        long long sum = 0;
        for (int d : cnot_dists) sum += d;
        avg_path_len = static_cast<double>(sum) / cnot_dists.size();
        double var = 0.0;
        for (int d : cnot_dists) {
            const double diff = d - avg_path_len;
            var += diff * diff;
        }
        var /= cnot_dists.size();
        path_length_stddev = std::sqrt(var);
    }

    if(PRINT_CACHE_METRICS)
    { 
        std::cout << "\n========== CIRCUIT CACHE METRICS ==========\n"
                << std::fixed << std::setprecision(4);

        std::cout << "[Gate Metrics]\n";
        std::cout << "  Total routable gates:          " << total_gates             << "\n";
        std::cout << "  Logical qubits:                " << num_qubits              << "\n";
        std::cout << "  CNOT gates:                    " << num_cnot                << "\n";
        std::cout << "  T/Tdg gates:                   " << num_t_tdg               << "\n";
        std::cout << "  Other gates (h,rz,x,...):      " << num_other_gates         << "\n";
        std::cout << "  T-count ratio:                 " << t_ratio                 << "\n";
        std::cout << "  CNOT ratio:                    " << cnot_ratio              << "\n";
        std::cout << "  Other-gate ratio:              " << other_gate_ratio        << "\n";
        std::cout << "  Unique CNOT pairs:             " << num_unique_cnot_pairs   << "\n";
        std::cout << "  Max CNOT pair repetition:      " << max_cnot_pair_rep       << "\n";
        std::cout << "  Avg CNOT pair repetition:      " << avg_cnot_pair_rep       << "\n";
        std::cout << "  CNOT interaction density:      " << cnot_interaction_density << "\n";
        std::cout << "  Max CNOT degree (hub qubit):   " << max_cnot_degree         << "\n";
        std::cout << "  T-qubit diversity:             " << t_qubit_diversity       << "\n";

        std::cout << "[Layer Metrics]\n";
        std::cout << "  Total layers (circuit depth):  " << num_layers           << "\n";
        std::cout << "  Unique layers:                 " << num_unique_layers    << "\n";
        std::cout << "  Layer reuse ratio:             " << layer_reuse_ratio    << "\n";
        std::cout << "  Depth/width ratio:             " << depth_width_ratio    << "\n";
        std::cout << "  Avg layer size (gates/layer):  " << avg_layer_size       << "\n";
        std::cout << "  Max layer size:                " << max_layer_size       << "\n";
        std::cout << "  Avg CNOT per layer:            " << avg_cnot_per_layer   << "\n";
        std::cout << "  Avg T/Tdg per layer:           " << avg_t_per_layer      << "\n";
        std::cout << "  Max T/Tdg in one layer:        " << max_t_in_layer       << "\n";
        std::cout << "  Max CNOT in one layer:         " << max_cnot_in_layer    << "\n";
        std::cout << "  T-depth (layers with T):       " << t_depth              << "\n";
        std::cout << "  CNOT-depth (layers with CNOT): " << cnot_depth           << "\n";
        std::cout << "  T-layer ratio:                 " << t_layer_ratio        << "\n";
        std::cout << "  Layer size CV (parallelism):   " << congestion_score     << "\n";
        std::cout << "  Max repeated seq length:       " << max_rep_seq          << "\n";

        std::cout << "[Layer Size Distribution]\n";
        for (const std::pair<const int, int>& entry : size_dist)
            std::cout << "  size=" << entry.first << ": " << entry.second << " layer(s)\n";

        std::cout << "[Top Layers by Frequency]\n";
        const int show_n = std::min(static_cast<int>(fps_sorted.size()), 5);
        for (int i = 0; i < show_n; i++)
            std::cout << "  [" << (i + 1) << "] freq=" << fps_sorted[i].second
                    << "  pattern: " << fps_sorted[i].first << "\n";

        std::cout << "[Path Length Metrics (post-mapping, Manhattan distance)]\n";
        std::cout << "  Avg estimated path length:     " << avg_path_len       << "\n";
        std::cout << "  Max estimated path length:     " << max_path_len       << "\n";
        std::cout << "  Path length stddev:            " << path_length_stddev << "\n";
        std::cout << "============================================\n\n";
    }
    
    // Build the result struct once via designated initializers. Field names must match
    // CircuitMetrics declaration; ordering follows the struct definition.
    CircuitMetrics metrics{
        .total_gates                = total_gates,
        .num_qubits                 = num_qubits,
        .num_cnot                   = num_cnot,
        .num_t_tdg                  = num_t_tdg,
        .num_other_gates            = num_other_gates,
        .t_ratio                    = t_ratio,
        .cnot_ratio                 = cnot_ratio,
        .other_gate_ratio           = other_gate_ratio,
        .num_unique_cnot_pairs      = num_unique_cnot_pairs,
        .max_cnot_pair_rep          = max_cnot_pair_rep,
        .avg_cnot_pair_rep          = avg_cnot_pair_rep,
        .cnot_interaction_density   = cnot_interaction_density,
        .max_cnot_degree            = max_cnot_degree,
        .t_qubit_diversity          = t_qubit_diversity,
        .num_layers                 = num_layers,
        .num_unique_layers          = num_unique_layers,
        .layer_reuse_ratio          = layer_reuse_ratio,
        .depth_width_ratio          = depth_width_ratio,
        .avg_layer_size             = avg_layer_size,
        .max_layer_size             = max_layer_size,
        .avg_cnot_per_layer         = avg_cnot_per_layer,
        .avg_t_per_layer            = avg_t_per_layer,
        .max_t_in_layer             = max_t_in_layer,
        .max_cnot_in_layer          = max_cnot_in_layer,
        .t_depth                    = t_depth,
        .cnot_depth                 = cnot_depth,
        .t_layer_ratio              = t_layer_ratio,
        .layer_congestion_score     = congestion_score,
        .max_repeated_seq_len       = max_rep_seq,
        .avg_estimated_path_length  = avg_path_len,
        .max_estimated_path_length  = max_path_len,
        .path_length_stddev         = path_length_stddev,
    };

    if (write_csv) {
        // ====== SINGLE CSV (update-or-insert) ======
        const std::string circuit_name = fs::path(circuit_path).stem().string();
        const fs::path csv_dir = fs::path(PROJECT_ROOT) / "benchmarks" / "results" / "cache_metrics";
        fs::create_directories(csv_dir);
        const fs::path csv_path = csv_dir / "all_circuits_cache_metrics.csv";

        // Serialize layer size distribution and top-5 frequencies
        std::ostringstream dist_ss, topfreq_ss;
        for (const std::pair<const int, int>& entry : size_dist) dist_ss << entry.first << ':' << entry.second << ';';
        const int top5 = std::min(static_cast<int>(fps_sorted.size()), 5);
        for (int i = 0; i < top5; i++) {
            topfreq_ss << fps_sorted[i].second;
            if (i + 1 < top5) topfreq_ss << ';';
        }

        // Canonical header for the current metrics schema. If a stale CSV exists with a
        // different header, its rows are discarded (different columns would misalign).
        static constexpr const char* CANONICAL_HEADER =
            "circuit,total_routable_gates,num_logical_qubits,"
            "num_cnot,num_t_tdg,num_other_gates,"
            "t_count_ratio,cnot_ratio,other_gate_ratio,"
            "num_unique_cnot_pairs,max_cnot_pair_repetition,avg_cnot_pair_repetition,"
            "cnot_interaction_density,max_cnot_degree,t_qubit_diversity,"
            "total_layers,num_unique_layers,layer_reuse_ratio,depth_width_ratio,"
            "avg_layer_size,max_layer_size,avg_cnot_per_layer,avg_t_per_layer,"
            "max_t_in_layer,max_cnot_in_layer,t_depth,cnot_depth,t_layer_ratio,"
            "layer_congestion_score,max_repeated_seq_len,"
            "layer_size_distribution,top5_layer_frequencies,"
            "avg_estimated_path_length,max_estimated_path_length,path_length_stddev";

        // Read existing CSV and filter out current circuit (if it exists). When the
        // header doesn't match the canonical one, drop all old rows — they cannot be
        // safely concatenated under a different column layout.
        std::vector<std::string> csv_lines;
        bool schema_match = true;
        {
            std::ifstream read_csv(csv_path);
            std::string line;
            int line_num = 0;
            while (std::getline(read_csv, line)) {
                line_num++;
                if (line_num == 1) {
                    if (line != CANONICAL_HEADER) {
                        schema_match = false;
                        std::cout << "Cache-metrics CSV schema changed: regenerating from scratch.\n";
                        break;
                    }
                } else {
                    size_t comma_pos = line.find(',');
                    if (comma_pos != std::string::npos) {
                        std::string existing_circuit = line.substr(0, comma_pos);
                        if (existing_circuit != circuit_name) {
                            csv_lines.push_back(line);
                        }
                    }
                }
            }
        }
        (void)schema_match;  // value already used to decide whether to keep rows

        // Write CSV with canonical header + existing (compatible) circuits + updated circuit
        std::ofstream csv(csv_path, std::ios::out);
        if (!csv.is_open()) {
            std::cerr << "Warning: could not open " << csv_path << " for writing\n";
            return CircuitMetrics{};
        }

        csv << CANONICAL_HEADER << '\n';

        for (const std::string& line : csv_lines) {
            csv << line << '\n';
        }

        // Write current circuit. Column order MUST match CANONICAL_HEADER.
        csv << std::fixed << std::setprecision(6)
            << circuit_name << ','
            << total_gates << ',' << num_qubits << ','
            << num_cnot << ',' << num_t_tdg << ',' << num_other_gates << ','
            << t_ratio << ',' << cnot_ratio << ',' << other_gate_ratio << ','
            << num_unique_cnot_pairs << ',' << max_cnot_pair_rep << ',' << avg_cnot_pair_rep << ','
            << cnot_interaction_density << ',' << max_cnot_degree << ',' << t_qubit_diversity << ','
            << num_layers << ',' << num_unique_layers << ',' << layer_reuse_ratio << ',' << depth_width_ratio << ','
            << avg_layer_size << ',' << max_layer_size << ',' << avg_cnot_per_layer << ',' << avg_t_per_layer << ','
            << max_t_in_layer << ',' << max_cnot_in_layer << ',' << t_depth << ',' << cnot_depth << ',' << t_layer_ratio << ','
            << congestion_score << ',' << max_rep_seq << ','
            << '"' << dist_ss.str() << '"' << ',' << '"' << topfreq_ss.str() << '"' << ','
            << avg_path_len << ',' << max_path_len << ',' << path_length_stddev << '\n';

        csv.close();
        std::cout << "Cache metrics CSV written to: " << csv_path << "\n\n";
    }

    return metrics;
}

#endif // CIRCUIT_METRICS_HPP
