



#include "mapping.hpp"

    const bool Mapping::mapToNeighbor(const Qubit* qubit, int node_id){
        if (qubit == nullptr) {
            throw std::runtime_error("Cannot map a null qubit pointer.");
        }
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





    void Mapping::map_qubit_to_node(int qubit, int node) {
        std::unordered_map<int, int>::iterator already_mapped = graph_to_circuit.find(qubit);
        if (already_mapped != graph_to_circuit.end()) {
            if (already_mapped->second == node) {
                return;
            }
            throw std::runtime_error(
                "Qubit " + std::to_string(qubit) + " already mapped to node " +
                std::to_string(already_mapped->second) + ", cannot remap to node " +
                std::to_string(node) + "."
            );
        }
        if (graph.is_occupied(node)) {
            throw std::runtime_error(
                "Node " + std::to_string(node) + " is already occupied."
            );
        }
        graph_to_circuit[qubit] = node;
        graph.occupy_node(node);
        if (PRINT_MAPPING) std::cout << "Mapped qubit " << qubit << " to node " << node << "\n";
        if (PRINT_MAPPING_GRAPH) graph.print_rectangular();
    }
