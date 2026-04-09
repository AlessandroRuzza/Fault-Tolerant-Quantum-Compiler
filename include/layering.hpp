#ifndef LAYERING_HPP
#define LAYERING_HPP

#include "circuit.hpp"


#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <algorithm>

using Layer = std::unordered_set<Gate>;

class LayeredCircuit : public Circuit {
    static const Layer emptyLayer;
protected:
    // Each layer is a vector of gate pointers
    std::vector<Layer> layers;
    std::unordered_set<Gate> ignored_gates;
    
private:
    void build_layers();
    
public:
    LayeredCircuit(const Circuit& circuit) : Circuit(circuit) {
        build_layers();
    }

    void update_layers(const std::vector<Gate>& routed_gates);
    void reset();
    void reset(const std::vector<Gate>& routed_gates);
    void print_layered() const;

    const Layer& getLayer(int i) const {
        if(i >= layers.size()) return emptyLayer;
        else return layers[i];
    }
    int getNumLayers() const {
        return layers.size();
    }
};

#endif // LAYERING_HPP
