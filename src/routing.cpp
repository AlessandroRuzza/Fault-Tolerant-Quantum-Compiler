#include "routing.hpp"

namespace circuit {
    // Find shortest path between two nodes
    Path NaiveShortestPath::find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const {
        if (start_node == end_node) return {start_node};
        
        std::unordered_map<int, int> parent;
        auto cmp = [&](int a, int b){ 
            Node aNode = this->graph.get_node(a);
            Node bNode = this->graph.get_node(b);
            return aNode.distance(bNode); 
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
                if (used_nodes.count(neighbor) == 0
                    && parent.find(neighbor) == parent.end() 
                ){
                    parent[neighbor] = current;
                    q.push(neighbor);
                }
            }
        }
        
        return {}; // no path found
    }

    Routing QubitRouter::route_layer(const std::vector<Gate>& layer_gates) const {
        Routing routing;
        std::unordered_map<int, int> node_to_qubit; // inverse mapping
        std::unordered_set<int> used_nodes;
        
        // Build inverse mapping (node -> qubit)
        for (int qubit = 0; qubit < circuit.getNumQubits(); ++qubit) {
            try {
                int node = mapping.get_mapped_node(qubit);
                node_to_qubit[node] = qubit;
                used_nodes.insert(node); // Cannot route through qubit nodes.
            } catch (...) {
                throw new std::runtime_error("Qubit was not mapped.");
            }
        }
        
        for (const Gate& gate : layer_gates) {
            Path path;
            if (gate.qubits.size() == 1) {
                // Single-qubit gate: always executable
                int node = mapping.get_mapped_node(gate.qubits[0]);
                path = {node};
            } else if (gate.qubits.size() == 2) {
                // Two-qubit gate: check if qubits are adjacent
                int qubit1 = gate.qubits[0];
                int qubit2 = gate.qubits[1];
                
                int node1 = mapping.get_mapped_node(qubit1);
                int node2 = mapping.get_mapped_node(qubit2);

                // TODO: route better (improve heuristic)
                path = pathStrategy.find_shortest_path(node1, node2, used_nodes);
            }
            
            if(path.size() > 0){
                routing.emplace(gate, path);
                used_nodes.insert(path.begin(), path.end());
            }
        }

        return routing;
    }


}