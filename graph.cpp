#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <nlohmann/json.hpp>

#include <Eigen/Sparse>
#include <fstream>
#include <algorithm>

using json = nlohmann::json;

struct Node{
    int id;
    int coordX, coordY;
    std::vector<int> neighbors;  // Store neighbor IDs, not Node objects
    
    Node(int node_id, int x = 0, int y = 0) : id(node_id), coordX(x), coordY(y) {}
};

class IGraph {
public:
    virtual ~IGraph() = default;
    virtual void add_edge(int u, int v) = 0;
    virtual std::vector<int> neighbors(int u) const = 0;
    virtual std::vector<int> bfs(int start) const = 0;
    virtual void print() const = 0;
};

// Graph represented as a sparse adjacency matrix (row-major)
class Graph {
public:
    using SpMat = Eigen::SparseMatrix<int, Eigen::RowMajor>;
    using Triplet = Eigen::Triplet<int>;

private:
    SpMat adj;
    std::unordered_set<int> nodes;
    int node_count;
    std::vector<Node> node_storage;  // Global array of nodes
    std::unordered_map<int, size_t> node_map;  // Map from node ID to index in storage

    // Constructor: specify maximum number of nodes
    Graph(int max_nodes = 100) : adj(max_nodes, max_nodes), node_count(0) {
        node_storage.reserve(max_nodes);
    }

    // Add a node with coordinates
    void add_node(int id, int x = 0, int y = 0) {
        if (node_map.find(id) == node_map.end()) {
            node_storage.emplace_back(id, x, y);
            node_map[id] = node_storage.size() - 1;  // Map ID to index in storage
            nodes.insert(id);
        }
    }

    // Get node by ID
    Node& get_node(int id) {
        auto it = node_map.find(id);
        if (it == node_map.end()) {
            add_node(id);  // Auto-create node if it doesn't exist
            it = node_map.find(id);
        }
        return node_storage[it->second];
    }

    const Node& get_node(int id) const {
        auto it = node_map.find(id);
        if (it == node_map.end()) {
            throw std::runtime_error("Node not found: " + std::to_string(id));
        }
        return node_storage[it->second];
    }

    // Add a directed edge from u to v
    void add_edge(int u, int v) {
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
    std::vector<int> neighbors(int u) const {
        auto it = node_map.find(u);
        if (it != node_map.end()) {
            return node_storage[it->second].neighbors;
        }
        return std::vector<int>();  // Return empty vector if node not found
    }

    // Get neighbors as Node objects
    std::vector<Node> neighbor_nodes(int u) const {
        std::vector<Node> result;
        for (int neighbor_id : neighbors(u)) {
            result.push_back(get_node(neighbor_id));
        }
        return result;
    }

private:
    void resize(int new_size) {
        SpMat new_adj(new_size, new_size);
        new_adj.reserve(adj.nonZeros());
        
        for (int k = 0; k < adj.outerSize(); ++k) {
            for (SpMat::InnerIterator it(adj, k); it; ++it) {
                new_adj.coeffRef(it.row(), it.col()) = it.value();
            }
        }
        adj = std::move(new_adj);
    }

public:

    // Print the adjacency list with node coordinates
    void print() const {
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
    static Graph from_json(const std::string& filename) {
        std::ifstream f(filename);
        if (!f) {
            std::cerr << "file non trovato: " << filename << "\n";
            return Graph{}; // return empty graph on failure
        }
        json j = json::parse(f);
        Graph g;
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
};

// Example usage
int main() {
    //Graph g;
    
    // // Add nodes with coordinates
    // g.add_node(1, 0, 0);
    // g.add_node(2, 1, 0);
    // g.add_node(3, 0, 1);
    // g.add_node(4, 1, 1);
    
    // // Add edges
    // g.add_edge(1, 2);
    // g.add_edge(1, 3);
    // g.add_edge(2, 4);
    // g.add_edge(3, 4);

    // std::cout << "Adjacency List with coordinates:" << std::endl;
    // g.print();

    // std::cout << "\nBFS from node 1:" << std::endl;
    // for (int node : g.bfs(1)) {
    //     const Node& n = g.get_node(node);
    //     std::cout << node << "(" << n.coordX << "," << n.coordY << ") ";
    // }
    // std::cout << std::endl;

    Graph g = Graph::from_json("graph_description_generic.json");
    g.print();

    return 0;
}