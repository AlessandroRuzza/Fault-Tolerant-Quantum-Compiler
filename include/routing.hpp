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

using circuit::LayeredCircuit;
using circuit::Layer;
using circuit::Gate;

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
public:
    NaiveShortestPath(const Graph& g) : IPathStrategy(g) {}
    Path find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const;
};

class QubitRouter {
private:
    const Mapping& mapping;
    LayeredCircuit& circuit;
    const Graph& graph;
    const IPathStrategy* pathStrategy;
    std::vector<Routing> routing_steps;

    Routing route_layer(const Layer& layer_gates) const;
    float minGateRouteLength(const Gate& g) const;

public:
    QubitRouter(const Mapping& m, LayeredCircuit& c, const Graph& g, const IPathStrategy* p) 
        : mapping(m), circuit(c), graph(g), pathStrategy(p) {}
    /**
     * Routes the whole circuit, returning a vector of mappings (gate-Path).
     * @attention this will modify the layering in the internal LayeredCircuit.
     * @return A vector of Routing maps.
     */
    void route_circuit();
    inline const std::vector<Routing>& get_routing() const {
        return routing_steps;
    }
    inline const Routing& get_route_step(int i) const {
        return routing_steps[i];
    }
    inline int get_routing_length() const {
        return routing_steps.size();
    }
    inline void reset(){
        circuit.reset();
        routing_steps.clear();
    }
    void print_routing_steps() const;
    void print_routing(int i) const;

};

#endif // ROUTING_HPP
