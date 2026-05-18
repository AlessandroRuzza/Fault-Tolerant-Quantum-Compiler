// Find shortest path between two nodes
#include "routing.hpp"

// Populate next_node[s][t] with the first hop on the shortest path from s to t.
// Runs one BFS per source node; the graph is static so this is computed once.
void NaiveShortestPath::populate_next_node() {
    const int N = graph.get_node_count();
    next_node.assign(N, std::vector<int>(N, -1));

    for (int s = 0; s < N; ++s) {
        std::vector<char> visited(N, 0);
        std::queue<int> q;
        q.push(s);
        visited[s] = 1;

        while (!q.empty()) {
            const int u = q.front();
            q.pop();
            for (int v : graph.neighbors(u)) {
                if (visited[v]) continue;
                visited[v] = 1;
                // First hop from s toward v: if u is the source, v itself is the
                // first hop; otherwise inherit the first hop already recorded for u.
                next_node[s][v] = (u == s) ? v : next_node[s][u];
                q.push(v);
            }
        }
    }
}

Path NaiveShortestPath::find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const {
    if (start_node == end_node) return {start_node};

    // APSP fast path: if the precomputed shortest path avoids all used_nodes,
    // return it directly. Otherwise fall through to the regular BFS that can
    // route around blocked nodes.
    if (!next_node.empty()) {
        Path apsp_path;
        apsp_path.push_back(start_node);
        int cur = start_node;
        bool clear = true;
        while (cur != end_node) {
            const int nxt = next_node[cur][end_node];
            if (nxt < 0) { clear = false; break; } // no path in the static graph
            if (used_nodes.count(nxt) != 0 && nxt != end_node) {
                clear = false;
                break;
            }
            apsp_path.push_back(nxt);
            cur = nxt;
        }
        if (clear) return apsp_path;
    }

    std::unordered_map<int, int> parent;
    auto cmp = [&](int a, int b){ 
        Node aNode = this->graph.get_node(a);
        Node bNode = this->graph.get_node(b);
        Node target = this->graph.get_node(end_node);
        return aNode.distance(target) > bNode.distance(target); 
    };
    std::priority_queue<int, std::vector<int>, decltype(cmp)> q(cmp);

    q.push(start_node);
    parent[start_node] = -1;

    //TODO: constrain direction of arrival (i.e. only from top/side)
    
    while (!q.empty()) {
        int current = q.top();
        q.pop();
        
        if (current == end_node) {
            // Reconstruct path
            Path path;
            int node = end_node;
            while (node != -1) {
                path.push_back(node);
                node = parent[node];
            }
            std::reverse(path.begin(), path.end());
            return path;
        }
        
        for (int neighbor : graph.neighbors(current)) {
            if(neighbor == end_node ||                          // if target
               (used_nodes.count(neighbor) == 0                 // or unused & unexplored node
                && parent.find(neighbor) == parent.end())
            ){
                parent[neighbor] = current;
                q.push(neighbor);                           // Add to queue with current as parent
            }
        }
    }
    
    return {}; // no path found
}