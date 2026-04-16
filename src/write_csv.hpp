#pragma once

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace write_csv {

inline constexpr const char *kBenchmarkRunsCsvHeader =
    "run_id,run_date,run_datetime,circuit,graph_x,graph_y,circuit_graph_label,mapping_type,"
    "magic_aware_strategy,gaussian_strategy,safe_passage_strategy,magic_state_placement_strategy,"
    "border_distance_percentage,number_of_magic_states,routing_strategy,routing_steps,timeout_reached,"
    "status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kPreviousBenchmarkRunsCsvHeader =
    "run_id,run_date,run_datetime,benchmark_suite,chart_group,case_id,circuit,graph_x,graph_y,"
    "graph_dimensions,circuit_graph_label,mapping_type,magic_aware_strategy,gaussian_strategy,"
    "safe_passage_strategy,magic_state_placement_strategy,border_distance_percentage,"
    "number_of_magic_states,routing_steps,timeout_reached,status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kLegacyBenchmarkRunsCsvHeader =
    "run_id,run_date,run_datetime,benchmark_suite,chart_group,case_id,circuit,graph_x,graph_y,"
    "graph_dimensions,circuit_graph_label,mapping_type,magic_aware_strategy,gaussian_strategy,"
    "safe_passage_strategy,magic_state_placement_strategy,border_distance_percentage,"
    "number_of_magic_states,routing_steps,status,exit_code,duration_seconds,log_file,error_excerpt";

inline std::vector<std::string> parse_row(const std::string &line) {
    std::vector<std::string> out;
    std::string current;
    bool in_quotes = false;

    for (std::size_t i = 0; i < line.size(); ++i) {
        const char c = line[i];
        if (in_quotes) {
            if (c == '"') {
                if (i + 1 < line.size() && line[i + 1] == '"') {
                    current.push_back('"');
                    ++i;
                } else {
                    in_quotes = false;
                }
            } else {
                current.push_back(c);
            }
        } else {
            if (c == ',') {
                out.push_back(current);
                current.clear();
            } else if (c == '"') {
                in_quotes = true;
            } else {
                current.push_back(c);
            }
        }
    }
    out.push_back(current);
    return out;
}

inline std::string at_or_empty(const std::vector<std::string> &row, std::size_t idx) {
    return idx < row.size() ? row[idx] : "";
}

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

    if (header == kBenchmarkRunsCsvHeader &&
        (first_line == kPreviousBenchmarkRunsCsvHeader || first_line == kLegacyBenchmarkRunsCsvHeader)) {
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
            const std::vector<std::string> parsed = parse_row(row);
            const bool from_legacy = (first_line == kLegacyBenchmarkRunsCsvHeader);
            const std::vector<std::string> migrated = {
                at_or_empty(parsed, 0),   // run_id
                at_or_empty(parsed, 1),   // run_date
                at_or_empty(parsed, 2),   // run_datetime
                at_or_empty(parsed, 6),   // circuit
                at_or_empty(parsed, 7),   // graph_x
                at_or_empty(parsed, 8),   // graph_y
                at_or_empty(parsed, 10),  // circuit_graph_label
                at_or_empty(parsed, 11),  // mapping_type
                at_or_empty(parsed, 12),  // magic_aware_strategy
                at_or_empty(parsed, 13),  // gaussian_strategy
                at_or_empty(parsed, 14),  // safe_passage_strategy
                at_or_empty(parsed, 15),  // magic_state_placement_strategy
                at_or_empty(parsed, 16),  // border_distance_percentage
                at_or_empty(parsed, 17),  // number_of_magic_states
                "",                       // routing_strategy (not available in old rows)
                at_or_empty(parsed, 18),  // routing_steps
                from_legacy ? "false" : at_or_empty(parsed, 19), // timeout_reached
                from_legacy ? at_or_empty(parsed, 19) : at_or_empty(parsed, 20), // status
                from_legacy ? at_or_empty(parsed, 20) : at_or_empty(parsed, 21), // exit_code
                from_legacy ? at_or_empty(parsed, 21) : at_or_empty(parsed, 22), // duration_seconds
                from_legacy ? at_or_empty(parsed, 22) : at_or_empty(parsed, 23), // log_file
                from_legacy ? at_or_empty(parsed, 23) : at_or_empty(parsed, 24)  // error_excerpt
            };

            for (std::size_t i = 0; i < migrated.size(); ++i) {
                if (i != 0) {
                    out << ',';
                }
                out << escape(migrated[i]);
            }
            out << '\n';
        }
        return;
    }

    throw std::runtime_error(
        "CSV header mismatch for " + csv_path.string() +
        ". Expected: " + header + " ; Found: " + first_line
    );
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
