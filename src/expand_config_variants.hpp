#pragma once

#include <filesystem>
#include <fstream>
#include <functional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <nlohmann/json.hpp>

inline std::string expand_config_variants(const std::string &json_name) {
    using json = nlohmann::json;

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

    json expanded = json::array();
    json current = json::object();
    std::size_t next_id = 1;

    std::function<void(std::size_t)> build = [&](std::size_t idx) {
        if (idx == keys.size()) {
            current["id"] = next_id++;
            current["executed"] = false;
            expanded.push_back(current);
            return;
        }

        const std::string &key = keys[idx];
        for (const auto &value : values_per_key[idx]) {
            current[key] = value;
            build(idx + 1);
        }
    };

    build(0);

    std::ofstream output_stream(output_path);
    if (!output_stream.is_open()) {
        throw std::runtime_error("Cannot open output file: " + output_path.string());
    }

    output_stream << expanded.dump(2) << '\n';
    return output_path.string();
}
