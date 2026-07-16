#pragma once

#include "circuit.hpp"
#include "graph.hpp"
#include "mapping.hpp"
#include "routing.hpp"

#include <nlohmann/json.hpp>

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Serialize the routed circuit in WISQ's `--mode scmr` output schema, so every
// consumer that already reads a WISQ result reads ours unchanged
// (scripts/plots/visualize_wisq_steps.py, visualize_wisq_schedule.py, the step
// counters in scripts/wisq_compare/):
//
//   {"map":   [[logical_qubit, node], ...],
//    "arch":  {"width", "height", "alg_qubits", "magic_states"},
//    "steps": [[{"id", "op", "qubits", "path": [node, ...]}, ...], ...],
//    "gates": [{"id", "op", "qubits"}, ...]}
//
// Nodes are flat row-major grid indices (node = y * width + x), WISQ's
// convention and the one Graph::create_rectangular_with_magic_states assigns.
// `arch.alg_qubits` lists the nodes actually holding a logical qubit: WISQ picks
// its data qubits from a fixed even/even sublattice, we let the mapper choose,
// so the field means "occupied slots" here rather than "available slots".
//
// `steps` holds the best repetition's routing: step i is the set of gates routed
// in parallel on that step, each with the node path lattice surgery follows
// (2-qubit gate: node(control) -> node(target); T gate: node(qubit) -> magic
// state). Gates are sorted by id, so two runs of the same configuration produce
// byte-identical files.
inline void write_routing_json(
    const std::filesystem::path& out_path,
    const Circuit& circuit,
    const Graph& graph,
    const Mapping& mapping,
    const IQubitRouter& router
) {
    using nlohmann::json;

    const auto gate_to_json = [](const Gate& gate) {
        json entry;
        entry["id"] = gate.id;
        entry["op"] = gate.name;
        entry["qubits"] = gate.qubits;
        return entry;
    };

    json map_entries = json::array();
    std::vector<int> alg_qubits;
    for (int qubit = 0; qubit < circuit.getQubitsVectorSize(); ++qubit) {
        if (circuit.getQubit(qubit) == nullptr) {
            continue;
        }
        const int node = mapping.get_mapped_node(qubit);
        if (node < 0) {
            continue;
        }
        map_entries.push_back(json::array({qubit, node}));
        alg_qubits.push_back(node);
    }
    std::sort(alg_qubits.begin(), alg_qubits.end());

    std::vector<int> magic_states = graph.get_magic_state_ids();
    std::sort(magic_states.begin(), magic_states.end());

    json steps = json::array();
    for (const Routing& step : router.get_routing()) {
        std::vector<std::pair<const Gate*, const Path*>> ordered;
        ordered.reserve(step.size());
        for (const auto& [gate, path] : step) {
            ordered.emplace_back(&gate, &path);
        }
        // Routing is an unordered_map: sort by gate id so the output is
        // reproducible instead of hash-order dependent.
        std::sort(ordered.begin(), ordered.end(),
                  [](const auto& a, const auto& b) { return a.first->id < b.first->id; });

        json step_json = json::array();
        for (const auto& [gate, path] : ordered) {
            json entry = gate_to_json(*gate);
            entry["path"] = *path;
            step_json.push_back(std::move(entry));
        }
        steps.push_back(std::move(step_json));
    }

    json gates = json::array();
    for (const Gate& gate : circuit.getGates()) {
        gates.push_back(gate_to_json(gate));
    }

    json out;
    out["map"] = std::move(map_entries);
    out["arch"] = {
        {"width", graph.getMaxX() + 1},
        {"height", graph.getMaxY() + 1},
        {"alg_qubits", alg_qubits},
        {"magic_states", magic_states}
    };
    out["steps"] = std::move(steps);
    out["gates"] = std::move(gates);

    const std::filesystem::path parent = out_path.parent_path();
    if (!parent.empty()) {
        std::error_code ec;
        std::filesystem::create_directories(parent, ec);
        if (ec) {
            throw std::runtime_error(
                "Cannot create output directory " + parent.string() + ": " + ec.message()
            );
        }
    }

    std::ofstream stream(out_path);
    if (!stream) {
        throw std::runtime_error("Cannot open output file: " + out_path.string());
    }
    stream << out.dump(2) << "\n";
    if (!stream) {
        throw std::runtime_error("Failed to write output file: " + out_path.string());
    }
}
