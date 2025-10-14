#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <string>
#include <fstream>
#include <algorithm>
#include <stdexcept>
#include <nlohmann/json.hpp>
#include <Eigen/Sparse>


using json = nlohmann::json;

struct Node {
    int id;
    int coordX, coordY;
    std::vector<int> neighbors;  // Store neighbor IDs, not Node objects
    
    Node(int node_id, int x = 0, int y = 0);
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
class Graph : public IGraph {
public:
    using SpMat = Eigen::SparseMatrix<int, Eigen::RowMajor>;
    using Triplet = Eigen::Triplet<int>;

private:
    SpMat adj;
    std::unordered_set<int> nodes;
    int node_count;
    std::vector<Node> node_storage;  // Global array of nodes
    std::unordered_map<int, size_t> node_map;  // Map from node ID to index in storage

    void resize(int new_size);

public:
    // Constructor: specify maximum number of nodes
    explicit Graph(int max_nodes = 100);

    // Add a node with coordinates
    void add_node(int id, int x = 0, int y = 0);

    // Get node by ID
    Node& get_node(int id);
    const Node& get_node(int id) const;

    // Add a directed edge from u to v
    void add_edge(int u, int v) override;

    // Get neighbors of node u (outgoing edges) - returns neighbor IDs
    std::vector<int> neighbors(int u) const override;

    // Get neighbors as Node objects
    std::vector<Node> neighbor_nodes(int u) const;

    // BFS traversal
    std::vector<int> bfs(int start) const override;

    // Print the adjacency list with node coordinates
    void print() const override;

    // Static method to construct a Graph from JSON file
    static Graph from_json(const std::string& filename);

    // Get all node IDs
    std::unordered_set<int> get_nodes() const { return nodes; }
    
    // Get node count
    int get_node_count() const { return node_count; }
};

#endif // GRAPH_HPP