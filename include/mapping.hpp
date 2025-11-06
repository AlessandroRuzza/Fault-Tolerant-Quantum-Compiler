#ifndef MAPPING_HPP
#define MAPPING_HPP

#include <unordered_map>
#include <iostream>
#include <stdexcept>
#include "graph.hpp"
#include "farthest_from_magic.hpp"
#include "qubit.hpp"

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
        bool mapped = false;
        for (int neighbor_id : neighbors) {
            if (!graph.is_occupied(neighbor_id)) {
                map_qubit_to_node(qubit->getQubitID(), neighbor_id);
                mapped = true;
                break;
            }
        }
        if (!mapped) {
            std::cerr << "No unoccupied neighbor available for mapping qubit " << qubit->getQubitID() << ".\n";
        }
        return mapped;
    }



public:
    Mapping(circuit::Circuit& c, Graph& g) : circuit(c), graph(g) {}

    inline void map_qubit_to_node(int qubit, int node) {
        graph_to_circuit[qubit] = node;
        graph.occupy_node(node);
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

    // Dichiarazione solo: implementazione in src/mapping.cpp
    void magic_aware_mapping(int T_lower_bound, int T_upper_bound, int maximum_iterations, FarthestFromMagicSelector& farthest_from_magic_selector);

    void homogenous_mapping_rowmajor(int maxX, int maxY);

};

#endif // MAPPING_HPP
