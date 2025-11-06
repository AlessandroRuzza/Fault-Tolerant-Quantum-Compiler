#include "mapping.hpp"
#include "circuit.hpp"

using namespace circuit;

//IDEA PER IL FUTURO:
//calcolare pc = CNOT_count / (CNOT_count + T_count) 
//calcolare pt = T_count / (CNOT_count + T_count) 
//mappare vicino in mezzo al magic state e al cnot vicino spostato più verso quale valore tra pc e pt è più grande



// if CNOT count > T_count:
    //if T_count > upper_bound: map to magic state
    //if T_count < lower_bound: map far from magic state
    //else: map randomly)
void Mapping::magic_aware_mapping(int T_lower_bound, int T_upper_bound, int maximum_iterations, FarthestFromMagicSelector& farthest_from_magic_selector) {
    // Implement mapping logic here
    int mapped_qubits = 0;
    int total_qubits = circuit.getNumQubits();

    //mapping ad ammassi, se n qubit hanno tanti CNOT con lo stesso qubit,
    //vengono ammassati, non si cerca il secondo migliore 

    int c = 0;
    std::cout << "total_qubits:" << total_qubits;
    while (circuit.getHeapSize() > 0 && c < maximum_iterations) {
        circuit.print_qubit_heap();
        Qubit* qubit = circuit.popFromHeap();
        if (qubit->getTCount() > qubit->getMaxCNOTCount()) {
            // voglio mapppare inizialmente a caso in un magic state e aggiornare il valore di 
            // mapped_magic_states, poi ogni volta che mappo un altro qubit, anche solo perchè ha tanti 
            // CNOT con un qubit già mappato 'vicino' (setto una threshold che dipende dalle dimensioni totali) 
            // a un magic state, aggiorno mapped_magic_states
            // scelgo il magic state con meno qubit mappati vicino
            int best_magic_state = graph.getBestMagicStateId();

            int node_id;
            if (mapToNeighbor(qubit, best_magic_state)) {
                graph.increment_mapped_magic_state(best_magic_state);
                mapped_qubits++;
            } else throw std::runtime_error("Failed to map qubit " + std::to_string(qubit->getQubitID()) + " to a neighbor of magic state node " + std::to_string(best_magic_state) + ".\n");
        } else {
            int second_qubit = qubit->getMaxCNOTCountIndex();
            int mapped_node = get_mapped_node(second_qubit);
            if (mapped_node != -1) {
                // Try to find an unoccupied neighbor of the mapped node
                if (mapToNeighbor(qubit, mapped_node)) {
                    mapped_qubits++;
                } else throw std::runtime_error("Failed to map qubit " + std::to_string(qubit->getQubitID()) + " to a neighbor of mapped node " + std::to_string(mapped_node) + ".\n");
            } else {
                    int bestMagicStateId = graph.getBestMagicStateId();                std::cout << "Second qubit " << second_qubit << " is not mapped yet.\n";
                if (qubit->getTCount() > T_upper_bound) {
                    // Map to any available non-magic state node

                    if (mapToNeighbor(qubit, bestMagicStateId)) {
                        graph.increment_mapped_magic_state(bestMagicStateId);
                        mapped_qubits++;
                    } else throw std::runtime_error("Failed to map qubit " + std::to_string(qubit->getQubitID()) + " to a neighbor of magic state node " + std::to_string(bestMagicStateId) + ".\n");

                    if (mapToNeighbor(circuit.getQubit(second_qubit), qubit->getQubitID())) {
                        graph.increment_mapped_magic_state(bestMagicStateId);
                        mapped_qubits++;
                    } else throw std::runtime_error("Failed to map qubit " + std::to_string(qubit->getQubitID()) + " to a neighbor of magic state node " + std::to_string(bestMagicStateId) + ".\n");
                } else if (qubit->getTCount() < T_lower_bound) {
                    // Map far from magic states
                    int node_id = farthest_from_magic_selector.pick_next();
                    if (node_id != -1) {
                        map_qubit_to_node(qubit->getQubitID(), node_id);
                        mapped_qubits++;
                    } else throw std::runtime_error("No available node found far from magic states for qubit " + std::to_string(qubit->getQubitID()) + ".\n");

                    if (mapToNeighbor(circuit.getQubit(second_qubit), qubit->getQubitID())) {
                        mapped_qubits++;
                    } else throw std::runtime_error("Failed to map qubit " + std::to_string(qubit->getQubitID()) + " to a neighbor of mapped node " + std::to_string(qubit->getQubitID()) + ".\n");
                    
                } else {
                    // Map randomly to any available node
                    for (int node_id = 0; node_id < graph.get_node_count(); node_id++) {
                        if (!graph.is_occupied(node_id)) {
                            map_qubit_to_node(qubit->getQubitID(), node_id);
                            mapped_qubits++;
                            break;
                        }
                    }
                    if (mapToNeighbor(circuit.getQubit(second_qubit), qubit->getQubitID())){
                        graph.increment_mapped_magic_state(bestMagicStateId);
                        mapped_qubits++;
                    }

                }
            }
        }
        c++;

    }
}

void Mapping::homogenous_mapping_rowmajor(int maxX, int maxY) {
    for(int qubit_id=0, node_id=0, count=0; qubit_id<circuit.getNumQubits(); qubit_id++, node_id+=2){
        if(qubit_id >= graph.get_node_count()){
            std::cerr << "Not enough nodes in the graph to map all qubits homogeneously.\n";
            break;
        }
        if(!graph.get_magic_states().contains(node_id)) {
            map_qubit_to_node(qubit_id, node_id);
            count++;
            if(maxY%2 == 1 && count == (maxY+1)/2){
                node_id += maxY-1;
                count = 0;
            }
            if(maxY%2 == 0 && count == (maxY)/2){
                node_id += maxY;
                count = 0;
            }
        }
    }
}