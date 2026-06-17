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

// How QubitRouter orders the gates of a layer when deciding which to route first
// in a step. PATH_LENGTH is the historical behaviour ("naive"); CRITICALITY is
// the "naive_critical" strategy, which routes critical-path gates first.
enum class GateOrdering {
    PATH_LENGTH,   // shortest route length first (default; unchanged behaviour)
    CRITICALITY    // dependency-chain tail (descending), route-length as tiebreak
};

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

    // When the layer routing cache is active, call this once before routing begins so
    // that node weights are computed once and never rebuilt. This ensures every cache
    // hit uses the same weight basis as the original cache-miss routing.
    void force_static_mode() { update_policy = CongestionUpdatePolicy::STATIC_GLOBAL; }

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
    virtual void print_non_routed_histogram() const = 0;
    virtual void reset() = 0;
    // Percentage of gates that were NOT routed on the first step they appeared in
    // the top layer (each gate counted once, denominator = total routable gates).
    // 0 = every layer routed without splitting. Returns -1 when not tracked.
    virtual double get_non_routed_layer_percentage() const { return -1.0; }
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
    std::unordered_map<size_t, Routing>* layer_routing_cache;
    GateOrdering gate_ordering;
    // gate.id -> criticality (longest dependency-chain tail). Populated once by
    // compute_gate_criticality() and only used when gate_ordering == CRITICALITY.
    std::unordered_map<int, int> gate_tail_by_id;
    std::unordered_map<std::size_t, std::size_t> non_routed_histogram;

    // Non-routed metric accumulators (see get_non_routed_layer_percentage).
    // first_exposure_total: gates seen for the first time at the top layer (== total gates).
    // first_exposure_routed: of those, how many were routed in that same first step.
    std::size_t first_exposure_total = 0;
    std::size_t first_exposure_routed = 0;

    mutable std::unordered_set<int> used_nodes_cache;
    mutable std::unordered_map<std::pair<int,int>, float, PairIntHash> min_gate_route_length_cache;
    std::unordered_set<int> get_used_nodes() const;
    int closestMagicState(const Gate& g) const;
    Routing route_layer(const Layer& layer_gates) const;
    float minGateRouteLength(const Gate& g) const;

    // Compute, for every gate, the length of the longest chain of gates that
    // depend on it (its "tail"). This is its criticality: routing it late delays
    // that whole chain, so high-tail gates are scheduled first under CRITICALITY.
    void compute_gate_criticality();
    inline int gate_criticality(const Gate& g) const {
        const auto it = gate_tail_by_id.find(g.id);
        return it != gate_tail_by_id.end() ? it->second : 0;
    }

public:
    QubitRouter(
        const Mapping& m,
        LayeredCircuit& c,
        const Graph& g,
        const IPathStrategy* p,
        const ITGateRoutingStrategy* t,
        std::unordered_map<size_t, Routing>* cache = nullptr,
        GateOrdering ordering = GateOrdering::PATH_LENGTH
    ) : mapping(m),
        circuit(c),
        graph(g),
        pathStrategy(p),
        tGateRoutingStrategy(t),
        layer_routing_cache(cache),
        gate_ordering(ordering) {
            precompute_magic_state_order();
        }
    void route_circuit() override;
    void precompute_magic_state_order();
    inline int get_routing_length() const override { return routing_steps.size(); }

    inline double get_non_routed_layer_percentage() const override {
        if (first_exposure_total == 0) return 0.0;
        return 100.0 * static_cast<double>(first_exposure_total - first_exposure_routed)
                     / static_cast<double>(first_exposure_total);
    }

    void print_routing_steps() const override;
    inline void reset() override {
        circuit.reset();
        routing_steps.clear();
        first_exposure_total = 0;
        first_exposure_routed = 0;
    }

    inline const std::vector<Routing>& get_routing() const { return routing_steps; }
    inline const Routing& get_route_step(int i) const { return routing_steps[i]; }
    void print_routing(int i) const;
    void print_non_routed_histogram() const;

};

/*
 * PackingQubitRouter
 *
 * Routes each layer by *packing* a maximum set of vertex-disjoint paths instead
 * of routing gates one-by-one in a fixed greedy order. Per layer:
 *   1. Generate up to num_candidates diverse candidate paths per gate
 *      (penalized re-search for 2q gates; nearest free magic states for T gates).
 *   2. Greedily select a high-weight conflict-free subset, where weight is the
 *      gate's downstream criticality (how many gates in the next
 *      criticality_lookahead layers touch its qubits), ties broken by shorter path.
 *   3. Fill pass: any still-unrouted gate gets a fresh shortest path avoiding the
 *      selected ones, so the result is always maximal (never routes fewer gates
 *      than "nothing left fits").
 */
class PackingQubitRouter : public IQubitRouter {
private:
    const Mapping& mapping;
    LayeredCircuit& circuit;
    const Graph& graph;

    int num_candidates;
    int criticality_lookahead;
    float diversity_penalty;
    // "packing_commute": when true, widen each step's candidate set with gates
    // pulled from deeper layers that commute (CX same-control / same-target) with
    // all pending predecessors on their qubits. Off by default → behaviour is
    // byte-identical to before. The commute window equals criticality_lookahead.
    bool enable_commute;

    std::vector<Routing> routing_steps;
    std::unordered_map<std::size_t, std::size_t> non_routed_histogram;
    std::size_t first_exposure_total = 0;
    std::size_t first_exposure_routed = 0;

    std::unordered_set<int> base_blocked_nodes() const;
    Path penalized_shortest_path(
        int start_node,
        int end_node,
        const std::unordered_set<int>& blocked,
        const std::unordered_map<int, float>& penalties
    ) const;
    Routing route_layer_packing(const Layer& layer_gates) const;

protected:
    // Selection priority for a gate within a step: {primary, secondary}, higher
    // is routed first (std::pair compares lexicographically). Base "packing"
    // returns {downstream qubit pressure, 0}, so the secondary key is inert and
    // behaviour is unchanged. The "critical_packing" subclass overrides this to
    // use the true dependency-chain tail (critical path) as the primary key.
    virtual std::pair<int, int> gate_priority(const Gate& g, int qubit_pressure_sum) const;

public:
    PackingQubitRouter(
        const Mapping& m,
        LayeredCircuit& c,
        const Graph& g,
        int num_candidates = 2,
        int criticality_lookahead = 4,
        float diversity_penalty = 1.0f,
        bool enable_commute = false
    ) : mapping(m),
        circuit(c),
        graph(g),
        num_candidates(std::max(1, num_candidates)),
        criticality_lookahead(std::max(0, criticality_lookahead)),
        diversity_penalty(diversity_penalty),
        enable_commute(enable_commute) {}

    void route_circuit() override;
    inline int get_routing_length() const override { return static_cast<int>(routing_steps.size()); }

    inline double get_non_routed_layer_percentage() const override {
        if (first_exposure_total == 0) return 0.0;
        return 100.0 * static_cast<double>(first_exposure_total - first_exposure_routed)
                     / static_cast<double>(first_exposure_total);
    }

    void print_routing_steps() const override;
    inline void reset() override {
        circuit.reset();
        routing_steps.clear();
        first_exposure_total = 0;
        first_exposure_routed = 0;
    }

    inline const std::vector<Routing>& get_routing() const { return routing_steps; }
    inline const Routing& get_route_step(int i) const { return routing_steps[i]; }
    void print_routing(int i) const;
    void print_non_routed_histogram() const;
};

/*
 * CriticalPackingQubitRouter ("critical_packing")
 *
 * Identical per-step disjoint-path packing as PackingQubitRouter, but gates are
 * prioritised by their true critical-path criticality — the length of the
 * longest dependency chain hanging off the gate (its "tail") — instead of the
 * base router's downstream qubit pressure. The pressure is kept as the tiebreak.
 *
 * Rationale: pressure is a breadth measure over a short lookahead window and
 * misses the depth of long serial cascades (e.g. QFT), where routing the
 * longest-chain gate first is what reduces the step count. Using the tail as the
 * primary key recovers that, while the pressure tiebreak preserves the base
 * router's behaviour on circuits whose tails are flat (e.g. QAOA).
 */
class CriticalPackingQubitRouter : public PackingQubitRouter {
private:
    // gate.id -> longest dependency-chain tail. Computed once from the circuit's
    // textual gate order; stays valid as routed gates are removed, so it is never
    // recomputed per step.
    std::unordered_map<int, int> gate_tail_by_id;
    void compute_gate_criticality(const Circuit& circuit);

protected:
    std::pair<int, int> gate_priority(const Gate& g, int qubit_pressure_sum) const override {
        const auto it = gate_tail_by_id.find(g.id);
        const int tail = (it != gate_tail_by_id.end()) ? it->second : 0;
        return {tail, qubit_pressure_sum};  // tail primary, pressure tiebreak
    }

public:
    CriticalPackingQubitRouter(
        const Mapping& m,
        LayeredCircuit& c,
        const Graph& g,
        int num_candidates = 2,
        int criticality_lookahead = 4,
        float diversity_penalty = 1.0f,
        bool enable_commute = false
    ) : PackingQubitRouter(m, c, g, num_candidates, criticality_lookahead, diversity_penalty, enable_commute) {
        compute_gate_criticality(c);
    }
};

#endif // ROUTING_HPP
