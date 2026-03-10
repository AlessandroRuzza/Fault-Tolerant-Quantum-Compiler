#include "mapping.hpp"
#include "circuit.hpp"

void Mapping::homogenous_mapping_rowmajor(int maxX, int maxY) {
    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();

    for (int qubit_id = 0, node_id = 0, count = 0; qubit_id < circuit.getNumQubits();
         node_id += 2) {
        if (node_id >= graph.get_node_count()) {
            std::cerr << "Not enough nodes in the graph to map all qubits homogeneously.\n";
            break;
        }
        if (std::find(magic_state_ids.begin(), magic_state_ids.end(), node_id) == magic_state_ids.end()) {
            map_qubit_to_node(qubit_id, node_id);
            qubit_id++;
            count++;
            if (maxY % 2 == 1 && count == (maxY + 1) / 2) {
                node_id += maxY - 1;
                count = 0;
            }
            if (maxY % 2 == 0 && count == maxY / 2) {
                node_id += maxY;
                count = 0;
            }
        }
    }
}
