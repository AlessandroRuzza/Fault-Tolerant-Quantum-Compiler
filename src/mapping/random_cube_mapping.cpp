#include "mapping.hpp"
#include "circuit.hpp"

#include <algorithm>
#include <random>
#include <stdexcept>
#include <vector>

void Mapping::random_cube_mapping() {
    const std::vector<int> magic_state_ids = graph.get_magic_state_ids();
    const std::unordered_set<int> magic_set(magic_state_ids.begin(), magic_state_ids.end());
    const int width  = graph.getMaxX() + 1;
    const int height = graph.getMaxY() + 1;

    static thread_local std::mt19937 rng(std::random_device{}());

    // Single pass: visit rows y = 0, 2, 4, ...
    // Within each row walk columns with "one yes, one no":
    //   - normal cell: add to candidates, advance by 2
    //   - magic cell:  skip it, add the next cell (if valid), advance by 2 from there
    std::vector<int> candidates;
    candidates.reserve(graph.get_node_count() / 4);

    for (int y = 0; y < height; y += 2) {
        int x = 0;
        while (x < width) {
            const int node_id = y * width + x;
            if (magic_set.count(node_id)) {
                ++x;                              // skip over the magic state
                if (x < width) {
                    const int next_id = y * width + x;
                    if (!magic_set.count(next_id) && !graph.is_occupied(next_id))
                        candidates.push_back(next_id);
                }
                x += 2;                           // keep the one-yes-one-no rhythm
            } else {
                if (!graph.is_occupied(node_id))
                    candidates.push_back(node_id);
                x += 2;
            }
        }
    }

    if (candidates.empty())
        throw std::runtime_error("No mappable node found in random_cube_mapping.");

    std::shuffle(candidates.begin(), candidates.end(), rng);

    const int total_qubits = circuit.getNumQubits();
    int cand_idx = 0;
    int mapped   = 0;
    for (int qubit_id = 0; qubit_id < circuit.getQubitsVectorSize(); ++qubit_id) {
        const Qubit* qubit = circuit.getQubit(qubit_id);
        if (qubit == nullptr) continue;
        if (get_mapped_node(qubit_id) != -1) continue;

        if (cand_idx >= static_cast<int>(candidates.size()))
            throw std::runtime_error(
                "No cube-valid node found for qubit " + std::to_string(qubit_id) + ".");

        const int chosen = candidates[cand_idx++];
        graph_to_circuit[qubit_id] = chosen;
        graph.occupy_node(chosen);
        if (PRINT_MAPPING) std::cout << "\nMapped qubit " << qubit_id << " to node " << chosen << "\n";
        if (PRINT_MAPPING_GRAPH) graph.print_rectangular();
        ++mapped;
        if (PRINT_MAPPING) std::cout << "Mapped qubits: " << mapped << "/" << total_qubits << "\n\n";
    }

    if (mapped < circuit.getNumQubits())
        std::cerr << "Not all qubits were mapped in random_cube_mapping.\n";
}
