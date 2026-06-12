#include "routing.hpp"
#include "defines.hpp"

#include <iomanip>
#include <map>

void draw_routing_layer(
    int step_index,
    const Graph& graph,
    const Mapping& mapping,
    const Layer& layer_gates,
    const Routing& routing
);

std::unordered_set<int> PackingQubitRouter::base_blocked_nodes() const {
    std::unordered_set<int> blocked;
    for (int qubit = 0; qubit < circuit.getQubitsVectorSize(); ++qubit) {
        if (circuit.getQubit(qubit) == nullptr) {
            continue;
        }
        const int node = mapping.get_mapped_node(qubit);
        if (node >= 0) {
            blocked.insert(node);
        }
    }
    if (MAGIC_STOPS_ROUTE) {
        blocked.insert(graph.get_magic_state_ids().begin(), graph.get_magic_state_ids().end());
    }
    return blocked;
}

// Dijkstra where entering node v costs 1 + penalties[v]. Nodes in `blocked` are
// not traversable except as the destination (mirrors NaiveShortestPath's
// `neighbor == end_node ||` exemption so mapped/magic endpoints stay reachable).
Path PackingQubitRouter::penalized_shortest_path(
    int start_node,
    int end_node,
    const std::unordered_set<int>& blocked,
    const std::unordered_map<int, float>& penalties
) const {
    if (start_node == end_node) return {start_node};

    using QueueItem = std::pair<float, int>;
    std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<QueueItem>> pq;
    std::unordered_map<int, float> distance;
    std::unordered_map<int, int> parent;

    distance[start_node] = 0.0f;
    parent[start_node] = -1;
    pq.push({0.0f, start_node});

    while (!pq.empty()) {
        const auto [current_cost, current] = pq.top();
        pq.pop();

        const auto best_it = distance.find(current);
        if (best_it == distance.end() || current_cost > best_it->second) {
            continue;
        }
        if (current == end_node) {
            break;
        }

        for (int neighbor : graph.neighbors(current)) {
            const bool traversable = (neighbor == end_node) || (blocked.count(neighbor) == 0);
            if (!traversable) {
                continue;
            }

            float step_cost = 1.0f;
            const auto penalty_it = penalties.find(neighbor);
            if (penalty_it != penalties.end()) {
                step_cost += penalty_it->second;
            }

            const float new_cost = current_cost + step_cost;
            const auto old_it = distance.find(neighbor);
            if (old_it == distance.end() || new_cost < old_it->second) {
                distance[neighbor] = new_cost;
                parent[neighbor] = current;
                pq.push({new_cost, neighbor});
            }
        }
    }

    if (parent.find(end_node) == parent.end()) {
        return {};
    }

    Path path;
    for (int node = end_node; node != -1; node = parent[node]) {
        path.push_back(node);
    }
    std::reverse(path.begin(), path.end());
    return path;
}

Routing PackingQubitRouter::route_layer_packing(const Layer& layer_gates) const {
    const std::unordered_set<int> blocked = base_blocked_nodes();

    // Deterministic gate order independent of Gate::id (same trick as QubitRouter).
    std::vector<Gate> ordered_gates(layer_gates.begin(), layer_gates.end());
    std::sort(ordered_gates.begin(), ordered_gates.end(),
        [](const Gate& a, const Gate& b) {
            if (a.name != b.name) return a.name < b.name;
            return a.qubits < b.qubits;
        });

    // Downstream criticality: how many gates in the next criticality_lookahead
    // layers touch each qubit. Routing a gate whose qubits are in high demand
    // unblocks more future work, so it deserves priority in the packing.
    std::unordered_map<uint32_t, int> qubit_pressure;
    for (int layer_idx = 1; layer_idx <= criticality_lookahead; ++layer_idx) {
        const Layer& future_layer = circuit.getLayer(layer_idx);
        for (const Gate& g : future_layer) {
            for (const uint32_t q : g.qubits) {
                qubit_pressure[q]++;
            }
        }
    }
    const auto criticality_of = [&qubit_pressure](const Gate& g) {
        int crit = 0;
        for (const uint32_t q : g.qubits) {
            const auto it = qubit_pressure.find(q);
            if (it != qubit_pressure.end()) crit += it->second;
        }
        return crit;
    };

    Routing routing;
    std::unordered_set<int> selected_nodes;   // nodes consumed by accepted paths
    std::unordered_set<int> used_magic_states;

    struct Candidate {
        Gate gate;
        Path path;
        int crit;
        bool is_t;
        int magic;     // -1 for non-T
        int order;     // insertion order, final tie-break
    };
    std::vector<Candidate> candidates;
    std::vector<Gate> pending;  // non-trivial gates, for the fill pass

    int insertion_order = 0;
    for (const Gate& gate : ordered_gates) {
        if (gate.qubits.size() == 1 && gate.name != "t") {
            // Trivial single-qubit gate: executes in place, can never conflict
            // (its node is a mapped qubit node, untraversable by other paths).
            const int node = mapping.get_mapped_node(gate.qubits[0]);
            if (node < 0) {
                throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
            }
            routing.emplace(gate, Path{node});
            selected_nodes.insert(node);
            continue;
        }

        const int crit = criticality_of(gate);

        if (gate.qubits.size() == 2) {
            const int node1 = mapping.get_mapped_node(gate.qubits[0]);
            const int node2 = mapping.get_mapped_node(gate.qubits[1]);
            if (node1 < 0 || node2 < 0) {
                throw std::runtime_error(
                    "Cannot route gate " + gate.to_string() + ": at least one qubit is unmapped."
                );
            }
            // Diverse candidates: after each found path, penalize its interior
            // nodes so the next search prefers a different corridor.
            std::unordered_map<int, float> penalties;
            std::vector<Path> gate_paths;
            for (int c = 0; c < num_candidates; ++c) {
                Path path = penalized_shortest_path(node1, node2, blocked, penalties);
                if (path.empty()) break;
                if (std::find(gate_paths.begin(), gate_paths.end(), path) != gate_paths.end()) {
                    break;  // penalization re-produced a known path: no more diversity
                }
                for (std::size_t k = 1; k + 1 < path.size(); ++k) {
                    penalties[path[k]] += diversity_penalty;
                }
                gate_paths.push_back(path);
                candidates.push_back({gate, std::move(path), crit, false, -1, insertion_order++});
            }
            pending.push_back(gate);
        } else if (gate.name == "t") {
            const int start_node = mapping.get_mapped_node(gate.qubits[0]);
            if (start_node < 0) {
                throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
            }
            // Candidates = shortest path to each reachable magic state, keep the
            // num_candidates closest. Distinct magic targets give path diversity.
            std::vector<std::pair<std::size_t, std::pair<int, Path>>> ranked;
            for (int magic : graph.get_magic_state_ids()) {
                Path path = penalized_shortest_path(start_node, magic, blocked, {});
                if (!path.empty()) {
                    ranked.push_back({path.size(), {magic, std::move(path)}});
                }
            }
            std::sort(ranked.begin(), ranked.end(),
                [](const auto& a, const auto& b) {
                    if (a.first != b.first) return a.first < b.first;
                    return a.second.first < b.second.first;
                });
            const int keep = std::min<int>(num_candidates, static_cast<int>(ranked.size()));
            for (int c = 0; c < keep; ++c) {
                candidates.push_back({gate, std::move(ranked[c].second.second), crit, true,
                                      ranked[c].second.first, insertion_order++});
            }
            pending.push_back(gate);
        } else {
            std::cout << "ERROR. Unhandled Gate " << gate.to_string() << ".\n";
            throw std::runtime_error("Unhandled Gate.");
        }
    }

    // Selection: highest criticality first, then shorter path, then insertion
    // order (which already encodes the deterministic gate order).
    std::stable_sort(candidates.begin(), candidates.end(),
        [](const Candidate& a, const Candidate& b) {
            if (a.crit != b.crit) return a.crit > b.crit;
            if (a.path.size() != b.path.size()) return a.path.size() < b.path.size();
            return a.order < b.order;
        });

    std::unordered_set<int> routed_gate_orders;  // gates already satisfied, by first candidate order
    const auto gate_is_routed = [&routing](const Gate& g) {
        return routing.find(g) != routing.end();
    };
    const auto path_conflicts = [&selected_nodes](const Path& p) {
        for (const int node : p) {
            if (selected_nodes.count(node)) return true;
        }
        return false;
    };

    for (const Candidate& cand : candidates) {
        if (gate_is_routed(cand.gate)) continue;
        if (cand.is_t && used_magic_states.count(cand.magic)) continue;
        if (path_conflicts(cand.path)) continue;

        selected_nodes.insert(cand.path.begin(), cand.path.end());
        if (cand.is_t) used_magic_states.insert(cand.magic);
        routing.emplace(cand.gate, cand.path);
    }

    // Fill pass: gates whose candidates all conflicted may still fit along a
    // fresh detour around the selected paths. Guarantees maximality: after this
    // loop no routeable gate is left unrouted.
    std::unordered_set<int> fill_blocked = blocked;
    fill_blocked.insert(selected_nodes.begin(), selected_nodes.end());

    std::stable_sort(pending.begin(), pending.end(),
        [&criticality_of](const Gate& a, const Gate& b) {
            return criticality_of(a) > criticality_of(b);
        });

    for (const Gate& gate : pending) {
        if (gate_is_routed(gate)) continue;

        Path path;
        if (gate.qubits.size() == 2) {
            path = penalized_shortest_path(
                mapping.get_mapped_node(gate.qubits[0]),
                mapping.get_mapped_node(gate.qubits[1]),
                fill_blocked, {}
            );
        } else {  // T gate
            const int start_node = mapping.get_mapped_node(gate.qubits[0]);
            std::size_t best_size = std::numeric_limits<std::size_t>::max();
            for (int magic : graph.get_magic_state_ids()) {
                if (used_magic_states.count(magic)) continue;
                Path p = penalized_shortest_path(start_node, magic, fill_blocked, {});
                if (!p.empty() && p.size() < best_size) {
                    best_size = p.size();
                    path = std::move(p);
                }
            }
        }

        if (!path.empty()) {
            fill_blocked.insert(path.begin(), path.end());
            if (gate.name == "t") used_magic_states.insert(path.back());
            routing.emplace(gate, std::move(path));
        }
    }

    return routing;
}

void PackingQubitRouter::route_circuit() {
    routing_steps.clear();
    routing_steps.reserve(circuit.getNumLayers());
    non_routed_histogram.clear();

    first_exposure_total = 0;
    first_exposure_routed = 0;
    std::unordered_set<Gate> seen_gates;

    while (circuit.getNumLayers() > 0) {
        const Layer& topLayer = circuit.getLayer(0);

        if (PRINT_ROUTING_PROGRESS) {
            std::cout << "Packing-routing, " << circuit.getNumLayers() << " Layers remaining...\n";
        }

        if (topLayer.empty()) {
            throw std::runtime_error("Layer is empty: no gates to route.");
        }

        Routing route = route_layer_packing(topLayer);

        draw_routing_layer(
            static_cast<int>(routing_steps.size()) + 1,
            graph,
            mapping,
            topLayer,
            route
        );

        const std::size_t non_routed = topLayer.size() - route.size();
        if (non_routed > 0) {
            non_routed_histogram[non_routed]++;
        }

        for (const Gate& gate : topLayer) {
            if (seen_gates.insert(gate).second) {
                ++first_exposure_total;
                if (route.find(gate) != route.end()) {
                    ++first_exposure_routed;
                }
            }
        }

        if (route.size() == 0) {
            std::cout << "ERROR trying to route layer with " << topLayer.size() << " gates:" << std::endl;
            for (const auto& gate : topLayer) {
                std::cout << "  " << gate.to_string() << std::endl;
            }
            throw std::runtime_error(
                "Packing routing made no progress at layer " + std::to_string(routing_steps.size() + 1) +
                ": no routeable gate found with current constraints."
            );
        }

        std::vector<Gate> used_gates;
        used_gates.reserve(route.size());
        for (const auto& item : route) {
            used_gates.push_back(item.first);
        }

        routing_steps.push_back(std::move(route));
        circuit.update_layers(used_gates);
    }
}

void PackingQubitRouter::print_routing_steps() const {
    for (std::size_t i = 0; i < routing_steps.size(); i++) {
        std::cout << "# Step " << i << " #############" << std::endl;
        print_routing(static_cast<int>(i));
        std::cout << std::endl;
    }
}

void PackingQubitRouter::print_routing(int i) const {
    for (const auto& pair : routing_steps[i]) {
        std::cout << pair.first.to_string() << ": ";
        const Path& p = pair.second;
        for (std::size_t k = 0; k < p.size(); ++k) {
            if (k > 0) std::cout << "-";
            std::cout << p[k];
        }
        std::cout << std::endl;
    }
}

void PackingQubitRouter::print_non_routed_histogram() const {
    if (non_routed_histogram.empty()) return;

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
