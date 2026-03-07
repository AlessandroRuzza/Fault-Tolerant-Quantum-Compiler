#ifndef FARTHEST_FROM_MAGIC_HPP
#define FARTHEST_FROM_MAGIC_HPP

#include "graph.hpp"


#include <unordered_map>
#include <queue>
#include <limits>
#include <algorithm>

// Selector that picks, each time, the farthest FREE node from the fixed
// set of magic states in the Graph. Occupancy is read/written via Node::occupied.
class FarthestFromMagicSelector {
public:
    // Constructor: precompute distances from magic states and build ordering.
    explicit FarthestFromMagicSelector(Graph& g) : graph(g), idx(0) {
        compute_order();
    }

    // Return the farthest non-occupied node from magic states.
    // Mark it as occupied (Node::occupied = true).
    // Return -1 if no free node is available.
    int pick_next() {
        // Skip nodes that are already occupied
        while (idx < order.size() && graph.get_node(order[idx]).occupied) {
            ++idx;
        }

        if (idx == order.size()) {
            return -1; // No more free nodes
        }

        int v = order[idx];
        // Mark node as occupied in the underlying graph
        graph.get_node(v).occupied = true;
        ++idx;
        return v;
    }

private:
    Graph& graph;
    std::vector<int> order;   // nodes sorted by distance from magic states (descending)
    std::size_t idx;          // current index in 'order'

    void compute_order() {
        const auto nodes        = graph.get_nodes();        // copy of all node IDs
        const auto magic_states = graph.get_magic_states(); // copy of magic state IDs

        // Distance map: node_id -> distance from nearest magic state
        std::unordered_map<int, int> dist;
        dist.reserve(nodes.size());

        const int INF = std::numeric_limits<int>::max();
        std::queue<int> q;

        // Initialize distances to INF
        for (int u : nodes) {
            dist[u] = INF;
        }

        // Multi-source BFS initialization: all magic states start at distance 0
        for (int s : magic_states) {
            auto it = dist.find(s);
            if (it == dist.end()) continue; // safety, in case s not in nodes
            it->second = 0;
            q.push(s);
        }

        // Multi-source BFS over the graph using Graph::neighbors(u)
        while (!q.empty()) {
            int u  = q.front();
            q.pop();
            int du = dist[u];

            const auto& neigh = graph.neighbors(u);
            for (int v : neigh) {
                auto it = dist.find(v);
                if (it == dist.end()) {
                    // If v is not in 'nodes' set for some reason, skip it
                    continue;
                }
                if (it->second == INF) {
                    it->second = du + 1;
                    q.push(v);
                }
            }
        }

        // Build list of candidate nodes.
        // If you do not want to place on magic states themselves, skip them here.
        order.clear();
        order.reserve(nodes.size());

        for (int u : nodes) {
            if (magic_states.find(u) == magic_states.end()) {
                order.push_back(u);
            }
        }

        // Sort by distance descending.
        // Nodes with dist = INF (unreachable from magic states) are treated as "very far".
        std::sort(order.begin(), order.end(),
                  [&](int a, int b) {
                      int da = dist[a];
                      int db = dist[b];

                      bool a_inf = (da == INF);
                      bool b_inf = (db == INF);

                      if (a_inf && b_inf) {
                          // tie-breaker: just by ID
                          return a < b;
                      }
                      if (a_inf) return true;   // a before b (consider a farther)
                      if (b_inf) return false;  // b before a

                      // Otherwise, larger distance first
                      return da > db;
                  });
    }
};

#endif // FARTHEST_FROM_MAGIC_HPP
