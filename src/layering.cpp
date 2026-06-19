#include "layering.hpp"
#include "commute.hpp"  // gates_commute (shared with the packing router)

// Definition of static member
const Layer LayeredCircuit::emptyLayer = {};

namespace {
// Shallow pull depth used after a layer is fully routed. 
// This runs every normal step, so
// its value is 1 to keep negligible cost.
constexpr std::size_t FULLY_ROUTED_PULL_LOOKAHEAD = 1;
} // namespace

void LayeredCircuit::build_layers() {
    if (commute_layering) {
        build_layers_commute();
        return;
    }
    layers.clear();
    std::unordered_map<int, int> qubit_last_layer;
    std::vector<Gate> g;
    for (Gate& gate : this->gates){
        if (ignored_gates.count(gate) == 0)
            g.push_back(gate);
    }
    for (Gate& gate : g) {
        int max_layer = 0;
        for (const int q : gate.qubits) {
            if (qubit_last_layer.count(q))
                max_layer = std::max(max_layer, qubit_last_layer[q] + 1);
        }
        if (layers.size() <= max_layer)
            layers.resize(max_layer + 1);
        layers[max_layer].insert(gate);
        for (const int q : gate.qubits)
            qubit_last_layer[q] = max_layer;
    }
}

void LayeredCircuit::build_layers_commute() {
    layers.clear();

    // Gates in textual order, skipping any ignored ones (same filter as the
    // ASAP build). Pointers into `remaining` stay valid for one pass below.
    std::vector<Gate> remaining;
    remaining.reserve(this->gates.size());
    for (const Gate& gate : this->gates) {
        if (ignored_gates.count(gate) == 0)
            remaining.push_back(gate);
    }

    // Greedy front-to-back. Each pass emits one layer: a maximal set of gates,
    // qubit-disjoint within the layer, where a gate may jump ahead of earlier
    // still-unplaced gates only if it commutes with every one it shares a qubit
    // with. Non-CX gates never commute (gates_commute), so they act as full
    // barriers on their qubits — order across them is always preserved. The
    // first remaining gate is always placeable, so each pass shrinks `remaining`
    // and the loop terminates. With commutation disabled everywhere this reduces
    // to the same depth as the ASAP build; commuting gates only ever pack tighter.
    while (!remaining.empty()) {
        Layer layer;
        std::unordered_set<uint32_t> used_qubits;  // qubits already busy this layer
        // Earlier gates we skipped this pass, indexed by qubit. A candidate must
        // commute with every skipped gate on each of its qubits to move ahead.
        std::unordered_map<uint32_t, std::vector<const Gate*>> blockers;
        std::vector<Gate> next_remaining;
        next_remaining.reserve(remaining.size());

        for (const Gate& g : remaining) {
            bool placeable = true;
            for (const uint32_t q : g.qubits) {
                if (used_qubits.count(q)) { placeable = false; break; }
            }
            if (placeable) {
                for (const uint32_t q : g.qubits) {
                    const auto it = blockers.find(q);
                    if (it == blockers.end()) continue;
                    for (const Gate* h : it->second) {
                        if (!gates_commute(g, *h)) { placeable = false; break; }
                    }
                    if (!placeable) break;
                }
            }

            if (placeable) {
                layer.insert(g);
                for (const uint32_t q : g.qubits) used_qubits.insert(q);
            } else {
                next_remaining.push_back(g);
                for (const uint32_t q : g.qubits) blockers[q].push_back(&g);
            }
        }

        layers.push_back(std::move(layer));
        remaining = std::move(next_remaining);
    }
}

inline void LayeredCircuit::remove_routed_from_topLayer(const std::unordered_set<Gate>& routed_set) {
    if (routed_set.empty() || layers.empty()) {
        return;
    }

    Layer& topLayer = layers.front();
    for (auto it = topLayer.begin(); it != topLayer.end(); ) {
        if (routed_set.count(*it) > 0) {
            it = topLayer.erase(it);
        } else {
            ++it;
        }
    }
}

inline void LayeredCircuit::remove_leading_empty_layers() {
    // pop_front() on a deque is O(1); using it in a loop avoids the O(N) shift
    // that a vector erase-from-front would cause.
    while (!layers.empty() && layers.front().empty()) {
        layers.pop_front();
    }
}

inline void LayeredCircuit::remove_trailing_empty_layers() {
    while (!layers.empty() && layers.back().empty()) {
        layers.pop_back();
    }
}

void LayeredCircuit::pull_gates_into_top_layer(std::size_t max_lookahead_layers) {
    if (layers.empty() || max_lookahead_layers == 0 || layers.size() < 2) {
        return;
    }

    std::unordered_set<uint32_t> blocked_qubits;
    for (const Gate& gate : layers[0]) {
        for (uint32_t q : gate.qubits) {
            blocked_qubits.insert(q);
        }
    }

    const std::size_t max_layer_index = std::min(max_lookahead_layers, layers.size() - 1);
    for (std::size_t layer_idx = 1; layer_idx <= max_layer_index; ++layer_idx) {
        std::vector<Gate> movable_gates;
        movable_gates.reserve(layers[layer_idx].size());

        for (const Gate& gate : layers[layer_idx]) {
            bool is_blocked = false;
            for (uint32_t q : gate.qubits) {
                if (blocked_qubits.count(q) > 0) {
                    is_blocked = true;
                    break;
                }
            }
            if (!is_blocked) {
                movable_gates.push_back(gate);
            }
        }

        for (const Gate& gate : movable_gates) {
            layers[layer_idx].erase(gate);
            layers[0].insert(gate);
            for (uint32_t q : gate.qubits) {
                blocked_qubits.insert(q);
            }
        }

        for (const Gate& gate : layers[layer_idx]) {
            for (uint32_t q : gate.qubits) {
                blocked_qubits.insert(q);
            }
        }
    }
}

void LayeredCircuit::compact_top_layer() {
    // Decide the pull depth *before* dropping leading empty layers — that step
    // erases the "was the top fully routed?" signal we need here.
    //   front empty  -> top was fully routed: a shallow backfill is enough, and
    //                   this path runs every normal step so it must stay cheap.
    //   front filled -> gates were postponed: pull deeper to re-flatten the
    //                   staircase those postponed gates left behind.
    const std::size_t pull_lookahead = (!layers.empty() && layers.front().empty())
        ? FULLY_ROUTED_PULL_LOOKAHEAD
        : layer_pull_lookahead;

    remove_leading_empty_layers();
    pull_gates_into_top_layer(pull_lookahead);
    remove_trailing_empty_layers();
}

void LayeredCircuit::update_layers(const std::vector<Gate>& routed_gates){
    if (routed_gates.empty()) {
        return;
    }

    // ignored_gates is only read by build_layers() (i.e. via reset()), which is
    // never called during routing. Accumulating into it here was pure overhead
    // for long-running circuits (e.g. hhl_n10: ~72k routing steps).

    std::unordered_set<Gate> routed_set(routed_gates.begin(), routed_gates.end());
    remove_routed_from_topLayer(routed_set);
    
    if (layers.empty())
        return;

    compact_top_layer();
}
void LayeredCircuit::update_layers_within(const std::vector<Gate>& routed_gates, std::size_t max_depth) {
    if (routed_gates.empty() || layers.empty()) {
        return;
    }

    std::unordered_set<Gate> routed_set(routed_gates.begin(), routed_gates.end());

    // Remove the routed gates from the bounded window [0, max_depth]. The packing
    // commutation mode only ever routes gates from this window, so this is enough
    // in practice; the safety scan below covers any unexpected leftover without
    // paying the full O(layers) cost on the common path.
    const std::size_t windowed_last = std::min(max_depth, layers.size() - 1);
    auto erase_routed_from_layer = [&](Layer& layer) {
        for (auto it = layer.begin(); it != layer.end() && !routed_set.empty(); ) {
            if (routed_set.count(*it) > 0) {
                routed_set.erase(*it);
                it = layer.erase(it);
            } else {
                ++it;
            }
        }
    };

    for (std::size_t d = 0; d <= windowed_last && !routed_set.empty(); ++d) {
        erase_routed_from_layer(layers[d]);
    }
    for (std::size_t d = windowed_last + 1; d < layers.size() && !routed_set.empty(); ++d) {
        erase_routed_from_layer(layers[d]);
    }

    compact_top_layer();
}

void LayeredCircuit::reset(){
    ignored_gates.clear();
    build_layers();
}
void LayeredCircuit::reset(const std::vector<Gate>& routed_gates){
    ignored_gates.clear();
    update_layers(routed_gates);
}

void LayeredCircuit::print_layered() const {
    for (size_t i = 0; i < layers.size(); ++i) {
        std::cout << "Layer " << i << ": ";
        for (const auto& gate : layers[i]) {
            std::cout << gate.to_string() << " ";
        }
        std::cout << std::endl;
    }
}
