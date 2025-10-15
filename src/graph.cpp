#include "graph.hpp"

// Node constructor implementation
Node::Node(int node_id, int x, int y) : id(node_id), coordX(x), coordY(y) {}

// Graph constructor implementation
Graph::Graph(int max_nodes) : adj(max_nodes, max_nodes), node_count(0) {
    node_storage.reserve(max_nodes);
}

// Add a node with coordinates
void Graph::add_node(int id, int x, int y) {
    if (node_map.find(id) == node_map.end()) {
        node_storage.emplace_back(id, x, y);
        node_map[id] = node_storage.size() - 1;  // Map ID to index in storage
        nodes.insert(id);
    }
}

// Get node by ID (non-const)
Node& Graph::get_node(int id) {
    auto it = node_map.find(id);
    if (it == node_map.end()) {
        add_node(id);  // Auto-create node if it doesn't exist
        it = node_map.find(id);
    }
    return node_storage[it->second];
}

// Get node by ID (const)
const Node& Graph::get_node(int id) const {
    auto it = node_map.find(id);
    if (it == node_map.end()) {
        throw std::runtime_error("Node not found: " + std::to_string(id));
    }
    return node_storage[it->second];
}

// Add a directed edge from u to v
void Graph::add_edge(int u, int v) {
    if (u < 0 || v < 0) return;
    
    // Ensure nodes exist
    add_node(u);
    add_node(v);
    
    if (u >= adj.rows() || v >= adj.cols()) {
        resize(std::max(u, v) + 1);
    }
    adj.coeffRef(u, v) = 1;
    
    // Update node's neighbor list
    auto& u_node = get_node(u);
    if (std::find(u_node.neighbors.begin(), u_node.neighbors.end(), v) == u_node.neighbors.end()) {
        u_node.neighbors.push_back(v);
    }
    auto& v_node = get_node(v);
    if (std::find(v_node.neighbors.begin(), v_node.neighbors.end(), v) == v_node.neighbors.end()) {
        v_node.neighbors.push_back(u);
    }
    
    nodes.insert(u);
    nodes.insert(v);
    node_count = std::max(node_count, std::max(u, v) + 1);
}

// Get neighbors of node u (outgoing edges) - returns neighbor IDs
std::vector<int> Graph::neighbors(int u) const {
    auto it = node_map.find(u);
    if (it != node_map.end()) {
        return node_storage[it->second].neighbors;
    }
    return std::vector<int>();  // Return empty vector if node not found
}

// Get neighbors as Node objects
std::vector<Node> Graph::neighbor_nodes(int u) const {
    std::vector<Node> result;
    std::vector<int> neighbors_u = neighbors(u);
    result.reserve(neighbors_u.size());
    for (int neighbor_id : neighbors_u) {
        result.emplace_back(get_node(neighbor_id));
    }
    return result;
}

// BFS traversal implementation
std::vector<int> Graph::bfs(int start) const {
    std::vector<int> result;
    std::unordered_set<int> visited;
    std::queue<int> q;
    
    if (nodes.find(start) == nodes.end()) {
        return result; // Start node doesn't exist
    }
    
    q.push(start);
    visited.insert(start);
    
    while (!q.empty()) {
        int current = q.front();
        q.pop();
        result.push_back(current);
        
        for (int neighbor : neighbors(current)) {
            if (visited.find(neighbor) == visited.end()) {
                visited.insert(neighbor);
                q.push(neighbor);
            }
        }
    }
    
    return result;
}

// Resize adjacency matrix
void Graph::resize(int new_size) {
    SpMat new_adj(new_size, new_size);
    new_adj.reserve(adj.nonZeros());
    
    std::vector<Eigen::Triplet<int>> triplets;
    for (int k = 0; k < adj.outerSize(); ++k) {
        for (SpMat::InnerIterator it(adj, k); it; ++it) {
            triplets.emplace_back(it.row(), it.col(), it.value());
        }
    }
    new_adj.setFromTriplets(triplets.begin(), triplets.end());
    adj = std::move(new_adj);
}

// Print the adjacency list with node coordinates
void Graph::print() const {
    for (int u : nodes) {
        const Node& node = get_node(u);
        std::cout << u << " (" << node.coordX << "," << node.coordY << "):";
        for (int v : neighbors(u)) {
            std::cout << " " << v;
        }
        std::cout << std::endl;
    }
}

// Static method to construct a Graph from JSON file
Graph Graph::from_json(const std::string& filename) {
    std::ifstream f(filename);
    if (!f) {
        std::cerr << "file non trovato: " << filename << "\n";
        return Graph{}; // return empty graph on failure
    }
    
    json j = json::parse(f);
    Graph g;

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
        return Graph{};
    }

    // Handle generic graph type with fields at the root
    if (j["type"] == "generic") {
        int num_nodes = j.value("num_nodes", 0);
        // Add nodes with default coordinates
        for (int i = 0; i < num_nodes; ++i) {
            g.add_node(i);
        }
        // Set coordinates if present
        if (j.contains("coordinates")) {
            for (auto it = j["coordinates"].begin(); it != j["coordinates"].end(); ++it) {
                int node_id = std::stoi(it.key());
                const auto& coords = it.value();
                if (coords.is_array() && coords.size() >= 2) {
                    int x = static_cast<int>(coords[0]);
                    int y = static_cast<int>(coords[1]);
                    Node& n = g.get_node(node_id);
                    n.coordX = x;
                    n.coordY = y;
                }
            }
        }
        else{
            std::cerr << "node coordinates not specified!\n";
            return Graph{};
        }

        // Add edges from connectivity
        if (j.contains("connectivity")) {
            for (const auto& edge : j["connectivity"]) {
                if (edge.is_array() && edge.size() == 2) {
                    int u = edge[0];
                    int v = edge[1];
                    g.add_edge(u, v);
                }
            }
        } 
        else{
            std::cerr << "node connectivity not specified!\n";
            return Graph{};
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
                    g.add_node(node_id, c, r); // x = col, y = row
                }
            }
            // Create edges
            for (int r = 0; r < rows; ++r) {
                for (int c = 0; c < cols; ++c) {
                    int node_id = r * cols + c;
                    // Right neighbor
                    if (c + 1 < cols) g.add_edge(node_id, node_id + 1);
                    // Bottom neighbor
                    if (r + 1 < rows) g.add_edge(node_id, node_id + cols);
                    if (diagonal) {
                        // Bottom-right neighbor
                        if (c + 1 < cols && r + 1 < rows) g.add_edge(node_id, node_id + cols + 1);
                        // Bottom-left neighbor
                        if (c - 1 >= 0 && r + 1 < rows) g.add_edge(node_id, node_id + cols - 1);
                    }
                }
            }
        }
        else{
            std::cerr << "rows or cols not specified!\n";
            return Graph{};
        }
        std::cout << g.get_node_count() << " nodes created in rectangular grid.\n";
        return g;
    }


    if(j.contains("magic states")){
        if(j["magic states"].is_array()){
            g.magic_states.insert(j["magic states"].begin(), j["magic states"].end());
        }
        else{
            std::cerr << "magic states not specified as array of ints!\n";
            return Graph{};
        }
    }
    else{
        std::cerr << "magic states not specified!\n";
        return Graph{};
    }
    return g;
}
