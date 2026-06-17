#ifndef LAYERING_HPP
#define LAYERING_HPP

#include "circuit.hpp"


#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <deque>
#include <algorithm>

using Layer = std::unordered_set<Gate>;

class LayeredCircuit : public Circuit {
    static const Layer emptyLayer;
protected:
    // Stored as a deque so that popping the front layer (called once per routing
    // step) is O(1) instead of O(N) shift that std::vector would require.
    std::deque<Layer> layers;
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
    // Like update_layers, but removes routed gates from any of the top
    // (max_depth + 1) layers, not just the front one. Needed by the packing
    // router's commutation mode, which may route a gate pulled from a deeper
    // layer. Scanning is bounded by max_depth so it stays cheap per step.
    void update_layers_within(const std::vector<Gate>& routed_gates, std::size_t max_depth);
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
