#include "routing.hpp"

// Find shortest path between two nodes
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

float QubitRouter::minGateRouteLength(const Gate& g) const {
    if (g.qubits.empty()) {
        throw std::runtime_error("Gate without qubits found while computing route length.");
    }
    if(g.name == "h") return 0;

    const int mapped_q0 = mapping.get_mapped_node(g.qubits[0]);
    if (mapped_q0 < 0) {
        throw std::runtime_error("Qubit " + std::to_string(g.qubits[0]) + " is not mapped.");
    }
    const Node& node1 = graph.get_node(mapped_q0);
    int target;
    if(g.qubits.size() == 2){
        target = mapping.get_mapped_node(g.qubits[1]);
        if (target < 0) {
            throw std::runtime_error("Qubit " + std::to_string(g.qubits[1]) + " is not mapped.");
        }
    }
    else { // target = closest magic state
        const auto& magic_ids = graph.get_magic_state_ids();
        if (magic_ids.empty()) {
            throw std::runtime_error("No magic states available in graph.");
        }
        float minDist = INT32_MAX;
        target = magic_ids.front();
        for(int m : magic_ids){
            float dist = node1.distance(graph.get_node(m));
            if(dist < minDist){
                minDist = dist;
                target = m; 
            }
        }
    }
    const Node& node2 = graph.get_node(target); 
    return node1.distance(node2);
}

Routing QubitRouter::route_layer(const Layer& layer_gates) const {
    Routing routing;
    std::unordered_set<int> used_nodes;
    
    // Reserve mapped qubit nodes so routes do not pass through occupied data nodes.
    for (int qubit = 0; qubit < circuit.getQubitsVectorSize(); ++qubit) {
        if (circuit.getQubit(qubit) == nullptr) {
            continue;
        }
        int node = mapping.get_mapped_node(qubit);
        if (node < 0) {
            continue;
        }
        used_nodes.insert(node); // Cannot route through qubit nodes.
    }


    /*** Order Layer Gates by node distance length ******/
    std::vector<Gate> ordered_gates;
    ordered_gates.reserve(layer_gates.size());
    ordered_gates.insert(ordered_gates.end(), layer_gates.begin(), layer_gates.end());
    auto ordering = [&](const Gate& a, const Gate& b) {
        return minGateRouteLength(a) < minGateRouteLength(b);
    };

    std::sort(ordered_gates.begin(), ordered_gates.end(), ordering);


    for (const Gate& gate : ordered_gates) {
        Path path;
        if (gate.qubits.size() == 1 && gate.name != "t") {
            // Single-qubit gate (non-t): always executable
            int node = mapping.get_mapped_node(gate.qubits[0]);
            if (node < 0) {
                throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
            }
            path = {node};
        } else if (gate.qubits.size() == 2) {
            // Two-qubit gate: find path between the 2 qubits
            int qubit1 = gate.qubits[0];
            int qubit2 = gate.qubits[1];
            
            int node1 = mapping.get_mapped_node(qubit1);
            int node2 = mapping.get_mapped_node(qubit2);
            if (node1 < 0 || node2 < 0) {
                throw std::runtime_error(
                    "Cannot route gate " + gate.to_string() + ": at least one qubit is unmapped."
                );
            }

            // TODO: route better (improve heuristic) (congestion-avoidance?)
            path = pathStrategy->find_shortest_path(node1, node2, used_nodes);
        }
        else if(gate.name == "t"){ // path to closest magic state 
            int closestDist = INT32_MAX;
            Path closestPath;
            const int start_node = mapping.get_mapped_node(gate.qubits[0]);
            if (start_node < 0) {
                throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
            }
            for(int magicState : graph.get_magic_state_ids()){
                path = pathStrategy->find_shortest_path(start_node, magicState, used_nodes);
                if(path.size() < closestDist){
                    closestDist = path.size();
                    closestPath = path;
                }
            }
            path = closestPath;
        }

        if(path.size() > 0){
            routing.emplace(gate, path);
            used_nodes.insert(path.begin(), path.end());
        }
    }


    return routing;
}

void QubitRouter::route_circuit() {
    std::cout << "Starting qubit routing...\n";

    routing_steps.clear();
    routing_steps.reserve(circuit.getNumLayers());

    while(circuit.getNumLayers() > 0){
        const Layer& topLayer = circuit.getLayer(0);
        /*
        *   Optimization for LayeredCircuit (?)
        *       Since this only needs the first layer,
        *       no need to construct all layers at each routing step.
        *       Only the first can be made and rebuilt from scratch after routing.
        * 
        *   OR (better): change LayeredCircuit::update_layers to not rebuild from scratch, 
        *                instead scan the 2nd layer and move gates to first layer.
        */
        Routing route = route_layer(topLayer);
        if(route.size() == 0){
            std::cout << "Layer " << routing_steps.size()+1 << " empty! Returning incomplete." << std::endl;
            return;
        }

        routing_steps.emplace_back(route);

        // Extract all keys of route (== gates that have been routed)
        std::vector<Gate> used_gates;
        used_gates.reserve(route.size());
        for (const auto& item : route) {
            used_gates.push_back(item.first);
        }

        // Update layering given used gates
        circuit.update_layers(used_gates);
    }


    
    std::cout << "Qubit routing completed.\n";
}

void QubitRouter::print_routing_steps() const {
    for(int i=0; i < routing_steps.size(); i++){
        std::cout << "# Step " << i << " #############" << std::endl;
        print_routing(i);
        std::cout << std::endl;
    }
}

void QubitRouter::print_routing(int i) const {
    for(auto pair : routing_steps[i]){
        std::cout << pair.first.to_string() << ": ";
        Path& p = pair.second;
        for(int step : p)
            if(step == p[0])
                std::cout << step;
            else 
                std::cout << "-" << step;
        std::cout << std::endl;
    }
}
