#pragma once

#include <filesystem>
#include <fstream>
#include <functional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include <nlohmann/json.hpp>

inline std::string expand_config_variants(const std::string &json_name) {
    using json = nlohmann::json;
    const auto make_signature = [](const json &entry) {
        json normalized = json::object();
        if (!entry.is_object()) {
            return std::string {};
        }
        for (auto it = entry.begin(); it != entry.end(); ++it) {
            // Runtime-only fields must not affect identity of a benchmark case.
            if (it.key() == "id" ||
                it.key() == "executed" ||
                it.key() == "timeout" ||
                it.key() == "timeout_reached") {
                continue;
            }
            normalized[it.key()] = it.value();
        }
        return normalized.dump();
    };

#ifdef PROJECT_ROOT
    const std::filesystem::path project_root = PROJECT_ROOT;
#else
    const std::filesystem::path project_root = std::filesystem::current_path();
#endif

    const std::filesystem::path config_dir = project_root / "config";
    const std::filesystem::path input_path = config_dir / (json_name + ".json");
    const std::filesystem::path output_path = config_dir / (json_name + "_expanded.json");

    std::ifstream input_stream(input_path);
    if (!input_stream.is_open()) {
        throw std::runtime_error("Cannot open input file: " + input_path.string());
    }

    json source;
    input_stream >> source;

    if (!source.is_object()) {
        throw std::invalid_argument("Input JSON must be an object.");
    }

    std::vector<std::string> keys;
    std::vector<std::vector<json>> values_per_key;

    for (auto it = source.begin(); it != source.end(); ++it) {
        const std::string key = it.key();
        if (key == "id" || key == "executed") {
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

    json generated = json::array();
    json current = json::object();

    std::function<void(std::size_t)> build = [&](std::size_t idx) {
        if (idx == keys.size()) {
            generated.push_back(current);
            return;
        }

        const std::string &key = keys[idx];
        for (const auto &value : values_per_key[idx]) {
            current[key] = value;
            build(idx + 1);
        }
    };

    build(0);

    std::unordered_map<std::string, json> existing_by_signature;
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

                        existing_by_signature[signature] = existing_entry;

                        if (existing_entry.contains("id") && existing_entry["id"].is_number_integer()) {
                            const int id_value = existing_entry["id"].get<int>();
                            if (id_value >= 1) {
                                next_id = std::max(next_id, static_cast<std::size_t>(id_value + 1));
                            }
                        }
                    }
                }
            } catch (const std::exception &) {
            }
        }
    }

    json expanded = json::array();
    for (const auto &generated_entry : generated) {
        json final_entry = generated_entry;
        const std::string signature = make_signature(generated_entry);

        auto it = existing_by_signature.find(signature);
        if (it != existing_by_signature.end()) {
            const json &existing_entry = it->second;
            if (existing_entry.contains("id") && existing_entry["id"].is_number_integer()) {
                final_entry["id"] = existing_entry["id"].get<int>();
            } else {
                final_entry["id"] = static_cast<int>(next_id++);
            }
            if (existing_entry.contains("executed") && existing_entry["executed"].is_boolean()) {
                final_entry["executed"] = existing_entry["executed"].get<bool>();
            } else {
                final_entry["executed"] = false;
            }

            if (existing_entry.contains("timeout_reached") && existing_entry["timeout_reached"].is_boolean()) {
                final_entry["timeout_reached"] = existing_entry["timeout_reached"].get<bool>();
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

        expanded.push_back(final_entry);
    }

    std::ofstream output_stream(output_path);
    if (!output_stream.is_open()) {
        throw std::runtime_error("Cannot open output file: " + output_path.string());
    }

    output_stream << expanded.dump(2) << '\n';
    return output_path.string();
}
