#ifndef MAPPING_HPP
#define MAPPING_HPP

#include <unordered_map>
#include <iostream>
#include <stdexcept>
#include "graph.hpp"

// Forward declaration per evitare dipendenza completa dal typedef Circuit qui
class Circuit;

class Mapping {
    const Circuit& circuit;
    const Graph& graph;
    std::unordered_map<int, int> graph_to_circuit;

public:
    Mapping(const Circuit& c, const Graph& g) : circuit(c), graph(g) {}

    void map_qubit_to_node(int qubit, int node) {
        graph_to_circuit[qubit] = node;
    }

    int get_mapped_node(int qubit) const {
        auto it = graph_to_circuit.find(qubit);
        if (it != graph_to_circuit.end()) {
            return it->second;
        }
        throw std::runtime_error("Qubit not mapped to any node");
    }

    void print_mapping() const {
        for (const auto& pair : graph_to_circuit) {
            std::cout << "Qubit " << pair.first << " -> Node " << pair.second << "\n";
        }
    }

    void clear_mapping() {
        graph_to_circuit.clear();
    }

    // Dichiarazione solo: implementazione in src/mapping.cpp
    void mapping();

};

#endif // MAPPING_HPP
