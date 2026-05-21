#include "routing.hpp"
#include "circuit_metrics.hpp"
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

Path NormalTGateRouting::find_t_gate_path(
    const Gate& gate,
    const Mapping& mapping,
    const Graph& graph,
    const IPathStrategy& path_strategy,
    const std::unordered_set<int>& used_nodes,
    const std::unordered_set<int>& used_magic_states,
    const std::unordered_map<int, std::vector<int>>& magic_state_order_cache
) const {
    (void)magic_state_order_cache;

    int closestDist = INT32_MAX;
    Path closestPath;
    const int start_node = mapping.get_mapped_node(gate.qubits[0]);
    if (start_node < 0) {
        throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
    }

    for (int magicState : graph.get_magic_state_ids()) {
        if (used_magic_states.count(magicState) > 0) {
            continue;
        }
        Path path = path_strategy.find_shortest_path(start_node, magicState, used_nodes);
        if (!path.empty() && static_cast<int>(path.size()) < closestDist) {
            closestDist = path.size();
            closestPath = path;
        }
    }

    return closestPath;
}

Path SmartTGateRouting::find_t_gate_path(
    const Gate& gate,
    const Mapping& mapping,
    const Graph& graph,
    const IPathStrategy& path_strategy,
    const std::unordered_set<int>& used_nodes,
    const std::unordered_set<int>& used_magic_states,
    const std::unordered_map<int, std::vector<int>>& magic_state_order_cache
) const {
    int closestDist = INT32_MAX;
    Path closestPath;
    const int start_node = mapping.get_mapped_node(gate.qubits[0]);
    if (start_node < 0) {
        throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
    }

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
            Path path = path_strategy.find_shortest_path(start_node, magicState, used_nodes);

            if (!path.empty() && static_cast<int>(path.size()) < closestDist) {
                closestDist = path.size();
                closestPath = path;
                failed_attempts = 0;
            } else {
                failed_attempts++;
                if (failed_attempts >= patience_threshold && !closestPath.empty()) {
                    break;
                } else if (failed_attempts >= patience_threshold && closestPath.empty()) {
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
            Path path = path_strategy.find_shortest_path(start_node, magicState, used_nodes);
            if (!path.empty() && static_cast<int>(path.size()) < closestDist) {
                closestDist = path.size();
                closestPath = path;
            }
        }
    }

    return closestPath;
}

void QubitRouter::precompute_magic_state_order() {
    magic_state_order_cache.clear();
    magic_state_order_cache.reserve(circuit.getQubitsVectorSize());

    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
    if (magic_state_ids.empty()) {
        throw std::runtime_error("No magic states available in graph.");
    }

    std::unordered_set<int> blocked_nodes = get_used_nodes();
    for(int mapped_node : blocked_nodes)
        if(!graph.is_magic(mapped_node))
            magic_state_order_cache[mapped_node] = {};

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

int QubitRouter::closestMagicState(const Gate& gate) const {
    const int start_node = mapping.get_mapped_node(gate.qubits[0]);
    int best = -1;

    if(ORDER_GATES_BY_MANHATTAN){
        float minDist = INT32_MAX;
        for(int m : graph.get_magic_state_ids()){
            float dist = graph.get_node(start_node).distance(graph.get_node(m));
            if(dist < minDist){
                minDist = dist;
                best = m; 
            }
        }
    }
    else{
        Path path = tGateRoutingStrategy->find_t_gate_path(
                gate,
                mapping,
                graph,
                *pathStrategy,
                get_used_nodes(),
                {},
                magic_state_order_cache
            );
        if (!path.empty()) {
            best = path.back();
        }
    }

    if(best < 0) throw std::runtime_error("No magic states available in graph.");
    return best;
}

float QubitRouter::minGateRouteLength(const Gate& g) const {
    if (g.qubits.empty()) {
        throw std::runtime_error("Gate without qubits found while computing route length.");
    }
    if(g.name == "h") return 0;

    const int q0 = g.qubits[0];
    const int q1 = g.qubits.size() > 1 ? g.qubits[1] : -1;
    const auto cache_key = std::make_pair(q0, q1);

    const auto cache_it = min_gate_route_length_cache.find(cache_key);
    if (cache_it != min_gate_route_length_cache.end()) {
        return cache_it->second;
    }

    const int mapped_q0 = mapping.get_mapped_node(q0);
    if (mapped_q0 < 0) {
        throw std::runtime_error("Qubit " + std::to_string(q0) + " is not mapped.");
    }
    int target;
    if(g.qubits.size() == 2){
        target = mapping.get_mapped_node(q1);
        if (target < 0) {
            throw std::runtime_error("Qubit " + std::to_string(q1) + " is not mapped.");
        }
    }
    else { // target = closest magic state
        target = closestMagicState(g);
    }

    float result;
    if(ORDER_GATES_BY_MANHATTAN){
        const Node& node1 = graph.get_node(mapped_q0);
        const Node& node2 = graph.get_node(target);
        result = node1.distance(node2);
    }
    else
        result = static_cast<float>(pathStrategy->find_shortest_path(mapped_q0, target, get_used_nodes()).size());

    min_gate_route_length_cache[cache_key] = result;
    return result;
}

std::unordered_set<int> QubitRouter::get_used_nodes() const {
    if(used_nodes_cache.size() > 0) return used_nodes_cache;

    std::unordered_set<int> used_nodes;
    // Reserve mapped qubit nodes so routes do not pass through occupied nodes.
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

    // Also reserve magic state nodes
    if(MAGIC_STOPS_ROUTE)
        used_nodes.insert(graph.get_magic_state_ids().begin(), graph.get_magic_state_ids().end());
    
    used_nodes_cache = used_nodes;
    return used_nodes;
}

Routing QubitRouter::route_layer(const Layer& layer_gates) const {
    // Pure computation: no cache logic here.
    // Cache lookup and insert are handled by the caller (route_circuit).

    // min_gate_route_length_cache.clear();
    Routing routing;
    std::unordered_set<int> used_nodes = get_used_nodes();
    std::unordered_set<int> used_magic_states;

    if (const auto* congestion_strategy = dynamic_cast<const CongestionAwareShortestPath*>(pathStrategy)) {
        congestion_strategy->prepare_for_layer(circuit, mapping, used_nodes);
    }

    /*** Order Layer Gates by node distance length ******/
    // Layer is std::unordered_set<Gate>, whose iteration order depends on Gate::id
    // (the Gate hash combines id and name). Sorting first by (name, qubits) — a key
    // independent of Gate::id — gives a baseline order that's identical for any two
    // layers with the same logical content. The subsequent stable_sort then breaks
    // route-length ties on that baseline, so route_layer becomes deterministic for
    // a given logical layer regardless of which concrete Gate IDs are present.
    std::vector<Gate> ordered_gates;
    ordered_gates.reserve(layer_gates.size());
    ordered_gates.insert(ordered_gates.end(), layer_gates.begin(), layer_gates.end());

    std::sort(ordered_gates.begin(), ordered_gates.end(),
        [](const Gate& a, const Gate& b) {
            if (a.name != b.name) return a.name < b.name;
            return a.qubits < b.qubits;
        });

    std::stable_sort(ordered_gates.begin(), ordered_gates.end(),
        [&](const Gate& a, const Gate& b) {
            return minGateRouteLength(a) < minGateRouteLength(b);
        });


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
            path = tGateRoutingStrategy->find_t_gate_path(
                gate,
                mapping,
                graph,
                *pathStrategy,
                used_nodes,
                used_magic_states,
                magic_state_order_cache
            );
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

    // When the layer cache is active and the path strategy is congestion-aware,
    // force STATIC_GLOBAL so weights are computed once. Cache hits must replay
    // the same routing basis as the original cache-miss routing.
    if (layer_routing_cache != nullptr) {
        if (auto* cong = dynamic_cast<CongestionAwareShortestPath*>(
                const_cast<IPathStrategy*>(pathStrategy))) {
            cong->force_static_mode();
        }
    }

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

        // Compute fingerprint once. Used for both cache lookup and insert below.
        // Only compute when a cache is active (avoids hashing cost when cache is off).
        const size_t layer_fp = (layer_routing_cache != nullptr)
            ? compute_layer_fingerprint(topLayer)
            : 0;

        // Cache hit: get a const reference — no copy inside route_layer, one copy into routing_steps.
        const Routing* cached_route = nullptr;
        if (layer_routing_cache != nullptr) {
            auto it = layer_routing_cache->find(layer_fp);
            if (it != layer_routing_cache->end()) {
                cached_route = &it->second;
            }
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

        Routing computed_route;
        bool was_cache_hit = false;
        bool fingerprint_collision = false;
        if (cached_route != nullptr) {
            // Cache hit: the stored Routing maps Gate objects from the first occurrence of
            // this layer. Gate::operator== includes the gate ID, so those stale Gate objects
            // would not match the current layer's gates in update_layers(), causing it to
            // silently skip removal and loop forever. Rebuild the Routing by matching each
            // cached entry to the current topLayer gate with the same name+qubits.
            // compute_layer_fingerprint is a 64-bit XOR hash and can collide: two different
            // layers may share a fingerprint. Verify every cached gate matches a topLayer
            // gate; if not, treat as cache miss and re-route without overwriting the entry.
            if (cached_route->size() == topLayer.size()) {
                Routing tentative;
                bool all_matched = true;
                for (const auto& [cached_gate, path] : *cached_route) {
                    bool found = false;
                    for (const Gate& cur : topLayer) {
                        if (cur.name == cached_gate.name && cur.qubits == cached_gate.qubits) {
                            tentative.emplace(cur, path);
                            found = true;
                            break;
                        }
                    }
                    if (!found) { all_matched = false; break; }
                }
                if (all_matched) {
                    computed_route = std::move(tentative);
                    was_cache_hit = true;
                } else {
                    fingerprint_collision = true;
                }
            } else {
                fingerprint_collision = true;
            }
        }
        if (!was_cache_hit) {
            computed_route = route_layer(topLayer);
            if (layer_routing_cache != nullptr && !fingerprint_collision) {
                layer_routing_cache->emplace(layer_fp, computed_route);  // copy into cache
            }
        }

        const Routing& route = computed_route;

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

        // Extract routed gates before moving route into routing_steps.
        std::vector<Gate> used_gates;
        used_gates.reserve(route.size());
        for (const auto& item : route) {
            used_gates.push_back(item.first);
        }

        routing_steps.push_back(std::move(computed_route));

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
