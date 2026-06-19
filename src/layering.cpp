#include "layering.hpp"
#include "commute.hpp"  // gates_commute (shared with the packing router)

// Definition of static member
const Layer LayeredCircuit::emptyLayer = {};

void LayeredCircuit::build_layers() {
    if (commute_layering) {
        build_layers_commute();
        return;
    }
    layers.clear();
    // ASAP placement below puts every gate at its earliest legal layer, so the
    // result has no movable gates: start clean.
    layers_need_compaction = false;
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

bool LayeredCircuit::pull_gates_into_top_layer(std::size_t max_lookahead_layers) {
    if (layers.empty() || max_lookahead_layers == 0 || layers.size() < 2) {
        return false;
    }

    bool moved_any = false;
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
            moved_any = true;
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

    return moved_any;
}

void LayeredCircuit::compact_top_layer() {
    remove_leading_empty_layers();

    // A pristine ASAP layering has no movable gates, so the pull scan is pure
    // overhead until a postponement (or an earlier pull) creates a hole. Run it
    // only when such a hole might exist; the caller sets the flag when it does.
    if (layers_need_compaction) {
        const bool moved = pull_gates_into_top_layer(layer_pull_lookahead);
        // Pulling gates out of deeper layers can expose more movable gates, so stay dirty.
        // Once a pull moves nothing, we can stop scanning.
        layers_need_compaction = moved;
    }

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

    // route_layer only routes gates from the top layer, so a non-empty front
    // after removal means some gates were postponed — their layer-below
    // dependents may now be movable. Mark dirty so compact_top_layer pulls.
    if (!layers.front().empty()) {
        layers_need_compaction = true;
    }

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
    auto erase_routed_from_layer = [&](Layer& layer) -> std::size_t {
        std::size_t erased = 0;
        for (auto it = layer.begin(); it != layer.end() && !routed_set.empty(); ) {
            if (routed_set.count(*it) > 0) {
                routed_set.erase(*it);
                it = layer.erase(it);
                ++erased;
            } else {
                ++it;
            }
        }
        return erased;
    };

    // Removing a gate from any layer below the front leaves a hole that can make
    // gates further down movable, so track whether that happened.
    bool removed_below_front = false;
    for (std::size_t d = 0; d <= windowed_last && !routed_set.empty(); ++d) {
        const std::size_t erased = erase_routed_from_layer(layers[d]);
        if (d > 0 && erased > 0) removed_below_front = true;
    }
    for (std::size_t d = windowed_last + 1; d < layers.size() && !routed_set.empty(); ++d) {
        if (erase_routed_from_layer(layers[d]) > 0) removed_below_front = true;
    }

    if (removed_below_front || !layers.front().empty()) {
        layers_need_compaction = true;
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
