#include "one_execution.hpp"
#include "expand_config_variants.hpp"
#include "helpers.hpp"
#include "parsing.hpp"
#include "write_csv.hpp"

#include <algorithm>
#include <chrono>
#include <cctype>
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


int run_bench_mode(const std::string &bench_path_arg, char *executable);
benchmarkResult run_one_execution_from_args(int argc, char **argv);



int main(int argc, char **argv) {
    try {
        std::string bench_path;
        if (extract_bench_path_arg(argc, argv, bench_path)) {
            return run_bench_mode(bench_path, argv[0]);
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

int run_bench_mode(const std::string &bench_path_arg, char *executable) {
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

    try {
        for (std::size_t i = 0; i < bench_data.size(); ++i) {
            if (!bench_data.at(i).is_object()) {
                throw std::runtime_error("Bench entry " + std::to_string(i + 1) + " must be a JSON object.");
            }
            json &entry = bench_data.at(i);

            std::string case_id = get_json_field(entry, {"case_id"});
            if (case_id.empty()) {
                case_id = get_json_field(entry, {"id"});
            }

            const bool already_executed =
                entry.contains("executed") && entry["executed"].is_boolean() && entry["executed"].get<bool>();
            if (already_executed) {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] SKIP"
                    << " " << empty_to_dash(case_id)
                    << " executed=true\n";
                continue;
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

            std::vector<std::string> bench_args_storage = {
                std::string(executable),
                "--config",
                temp_config_path.string()
            };
            std::vector<char *> bench_argv;
            bench_argv.reserve(bench_args_storage.size());
            for (auto &arg : bench_args_storage) {
                bench_argv.push_back(arg.data());
            }

            std::string status = "success";
            int exit_code = 0;
            std::string routing_steps;
            std::string avg_parallelism;
            std::string error_excerpt;
            std::string captured_output;

            {
                ScopedStreamRedirect capture;
                try {
                    const benchmarkResult run_result = run_one_execution_from_args(
                        static_cast<int>(bench_argv.size()),
                        bench_argv.data()
                    );
                    routing_steps = std::to_string(run_result.routing_steps);
                } catch (const std::exception &e) {
                    status = "failed";
                    exit_code = 1;
                    final_exit_code = 1;
                    error_excerpt = e.what();
                } catch (...) {
                    status = "failed";
                    exit_code = 1;
                    final_exit_code = 1;
                    error_excerpt = "Unknown error";
                }
                captured_output = capture.str();
            }

            std::ofstream log_out(log_path);
            if (log_out.is_open()) {
                log_out << captured_output;
            }

            if (error_excerpt.empty() && status != "success") {
                error_excerpt = "Execution failed";
            }

            entry["executed"] = true;
            persist_expanded();

            const auto end_steady = std::chrono::steady_clock::now();
            const std::chrono::duration<double> elapsed = end_steady - start_steady;
            std::ostringstream duration_ss;
            duration_ss << std::fixed << std::setprecision(6) << elapsed.count();
            std::ostringstream duration_short_ss;
            duration_short_ss << std::fixed << std::setprecision(3) << elapsed.count() << "s";

            const std::string circuit = get_json_field(entry, {"circuit"});
            const std::string graph_x = get_json_field(entry, {"graph_x", "x"});
            const std::string graph_y = get_json_field(entry, {"graph_y", "y"});
            std::string graph_dimensions = get_json_field(entry, {"graph_dimensions"});
            if (graph_dimensions.empty() && !graph_x.empty() && !graph_y.empty()) {
                graph_dimensions = graph_x + "x" + graph_y;
            }

            std::string circuit_graph_label = get_json_field(entry, {"circuit_graph_label"});
            if (circuit_graph_label.empty() && !circuit.empty() && !graph_dimensions.empty()) {
                circuit_graph_label = circuit + "-" + graph_dimensions;
            }

            write_csv::append_row(
                csv_path,
                {
                    std::to_string(run_id),
                    run_date,
                    run_datetime,
                    get_json_field(entry, {"benchmark_suite"}),
                    get_json_field(entry, {"chart_group"}),
                    case_id,
                    circuit,
                    graph_x,
                    graph_y,
                    graph_dimensions,
                    circuit_graph_label,
                    get_json_field(entry, {"mapping_type", "type"}),
                    get_json_field(entry, {"magic_aware_strategy"}),
                    get_json_field(entry, {"gaussian_strategy"}),
                    get_json_field(entry, {"safe_passage_strategy"}),
                    get_json_field(entry, {"magic_state_placement_strategy", "MagicStatePlacementStrategy"}),
                    get_json_field(entry, {"border_distance_percentage"}),
                    get_json_field(entry, {"number_of_magic_states"}),
                    routing_steps,
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
