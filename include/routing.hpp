#ifndef ROUTING_HPP
#define ROUTING_HPP

#include "layering.hpp"
#include "mapping.hpp"
#include "graph.hpp"

#include <vector>
#include <queue>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <limits>

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

enum class CongestionUpdatePolicy {
    STATIC_GLOBAL,
    DYNAMIC_PER_LAYER
};

class CongestionAwareShortestPath : public IPathStrategy {
private:
    float congestion_penalty_scale;
    CongestionUpdatePolicy update_policy;
    mutable std::unordered_map<int, float> node_weights;
    mutable bool static_weights_ready;
    NaiveShortestPath naivePath;

    Path naive_unweighted_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const;
    void accumulate_path_congestion(const Path& path) const;
    void rebuild_node_weights(
        const LayeredCircuit& circuit,
        const Mapping& mapping,
        const std::unordered_set<int>& blocked_nodes
    ) const;

public:
    CongestionAwareShortestPath(
        const Graph& g,
        float congestion_penalty_scale = 1.0f,
        CongestionUpdatePolicy update_policy = CongestionUpdatePolicy::DYNAMIC_PER_LAYER
    ) : IPathStrategy(g),
        congestion_penalty_scale(congestion_penalty_scale),
        update_policy(update_policy),
        static_weights_ready(false),
        naivePath(g) {}

    void prepare_for_layer(
        const LayeredCircuit& circuit,
        const Mapping& mapping,
        const std::unordered_set<int>& blocked_nodes
    ) const;

    Path find_shortest_path(int start_node, int end_node, const std::unordered_set<int>& used_nodes) const override;
};

class QubitRouter {
private:
    const Mapping& mapping;
    LayeredCircuit& circuit;
    const Graph& graph;
    const IPathStrategy* pathStrategy;
    std::string t_routing_mode;
    int patience_threshold;
    std::vector<Routing> routing_steps;
    std::unordered_map<int, std::vector<int>> magic_state_order_cache;

    Routing route_layer(const Layer& layer_gates) const;
    float minGateRouteLength(const Gate& g) const;

public:
    QubitRouter(
        const Mapping& m,
        LayeredCircuit& c,
        const Graph& g,
        const IPathStrategy* p,
        std::string t_routing_mode = "normal_t_routing",
        int patience_threshold = 3
    ) : mapping(m),
        circuit(c),
        graph(g),
        pathStrategy(p),
        t_routing_mode(std::move(t_routing_mode)),
        patience_threshold(patience_threshold) {}
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

    // Precompute the order of magic states to be used for routing each gate, based on the mapping's strategy.
    void precompute_magic_state_order();

    void print_routing_steps() const;
    void print_routing(int i) const;

};

#endif // ROUTING_HPP
