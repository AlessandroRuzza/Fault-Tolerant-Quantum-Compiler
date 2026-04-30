#ifndef BOOST_ROUTER_HPP
#define BOOST_ROUTER_HPP

#include "routing.hpp"

#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/dijkstra_shortest_paths.hpp>
#include <boost/graph/graph_traits.hpp>

/*
 * Directed graph: edge u→v carries the cost of *entering* v.
 * This lets us encode per-node costs directionally (congestion, hard-blocks)
 * without a symmetric undirected weight assumption.
 */
using BGraph = boost::adjacency_list<
    boost::vecS,
    boost::vecS,
    boost::directedS,
    boost::no_property,
    boost::property<boost::edge_weight_t, float>
>;

/*
 * Boost_QubitRouter
 *
 * Routes the circuit layer-by-layer using a Rip-up and Re-route (RRR) strategy.
 * All gates in a layer are routed simultaneously on a weighted copy of the
 * device graph.  When two routes share a node, the lower-priority route is
 * "ripped up", that node's congestion weight is raised, and the ripped-up gate
 * is re-routed in the next iteration.  This repeats up to max_rrr_iterations
 * times; any gate still unrouted after that is deferred to a later routing step.
 *
 * Note: MAGIC_STOPS_ROUTE is not enforced for intermediate nodes — the RRR cost
 * model naturally steers non-T-gate paths away from contested magic-state nodes.
 */
class Boost_QubitRouter : public IQubitRouter {
private:
    const Mapping&    mapping;
    LayeredCircuit&   circuit;
    const Graph&      graph;
    std::vector<Routing> routing_steps;

    int   max_rrr_iterations;
    float congestion_penalty;  // added weight per congestion count on a node

    mutable BGraph bgraph;
    int num_nodes;

    // Rebuild the Boost graph from the project Graph (called once in ctor).
    void build_boost_graph();

    // Rewrite all edge weights from the current node_congestion vector.
    // Edges *into* hard_blocked nodes receive HARD_BLOCK_WEIGHT.
    void update_edge_weights(
        const std::vector<float>& node_congestion,
        const std::unordered_set<int>& hard_blocked
    ) const;

    // Dijkstra from start to end; returns empty path if unreachable.
    // Weights must already be set via update_edge_weights.
    Path dijkstra_path(int start, int end) const;

    // Dijkstra from start; returns the path to the closest magic state
    // that is not in used_magic_states (empty if none reachable).
    Path dijkstra_to_closest_magic(
        int start,
        const std::unordered_set<int>& used_magic_states
    ) const;

    // Returns the set of physical nodes occupied by mapped qubits.
    std::unordered_set<int> get_blocked_nodes() const;

    // Core per-layer RRR algorithm.
    Routing route_layer_rrr(const Layer& layer_gates) const;

public:
    Boost_QubitRouter(
        const Mapping&  m,
        LayeredCircuit& c,
        const Graph&    g,
        int   max_rrr_iterations = 10,
        float congestion_penalty = 3.0f
    );

    void route_circuit() override;
    inline int  get_routing_length()  const override { return static_cast<int>(routing_steps.size()); }
    void print_routing_steps()        const override;
    inline void reset()                     override { circuit.reset(); routing_steps.clear(); }

    inline const std::vector<Routing>& get_routing()    const { return routing_steps; }
    inline const Routing& get_route_step(int i)         const { return routing_steps[i]; }
    void print_routing(int i)  const;
};

#endif // BOOST_ROUTER_HPP
