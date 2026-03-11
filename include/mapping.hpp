#ifndef MAPPING_HPP
#define MAPPING_HPP

#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <cctype>

#include "circuit.hpp"
#include "graph.hpp"
#include "farthest_from_magic.hpp"
#include "qubit.hpp"
#include "defines.hpp"


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
        DISTANCE_FIRST,
        CENTER_SPACED,
        RANDOM
    };


    enum class MappingType {
        MAGIC_AWARE,
        HOMOGENOUS_ROWMAJOR
    };

    static vector<std::string> get_available_mapping_strategies() {
        return {"distance_first", "center_spaced", "random"};
    }

    static vector<std::string> get_available_mapping_types() {
        return {"magic_aware", "homogenous_rowmajor"};
    }


    static std::string available_mapping_strategies() {
        return "distance_first | center_spaced | random";
    } 

    static std::string available_mapping_types() {
        return "magic_aware | homogenous_rowmajor";
    }


private:
    circuit::Circuit& circuit;
    Graph& graph;
    std::unordered_map<int, int> graph_to_circuit;
    MappingStrategy mappingStrategy;
    MappingType mappingType;
    int T_lower_bound;
    int T_upper_bound;
    int maximum_iterations;
    FarthestFromMagicSelector farthest_from_magic_selector;


public:

    Mapping(circuit::Circuit& circuit, Graph& graph, const std::string& strategy_name,const std::string& type_name, int maximum_iterations) : 
    circuit(circuit), graph(graph), maximum_iterations(maximum_iterations), farthest_from_magic_selector(graph)  {
        if (!set_mapping_strategy(strategy_name)) {
            throw std::invalid_argument("Invalid mapping strategy: " + strategy_name);
        }
        if (!set_mapping_type(type_name)) {
            throw std::invalid_argument("Invalid mapping type: " + type_name);
        }
        set_thresholds();
    }



    inline void pseudo_random_mapping(Qubit* qubit, int second_qubit) {
        switch (mappingStrategy) {
            case MappingStrategy::CENTER_SPACED:
                center_spaced_mapping(qubit, second_qubit);
                return;
            case MappingStrategy::RANDOM:
                random_mapping(qubit, second_qubit);
                return;
            case MappingStrategy::DISTANCE_FIRST:
            default:
                distance_first_mapping(qubit, second_qubit);
                return;
        }
    }

    
    inline void map() {
        switch (mappingType) {
            case MappingType::MAGIC_AWARE:
                magic_aware_mapping();
                return;
            case MappingType::HOMOGENOUS_ROWMAJOR:
                homogenous_mapping_rowmajor();
                return;
            default:
                throw std::runtime_error("Invalid mapping type");
        }
    }




    inline std::string current_mapping_strategy_name() const {
        switch (mappingStrategy) {
            case MappingStrategy::DISTANCE_FIRST:
                return "distance_first";
            case MappingStrategy::CENTER_SPACED:
                return "center_spaced";
            case MappingStrategy::RANDOM:
                return "random";
            default:
                return "unknown";
        }
    }


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

    const bool mapToNeighbor(const Qubit* qubit, int node_id);


    void map_qubit_to_node(int qubit, int node);


    // ----------mapping algorithms----------

    void magic_aware_mapping();

    void homogenous_mapping_rowmajor();

private:

    void one_iteration_magic_aware_mapping(Qubit* qubit, int* iterations);
    
    void random_mapping(Qubit* qubit, int second_qubit);

    void center_spaced_mapping(Qubit* qubit, int second_qubit);

    void distance_first_mapping(Qubit* qubit, int second_qubit);




    //---------helpers---------------


    inline void set_thresholds() {
        int total_qubits = circuit.getNumQubits();
        std::cout << "\n\ntotal_qubits:" << total_qubits << "\n";
        std::cout << "T gates per qubit - Mean: " << circuit.getTMean() << ", Std: " << circuit.getTStd() << "\n";

        T_lower_bound = static_cast<int>(circuit.getTMean() - circuit.getTStd());
        T_upper_bound = static_cast<int>(circuit.getTMean() + circuit.getTStd());

        std::cout << "T_count lower bound: " << T_lower_bound << "\n";
        std::cout << "T_count upper bound: " << T_upper_bound << "\n";
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

        if (normalized_name == "distance_first") {
            mappingStrategy = MappingStrategy::DISTANCE_FIRST;
            return true;
        } else if (normalized_name == "center_spaced") {
            mappingStrategy = MappingStrategy::CENTER_SPACED;
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
        } else if (normalized_name == "homogenous_rowmajor") {
            mappingType = MappingType::HOMOGENOUS_ROWMAJOR;
            return true;
        }

        return false;
    }


};

#endif // MAPPING_HPP
