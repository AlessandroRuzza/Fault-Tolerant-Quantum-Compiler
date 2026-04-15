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
    std::size_t layer_pull_lookahead;
    
private:
    void build_layers();
    void remove_routed_from_topLayer(const std::unordered_set<Gate>& routed_set);
    void remove_leading_empty_layers();
    void remove_trailing_empty_layers();
    void pull_gates_into_top_layer(std::size_t max_lookahead_layers);
    
public:
    LayeredCircuit(const Circuit& circuit, std::size_t lookahead_layers = 8)
        : Circuit(circuit),
          layer_pull_lookahead(std::max<std::size_t>(1, lookahead_layers)) {
        build_layers();
    }

    void update_layers(const std::vector<Gate>& routed_gates);
    inline void set_layer_pull_lookahead(std::size_t lookahead_layers) {
        layer_pull_lookahead = std::max<std::size_t>(1, lookahead_layers);
    }
    inline std::size_t get_layer_pull_lookahead() const {
        return layer_pull_lookahead;
    }
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
