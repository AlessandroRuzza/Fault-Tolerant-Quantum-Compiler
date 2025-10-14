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
    for (int neighbor_id : neighbors(u)) {
        result.push_back(get_node(neighbor_id));
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
    
    for (int k = 0; k < adj.outerSize(); ++k) {
        for (SpMat::InnerIterator it(adj, k); it; ++it) {
            new_adj.coeffRef(it.row(), it.col()) = it.value();
        }
    }
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
    
    // Load nodes if present
    if (j.contains("nodes") && j["nodes"].is_array()) {
        for (const auto& node : j["nodes"]) {
            if (node.contains("id")) {
                int id = node["id"];
                int x = node.value("x", 0);
                int y = node.value("y", 0);
                g.add_node(id, x, y);
            }
        }
    }
    
    // Load edges
    if (j.contains("edges") && j["edges"].is_array()) {
        for (const auto& edge : j["edges"]) {
            if (edge.is_array() && edge.size() == 2) {
                int u = edge[0];
                int v = edge[1];
                g.add_edge(u, v);
            }
        }
    }
    
    return g;
}
