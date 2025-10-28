#ifndef ROUTING_HPP
#define ROUTING_HPP

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
    
    Routing route_layer(const Layer& layer_gates) const;
    void route_circuit();
};

} // namespace circuit

#endif // ROUTING_HPP