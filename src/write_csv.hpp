#pragma once

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace write_csv {

inline constexpr const char *kBenchmarkRunsCsvHeader =
    "run_id,run_date,run_datetime,benchmark_suite,chart_group,case_id,circuit,graph_x,graph_y,"
    "graph_dimensions,circuit_graph_label,mapping_type,magic_aware_strategy,gaussian_strategy,"
    "safe_passage_strategy,magic_state_placement_strategy,border_distance_percentage,"
    "number_of_magic_states,routing_steps,timeout_reached,status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kLegacyBenchmarkRunsCsvHeader =
    "run_id,run_date,run_datetime,benchmark_suite,chart_group,case_id,circuit,graph_x,graph_y,"
    "graph_dimensions,circuit_graph_label,mapping_type,magic_aware_strategy,gaussian_strategy,"
    "safe_passage_strategy,magic_state_placement_strategy,border_distance_percentage,"
    "number_of_magic_states,routing_steps,status,exit_code,duration_seconds,log_file,error_excerpt";

inline std::string escape(const std::string &value) {
    bool must_quote = false;
    for (char c : value) {
        if (c == ',' || c == '"' || c == '\n' || c == '\r') {
            must_quote = true;
            break;
        }
    }
    if (!must_quote) {
        return value;
    }

    std::string out;
    out.reserve(value.size() + 8);
    out.push_back('"');
    for (char c : value) {
        if (c == '"') {
            out.push_back('"');
        }
        out.push_back(c);
    }
    out.push_back('"');
    return out;
}

inline void append_row(const std::filesystem::path &csv_path, const std::vector<std::string> &columns) {
    std::ofstream out(csv_path, std::ios::app);
    if (!out.is_open()) {
        throw std::runtime_error("Cannot append CSV row: " + csv_path.string());
    }

    for (std::size_t i = 0; i < columns.size(); ++i) {
        if (i != 0) {
            out << ',';
        }
        out << escape(columns[i]);
    }
    out << '\n';
}

inline void ensure_initialized(const std::filesystem::path &csv_path, const std::string &header) {
    if (!std::filesystem::exists(csv_path)) {
        std::ofstream out(csv_path);
        if (!out.is_open()) {
            throw std::runtime_error("Cannot create CSV file: " + csv_path.string());
        }
        out << header << '\n';
        return;
    }

    if (std::filesystem::is_regular_file(csv_path) && std::filesystem::file_size(csv_path) == 0) {
        std::ofstream out(csv_path, std::ios::app);
        out << header << '\n';
        return;
    }

    std::ifstream in(csv_path);
    if (!in.is_open()) {
        return;
    }

    std::string first_line;
    if (!std::getline(in, first_line)) {
        return;
    }

    if (first_line == header) {
        return;
    }

    if (header == kBenchmarkRunsCsvHeader && first_line == kLegacyBenchmarkRunsCsvHeader) {
        std::vector<std::string> rows;
        std::string line;
        while (std::getline(in, line)) {
            if (!line.empty()) {
                rows.push_back(line);
            }
        }

        std::ofstream out(csv_path, std::ios::trunc);
        if (!out.is_open()) {
            throw std::runtime_error("Cannot migrate CSV file: " + csv_path.string());
        }

        out << header << '\n';
        for (const std::string &row : rows) {
            out << row << ",false\n";
        }
    }
}

inline int read_max_run_id(const std::filesystem::path &csv_path) {
    if (!std::filesystem::exists(csv_path)) {
        return 0;
    }

    std::ifstream in(csv_path);
    if (!in.is_open()) {
        return 0;
    }

    std::string line;
    int max_run_id = 0;
    bool first_line = true;
    while (std::getline(in, line)) {
        if (line.empty()) {
            continue;
        }
        if (first_line) {
            first_line = false;
            if (line.rfind("run_id,", 0) == 0) {
                continue;
            }
        }

        const std::size_t comma_pos = line.find(',');
        const std::string run_id_token = (comma_pos == std::string::npos) ? line : line.substr(0, comma_pos);
        try {
            max_run_id = std::max(max_run_id, std::stoi(run_id_token));
        } catch (const std::exception &) {
        }
    }
    return max_run_id;
}

} // namespace write_csv
