// Find shortest path between two nodes
#include "routing.hpp"

Path NaiveShortestPath::find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const {
    if (start_node == end_node) return {start_node};
    
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