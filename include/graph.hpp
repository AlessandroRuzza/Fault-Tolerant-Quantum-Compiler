#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <string>
#include <fstream>
#include <algorithm>
#include <stdexcept>
#include <nlohmann/json.hpp>
#include <Eigen/Sparse>

#include "igraph.hpp"

// Graph represented as a sparse adjacency matrix (row-major)
class Graph : public IGraph {
public:
    using SpMat = Eigen::SparseMatrix<int, Eigen::RowMajor>;
    using Triplet = Eigen::Triplet<int>;

private:
    SpMat adj;
    std::vector<Node> node_storage;  // Global array of nodes
    std::unordered_map<int, size_t> node_map;  // Map from node ID to index in storage

    void resize(int new_size);

public:
    // Constructor: specify maximum number of nodes
    explicit Graph(int max_nodes = 100);


    //----------overrides------------------

    // Add a directed edge from u to v
    void add_edge(int u, int v) override;

    // Get neighbors of node u (outgoing edges) - returns neighbor IDs
    const std::vector<int>& neighbors(int u) const override;

    // BFS traversal
    std::vector<int> bfs(int start) const override;

    bool is_occupied(int id) const override; 

    // Print the adjacency list with node coordinates
    void print() const override;

    Node& get_node(int id) override;
    
    const Node& get_node(int id) const override;

    void occupy_node(int id) override;

    std::vector<Node> neighbor_nodes(int u) const override;


    //-------coordinates---------

    // Add a node with coordinates
    void add_node(int id, int x = 0, int y = 0);


    const Node& get_node_by_coordinates(int x, int y) const;

    const int get_node_id_by_coordinates(int x, int y) const {
        return get_node_by_coordinates(x, y).id;
    }

    const int get_coordX(int id) const {
        return get_node(id).coordX;
    }

    const int get_coordY(int id) const {
        return get_node(id).coordY;
    }


    // Get neighbors as Node objects


    void print_rectangular() const;

    // Static method to construct a Graph from JSON file
    static Graph from_json(const std::string& filename);

    // Static method to create a rectangular grid with magic states
    static Graph create_rectangular_with_magic_states(int width, int height);



    // Get all node IDs
    std::unordered_set<int> get_nodes() const { return nodes; }
    // Get all magic state node IDs
    std::unordered_set<int> get_magic_states() const { return magic_states; }
    
    // Get node count
    int get_node_count() const { return node_count; }

    const int getNearestMagicStateId(int node_id) const;

    const Node& getNearestMagicState(const Node& node) const;
};

#endif // GRAPH_HPP