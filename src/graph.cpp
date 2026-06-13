#include "graph.hpp"
#include "defines.hpp"
#include <cctype>
#include <cmath>
#include <random>

const std::vector<int> emptyVec;

Graph::MagicStatePlacementStrategy Graph::parse_magic_state_placement_strategy(
    const std::string& strategy_name
) {
    std::string normalized = strategy_name;
    std::transform(normalized.begin(), normalized.end(), normalized.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    std::replace(normalized.begin(), normalized.end(), '-', '_');

    if (normalized == "rightrow") {
        normalized = "right_row";
    }

    if (normalized == "right_row") {
        return MagicStatePlacementStrategy::RIGHT_ROW;
    }
    if (normalized == "center_circle") {
        return MagicStatePlacementStrategy::CENTER_CIRCLE;
    }

    throw std::invalid_argument(
        "Invalid MagicStatePlacementStrategy '" + strategy_name +
        "'. Allowed values: " + available_magic_state_placement_strategies() + "."
    );
}

void Graph::set_magic_state_placement_strategy(const std::string& strategy_name) {
    magic_state_placement_strategy = parse_magic_state_placement_strategy(strategy_name);
}

// Node constructor implementation
Node::Node(int node_id, int x, int y) : id(node_id), coordX(x), coordY(y) {}


// Add a directed edge from u to v
void Graph::add_edge(int u, int v) {
    if (u < 0 || v < 0) return;
    
    // Ensure nodes exist
    if (u >= nodes.size()) {
        add_node(u);
    } else if (nodes[u].id == -1) {
        add_node(u);
    }
    if (v >= nodes.size()) {
        add_node(v);
    } else if (nodes[v].id == -1) {
        add_node(v);
    }

    // Update node's neighbor list
    Node& u_node = get_node(u);
    if (std::find(u_node.neighbors.begin(), u_node.neighbors.end(), v) == u_node.neighbors.end()) {
        u_node.neighbors.push_back(v);
    }
    Node& v_node = get_node(v);
    if (std::find(v_node.neighbors.begin(), v_node.neighbors.end(), u) == v_node.neighbors.end()) {
        v_node.neighbors.push_back(u);
    }
    
    node_count = std::max(node_count, std::max(u, v) + 1);
}



// Static method to construct a Graph from JSON file
void Graph::from_json(const std::string& filename) {
        std::ifstream f(filename);
        if (!f) {
            std::cerr << "file non trovato: " << filename << "\n";
            return; // return empty graph on failure
            // throw std::runtime_error("Could not open file: " + filename);
        }
        
        json j = json::parse(f);

        // // STAMPA IL JSON RAW PER DEBUG
        // std::cout << "=== JSON RAW CONTENT ===\n";
        // std::cout << j.dump(2) << std::endl; // indent=2 per pretty print
        // std::cout << "========================\n";

        // Stampa anche i tipi e le chiavi principali
        std::cout << "JSON type: " << j.type_name() << std::endl;
        std::cout << "Keys in JSON object:\n";
        if (j.is_object()) {
            for (auto it = j.begin(); it != j.end(); ++it) {
                std::cout << "  - \"" << it.key() << "\" : " << it.value().type_name() << std::endl;
            }
        }
        std::cout << "------------------------\n";

        std::cout << "Parsing graph from JSON file: " << filename << "\n";

        if(!j.contains("type")){
            std::cerr << "type not specified!\n";
            return;
        }

        // Handle generic graph type with fields at the root
        if (j["type"] == "generic") {
            int num_nodes = j.value("num_nodes", 0);
            // Add nodes with default coordinates
            for (int i = 0; i < num_nodes; ++i) {
                this->add_node(i);
            }
            // Set coordinates if present
            if (j.contains("coordinates")) {
                for (auto it = j["coordinates"].begin(); it != j["coordinates"].end(); ++it) {
                    int node_id = std::stoi(it.key());
                    const auto& coords = it.value();
                    if (coords.is_array() && coords.size() >= 2) {
                        int x = static_cast<int>(coords[0]);
                        int y = static_cast<int>(coords[1]);
                        this->add_node(node_id, x, y);
                    }
                }
            }
            else{
                std::cerr << "node coordinates not specified!\n";
                return;
            }

            // Add edges from connectivity
            if (j.contains("connectivity")) {
                for (const auto& edge : j["connectivity"]) {
                    if (edge.is_array() && edge.size() == 2) {
                        int u = edge[0];
                        int v = edge[1];
                        this->add_edge(u, v);
                    }
                }
            } 
            else{
                std::cerr << "node connectivity not specified!\n";
                return;
            }
        }
        else
        if(j["type"] == "rectangular") {
            std::cout << "Creating rectangular grid graph...\n";
            int rows = j.value("rows", 0);
            int cols = j.value("cols", 0);
            bool diagonal = j.value("diagonal_connectivity", false);
            if (rows > 0 && cols > 0) {
                // Create grid nodes
                for (int r = 0; r < rows; ++r) {
                    for (int c = 0; c < cols; ++c) {
                        int node_id = r * cols + c;
                        this->add_node(node_id, c, r); // x = col, y = row
                    }
                }
                // Create edges
                for (int r = 0; r < rows; ++r) {
                    for (int c = 0; c < cols; ++c) {
                        int node_id = r * cols + c;
                        // Right neighbor
                        if (c + 1 < cols) this->add_edge(node_id, node_id + 1);
                        // Bottom neighbor
                        if (r + 1 < rows) this->add_edge(node_id, node_id + cols);
                        if (diagonal) {
                            // Bottom-right neighbor
                            if (c + 1 < cols && r + 1 < rows) this->add_edge(node_id, node_id + cols + 1);
                            // Bottom-left neighbor
                            if (c - 1 >= 0 && r + 1 < rows) this->add_edge(node_id, node_id + cols - 1);
                        }
                    }
                }
            }
            else{
                std::cerr << "rows or cols not specified!\n";
                return;
            }
            std::cout << this->get_node_count() << " nodes created in rectangular grid.\n";
        }


        if(j.contains("magic states")){
            if(j["magic states"].is_array()){
                std::unordered_set<int> seen_magic_ids;
                for (const auto& magic_state_entry : j["magic states"]) {
                    if (!magic_state_entry.is_number_integer()) {
                        std::cerr << "magic states must be an array of integer node ids!\n";
                        return;
                    }

                    const int magic_state_id = magic_state_entry.get<int>();
                    if (magic_state_id < 0 || magic_state_id >= this->get_node_count()) {
                        std::cerr << "magic state id out of range: " << magic_state_id << "\n";
                        return;
                    }
                    if (this->get_node(magic_state_id).id == -1) {
                        std::cerr << "magic state id does not correspond to an existing node: "
                                  << magic_state_id << "\n";
                        return;
                    }

                    if (seen_magic_ids.insert(magic_state_id).second) {
                        this->get_node(magic_state_id).occupied = true;
                        this->magic_states_ids.push_back(magic_state_id);
                    }
                }
        }
            else{
                std::cerr << "magic states not specified as array of ints!\n";
                return;
            }
        }
        else{
            std::cerr << "magic states not specified!\n";
            return;
        }
    }

        
void Graph::add_magic_states_rightrow(const std::vector<int>& magic_state_ids, int height, int width) {
    int placed_magic_states = 0;
    for (int row = 0; row < height && placed_magic_states < number_of_magic_states; row++) {
        const int magic_id = row * width + (width - 1);
        magic_states_ids.push_back(magic_id);
        placed_magic_states++;
    }

    if (placed_magic_states < number_of_magic_states) {
        std::cerr
            << "warning: requested " << number_of_magic_states
            << " magic states with RIGHT_ROW, but only " << placed_magic_states
            << " positions are available.\n";
    }
}

void Graph::add_magic_states_center_circle(
    const std::vector<int>&,
    int height,
    int width,
    int number_of_magic_states,
    double border_distance_percentage
) {
    if (height <= 0 || width <= 0 || number_of_magic_states <= 0) {
        return;
    }

    const int center_row = height / 2;
    const int center_col = width / 2;
    const int center_id = center_row * width + center_col;
    const int max_inset = std::max(0, (std::min(height, width) - 1) / 2);

    std::unordered_set<int> used_magic_ids(magic_states_ids.begin(), magic_states_ids.end());

    auto try_add_magic_id = [&](int magic_id) -> bool {
        if (magic_states_ids.size() >= static_cast<size_t>(number_of_magic_states)) return false;
        if (magic_id < 0 || magic_id >= height * width) return false;
        if (used_magic_ids.insert(magic_id).second) {
            magic_states_ids.push_back(magic_id);
            return true;
        }
        return false;
    };

    auto needs_more = [&]() {
        return magic_states_ids.size() < static_cast<size_t>(number_of_magic_states);
    };

    try_add_magic_id(center_id);
    if (!needs_more()) return;

    auto build_ring = [&](int inset) -> std::vector<int> {
        std::vector<int> ring;
        if (inset < 0 || inset > max_inset) return ring;
        const int top = inset;
        const int bottom = height - 1 - inset;
        const int left = inset;
        const int right = width - 1 - inset;
        if (top > bottom || left > right) return ring;
        if (top == bottom && left == right) {
            ring.push_back(top * width + left);
            return ring;
        }
        for (int col = left; col <= right; ++col) ring.push_back(top * width + col);
        for (int row = top + 1; row <= bottom; ++row) ring.push_back(row * width + right);
        if (bottom > top) {
            for (int col = right - 1; col >= left; --col) ring.push_back(bottom * width + col);
        }
        if (right > left) {
            for (int row = bottom - 1; row > top; --row) ring.push_back(row * width + left);
        }
        return ring;
    };

    // Spread the magic states evenly around the ring (circle) instead of
    // filling consecutive cells from the start. "One yes, one no" is enforced
    // as a *minimum* separation: we cap the count at every-other-cell (n/2) so
    // the even-distribution step is always >= 2, keeping neighbors at least one
    // empty cell apart. With few magic states this distributes them around the
    // whole circle rather than clustering them on one side.
    auto place_alternating = [&](const std::vector<int>& ring) {
        const size_t n = ring.size();
        if (n == 0 || !needs_more()) return;
        const size_t remaining =
            static_cast<size_t>(number_of_magic_states) - magic_states_ids.size();
        const size_t max_on_ring = std::max<size_t>(1, n / 2);
        const size_t to_place = std::min(remaining, max_on_ring);
        for (size_t k = 0; k < to_place && needs_more(); ++k) {
            try_add_magic_id(ring[(k * n) / to_place]);
        }
    };

    const double clamped_percentage = std::clamp(border_distance_percentage, 0.0, 100.0);
    int first_inset = static_cast<int>(std::ceil((std::min(height, width) * clamped_percentage) / 100.0));
    first_inset = std::clamp(first_inset, 0, max_inset);

    place_alternating(build_ring(first_inset));
    if (!needs_more()) return;

    // Second ring: pick the side of the first ring (toward center vs. toward
    // exterior) with more free space and place a ring halfway between that
    // edge and the first ring, keeping at least one cell of separation.
    const int distance_to_center = max_inset - first_inset;
    const int distance_to_exterior = first_inset;

    int second_inset = -1;
    if (distance_to_center >= distance_to_exterior && distance_to_center >= 1) {
        second_inset = (first_inset + max_inset) / 2;
        if (second_inset - first_inset < 1) second_inset = first_inset + 1;
        if (second_inset > max_inset) second_inset = -1;
    } else if (distance_to_exterior >= 1) {
        second_inset = first_inset / 2;
        if (first_inset - second_inset < 1) second_inset = first_inset - 1;
        if (second_inset < 0) second_inset = -1;
    }

    if (second_inset >= 0 && second_inset != first_inset) {
        place_alternating(build_ring(second_inset));
        if (!needs_more()) return;
    }

    // Random fill: Chebyshev distance >= 2 from every existing magic state
    // (no edge- or diagonal-adjacency to any other magic state).
    auto far_enough = [&](int row, int col) {
        for (int magic_id : magic_states_ids) {
            const int mrow = magic_id / width;
            const int mcol = magic_id % width;
            if (std::max(std::abs(mrow - row), std::abs(mcol - col)) < 2) return false;
        }
        return true;
    };

    std::vector<int> candidates;
    candidates.reserve(static_cast<size_t>(width) * height);
    for (int row = 0; row < height; ++row) {
        for (int col = 0; col < width; ++col) {
            candidates.push_back(row * width + col);
        }
    }

    static thread_local std::mt19937 rng{std::random_device{}()};
    std::shuffle(candidates.begin(), candidates.end(), rng);
    for (int cand : candidates) {
        if (!needs_more()) break;
        if (used_magic_ids.count(cand)) continue;
        if (!far_enough(cand / width, cand % width)) continue;
        try_add_magic_id(cand);
    }
}


// Create a rectangular grid graph with magic states
void Graph::create_rectangular_with_magic_states(
    int height,
    int width
) {
    // Create all grid nodes with explicit coordinates.
    for (int row = 0; row < height; row++) {
        for (int col = 0; col < width; col++) {
            const int id = row * width + col;
            this->add_node(id, col, row);
        }
    }

    if (magic_state_placement_strategy == MagicStatePlacementStrategy::RIGHT_ROW) {
        this->add_magic_states_rightrow(this->magic_states_ids, height, width);
    } else if (magic_state_placement_strategy == MagicStatePlacementStrategy::CENTER_CIRCLE) {
        this->add_magic_states_center_circle(
            this->magic_states_ids,
            height,
            width,
            number_of_magic_states,
            border_distance_percentage
        );
    }

    // Occupy all graph nodes that have magic states
    for(int magic_id : magic_states_ids){
        occupy_node(magic_id);
    }

    // Add horizontal and vertical edges in the grid.
    for (int row = 0; row < height; row++) {
        for (int col = 0; col < width; col++) {
            int id = row * width + col;
            
            // Right neighbor
            if (col < width - 1) {
                this->add_edge(id, id + 1);
            }
            
            // Bottom neighbor
            if (row < height - 1) {
                this->add_edge(id, id + width);
            }
        }
    }
}

void Graph::write_file(const std::string& path) const {
    std::filesystem::path output_path(path);
    if (output_path.has_parent_path()) {
        std::filesystem::create_directories(output_path.parent_path());
    }

    std::ofstream ofs(output_path);
    if (!ofs) throw std::runtime_error("failed to open file for writing: " + path);

    const int width = maxX + 1;
    const int height = maxY + 1;

    const std::unordered_set<int> magic_set(magic_states_ids.begin(), magic_states_ids.end());

    std::vector<int> alg_qubits;
    std::unordered_set<int> locked_qubits;
    if(GRAPH_FOR_WISQ_USES_3x3_CUBE)
        locked_qubits.reserve(maxX*maxY);
    std::vector<int> magic_state_indices;
    
    const auto update_locked = [&locked_qubits, width](int wisq_idx){
        if(GRAPH_FOR_WISQ_USES_3x3_CUBE)
            for (short i = -1; i <= 1; i++)
            {
                locked_qubits.insert(wisq_idx - width + i);
                locked_qubits.insert(wisq_idx + i);
                locked_qubits.insert(wisq_idx + width + i);
            }
    };
    
    for (const Node& node : nodes) {
        const int wisq_idx = node.coordY * width + node.coordX;
        if (magic_set.count(node.id)) {
            magic_state_indices.push_back(wisq_idx);
            update_locked(wisq_idx);
        } else if (locked_qubits.count(wisq_idx) == 0) {
            alg_qubits.push_back(wisq_idx);
            update_locked(wisq_idx);
        }

        
    }

    json j;
    j["width"] = width;
    j["height"] = height;
    j["alg_qubits"] = alg_qubits;
    j["magic_states"] = magic_state_indices;

    ofs << j.dump(2);
}

