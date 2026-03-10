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

using json = nlohmann::json;


// Graph represented as a sparse adjacency matrix (row-major)
class Graph : public IGraph {
public:
    using SpMat = Eigen::SparseMatrix<int, Eigen::RowMajor>;
    using Triplet = Eigen::Triplet<int>;

private:
    SpMat adj;

    void resize(int new_size);

public:
    // Constructor: specify maximum number of nodes
    explicit Graph(int max_nodes = 100);


    //----------overrides------------------

    // Add a directed edge from u to v
    void add_edge(int u, int v) override;


    static Graph from_json(const std::string& filename);
    static Graph create_rectangular_with_magic_states(int height, int width);


};

#endif // GRAPH_HPP
