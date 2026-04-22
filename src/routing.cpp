#include "routing.hpp"
#include <map>
#include <iomanip>

void draw_routing_layer(
    int step_index,
    const Graph& graph,
    const Mapping& mapping,
    const Layer& layer_gates,
    const Routing& routing
);

namespace {
void print_non_routed_histogram(const std::map<std::size_t, std::size_t>& non_routed_histogram) {
    std::cout << "\n\033[35mNon-routed gates histogram (top layer per step)\033[0m\n";
    const int col1w = 45;
    const int col2w = 8;
    std::cout << "\033[35m" << std::left
              << std::setw(col1w) << "number of non routed gates in the top layer"
              << std::right << std::setw(col2w) << "count"
              << "\033[0m\n";
    std::cout << "\033[35m" << std::string(col1w + col2w, '-') << "\033[0m\n";
    for (const auto& [value, count] : non_routed_histogram) {
        std::cout << "\033[35m" << std::left << std::setw(col1w) << value
                  << std::right << std::setw(col2w) << count << "\033[0m\n";
    }
}
}

void QubitRouter::precompute_magic_state_order() {
    magic_state_order_cache.clear();
    magic_state_order_cache.reserve(circuit.getQubitsVectorSize());

    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
    if (magic_state_ids.empty()) {
        throw std::runtime_error("No magic states available in graph.");
    }

    std::unordered_set<int> blocked_nodes;
    blocked_nodes.reserve(circuit.getQubitsVectorSize() + magic_state_ids.size());

    for (int qubit = 0; qubit < circuit.getQubitsVectorSize(); ++qubit) {
        if (circuit.getQubit(qubit) == nullptr) {
            continue;
        }

        const int mapped_node = mapping.get_mapped_node(qubit);
        if (mapped_node < 0) {
            throw std::runtime_error("Qubit " + std::to_string(qubit) + " is not mapped.");
        }

        blocked_nodes.insert(mapped_node);
        magic_state_order_cache[mapped_node] = {};
    }

    if (MAGIC_STOPS_ROUTE) {
        blocked_nodes.insert(magic_state_ids.begin(), magic_state_ids.end());
    }

    if (const auto* congestion_strategy = dynamic_cast<const CongestionAwareShortestPath*>(pathStrategy)) {
        congestion_strategy->prepare_for_layer(circuit, mapping, blocked_nodes);
    }

    for (auto& cache_entry : magic_state_order_cache) {
        const int start_node = cache_entry.first;
        std::vector<std::pair<std::size_t, int>> ranked_magic_states;
        ranked_magic_states.reserve(magic_state_ids.size());

        for (int magic_state : magic_state_ids) {
            const Path path = pathStrategy->find_shortest_path(start_node, magic_state, blocked_nodes);
            if (!path.empty()) {
                ranked_magic_states.emplace_back(path.size(), magic_state);
            }
        }

        std::sort(
            ranked_magic_states.begin(),
            ranked_magic_states.end(),
            [](const std::pair<std::size_t, int>& lhs, const std::pair<std::size_t, int>& rhs) {
                if (lhs.first != rhs.first) {
                    return lhs.first < rhs.first;
                }
                return lhs.second < rhs.second;
            }
        );

        std::vector<int>& ordered_magic_states = cache_entry.second;
        ordered_magic_states.reserve(ranked_magic_states.size());
        for (const auto& ranked_magic_state : ranked_magic_states) {
            ordered_magic_states.push_back(ranked_magic_state.second);
        }
    }
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
        // TODO(static-magic-ranking): once the cache exists, use the first cached
        // magic-state candidate for the mapped node instead of geometric distance.
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
    std::unordered_set<int> used_magic_states;
    
    // Reserve mapped qubit and magic state nodes so routes do not pass through occupied nodes.
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

    if(MAGIC_STOPS_ROUTE)
        for (int magic_state : graph.get_magic_state_ids()) {
            used_nodes.insert(magic_state);
        }

    if (const auto* congestion_strategy = dynamic_cast<const CongestionAwareShortestPath*>(pathStrategy)) {
        congestion_strategy->prepare_for_layer(circuit, mapping, used_nodes);
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

            const bool use_smart_t_routing = (t_routing_mode == "smart_t_routing");

            int closestDist = INT32_MAX;
            Path closestPath;
            const int start_node = mapping.get_mapped_node(gate.qubits[0]);
            if (start_node < 0) {
                throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
            }
            if(!use_smart_t_routing){   
                for(int magicState : graph.get_magic_state_ids()){
                    if (used_magic_states.count(magicState) > 0) {
                        continue;
                    }
                    path = pathStrategy->find_shortest_path(start_node, magicState, used_nodes);
                    if(!path.empty() && static_cast<int>(path.size()) < closestDist){
                        closestDist = path.size();
                        closestPath = path;
                    }
                }
            }
            else{
                const auto cache_it = magic_state_order_cache.find(start_node);
                int failed_attempts = 0;
                bool fallback_to_unranked_search = false;

                if (cache_it == magic_state_order_cache.end() || cache_it->second.empty()) {
                    fallback_to_unranked_search = true;
                } else {
                    for (int magicState : cache_it->second) {
                        if (used_magic_states.count(magicState) > 0) {
                            continue;
                        }
                        path = pathStrategy->find_shortest_path(start_node, magicState, used_nodes);

                        if (!path.empty() && static_cast<int>(path.size()) < closestDist) {
                            closestDist = path.size();
                            closestPath = path;
                            failed_attempts = 0;
                        } else {
                            failed_attempts++;
                            if (failed_attempts >= patience_threshold  && !closestPath.empty()) {
                                break;
                            }else if (failed_attempts >= patience_threshold && closestPath.empty()) {
                                failed_attempts = 0;
                            }
                        }
                    }
                }

                // If there are empty elements in the magic state map, fallback to unranked search among all magic states.
                if (fallback_to_unranked_search) {
                    for (int magicState : graph.get_magic_state_ids()) {
                        if (used_magic_states.count(magicState) > 0) {
                            continue;
                        }
                        path = pathStrategy->find_shortest_path(start_node, magicState, used_nodes);
                        if (!path.empty() && static_cast<int>(path.size()) < closestDist) {
                            closestDist = path.size();
                            closestPath = path;
                        }
                    }
                }
            }
            path = closestPath;
        }
        else{
            std::cout << "ERROR. Unhandled Gate " << gate.to_string() << ".\n";
            throw std::runtime_error("Unhandled Gate.");
        }

        if (path.size() > 0) {
            routing.emplace(gate, path);
            used_nodes.insert(path.begin(), path.end());
            if (gate.name == "t") {
                used_magic_states.insert(path.back());
            }
        }
    }


    return routing;
}

void QubitRouter::route_circuit() {
    std::cout << "Starting qubit routing...\n";

    routing_steps.clear();
    routing_steps.reserve(circuit.getNumLayers());
    std::map<std::size_t, std::size_t> non_routed_histogram;

    while(circuit.getNumLayers() > 0){
        const Layer& topLayer = circuit.getLayer(0);
        
        if(PRINT_ROUTING_PROGRESS){
            std::cout << "Routing, " << circuit.getNumLayers() << " Layers remaining...\n";
            std::cout << "TopLayer gates (" << topLayer.size() << "):\n";
            for (const auto& gate : topLayer) {
                std::cout << "  " << gate.to_string() << "\n";
            }
        }        
        
        if (topLayer.empty()) {
            throw std::runtime_error("Layer is empty: no gates to route.");
        }
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
        draw_routing_layer(
            static_cast<int>(routing_steps.size()) + 1,
            graph,
            mapping,
            topLayer,
            route
        );
        
        const std::size_t non_routed = topLayer.size() - route.size();
        if(non_routed > 0)
            non_routed_histogram[non_routed]++;

        if(route.size() == 0){
            std::cout << "ERROR trying to route layer with " << topLayer.size() << " gates:" << std::endl;
            for (const auto& gate : topLayer) {
                std::cout << "  " << gate.to_string() << std::endl;
            }
            throw std::runtime_error(
                "Routing made no progress at layer " + std::to_string(routing_steps.size() + 1) +
                ": no routeable gate found with current constraints."
            );
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
    if (!non_routed_histogram.empty()) {
        print_non_routed_histogram(non_routed_histogram);
    }
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
