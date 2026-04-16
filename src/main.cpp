#include "one_execution.hpp"
#include "expand_config_variants.hpp"
#include "helpers.hpp"
#include "parsing.hpp"
#include "write_csv.hpp"

#include <algorithm>
#include <chrono>
#include <cctype>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <unordered_set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include <sys/wait.h>


int run_bench_mode(const std::string &bench_path_arg, char *executable, bool rerun_timeouts);
benchmarkResult run_one_execution_from_args(int argc, char **argv);

int main(int argc, char **argv) {
    try {
        std::string bench_path;
        if (extract_bench_path_arg(argc, argv, bench_path)) {
            const bool rerun_timeouts = extract_rerun_timeouts_arg(argc, argv);
            return run_bench_mode(bench_path, argv[0], rerun_timeouts);
        }
        run_one_execution_from_args(argc, argv);
        return 0;
    } catch (const std::exception &e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }
}

benchmarkResult run_one_execution_from_args(int argc, char **argv) {
    clear_visualization_outputs();

    std::string path = "../qasms/example.qasm";
    std::string magic_aware_strategy = "distance";
    std::string type = "magic_aware";
    std::string gaussian_strategy = "fine";
    std::string safe_passage_strategy = "passage";
    double magic_high = 1.5;
    double magic_low = 0.5;
    double cnot_high = 1.5;
    double cnot_low = 0.5;
    double mapped_gaussian_weight = 0.8;
    double base_gaussian_weight = 1.0;
    std::string config_path = "../config/compiler_config.json";
    std::string graph_path = "";
    std::string magic_state_placement_strategy = "center_circle";
    int number_of_magic_states = 10;
    double border_distance_percentage = 10.0;
    int x = 10;
    int y = 11;
    int maximum_iterations = 100;
    std::string routing_strategy = "congestion";

    apply_config_overrides(
        argc,
        argv,
        path,
        magic_aware_strategy,
        type,
        gaussian_strategy,
        safe_passage_strategy,
        magic_high,
        magic_low,
        cnot_high,
        cnot_low,
        mapped_gaussian_weight,
        base_gaussian_weight,
        config_path,
        x,
        y,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        border_distance_percentage, 
        routing_strategy
    );

    argument_parsing(
        argc,
        argv,
        path,
        magic_aware_strategy,
        type,
        gaussian_strategy,
        safe_passage_strategy,
        magic_high,
        magic_low,
        cnot_high,
        cnot_low,
        mapped_gaussian_weight,
        base_gaussian_weight,
        x,
        y,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        border_distance_percentage,
        routing_strategy
    );

    std::cout << "circuit path: " << path << std::endl;
    std::cout << "magic aware strategy: " << magic_aware_strategy << std::endl;
    std::cout << "type: " << type << std::endl;
    std::cout << "gaussian strategy: " << gaussian_strategy << std::endl;
    std::cout << "MAGIC_HIGH: " << magic_high << std::endl;
    std::cout << "MAGIC_LOW: " << magic_low << std::endl;
    std::cout << "CNOT_HIGH: " << cnot_high << std::endl;
    std::cout << "CNOT_LOW: " << cnot_low << std::endl;
    std::cout << "MAPPED_GAUSSIAN_WEIGHT: " << mapped_gaussian_weight << std::endl;
    std::cout << "BASE_GAUSSIAN_WEIGHT: " << base_gaussian_weight << std::endl;
    std::cout << "safe passage strategy: " << safe_passage_strategy << std::endl;
    std::cout << "MagicStatePlacementStrategy: " << magic_state_placement_strategy << std::endl;
    std::cout << "number_of_magic_states: " << number_of_magic_states << std::endl;
    std::cout << "border_distance_percentage: " << border_distance_percentage << std::endl;
    std::cout << "routing strategy: " << routing_strategy << std::endl;
    if (!graph_path.empty()) {
        std::cout << "graph path: " << graph_path << std::endl;
    } else {
        std::cout << "graph dimensions: " << x << "x" << y << std::endl;
    }

    return one_execution(
        path,
        magic_aware_strategy,
        type,
        gaussian_strategy,
        safe_passage_strategy,
        magic_high,
        magic_low,
        cnot_high,
        cnot_low,
        mapped_gaussian_weight,
        base_gaussian_weight,
        x,
        y,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        border_distance_percentage,
        maximum_iterations,
        routing_strategy
    );
}

int run_bench_mode(const std::string &bench_path_arg, char *executable, bool rerun_timeouts) {
    const std::string bench_name = extract_bench_name(bench_path_arg);
    if (bench_name.empty()) {
        throw std::runtime_error("Invalid bench name for --bench_path");
    }

    const std::filesystem::path expanded_path = expand_config_variants(bench_name);
    std::ifstream expanded_stream(expanded_path);
    if (!expanded_stream.is_open()) {
        throw std::runtime_error("Cannot open expanded bench file: " + expanded_path.string());
    }

    json bench_data;
    expanded_stream >> bench_data;
    if (!bench_data.is_array()) {
        throw std::runtime_error("Expanded bench file must contain a JSON array: " + expanded_path.string());
    }

    const std::filesystem::path project_root(PROJECT_ROOT);
    const std::filesystem::path results_dir = project_root / "benchmarks" / "results";
    const std::filesystem::path logs_dir = project_root / "benchmarks" / "logs";
    std::filesystem::create_directories(results_dir);
    std::filesystem::create_directories(logs_dir);

    const std::string csv_file_name = sanitize_filename(bench_name) + "_runs.csv";
    const std::filesystem::path csv_path = results_dir / csv_file_name;
    write_csv::ensure_initialized(csv_path, write_csv::kBenchmarkRunsCsvHeader);
    int next_run_id = write_csv::read_max_run_id(csv_path) + 1;

    const std::filesystem::path temp_config_path = expanded_path.parent_path() / "__bench_runtime_config.json";

    auto cleanup_temp = [&]() {
        std::error_code ec;
        std::filesystem::remove(temp_config_path, ec);
    };

    auto persist_expanded = [&]() {
        std::ofstream out(expanded_path);
        if (!out.is_open()) {
            throw std::runtime_error("Cannot write expanded bench file: " + expanded_path.string());
        }
        out << bench_data.dump(2) << '\n';
    };

    int final_exit_code = 0;
    const std::size_t total_cases = bench_data.size();

    const auto parse_timeout_seconds = [](const json &entry) -> double {
        if (!entry.contains("timeout")) {
            return -1.0;
        }

        const json &timeout_value = entry.at("timeout");
        if (!timeout_value.is_number()) {
            throw std::runtime_error("Bench field 'timeout' must be numeric.");
        }

        const double timeout_seconds = timeout_value.get<double>();
        if (!std::isfinite(timeout_seconds) || timeout_seconds < 0.0) {
            throw std::runtime_error("Bench field 'timeout' must be a finite number >= 0.");
        }

        return timeout_seconds;
    };

    const auto shell_quote = [](const std::string &value) {
        std::string quoted = "'";
        for (char c : value) {
            if (c == '\'') {
                quoted += "'\"'\"'";
            } else {
                quoted.push_back(c);
            }
        }
        quoted.push_back('\'');
        return quoted;
    };

    const auto decode_system_exit_code = [](int system_rc) {
        if (system_rc == -1) {
            return 1;
        }
        if (WIFEXITED(system_rc)) {
            return WEXITSTATUS(system_rc);
        }
        if (WIFSIGNALED(system_rc)) {
            return 128 + WTERMSIG(system_rc);
        }
        return 1;
    };

    const auto extract_routing_steps_from_log = [](const std::filesystem::path &log_path) {
        std::ifstream in(log_path);
        if (!in.is_open()) {
            return std::string {};
        }

        std::string line;
        std::string last_match;
        while (std::getline(in, line)) {
            const std::size_t marker_pos = line.find("Total routing steps");
            if (marker_pos == std::string::npos) {
                continue;
            }
            const std::size_t colon_pos = line.rfind(':');
            if (colon_pos == std::string::npos || colon_pos <= marker_pos) {
                continue;
            }
            std::string tail = line.substr(colon_pos + 1);
            while (!tail.empty() && std::isspace(static_cast<unsigned char>(tail.front()))) {
                tail.erase(tail.begin());
            }
            std::size_t digits_len = 0;
            while (digits_len < tail.size() && std::isdigit(static_cast<unsigned char>(tail[digits_len]))) {
                ++digits_len;
            }
            if (digits_len > 0) {
                last_match = tail.substr(0, digits_len);
            }
        }
        return last_match;
    };

    const auto extract_resolved_graph_dimensions_from_log = [](const std::filesystem::path &log_path) {
        std::ifstream in(log_path);
        if (!in.is_open()) {
            return std::pair<std::string, std::string> {"", ""};
        }

        std::string line;
        std::string last_x;
        std::string last_y;
        const std::string marker = "resolved graph dimensions:";
        while (std::getline(in, line)) {
            const std::size_t marker_pos = line.find(marker);
            if (marker_pos == std::string::npos) {
                continue;
            }

            std::string tail = line.substr(marker_pos + marker.size());
            while (!tail.empty() && std::isspace(static_cast<unsigned char>(tail.front()))) {
                tail.erase(tail.begin());
            }

            std::size_t i = 0;
            while (i < tail.size() && std::isdigit(static_cast<unsigned char>(tail[i]))) {
                ++i;
            }
            if (i == 0 || i >= tail.size() || tail[i] != 'x') {
                continue;
            }
            const std::string x = tail.substr(0, i);

            std::size_t j = i + 1;
            std::size_t k = j;
            while (k < tail.size() && std::isdigit(static_cast<unsigned char>(tail[k]))) {
                ++k;
            }
            if (k == j) {
                continue;
            }
            const std::string y = tail.substr(j, k - j);

            last_x = x;
            last_y = y;
        }

        return std::pair<std::string, std::string> {last_x, last_y};
    };

    const auto extract_error_excerpt_from_log = [](const std::filesystem::path &log_path) {
        std::ifstream in(log_path);
        if (!in.is_open()) {
            return std::string {};
        }

        const auto trim = [](const std::string &s) {
            std::size_t start = 0;
            while (start < s.size() && std::isspace(static_cast<unsigned char>(s[start]))) {
                ++start;
            }
            std::size_t end = s.size();
            while (end > start && std::isspace(static_cast<unsigned char>(s[end - 1]))) {
                --end;
            }
            return s.substr(start, end - start);
        };

        std::string line;
        std::string last_non_empty;
        std::string best_hint;
        while (std::getline(in, line)) {
            std::string cleaned = trim(line);
            if (cleaned.empty()) {
                continue;
            }
            last_non_empty = cleaned;

            std::string lowered = cleaned;
            std::transform(lowered.begin(), lowered.end(), lowered.begin(), [](unsigned char c) {
                return static_cast<char>(std::tolower(c));
            });
            if (lowered.find("error") != std::string::npos ||
                lowered.find("failed") != std::string::npos ||
                lowered.find("invalid") != std::string::npos ||
                lowered.find("exception") != std::string::npos ||
                lowered.find("terminate") != std::string::npos ||
                lowered.find("what():") != std::string::npos) {
                best_hint = cleaned;
            }
        }

        return best_hint.empty() ? last_non_empty : best_hint;
    };

    try {
        for (std::size_t i = 0; i < bench_data.size(); ++i) {
            if (!bench_data.at(i).is_object()) {
                throw std::runtime_error("Bench entry " + std::to_string(i + 1) + " must be a JSON object.");
            }
            json &entry = bench_data.at(i);
            const double timeout_seconds = parse_timeout_seconds(entry);
            const bool timeout_enabled = timeout_seconds >= 0.0;

            std::string case_id = get_json_field(entry, {"case_id"});
            if (case_id.empty()) {
                case_id = get_json_field(entry, {"id"});
            }

            const bool already_executed =
                entry.contains("executed") && entry["executed"].is_boolean() && entry["executed"].get<bool>();
            const bool timeout_reached_before =
                entry.contains("timeout_reached") &&
                entry["timeout_reached"].is_boolean() &&
                entry["timeout_reached"].get<bool>();
            const bool rerun_timeout_case = rerun_timeouts && already_executed && timeout_reached_before;

            if (already_executed && !rerun_timeout_case) {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] SKIP"
                    << " " << empty_to_dash(case_id)
                    << " executed=true\n";
                continue;
            }

            if (rerun_timeout_case) {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] RERUN_TIMEOUT"
                    << " " << empty_to_dash(case_id)
                    << " executed=true timeout_reached=true\n";
            }

            const int run_id = next_run_id++;
            const auto start_tp = std::chrono::system_clock::now();
            const auto start_steady = std::chrono::steady_clock::now();
            const std::string run_date = format_now_date(start_tp);
            const std::string run_datetime = format_now_datetime(start_tp);

            const std::string log_file_name =
                "run_" + std::to_string(run_id) + "_" + sanitize_filename(case_id.empty() ? std::to_string(i + 1) : case_id) + ".log";
            const std::filesystem::path log_path = logs_dir / log_file_name;

            std::ofstream temp_stream(temp_config_path);
            if (!temp_stream.is_open()) {
                throw std::runtime_error("Cannot write temporary config: " + temp_config_path.string());
            }
            temp_stream << entry.dump(2) << '\n';
            temp_stream.close();

            std::string status = "success";
            int exit_code = 0;
            std::string routing_steps;
            std::string error_excerpt;
            bool timeout_reached = false;
            std::string resolved_graph_x;
            std::string resolved_graph_y;

            std::string command;
            if (timeout_enabled) {
                std::ostringstream timeout_ss;
                timeout_ss << std::fixed << std::setprecision(3) << timeout_seconds;
                command =
                    "timeout --signal=TERM --kill-after=1s " + timeout_ss.str() +
                    " " + shell_quote(executable) +
                    " --config " + shell_quote(temp_config_path.string()) +
                    " > " + shell_quote(log_path.string()) +
                    " 2>&1";
            } else {
                command =
                    shell_quote(executable) +
                    " --config " + shell_quote(temp_config_path.string()) +
                    " > " + shell_quote(log_path.string()) +
                    " 2>&1";
            }

            exit_code = decode_system_exit_code(std::system(command.c_str()));
            timeout_reached = timeout_enabled && exit_code == 124;

            if (timeout_reached) {
                status = "timeout";
                // Timeout is tracked in CSV, but should not fail the whole benchmark target.
                std::ostringstream timeout_ss;
                timeout_ss << std::fixed << std::setprecision(3) << timeout_seconds;
                error_excerpt = "Execution exceeded timeout of " + timeout_ss.str() + "s";
            } else if (exit_code != 0) {
                status = "failed";
                if (final_exit_code == 0) {
                    final_exit_code = exit_code;
                }
                const std::string log_excerpt = extract_error_excerpt_from_log(log_path);
                error_excerpt = "Execution failed with exit code " + std::to_string(exit_code);
                if (!log_excerpt.empty()) {
                    error_excerpt += ": " + log_excerpt;
                }
            } else {
                routing_steps = extract_routing_steps_from_log(log_path);
            }
            {
                const auto resolved_dims = extract_resolved_graph_dimensions_from_log(log_path);
                resolved_graph_x = resolved_dims.first;
                resolved_graph_y = resolved_dims.second;
            }

            const auto end_steady = std::chrono::steady_clock::now();
            const std::chrono::duration<double> elapsed = end_steady - start_steady;
            std::ostringstream duration_ss;
            duration_ss << std::fixed << std::setprecision(6) << elapsed.count();
            std::ostringstream duration_short_ss;
            duration_short_ss << std::fixed << std::setprecision(3) << elapsed.count() << "s";

            if (error_excerpt.empty() && status != "success") {
                error_excerpt = "Execution failed";
            }

            entry["executed"] = true;
            entry["timeout_reached"] = timeout_reached;
            persist_expanded();

            const std::string circuit = get_json_field(entry, {"circuit"});

            std::string circuit_graph_label = get_json_field(entry, {"circuit_graph_label"});
            if (circuit_graph_label.empty() && !circuit.empty() && !resolved_graph_x.empty() && !resolved_graph_y.empty()) {
                circuit_graph_label = circuit + "-" + resolved_graph_x + "x" + resolved_graph_y;
            }
            std::string routing_strategy_csv = get_json_field(
                entry,
                {"routing_strategy", "routing-strategy", "routing_method", "routing-method", "routing"}
            );
            if (routing_strategy_csv.empty()) {
                routing_strategy_csv = "congestion";
            }

            write_csv::append_row(
                csv_path,
                {
                    std::to_string(run_id),
                    run_date,
                    run_datetime,
                    circuit,
                    resolved_graph_x,
                    resolved_graph_y,
                    circuit_graph_label,
                    get_json_field(entry, {"mapping_type", "type"}),
                    get_json_field(entry, {"magic_aware_strategy"}),
                    get_json_field(entry, {"gaussian_strategy"}),
                    get_json_field(entry, {"safe_passage_strategy"}),
                    get_json_field(entry, {"magic_state_placement_strategy", "MagicStatePlacementStrategy"}),
                    get_json_field(entry, {"border_distance_percentage"}),
                    get_json_field(entry, {"number_of_magic_states"}),
                    routing_strategy_csv,
                    routing_steps,
                    timeout_reached ? "true" : "false",
                    status,
                    std::to_string(exit_code),
                    duration_ss.str(),
                    log_path.string(),
                    limit_text(compact_line(error_excerpt), 300)
                }
            );

            const std::string mw = get_json_field(entry, {"MAPPED_GAUSSIAN_WEIGHT", "mapped_gaussian_weight"});
            const std::string bw = get_json_field(entry, {"BASE_GAUSSIAN_WEIGHT", "base_gaussian_weight"});
            const std::string mh = get_json_field(entry, {"MAGIC_HIGH", "magic_high"});
            const std::string ml = get_json_field(entry, {"MAGIC_LOW", "magic_low"});
            const std::string ch = get_json_field(entry, {"CNOT_HIGH", "cnot_high"});
            const std::string cl = get_json_field(entry, {"CNOT_LOW", "cnot_low"});

            if (status == "success") {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] OK"
                    << " #" << run_id
                    << " " << empty_to_dash(case_id)
                    << " routing_steps=" << empty_to_dash(routing_steps)
                    << " duration=" << duration_short_ss.str()
                    << " mw=" << empty_to_dash(mw)
                    << " bw=" << empty_to_dash(bw)
                    << " mh=" << empty_to_dash(mh)
                    << " ml=" << empty_to_dash(ml)
                    << " ch=" << empty_to_dash(ch)
                    << " cl=" << empty_to_dash(cl)
                    << " timeout_reached=" << (timeout_reached ? "true" : "false")
                    << "\n";
            } else if (status == "timeout") {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] TIMEOUT"
                    << " #" << run_id
                    << " " << empty_to_dash(case_id)
                    << " duration=" << duration_short_ss.str()
                    << " timeout_reached=true"
                    << "\n";
            } else {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] FAIL"
                    << " #" << run_id
                    << " " << empty_to_dash(case_id)
                    << " duration=" << duration_short_ss.str()
                    << " error=" << empty_to_dash(limit_text(compact_line(error_excerpt), 120))
                    << "\n";
            }
        }
    } catch (...) {
        cleanup_temp();
        throw;
    }

    cleanup_temp();
    return final_exit_code;
}
