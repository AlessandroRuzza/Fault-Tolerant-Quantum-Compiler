#ifndef MAPPING_HPP
#define MAPPING_HPP

#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <cctype>
#include <cmath>

#include "circuit.hpp"
#include "graph.hpp"
#include "farthest_from_magic.hpp"
#include "qubit.hpp"
#include "defines.hpp"

class Gaussian;


// Custom exceptions for mapping errors
class MapNearMagicError : public std::runtime_error {
public:
    MapNearMagicError(const std::string& msg) : std::runtime_error(msg) {}
};

class MapNearQubitError : public std::runtime_error {
public:
    MapNearQubitError(const std::string& msg) : std::runtime_error(msg) {}
};

class Mapping {


public:
    enum class MappingStrategy {
        DISTANCE,
        CENTER,
        RANDOM
    };


    enum class MappingType {
        MAGIC_AWARE,
        HOMOGENEOUS,
        GAUSSIAN,
        RANDOM
    };

    enum class GaussianStrategy {
        COARSE,
        FINE
    };

    enum class SafePassageStrategy {
        PASSAGE,
        PASSAGE_NO_SUBGRAPHS,
        CUBE,
        CONNECTIVITY
    };

    static vector<std::string> get_available_mapping_strategies() {
        return {"distance", "center", "random"};
    }

    static vector<std::string> get_available_mapping_types() {
        return {"magic_aware", "gaussian", "random"};
    }

    static vector<std::string> get_available_gaussian_strategies() {
        return {"coarse", "fine"};
    }

    static vector<std::string> get_available_safe_passage_strategies() {
        return {"passage", "passage_no_subgraphs", "cube", "connectivity"};
    }


    static std::string available_mapping_strategies() {
        return "distance | center | random";
    } 

    static std::string available_mapping_types() {
        return "magic_aware | gaussian | random";
    }

    static std::string available_gaussian_strategies() {
        return "coarse | fine";
    }

    static std::string available_safe_passage_strategies() {
        return "passage | passage_no_subgraphs | cube | connectivity";
    }


private:
    Circuit& circuit;
    Graph& graph;
    std::unordered_map<int, int> graph_to_circuit;
    MappingStrategy mappingStrategy;
    MappingType mappingType;
    GaussianStrategy gaussianStrategy;
    SafePassageStrategy safePassageStrategy;
    double magicHigh;
    double magicLow;
    double cnotHigh;
    double cnotLow;
    double mappedGaussianWeight;
    double baseGaussianWeight;
    double sizeMoltiplier;
    double gaussianConfidence;
    double externalWeight;
    int T_lower_bound;
    int T_upper_bound;
    int CNOT_threshold;
    int maximum_iterations;
    FarthestFromMagicSelector farthest_from_magic_selector;
    int safe_passage_ignore_outer_layers;
    std::vector<Gate> cnot_gates;
    std::vector<Gate> t_gates;

public:

    Mapping(
        Circuit& circuit,
        Graph& graph,
        const std::string& magic_aware_strategy_name,
        const std::string& type_name,
        const std::string& gaussian_strategy_name,
        const std::string& safe_passage_strategy,
        double magic_high,
        double magic_low,
        double cnot_high,
        double cnot_low,
        double mapped_gaussian_weight,
        double base_gaussian_weight,
        double size_moltiplier,
        double gaussian_confidence,
        double external_weight,
        int maximum_iterations,
        int safe_passage_ignore_outer_layers
    ) :
    circuit(circuit),
    graph(graph),
    magicHigh(magic_high),
    magicLow(magic_low),
    cnotHigh(cnot_high),
    cnotLow(cnot_low),
    mappedGaussianWeight(mapped_gaussian_weight),
    baseGaussianWeight(base_gaussian_weight),
    sizeMoltiplier(size_moltiplier),
    gaussianConfidence(gaussian_confidence),
    externalWeight(external_weight),
    maximum_iterations(maximum_iterations),
    safe_passage_ignore_outer_layers(safe_passage_ignore_outer_layers),
    farthest_from_magic_selector(graph)  {
        if (!set_mapping_strategy(magic_aware_strategy_name)) {
            throw std::invalid_argument("Invalid magic-aware strategy: " + magic_aware_strategy_name);
        }
        if (!set_mapping_type(type_name)) {
            throw std::invalid_argument("Invalid mapping type: " + type_name);
        }
        if (!set_gaussian_strategy(gaussian_strategy_name)) {
            throw std::invalid_argument("Invalid gaussian strategy: " + gaussian_strategy_name);
        }
        if (!set_safe_passage_strategy(safe_passage_strategy)) {
            throw std::invalid_argument("Invalid safe passage strategy: " + safe_passage_strategy);
        }
        cnot_gates = circuit.getGates();
        {
            std::unordered_set<uint64_t> seen_pairs;
            cnot_gates.erase( // Filter to 2qubit gates and dedup by qubit pair
                std::remove_if(cnot_gates.begin(), cnot_gates.end(),
                    [&seen_pairs](const Gate& gate) {
                        if (gate.qubits.size() < 2) return true;
                        const int a = std::min(gate.qubits[0], gate.qubits[1]);
                        const int b = std::max(gate.qubits[0], gate.qubits[1]);
                        const uint64_t key = ((uint64_t)a << 32) | (uint32_t)b;
                        return !seen_pairs.insert(key).second;
                    }),
                cnot_gates.end()
            );
        }
        t_gates = circuit.getGates();
        {
            std::unordered_set<int> seen_qubits;
            t_gates.erase( // Filter to T gates and dedup by qubit
                std::remove_if(t_gates.begin(), t_gates.end(),
                    [&seen_qubits](const Gate& gate) {
                        if (gate.name != "t") return true;
                        return !seen_qubits.insert(gate.qubits[0]).second;
                    }),
                t_gates.end()
            );
        }
        validate_gaussian_weights();
        set_thresholds();
    }



    inline void pseudo_random_mapping(Qubit* qubit, int second_qubit) {
        switch (mappingStrategy) {
            case MappingStrategy::CENTER:
                center_mapping(qubit, second_qubit);
                return;
            case MappingStrategy::RANDOM:
                random_mapping(qubit, second_qubit);
                return;
            case MappingStrategy::DISTANCE:
            default:
                distance_mapping(qubit, second_qubit);
                return;
        }
    }

    
    inline void map() {
        switch (mappingType) {
            case MappingType::MAGIC_AWARE:
                magic_aware_mapping();
                return;
            case MappingType::HOMOGENEOUS:
                homogeneous_mapping();
                return;
            case MappingType::GAUSSIAN:
                gaussian_mapping();
                return;
            case MappingType::RANDOM:
                random_cube_mapping();
                return;
            default:
                throw std::runtime_error("Invalid mapping type");
        }
    }


    inline bool check_safe_passage(const Node& node, const Qubit& q, const std::vector<Node>& occupied_nodes) {
        switch (safePassageStrategy) {
            case SafePassageStrategy::PASSAGE:
                return safe_passage(node, occupied_nodes);
            case SafePassageStrategy::PASSAGE_NO_SUBGRAPHS:
                return safe_passage_no_subgraphs(node, occupied_nodes);
            case SafePassageStrategy::CUBE:
                return _3x3_occupied(node, occupied_nodes);
            case SafePassageStrategy::CONNECTIVITY:
                return safe_connectivity(node, q, occupied_nodes);
            default:
                throw std::runtime_error("Invalid safe passage strategy");
        }
    }

    inline bool check_safe_passage(const Node& node, const Qubit& q) {
        return check_safe_passage(node, q, graph.get_occupied_nodes());
    }




    inline std::string current_mapping_strategy_name() const {
        switch (mappingStrategy) {
            case MappingStrategy::DISTANCE:
                return "distance";
            case MappingStrategy::CENTER:
                return "center";
            case MappingStrategy::RANDOM:
                return "random";
            default:
                return "unknown";
        }
    }

    inline std::string current_gaussian_strategy_name() const {
        switch (gaussianStrategy) {
            case GaussianStrategy::COARSE:
                return "coarse";
            case GaussianStrategy::FINE:
                return "fine";
            default:
                return "unknown";
        }
    }

    inline double getMagicHigh() const { return magicHigh; }
    inline double getMagicLow() const { return magicLow; }
    inline double getCnotHigh() const { return cnotHigh; }
    inline double getCnotLow() const { return cnotLow; }
    inline double getMappedGaussianWeight() const { return mappedGaussianWeight; }
    inline double getBaseGaussianWeight() const { return baseGaussianWeight; }
    inline double getSizeMoltiplier() const { return sizeMoltiplier; }
    inline double getGaussianConfidence() const { return gaussianConfidence; }
    inline double getExternalWeight() const { return externalWeight; }


    // returns -1 if qubit is not mapped
    inline const int get_mapped_node(int qubit) const {
        auto it = graph_to_circuit.find(qubit);
        if (it != graph_to_circuit.end()) {
            return it->second;
        }
        return -1; // Not mapped
    }

    const void print_mapping() const {
        for (const auto& pair : graph_to_circuit) {
            std::cout << "Qubit " << pair.first << " -> Node " << pair.second << "\n";
        }
    }

    void clear_mapping() {
        graph_to_circuit.clear();
    }

    const bool mapToNeighbor(
        int qubit,
        int node_id,
        int iterations,
        std::unordered_set<int>* visited_nodes = nullptr
    );


    int map_qubit_to_node(
        int qubit,
        int node,
        int iterations,
        std::unordered_set<int>* visited_nodes = nullptr
    );


    // ----------mapping algorithms----------

    void magic_aware_mapping();

    void homogeneous_mapping();

    void gaussian_mapping();

    void random_cube_mapping();

    bool _3x3_occupied(const Node& node, const std::vector<Node>& occupied_nodes);

    bool safe_passage(const Node& node, const std::vector<Node>& occupied_nodes);
    bool safe_passage_no_subgraphs(const Node& node, const std::vector<Node>& occupied_nodes);
    bool safe_connectivity(const Node& node, const Qubit& q, const std::vector<Node>& occupied_nodes);
private:

    void one_iteration_magic_aware_mapping(Qubit* qubit, int* iterations);

    void one_iteration_gaussian_mapping(Qubit* qubit, int* iterations, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, Gaussian& baseline_gaussian);
    
    void random_mapping(Qubit* qubit, int second_qubit);

    void center_mapping(Qubit* qubit, int second_qubit);

    void distance_mapping(Qubit* qubit, int second_qubit);

    Node computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit);




    //---------helpers---------------


    inline void set_thresholds() {
        int total_qubits = circuit.getNumQubits();
        const double t_mean = circuit.getTMean();
        const double t_std = circuit.getTStd();
        const double cnot_mean = circuit.getCNOTMean();

        std::cout << "\n\ntotal_qubits:" << total_qubits << "\n";
        std::cout << "T gates per qubit - Mean: " << t_mean << ", Std: " << t_std << "\n";

        T_lower_bound = static_cast<int>(std::floor(t_mean - t_std));
        T_upper_bound = static_cast<int>(std::ceil(t_mean + t_std));

        CNOT_threshold = static_cast<int>(std::ceil(cnot_mean));
        if (CNOT_threshold < 1) {
            CNOT_threshold = 1;
        }

        std::cout << "T_count lower bound: " << T_lower_bound << "\n";
        std::cout << "T_count upper bound: " << T_upper_bound << "\n";
        std::cout << "CNOT_count threshold: " << CNOT_threshold << "\n\n";
    }



    std::string normalize_strategy_name(const std::string& strategy_name) {
        std::string normalized;
        normalized.reserve(strategy_name.size());

        for (char ch : strategy_name) {
            normalized.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
        }

        return normalized;
    }

    std::string normalize_type_name(const std::string& type_name) {
        std::string normalized;
        normalized.reserve(type_name.size());

        for (char ch : type_name) {
            normalized.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
        }

        return normalized;
    }


    inline bool set_mapping_strategy(const std::string& strategy_name) {
        const std::string normalized_name = normalize_strategy_name(strategy_name);

        if (normalized_name == "distance") {
            mappingStrategy = MappingStrategy::DISTANCE;
            return true;
        } else if (normalized_name == "center") {
            mappingStrategy = MappingStrategy::CENTER;
            return true;
        } else if (normalized_name == "random") {
            mappingStrategy = MappingStrategy::RANDOM;
            return true;
        }

        return false;
    }

    inline bool set_mapping_type(const std::string& type_name) {
        const std::string normalized_name = normalize_type_name(type_name);

        if (normalized_name == "magic_aware") {
            mappingType = MappingType::MAGIC_AWARE;
            return true;
        } else if (normalized_name == "gaussian") {
            mappingType = MappingType::GAUSSIAN;
            return true;
        } else if (normalized_name == "random") {
            mappingType = MappingType::RANDOM;
            return true;
        }

        return false;
    }

    inline bool set_gaussian_strategy(const std::string& strategy_name) {
        const std::string normalized_name = normalize_strategy_name(strategy_name);

        if (normalized_name == "coarse") {
            gaussianStrategy = GaussianStrategy::COARSE;
            return true;
        } else if (normalized_name == "fine") {
            gaussianStrategy = GaussianStrategy::FINE;
            return true;
        }

        return false;
    }

    inline bool set_safe_passage_strategy(const std::string& strategy_name) {
        const std::string normalized_name = normalize_strategy_name(strategy_name);

        if (normalized_name == "passage") {
            safePassageStrategy = SafePassageStrategy::PASSAGE;
            return true;
        } else if (normalized_name == "passage_no_subgraphs") {
            safePassageStrategy = SafePassageStrategy::PASSAGE_NO_SUBGRAPHS;
            return true;
        } else if (normalized_name == "cube") {
            safePassageStrategy = SafePassageStrategy::CUBE;
            return true;
        } else if (normalized_name == "connectivity") {
            safePassageStrategy = SafePassageStrategy::CONNECTIVITY;
            return true;
        }

        return false;
    }

    inline void validate_non_negative_finite(double value, const char* name) {
        if (!std::isfinite(value) || value < 0.0) {
            throw std::invalid_argument(std::string(name) + " must be a finite number >= 0");
        }
    }

    inline void validate_gaussian_confidence(double value) {
        if (!std::isfinite(value) || value <= 0.0 || value >= 1.0) {
            throw std::invalid_argument("GAUSSIAN_CONFIDENCE must be a finite number in (0, 1)");
        }
    }

    inline void validate_gaussian_weights() {
        validate_non_negative_finite(magicHigh, "MAGIC_HIGH");
        validate_non_negative_finite(magicLow, "MAGIC_LOW");
        validate_non_negative_finite(cnotHigh, "CNOT_HIGH");
        validate_non_negative_finite(cnotLow, "CNOT_LOW");
        validate_non_negative_finite(mappedGaussianWeight, "MAPPED_GAUSSIAN_WEIGHT");
        validate_non_negative_finite(baseGaussianWeight, "BASE_GAUSSIAN_WEIGHT");
        validate_non_negative_finite(sizeMoltiplier, "SIZE_MOLTIPLIER");
        if (!std::isfinite(externalWeight)) {
            throw std::invalid_argument("EXTERNAL_WEIGHT must be a finite number");
        }
        validate_gaussian_confidence(gaussianConfidence);

        if (magicHigh < magicLow) {
            throw std::invalid_argument("MAGIC_HIGH must be >= MAGIC_LOW");
        }
        if (cnotHigh < cnotLow) {
            throw std::invalid_argument("CNOT_HIGH must be >= CNOT_LOW");
        }
    }


};

#endif // MAPPING_HPP
