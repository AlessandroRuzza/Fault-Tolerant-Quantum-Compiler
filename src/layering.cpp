#include "layering.hpp"

namespace qasm {

void LayeredCircuit::build_layers() {
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

void LayeredCircuit::print_layered() const {
    for (size_t i = 0; i < layers.size(); ++i) {
        std::cout << "Layer " << i << ": ";
        for (const auto& gate : layers[i]) {
            std::cout << gate.to_string() << " ";
        }
        std::cout << std::endl;
    }
}

}