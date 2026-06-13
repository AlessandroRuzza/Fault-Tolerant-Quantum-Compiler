#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <string>
#include <fstream>
#include <filesystem>
#include <algorithm>
#include <stdexcept>
#include <nlohmann/json.hpp>
#include <vector>

#include "igraph.hpp"

using json = nlohmann::json;


// Grid graph; adjacency lives in Node::neighbors (see IGraph).
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

    const MagicStatePlacementStrategy get_magic_state_placement_strategy() const {
        return magic_state_placement_strategy;
    }

private:
    int number_of_magic_states;
    double border_distance_percentage;
    MagicStatePlacementStrategy magic_state_placement_strategy = MagicStatePlacementStrategy::CENTER_CIRCLE;

public:
    void set_magic_state_placement_strategy(const std::string& strategy_name);

    // max_nodes is kept for call-site compatibility; sizing now happens in
    // add_node as nodes are created.
    explicit Graph(bool use_generated_graph, int /*max_nodes*/, int number_of_magic_states,
        double border_distance_percentage, const std::string& magic_state_placement_strategy,
        int x, int y, const std::string& filename) :
    
    IGraph(),
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

    
    void write_file(const std::string& path) const;
};

#endif // GRAPH_HPP
