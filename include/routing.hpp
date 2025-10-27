#include "layering.hpp"
#include "mapping.hpp"
#include "graph.hpp"

#include <vector>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <limits>

namespace circuit {
using Path = std::vector<int>;
using Routing = std::unordered_map<Gate, Path>;

class IPathStrategy{
protected:
    const Graph& graph;
    IPathStrategy(const Graph& g) : graph(g) {}
public:
    virtual ~IPathStrategy() = default;
    virtual Path find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const = 0;
};

class NaiveShortestPath : public IPathStrategy {
    std::vector<int> find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const;
};

class QubitRouter {
private:
    const Mapping& mapping;
    LayeredCircuit& circuit;
    const Graph& graph;
    const IPathStrategy& pathStrategy;
public:
    QubitRouter(const Mapping& m, LayeredCircuit& c, const Graph& g, const IPathStrategy& p) 
        : mapping(m), circuit(c), graph(g), pathStrategy(p) {}
    
    // Route a single layer of gates
    Routing route_layer(const std::vector<Gate>& layer_gates) const;

    // Route the entire circuit
    void route_circuit() {
        std::cout << "Starting qubit routing...\n";
        
        throw new std::runtime_error("QubitRouter::route_circuit not implemented yet.");
        // TODO:
        // Process layers until all gates are routed
        // This is a simplified version; a full implementation would iterate
        // until all gates are executed or moved to the routed circuit
        
        std::cout << "Qubit routing completed.\n";
    }
};

} // namespace circuit

