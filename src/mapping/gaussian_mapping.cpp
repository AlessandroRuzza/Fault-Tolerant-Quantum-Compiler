#include "mapping.hpp"
#include "gaussian.hpp"
#include "circuit.hpp"
#include "qubit.hpp"
#include "graph.hpp"

#define MAPPED_GAUSSIAN_WEIGHT 0.8
#define MAGIC_HIGHEST 1.5
#define MAGIC_ABOVE_THRESHOLD 1.2
#define CNOT_ABOVE_THRESHOLD 1.5
#define MAGIC_BELOW_THRESHOLD 1.2
#define BASE_GAUSSIAN_WEIGHT 1

#define CNOT_THRESHOLD 

double compute_sigma(int radius, double confidence) return radius / sqrt(-2 * log(1 - confidence));
void update_weight(std::vector<Gaussian>& gaussians, double new_weight);
void update_inverse(std::vector<Gaussian>& gaussians, bool inverse);
void update_gaussians(Qubit qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians);
Node computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians);



void one_iteration_gaussian_mapping(Qubit qubit, int* iterations, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians) {
    
    std::vector<Gaussian> cnot_gaussians;

    update_gaussians(qubit, mapped_gaussians, magic_gaussians, cnot_gaussians);

    Node best_node = computeNextMappingNode(mapped_gaussians, magic_gaussians, cnot_gaussians);
    map_qubit_to_node(qubit->getQubitID(), best_node.id);

    gaussians.push_back(Gaussian(
        //mean
        best_node.get_coordinates().first,
        best_node.get_coordinates().second,

        //sigma
        compute_sigma(circuit.get_maxX() / 2, 0.95),
        compute_sigma(circuit.get_maxY() / 2, 0.95),

        //size
        circuit.get_maxX() / 2.0, 
        circuit.get_maxY() / 2.0, 

        //weight
        MAPPED_GAUSSIAN_WEIGHT,

        //inverse
        true
    ));


    (*iterations)++;

}


void Mapping::gaussian_mapping() {
    if (PRINT_MAPPING) std::cout << "\n\n";
    
    std::vector<Gaussian> mapped_gaussians;
    std::vector<Gaussian> magic_gaussians;

    Gaussian baseline_gaussian(
        //mean
        circuit.get_maxX() / 2,
        circuit.get_maxY() / 2,

        //sigma
        compute_sigma(circuit.get_maxX() / 2, 0.95),
        compute_sigma(circuit.get_maxY() / 2, 0.95),

        //size
        circuit.get_maxX() / 2.0, 
        circuit.get_maxY() / 2.0, 

        //weight
        BASE_GAUSSIAN_WEIGHT,

        //inverse
        false
    );
    
    for (int node_id : graph.getMagicStateNodes()) {
        magic_gaussians.push_back(Gaussian(
            //mean
            graph.getNodeX(node_id),
            graph.getNodeY(node_id),

            //sigma
            compute_sigma(circuit.get_maxX() / 4, 0.95),
            compute_sigma(circuit.get_maxY() / 4, 0.95),

            //size
            circuit.get_maxX() / 4.0, 
            circuit.get_maxY() / 4.0, 

            //weight
            BASE_GAUSSIAN_WEIGHT,

            //inverse
            false
        ));
    }
    

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
            one_iteration_gaussian_mapping(qubit, &iterations, mapped_gaussians, magic_gaussians);
        } catch (const std::exception& e) {
            throw std::runtime_error(
                "Failed to map qubit " + std::to_string(qubit->getQubitID()) + ": " + e.what()
            );
        }
        if (PRINT_MAPPING) std::cout << "Mapped qubits: " << iterations << "/" << total_qubits << "\n\n";
    }
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





void update_gaussians(Qubit qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians) {

    if (PRINT_MAPPING) std::cout << "Mapping qubit " << qubit->getQubitID() << " with T_count = "
              << qubit->getTCount() << " and max CNOT count = "
              << qubit->getMaxCNOTCount() << "\n";

    if (qubit->getTCount() > qubit->getMaxCNOTCount()) {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on T_count" << "\n";
        update_weight(magic_gaussians, MAGIC_ABOVE_THRESHOLD);

    } else {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on CNOT_count" << "\n";

        std::vector<int> qubit.highCnotQubits(CNOT_THRESHOLD);
        
        for (int i = 0; i < circuit.getNumQubits(); i++){
            int second_qubit_mapped_node = get_mapped_node(i);
            if (second_qubit_mapped_node != -1){
                cnot_gaussians.push_back(Gaussian(
                    //mean
                    graph.get_coordX(second_qubit_mapped_node),
                    graph.get_coordY(second_qubit_mapped_node),


                    //sigma
                    compute_sigma(circuit.get_maxX() , 0.95),
                    compute_sigma(circuit.get_maxY() , 0.95),

                    //size
                    circuit.get_maxX() / 2.0, 
                    circuit.get_maxY() / 2.0, 

                    //weight
                    CNOT_ABOVE_THRESHOLD,

                    //inverse
                    false
                ));
            }
        }


        if (qubit.getTCount() < T_lower_bound) {
            if (MAPPING_VERBOSE) std::cout << "mapping far from magic states because second qubit is not "
                             "mapped and T_count is low\n";
            update_weight(magic_gaussians, MAGIC_BELOW_THRESHOLD);
            update_inverse(magic_gaussians, true);
        } else {
            update_weight(mapped_gaussians, MAGIC_HIGHEST);
        }

        
    }
}




Node computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians) {
    // Compute the combined Gaussian influence for each node and select the best one
    Node best_node;
    double best_score = -std::numeric_limits<double>::infinity();

    for (const Node& node : graph.get_nodes()) {
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

        if (score > best_score && !node.occupied) {
            best_score = score;
            best_node = node;
        }
    }

    return best_node;
}

