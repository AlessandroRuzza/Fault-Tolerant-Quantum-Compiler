#pragma once

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <functional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include <unistd.h>

#include <nlohmann/json.hpp>

inline std::string expand_config_variants(const std::string &json_name, int process_count = 1) {
    using json = nlohmann::json;
    if (process_count <= 0) {
        throw std::invalid_argument("process_count must be > 0");
    }

    const auto make_signature = [](const json &entry) {
        json normalized = json::object();
        if (!entry.is_object()) {
            return std::string {};
        }

        const auto is_runtime_key = [](const std::string &key) {
            // Runtime-only fields must not affect identity of a benchmark case.
            return key == "id" ||
                   key == "executed" ||
                   key == "process" ||
                   key == "timeout" ||
                   key == "timeout_reached";
        };

        // First pass: copy non-runtime, non-object fields as-is.
        for (auto it = entry.begin(); it != entry.end(); ++it) {
            if (is_runtime_key(it.key())) {
                continue;
            }
            if (!it.value().is_object()) {
                normalized[it.key()] = it.value();
            }
        }

        // Compatibility pass: flatten object-valued fields.
        // This keeps identity stable across:
        // - old expansion format that stored object-list entries under a key
        // - new format that merges those object fields at top-level
        for (auto it = entry.begin(); it != entry.end(); ++it) {
            if (is_runtime_key(it.key()) || !it.value().is_object()) {
                continue;
            }
            for (auto nested = it.value().begin(); nested != it.value().end(); ++nested) {
                if (is_runtime_key(nested.key())) {
                    continue;
                }
                normalized[nested.key()] = nested.value();
            }
        }
        return normalized.dump();
    };

#ifdef PROJECT_ROOT
    const std::filesystem::path project_root = PROJECT_ROOT;
#else
    const std::filesystem::path project_root = std::filesystem::current_path();
#endif

    const std::filesystem::path config_dir = project_root / "config";
    const std::filesystem::path executed_dir = config_dir / "executed";
    std::filesystem::create_directories(executed_dir);
    const std::filesystem::path input_path = config_dir / (json_name + ".json");
    const std::filesystem::path output_path = executed_dir / (json_name + "_expanded.json");

    std::ifstream input_stream(input_path);
    if (!input_stream.is_open()) {
        throw std::runtime_error("Cannot open input file: " + input_path.string());
    }

    json source;
    input_stream >> source;

    const auto is_runtime_key = [](const std::string &key) {
        return key == "id" || key == "executed" || key == "process";
    };

    std::function<void(const json &, const std::function<void(const json &)> &)> expand_entry_variants;
    expand_entry_variants = [&](const json &entry, const std::function<void(const json &)> &sink) -> void {
        if (!entry.is_object()) {
            throw std::invalid_argument("Each benchmark entry must be a JSON object.");
        }

        // Support lists of JSON objects inside the main config object.
        // Example:
        // {
        //   "timeout": 10,
        //   "cases": [ {"circuit":"a"}, {"circuit":"b"} ]
        // }
        // The key containing the list ("cases" here) is treated as expansion-only
        // and is not copied to generated entries.
        for (auto it = entry.begin(); it != entry.end(); ++it) {
            const std::string key = it.key();
            if (is_runtime_key(key) || !it.value().is_array()) {
                continue;
            }
            if (it.value().empty()) {
                throw std::invalid_argument("Field '" + key + "' cannot be an empty list.");
            }

            bool all_objects = true;
            for (const auto &candidate : it.value()) {
                if (!candidate.is_object()) {
                    all_objects = false;
                    break;
                }
            }
            if (!all_objects) {
                continue;
            }

            json base_entry = entry;
            base_entry.erase(key);
            for (const auto &obj_override : it.value()) {
                json merged_entry = base_entry;
                for (auto override_it = obj_override.begin(); override_it != obj_override.end(); ++override_it) {
                    merged_entry[override_it.key()] = override_it.value();
                }
                expand_entry_variants(merged_entry, sink);
            }
            return;
        }

        std::vector<std::string> keys;
        std::vector<std::vector<json>> values_per_key;
        for (auto it = entry.begin(); it != entry.end(); ++it) {
            const std::string key = it.key();
            if (is_runtime_key(key)) {
                continue;
            }

            if (it.value().is_array()) {
                if (it.value().empty()) {
                    throw std::invalid_argument("Field '" + key + "' cannot be an empty list.");
                }

                std::vector<json> values;
                values.reserve(it.value().size());
                for (const auto &value : it.value()) {
                    values.push_back(value);
                }
                values_per_key.push_back(std::move(values));
            } else {
                values_per_key.push_back({it.value()});
            }

            keys.push_back(key);
        }

        json current = json::object();
        std::function<void(std::size_t)> build = [&](std::size_t idx) {
            if (idx == keys.size()) {
                sink(current);
                return;
            }

            const std::string &key = keys[idx];
            for (const auto &value : values_per_key[idx]) {
                current[key] = value;
                build(idx + 1);
            }
        };

        build(0);
    };

    // Existing per-case state (id / executed / timeout_reached) is preserved
    // across runs so resuming a partially-executed sweep keeps stable ids and
    // skip flags. Only this lightweight state is kept in the map; the full
    // existing DOM is read inside a scoped block so it frees before generation,
    // keeping peak memory to a single copy of the expanded structure.
    struct ExistingState {
        int id = 0;
        bool has_id = false;
        bool executed = false;
        bool has_executed = false;
        bool timeout_reached = false;
        bool has_timeout = false;
    };
    std::unordered_map<std::string, ExistingState> existing_by_signature;
    std::size_t next_id = 1;

    if (std::filesystem::exists(output_path)) {
        std::ifstream existing_stream(output_path);
        if (existing_stream.is_open()) {
            json existing_data;
            try {
                existing_stream >> existing_data;
                if (existing_data.is_array()) {
                    for (const auto &existing_entry : existing_data) {
                        if (!existing_entry.is_object()) {
                            continue;
                        }
                        const std::string signature = make_signature(existing_entry);
                        if (signature.empty()) {
                            continue;
                        }
                        ExistingState state;
                        if (existing_entry.contains("id") && existing_entry["id"].is_number_integer()) {
                            state.id = existing_entry["id"].get<int>();
                            state.has_id = true;
                            if (state.id >= 1) {
                                next_id = std::max(next_id, static_cast<std::size_t>(state.id + 1));
                            }
                        }
                        if (existing_entry.contains("executed") && existing_entry["executed"].is_boolean()) {
                            state.executed = existing_entry["executed"].get<bool>();
                            state.has_executed = true;
                        }
                        if (existing_entry.contains("timeout_reached") && existing_entry["timeout_reached"].is_boolean()) {
                            state.timeout_reached = existing_entry["timeout_reached"].get<bool>();
                            state.has_timeout = true;
                        }
                        existing_by_signature[signature] = state;
                    }
                }
            } catch (const std::exception &) {
            }
        }
    }

    // Stream each expanded entry straight to disk so the full set of generated
    // entries is never held in memory at once. Write to a temp file and rename
    // so an interrupted expansion never leaves a truncated output behind. The
    // temp name carries the PID so that several processes regenerating the same
    // benchmark at once (one per --processor) each rename their own file instead
    // of racing on a shared "<name>.tmp" (the loser used to fail with "cannot
    // rename: No such file or directory"). The final rename is atomic, so the
    // shared output ends up as one complete, identical expansion.
    const std::filesystem::path tmp_path =
        output_path.string() + ".tmp." + std::to_string(static_cast<long long>(::getpid()));
    std::ofstream output_stream(tmp_path, std::ios::trunc);
    if (!output_stream.is_open()) {
        throw std::runtime_error("Cannot open output file: " + tmp_path.string());
    }

    output_stream << "[";
    std::size_t generated_index = 0;
    bool first_entry = true;
    const std::function<void(const json &)> sink = [&](const json &generated_entry) {
        json final_entry = generated_entry;
        const std::string signature = make_signature(generated_entry);

        auto it = existing_by_signature.find(signature);
        if (it != existing_by_signature.end()) {
            const ExistingState &state = it->second;
            final_entry["id"] = state.has_id ? state.id : static_cast<int>(next_id++);
            final_entry["executed"] = state.has_executed ? state.executed : false;
            if (state.has_timeout) {
                final_entry["timeout_reached"] = state.timeout_reached;
            } else if (!final_entry.contains("timeout_reached")) {
                final_entry["timeout_reached"] = false;
            }
        } else {
            final_entry["id"] = static_cast<int>(next_id++);
            final_entry["executed"] = false;
            if (!final_entry.contains("timeout_reached")) {
                final_entry["timeout_reached"] = false;
            }
        }

        final_entry["process"] = static_cast<int>(generated_index % static_cast<std::size_t>(process_count));
        ++generated_index;

        output_stream << (first_entry ? "\n" : ",\n");
        first_entry = false;
        output_stream << final_entry.dump(2);
    };

    if (source.is_object()) {
        expand_entry_variants(source, sink);
    } else if (source.is_array()) {
        for (const auto &entry : source) {
            expand_entry_variants(entry, sink);
        }
    } else {
        throw std::invalid_argument("Input JSON must be an object or an array of objects.");
    }

    output_stream << "\n]\n";
    output_stream.close();
    if (!output_stream) {
        throw std::runtime_error("Failed while writing output file: " + tmp_path.string());
    }

    std::filesystem::rename(tmp_path, output_path);
    return output_path.string();
}
