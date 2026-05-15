#include "igraph.hpp"

#include <climits>
#include <cstdio>
#include <iostream>
#include <unordered_set>
#include <limits>

namespace {
    constexpr double kLoadWeight = 1.0;
    constexpr double kMappedNeighborPenaltyWeight = 6.0;
    constexpr double kScoreEpsilon = 1e-9;

    const IGraph* g_scoring_graph = nullptr;
    const std::unordered_map<int, int>* g_scoring_mapped_magic_states = nullptr;
    std::unordered_map<int, double> g_magic_states_score;
} // namespace


// Print the adjacency list with node coordinates
void IGraph::print() const {
    for (const Node& node : nodes) {
        std::cout << node.id << " (" << node.coordX << "," << node.coordY << "):";
        for (int v : neighbors(node.id)) {
            std::cout << " " << v;
        }
        std::cout << std::endl;
    }
}


    
void IGraph::print_rectangular() const {
    if (node_count == 0 || maxX < 0 || maxY < 0) {
        std::cout << "(empty graph)" << std::endl;
        return;
    }

    // Print the grid with fixed-width columns
    for (int y = 0; y <= this->maxY; ++y) {
        for (int x = 0; x <= this->maxX; ++x) {
            int node_id = -1;
            try {
                node_id = get_node_by_coordinates(x, y).id;
            } catch (const std::exception& e) {
                std::cout << "   "; // Empty space for missing nodes
                continue;
            }
            const bool is_magic =
                std::find(magic_states_ids.begin(), magic_states_ids.end(), node_id) != magic_states_ids.end();

            if (is_magic) {
                // Print magic-state nodes in green.
                std::cout << "\033[1;32m";
                printf("%3d", node_id);
                std::cout << "\033[0m";
            } else if (is_occupied(node_id)) {
                // Print occupied non-magic nodes in red.
                std::cout << "\033[1;31m";
                printf("%3d", node_id);
                std::cout << "\033[0m";
            } else {
                printf("%3d", node_id);
            }
            std::cout << " ";
        }
        std::cout << std::endl;
    }
}



void IGraph::print_rectangular(const std::unordered_set<int>& candidates) const {
    if (node_count == 0 || maxX < 0 || maxY < 0) {
        std::cout << "(empty graph)" << std::endl;
        return;
    }

    for (int y = 0; y <= this->maxY; ++y) {
        for (int x = 0; x <= this->maxX; ++x) {
            int node_id = -1;
            try {
                node_id = get_node_by_coordinates(x, y).id;
            } catch (const std::exception&) {
                std::cout << "   ";
                continue;
            }
            const bool is_magic =
                std::find(magic_states_ids.begin(), magic_states_ids.end(), node_id) != magic_states_ids.end();

            if (is_magic) {
                std::cout << "\033[1;32m";
                printf("%3d", node_id);
                std::cout << "\033[0m";
            } else if (is_occupied(node_id)) {
                std::cout << "\033[1;31m";
                printf("%3d", node_id);
                std::cout << "\033[0m";
            } else if (candidates.count(node_id)) {
                std::cout << "\033[1;33m";
                printf("%3d", node_id);
                std::cout << "\033[0m";
            } else {
                printf("%3d", node_id);
            }
            std::cout << " ";
        }
        std::cout << std::endl;
    }
}


// Add a node with coordinates
void IGraph::add_node(int id, int x, int y) {
    // Resize vector if necessary to accommodate the id
    if (id >= nodes.size()) {
        nodes.resize(id + 1, Node(-1, 0, 0)); // Initialize with sentinel values
    }

    // Add if missing, otherwise refresh coordinates.
    if (nodes[id].id == -1) {
        nodes[id] = Node(id, x, y);
        node_count++;
    } else {
        nodes[id].coordX = x;
        nodes[id].coordY = y;
    }

    maxX = std::max(maxX, nodes[id].coordX);
    maxY = std::max(maxY, nodes[id].coordY);
}

void IGraph::add_node(int id) {
    // Add a default node only if missing; do not overwrite existing coordinates.
    if (id >= nodes.size()) {
        nodes.resize(id + 1, Node(-1, 0, 0));
    }
    if (nodes[id].id == -1) {
        nodes[id] = Node(id, 0, 0);
        node_count++;
        maxX = std::max(maxX, 0);
        maxY = std::max(maxY, 0);
    }
}





const int IGraph::getNearestMagicStateId(int node_id) const {
    if (magic_states_ids.empty()) {
        throw std::runtime_error("No magic states available in the graph.");
    }

    const Node& start_node = get_node(node_id);
    int nearest_magic_state = -1;
    double min_distance = std::numeric_limits<double>::max();

    for (Node magic_node : get_magic_states()) {
        double distance = std::sqrt(std::pow(start_node.coordX - magic_node.coordX, 2) +
                                    std::pow(start_node.coordY - magic_node.coordY, 2));
        if (distance < min_distance) {
            min_distance = distance;
            nearest_magic_state = magic_node.id;
        }
    }

    return nearest_magic_state;
}



const Node& IGraph::getNearestMagicState(const Node& node) const {
    int nearest_id = getNearestMagicStateId(node.id);
    return get_node(nearest_id);
}




const int IGraph::getBestMagicStateId() {
    if (magic_states_ids.empty()) {
        throw std::runtime_error("No magic states available in the graph.");
    }

    g_scoring_graph = this;
    g_scoring_mapped_magic_states = &mapped_magic_states;

    int best_magic_state_id = -1;
    double best_score = std::numeric_limits<double>::infinity();
    int best_min_distance_to_mapped = -1;

    for (int magic_state_id : magic_states_ids) {
        update_magic_states_score(magic_state_id);
        const double score = g_magic_states_score[magic_state_id];

        int min_distance_to_mapped = INT_MAX;
        for (int other_magic_state_id : magic_states_ids) {
            if (other_magic_state_id == magic_state_id) {
                continue;
            }
            auto mapped_it = mapped_magic_states.find(other_magic_state_id);
            if (mapped_it == mapped_magic_states.end() || mapped_it->second <= 0) {
                continue;
            }

            const int manhattan_distance =
                std::abs(get_coordX(magic_state_id) - get_coordX(other_magic_state_id)) +
                std::abs(get_coordY(magic_state_id) - get_coordY(other_magic_state_id));
            min_distance_to_mapped = std::min(min_distance_to_mapped, manhattan_distance);
        }
        if (min_distance_to_mapped == INT_MAX) {
            min_distance_to_mapped = std::numeric_limits<int>::max();
        }

        const bool better_score = (score + kScoreEpsilon) < best_score;
        const bool same_score = !better_score && std::abs(score - best_score) <= kScoreEpsilon;
        if (best_magic_state_id == -1 ||
            better_score ||
            (same_score && min_distance_to_mapped > best_min_distance_to_mapped) ||
            (same_score && min_distance_to_mapped == best_min_distance_to_mapped &&
                magic_state_id < best_magic_state_id)) {
            best_magic_state_id = magic_state_id;
            best_score = score;
            best_min_distance_to_mapped = min_distance_to_mapped;
        }
    }

    return best_magic_state_id;
}



const void IGraph::update_magic_states_score(int magic_state_id) {
    if (g_scoring_graph == nullptr || g_scoring_mapped_magic_states == nullptr) {
        return;
    }

    const auto& mapped_counts = *g_scoring_mapped_magic_states;

    int local_load = 0;
    auto local_it = mapped_counts.find(magic_state_id);
    if (local_it != mapped_counts.end()) {
        local_load = local_it->second;
    }

    // Penalize candidates that are close to already-used magic states.
    double proximity_penalty = 0.0;
    for (int other_magic_state_id : g_scoring_graph->get_magic_state_ids()) {
        if (other_magic_state_id == magic_state_id) {
            continue;
        }

        auto mapped_it = mapped_counts.find(other_magic_state_id);
        if (mapped_it == mapped_counts.end() || mapped_it->second <= 0) {
            continue;
        }

        const int manhattan_distance =
            std::abs(g_scoring_graph->get_coordX(magic_state_id) -
                        g_scoring_graph->get_coordX(other_magic_state_id)) +
            std::abs(g_scoring_graph->get_coordY(magic_state_id) -
                        g_scoring_graph->get_coordY(other_magic_state_id));
        proximity_penalty += static_cast<double>(mapped_it->second) /
                                static_cast<double>(manhattan_distance + 1);
    }

    g_magic_states_score[magic_state_id] =
        (kLoadWeight * static_cast<double>(local_load)) +
        (kMappedNeighborPenaltyWeight * proximity_penalty);
}

void IGraph::increment_mapped_magic_state(int magic_state_id) {
    mapped_magic_states[magic_state_id]++;
    update_magic_states_score(magic_state_id);


}
