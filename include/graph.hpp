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
#include <vector>

#include "igraph.hpp"

using json = nlohmann::json;


// Graph represented as a sparse adjacency matrix (row-major)
class Graph : public IGraph {

public:

    enum class MagicStatePlacementStrategy {
        RIGHT_ROW,
        CENTER_CIRCLE
    };

    static std::vector<std::string> get_available_magic_state_placement_strategies() {
        return {"right_row", "center_circle"};
    }

    static std::string available_magic_state_placement_strategies() {
        return "right_row | center_circle";
    }

    static MagicStatePlacementStrategy parse_magic_state_placement_strategy(const std::string& strategy_name);


    using SpMat = Eigen::SparseMatrix<int, Eigen::RowMajor>;
    using Triplet = Eigen::Triplet<int>;

private:
    SpMat adj;
    int number_of_magic_states;
    double border_distance_percentage;
    MagicStatePlacementStrategy magic_state_placement_strategy = MagicStatePlacementStrategy::CENTER_CIRCLE;

    void resize(int new_size);

public:
    void set_magic_state_placement_strategy(const std::string& strategy_name);

    // Constructor: specify maximum number of nodes
    explicit Graph(bool use_generated_graph, int max_nodes, int number_of_magic_states,  
        double border_distance_percentage, const std::string& magic_state_placement_strategy,
        int x, int y, const std::string& filename) : 
    
    IGraph(), 
    adj(max_nodes, max_nodes), 
    number_of_magic_states(number_of_magic_states), 
    border_distance_percentage(border_distance_percentage) {
        set_magic_state_placement_strategy(magic_state_placement_strategy);
        if (use_generated_graph) {
            create_rectangular_with_magic_states(x, y);
        } else {
            from_json(filename);
        }
    }



    //----------overrides------------------

    // Add a directed edge from u to v
    void add_edge(int u, int v) override;



    void add_magic_states_rightrow(const std::vector<int>& magic_state_ids, int height, int width) override;

    void add_magic_states_center_circle(
        const std::vector<int>& magic_state_ids,
        int height,
        int width,
        int number_of_magic_states,
        double border_distance_percentage
    ) override;


    // -------- new methods ----------------


    void from_json(const std::string& filename);
    void create_rectangular_with_magic_states(
        int height,
        int width
    );


};

#endif // GRAPH_HPP
