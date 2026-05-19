#include "mapping.hpp"
#include "routing.hpp"
#include "exceptions.hpp"

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

    const std::vector<int> neighbors_vec = graph.neighbors(node_id);
    std::deque<int> neighbors(neighbors_vec.begin(), neighbors_vec.end());
    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
    bool mapped = false;
    std::string last_error;
    while (!neighbors.empty()) {
        const int neighbor_id = neighbors.front();
        neighbors.pop_front();

        if (visited_nodes->find(neighbor_id) != visited_nodes->end()) {
            continue; // Avoid cycles in the current DFS branch.
        }

        visited_nodes->insert(neighbor_id);
        if (!graph.is_occupied(neighbor_id)) {
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
        else{
            for (int far_neighbor_id : graph.neighbors(neighbor_id)) {
                neighbors.push_back(far_neighbor_id);
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

    if (!check_safe_passage(graph.get_node(node), *q)) {
        if (PRINT_SAFE_PASSAGE) {
            std::cout
                << "[safe-passage] qubit=" << qubit
                << " node=" << node
                << " fallback_depth=" << iterations
                << " (candidate rejected)\n";
        }
        if (iterations > circuit.getNumQubits()) {
            throw SafePassageException(
                "Failed to find a safe passage for qubit " + std::to_string(qubit) + " after " + std::to_string(iterations) + " iterations. Aborting mapping."
            );
        }
        if (!mapToNeighbor(qubit, node, iterations + 1, visited_nodes)) {
            throw SafePassageException(
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
    int height,
    int safe_passage_ignore_outer_layers
);

bool has_entry_path_from_border(
    const Node& border_node,
    const std::vector<Node>& blocked_nodes,
    int width,
    int height,
    int ignored_outer_layers
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


static bool can_reach_opposite_borders(
    const Node& node,
    const std::vector<Node>& blocked_nodes,
    int width,
    int height,
    int ignored_outer_layers = 0
) {
    const int layers = std::max(0, ignored_outer_layers);
    const int minX = layers,         minY = layers;
    const int maxX = width  - 1 - layers;
    const int maxY = height - 1 - layers;

    if (minX > maxX || minY > maxY) return true;

    // The two "opposite" borders are those farthest from the node in each axis.
    const int target_x = (node.coordX * 2 <= minX + maxX) ? maxX : minX;
    const int target_y = (node.coordY * 2 <= minY + maxY) ? maxY : minY;

    std::unordered_set<int> blocked_set;
    blocked_set.reserve(blocked_nodes.size());
    for (const Node& b : blocked_nodes)
        blocked_set.insert(b.coordY * width + b.coordX);

    const int dirs[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};
    std::vector<char> visited(static_cast<size_t>(width * height), 0);

    // Min-heap: prioritise cells closest to either target border.
    auto cmp = [target_x, target_y](const std::pair<int,int>& a, const std::pair<int,int>& b) {
        const int da = std::min(std::abs(a.first - target_x), std::abs(a.second - target_y));
        const int db = std::min(std::abs(b.first - target_x), std::abs(b.second - target_y));
        return da > db;
    };
    std::priority_queue<std::pair<int,int>, std::vector<std::pair<int,int>>, decltype(cmp)> queue(cmp);

    const auto in_bounds = [width, height](int x, int y) {
        return x >= 0 && x < width && y >= 0 && y < height;
    };

    // The node itself is occupied; seed from its free neighbours.
    visited[static_cast<size_t>(node.coordY * width + node.coordX)] = 1;
    for (const auto& d : dirs) {
        const int nx = node.coordX + d[0], ny = node.coordY + d[1];
        if (!in_bounds(nx, ny)) continue;
        const int idx = ny * width + nx;
        if (!blocked_set.count(idx) && !visited[static_cast<size_t>(idx)]) {
            visited[static_cast<size_t>(idx)] = 1;
            queue.push({nx, ny});
        }
    }

    bool reached_x = false, reached_y = false;
    while (!queue.empty()) {
        const auto [x, y] = queue.top();
        queue.pop();
        if (x == target_x) reached_x = true;
        if (y == target_y) reached_y = true;
        if (reached_x || reached_y) return true;
        for (const auto& d : dirs) {
            const int nx = x + d[0], ny = y + d[1];
            if (!in_bounds(nx, ny)) continue;
            const int idx = ny * width + nx;
            if (!blocked_set.count(idx) && !visited[static_cast<size_t>(idx)]) {
                visited[static_cast<size_t>(idx)] = 1;
                queue.push({nx, ny});
            }
        }
    }
    return reached_x || reached_y;
}


bool Mapping::safe_connectivity(const Node& node, const Qubit& q, const std::vector<Node>& occupied_nodes){
    // Impossible mapping
    for (const Node& blocked_node : occupied_nodes) {
        if (blocked_node.id == node.id) {
            return false;
        }
    }
    
    std::vector<Node> occupied_nodes_after_map = occupied_nodes;
    occupied_nodes_after_map.push_back(node);

    const auto pathStrategyPtr = std::make_unique<NaiveShortestPath>(graph);
    std::unordered_set<int> used_nodes;
    used_nodes.reserve(occupied_nodes_after_map.size());
    for(const Node& n : occupied_nodes_after_map){
        used_nodes.insert(n.id);
    }

    const auto path_exists = [&pathStrategyPtr, &used_nodes](const int start, const int goal) -> bool {
        Path path = pathStrategyPtr->find_shortest_path(start, goal, used_nodes);
        return !path.empty();
    };

    const int qID = q.getQubitID();
    const auto mapped_node_after_candidate = [this, qID, &node](const int qubit_id) -> int {
        if (qubit_id == qID) {
            return node.id;
        }
        return get_mapped_node(qubit_id);
    };

    const auto has_escape_path = [this, &occupied_nodes_after_map](const int node) -> bool {
        const Node& n = graph.get_node(node);
        const int maxX = graph.getMaxX();
        const int maxY = graph.getMaxY();
        const int eps = safe_passage_ignore_outer_layers;
        return can_reach_opposite_borders(n, occupied_nodes_after_map, maxX+1, maxY+1, safe_passage_ignore_outer_layers);
        
        if (n.coordX <= eps || n.coordX >= maxX - eps || n.coordY <= eps || n.coordY >= maxY - eps) {
            return has_entry_path_from_border(n, occupied_nodes_after_map, maxX + 1, maxY + 1, safe_passage_ignore_outer_layers);
        }
        return has_exit_path_from_occupied(n, occupied_nodes_after_map, maxX + 1, maxY + 1, safe_passage_ignore_outer_layers);
    };

    std::unordered_set<int> cnot_nodes_requiring_access;
    for (const Gate& gate : cnot_gates) {
        const int node1 = mapped_node_after_candidate(gate.qubits[0]);
        const int node2 = mapped_node_after_candidate(gate.qubits[1]);

        if(node1 < 0 && node2 < 0) continue; // gate fully unmapped

        if (node1 >= 0 && node2 >= 0) {
            if (!path_exists(node1, node2)) {
                return false; // This placement is blocking that gate path
            }
        }
        else{ // either node1 or node2 are mapped (>= 0)
            if (node1 >= 0)
                cnot_nodes_requiring_access.insert(node1);
            else 
                cnot_nodes_requiring_access.insert(node2);
        }
    }

    // Ensure partially mapped CNOTs have escape path
    for (const int mapped_node : cnot_nodes_requiring_access) {
        if (!has_escape_path(mapped_node)) {
            if (PRINT_SAFE_PASSAGE) {
                std::cout << "CANDIDATE REJECTED " << node.id
                          << ": it blocks CNOT connectivity for node "
                          << mapped_node << "\n";
            }
            return false;
        }
    }

    bool has_unmapped_t_qubit = false;
    for (const Gate& gate : t_gates) {
        if (mapped_node_after_candidate(gate.qubits[0]) < 0) {
            has_unmapped_t_qubit = true;
            break;
        }
    }

    if (has_unmapped_t_qubit) {
        bool has_open_magic_entry = false;
        for (const int magic : graph.get_magic_state_ids()) {
            for (const int neighbor : graph.neighbors(magic)) {
                if (used_nodes.count(neighbor) == 0) {
                    has_open_magic_entry = true;
                    break;
                }
            }
            if (has_open_magic_entry) {
                break;
            }
        }

        if (!has_open_magic_entry) {
            if (PRINT_SAFE_PASSAGE) {
                std::cout << "CANDIDATE REJECTED " << node.id
                          << ": it blocks magic-state access for unmapped T gates\n";
            }
            return false;
        }
    }

    // Ensure all mapped qubits can reach a magic state if they need
    std::unordered_set<int> ensured_qubits;
    ensured_qubits.reserve(circuit.getNumQubits());
    for(const Gate& gate : t_gates){
        if(ensured_qubits.count(gate.qubits[0])) continue;

        int loc_node = mapped_node_after_candidate(gate.qubits[0]);
        if(loc_node < 0){
            ensured_qubits.insert(gate.qubits[0]);
            continue; // Unmapped qubit
        }
        bool canReachMagic = false;
        for(int magic : graph.get_magic_state_ids()){
            if (path_exists(loc_node, magic)) {
                canReachMagic = true;
                ensured_qubits.insert(gate.qubits[0]);
                break; 
            }
        }
        if(!canReachMagic){
            if (PRINT_SAFE_PASSAGE) {
                std::cout << "CANDIDATE REJECTED " << node.id
                          << ": it blocks magic-state T-gate access for node "
                          << loc_node << "\n";
            }
            return false;

        } 
    }

    return true;
}


bool Mapping::safe_passage(const Node& node, const std::vector<Node>& occupied_nodes) {
    int width = graph.getMaxX() + 1;
    int height = graph.getMaxY() + 1;
    
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

    for (const Node& occupied_node : occupied_after) {
        if (!has_exit_path_from_occupied(occupied_node, blocked_nodes, width, height, safe_passage_ignore_outer_layers)) {
            return false;
        }
    }

    return true;
}

bool Mapping::safe_passage_no_subgraphs(const Node& node, const std::vector<Node>& occupied_nodes) {
    int width = graph.getMaxX() + 1;
    int height = graph.getMaxY() + 1;
    auto node_cmp = [width, height](const Node& a, const Node& b) {
        int da = std::min({a.coordX, width - 1 - a.coordX, a.coordY, height - 1 - a.coordY});
        int db = std::min({b.coordX, width - 1 - b.coordX, b.coordY, height - 1 - b.coordY});
        return da > db;
    };
    std::priority_queue<Node, std::vector<Node>, decltype(node_cmp)> node_queue(node_cmp);
    node_queue.push(node);
    std::unordered_set<int> visited_ids;

    const auto magic_ids = graph.get_magic_state_ids();
    std::unordered_set<int> magic_ids_set(magic_ids.begin(), magic_ids.end());

    int num_touching_borders = 0;

    for (Node current = node_queue.top();
         !node_queue.empty() && num_touching_borders < 2;
         node_queue.pop(), current = node_queue.empty() ? current : node_queue.top()) {

        if (visited_ids.count(current.id) > 0) continue;

        for (int dy = -1; dy <= 1; ++dy) {
            for (int dx = -1; dx <= 1; ++dx) {
                if (dx == 0 && dy == 0) continue; // salta il nodo centrale

                const int nx = current.coordX + dx;  // era node.coordX
                const int ny = current.coordY + dy;  // era node.coordY

                if (nx < 0 || nx > graph.getMaxX() || ny < 0 || ny > graph.getMaxY()) continue;

                const int nid = ny * width + nx;

                if (visited_ids.count(nid) == 0 && (graph.is_occupied(nid) || magic_ids_set.count(nid) > 0)) {
                    node_queue.push(graph.get_node(nid));
                }
            }
        }
            // Check if the current node touches the border of the lattice
        if (current.coordX == 0 || current.coordX == graph.getMaxX() || current.coordY == 0 || current.coordY == graph.getMaxY()) {
            for (int vid : visited_ids) {
                const Node& v = graph.get_node(vid);
                if (v.coordX == 0 || v.coordX == graph.getMaxX() ||
                    v.coordY == 0 || v.coordY == graph.getMaxY()) {
                    if (std::abs(v.coordX - current.coordX) > 1 ||
                        std::abs(v.coordY - current.coordY) > 1) {
                        num_touching_borders++;
                        break;
                    }
                }
            }
        }
        visited_ids.insert(current.id);
    }

    if (num_touching_borders >= 2) {
        return false;
    }

    // Suffocation check: placing `node` must not strip every free neighbour from any
    // already-mapped data qubit, and must leave at least one magic state reachable
    // (i.e. with at least one free neighbour) so future T gates can still be routed.
    std::unordered_set<int> blocked_after;
    blocked_after.reserve(occupied_nodes.size() + magic_ids.size() + 1);
    for (const Node& on : occupied_nodes) {
        blocked_after.insert(on.id);
    }
    for (int mid : magic_ids) {
        blocked_after.insert(mid);
    }
    blocked_after.insert(node.id);

    // Compute 4-connected free-cell components (cells that are not occupied,
    // not magic, and not the candidate). A qubit is "useful" only if at least
    // one of its free 4-neighbours belongs to the *largest* free component;
    // otherwise the placement traps the qubit in an off-main pocket.
    const int total_cells = width * height;
    std::vector<int> component_of(static_cast<std::size_t>(total_cells), -1);
    std::vector<int> component_size;
    {
        const int dx_4[4] = {1, -1, 0, 0};
        const int dy_4[4] = {0, 0, 1, -1};
        for (int id = 0; id < total_cells; ++id) {
            if (blocked_after.count(id) > 0) continue;
            if (component_of[id] >= 0) continue;
            const int label = static_cast<int>(component_size.size());
            int size = 0;
            std::queue<int> bfs;
            bfs.push(id);
            component_of[id] = label;
            while (!bfs.empty()) {
                const int cur = bfs.front();
                bfs.pop();
                ++size;
                const int cx = cur % width;
                const int cy = cur / width;
                for (int i = 0; i < 4; ++i) {
                    const int nx = cx + dx_4[i];
                    const int ny = cy + dy_4[i];
                    if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
                    const int nid = ny * width + nx;
                    if (blocked_after.count(nid) > 0) continue;
                    if (component_of[nid] >= 0) continue;
                    component_of[nid] = label;
                    bfs.push(nid);
                }
            }
            component_size.push_back(size);
        }
    }
    const int max_component_size =
        component_size.empty() ? 0 : *std::max_element(component_size.begin(), component_size.end());

    const auto reaches_largest_component = [&](int qubit_id) -> bool {
        for (int nbr : graph.neighbors(qubit_id)) {
            if (blocked_after.count(nbr) > 0) continue;
            const int c = component_of[nbr];
            if (c >= 0 && component_size[c] == max_component_size) {
                return true;
            }
        }
        return false;
    };

    if (max_component_size > 0 && !reaches_largest_component(node.id)) {
        if (PRINT_SAFE_PASSAGE) {
            std::cout << "CANDIDATE REJECTED " << node.id
                      << ": placing it here leaves it off the main free region\n";
        }
        return false;
    }

    for (const Node& on : occupied_nodes) {
        if (magic_ids_set.count(on.id) > 0) continue;
        if (max_component_size > 0 && !reaches_largest_component(on.id)) {
            if (PRINT_SAFE_PASSAGE) {
                std::cout << "CANDIDATE REJECTED " << node.id
                          << ": it cuts occupied node " << on.id << " off the main free region\n";
            }
            return false;
        }
    }

    if (!magic_ids.empty()) {
        bool any_magic_accessible = false;
        for (int mid : magic_ids) {
            for (int nid : graph.neighbors(mid)) {
                if (blocked_after.count(nid) == 0) {
                    any_magic_accessible = true;
                    break;
                }
            }
            if (any_magic_accessible) break;
        }
        if (!any_magic_accessible) {
            if (PRINT_SAFE_PASSAGE) {
                std::cout << "CANDIDATE REJECTED " << node.id
                          << ": it blocks every magic state\n";
            }
            return false;
        }
    }

    return true;
}

bool has_exit_path_from_occupied(
    const Node& occupied_node,
    const std::vector<Node>& blocked_nodes,
    int width,
    int height,
    int safe_passage_ignore_outer_layers
) {
    int min_x = 0;
    int min_y = 0;
    int max_x = width - 1;
    int max_y = height - 1;

    const int ignored_outer_layers = std::max(0, safe_passage_ignore_outer_layers);
    min_x += ignored_outer_layers;
    min_y += ignored_outer_layers;
    max_x -= ignored_outer_layers;
    max_y -= ignored_outer_layers;

    const auto is_inside_effective_area = [min_x, min_y, max_x, max_y](int x, int y) {
        return x >= min_x && x <= max_x && y >= min_y && y <= max_y;
    };

    const auto is_blocked = [&blocked_nodes](int x, int y) {
        for (const Node& blocked : blocked_nodes) {
            if (blocked.coordX == x && blocked.coordY == y) {
                return true;
            }
        }
        return false;
    };

    if (!is_inside_effective_area(occupied_node.coordX, occupied_node.coordY)) {
        // This node belongs to the ignored outer layers.
        return true;
    }

    const int effective_width = max_x - min_x + 1;
    const int effective_height = max_y - min_y + 1;
    std::vector<char> visited(static_cast<std::size_t>(effective_width * effective_height), 0);
    std::vector<std::pair<int, int>> queue;
    queue.reserve(static_cast<std::size_t>(effective_width * effective_height));

    const auto index = [min_x, min_y, effective_width](int x, int y) {
        return (y - min_y) * effective_width + (x - min_x);
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
        if (!is_inside_effective_area(nx, ny)) {
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

        if (x == min_x || x == max_x || y == min_y || y == max_y) {
            return true;
        }

        for (const auto& direction : directions) {
            const int nx = x + direction[0];
            const int ny = y + direction[1];
            if (!is_inside_effective_area(nx, ny)) {
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

bool has_entry_path_from_border(
    const Node& border_node,
    const std::vector<Node>& blocked_nodes,
    int width,
    int height,
    int ignored_outer_layers
) {
    const int layers = std::max(0, ignored_outer_layers);
    const int min_x = layers;
    const int min_y = layers;
    const int max_x = width - 1 - layers;
    const int max_y = height - 1 - layers;

    // No target region exists — the ignored layers consume the entire grid.
    if (min_x > max_x || min_y > max_y) return false;

    const int bx = border_node.coordX;
    const int by = border_node.coordY;

    if (bx < 0 || bx >= width || by < 0 || by >= height) return false;

    // Node is already in the target region — entry path trivially exists.
    if (bx >= min_x && bx <= max_x && by >= min_y && by <= max_y) return true;

    std::unordered_set<int> blocked_set;
    blocked_set.reserve(blocked_nodes.size());
    for (const Node& n : blocked_nodes) {
        blocked_set.insert(n.coordY * width + n.coordX);
    }

    const auto is_blocked = [&blocked_set, width](int x, int y) {
        return blocked_set.count(y * width + x) != 0;
    };

    const auto is_inside_grid = [width, height](int x, int y) {
        return x >= 0 && x < width && y >= 0 && y < height;
    };

    std::vector<char> visited(static_cast<std::size_t>(width * height), 0);
    std::vector<std::pair<int, int>> queue;
    queue.reserve(static_cast<std::size_t>(width * height));

    const int directions[4][2] = {{1,0},{-1,0},{0,1},{0,-1}};

    visited[static_cast<std::size_t>(by * width + bx)] = 1;

    for (const auto& dir : directions) {
        const int nx = bx + dir[0];
        const int ny = by + dir[1];
        if (!is_inside_grid(nx, ny)) continue;
        if (is_blocked(nx, ny)) continue;
        const int idx = ny * width + nx;
        if (!visited[static_cast<std::size_t>(idx)]) {
            visited[static_cast<std::size_t>(idx)] = 1;
            queue.push_back({nx, ny});
        }
    }

    if (queue.empty()) return false;

    for (std::size_t head = 0; head < queue.size(); ++head) {
        const int x = queue[head].first;
        const int y = queue[head].second;

        if (x >= min_x && x <= max_x && y >= min_y && y <= max_y) {
            return true;
        }

        for (const auto& dir : directions) {
            const int nx = x + dir[0];
            const int ny = y + dir[1];
            if (!is_inside_grid(nx, ny)) continue;
            if (is_blocked(nx, ny)) continue;
            const int idx = ny * width + nx;
            if (!visited[static_cast<std::size_t>(idx)]) {
                visited[static_cast<std::size_t>(idx)] = 1;
                queue.push_back({nx, ny});
            }
        }
    }

    return false;
}
