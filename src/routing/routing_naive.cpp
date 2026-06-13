// Find shortest path between two nodes
#include "routing.hpp"

#include <limits>

// A*: f = g (steps so far) + h (Manhattan distance, admissible and consistent
// on a unit-cost grid), so the returned path is a true shortest path around
// obstacles. The previous version was greedy best-first on h alone and could
// return suboptimal paths, which biased the congestion-vs-naive comparison and
// the "closest magic state" selection.
Path NaiveShortestPath::find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const {
    if (start_node == end_node) return {start_node};

    const int node_count = graph.get_node_count();
    const Node& target = graph.get_node(end_node);
    const auto heuristic = [&](int node) {
        return graph.get_node(node).distance(target);
    };

    constexpr int kUnvisited = std::numeric_limits<int>::max();
    std::vector<int> g_cost(node_count, kUnvisited);
    std::vector<int> parent(node_count, -1);
    std::vector<char> closed(node_count, 0);

    using QueueItem = std::pair<float, int>; // (f = g + h, node)
    std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<QueueItem>> open;

    g_cost[start_node] = 0;
    open.push({heuristic(start_node), start_node});

    while (!open.empty()) {
        const int current = open.top().second;
        open.pop();

        if (current == end_node) {
            Path path;
            for (int node = end_node; node != start_node; node = parent[node]) {
                path.push_back(node);
            }
            path.push_back(start_node);
            std::reverse(path.begin(), path.end());
            return path;
        }

        // With a consistent heuristic a node is final the first time it pops.
        if (closed[current]) continue;
        closed[current] = 1;

        const int tentative = g_cost[current] + 1;
        for (int neighbor : graph.neighbors(current)) {
            // The target is reachable even when "used" (it is the other gate
            // endpoint / magic state); every other used node blocks the path.
            if (neighbor != end_node && used_nodes.count(neighbor) > 0) {
                continue;
            }
            if (tentative < g_cost[neighbor]) {
                g_cost[neighbor] = tentative;
                parent[neighbor] = current;
                open.push({static_cast<float>(tentative) + heuristic(neighbor), neighbor});
            }
        }
    }

    return {}; // no path found
}
