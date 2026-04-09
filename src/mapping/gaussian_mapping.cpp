#include "mapping.hpp"
#include "gaussian.hpp"
#include "circuit.hpp"
#include "qubit.hpp"
#include "graph.hpp"
#include "gaussian_images.hpp"
#include "gaussians.hpp"

#include <array>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>


#define MAGIC_HIGH 1.5
#define MAGIC_LOW 0.5

#define CNOT_HIGH 1.5
#define CNOT_LOW 0.5


void update_weight(std::vector<Gaussian>& gaussians, double new_weight);
void update_inverse(std::vector<Gaussian>& gaussians, bool inverse);
void update_gaussians_coarse(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Graph& graph, const Mapping& mapping, int t_lower_bound, int t_upper_bound, int cnot_threshold);
void update_gaussians_fine(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, const Circuit& circuit, const Graph& graph, const Mapping& mapping, int CNOT_threshold);
Node computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit);
void update_weight(std::vector<Gaussian>& gaussians, double new_weight);
void update_inverse(std::vector<Gaussian>& gaussians, bool inverse);




void Mapping::one_iteration_gaussian_mapping(Qubit* qubit, int* iterations, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, Gaussian& baseline_gaussian) {
    
    std::vector<Gaussian> cnot_gaussians;

    switch (gaussianStrategy) {
        case GaussianStrategy::COARSE:
            update_gaussians_coarse(qubit, mapped_gaussians, magic_gaussians, cnot_gaussians, graph, *this, T_lower_bound, T_upper_bound, CNOT_threshold);
            break;
        case GaussianStrategy::FINE:
            update_gaussians_fine(qubit, mapped_gaussians, magic_gaussians, cnot_gaussians, circuit, graph, *this, CNOT_threshold);
            break;
    }

    Node best_node = computeNextMappingNode(mapped_gaussians, magic_gaussians, cnot_gaussians, baseline_gaussian, graph, *qubit);
    
    map_qubit_to_node(qubit->getQubitID(), best_node.id, 0);

    mapped_gaussians.push_back(Gaussians::mapped_gaussian(graph, best_node));

    (*iterations)++;

}


void Mapping::gaussian_mapping() {
    if (PRINT_MAPPING) std::cout << "\n\n";
    
    std::vector<Gaussian> mapped_gaussians;
    std::vector<Gaussian> magic_gaussians;

    Gaussian baseline_gaussian = Gaussians::baseline_gaussian(graph);
    
    for (int node_id : graph.get_magic_state_ids()) {
        magic_gaussians.push_back(Gaussians::magic_gaussian(graph, node_id));
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
            one_iteration_gaussian_mapping(qubit, &iterations, mapped_gaussians, magic_gaussians, baseline_gaussian);
        } catch (const std::exception& e) {
            throw std::runtime_error(
                "Failed to map qubit " + std::to_string(qubit->getQubitID()) + ": " + e.what()
            );
        }
        if (PRINT_MAPPING) std::cout << "Mapped qubits: " << iterations << "/" << total_qubits << "\n\n";
    }
}






void update_gaussians_coarse(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Graph& graph, const Mapping& mapping, int t_lower_bound, int t_upper_bound, int cnot_threshold) {

    if (PRINT_MAPPING) std::cout << "Mapping qubit " << qubit->getQubitID() << " with T_count = "
              << qubit->getTCount() << " and max CNOT count = "
              << qubit->getMaxCNOTCount() << "\n";

    if (qubit->getTCount() > qubit->getMaxCNOTCount()) {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on T_count" << "\n";
        update_weight(magic_gaussians, MAGIC_HIGH);
        update_inverse(magic_gaussians, false);

    } else {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on CNOT_count" << "\n";

        std::vector<int> highCnotQubits = qubit->highCnotQubits(cnot_threshold);

        std::cout << "Qubits with CNOT count above threshold (" << cnot_threshold << "): ";
        for (int i : highCnotQubits) {
            std::cout << i << " ";
        }
        
        for (int i : highCnotQubits) {
            int second_qubit_mapped_node = mapping.get_mapped_node(i);
            if (second_qubit_mapped_node != -1){
                cnot_gaussians.push_back(Gaussians::cnot_gaussian(graph, second_qubit_mapped_node, CNOT_HIGH, false));
            }
        }



        if (qubit->getTCount() < t_lower_bound) {
            if (MAPPING_VERBOSE) std::cout << "mapping far from magic states because second qubit is not "
                             "mapped and T_count is low\n";
            update_weight(magic_gaussians, MAGIC_HIGH);
            update_inverse(magic_gaussians, true);
        } else if (qubit->getTCount() > t_upper_bound) {
            update_weight(magic_gaussians, MAGIC_HIGH);
            update_inverse(magic_gaussians, false);

        } else {
            update_weight(magic_gaussians, 0);
        }

        
    }
}


void update_gaussians_fine(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, const Circuit& circuit, const Graph& graph, const Mapping& mapping, int CNOT_threshold) {

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


    const int T_mean = circuit.getTMean();
    const int T_std = circuit.getTStd();
    const int CNOT_mean = circuit.getCNOTMean();
    const int CNOT_std = circuit.getCNOTStd();

    if (qubit->getTCount() == T_mean) {
        update_weight(magic_gaussians, 0);
    } else if (qubit->getTCount() < T_mean - T_std) {
        update_weight(magic_gaussians, MAGIC_HIGH);
        update_inverse(magic_gaussians, true);
    } else if (qubit->getTCount() > T_mean + T_std) {
        update_weight(magic_gaussians, MAGIC_HIGH);
        update_inverse(magic_gaussians, false);
    } else if (qubit->getTCount() >= T_mean - T_std && qubit->getTCount() <= T_mean) {
        double weight = MAGIC_LOW + (MAGIC_HIGH - MAGIC_LOW) * (qubit->getTCount() - (T_mean - T_std)) / (T_std);
        update_weight(magic_gaussians, weight);
        update_inverse(magic_gaussians, true);
    } else if (qubit->getTCount() > T_mean && qubit->getTCount() <= T_mean + T_std) {
        double weight = MAGIC_LOW + (MAGIC_HIGH - MAGIC_LOW) * ((qubit->getTCount() - T_mean) / (T_std));
        update_weight(magic_gaussians, weight);
        update_inverse(magic_gaussians, false);
    }

    std::vector<int> high_cnot_qubits = qubit->highCnotQubits(CNOT_threshold);

    for (int q_id : high_cnot_qubits){
        double weight = 0.0;
        bool inverse;

        if (circuit.getCNOTCount(qubit->getQubitID(), q_id) == CNOT_mean) {
            weight = 0.0;
            inverse = false;
        } else if (circuit.getCNOTCount(qubit->getQubitID(), q_id) < CNOT_mean - CNOT_std) {
            weight = CNOT_HIGH;
            inverse = true;
        } else if (circuit.getCNOTCount(qubit->getQubitID(), q_id) > CNOT_mean + CNOT_std) {
            weight = CNOT_HIGH;
            inverse = false;

        } else if (circuit.getCNOTCount(qubit->getQubitID(), q_id) >= CNOT_mean - CNOT_std && 
                   circuit.getCNOTCount(qubit->getQubitID(), q_id) <= CNOT_mean) {

            weight = CNOT_LOW + (CNOT_HIGH - CNOT_LOW) * (qubit->getMaxCNOTCount() - (CNOT_mean - CNOT_std)) / (CNOT_std);
            inverse = true;

        } else if (circuit.getCNOTCount(qubit->getQubitID(), q_id) > CNOT_mean && 
                   circuit.getCNOTCount(qubit->getQubitID(), q_id) <= CNOT_mean + CNOT_std) {

            weight = CNOT_LOW + (CNOT_HIGH - CNOT_LOW) * ((qubit->getMaxCNOTCount() - CNOT_mean) / (CNOT_std));
            inverse = false;
        }

        const int mapped_node = mapping.get_mapped_node(q_id);
        if (mapped_node != -1) {
            cnot_gaussians.push_back(Gaussians::cnot_gaussian(graph, mapped_node, weight, inverse));
        }

    }

    
}



Node Mapping::computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit) {
    
    GaussianMappingVisualization::save_gaussian_frame(mapped_gaussians, magic_gaussians, cnot_gaussians, baseline_gaussian, graph, qubit);

    // Compute the combined Gaussian influence for each node and select the best one
    const std::vector<Node> nodes = graph.get_nodes();
    if (nodes.empty()) {
        throw std::runtime_error("Graph has no nodes");
    }

    Node best_node = nodes.front();
    double best_score = -std::numeric_limits<double>::infinity();
    const std::vector<int> magic_ids = graph.get_magic_state_ids();

    for (const Node& node : graph.get_nodes()) {
        

        if (node.occupied) {
            continue;
        }
        if (std::find(magic_ids.begin(), magic_ids.end(), node.id) != magic_ids.end()) {
            continue;
        }

        bool is_safe = check_safe_passage(node);
        if (!is_safe) {
            continue;
        }


        double score = 0.0;

        for (const Gaussian& g : mapped_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }
        for (const Gaussian& g : magic_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }
        for (const Gaussian& g : cnot_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }

        score += baseline_gaussian.gaussian_at(node.coordX, node.coordY);

        if (score > best_score) {
            best_score = score;
            best_node = node;
        }
    }

    return best_node;
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
