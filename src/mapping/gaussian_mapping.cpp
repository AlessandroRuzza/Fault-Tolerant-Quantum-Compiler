#include "mapping.hpp"
#include "exceptions.hpp"
#include "gaussian.hpp"
#include "circuit.hpp"
#include "qubit.hpp"
#include "graph.hpp"
#include "gaussian_images.hpp"
#include "gaussians.hpp"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <sstream>
#include <unordered_set>

void update_weight(std::vector<Gaussian>& gaussians, double new_weight);
void update_inverse(std::vector<Gaussian>& gaussians, bool inverse);
void update_gaussians_coarse(
    Qubit* qubit,
    std::vector<Gaussian>& mapped_gaussians,
    std::vector<Gaussian>& magic_gaussians,
    std::vector<Gaussian>& cnot_gaussians,
    Graph& graph,
    const Mapping& mapping,
    int t_lower_bound,
    int t_upper_bound,
    int cnot_threshold,
    double magic_high,
    double cnot_high
);
void update_gaussians_fine(
    Qubit* qubit,
    std::vector<Gaussian>& mapped_gaussians,
    std::vector<Gaussian>& magic_gaussians,
    std::vector<Gaussian>& cnot_gaussians,
    const Circuit& circuit,
    const Graph& graph,
    const Mapping& mapping,
    int CNOT_threshold,
    double magic_high,
    double magic_low,
    double cnot_high,
    double cnot_low
);
Node computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit, const std::vector<double>& baseline_cache, const std::vector<double>& mapped_cache);
void update_weight(std::vector<Gaussian>& gaussians, double new_weight);
void update_inverse(std::vector<Gaussian>& gaussians, bool inverse);

namespace {
double interpolate_weight(double low, double high, double ratio) {
    return low + (high - low) * std::clamp(ratio, 0.0, 1.0);
}

// Fold a gaussian's per-node contribution into a cache (cache[id] += g(node)).
// Used for the contributions that stay constant across iterations: the baseline
// (added once) and the mapped gaussians (append-only, one added per iteration),
// so computeNextMappingNode never re-sums them from scratch.
void add_gaussian_to_cache(const Graph& graph, std::vector<double>& cache, const Gaussian& g) {
    const int node_count = graph.get_node_count();
    for (int id = 0; id < node_count; ++id) {
        const Node& node = graph.get_node(id);
        cache[id] += g.gaussian_at(node.coordX, node.coordY);
    }
}
} // namespace




void Mapping::one_iteration_gaussian_mapping(Qubit* qubit, int* iterations, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, Gaussian& baseline_gaussian, const std::vector<double>& baseline_cache, std::vector<double>& mapped_cache) {

    std::vector<Gaussian> cnot_gaussians;

    switch (gaussianStrategy) {
        case GaussianStrategy::COARSE:
            update_gaussians_coarse(
                qubit,
                mapped_gaussians,
                magic_gaussians,
                cnot_gaussians,
                graph,
                *this,
                T_lower_bound,
                T_upper_bound,
                CNOT_threshold,
                magicHigh,
                cnotHigh
            );
            break;
        case GaussianStrategy::FINE:
            update_gaussians_fine(
                qubit,
                mapped_gaussians,
                magic_gaussians,
                cnot_gaussians,
                circuit,
                graph,
                *this,
                CNOT_threshold,
                magicHigh,
                magicLow,
                cnotHigh,
                cnotLow
            );
            break;
    }

    Node best_node = computeNextMappingNode(mapped_gaussians, magic_gaussians, cnot_gaussians, baseline_gaussian, graph, *qubit, baseline_cache, mapped_cache);

    const int mapped_node_id = map_qubit_to_node(qubit->getQubitID(), best_node.id, 0);
    const Node& mapped_node = graph.get_node(mapped_node_id);
    mapped_gaussians.push_back(Gaussians::mapped_gaussian(
        graph,
        mapped_node,
        mappedGaussianWeight,
        gaussianConfidence
    ));

    // mapped gaussians are append-only, so fold the new one into the running cache.
    add_gaussian_to_cache(graph, mapped_cache, mapped_gaussians.back());

    (*iterations)++;

}


void Mapping::gaussian_mapping() {
    if (PRINT_MAPPING) std::cout << "\n\n";

    std::vector<Gaussian> mapped_gaussians;
    std::vector<Gaussian> magic_gaussians;

    Gaussian baseline_gaussian = Gaussians::baseline_gaussian(graph, baseGaussianWeight, gaussianConfidence);

    // Per-node caches for the contributions that don't vary across the inner
    // candidate loop. baseline_cache is constant (computed once); mapped_cache is
    // a running sum grown by one gaussian per iteration. Kept separate so the
    // score sum reproduces the original order (mapped, then magic/cnot, then
    // baseline) bit-for-bit.
    const int node_count = graph.get_node_count();
    std::vector<double> baseline_cache(node_count, 0.0);
    std::vector<double> mapped_cache(node_count, 0.0);
    add_gaussian_to_cache(graph, baseline_cache, baseline_gaussian);

    for (int node_id : graph.get_magic_state_ids()) {
        magic_gaussians.push_back(Gaussians::magic_gaussian(graph, node_id, gaussianConfidence));
    }

    int total_qubits = circuit.getNumQubits();
    int iterations = 0;

    while (circuit.getHeapSize() > 0 && iterations < maximum_iterations) {
        if (MAPPING_VERBOSE) circuit.print_qubit_heap();
        Qubit* qubit = circuit.popFromHeap();
        if (qubit == nullptr) {
            continue;
        }
        if (get_mapped_node(qubit->getQubitID()) != -1) {
            continue; // already mapped as a side effect of mapping a related qubit
        }
        try {
            one_iteration_gaussian_mapping(qubit, &iterations, mapped_gaussians, magic_gaussians, baseline_gaussian, baseline_cache, mapped_cache);
        } catch (const SafePassageException& e) {
            throw SafePassageException(
                "Failed to map qubit " + std::to_string(qubit->getQubitID()) + ": " + e.what()
            );
        } catch (const std::exception& e) {
            throw std::runtime_error(
                "Failed to map qubit " + std::to_string(qubit->getQubitID()) + ": " + e.what()
            );
        }
        if (PRINT_MAPPING) std::cout << "Mapped qubits: " << iterations << "/" << total_qubits << "\n\n";
    }

    if (circuit.getHeapSize() > 0 && iterations >= maximum_iterations) {
        throw std::runtime_error(
            "Mapping stopped after reaching the maximum iteration limit (" +
            std::to_string(maximum_iterations) +
            ") before all active qubits were processed."
        );
    }
}






void update_gaussians_coarse(
    Qubit* qubit,
    std::vector<Gaussian>& mapped_gaussians,
    std::vector<Gaussian>& magic_gaussians,
    std::vector<Gaussian>& cnot_gaussians,
    Graph& graph,
    const Mapping& mapping,
    int t_lower_bound,
    int t_upper_bound,
    int cnot_threshold,
    double magic_high,
    double cnot_high
) {

    if (PRINT_MAPPING) std::cout << "Mapping qubit " << qubit->getQubitID() << " with T_count = "
              << qubit->getTCount() << " and max CNOT count = "
              << qubit->getMaxCNOTCount() << "\n";

    if (qubit->getTCount() > qubit->getMaxCNOTCount()) {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on T_count" << "\n";
        update_weight(magic_gaussians, magic_high);
        update_inverse(magic_gaussians, false);

    } else {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on CNOT_count" << "\n";

        std::vector<int> highCnotQubits = qubit->highCnotQubits(cnot_threshold);

        if (MAPPING_VERBOSE) {
            std::cout << "Qubits with CNOT count above threshold (" << cnot_threshold << "): ";
            for (int i : highCnotQubits) {
                const int mapped_node = mapping.get_mapped_node(i);
                std::cout << i << "(" << mapped_node << ") ";
            }
            std::cout << "\n";
        }
        
        for (int i : highCnotQubits) {
            int second_qubit_mapped_node = mapping.get_mapped_node(i);
            if (second_qubit_mapped_node != -1){
                cnot_gaussians.push_back(Gaussians::cnot_gaussian(
                    graph,
                    second_qubit_mapped_node,
                    cnot_high,
                    false,
                    mapping.getGaussianConfidence()
                ));
            }
        }



        if (qubit->getTCount() < t_lower_bound) {
            if (MAPPING_VERBOSE) std::cout << "mapping far from magic states because second qubit is not "
                             "mapped and T_count is low\n";
            update_weight(magic_gaussians, magic_high);
            update_inverse(magic_gaussians, true);
        } else if (qubit->getTCount() > t_upper_bound) {
            update_weight(magic_gaussians, magic_high);
            update_inverse(magic_gaussians, false);

        } else {
            update_weight(magic_gaussians, 0);
        }

        
    }
}


void update_gaussians_fine(
    Qubit* qubit,
    std::vector<Gaussian>& mapped_gaussians,
    std::vector<Gaussian>& magic_gaussians,
    std::vector<Gaussian>& cnot_gaussians,
    const Circuit& circuit,
    const Graph& graph,
    const Mapping& mapping,
    int CNOT_threshold,
    double magic_high,
    double magic_low,
    double cnot_high,
    double cnot_low
) {

    //2 pesi per T: LOW, HIGH
    //2 pesi per CNOT: LOW, HIGH

    //Se T_count = media allora peso = 0
    //Se T_count < media - varianza allora peso = peso alto, inverso
    //Se T_count > media + varianza allora peso = peso alto, non inverso
    //Se T_count compreso tra media e media - varianza, prendi T_count, 
    //                                 dividi per (media - varianza), e moltiplica per peso alto - basso, inverso
    //Se T_count compreso tra media e media + varianza, prendi T_count,
    //                                 dividi per (media + varianza) e moltiplica per peso alto - basso, non inverso


    //es: media = 10, varianza = 5, peso alto = 1, peso basso = 0.5
    //T_count = 5 -> peso = 1, inverso
    //T_count = 15 -> peso = 1, non inverso
    //T_count = 7 -> peso = 0.5 + (1 - 0.5) * (7 - 5) / (10 - 5) = 0.7, inverso
    //T_count = 12 -> peso = 0.5 + (1 - 0.5) * (12 - 10) / (15 - 10) = 0.7, non inverso

    // tutto uguale per CNOT


    const double T_mean = circuit.getTMean();
    const double T_std = circuit.getTStd();
    const double CNOT_mean = circuit.getCNOTMean();
    const double CNOT_std = circuit.getCNOTStd();
    const double t_count = static_cast<double>(qubit->getTCount());

    if (t_count == T_mean || T_std <= 0.0) {
        update_weight(magic_gaussians, 0);
    } else if (t_count < T_mean - T_std) {
        update_weight(magic_gaussians, magic_high);
        update_inverse(magic_gaussians, true);
    } else if (t_count > T_mean + T_std) {
        update_weight(magic_gaussians, magic_high);
        update_inverse(magic_gaussians, false);
    } else if (t_count >= T_mean - T_std && t_count <= T_mean) {
        double weight = interpolate_weight(magic_low, magic_high, (t_count - (T_mean - T_std)) / T_std);
        update_weight(magic_gaussians, weight);
        update_inverse(magic_gaussians, true);
    } else if (t_count > T_mean && t_count <= T_mean + T_std) {
        double weight = interpolate_weight(magic_low, magic_high, (t_count - T_mean) / T_std);
        update_weight(magic_gaussians, weight);
        update_inverse(magic_gaussians, false);
    }

    // Mirror coarse's dominant-regime split: only cluster on CNOT partners when the
    // qubit is CNOT-dominated. For a T-dominated qubit (T_count > maxCNOTCount),
    // adding the CNOT pull on top of the magic pull dilutes both forces and lands
    // it in a mediocre spot — part of why fine underperformed coarse. The magic
    // interpolation above always runs, as coarse also touches magic in both regimes.
    if (qubit->getTCount() <= qubit->getMaxCNOTCount()) {
        std::vector<int> high_cnot_qubits = qubit->highCnotQubits(CNOT_threshold);

        for (int q_id : high_cnot_qubits){
            const double cnot_count = static_cast<double>(circuit.getCNOTCount(qubit->getQubitID(), q_id));

            // These partners are pre-filtered by CNOT_threshold = ceil(CNOT_mean), so
            // they all interact at least as much as average. A shared CNOT must always
            // *attract* (never repel) and at no less than full strength: cnot_high is
            // the floor (matching coarse). The heaviest partners (beyond mean+std) get
            // a strong extra boost — empirically, the stronger this pull, the tighter
            // the heavily-interacting qubits cluster, which sharply cuts non-routed
            // layers (the primary metric). A sweep of the boost factor showed
            // non_routed mean(no-out) drops monotonically up to ~4x and then plateaus,
            // so the factor is fixed at 4 (peak weight ≈ cnot_high + 4*(cnot_high-cnot_low)).
            double weight = cnot_high;
            if (CNOT_std > 0.0 && cnot_count > CNOT_mean + CNOT_std) {
                weight = cnot_high + 4.0 * (cnot_high - cnot_low) *
                         std::clamp((cnot_count - (CNOT_mean + CNOT_std)) / CNOT_std, 0.0, 1.0);
            }

            const int mapped_node = mapping.get_mapped_node(q_id);
            if (mapped_node != -1) {
                cnot_gaussians.push_back(Gaussians::cnot_gaussian(
                    graph,
                    mapped_node,
                    weight,
                    false,
                    mapping.getGaussianConfidence()
                ));
            }

        }

        // Partners below the threshold still share real CNOTs, but they get no
        // cnot_gaussian above, so the universal repulsion from their mapped_gaussian
        // (inverse, weight mappedGaussianWeight) treats them exactly like
        // non-interacting strangers and pushes the qubit away from them. Add a mild
        // attraction, scaled by how much they interact, to partially cancel that
        // repulsion: the more CNOTs shared, the less they are pushed away. Stays
        // below cnot_high so genuinely strong partners keep priority, and zero-CNOT
        // qubits (excluded by lowCnotQubits) remain fully repelled.
        for (int q_id : qubit->lowCnotQubits(CNOT_threshold)) {
            const int mapped_node = mapping.get_mapped_node(q_id);
            if (mapped_node == -1) continue;

            const double cnot_count = static_cast<double>(circuit.getCNOTCount(qubit->getQubitID(), q_id));
            const double weight = cnot_low * (cnot_count / static_cast<double>(CNOT_threshold));
            if (weight <= 0.0) continue;

            cnot_gaussians.push_back(Gaussians::cnot_gaussian(
                graph,
                mapped_node,
                weight,
                false,
                mapping.getGaussianConfidence()
            ));
        }
    }

    
}



Node Mapping::computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit, const std::vector<double>& baseline_cache, const std::vector<double>& mapped_cache) {

    GaussianMappingVisualization::save_gaussian_frame(mapped_gaussians, magic_gaussians, cnot_gaussians, baseline_gaussian, graph, qubit, externalWeight);

    // Compute the combined Gaussian influence for each node and select the best one
    const std::vector<Node>& nodes = graph.get_nodes_ref();
    if (nodes.empty()) {
        throw std::runtime_error("Graph has no nodes");
    }

    struct CandidateScore {
        const Node* node = nullptr;
        double score = 0.0;
        std::size_t order = 0;
    };

    const std::vector<Node> occupied_nodes = graph.get_occupied_nodes();
    std::vector<CandidateScore> candidates;
    candidates.reserve(nodes.size());

    for (std::size_t order = 0; order < nodes.size(); ++order) {
        const Node& node = nodes[order];

        if (graph.is_occupied(node.id)) continue;
     
        // Same summation order as before (mapped, then magic, then cnot, then
        // baseline) so the result is bit-for-bit identical, but mapped and
        // baseline are read from their caches instead of being recomputed.
        double score = mapped_cache[node.id];
        for (const Gaussian& g : magic_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }
        for (const Gaussian& g : cnot_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }

        score += baseline_cache[node.id];

        const double ext_w = this->getExternalWeight();
        if (ext_w != 0.0) {
            const bool on_border = (node.coordX == 0 || node.coordX == graph.get_maxX() ||
                                    node.coordY == 0 || node.coordY == graph.get_maxY());
            if (on_border) {
                score += ext_w;
            }
        }

        if (std::isfinite(score)) {
            candidates.push_back(CandidateScore{&node, score, order});
        }
    }

    std::stable_sort(candidates.begin(), candidates.end(), [](const CandidateScore& a, const CandidateScore& b) {
        if (a.score != b.score) {
            return a.score > b.score;
        }
        return a.order < b.order;
    });

    for (const CandidateScore& candidate : candidates) {
        if (check_safe_passage(*candidate.node, qubit, occupied_nodes)) {
            if (PRINT_SAFE_PASSAGE) {
                std::cout << "Accepted map qubit " << qubit.getQubitID() << " into node " << candidate.node->id
                << ": passes safe passage" << std::endl; 
            }
            return *candidate.node;
        } else {
            if (PRINT_SAFE_PASSAGE) {
                std::cout << "tried to map qubit " << qubit.getQubitID() << " into node " << candidate.node->id
                << " but did not pass safe passage" << std::endl; 
            }
        }
    }

    if (candidates.empty()) {
        throw SafePassageException("No valid free non-magic node was found.");
    }

    throw SafePassageException("No valid free non-magic node with safe passage was found.");
}




void update_weight(std::vector<Gaussian>& gaussians, double new_weight) {
    for (Gaussian& g : gaussians) {
        g.update_weight(new_weight);
    }
}


void update_inverse(std::vector<Gaussian>& gaussians, bool inverse) {
    for (Gaussian& g : gaussians) {
        g.update_inverse(inverse);
    }
}
