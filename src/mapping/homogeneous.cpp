#include "mapping.hpp"
#include "circuit.hpp"

void Mapping::homogeneous_mapping() {
    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
    const int width = graph.getMaxX() + 1;
    const int height = graph.getMaxY() + 1;
    int qubit_id = 0;
    int mapped = 0;

    const auto next_active_qubit = [&]() {
        while (qubit_id < circuit.getQubitsVectorSize() && circuit.getQubit(qubit_id) == nullptr) {
            ++qubit_id;
        }
    };

    const auto map_pass = [&](int row_start, int col_start) {
        for (int y = row_start; y < height && qubit_id < circuit.getQubitsVectorSize(); y += 2) {
            for (int x = col_start; x < width && qubit_id < circuit.getQubitsVectorSize(); x += 2) {
                const int node_id = y * width + x;
                if (std::find(magic_state_ids.begin(), magic_state_ids.end(), node_id) != magic_state_ids.end()) {
                    continue;
                }
                // safe_passage fallback may place the current qubit on a different
                // node that will be visited later by this scan.
                if (graph.is_occupied(node_id)) {
                    continue;
                }
                map_qubit_to_node(qubit_id, node_id, 0);
                ++mapped;
                ++qubit_id;
                next_active_qubit();
            }
        }
    };

    next_active_qubit();
    map_pass(0, 0); // righe pari, colonne pari
    map_pass(0, 1); // righe pari, colonne dispari
    map_pass(1, 0); // righe dispari, colonne pari
    map_pass(1, 1); // righe dispari, colonne dispari

    if (mapped < circuit.getNumQubits()) {
        std::cerr << "Not enough nodes in the graph to map all qubits homogeneously.\n";
    }
}
