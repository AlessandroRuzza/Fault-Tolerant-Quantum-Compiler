#include "routing.hpp"

#include <iomanip>
#include <iostream>
#include <sstream>
#include <unordered_set>

namespace {

constexpr const char* RESET  = "\033[0m";
constexpr const char* RED    = "\033[31m";
constexpr const char* GREEN  = "\033[32m";
constexpr const char* BLUE   = "\033[34m";
constexpr const char* YELLOW = "\033[33m";

std::unordered_set<int> make_active_qubit_set(const Layer& layer_gates, const Mapping& mapping) {
    std::unordered_set<int> active_nodes;
    for (const Gate& gate : layer_gates) {
        for (int qubit : gate.qubits) {
            const int node = mapping.get_mapped_node(qubit);
            if (node >= 0) {
                active_nodes.insert(node);
            }
        }
    }
    return active_nodes;
}

std::unordered_set<int> make_magic_set(const Graph& graph) {
    const auto& magic_ids = graph.get_magic_state_ids();
    return std::unordered_set<int>(magic_ids.begin(), magic_ids.end());
}

std::unordered_set<int> make_route_set(const Routing& routing) {
    std::unordered_set<int> route_nodes;
    for (const auto& item : routing) {
        const Path& path = item.second;
        route_nodes.insert(path.begin(), path.end());
    }
    return route_nodes;
}

void print_route_path(const Path& path) {
    for (std::size_t i = 0; i < path.size(); ++i) {
        if (i > 0) {
            std::cout << BLUE << "-" << RESET;
        }
        std::cout << BLUE << path[i] << RESET;
    }
}

} // namespace

std::string gate_on_graph_string(const Gate& gate, const Mapping& mapping) {
    std::ostringstream oss;
    oss << "(" << gate.name;
    for (std::size_t i = 0; i < gate.qubits.size(); ++i) {
        if (i == 0) {
            oss << " ";
        } else {
            oss << ",";
        }
        oss << mapping.get_mapped_node(gate.qubits[i]);
    }
    oss << ")";
    return oss.str();
}

void draw_routing_layer(
    int step_index,
    const Graph& graph,
    const Mapping& mapping,
    const Layer& layer_gates,
    const Routing& routing
) {
    if (!PRINT_DRAW_ROUTING) {
        return;
    }

    const int width = graph.getMaxX() + 1;
    const int height = graph.getMaxY() + 1;

    const std::unordered_set<int> magic_nodes = make_magic_set(graph);
    const std::unordered_set<int> route_nodes = make_route_set(routing);
    const std::unordered_set<int> active_qubit_nodes = make_active_qubit_set(layer_gates, mapping);

    std::cout << "\n=== Routing Layer " << step_index << " ===\n";
    std::cout << "Legend: "
              << GREEN << "magic states" << RESET << ", "
              << RED << "qubits" << RESET << ", "
              << BLUE << "routes" << RESET << "\n\n";

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const int node_id = y * width + x;

            const bool is_magic = magic_nodes.count(node_id) > 0;
            const bool is_qubit = graph.is_occupied(node_id);
            const bool is_route = route_nodes.count(node_id) > 0;
            const bool is_active_qubit = active_qubit_nodes.count(node_id) > 0;

            const char* color = RESET;
            if (is_magic) {
                color = GREEN;
            } else if (is_active_qubit) {
                color = YELLOW;
            } else if (is_route) {
                color = BLUE;
            } else if (is_qubit) {
                color = RED;
            }

            std::cout << color << std::setw(4) << node_id << RESET;
        }
        std::cout << "\n";
    }

    std::cout << "\nRouted gates in this layer:\n";
    if (routing.empty()) {
        std::cout << "  none\n";
    } else {
        for (const auto& item : routing) {
            const Gate& gate = item.first;
            const Path& path = item.second;
            std::cout << "  " << gate_on_graph_string(gate, mapping) << " -> ";
            print_route_path(path);
            std::cout << "\n";
        }
    }

    for (const Gate& gate : layer_gates) {
        if (routing.find(gate) == routing.end()) {
            std::cout << YELLOW
                      << "WARNING: gate not routed, postponed to next layer: "
                      << gate_on_graph_string(gate, mapping)
                      << RESET << "\n";
        }
    }

    std::cout << std::endl;
}
