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

inline std::string compute_layer_fingerprint(const Layer& layer) {
    std::vector<std::string> parts;
    parts.reserve(layer.size());
    for (const Gate& g : layer) {
        std::ostringstream oss;
        oss << g.name;
        std::vector<uint32_t> qs = g.qubits;
        std::sort(qs.begin(), qs.end());
        for (uint32_t q : qs) oss << '_' << q;
        parts.push_back(oss.str());
    }
    std::sort(parts.begin(), parts.end());
    std::ostringstream res;
    for (const std::string& s : parts) res << s << '|';
    return res.str();
}

struct CircuitMetrics {
    int total_gates = 0;
    int num_qubits = 0;
    int num_cnot = 0;
    int num_t_tdg = 0;
    double t_ratio = 0.0;
    double cnot_ratio = 0.0;
    int num_unique_cnot_pairs = 0;
    int max_cnot_pair_rep = 0;
    double avg_cnot_pair_rep = 0.0;
    int num_layers = 0;
    int num_unique_layers = 0;
    double layer_reuse_ratio = 0.0;
    double avg_layer_size = 0.0;
    int max_layer_size = 0;
    double avg_cnot_per_layer = 0.0;
    double avg_t_per_layer = 0.0;
    int max_t_in_layer = 0;
    int max_cnot_in_layer = 0;
    double layer_congestion_score = 0.0;
    int max_repeated_seq_len = 0;
    double avg_estimated_path_length = 0.0;
    int max_estimated_path_length = 0;
    std::unordered_map<std::string, Routing> layer_routing_cache;
};

// Computes, prints, and optionally writes to CSV all circuit cache metrics.
// Call with write_csv=true on the first invocation (after mapping, before routing)
// and write_csv=false on the second invocation (final summary after routing).
// Returns a CircuitMetrics struct with all computed metrics.
inline CircuitMetrics compute_and_print_circuit_metrics(
    const LayeredCircuit& layered,
    const Mapping& mapping,
    const IGraph& graph,
    const std::string& circuit_path,
    bool write_csv
) {
    namespace fs = std::filesystem;

    // ---- Gate-level metrics ----
    const std::vector<Gate>& gates = layered.getGates();
    const int total_gates  = layered.getNumGates();
    const int num_qubits   = layered.getNumQubits();
    const int num_layers   = layered.getNumLayers();

    int num_cnot = 0, num_t_tdg = 0;
    std::map<std::pair<int,int>, int> cnot_pair_counts;

    for (const Gate& g : gates) {
        if (g.name == "cx") {
            num_cnot++;
            if (g.qubits.size() >= 2) {
                std::pair<int,int> key = std::make_pair(
                    static_cast<int>(std::min(g.qubits[0], g.qubits[1])),
                    static_cast<int>(std::max(g.qubits[0], g.qubits[1]))
                );
                cnot_pair_counts[key]++;
            }
        } else if (g.name == "t" || g.name == "tdg") {
            num_t_tdg++;
        }
    }

    const double t_ratio    = total_gates > 0 ? static_cast<double>(num_t_tdg) / total_gates : 0.0;
    const double cnot_ratio = total_gates > 0 ? static_cast<double>(num_cnot)   / total_gates : 0.0;
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

    // ---- Layer fingerprints (structural: gate name + sorted qubits) ----
    std::vector<std::string> layer_fps;
    std::vector<int>         layer_sizes;
    std::vector<int>         layer_cnot_counts;
    std::vector<int>         layer_t_counts;
    std::map<std::string, int> fp_counts;

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

        std::string fp = compute_layer_fingerprint(layer);
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

    if (num_layers > 0) {
        int total_sz = 0, total_cnot = 0, total_t = 0;
        for (int i = 0; i < num_layers; i++) {
            total_sz   += layer_sizes[i];
            total_cnot += layer_cnot_counts[i];
            total_t    += layer_t_counts[i];
            max_layer_size    = std::max(max_layer_size,    layer_sizes[i]);
            max_cnot_in_layer = std::max(max_cnot_in_layer, layer_cnot_counts[i]);
            max_t_in_layer    = std::max(max_t_in_layer,    layer_t_counts[i]);
        }
        avg_layer_size    = static_cast<double>(total_sz)   / num_layers;
        avg_cnot_per_layer = static_cast<double>(total_cnot) / num_layers;
        avg_t_per_layer    = static_cast<double>(total_t)    / num_layers;
    }

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
    std::vector<std::pair<std::string, int>> fps_sorted(fp_counts.begin(), fp_counts.end());
    std::sort(fps_sorted.begin(), fps_sorted.end(),
              [](const std::pair<std::string,int>& a, const std::pair<std::string,int>& b) {
                  return a.second > b.second;
              });

    // Estimated path lengths for CNOT gates (Manhattan distance between mapped nodes)
    double avg_path_len = 0.0;
    int    max_path_len = 0;
    int    cnot_counted = 0;
    for (const Gate& g : gates) {
        if (g.name == "cx" && g.qubits.size() >= 2) {
            const int n0 = mapping.get_mapped_node(static_cast<int>(g.qubits[0]));
            const int n1 = mapping.get_mapped_node(static_cast<int>(g.qubits[1]));
            if (n0 >= 0 && n1 >= 0) {
                const Node& nd0 = graph.get_node(n0);
                const Node& nd1 = graph.get_node(n1);
                const int dist = std::abs(nd0.coordX - nd1.coordX) +
                                 std::abs(nd0.coordY - nd1.coordY);
                avg_path_len += dist;
                max_path_len  = std::max(max_path_len, dist);
                cnot_counted++;
            }
        }
    }
    if (cnot_counted > 0) avg_path_len /= cnot_counted;

    // ====== PRINT ======
    std::cout << "\n========== CIRCUIT CACHE METRICS ==========\n"
              << std::fixed << std::setprecision(4);

    std::cout << "[Gate Metrics]\n";
    std::cout << "  Total routable gates:          " << total_gates          << "\n";
    std::cout << "  Logical qubits:                " << num_qubits           << "\n";
    std::cout << "  CNOT gates:                    " << num_cnot             << "\n";
    std::cout << "  T/Tdg gates:                   " << num_t_tdg            << "\n";
    std::cout << "  T-count ratio:                 " << t_ratio              << "\n";
    std::cout << "  CNOT ratio:                    " << cnot_ratio           << "\n";
    std::cout << "  Unique CNOT pairs:             " << num_unique_cnot_pairs << "\n";
    std::cout << "  Max CNOT pair repetition:      " << max_cnot_pair_rep    << "\n";
    std::cout << "  Avg CNOT pair repetition:      " << avg_cnot_pair_rep    << "\n";

    std::cout << "[Layer Metrics]\n";
    std::cout << "  Total layers:                  " << num_layers           << "\n";
    std::cout << "  Unique layers:                 " << num_unique_layers    << "\n";
    std::cout << "  Layer reuse ratio:             " << layer_reuse_ratio    << "\n";
    std::cout << "  Avg layer size:                " << avg_layer_size       << "\n";
    std::cout << "  Max layer size:                " << max_layer_size       << "\n";
    std::cout << "  Avg gates per layer:           " << avg_layer_size       << "\n";
    std::cout << "  Avg CNOT per layer:            " << avg_cnot_per_layer   << "\n";
    std::cout << "  Avg T/Tdg per layer:           " << avg_t_per_layer      << "\n";
    std::cout << "  Max T/Tdg in one layer:        " << max_t_in_layer       << "\n";
    std::cout << "  Max CNOT in one layer:         " << max_cnot_in_layer    << "\n";
    std::cout << "  Layer congestion score (CV):   " << congestion_score     << "\n";
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
    std::cout << "  Avg estimated path length:     " << avg_path_len << "\n";
    std::cout << "  Max estimated path length:     " << max_path_len << "\n";
    std::cout << "============================================\n\n";

    if (!write_csv) {
        CircuitMetrics metrics{
            total_gates, num_qubits, num_cnot, num_t_tdg, t_ratio, cnot_ratio,
            num_unique_cnot_pairs, max_cnot_pair_rep, avg_cnot_pair_rep,
            num_layers, num_unique_layers, layer_reuse_ratio, avg_layer_size,
            max_layer_size, avg_cnot_per_layer, avg_t_per_layer,
            max_t_in_layer, max_cnot_in_layer, congestion_score,
            max_rep_seq, avg_path_len, max_path_len
        };
        metrics.layer_routing_cache = {};
        return metrics;
    }

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

    // Read existing CSV and filter out current circuit (if it exists)
    std::vector<std::string> csv_lines;
    std::string header;
    {
        std::ifstream read_csv(csv_path);
        std::string line;
        int line_num = 0;
        while (std::getline(read_csv, line)) {
            line_num++;
            if (line_num == 1) {
                header = line;
            } else {
                // Keep lines that don't match current circuit
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

    // Write CSV with header + existing circuits + updated circuit
    std::ofstream csv(csv_path, std::ios::out);
    if (!csv.is_open()) {
        std::cerr << "Warning: could not open " << csv_path << " for writing\n";
        return CircuitMetrics{};
    }

    // Write header
    if (header.empty()) {
        csv << "circuit,total_routable_gates,num_logical_qubits,num_cnot,num_t_tdg,"
               "t_count_ratio,cnot_ratio,num_unique_cnot_pairs,max_cnot_pair_repetition,"
               "avg_cnot_pair_repetition,total_layers,num_unique_layers,layer_reuse_ratio,"
               "avg_layer_size,max_layer_size,avg_gates_per_layer,avg_cnot_per_layer,"
               "avg_t_per_layer,max_t_in_layer,max_cnot_in_layer,layer_congestion_score,"
               "max_repeated_seq_len,layer_size_distribution,top5_layer_frequencies,"
               "avg_estimated_path_length,max_estimated_path_length\n";
    } else {
        csv << header << '\n';
    }

    // Write existing circuits
    for (const std::string& line : csv_lines) {
        csv << line << '\n';
    }

    // Write current circuit (updated)
    csv << std::fixed << std::setprecision(6)
        << circuit_name << ',' << total_gates << ',' << num_qubits << ','
        << num_cnot << ',' << num_t_tdg << ',' << t_ratio << ',' << cnot_ratio << ','
        << num_unique_cnot_pairs << ',' << max_cnot_pair_rep << ',' << avg_cnot_pair_rep << ','
        << num_layers << ',' << num_unique_layers << ',' << layer_reuse_ratio << ','
        << avg_layer_size << ',' << max_layer_size << ',' << avg_layer_size << ','
        << avg_cnot_per_layer << ',' << avg_t_per_layer << ',' << max_t_in_layer << ','
        << max_cnot_in_layer << ',' << congestion_score << ',' << max_rep_seq << ','
        << '"' << dist_ss.str() << '"' << ',' << '"' << topfreq_ss.str() << '"' << ','
        << avg_path_len << ',' << max_path_len << '\n';

    csv.close();
    std::cout << "Cache metrics CSV written to: " << csv_path << "\n\n";

    CircuitMetrics metrics{
        total_gates, num_qubits, num_cnot, num_t_tdg, t_ratio, cnot_ratio,
        num_unique_cnot_pairs, max_cnot_pair_rep, avg_cnot_pair_rep,
        num_layers, num_unique_layers, layer_reuse_ratio, avg_layer_size,
        max_layer_size, avg_cnot_per_layer, avg_t_per_layer,
        max_t_in_layer, max_cnot_in_layer, congestion_score,
        max_rep_seq, avg_path_len, max_path_len
    };
    metrics.layer_routing_cache = {};
    return metrics;
}

#endif // CIRCUIT_METRICS_HPP
