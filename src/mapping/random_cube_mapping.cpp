#include "mapping.hpp"
#include "circuit.hpp"
#include "exceptions.hpp"

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

    std::vector<int>& candidates = candidates_cache;

    if(candidates.empty()){
        candidates.reserve(graph.get_node_count() / 4);

        const auto row_has_magic_gt2 = [&](int row) {
            if (row < 0 || row >= height) return false;
            int acc = 0;
            for (int x = 0; x < width; ++x)
                if (magic_set.count(row * width + x)) acc++;
            return acc > 2;
        };

        const auto row_has_magic = [&](int row) {
            if (row < 0 || row >= height) return false;
            int acc = 0;
            for (int x = 0; x < width; ++x)
                if (magic_set.count(row * width + x)) acc++;
            return acc > 0;
        };

        const auto is_magic_at = [&](int ny, int nx) -> bool {
            if (ny < 0 || ny >= height || nx < 0 || nx >= width) return false;
            return magic_set.count(ny * width + nx) > 0;
        };

        // Returns true if any row or column of the 3x3 neighborhood of (cy,cx)
        // contains 2 or more magic states (catches adjacent and opposite pairs).
        const auto has_magic_alignment = [&](int cy, int cx) -> bool {
            for (int dy = -1; dy <= 1; ++dy) {
                int row_count = 0;
                for (int dx = -1; dx <= 1; ++dx) {
                    if (dy == 0 && dx == 0) continue;
                    if (is_magic_at(cy + dy, cx + dx)) ++row_count;
                }
                if (row_count >= 2) return true;
            }
            for (int dx = -1; dx <= 1; ++dx) {
                int col_count = 0;
                for (int dy = -1; dy <= 1; ++dy) {
                    if (dy == 0 && dx == 0) continue;
                    if (is_magic_at(cy + dy, cx + dx)) ++col_count;
                }
                if (col_count >= 2) return true;
            }
            return false;
        };

        for (int y = 0; y < height; y += 2) {
            if (y == 0 || y == height - 1){
                if (row_has_magic(y+1)) {
                    y -= 1;
                    continue;
                }
                if (y > 0){
                    if (row_has_magic(y-1)) {
                        y -= 1;
                        continue;
                    }
                }
            } else {
                if (row_has_magic_gt2(y+1)) {
                    y -= 1;
                    continue;
                }
                if (y > 0){
                    if (row_has_magic_gt2(y-1)) {
                        y -= 1;
                        continue;
                    }
                }
            }

            for (int x = 0; x < width; x += 2) {
                const int nid = y * width + x;
                if (magic_set.count(nid +1)) {x -= 1; continue;}
                if (magic_set.count(nid)) continue;
                if (graph.is_occupied(nid)) continue;
                if (has_magic_alignment(y, x)) continue;

                candidates.push_back(nid);
            }
        }

        if (PRINT_MAPPING_GRAPH) {
            const std::unordered_set<int> cand_set(candidates.begin(), candidates.end());
            graph.print_rectangular(cand_set);
        }

        if (static_cast<int>(candidates.size()) < circuit.getNumQubits())
            throw SafePassageException(
                "Not enough cube-valid candidates (" + std::to_string(candidates.size()) +
                ") for " + std::to_string(circuit.getNumQubits()) + " qubits in random_cube_mapping.");

    }

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
