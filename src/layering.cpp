#include "layering.hpp"

// Definition of static member
const Layer LayeredCircuit::emptyLayer = {};

void LayeredCircuit::build_layers() {
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
    std::size_t first_non_empty = 0;
    while (first_non_empty < layers.size() && layers[first_non_empty].empty()) {
        ++first_non_empty;
    }
    if (first_non_empty > 0) {
        layers.erase(layers.begin(), layers.begin() + first_non_empty);
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

void LayeredCircuit::update_layers(const std::vector<Gate>& routed_gates){
    if (routed_gates.empty()) {
        return;
    }

    ignored_gates.insert(routed_gates.begin(), routed_gates.end());

    std::unordered_set<Gate> routed_set(routed_gates.begin(), routed_gates.end());
    remove_routed_from_topLayer(routed_set);
    
    if (layers.empty())
        return;

    if (layers.front().empty()) {
        remove_leading_empty_layers();
    }
    else{
        pull_gates_into_top_layer(layer_pull_lookahead);
        remove_trailing_empty_layers();
    }
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
