#ifndef MAPPING_HPP
#define MAPPING_HPP

#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>

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

// Forward declaration per evitare dipendenza completa dalla definizione di Circuit
namespace circuit {
    class Circuit;
}

class Mapping {

private:
    circuit::Circuit& circuit;
    Graph& graph;
    std::unordered_map<int, int> graph_to_circuit;

    const bool mapToNeighbor(const Qubit* qubit, int node_id){
        const std::vector<int>& neighbors = graph.neighbors(node_id);
        const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
        bool mapped = false;
        for (int neighbor_id : neighbors) {
            if (std::find(magic_state_ids.begin(), magic_state_ids.end(), neighbor_id) != magic_state_ids.end()) {
                continue; // Never map a data qubit on a magic-state node.
            }
            if (!graph.is_occupied(neighbor_id)) {
                map_qubit_to_node(qubit->getQubitID(), neighbor_id);
                mapped = true;
                break;
            }
        }
        if (!mapped) {
            if (PRINT_MAPPING) std::cout << "No unoccupied neighbor available for mapping qubit " << qubit->getQubitID() << ".\n";
        }

        return mapped;

    }



public:
    enum class MappingStrategy {
        DISTANCE_FIRST,
        CENTER_SPACED,
        RANDOM
    };

    static MappingStrategy mapping_strategy;
    static bool set_mapping_strategy(const std::string& strategy_name);
    static std::string current_mapping_strategy_name();
    static std::string available_mapping_strategies();

    Mapping(circuit::Circuit& c, Graph& g) : circuit(c), graph(g) {}

    inline void map_qubit_to_node(int qubit, int node) {
        graph_to_circuit[qubit] = node;
        graph.occupy_node(node);
        if (PRINT_MAPPING) std::cout << "Mapped qubit " << qubit << " to node " << node << "\n";
        if (PRINT_MAPPING_GRAPH) graph.print_rectangular();
    }

    //-----getters---------

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


    // ----------mapping algorithms----------

    // Dichiarazione solo: implementazione in src/mapping/*.cpp
    void magic_aware_mapping(int T_lower_bound, int T_upper_bound, int maximum_iterations, FarthestFromMagicSelector& farthest_from_magic_selector);

    void homogenous_mapping_rowmajor(int maxX, int maxY);

private:
    static std::string normalize_strategy_name(const std::string& strategy_name);
    static std::string strategy_to_string(MappingStrategy strategy);

    void one_iteration_magic_aware_mapping(Qubit* qubit, int T_lower_bound, int T_upper_bound, FarthestFromMagicSelector& farthest_from_magic_selector, int* c);
    
    void pseudo_random_mapping(Qubit* qubit, int second_qubit);

    void random_mapping(Qubit* qubit, int second_qubit);

    void center_spaced_mapping(Qubit* qubit, int second_qubit);

    void distance_first_mapping(Qubit* qubit, int second_qubit);

};

#endif // MAPPING_HPP
