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

void LayeredCircuit::update_layers(const std::vector<Gate>& routed_gates){
    ignored_gates.insert(routed_gates.begin(), routed_gates.end());
    build_layers();
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
