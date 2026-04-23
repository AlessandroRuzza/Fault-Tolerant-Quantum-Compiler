#include "mapping.hpp"
#include "circuit.hpp"

void Mapping::magic_aware_mapping() {
    int total_qubits = circuit.getNumQubits();
    int iterations = 0;

    if (PRINT_MAPPING) std::cout << "\n\n";

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
            one_iteration_magic_aware_mapping(qubit, &iterations);
        } catch (const MapNearMagicError&) {
            pseudo_random_mapping(qubit, -1);
            iterations++; // consider this as an iteration even if it falls back to pseudo-random
        } catch (const MapNearQubitError&) {
            Qubit* fallback_qubit = qubit;
            const int second_qubit_id = qubit->getMaxCNOTCountIndex();
            if (get_mapped_node(qubit->getQubitID()) != -1 &&
                second_qubit_id >= 0 &&
                get_mapped_node(second_qubit_id) == -1) {
                fallback_qubit = const_cast<Qubit*>(circuit.getQubit(second_qubit_id));
            }
            if (fallback_qubit == nullptr) {
                throw std::runtime_error("Fallback mapping target is null.");
            }
            pseudo_random_mapping(fallback_qubit, -1);
            iterations++; // consider this as an iteration even if it falls back to pseudo-random
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

void Mapping::one_iteration_magic_aware_mapping(Qubit* qubit, int* iterations) {
    
    if (PRINT_MAPPING) std::cout << "Mapping qubit " << qubit->getQubitID() << " with T_count = "
              << qubit->getTCount() << " and max CNOT count = "
              << qubit->getMaxCNOTCount() << "\n";

    if (qubit->getTCount() > qubit->getMaxCNOTCount()) {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on T_count"
                  << "\n";
        int best_magic_state = graph.getBestMagicStateId();

        if (mapToNeighbor(qubit->getQubitID(), best_magic_state, 0)) {
            graph.increment_mapped_magic_state(best_magic_state);
        } else {
            throw MapNearMagicError(
                "Failed to map qubit " + std::to_string(qubit->getQubitID()) +
                " to a neighbor of magic state node " + std::to_string(best_magic_state) +
                ".\n");
        }
    } else {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on CNOT_count"
                  << "\n";
        int second_qubit = qubit->getMaxCNOTCountIndex();
        if (second_qubit < 0) {
            pseudo_random_mapping(qubit, -1);
            (*iterations)++;
            return;
        }
        int second_qubit_mapped_node = get_mapped_node(second_qubit);
        if (second_qubit_mapped_node != -1) {
            if (MAPPING_VERBOSE) std::cout << "mapping near qubit " << second_qubit
                      << " which is already mapped to node " << second_qubit_mapped_node
                      << "\n";
            if (!mapToNeighbor(qubit->getQubitID(), second_qubit_mapped_node, 0)) {
                throw MapNearQubitError(
                    "Failed to map qubit " + std::to_string(qubit->getQubitID()) +
                    " to a neighbor of mapped node " +
                    std::to_string(second_qubit_mapped_node) + ".\n");
            }
        } else {
            int best_magic_state_id = graph.getBestMagicStateId();
            if (MAPPING_VERBOSE) std::cout << "Second qubit " << second_qubit << " is not mapped yet.\n";
            if (qubit->getTCount() > T_upper_bound) {
                if (MAPPING_VERBOSE) std::cout
                    << "mapping near magic state because second qubit is not mapped and "
                       "T_count is high\n";
                if (mapToNeighbor(qubit->getQubitID(), best_magic_state_id, 0)) {
                    graph.increment_mapped_magic_state(best_magic_state_id);
                } else {
                    throw MapNearMagicError(
                        "Failed to map qubit " + std::to_string(qubit->getQubitID()) +
                        " to a neighbor of magic state node " +
                        std::to_string(best_magic_state_id) + ".\n");
                }

                if (MAPPING_VERBOSE) std::cout << "mapping second qubit near the first\n";
                int qubit_mapped_node = get_mapped_node(qubit->getQubitID());
                if (mapToNeighbor(second_qubit, qubit_mapped_node, 0)) {
                    graph.increment_mapped_magic_state(best_magic_state_id);
                } else {
                    throw MapNearQubitError(
                        "Failed to map qubit " + std::to_string(qubit->getQubitID()) +
                        " to a neighbor of qubit " +
                        std::to_string(qubit->getQubitID()) + ".\n");
                }
            } else if (qubit->getTCount() < T_lower_bound) {
                if (MAPPING_VERBOSE) std::cout << "mapping far from magic states because second qubit is not "
                             "mapped and T_count is low\n";
                int node_id = farthest_from_magic_selector.pick_next();
                if (node_id != -1) {
                    map_qubit_to_node(qubit->getQubitID(), node_id, 0);
                } else {
                    throw std::runtime_error("No available node found far from magic states "
                                             "for qubit " +
                                             std::to_string(qubit->getQubitID()) + ".\n");
                }

                if (MAPPING_VERBOSE) std::cout << "mapping second qubit near the first\n";
                if (!mapToNeighbor(second_qubit, node_id, 0)) {
                    throw MapNearQubitError(
                        "Failed to map qubit " + std::to_string(qubit->getQubitID()) +
                        " to a neighbor of mapped node " +
                        std::to_string(qubit->getQubitID()) + ".\n");
                }
            } else {
                pseudo_random_mapping(qubit, second_qubit);
            }
        }
    }

    (*iterations)++;
}
