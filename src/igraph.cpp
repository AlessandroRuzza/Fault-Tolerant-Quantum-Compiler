#include "igraph.hpp"

#include <climits>
#include <cstdio>
#include <iostream>
#include <limits>

    // Print the adjacency list with node coordinates
    void IGraph::print() const {
        for (const Node& node : nodes) {
            std::cout << node.id << " (" << node.coordX << "," << node.coordY << "):";
            for (int v : neighbors(node.id)) {
                std::cout << " " << v;
            }
            std::cout << std::endl;
        }
    }


        
    void IGraph::print_rectangular() const {
        // Determine grid dimensions
        int maxX = 0, maxY = 0;
        for (const Node& node : nodes) {
            if (node.coordX > maxX) maxX = node.coordX;
            if (node.coordY > maxY) maxY = node.coordY;
        }

        // Print the grid with fixed-width columns
        for (int y = 0; y <= maxY; ++y) {
            for (int x = 0; x <= maxX; ++x) {
                const int node_id = get_node_by_coordinates(x, y).id;
                if (is_occupied(node_id)) {
                    // Print occupied nodes in red
                    std::cout << "\033[1;31m"; // ANSI escape code for red
                    printf("%3d", node_id);
                    std::cout << "\033[0m"; // Reset color
                } else {
                    printf("%3d", node_id);
                }
                if (std::find(magic_states_ids.begin(), magic_states_ids.end(), node_id) != magic_states_ids.end()) {
                    std::cout << "(M)";
                }
                std::cout << " ";
            }
            std::cout << std::endl;
        }
    }



    // Add a node with coordinates
    void IGraph::add_node(int id, int x, int y) {
        // Resize vector if necessary to accommodate the id
        if (id >= nodes.size()) {
            nodes.resize(id + 1, Node(-1, 0, 0)); // Initialize with sentinel values
        }
        // Only add if not already present
        if (nodes[id].id == -1) {
            nodes[id] = Node(id, x, y);
            node_count++;
        }
    }

    void IGraph::add_node(int id) {
        add_node(id, 0, 0); // Default coordinates (0,0) if not specified
    }



    

    const int IGraph::getNearestMagicStateId(int node_id) const {
        if (magic_states_ids.empty()) {
            throw std::runtime_error("No magic states available in the graph.");
        }

        const Node& start_node = get_node(node_id);
        int nearest_magic_state = -1;
        double min_distance = std::numeric_limits<double>::max();

        for (Node magic_node : get_magic_states()) {
            double distance = std::sqrt(std::pow(start_node.coordX - magic_node.coordX, 2) +
                                        std::pow(start_node.coordY - magic_node.coordY, 2));
            if (distance < min_distance) {
                min_distance = distance;
                nearest_magic_state = magic_node.id;
            }
        }

        return nearest_magic_state;
    }

    const Node& IGraph::getNearestMagicState(const Node& node) const {
        int nearest_id = getNearestMagicStateId(node.id);
        return get_node(nearest_id);
    }





    const int IGraph::getBestMagicStateId() {
        int best_magic_state_id = -1;
        int min_mapped_qubits = INT_MAX;
        for (const Node& magic_state : this->get_magic_states()) {
            int count = mapped_magic_states[magic_state.id];
            if (count < min_mapped_qubits) {
                min_mapped_qubits = count;
                best_magic_state_id = magic_state.id;
            }
        }
        return best_magic_state_id;
    }




    // const void update_magic_states_score(int magic_state_id) {
    //     // In this simple implementation, the score is just the count of mapped qubits.
    //     // More complex heuristics could be implemented here if needed.

        
    // }

    void IGraph::increment_mapped_magic_state(int magic_state_id) {
        mapped_magic_states[magic_state_id]++;
        //update_magic_states_score(magic_state_id);


    }
