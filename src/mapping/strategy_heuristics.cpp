#include "mapping.hpp"
#include "circuit.hpp"

#include <cmath>
#include <limits>
#include <random>
#include <vector>

void Mapping::random_mapping(Qubit* qubit, int second_qubit) {
    if (PRINT_MAPPING) std::cout << "mapping randomly because second qubit is not mapped and T_count is in "
                 "the middle\n";
    std::vector<int> candidates;
    candidates.reserve(graph.get_node_count());

    const std::unordered_set<int> magic_states = graph.get_magic_states();
    for (int node_id = 0; node_id < graph.get_node_count(); ++node_id) {
        if (!graph.is_occupied(node_id) && !magic_states.contains(node_id)) {
            candidates.push_back(node_id);
        }
    }

    if (candidates.empty()) {
        for (int node_id = 0; node_id < graph.get_node_count(); ++node_id) {
            if (!graph.is_occupied(node_id)) {
                candidates.push_back(node_id);
            }
        }
    }

    if (candidates.empty()) {
        throw std::runtime_error("No available node found for random_mapping.");
    }

    static thread_local std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<size_t> distribution(0, candidates.size() - 1);
    const int mapped_node = candidates[distribution(rng)];
    map_qubit_to_node(qubit->getQubitID(), mapped_node);

    if (second_qubit >= 0 && get_mapped_node(second_qubit) == -1) {
        mapToNeighbor(circuit.getQubit(second_qubit), mapped_node);
    }
}

void Mapping::center_spaced_mapping(Qubit* qubit, int second_qubit) {
    if (PRINT_MAPPING) std::cout << "mapping with center-spaced heuristic\n";

    const std::unordered_set<int> magic_states = graph.get_magic_states();
    std::vector<int> candidates;
    std::vector<int> occupied_data_nodes;
    candidates.reserve(graph.get_node_count());
    occupied_data_nodes.reserve(graph.get_node_count());

    int min_x = std::numeric_limits<int>::max();
    int min_y = std::numeric_limits<int>::max();
    int max_x = std::numeric_limits<int>::min();
    int max_y = std::numeric_limits<int>::min();

    for (int node_id = 0; node_id < graph.get_node_count(); ++node_id) {
        if (magic_states.contains(node_id)) {
            continue;
        }

        const Node& node = graph.get_node(node_id);
        min_x = std::min(min_x, node.coordX);
        min_y = std::min(min_y, node.coordY);
        max_x = std::max(max_x, node.coordX);
        max_y = std::max(max_y, node.coordY);

        if (graph.is_occupied(node_id)) {
            occupied_data_nodes.push_back(node_id);
            continue;
        }

        candidates.push_back(node_id);
    }

    if (candidates.empty()) {
        for (int node_id = 0; node_id < graph.get_node_count(); ++node_id) {
            if (!graph.is_occupied(node_id)) {
                candidates.push_back(node_id);
            }
        }
    }

    if (candidates.empty()) {
        throw std::runtime_error("No available node found for center_spaced_mapping.");
    }

    const float center_x = (min_x + max_x) / 2.0f;
    const float center_y = (min_y + max_y) / 2.0f;

    const auto center_distance = [&](int node_id) -> float {
        const Node& node = graph.get_node(node_id);
        return std::abs(node.coordX - center_x) + std::abs(node.coordY - center_y);
    };

    const auto min_distance_from_occupied = [&](int node_id) -> float {
        if (occupied_data_nodes.empty()) {
            return std::numeric_limits<float>::infinity();
        }
        const Node& candidate = graph.get_node(node_id);
        float min_dist = std::numeric_limits<float>::infinity();
        for (int occupied_id : occupied_data_nodes) {
            const Node& occupied = graph.get_node(occupied_id);
            const float dist = std::abs(candidate.coordX - occupied.coordX) +
                               std::abs(candidate.coordY - occupied.coordY);
            min_dist = std::min(min_dist, dist);
        }
        return min_dist;
    };

    int best_node = -1;
    float best_center_dist = std::numeric_limits<float>::infinity();
    float best_spacing = -1.0f;

    for (int node_id : candidates) {
        const float current_center_dist = center_distance(node_id);
        const float current_spacing = min_distance_from_occupied(node_id);

        if (best_node == -1 || current_center_dist < best_center_dist ||
            (current_center_dist == best_center_dist && current_spacing > best_spacing) ||
            (current_center_dist == best_center_dist && current_spacing == best_spacing &&
             node_id < best_node)) {
            best_node = node_id;
            best_center_dist = current_center_dist;
            best_spacing = current_spacing;
        }
    }

    map_qubit_to_node(qubit->getQubitID(), best_node);

    if (second_qubit >= 0 && get_mapped_node(second_qubit) == -1) {
        mapToNeighbor(circuit.getQubit(second_qubit), best_node);
    }
}

void Mapping::distance_first_mapping(Qubit* qubit, int second_qubit) {
    if (PRINT_MAPPING) std::cout << "mapping with distance-first heuristic\n";

    const std::unordered_set<int> magic_states = graph.get_magic_states();
    std::vector<int> candidates;
    std::vector<int> occupied_data_nodes;
    candidates.reserve(graph.get_node_count());
    occupied_data_nodes.reserve(graph.get_node_count());

    int min_x = std::numeric_limits<int>::max();
    int min_y = std::numeric_limits<int>::max();
    int max_x = std::numeric_limits<int>::min();
    int max_y = std::numeric_limits<int>::min();

    for (int node_id = 0; node_id < graph.get_node_count(); ++node_id) {
        if (magic_states.contains(node_id)) {
            continue;
        }

        const Node& node = graph.get_node(node_id);
        min_x = std::min(min_x, node.coordX);
        min_y = std::min(min_y, node.coordY);
        max_x = std::max(max_x, node.coordX);
        max_y = std::max(max_y, node.coordY);

        if (graph.is_occupied(node_id)) {
            occupied_data_nodes.push_back(node_id);
            continue;
        }

        candidates.push_back(node_id);
    }

    if (candidates.empty()) {
        for (int node_id = 0; node_id < graph.get_node_count(); ++node_id) {
            if (!graph.is_occupied(node_id)) {
                candidates.push_back(node_id);
            }
        }
    }

    if (candidates.empty()) {
        throw std::runtime_error("No available node found for distance_first_mapping.");
    }

    const float center_x = (min_x + max_x) / 2.0f;
    const float center_y = (min_y + max_y) / 2.0f;

    const auto center_distance = [&](int node_id) -> float {
        const Node& node = graph.get_node(node_id);
        return std::abs(node.coordX - center_x) + std::abs(node.coordY - center_y);
    };

    const auto min_distance_from_occupied = [&](int node_id) -> float {
        if (occupied_data_nodes.empty()) {
            return std::numeric_limits<float>::infinity();
        }
        const Node& candidate = graph.get_node(node_id);
        float min_dist = std::numeric_limits<float>::infinity();
        for (int occupied_id : occupied_data_nodes) {
            const Node& occupied = graph.get_node(occupied_id);
            const float dist = std::abs(candidate.coordX - occupied.coordX) +
                               std::abs(candidate.coordY - occupied.coordY);
            min_dist = std::min(min_dist, dist);
        }
        return min_dist;
    };

    int best_node = -1;
    float best_spacing = -1.0f;
    float best_center_dist = std::numeric_limits<float>::infinity();

    for (int node_id : candidates) {
        const float current_spacing = min_distance_from_occupied(node_id);
        const float current_center_dist = center_distance(node_id);

        if (best_node == -1 || current_spacing > best_spacing ||
            (current_spacing == best_spacing && current_center_dist < best_center_dist) ||
            (current_spacing == best_spacing && current_center_dist == best_center_dist &&
             node_id < best_node)) {
            best_node = node_id;
            best_spacing = current_spacing;
            best_center_dist = current_center_dist;
        }
    }

    map_qubit_to_node(qubit->getQubitID(), best_node);

    if (second_qubit >= 0 && get_mapped_node(second_qubit) == -1) {
        mapToNeighbor(circuit.getQubit(second_qubit), best_node);
    }
}
