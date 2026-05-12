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

class ITGateRoutingStrategy {
public:
    virtual ~ITGateRoutingStrategy() = default;
    virtual Path find_t_gate_path(
        const Gate& gate,
        const Mapping& mapping,
        const Graph& graph,
        const IPathStrategy& path_strategy,
        const std::unordered_set<int>& used_nodes,
        const std::unordered_set<int>& used_magic_states,
        const std::unordered_map<int, std::vector<int>>& magic_state_order_cache
    ) const = 0;
};

class NormalTGateRouting : public ITGateRoutingStrategy {
public:
    Path find_t_gate_path(
        const Gate& gate,
        const Mapping& mapping,
        const Graph& graph,
        const IPathStrategy& path_strategy,
        const std::unordered_set<int>& used_nodes,
        const std::unordered_set<int>& used_magic_states,
        const std::unordered_map<int, std::vector<int>>& magic_state_order_cache
    ) const override;
};

class SmartTGateRouting : public ITGateRoutingStrategy {
private:
    int patience_threshold;

public:
    explicit SmartTGateRouting(int patience_threshold = 3) : patience_threshold(patience_threshold) {}

    Path find_t_gate_path(
        const Gate& gate,
        const Mapping& mapping,
        const Graph& graph,
        const IPathStrategy& path_strategy,
        const std::unordered_set<int>& used_nodes,
        const std::unordered_set<int>& used_magic_states,
        const std::unordered_map<int, std::vector<int>>& magic_state_order_cache
    ) const override;
};

struct PairIntHash {
    std::size_t operator()(const std::pair<int,int>& p) const noexcept {
        std::size_t h1 = std::hash<int>{}(p.first);
        std::size_t h2 = std::hash<int>{}(p.second);
        return h1 ^ (h2 + 0x9e3779b9u + (h1 << 6) + (h1 >> 2));
    }
};

class IQubitRouter {
public:
    virtual ~IQubitRouter() = default;
    virtual void route_circuit() = 0;
    virtual int  get_routing_length() const = 0;
    virtual void print_routing_steps() const = 0;
    virtual void reset() = 0;
};

class QubitRouter : public IQubitRouter {
private:
    const Mapping& mapping;
    LayeredCircuit& circuit;
    const Graph& graph;
    const IPathStrategy* pathStrategy;
    const ITGateRoutingStrategy* tGateRoutingStrategy;
    std::vector<Routing> routing_steps;
    std::unordered_map<int, std::vector<int>> magic_state_order_cache;
    std::unordered_map<std::string, Routing>* layer_routing_cache;

    mutable std::unordered_set<int> used_nodes_cache;
    mutable std::unordered_map<std::pair<int,int>, float, PairIntHash> min_gate_route_length_cache;
    std::unordered_set<int> get_used_nodes() const;
    int closestMagicState(const Gate& g) const;
    Routing route_layer(const Layer& layer_gates) const;
    float minGateRouteLength(const Gate& g) const;

public:
    QubitRouter(
        const Mapping& m,
        LayeredCircuit& c,
        const Graph& g,
        const IPathStrategy* p,
        const ITGateRoutingStrategy* t,
        std::unordered_map<std::string, Routing>* cache = nullptr
    ) : mapping(m),
        circuit(c),
        graph(g),
        pathStrategy(p),
        tGateRoutingStrategy(t),
        layer_routing_cache(cache) {
            precompute_magic_state_order();
        }
    void route_circuit() override;
    void precompute_magic_state_order();
    inline int get_routing_length() const override { return routing_steps.size(); }

    void print_routing_steps() const override;
    inline void reset() override { circuit.reset(); routing_steps.clear(); }

    inline const std::vector<Routing>& get_routing() const { return routing_steps; }
    inline const Routing& get_route_step(int i) const { return routing_steps[i]; }
    void print_routing(int i) const;

};

#endif // ROUTING_HPP
