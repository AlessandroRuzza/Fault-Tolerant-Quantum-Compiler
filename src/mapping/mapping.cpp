#include "mapping.hpp"

const bool Mapping::mapToNeighbor(
    int qubit,
    int node_id,
    int iterations,
    std::unordered_set<int>* visited_nodes
) {
    const Qubit* q = circuit.getQubit(qubit);
    if (q == nullptr) {
        throw std::runtime_error("Cannot map a null qubit pointer.");
    }

    std::unordered_set<int> local_visited_nodes;
    if (visited_nodes == nullptr) {
        local_visited_nodes.insert(node_id);
        visited_nodes = &local_visited_nodes;
    }

    const std::vector<int>& neighbors = graph.neighbors(node_id);
    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
    bool mapped = false;
    std::string last_error;
    for (int neighbor_id : neighbors) {
        if (std::find(magic_state_ids.begin(), magic_state_ids.end(), neighbor_id) != magic_state_ids.end()) {
            continue; // Never map a data qubit on a magic-state node.
        }
        if (!graph.is_occupied(neighbor_id)) {
            if (visited_nodes->find(neighbor_id) != visited_nodes->end()) {
                continue; // Avoid cycles in the current DFS branch.
            }
            visited_nodes->insert(neighbor_id);
            try {
                map_qubit_to_node(qubit, neighbor_id, iterations, visited_nodes);
                mapped = true;
                break;
            } catch (const std::exception& e) {
                last_error = e.what();
                // Keep neighbor_id in visited_nodes so we do not retry the same
                // failing candidate from a different DFS branch.
            }
        }
    }
    if (!mapped) {
        if (PRINT_MAPPING) std::cout << "No unoccupied neighbor available for mapping qubit " << qubit << ".\n";
        if (MAPPING_VERBOSE && !last_error.empty()) {
            std::cout << "Last neighbor-mapping error for qubit " << qubit << ": " << last_error << "\n";
        }
    }

    return mapped;

}




int Mapping::map_qubit_to_node(
    int qubit,
    int node,
    int iterations,
    std::unordered_set<int>* visited_nodes
) {
    const Qubit* q = circuit.getQubit(qubit);
    if (q == nullptr) {
        throw std::runtime_error("Cannot map a null qubit pointer.");
    }

    std::unordered_set<int> local_visited_nodes;
    if (visited_nodes == nullptr) {
        local_visited_nodes.insert(node);
        visited_nodes = &local_visited_nodes;
    } else {
        visited_nodes->insert(node);
    }

    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
    if (std::find(magic_state_ids.begin(), magic_state_ids.end(), node) != magic_state_ids.end()) {
        throw std::runtime_error(
            "Cannot map data qubit " + std::to_string(qubit) +
            " directly on magic-state node " + std::to_string(node) + "."
        );
    }

    if (!check_safe_passage(graph.get_node(node))) {
        if (PRINT_SAFE_PASSAGE) {
            std::cout
                << "[safe-passage] qubit=" << qubit
                << " node=" << node
                << " fallback_depth=" << iterations
                << " (candidate rejected)\n";
        }
        if (iterations > circuit.getNumQubits()) {
            throw std::runtime_error(
                "Failed to find a safe passage for qubit " + std::to_string(qubit) + " after " + std::to_string(iterations) + " iterations. Aborting mapping.\n"
            );
        }
        if (!mapToNeighbor(qubit, node, iterations + 1, visited_nodes)) {
            throw std::runtime_error(
                "Failed to map qubit " + std::to_string(qubit) +
                ": no safe neighbor found from node " + std::to_string(node) + "."
            );
        }
        const int mapped_node = get_mapped_node(qubit);
        if (mapped_node < 0) {
            throw std::runtime_error(
                "Internal error: qubit " + std::to_string(qubit) +
                " is still unmapped after neighbor fallback."
            );
        }
        return mapped_node;
    }

    std::unordered_map<int, int>::iterator already_mapped = graph_to_circuit.find(qubit);
    if (already_mapped != graph_to_circuit.end()) {
        if (already_mapped->second == node) {
            return node;
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
    return node;
}




bool has_exit_path_from_occupied(
    const Node& occupied_node,
    const std::vector<Node>& blocked_nodes,
    int width,
    int height
);


bool Mapping::_3x3_occupied(const Node& node, const std::vector<Node>& occupied_nodes) {

    bool in_3x3_of_occupied = false;
    for (const Node& occupied_node : occupied_nodes) {
        const int dx = std::abs(node.coordX - occupied_node.coordX);
        const int dy = std::abs(node.coordY - occupied_node.coordY);
        if (dx <= 1 && dy <= 1) {
            in_3x3_of_occupied = true;
            break;
        }
    }
    return !in_3x3_of_occupied;
}





bool Mapping::safe_passage(const Node& node, const std::vector<Node>& occupied_nodes, int width, int height) {
    if (width <= 0 || height <= 0) {
        return false;
    }

    std::vector<Node> occupied_after = occupied_nodes;
    bool already_present = false;
    for (const Node& occupied_node : occupied_after) {
        if (occupied_node.coordX == node.coordX && occupied_node.coordY == node.coordY) {
            already_present = true;
            break;
        }
    }
    if (!already_present) {
        occupied_after.push_back(node);
    }

    // Magic-state nodes are not valid placement cells for data qubits, so they
    // must be treated as blocked when checking escape passages.
    std::vector<Node> blocked_nodes = occupied_after;
    const auto add_blocked_if_missing = [&blocked_nodes](const Node& candidate) {
        for (const Node& blocked : blocked_nodes) {
            if (blocked.coordX == candidate.coordX && blocked.coordY == candidate.coordY) {
                return;
            }
        }
        blocked_nodes.push_back(candidate);
    };

    for (int magic_state_id : graph.get_magic_state_ids()) {
        const Node& magic_node = graph.get_node(magic_state_id);
        add_blocked_if_missing(magic_node);
    }

    for (const Node& occupied_node : occupied_after) {
        if (!has_exit_path_from_occupied(occupied_node, blocked_nodes, width, height)) {
            return false;
        }
    }

    return true;
}






bool has_exit_path_from_occupied(
    const Node& occupied_node,
    const std::vector<Node>& blocked_nodes,
    int width,
    int height
) {
    const auto is_blocked = [&blocked_nodes](int x, int y) {
        for (const Node& blocked : blocked_nodes) {
            if (blocked.coordX == x && blocked.coordY == y) {
                return true;
            }
        }
        return false;
    };

    if (occupied_node.coordX < 0 || occupied_node.coordX >= width || occupied_node.coordY < 0 || occupied_node.coordY >= height) {
        return false;
    }

    if (occupied_node.coordY == 0 && (occupied_node.coordY + 1 >= height || is_blocked(occupied_node.coordX, occupied_node.coordY + 1))) {
        return false;
    }
    if (occupied_node.coordY == height - 1 && (occupied_node.coordY - 1 < 0 || is_blocked(occupied_node.coordX, occupied_node.coordY - 1))) {
        return false;
    }
    if (occupied_node.coordX == 0 && (occupied_node.coordX + 1 >= width || is_blocked(occupied_node.coordX + 1, occupied_node.coordY))) {
        return false;
    }
    if (occupied_node.coordX == width - 1 && (occupied_node.coordX - 1 < 0 || is_blocked(occupied_node.coordX - 1, occupied_node.coordY))) {
        return false;
    }

    std::vector<char> visited(static_cast<std::size_t>(width * height), 0);
    std::vector<std::pair<int, int>> queue;
    queue.reserve(static_cast<std::size_t>(width * height));

    const auto index = [width](int x, int y) {
        return y * width + x;
    };

    const int directions[4][2] = {
        {1, 0},
        {-1, 0},
        {0, 1},
        {0, -1}
    };

    visited[static_cast<std::size_t>(index(occupied_node.coordX, occupied_node.coordY))] = 1;

    for (const auto& direction : directions) {
        const int nx = occupied_node.coordX + direction[0];
        const int ny = occupied_node.coordY + direction[1];
        if (nx < 0 || nx >= width || ny < 0 || ny >= height) {
            continue;
        }
        if (is_blocked(nx, ny)) {
            continue;
        }
        const int idx = index(nx, ny);
        if (!visited[static_cast<std::size_t>(idx)]) {
            visited[static_cast<std::size_t>(idx)] = 1;
            queue.push_back({nx, ny});
        }
    }

    if (queue.empty()) {
        return false;
    }

    for (std::size_t head = 0; head < queue.size(); ++head) {
        const int x = queue[head].first;
        const int y = queue[head].second;

        if (x == 0 || x == width - 1 || y == 0 || y == height - 1) {
            return true;
        }

        for (const auto& direction : directions) {
            const int nx = x + direction[0];
            const int ny = y + direction[1];
            if (nx < 0 || nx >= width || ny < 0 || ny >= height) {
                continue;
            }
            if (is_blocked(nx, ny)) {
                continue;
            }
            const int idx = index(nx, ny);
            if (!visited[static_cast<std::size_t>(idx)]) {
                visited[static_cast<std::size_t>(idx)] = 1;
                queue.push_back({nx, ny});
            }
        }
    }

    return false;
}
