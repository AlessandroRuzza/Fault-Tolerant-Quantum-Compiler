#include "circuit.hpp"

#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <algorithm>

namespace circuit {

class LayeredCircuit : public Circuit {
protected:
    // Each layer is a vector of gate pointers
    std::vector<std::unordered_set<Gate>> layers;
    std::unordered_set<Gate> ignored_gates;
    
private:
    void build_layers();
    
public:
    LayeredCircuit(const Circuit& circuit) : Circuit(circuit) {
        build_layers();
    }

    void update_layers(const std::vector<Gate>& routed_gates){
        ignored_gates.insert(routed_gates.begin(), routed_gates.end());
        build_layers();
    }
    void print_layered() const;
};

}