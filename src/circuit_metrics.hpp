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

    // Layer size distribution and top-5 layer frequencies, pre-serialized
    // for the CSV writer (computed once in compute_structural_metrics).
    std::string layer_size_distribution_csv;
    std::string top5_layer_frequencies_csv;

    // Path lengths (Manhattan distance between mapped nodes; post-mapping).
    // Populated by add_path_length_metrics; stay at 0 in metrics-only mode.
    double avg_estimated_path_length = 0.0;
    int max_estimated_path_length = 0;
    double path_length_stddev = 0.0;

    std::unordered_map<size_t, Routing> layer_routing_cache;
};


// Compute every metric that depends only on the layered circuit (gate counts,
// CNOT interaction graph, layer structure, fingerprints, congestion, etc.).
// Path-length fields are left at 0 — call add_path_length_metrics later to fill
// them once a Mapping and a Graph are available.
inline CircuitMetrics compute_structural_metrics(const LayeredCircuit& layered) {
    // ---- Gate-level metrics ----
    const std::vector<Gate>& gates = layered.getGates();
    const int total_gates = layered.getNumGates();
    const int num_qubits  = layered.getNumQubits();
    const int num_layers  = layered.getNumLayers();

    int num_cnot = 0, num_t_tdg = 0;
    std::map<std::pair<int,int>, int> cnot_pair_counts;
    std::unordered_set<int> t_qubits;                            // qubits that receive a T/Tdg
    std::unordered_map<int, std::unordered_set<int>> cnot_adj;   // qubit -> partner qubits

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
            if (g.name == "cx")                        lc++;
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

    double avg_layer_size     = 0.0;
    int    max_layer_size     = 0;
    double avg_cnot_per_layer = 0.0;
    double avg_t_per_layer    = 0.0;
    int    max_t_in_layer     = 0;
    int    max_cnot_in_layer  = 0;
    int    t_depth            = 0;
    int    cnot_depth         = 0;

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
        avg_layer_size     = static_cast<double>(total_sz)   / num_layers;
        avg_cnot_per_layer = static_cast<double>(total_cnot) / num_layers;
        avg_t_per_layer    = static_cast<double>(total_t)    / num_layers;
    }

    const double t_layer_ratio     = num_layers > 0 ? static_cast<double>(t_depth)   / num_layers : 0.0;
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

    // Top-5 layer fingerprints by frequency
    std::vector<std::pair<size_t, int>> fps_sorted(fp_counts.begin(), fp_counts.end());
    std::sort(fps_sorted.begin(), fps_sorted.end(),
              [](const std::pair<size_t,int>& a, const std::pair<size_t,int>& b) {
                  return a.second > b.second;
              });

    // Pre-serialize distribution / top-5 strings so write_metrics_csv doesn't
    // need access to the layered circuit.
    std::ostringstream dist_ss, topfreq_ss;
    for (const std::pair<const int, int>& entry : size_dist) dist_ss << entry.first << ':' << entry.second << ';';
    const int top5 = std::min(static_cast<int>(fps_sorted.size()), 5);
    for (int i = 0; i < top5; i++) {
        topfreq_ss << fps_sorted[i].second;
        if (i + 1 < top5) topfreq_ss << ';';
    }

    return CircuitMetrics{
        .total_gates                  = total_gates,
        .num_qubits                   = num_qubits,
        .num_cnot                     = num_cnot,
        .num_t_tdg                    = num_t_tdg,
        .num_other_gates              = num_other_gates,
        .t_ratio                      = t_ratio,
        .cnot_ratio                   = cnot_ratio,
        .other_gate_ratio             = other_gate_ratio,
        .num_unique_cnot_pairs        = num_unique_cnot_pairs,
        .max_cnot_pair_rep            = max_cnot_pair_rep,
        .avg_cnot_pair_rep            = avg_cnot_pair_rep,
        .cnot_interaction_density     = cnot_interaction_density,
        .max_cnot_degree              = max_cnot_degree,
        .t_qubit_diversity            = t_qubit_diversity,
        .num_layers                   = num_layers,
        .num_unique_layers            = num_unique_layers,
        .layer_reuse_ratio            = layer_reuse_ratio,
        .depth_width_ratio            = depth_width_ratio,
        .avg_layer_size               = avg_layer_size,
        .max_layer_size               = max_layer_size,
        .avg_cnot_per_layer           = avg_cnot_per_layer,
        .avg_t_per_layer              = avg_t_per_layer,
        .max_t_in_layer               = max_t_in_layer,
        .max_cnot_in_layer            = max_cnot_in_layer,
        .t_depth                      = t_depth,
        .cnot_depth                   = cnot_depth,
        .t_layer_ratio                = t_layer_ratio,
        .layer_congestion_score       = congestion_score,
        .max_repeated_seq_len         = max_rep_seq,
        .layer_size_distribution_csv  = dist_ss.str(),
        .top5_layer_frequencies_csv   = topfreq_ss.str(),
        // path-length fields default to 0 — filled by add_path_length_metrics
    };
}


// Fill in the path-length fields (avg / max / stddev). Requires the mapping
// to be complete; uses Manhattan distance between mapped graph nodes for
// every CNOT in the circuit. No print, no CSV write.
inline void add_path_length_metrics(
    CircuitMetrics& metrics,
    const LayeredCircuit& layered,
    const Mapping& mapping,
    const IGraph& graph
) {
    const std::vector<Gate>& gates = layered.getGates();

    std::vector<int> cnot_dists;
    cnot_dists.reserve(metrics.num_cnot);
    int max_path_len = 0;

    for (const Gate& g : gates) {
        if (g.name != "cx" || g.qubits.size() < 2) continue;
        const int n0 = mapping.get_mapped_node(static_cast<int>(g.qubits[0]));
        const int n1 = mapping.get_mapped_node(static_cast<int>(g.qubits[1]));
        if (n0 < 0 || n1 < 0) continue;
        const Node& nd0 = graph.get_node(n0);
        const Node& nd1 = graph.get_node(n1);
        const int dist = std::abs(nd0.coordX - nd1.coordX) +
                         std::abs(nd0.coordY - nd1.coordY);
        cnot_dists.push_back(dist);
        max_path_len = std::max(max_path_len, dist);
    }

    if (cnot_dists.empty()) {
        metrics.avg_estimated_path_length = 0.0;
        metrics.max_estimated_path_length = 0;
        metrics.path_length_stddev        = 0.0;
        return;
    }

    long long sum = 0;
    for (int d : cnot_dists) sum += d;
    const double avg = static_cast<double>(sum) / cnot_dists.size();

    double var = 0.0;
    for (int d : cnot_dists) {
        const double diff = d - avg;
        var += diff * diff;
    }
    var /= cnot_dists.size();

    metrics.avg_estimated_path_length = avg;
    metrics.max_estimated_path_length = max_path_len;
    metrics.path_length_stddev        = std::sqrt(var);
}


// Write (update-or-insert) the CSV row for this circuit to
// benchmarks/results/cache_metrics/all_circuits_cache_metrics.csv.
// Does not print or compute anything: it only serializes the metrics struct.
inline void write_metrics_csv(const CircuitMetrics& metrics,
                              const std::string& circuit_path) {
    namespace fs = std::filesystem;

    const std::string circuit_name = fs::path(circuit_path).stem().string();
    const fs::path csv_dir = fs::path(PROJECT_ROOT) / "benchmarks" / "results" / "cache_metrics";
    fs::create_directories(csv_dir);
    const fs::path csv_path = csv_dir / "all_circuits_cache_metrics.csv";

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

    // Read existing CSV and filter out current circuit. Drop everything on schema mismatch.
    std::vector<std::string> csv_lines;
    {
        std::ifstream read_csv(csv_path);
        std::string line;
        int line_num = 0;
        while (std::getline(read_csv, line)) {
            line_num++;
            if (line_num == 1) {
                if (line != CANONICAL_HEADER) {
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

    std::ofstream csv(csv_path, std::ios::out);
    if (!csv.is_open()) {
        std::cerr << "Warning: could not open " << csv_path << " for writing\n";
        return;
    }

    csv << CANONICAL_HEADER << '\n';
    for (const std::string& line : csv_lines) csv << line << '\n';

    csv << std::fixed << std::setprecision(6)
        << circuit_name << ','
        << metrics.total_gates << ',' << metrics.num_qubits << ','
        << metrics.num_cnot << ',' << metrics.num_t_tdg << ',' << metrics.num_other_gates << ','
        << metrics.t_ratio << ',' << metrics.cnot_ratio << ',' << metrics.other_gate_ratio << ','
        << metrics.num_unique_cnot_pairs << ',' << metrics.max_cnot_pair_rep << ',' << metrics.avg_cnot_pair_rep << ','
        << metrics.cnot_interaction_density << ',' << metrics.max_cnot_degree << ',' << metrics.t_qubit_diversity << ','
        << metrics.num_layers << ',' << metrics.num_unique_layers << ',' << metrics.layer_reuse_ratio << ',' << metrics.depth_width_ratio << ','
        << metrics.avg_layer_size << ',' << metrics.max_layer_size << ',' << metrics.avg_cnot_per_layer << ',' << metrics.avg_t_per_layer << ','
        << metrics.max_t_in_layer << ',' << metrics.max_cnot_in_layer << ',' << metrics.t_depth << ',' << metrics.cnot_depth << ',' << metrics.t_layer_ratio << ','
        << metrics.layer_congestion_score << ',' << metrics.max_repeated_seq_len << ','
        << '"' << metrics.layer_size_distribution_csv << '"' << ',' << '"' << metrics.top5_layer_frequencies_csv << '"' << ','
        << metrics.avg_estimated_path_length << ',' << metrics.max_estimated_path_length << ',' << metrics.path_length_stddev << '\n';
}

#endif // CIRCUIT_METRICS_HPP
