// Dependency-aware routers: greedy_lookahead (deterministic, one-step
// lookahead) and dascot_sa (DASCOT-style simulated annealing over the routing
// order of the front layer). Shared machinery lives in
// DependencyAwareRouterBase; see routing.hpp for the strategy descriptions.
#include "routing.hpp"
#include "defines.hpp"

#include <iomanip>
#include <random>

void draw_routing_layer(
    int step_index,
    const Graph& graph,
    const Mapping& mapping,
    const Layer& layer_gates,
    const Routing& routing
);

std::unordered_map<int, int> compute_gate_tails(const std::vector<Gate>& gates) {
    std::unordered_map<int, int> tail_by_id;
    tail_by_id.reserve(gates.size());

    std::unordered_map<uint32_t, int> next_tail_on_qubit;  // qubit -> tail of next gate on it
    for (auto it = gates.rbegin(); it != gates.rend(); ++it) {
        const Gate& g = *it;
        int tail = 1;
        for (const uint32_t q : g.qubits) {
            const auto found = next_tail_on_qubit.find(q);
            if (found != next_tail_on_qubit.end()) {
                tail = std::max(tail, 1 + found->second);
            }
        }
        tail_by_id[g.id] = tail;
        for (const uint32_t q : g.qubits) {
            next_tail_on_qubit[q] = tail;
        }
    }
    return tail_by_id;
}

DependencyAwareRouterBase::DependencyAwareRouterBase(
    const Mapping& m, LayeredCircuit& c, const Graph& g
) : mapping(m), circuit(c), graph(g) {
    gate_tail_by_id = compute_gate_tails(c.getGates());
}

std::unordered_set<int> DependencyAwareRouterBase::base_blocked_nodes() const {
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

// Same A* as NaiveShortestPath::find_shortest_path (unit costs, Manhattan
// heuristic, destination exempt from the blocked set).
Path DependencyAwareRouterBase::shortest_available_path(
    int start_node, int end_node, const std::unordered_set<int>& blocked
) const {
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

    using QueueItem = std::pair<float, int>;  // (f = g + h, node)
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

        if (closed[current]) continue;
        closed[current] = 1;

        const int tentative = g_cost[current] + 1;
        for (int neighbor : graph.neighbors(current)) {
            if (neighbor != end_node && blocked.count(neighbor) > 0) {
                continue;
            }
            if (tentative < g_cost[neighbor]) {
                g_cost[neighbor] = tentative;
                parent[neighbor] = current;
                open.push({static_cast<float>(tentative) + heuristic(neighbor), neighbor});
            }
        }
    }

    return {};
}

Path DependencyAwareRouterBase::find_gate_path(
    const Gate& gate,
    const std::unordered_set<int>& blocked,
    const std::unordered_set<int>& used_magic_states
) const {
    if (gate.qubits.size() == 2) {
        const int node1 = mapping.get_mapped_node(gate.qubits[0]);
        const int node2 = mapping.get_mapped_node(gate.qubits[1]);
        if (node1 < 0 || node2 < 0) {
            throw std::runtime_error(
                "Cannot route gate " + gate.to_string() + ": at least one qubit is unmapped."
            );
        }
        return shortest_available_path(node1, node2, blocked);
    }

    if (gate.name == "t") {
        const int start_node = mapping.get_mapped_node(gate.qubits[0]);
        if (start_node < 0) {
            throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
        }
        Path best;
        std::size_t best_size = std::numeric_limits<std::size_t>::max();
        for (int magic : graph.get_magic_state_ids()) {
            if (used_magic_states.count(magic)) continue;
            Path p = shortest_available_path(start_node, magic, blocked);
            if (!p.empty() && p.size() < best_size) {
                best_size = p.size();
                best = std::move(p);
            }
        }
        return best;
    }

    std::cout << "ERROR. Unhandled Gate " << gate.to_string() << ".\n";
    throw std::runtime_error("Unhandled Gate.");
}

std::vector<Gate> DependencyAwareRouterBase::deterministic_gate_order(const Layer& layer_gates) {
    std::vector<Gate> ordered(layer_gates.begin(), layer_gates.end());
    std::sort(ordered.begin(), ordered.end(),
        [](const Gate& a, const Gate& b) {
            if (a.name != b.name) return a.name < b.name;
            return a.qubits < b.qubits;
        });
    return ordered;
}

void DependencyAwareRouterBase::route_circuit() {
    routing_steps.clear();
    routing_steps.reserve(circuit.getNumLayers());
    non_routed_histogram.clear();

    first_exposure_total = 0;
    first_exposure_routed = 0;
    std::unordered_set<Gate> seen_gates;

    while (circuit.getNumLayers() > 0) {
        const Layer& topLayer = circuit.getLayer(0);

        if (PRINT_ROUTING_PROGRESS) {
            std::cout << "Dependency-routing, " << circuit.getNumLayers() << " Layers remaining...\n";
        }

        if (topLayer.empty()) {
            throw std::runtime_error("Layer is empty: no gates to route.");
        }

        Routing route = route_layer_dependency(topLayer);

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
                "Dependency routing made no progress at layer " + std::to_string(routing_steps.size() + 1) +
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

void DependencyAwareRouterBase::print_routing_steps() const {
    for (std::size_t i = 0; i < routing_steps.size(); i++) {
        std::cout << "# Step " << i << " #############" << std::endl;
        print_routing(static_cast<int>(i));
        std::cout << std::endl;
    }
}

void DependencyAwareRouterBase::print_routing(int i) const {
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

void DependencyAwareRouterBase::print_non_routed_histogram() const {
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

// ---------------------------------------------------------------------------
// greedy_lookahead
// ---------------------------------------------------------------------------

Routing GreedyLookaheadRouter::route_layer_dependency(const Layer& layer_gates) const {
    std::unordered_set<int> blocked = base_blocked_nodes();
    std::unordered_set<int> used_magic_states;
    Routing routing;

    const std::vector<Gate> ordered_gates = deterministic_gate_order(layer_gates);

    // Candidate = a non-trivial gate with its current shortest available path.
    // Paths stay valid until a committed path consumes one of their nodes, so
    // after each commit only the invalidated candidates are re-searched.
    struct Candidate {
        Gate gate;
        Path path;      // empty = currently unroutable (kept for re-search on T-release)
        int crit;
        bool is_t;
    };
    std::vector<Candidate> candidates;
    candidates.reserve(ordered_gates.size());

    for (const Gate& gate : ordered_gates) {
        if (gate.qubits.size() == 1 && gate.name != "t") {
            // Trivial single-qubit gate: executes in place, never conflicts
            // (its node is a mapped qubit node, untraversable by other paths).
            const int node = mapping.get_mapped_node(gate.qubits[0]);
            if (node < 0) {
                throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
            }
            routing.emplace(gate, Path{node});
            continue;
        }
        candidates.push_back({gate, {}, gate_criticality(gate), gate.name == "t"});
    }

    for (Candidate& c : candidates) {
        c.path = find_gate_path(c.gate, blocked, used_magic_states);
    }

    std::vector<char> committed(candidates.size(), 0);

    while (true) {
        // Interference mass: for each candidate g, the criticality of the other
        // routable candidates whose current path shares a node with p_g. Built
        // via a node -> candidates index so the cost is linear in total path
        // nodes instead of quadratic in the front size.
        std::unordered_map<int, std::vector<std::size_t>> node_users;
        long long total_crit = 0;
        for (std::size_t i = 0; i < candidates.size(); ++i) {
            if (committed[i] || candidates[i].path.empty()) continue;
            total_crit += candidates[i].crit;
            for (const int node : candidates[i].path) {
                node_users[node].push_back(i);
            }
        }

        int best_idx = -1;
        float best_score = 0.0f;
        std::vector<char> touched(candidates.size(), 0);
        std::vector<std::size_t> touched_list;

        for (std::size_t i = 0; i < candidates.size(); ++i) {
            if (committed[i] || candidates[i].path.empty()) continue;
            const Candidate& c = candidates[i];

            // Criticality of candidates overlapping p_i (self included).
            long long overlap_crit = 0;
            touched_list.clear();
            for (const int node : c.path) {
                const auto it = node_users.find(node);
                if (it == node_users.end()) continue;
                for (const std::size_t j : it->second) {
                    if (!touched[j]) {
                        touched[j] = 1;
                        touched_list.push_back(j);
                        overlap_crit += candidates[j].crit;
                    }
                }
            }
            for (const std::size_t j : touched_list) touched[j] = 0;

            const long long future = total_crit - overlap_crit;  // disjoint candidates' criticality
            const float score = alpha * static_cast<float>(c.crit)
                              - beta * static_cast<float>(c.path.size())
                              + eta * static_cast<float>(future);

            // Ties: shorter path, then the deterministic candidate order.
            const bool better =
                best_idx < 0 ||
                score > best_score ||
                (score == best_score &&
                 c.path.size() < candidates[best_idx].path.size());
            if (better) {
                best_idx = static_cast<int>(i);
                best_score = score;
            }
        }

        if (best_idx < 0) break;

        // Commit the winner and invalidate only the overlapping candidates.
        Candidate& winner = candidates[best_idx];
        committed[best_idx] = 1;
        blocked.insert(winner.path.begin(), winner.path.end());
        if (winner.is_t) used_magic_states.insert(winner.path.back());
        routing.emplace(winner.gate, winner.path);
        const int taken_magic = winner.is_t ? winner.path.back() : -1;

        for (std::size_t i = 0; i < candidates.size(); ++i) {
            if (committed[i] || candidates[i].path.empty()) continue;
            bool invalid = false;
            for (const int node : candidates[i].path) {
                if (blocked.count(node) || node == taken_magic) { invalid = true; break; }
            }
            if (invalid) {
                candidates[i].path = find_gate_path(candidates[i].gate, blocked, used_magic_states);
            }
        }
    }

    return routing;
}

// ---------------------------------------------------------------------------
// dascot_sa
// ---------------------------------------------------------------------------

AnnealingOrderRouter::SeqResult AnnealingOrderRouter::evaluate_order(
    const std::vector<Gate>& order,
    const std::unordered_set<int>& blocked
) const {
    SeqResult result;
    std::unordered_set<int> blocked_now = blocked;
    std::unordered_set<int> used_magic_states;

    for (const Gate& gate : order) {
        Path path = find_gate_path(gate, blocked_now, used_magic_states);
        if (path.empty()) continue;  // skipped: stays for the next step

        blocked_now.insert(path.begin(), path.end());
        if (gate.name == "t") used_magic_states.insert(path.back());
        result.gain += gate_criticality(gate);
        result.total_nodes += path.size();
        result.routing.emplace(gate, std::move(path));
    }
    return result;
}

Routing AnnealingOrderRouter::route_layer_dependency(const Layer& layer_gates) const {
    const std::unordered_set<int> blocked = base_blocked_nodes();
    Routing trivial_routing;

    const std::vector<Gate> ordered_gates = deterministic_gate_order(layer_gates);

    std::vector<Gate> order;  // non-trivial gates, subject to the order search
    order.reserve(ordered_gates.size());
    long long max_gain = 0;
    for (const Gate& gate : ordered_gates) {
        if (gate.qubits.size() == 1 && gate.name != "t") {
            const int node = mapping.get_mapped_node(gate.qubits[0]);
            if (node < 0) {
                throw std::runtime_error("Qubit " + std::to_string(gate.qubits[0]) + " was not mapped.");
            }
            trivial_routing.emplace(gate, Path{node});
            continue;
        }
        order.push_back(gate);
        max_gain += gate_criticality(gate);
    }

    const auto merge_trivial = [&](Routing routed) {
        routed.insert(trivial_routing.begin(), trivial_routing.end());
        return routed;
    };

    if (order.empty()) return trivial_routing;

    // Initial order: criticality descending (the DASCOT cost premia critical
    // gates, so this is the natural warm start), route length untouched — the
    // deterministic base order is the stable tiebreak.
    std::stable_sort(order.begin(), order.end(),
        [this](const Gate& a, const Gate& b) {
            return gate_criticality(a) > gate_criticality(b);
        });

    SeqResult best = evaluate_order(order, blocked);

    // A full route (gain == max_gain) is provably optimal for this cost, so
    // the SA budget is only spent on genuinely congested steps.
    if (best.gain == max_gain || order.size() < 2 || sa_iterations <= 0) {
        return merge_trivial(std::move(best.routing));
    }

    // Deterministic per-step seed: same circuit + same step index -> same result.
    std::mt19937 rng(sa_seed + static_cast<unsigned int>(routing_steps.size()));
    std::uniform_int_distribution<std::size_t> pick(0, order.size() - 1);
    std::uniform_real_distribution<double> unif(0.0, 1.0);

    // Temperature scale from the problem: swapping two gates changes the gain
    // by at most ~the largest tail in the layer.
    double t0 = 1.0;
    for (const Gate& g : order) {
        t0 = std::max(t0, static_cast<double>(gate_criticality(g)));
    }
    const double t_end = 0.05;

    long long current_gain = best.gain;
    std::size_t current_nodes = best.total_nodes;

    for (int iter = 0; iter < sa_iterations; ++iter) {
        const double frac = sa_iterations > 1
            ? static_cast<double>(iter) / static_cast<double>(sa_iterations - 1)
            : 1.0;
        const double temperature = t0 * std::pow(t_end / t0, frac);

        std::size_t i = pick(rng);
        std::size_t j = pick(rng);
        if (i == j) continue;

        std::swap(order[i], order[j]);
        SeqResult candidate = evaluate_order(order, blocked);

        const long long delta = candidate.gain - current_gain;
        // Equal-gain moves that consume fewer nodes are accepted too: they walk
        // the plateau toward tighter packings without losing progress.
        const bool accept =
            delta > 0 ||
            (delta == 0 && candidate.total_nodes <= current_nodes) ||
            (delta < 0 && unif(rng) < std::exp(static_cast<double>(delta) / temperature));

        if (!accept) {
            std::swap(order[i], order[j]);  // revert
            continue;
        }

        current_gain = candidate.gain;
        current_nodes = candidate.total_nodes;

        const bool new_best =
            candidate.gain > best.gain ||
            (candidate.gain == best.gain && candidate.total_nodes < best.total_nodes);
        if (new_best) {
            best = std::move(candidate);
            if (best.gain == max_gain) break;  // optimum reached
        }
    }

    return merge_trivial(std::move(best.routing));
}
