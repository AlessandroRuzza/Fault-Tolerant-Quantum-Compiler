#include "boost_router.hpp"

#include <numeric>
#include <limits>
#include <map>
#include <iomanip>
#include <algorithm>

static constexpr float HARD_BLOCK_WEIGHT = 1e9f; 

// ---------------------------------------------------------------------------
// Construction
// ---------------------------------------------------------------------------

Boost_QubitRouter::Boost_QubitRouter(
    const Mapping&  m,
    LayeredCircuit& c,
    const Graph&    g,
    int   max_rrr_iterations,
    float congestion_penalty
)
    : mapping(m), circuit(c), graph(g),
      max_rrr_iterations(max_rrr_iterations),
      congestion_penalty(congestion_penalty),
      num_nodes(g.get_node_count())
{
    build_boost_graph();
}

void Boost_QubitRouter::build_boost_graph() {
    bgraph = BGraph(num_nodes);
    // Add both directed edges u→v and v→u for every undirected device edge.
    // Initial weights are 1.0f; update_edge_weights overwrites them before
    // every Dijkstra call.
    for (int u = 0; u < num_nodes; ++u) {
        for (int v : graph.neighbors(u)) {
            boost::add_edge(u, v, 1.0f, bgraph);
        }
    }
}

// ---------------------------------------------------------------------------
// Edge-weight management
// ---------------------------------------------------------------------------

void Boost_QubitRouter::update_edge_weights(
    const std::vector<float>& node_congestion,
    const std::unordered_set<int>& hard_blocked
) const {
    auto weight_map = boost::get(boost::edge_weight, bgraph);
    for (auto [ei, ei_end] = boost::edges(bgraph); ei != ei_end; ++ei) {
        const int v = static_cast<int>(boost::target(*ei, bgraph));
        const float w = hard_blocked.count(v)
            ? HARD_BLOCK_WEIGHT
            : 1.0f + congestion_penalty * node_congestion[v];
        boost::put(weight_map, *ei, w);
    }
}

// ---------------------------------------------------------------------------
// Dijkstra helpers
// ---------------------------------------------------------------------------

// Reconstruct predecessor map into a Path from start to end.
// Returns empty if end is unreachable.
static Path reconstruct_path(int start, int end, const std::vector<int>& pred, int num_nodes) {
    if (end == start) return {start};
    if (pred[end] == end) return {};  // predecessor not updated = unreachable

    Path path;
    path.reserve(static_cast<size_t>(num_nodes));
    for (int v = end; v != start; v = pred[v]) {
        if (static_cast<int>(path.size()) > num_nodes) return {};  // cycle guard
        path.push_back(v);
    }
    path.push_back(start);
    std::reverse(path.begin(), path.end());
    return path;
}

void Boost_QubitRouter::set_in_edge_weights(int node, float w) const {
    auto weight_map = boost::get(boost::edge_weight, bgraph);
    for (auto [ei, ei_end] = boost::in_edges(node, bgraph); ei != ei_end; ++ei)
        boost::put(weight_map, *ei, w);
}

Path Boost_QubitRouter::dijkstra_path(int start, int end, float end_node_congestion) const {
    if (start == end) return {start};

    // Temporarily unblock the end node so Dijkstra can reach it.
    // (end may be a mapped qubit node that is normally hard-blocked to prevent
    //  other routes passing through it, but it is a valid destination here.)
    set_in_edge_weights(end, 1.0f + congestion_penalty * end_node_congestion);

    std::vector<float> dist(num_nodes, std::numeric_limits<float>::max());
    std::vector<int>   pred(num_nodes);
    std::iota(pred.begin(), pred.end(), 0);

    boost::dijkstra_shortest_paths(
        bgraph,
        static_cast<boost::graph_traits<BGraph>::vertex_descriptor>(start),
        boost::predecessor_map(
            boost::make_iterator_property_map(pred.begin(), boost::get(boost::vertex_index, bgraph))
        ).distance_map(
            boost::make_iterator_property_map(dist.begin(), boost::get(boost::vertex_index, bgraph))
        )
    );

    // Restore hard-block on the end node.
    set_in_edge_weights(end, HARD_BLOCK_WEIGHT);

    if (dist[end] >= 0.5f * HARD_BLOCK_WEIGHT) return {};
    return reconstruct_path(start, end, pred, num_nodes);
}

Path Boost_QubitRouter::dijkstra_to_closest_magic(
    int start,
    const std::unordered_set<int>& used_magic_states
) const {
    std::vector<float> dist(num_nodes, std::numeric_limits<float>::max());
    std::vector<int>   pred(num_nodes);
    std::iota(pred.begin(), pred.end(), 0);

    boost::dijkstra_shortest_paths(
        bgraph,
        static_cast<boost::graph_traits<BGraph>::vertex_descriptor>(start),
        boost::predecessor_map(
            boost::make_iterator_property_map(pred.begin(), boost::get(boost::vertex_index, bgraph))
        ).distance_map(
            boost::make_iterator_property_map(dist.begin(), boost::get(boost::vertex_index, bgraph))
        )
    );

    // Pick the closest reachable, free magic state.
    int   best_magic = -1;
    float best_dist  = std::numeric_limits<float>::max();
    for (int m : graph.get_magic_state_ids()) {
        if (used_magic_states.count(m)) continue;
        if (dist[m] < best_dist && dist[m] < 0.5f * HARD_BLOCK_WEIGHT) {
            best_dist  = dist[m];
            best_magic = m;
        }
    }

    if (best_magic < 0) return {};
    return reconstruct_path(start, best_magic, pred, num_nodes);
}

// ---------------------------------------------------------------------------
// Blocked-node query
// ---------------------------------------------------------------------------

std::unordered_set<int> Boost_QubitRouter::get_blocked_nodes() const {
    std::unordered_set<int> blocked;
    for (int qubit = 0; qubit < circuit.getQubitsVectorSize(); ++qubit) {
        if (circuit.getQubit(qubit) == nullptr) continue;
        const int node = mapping.get_mapped_node(qubit);
        if (node >= 0) blocked.insert(node);
    }    
    blocked.insert(graph.get_magic_state_ids().begin(), graph.get_magic_state_ids().end());
    
    return blocked;
}

// ---------------------------------------------------------------------------
// Core RRR layer router
// ---------------------------------------------------------------------------

Routing Boost_QubitRouter::route_layer_rrr(const Layer& layer_gates) const {
    const std::unordered_set<int> qubit_nodes = get_blocked_nodes();

    // Per-gate routing state tracked across RRR iterations.
    struct GateRoute {
        Gate gate;
        Path path;
        int  start_node;
        int  end_node;   // fixed for 2q gates; -1 for T gates (re-assigned each iter)
        bool is_t_gate;
        int  rip_count = 0;
    };

    std::vector<GateRoute> trivial;      // H gates: routed immediately, never ripped
    std::vector<GateRoute> gate_routes;  // everything else

    for (const Gate& gate : layer_gates) {
        if (gate.name == "h") {
            const int node = mapping.get_mapped_node(gate.qubits[0]);
            if (node >= 0) trivial.push_back({gate, {node}, node, node, false, 0});
            continue;
        }
        if (gate.qubits.empty()) continue;

        GateRoute gr;
        gr.gate       = gate;
        gr.is_t_gate  = (gate.name == "t");
        gr.start_node = mapping.get_mapped_node(gate.qubits[0]);
        if (gr.start_node < 0) continue;

        if (!gr.is_t_gate && gate.qubits.size() == 2) {
            gr.end_node = mapping.get_mapped_node(gate.qubits[1]);
            if (gr.end_node < 0) continue;
        } else if (gr.is_t_gate) {
            gr.end_node = -1;
        } else {
            std::cout << "WARNING: unhandled gate " << gate.to_string() << " skipped in RRR.\n";
            continue;
        }
        gate_routes.push_back(std::move(gr));
    }

    // Per-node congestion accumulated across iterations.
    std::vector<float> node_congestion(num_nodes, 0.0f);

    for (int iter = 0; iter < max_rrr_iterations; ++iter) {
        // Bake current congestion + qubit-node hard-blocks into edge weights.
        update_edge_weights(node_congestion, qubit_nodes);

        // Reserve magic states already held by still-routed T gates.
        std::unordered_set<int> used_magic_states;
        for (const auto& gr : gate_routes) {
            if (!gr.path.empty() && gr.is_t_gate)
                used_magic_states.insert(gr.path.back());
        }

        // Route every gate that currently has no path.
        for (auto& gr : gate_routes) {
            if (!gr.path.empty()) continue;
            if (gr.is_t_gate) {
                gr.path = dijkstra_to_closest_magic(gr.start_node, used_magic_states);
                if (!gr.path.empty()) {
                    gr.end_node = gr.path.back();
                    used_magic_states.insert(gr.end_node);
                }
            } else {
                gr.path = dijkstra_path(gr.start_node, gr.end_node, node_congestion[gr.end_node]);
            }
        }

        // Conflict detection: collect all nodes used as non-start path nodes.
        // (Index 0 of a path is the start/qubit node — hard-blocked for others,
        //  so it cannot appear in a different gate's path anyway.)
        std::unordered_map<int, std::vector<int>> node_to_routes;
        for (int i = 0; i < static_cast<int>(gate_routes.size()); ++i) {
            const auto& gr = gate_routes[i];
            for (std::size_t k = 1; k < gr.path.size(); ++k)
                node_to_routes[gr.path[k]].push_back(i);
        }

        bool any_conflict = false;
        std::unordered_set<int> already_ripped;
        for (auto& [node, indices] : node_to_routes) {
            if (indices.size() <= 1) continue;
            any_conflict = true;
            node_congestion[node] += 1.0f;

            // Winner = fewest previous rip-ups; ties broken by shorter current path.
            const int winner = *std::min_element(
                indices.begin(), indices.end(),
                [&](int a, int b) {
                    const auto& ra = gate_routes[a];
                    const auto& rb = gate_routes[b];
                    if (ra.rip_count != rb.rip_count)
                        return ra.rip_count < rb.rip_count;
                    return ra.path.size() < rb.path.size();
                }
            );

            for (int idx : indices) {
                if (idx == winner || already_ripped.count(idx)) continue;
                already_ripped.insert(idx);
                gate_routes[idx].rip_count++;
                gate_routes[idx].path.clear();
                if (gate_routes[idx].is_t_gate)
                    gate_routes[idx].end_node = -1;
            }
        }

        if (!any_conflict) break;
    }

    // Assemble final routing.
    Routing routing;
    for (const auto& gr : trivial)      routing.emplace(gr.gate, gr.path);
    for (const auto& gr : gate_routes)  if (!gr.path.empty()) routing.emplace(gr.gate, gr.path);
    return routing;
}

// ---------------------------------------------------------------------------
// Circuit-level routing loop
// ---------------------------------------------------------------------------

void Boost_QubitRouter::route_circuit() {
    std::cout << "Starting RRR qubit routing (max " << max_rrr_iterations
              << " iters/layer, congestion penalty " << congestion_penalty << ")...\n";

    routing_steps.clear();
    routing_steps.reserve(circuit.getNumLayers());
    std::map<std::size_t, std::size_t> non_routed_histogram;

    while (circuit.getNumLayers() > 0) {
        const Layer& top_layer = circuit.getLayer(0);
        if (top_layer.empty())
            throw std::runtime_error("Empty layer encountered during RRR routing.");

        Routing route = route_layer_rrr(top_layer);

        const std::size_t non_routed = top_layer.size() - route.size();
        if (non_routed > 0) non_routed_histogram[non_routed]++;

        if (route.empty()) {
            std::cout << "ERROR: RRR made no progress at layer "
                      << routing_steps.size() + 1 << ":\n";
            for (const auto& g : top_layer)
                std::cout << "  " << g.to_string() << "\n";
            throw std::runtime_error(
                "RRR routing made no progress at layer " +
                std::to_string(routing_steps.size() + 1) + "."
            );
        } 

        routing_steps.emplace_back(route);

        std::vector<Gate> used_gates;
        used_gates.reserve(route.size());
        for (const auto& [gate, path] : route) used_gates.push_back(gate);
        circuit.update_layers(used_gates);
    }

    std::cout << "RRR qubit routing completed.\n";
    if (!non_routed_histogram.empty()) {
        const int col1w = 45, col2w = 8;
        std::cout << "\n\033[35mNon-routed gates histogram (RRR, top layer per step)\033[0m\n";
        std::cout << "\033[35m" << std::left
                  << std::setw(col1w) << "number of non-routed gates in the top layer"
                  << std::right << std::setw(col2w) << "count" << "\033[0m\n";
        std::cout << "\033[35m" << std::string(col1w + col2w, '-') << "\033[0m\n";
        for (const auto& [value, count] : non_routed_histogram)
            std::cout << "\033[35m" << std::left << std::setw(col1w) << value
                      << std::right << std::setw(col2w) << count << "\033[0m\n";
    }
}

// ---------------------------------------------------------------------------
// Debug printing
// ---------------------------------------------------------------------------

void Boost_QubitRouter::print_routing_steps() const {
    for (int i = 0; i < static_cast<int>(routing_steps.size()); ++i) {
        std::cout << "# Step " << i << " #############\n";
        print_routing(i);
        std::cout << "\n";
    }
}

void Boost_QubitRouter::print_routing(int i) const {
    for (const auto& [gate, path] : routing_steps[i]) {
        std::cout << gate.to_string() << ": ";
        for (std::size_t k = 0; k < path.size(); ++k) {
            if (k > 0) std::cout << "-";
            std::cout << path[k];
        }
        std::cout << "\n";
    }
}
