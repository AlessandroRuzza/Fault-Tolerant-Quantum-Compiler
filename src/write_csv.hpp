#pragma once

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace write_csv {

inline constexpr const char *kBenchmarkRunsCsvHeader =
    "id,run_date,run_datetime,circuit,graph_x,graph_y,circuit_graph_label,mapping_type,"
    "magic_aware_strategy,gaussian_strategy,magic_high,magic_low,cnot_high,cnot_low,"
    "mapped_gaussian_weight,base_gaussian_weight,size_moltiplier,gaussian_confidence,"
    "safe_passage_strategy,magic_state_placement_strategy,"
    "border_distance_percentage,number_of_magic_states,routing_strategy,t_routing_mode,routing_steps,timeout_reached,"
    "status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kBenchmarkRunsCsvHeaderV6 =
    "run_id,run_date,run_datetime,circuit,graph_x,graph_y,circuit_graph_label,mapping_type,"
    "magic_aware_strategy,gaussian_strategy,magic_high,magic_low,cnot_high,cnot_low,"
    "mapped_gaussian_weight,base_gaussian_weight,size_moltiplier,gaussian_confidence,"
    "safe_passage_strategy,magic_state_placement_strategy,"
    "border_distance_percentage,number_of_magic_states,routing_strategy,t_routing_mode,routing_steps,timeout_reached,"
    "status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kBenchmarkRunsCsvHeaderV5 =
    "run_id,run_date,run_datetime,circuit,graph_x,graph_y,circuit_graph_label,mapping_type,"
    "magic_aware_strategy,gaussian_strategy,magic_high,magic_low,cnot_high,cnot_low,"
    "mapped_gaussian_weight,base_gaussian_weight,size_moltiplier,"
    "safe_passage_strategy,magic_state_placement_strategy,"
    "border_distance_percentage,number_of_magic_states,routing_strategy,t_routing_mode,routing_steps,timeout_reached,"
    "status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kBenchmarkRunsCsvHeaderV4 =
    "run_id,run_date,run_datetime,circuit,graph_x,graph_y,circuit_graph_label,mapping_type,"
    "magic_aware_strategy,gaussian_strategy,magic_high,magic_low,cnot_high,cnot_low,"
    "mapped_gaussian_weight,base_gaussian_weight,"
    "safe_passage_strategy,magic_state_placement_strategy,"
    "border_distance_percentage,number_of_magic_states,routing_strategy,t_routing_mode,routing_steps,timeout_reached,"
    "status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kBenchmarkRunsCsvHeaderV3 =
    "run_id,run_date,run_datetime,circuit,graph_x,graph_y,circuit_graph_label,mapping_type,"
    "magic_aware_strategy,gaussian_strategy,magic_high,magic_low,cnot_high,cnot_low,"
    "mapped_gaussian_weight,base_gaussian_weight,"
    "safe_passage_strategy,magic_state_placement_strategy,"
    "border_distance_percentage,number_of_magic_states,routing_strategy,routing_steps,timeout_reached,"
    "status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kBenchmarkRunsCsvHeaderV2 =
    "run_id,run_date,run_datetime,circuit,graph_x,graph_y,circuit_graph_label,mapping_type,"
    "magic_aware_strategy,gaussian_strategy,mapped_gaussian_weight,base_gaussian_weight,"
    "safe_passage_strategy,magic_state_placement_strategy,"
    "border_distance_percentage,number_of_magic_states,routing_strategy,routing_steps,timeout_reached,"
    "status,exit_code,duration_seconds,log_file,error_excerpt";

inline constexpr const char *kBenchmarkRunsCsvHeaderV1 =
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

inline std::string render_row(const std::vector<std::string> &columns) {
    std::string row;
    for (std::size_t i = 0; i < columns.size(); ++i) {
        if (i != 0) {
            row.push_back(',');
        }
        row += escape(columns[i]);
    }
    return row;
}

inline std::string config_id_from_log_file(const std::string &log_file, const std::string &fallback) {
    const std::string filename = std::filesystem::path(log_file).filename().string();
    const std::string prefix = "run_";
    const std::string suffix = ".log";

    if (filename.rfind(prefix, 0) != 0 ||
        filename.size() <= prefix.size() + suffix.size() ||
        filename.substr(filename.size() - suffix.size()) != suffix) {
        return fallback;
    }

    const std::string body = filename.substr(prefix.size(), filename.size() - prefix.size() - suffix.size());
    const std::size_t separator = body.find('_');
    if (separator == std::string::npos || separator + 1 >= body.size()) {
        return fallback;
    }

    return body.substr(separator + 1);
}

inline int execution_id_from_log_file(const std::string &log_file, int fallback) {
    const std::string filename = std::filesystem::path(log_file).filename().string();
    const std::string prefix = "run_";
    const std::string suffix = ".log";

    if (filename.rfind(prefix, 0) != 0 ||
        filename.size() <= prefix.size() + suffix.size() ||
        filename.substr(filename.size() - suffix.size()) != suffix) {
        return fallback;
    }

    const std::string body = filename.substr(prefix.size(), filename.size() - prefix.size() - suffix.size());
    const std::size_t separator = body.find('_');
    const std::string token = separator == std::string::npos ? body : body.substr(0, separator);
    if (token.empty()) {
        return fallback;
    }

    try {
        std::size_t consumed = 0;
        const int value = std::stoi(token, &consumed);
        return consumed == token.size() ? value : fallback;
    } catch (const std::exception &) {
        return fallback;
    }
}

inline void append_row(const std::filesystem::path &csv_path, const std::vector<std::string> &columns) {
    std::ofstream out(csv_path, std::ios::app);
    if (!out.is_open()) {
        throw std::runtime_error("Cannot append CSV row: " + csv_path.string());
    }

    out << render_row(columns) << '\n';
}

inline void replace_row(
    const std::filesystem::path &csv_path,
    std::size_t data_row_index,
    const std::vector<std::string> &columns
) {
    std::ifstream in(csv_path);
    if (!in.is_open()) {
        throw std::runtime_error("Cannot read CSV rows for replacement: " + csv_path.string());
    }

    std::string header;
    if (!std::getline(in, header)) {
        throw std::runtime_error("Cannot replace CSV row in empty file: " + csv_path.string());
    }

    std::vector<std::string> rows;
    std::string line;
    while (std::getline(in, line)) {
        if (!line.empty()) {
            rows.push_back(line);
        }
    }

    if (data_row_index >= rows.size()) {
        throw std::runtime_error("CSV replacement row index out of range: " + csv_path.string());
    }

    rows[data_row_index] = render_row(columns);

    std::ofstream out(csv_path, std::ios::trunc);
    if (!out.is_open()) {
        throw std::runtime_error("Cannot rewrite CSV rows after replacement: " + csv_path.string());
    }

    out << header << '\n';
    for (const std::string &row : rows) {
        out << row << '\n';
    }
}

inline std::vector<std::vector<std::string>> read_data_rows(const std::filesystem::path &csv_path) {
    std::vector<std::vector<std::string>> rows;
    if (!std::filesystem::exists(csv_path)) {
        return rows;
    }

    std::ifstream in(csv_path);
    if (!in.is_open()) {
        return rows;
    }

    std::string line;
    bool first_line = true;
    while (std::getline(in, line)) {
        if (line.empty()) {
            continue;
        }
        if (first_line) {
            first_line = false;
            if (line.rfind("run_id,", 0) == 0 || line.rfind("id,", 0) == 0) {
                continue;
            }
        }
        rows.push_back(parse_row(line));
    }
    return rows;
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
        (first_line == kBenchmarkRunsCsvHeaderV6 ||
         first_line == kBenchmarkRunsCsvHeaderV5 ||
         first_line == kBenchmarkRunsCsvHeaderV4 ||
         first_line == kBenchmarkRunsCsvHeaderV3 ||
         first_line == kBenchmarkRunsCsvHeaderV2 ||
         first_line == kBenchmarkRunsCsvHeaderV1 ||
         first_line == kPreviousBenchmarkRunsCsvHeader ||
         first_line == kLegacyBenchmarkRunsCsvHeader)) {
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
            const bool from_v6 = (first_line == kBenchmarkRunsCsvHeaderV6);
            const bool from_v5 = (first_line == kBenchmarkRunsCsvHeaderV5);
            const bool from_v4 = (first_line == kBenchmarkRunsCsvHeaderV4);
            const bool from_v3 = (first_line == kBenchmarkRunsCsvHeaderV3);
            const bool from_v2 = (first_line == kBenchmarkRunsCsvHeaderV2);
            const bool from_v1 = (first_line == kBenchmarkRunsCsvHeaderV1);
            const bool from_legacy = (first_line == kLegacyBenchmarkRunsCsvHeader);

            std::vector<std::string> migrated;
            if (from_v6) {
                migrated = {
                    config_id_from_log_file(at_or_empty(parsed, 29), at_or_empty(parsed, 0)), // id
                    at_or_empty(parsed, 1),   // run_date
                    at_or_empty(parsed, 2),   // run_datetime
                    at_or_empty(parsed, 3),   // circuit
                    at_or_empty(parsed, 4),   // graph_x
                    at_or_empty(parsed, 5),   // graph_y
                    at_or_empty(parsed, 6),   // circuit_graph_label
                    at_or_empty(parsed, 7),   // mapping_type
                    at_or_empty(parsed, 8),   // magic_aware_strategy
                    at_or_empty(parsed, 9),   // gaussian_strategy
                    at_or_empty(parsed, 10),  // magic_high
                    at_or_empty(parsed, 11),  // magic_low
                    at_or_empty(parsed, 12),  // cnot_high
                    at_or_empty(parsed, 13),  // cnot_low
                    at_or_empty(parsed, 14),  // mapped_gaussian_weight
                    at_or_empty(parsed, 15),  // base_gaussian_weight
                    at_or_empty(parsed, 16),  // size_moltiplier
                    at_or_empty(parsed, 17),  // gaussian_confidence
                    at_or_empty(parsed, 18),  // safe_passage_strategy
                    at_or_empty(parsed, 19),  // magic_state_placement_strategy
                    at_or_empty(parsed, 20),  // border_distance_percentage
                    at_or_empty(parsed, 21),  // number_of_magic_states
                    at_or_empty(parsed, 22),  // routing_strategy
                    at_or_empty(parsed, 23),  // t_routing_mode
                    at_or_empty(parsed, 24),  // routing_steps
                    at_or_empty(parsed, 25),  // timeout_reached
                    at_or_empty(parsed, 26),  // status
                    at_or_empty(parsed, 27),  // exit_code
                    at_or_empty(parsed, 28),  // duration_seconds
                    at_or_empty(parsed, 29),  // log_file
                    at_or_empty(parsed, 30)   // error_excerpt
                };
            } else if (from_v5) {
                migrated = {
                    at_or_empty(parsed, 0),   // id
                    at_or_empty(parsed, 1),   // run_date
                    at_or_empty(parsed, 2),   // run_datetime
                    at_or_empty(parsed, 3),   // circuit
                    at_or_empty(parsed, 4),   // graph_x
                    at_or_empty(parsed, 5),   // graph_y
                    at_or_empty(parsed, 6),   // circuit_graph_label
                    at_or_empty(parsed, 7),   // mapping_type
                    at_or_empty(parsed, 8),   // magic_aware_strategy
                    at_or_empty(parsed, 9),   // gaussian_strategy
                    at_or_empty(parsed, 10),  // magic_high
                    at_or_empty(parsed, 11),  // magic_low
                    at_or_empty(parsed, 12),  // cnot_high
                    at_or_empty(parsed, 13),  // cnot_low
                    at_or_empty(parsed, 14),  // mapped_gaussian_weight
                    at_or_empty(parsed, 15),  // base_gaussian_weight
                    at_or_empty(parsed, 16),  // size_moltiplier
                    "",                       // gaussian_confidence
                    at_or_empty(parsed, 17),  // safe_passage_strategy
                    at_or_empty(parsed, 18),  // magic_state_placement_strategy
                    at_or_empty(parsed, 19),  // border_distance_percentage
                    at_or_empty(parsed, 20),  // number_of_magic_states
                    at_or_empty(parsed, 21),  // routing_strategy
                    at_or_empty(parsed, 22),  // t_routing_mode
                    at_or_empty(parsed, 23),  // routing_steps
                    at_or_empty(parsed, 24),  // timeout_reached
                    at_or_empty(parsed, 25),  // status
                    at_or_empty(parsed, 26),  // exit_code
                    at_or_empty(parsed, 27),  // duration_seconds
                    at_or_empty(parsed, 28),  // log_file
                    at_or_empty(parsed, 29)   // error_excerpt
                };
            } else if (from_v4) {
                migrated = {
                    at_or_empty(parsed, 0),   // id
                    at_or_empty(parsed, 1),   // run_date
                    at_or_empty(parsed, 2),   // run_datetime
                    at_or_empty(parsed, 3),   // circuit
                    at_or_empty(parsed, 4),   // graph_x
                    at_or_empty(parsed, 5),   // graph_y
                    at_or_empty(parsed, 6),   // circuit_graph_label
                    at_or_empty(parsed, 7),   // mapping_type
                    at_or_empty(parsed, 8),   // magic_aware_strategy
                    at_or_empty(parsed, 9),   // gaussian_strategy
                    at_or_empty(parsed, 10),  // magic_high
                    at_or_empty(parsed, 11),  // magic_low
                    at_or_empty(parsed, 12),  // cnot_high
                    at_or_empty(parsed, 13),  // cnot_low
                    at_or_empty(parsed, 14),  // mapped_gaussian_weight
                    at_or_empty(parsed, 15),  // base_gaussian_weight
                    "",                       // size_moltiplier
                    "",                       // gaussian_confidence
                    at_or_empty(parsed, 16),  // safe_passage_strategy
                    at_or_empty(parsed, 17),  // magic_state_placement_strategy
                    at_or_empty(parsed, 18),  // border_distance_percentage
                    at_or_empty(parsed, 19),  // number_of_magic_states
                    at_or_empty(parsed, 20),  // routing_strategy
                    at_or_empty(parsed, 21),  // t_routing_mode
                    at_or_empty(parsed, 22),  // routing_steps
                    at_or_empty(parsed, 23),  // timeout_reached
                    at_or_empty(parsed, 24),  // status
                    at_or_empty(parsed, 25),  // exit_code
                    at_or_empty(parsed, 26),  // duration_seconds
                    at_or_empty(parsed, 27),  // log_file
                    at_or_empty(parsed, 28)   // error_excerpt
                };
            } else if (from_v3) {
                migrated = {
                    at_or_empty(parsed, 0),   // id
                    at_or_empty(parsed, 1),   // run_date
                    at_or_empty(parsed, 2),   // run_datetime
                    at_or_empty(parsed, 3),   // circuit
                    at_or_empty(parsed, 4),   // graph_x
                    at_or_empty(parsed, 5),   // graph_y
                    at_or_empty(parsed, 6),   // circuit_graph_label
                    at_or_empty(parsed, 7),   // mapping_type
                    at_or_empty(parsed, 8),   // magic_aware_strategy
                    at_or_empty(parsed, 9),   // gaussian_strategy
                    at_or_empty(parsed, 10),  // magic_high
                    at_or_empty(parsed, 11),  // magic_low
                    at_or_empty(parsed, 12),  // cnot_high
                    at_or_empty(parsed, 13),  // cnot_low
                    at_or_empty(parsed, 14),  // mapped_gaussian_weight
                    at_or_empty(parsed, 15),  // base_gaussian_weight
                    "",                       // size_moltiplier
                    "",                       // gaussian_confidence
                    at_or_empty(parsed, 16),  // safe_passage_strategy
                    at_or_empty(parsed, 17),  // magic_state_placement_strategy
                    at_or_empty(parsed, 18),  // border_distance_percentage
                    at_or_empty(parsed, 19),  // number_of_magic_states
                    at_or_empty(parsed, 20),  // routing_strategy
                    "",                       // t_routing_mode (not available in old rows)
                    at_or_empty(parsed, 21),  // routing_steps
                    at_or_empty(parsed, 22),  // timeout_reached
                    at_or_empty(parsed, 23),  // status
                    at_or_empty(parsed, 24),  // exit_code
                    at_or_empty(parsed, 25),  // duration_seconds
                    at_or_empty(parsed, 26),  // log_file
                    at_or_empty(parsed, 27)   // error_excerpt
                };
            } else if (from_v2) {
                migrated = {
                    at_or_empty(parsed, 0),   // id
                    at_or_empty(parsed, 1),   // run_date
                    at_or_empty(parsed, 2),   // run_datetime
                    at_or_empty(parsed, 3),   // circuit
                    at_or_empty(parsed, 4),   // graph_x
                    at_or_empty(parsed, 5),   // graph_y
                    at_or_empty(parsed, 6),   // circuit_graph_label
                    at_or_empty(parsed, 7),   // mapping_type
                    at_or_empty(parsed, 8),   // magic_aware_strategy
                    at_or_empty(parsed, 9),   // gaussian_strategy
                    "",                       // magic_high
                    "",                       // magic_low
                    "",                       // cnot_high
                    "",                       // cnot_low
                    at_or_empty(parsed, 10),  // mapped_gaussian_weight
                    at_or_empty(parsed, 11),  // base_gaussian_weight
                    "",                       // size_moltiplier
                    "",                       // gaussian_confidence
                    at_or_empty(parsed, 12),  // safe_passage_strategy
                    at_or_empty(parsed, 13),  // magic_state_placement_strategy
                    at_or_empty(parsed, 14),  // border_distance_percentage
                    at_or_empty(parsed, 15),  // number_of_magic_states
                    at_or_empty(parsed, 16),  // routing_strategy
                    "",                       // t_routing_mode (not available in old rows)
                    at_or_empty(parsed, 17),  // routing_steps
                    at_or_empty(parsed, 18),  // timeout_reached
                    at_or_empty(parsed, 19),  // status
                    at_or_empty(parsed, 20),  // exit_code
                    at_or_empty(parsed, 21),  // duration_seconds
                    at_or_empty(parsed, 22),  // log_file
                    at_or_empty(parsed, 23)   // error_excerpt
                };
            } else if (from_v1) {
                migrated = {
                    at_or_empty(parsed, 0),   // id
                    at_or_empty(parsed, 1),   // run_date
                    at_or_empty(parsed, 2),   // run_datetime
                    at_or_empty(parsed, 3),   // circuit
                    at_or_empty(parsed, 4),   // graph_x
                    at_or_empty(parsed, 5),   // graph_y
                    at_or_empty(parsed, 6),   // circuit_graph_label
                    at_or_empty(parsed, 7),   // mapping_type
                    at_or_empty(parsed, 8),   // magic_aware_strategy
                    at_or_empty(parsed, 9),   // gaussian_strategy
                    "",                       // magic_high
                    "",                       // magic_low
                    "",                       // cnot_high
                    "",                       // cnot_low
                    "",                       // mapped_gaussian_weight
                    "",                       // base_gaussian_weight
                    "",                       // size_moltiplier
                    "",                       // gaussian_confidence
                    at_or_empty(parsed, 10),  // safe_passage_strategy
                    at_or_empty(parsed, 11),  // magic_state_placement_strategy
                    at_or_empty(parsed, 12),  // border_distance_percentage
                    at_or_empty(parsed, 13),  // number_of_magic_states
                    at_or_empty(parsed, 14),  // routing_strategy
                    "",                       // t_routing_mode (not available in old rows)
                    at_or_empty(parsed, 15),  // routing_steps
                    at_or_empty(parsed, 16),  // timeout_reached
                    at_or_empty(parsed, 17),  // status
                    at_or_empty(parsed, 18),  // exit_code
                    at_or_empty(parsed, 19),  // duration_seconds
                    at_or_empty(parsed, 20),  // log_file
                    at_or_empty(parsed, 21)   // error_excerpt
                };
            } else {
                const std::string legacy_case_id = at_or_empty(parsed, 5);
                migrated = {
                    legacy_case_id.empty() ? at_or_empty(parsed, 0) : legacy_case_id, // id
                    at_or_empty(parsed, 1),   // run_date
                    at_or_empty(parsed, 2),   // run_datetime
                    at_or_empty(parsed, 6),   // circuit
                    at_or_empty(parsed, 7),   // graph_x
                    at_or_empty(parsed, 8),   // graph_y
                    at_or_empty(parsed, 10),  // circuit_graph_label
                    at_or_empty(parsed, 11),  // mapping_type
                    at_or_empty(parsed, 12),  // magic_aware_strategy
                    at_or_empty(parsed, 13),  // gaussian_strategy
                    "",                       // magic_high
                    "",                       // magic_low
                    "",                       // cnot_high
                    "",                       // cnot_low
                    "",                       // mapped_gaussian_weight
                    "",                       // base_gaussian_weight
                    "",                       // size_moltiplier
                    "",                       // gaussian_confidence
                    at_or_empty(parsed, 14),  // safe_passage_strategy
                    at_or_empty(parsed, 15),  // magic_state_placement_strategy
                    at_or_empty(parsed, 16),  // border_distance_percentage
                    at_or_empty(parsed, 17),  // number_of_magic_states
                    "",                       // routing_strategy (not available in old rows)
                    "",                       // t_routing_mode (not available in old rows)
                    at_or_empty(parsed, 18),  // routing_steps
                    from_legacy ? "false" : at_or_empty(parsed, 19), // timeout_reached
                    from_legacy ? at_or_empty(parsed, 19) : at_or_empty(parsed, 20), // status
                    from_legacy ? at_or_empty(parsed, 20) : at_or_empty(parsed, 21), // exit_code
                    from_legacy ? at_or_empty(parsed, 21) : at_or_empty(parsed, 22), // duration_seconds
                    from_legacy ? at_or_empty(parsed, 22) : at_or_empty(parsed, 23), // log_file
                    from_legacy ? at_or_empty(parsed, 23) : at_or_empty(parsed, 24)  // error_excerpt
                };
            }

            if (!migrated.empty()) {
                migrated[0] = config_id_from_log_file(at_or_empty(migrated, 29), migrated[0]);
            }

            out << render_row(migrated) << '\n';
        }
        return;
    }

    throw std::runtime_error(
        "CSV header mismatch for " + csv_path.string() +
        ". Expected: " + header + " ; Found: " + first_line
    );
}

inline int read_max_execution_id(const std::filesystem::path &csv_path) {
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
            if (line.rfind("run_id,", 0) == 0 || line.rfind("id,", 0) == 0) {
                continue;
            }
        }

        const std::vector<std::string> parsed = parse_row(line);
        const std::string run_id_token = at_or_empty(parsed, 0);
        int fallback_id = 0;
        try {
            fallback_id = std::stoi(run_id_token);
        } catch (const std::exception &) {
        }
        max_run_id = std::max(
            max_run_id,
            execution_id_from_log_file(at_or_empty(parsed, 29), fallback_id)
        );
    }
    return max_run_id;
}

inline int read_max_run_id(const std::filesystem::path &csv_path) {
    return read_max_execution_id(csv_path);
}

} // namespace write_csv
