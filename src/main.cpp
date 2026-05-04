#include "one_execution.hpp"
#include "expand_config_variants.hpp"
#include "helpers.hpp"
#include "parsing.hpp"
#include "write_csv.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cctype>
#include <csignal>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <unordered_set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include <sys/wait.h>

#ifdef _OPENMP
#include <omp.h>
#endif


namespace {
constexpr const char *kBenchResultFileEnv = "FTQC_BENCH_RESULT_FILE";

volatile std::sig_atomic_t g_bench_interrupt_requested = 0;
volatile std::sig_atomic_t g_bench_interrupt_signal = 0;

void handle_bench_interrupt(int signal_number) {
    g_bench_interrupt_requested = 1;
    g_bench_interrupt_signal = signal_number;
}

void write_benchmark_worker_payload_if_requested(const json &payload) {
    const char *raw_path = std::getenv(kBenchResultFileEnv);
    if (raw_path == nullptr || *raw_path == '\0') {
        return;
    }

    std::ofstream out(raw_path);
    if (!out.is_open()) {
        throw std::runtime_error("Cannot write benchmark result file: " + std::string(raw_path));
    }
    out << payload.dump(2) << '\n';
}

void write_benchmark_result_file_if_requested(const benchmarkResult &result) {
    json payload = {
        {"status", "success"},
        {"routing_steps", result.routing_steps},
        {"avg_parallelism", result.avg_parallelism}
    };

    if (result.resolved_graph_x >= 0 && result.resolved_graph_y >= 0) {
        payload["resolved_graph_x"] = result.resolved_graph_x;
        payload["resolved_graph_y"] = result.resolved_graph_y;
    }

    write_benchmark_worker_payload_if_requested(payload);
}

void try_write_benchmark_error_file(const std::string &message) {
    try {
        write_benchmark_worker_payload_if_requested({
            {"status", "failed"},
            {"error", message}
        });
    } catch (const std::exception &) {
    }
}

json read_benchmark_worker_payload(const std::filesystem::path &path) {
    std::ifstream in(path);
    if (!in.is_open()) {
        throw std::runtime_error("Benchmark worker did not write result file: " + path.string());
    }

    json payload;
    in >> payload;
    if (!payload.is_object()) {
        throw std::runtime_error("Benchmark worker result file is not a JSON object: " + path.string());
    }
    return payload;
}

benchmarkResult benchmark_result_from_worker_payload(const json &payload) {
    const std::string status = get_json_field(payload, {"status"});
    if (status != "success") {
        const std::string error = get_json_field(payload, {"error"});
        throw std::runtime_error(error.empty() ? "Benchmark worker did not return a successful result." : error);
    }
    if (!payload.contains("routing_steps") || !payload.at("routing_steps").is_number_integer()) {
        throw std::runtime_error("Benchmark worker result is missing numeric routing_steps.");
    }

    benchmarkResult result;
    result.routing_steps = payload.at("routing_steps").get<int>();
    if (payload.contains("avg_parallelism") && payload.at("avg_parallelism").is_number()) {
        result.avg_parallelism = payload.at("avg_parallelism").get<double>();
    }
    if (payload.contains("resolved_graph_x") && payload.at("resolved_graph_x").is_number_integer()) {
        result.resolved_graph_x = payload.at("resolved_graph_x").get<int>();
    }
    if (payload.contains("resolved_graph_y") && payload.at("resolved_graph_y").is_number_integer()) {
        result.resolved_graph_y = payload.at("resolved_graph_y").get<int>();
    }
    return result;
}

std::string worker_error_from_result_file(const std::filesystem::path &path) {
    if (!std::filesystem::exists(path)) {
        return "";
    }

    try {
        return get_json_field(read_benchmark_worker_payload(path), {"error"});
    } catch (const std::exception &) {
        return "";
    }
}
} // namespace

int run_bench_mode(
    const std::string &bench_path_arg,
    char *executable,
    bool rerun_timeouts,
    int process_count,
    int processor
);
benchmarkResult run_one_execution_from_args(int argc, char **argv);

int main(int argc, char **argv) {
    try {
        std::string bench_path;
        if (extract_bench_path_arg(argc, argv, bench_path)) {
            const bool rerun_timeouts = extract_rerun_timeouts_arg(argc, argv);
            const int process_count = extract_process_count_arg(argc, argv);
            const int processor = extract_processor_arg(argc, argv);
            return run_bench_mode(bench_path, argv[0], rerun_timeouts, process_count, processor);
        }
        run_one_execution_from_args(argc, argv);
        return 0;
    } catch (const std::exception &e) {
        try_write_benchmark_error_file(e.what());
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }
}

benchmarkResult run_one_execution_from_args(int argc, char **argv) {
    if (benchmark_artifacts_enabled()) {
        clear_visualization_outputs();
    }

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
    double size_moltiplier = 1.0;
    double gaussian_confidence = 0.95;
    std::string config_path = "../config/compiler_config.json";
    std::string graph_path = "";
    std::string magic_state_placement_strategy = "center_circle";
    int number_of_magic_states = 10;
    double number_of_magic_states_multiplier = 0.0;
    double border_distance_percentage = 10.0;
    int x = 10;
    int y = 11;
    int maximum_iterations = 500;
    std::string routing_strategy = "congestion";
    std::string t_routing_mode = "normal_t_routing";
    int patience_threshold = 3;

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
        size_moltiplier,
        gaussian_confidence,
        config_path,
        x,
        y,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        number_of_magic_states_multiplier,
        border_distance_percentage, 
        routing_strategy,
        t_routing_mode,
        patience_threshold
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
        size_moltiplier,
        gaussian_confidence,
        x,
        y,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        number_of_magic_states_multiplier,
        border_distance_percentage,
        routing_strategy,
        t_routing_mode,
        patience_threshold
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
    std::cout << "size_moltiplier: " << size_moltiplier << std::endl;
    std::cout << "gaussian_confidence: " << gaussian_confidence << std::endl;
    std::cout << "safe passage strategy: " << safe_passage_strategy << std::endl;
    std::cout << "MagicStatePlacementStrategy: " << magic_state_placement_strategy << std::endl;
    if (number_of_magic_states_multiplier > 0.0) {
        std::cout << "number_of_magic_states: qubits*" << number_of_magic_states_multiplier
                  << " (resolved at runtime)" << std::endl;
    } else {
        std::cout << "number_of_magic_states: " << number_of_magic_states << std::endl;
    }
    std::cout << "border_distance_percentage: " << border_distance_percentage << std::endl;
    std::cout << "routing strategy: " << routing_strategy << std::endl;
    if (!graph_path.empty()) {
        std::cout << "graph path: " << graph_path << std::endl;
    } else {
        std::cout << "graph dimensions: " << x << "x" << y << std::endl;
    }

    const auto execution_start = std::chrono::steady_clock::now();
    benchmarkResult result = one_execution(
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
        size_moltiplier,
        gaussian_confidence,
        x,
        y,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        number_of_magic_states_multiplier,
        border_distance_percentage,
        routing_strategy,
        t_routing_mode,
        patience_threshold
    );
    write_benchmark_result_file_if_requested(result);

    const auto execution_end = std::chrono::steady_clock::now();
    const std::chrono::duration<double> execution_elapsed = execution_end - execution_start;
    if (!benchmark_worker_mode_enabled()) {
        std::cout << "Execution time: "
                  << std::fixed << std::setprecision(6)
                  << execution_elapsed.count()
                  << " seconds\n";
    }

    return result;
}

int run_bench_mode(
    const std::string &bench_path_arg,
    char *executable,
    bool rerun_timeouts,
    int process_count,
    int processor
) {
    const std::string bench_name = extract_bench_name(bench_path_arg);
    if (bench_name.empty()) {
        throw std::runtime_error("Invalid bench name for --bench_path");
    }

    const std::filesystem::path expanded_path = expand_config_variants(bench_name, process_count);
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
    int next_execution_id = write_csv::read_max_execution_id(csv_path) + 1;

    auto persist_expanded = [&]() {
        std::ofstream out(expanded_path);
        if (!out.is_open()) {
            throw std::runtime_error("Cannot write expanded bench file: " + expanded_path.string());
        }
        out << bench_data.dump(2) << '\n';
    };

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

    const auto parse_entry_processor = [](const json &entry) -> int {
        const json *processor_value = nullptr;
        if (entry.contains("processor")) {
            processor_value = &entry.at("processor");
        } else if (entry.contains("process")) {
            processor_value = &entry.at("process");
        } else {
            return 0;
        }

        if (!processor_value->is_number_integer()) {
            throw std::runtime_error("Bench field 'processor' must be an integer.");
        }

        const int parsed_processor = processor_value->get<int>();
        if (parsed_processor < 0) {
            throw std::runtime_error("Bench field 'processor' must be >= 0.");
        }

        return parsed_processor;
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

    g_bench_interrupt_requested = 0;
    g_bench_interrupt_signal = 0;
    using SignalHandler = void (*)(int);
    const SignalHandler previous_sigint_handler = std::signal(SIGINT, handle_bench_interrupt);
    const SignalHandler previous_sigterm_handler = std::signal(SIGTERM, handle_bench_interrupt);
    const SignalHandler previous_sighup_handler = std::signal(SIGHUP, handle_bench_interrupt);
    auto restore_signal_handlers = [&]() {
        if (previous_sigint_handler != SIG_ERR) {
            std::signal(SIGINT, previous_sigint_handler);
        }
        if (previous_sigterm_handler != SIG_ERR) {
            std::signal(SIGTERM, previous_sigterm_handler);
        }
        if (previous_sighup_handler != SIG_ERR) {
            std::signal(SIGHUP, previous_sighup_handler);
        }
    };

    struct BenchCasePlan {
        std::size_t index = 0;
        json entry;
        std::string case_id;
        int processor = 0;
        double timeout_seconds = -1.0;
        bool timeout_enabled = false;
        bool already_executed = false;
        bool timeout_reached_before = false;
        bool rerun_timeout_case = false;
        bool replace_interrupted_csv_row = false;
        std::size_t replacement_csv_data_row = 0;
    };

    struct BenchCaseResult {
        bool completed = false;
        std::size_t index = 0;
        int execution_id = 0;
        std::string case_id;
        std::string status = "failed";
        int exit_code = 1;
        bool timeout_reached = false;
        bool interrupted = false;
        bool mark_entry_as_executed = false;
        std::string progress_line;
        std::vector<std::string> csv_row;
    };

    std::vector<BenchCaseResult> results(total_cases);
    bool stop_message_printed = false;

    try {
        std::vector<BenchCasePlan> plans;
        plans.reserve(total_cases);
        std::vector<std::size_t> runnable_indices;
        runnable_indices.reserve(total_cases);

        std::cout << "Benchmark processor filter: processor=" << processor << "\n";

        const auto normalize_identity_value = [](std::string value) {
            while (!value.empty() && std::isspace(static_cast<unsigned char>(value.front()))) {
                value.erase(value.begin());
            }
            while (!value.empty() && std::isspace(static_cast<unsigned char>(value.back()))) {
                value.pop_back();
            }

            std::string lowered = value;
            std::transform(lowered.begin(), lowered.end(), lowered.begin(), [](unsigned char c) {
                return static_cast<char>(std::tolower(c));
            });
            if (lowered == "true" || lowered == "false") {
                return lowered;
            }

            char *end_ptr = nullptr;
            const double parsed = std::strtod(value.c_str(), &end_ptr);
            if (end_ptr != value.c_str() && end_ptr != nullptr && *end_ptr == '\0' && std::isfinite(parsed)) {
                std::ostringstream oss;
                oss << std::setprecision(12) << parsed;
                return oss.str();
            }

            return value;
        };

        const auto plan_field = [&](const json &entry, const std::vector<std::string> &keys, const std::string &fallback = "") {
            std::string value = get_json_field(entry, keys);
            if (value.empty()) {
                value = fallback;
            }
            return normalize_identity_value(value);
        };

        const auto csv_field = [&](const std::vector<std::string> &row, std::size_t index, const std::string &fallback = "") {
            std::string value = write_csv::at_or_empty(row, index);
            if (value.empty()) {
                value = fallback;
            }
            return normalize_identity_value(value);
        };

        const auto entry_has_explicit_graph_dimensions = [&](const json &entry) {
            const std::string x_value = plan_field(entry, {"x"});
            const std::string y_value = plan_field(entry, {"y"});
            return !x_value.empty() && !y_value.empty() && x_value != "-1" && y_value != "-1";
        };

        const auto csv_row_matches_plan = [&](const std::vector<std::string> &row, const json &entry) {
            const std::vector<std::pair<std::size_t, std::string>> comparisons = {
                {3, plan_field(entry, {"circuit"})},
                {7, plan_field(entry, {"mapping_type", "type"})},
                {8, plan_field(entry, {"magic_aware_strategy"})},
                {9, plan_field(entry, {"gaussian_strategy"})},
                {10, plan_field(entry, {"MAGIC_HIGH", "magic_high"})},
                {11, plan_field(entry, {"MAGIC_LOW", "magic_low"})},
                {12, plan_field(entry, {"CNOT_HIGH", "cnot_high"})},
                {13, plan_field(entry, {"CNOT_LOW", "cnot_low"})},
                {14, plan_field(entry, {"MAPPED_GAUSSIAN_WEIGHT", "mapped_gaussian_weight"})},
                {15, plan_field(entry, {"BASE_GAUSSIAN_WEIGHT", "base_gaussian_weight"})},
                {16, plan_field(entry, {"SIZE_MOLTIPLIER", "size_moltiplier", "SIZE_MULTIPLIER", "size_multiplier"})},
                {17, plan_field(entry, {"GAUSSIAN_CONFIDENCE", "gaussian_confidence"})},
                {18, plan_field(entry, {"safe_passage_strategy"})},
                {19, plan_field(entry, {"magic_state_placement_strategy", "MagicStatePlacementStrategy"})},
                {20, plan_field(entry, {"border_distance_percentage"})},
                {21, plan_field(entry, {"number_of_magic_states"})},
                {22, plan_field(entry, {"routing_strategy", "routing-strategy", "routing_method", "routing-method", "routing"}, "congestion")},
                {23, plan_field(entry, {"t_routing_mode", "t-routing-mode"}, "normal_t_routing")}
            };

            for (const auto &[index, expected] : comparisons) {
                const std::string fallback = (index == 23) ? "normal_t_routing" : "";
                if (csv_field(row, index, fallback) != expected) {
                    return false;
                }
            }

            if (entry_has_explicit_graph_dimensions(entry)) {
                if (csv_field(row, 4) != plan_field(entry, {"x"}) ||
                    csv_field(row, 5) != plan_field(entry, {"y"})) {
                    return false;
                }
            }

            const std::string expected_label = plan_field(entry, {"circuit_graph_label"});
            if (!expected_label.empty() && csv_field(row, 6) != expected_label) {
                return false;
            }

            return true;
        };

        struct InterruptedCsvRow {
            std::size_t data_row_index = 0;
            std::vector<std::string> row;
            bool used = false;
        };

        std::vector<InterruptedCsvRow> interrupted_csv_rows;
        const std::vector<std::vector<std::string>> existing_csv_rows = write_csv::read_data_rows(csv_path);
        for (std::size_t row_index = 0; row_index < existing_csv_rows.size(); ++row_index) {
            const std::vector<std::string> &row = existing_csv_rows[row_index];
            if (csv_field(row, 26) != "interrupted") {
                continue;
            }

            interrupted_csv_rows.push_back({row_index, row, false});
        }

        if (!interrupted_csv_rows.empty()) {
            std::cout
                << "Found " << interrupted_csv_rows.size()
                << " interrupted CSV row(s) that can be reused if their configuration is scheduled again.\n";
        }

        for (std::size_t i = 0; i < total_cases; ++i) {
            if (!bench_data.at(i).is_object()) {
                throw std::runtime_error("Bench entry " + std::to_string(i + 1) + " must be a JSON object.");
            }

            BenchCasePlan plan;
            plan.index = i;
            plan.entry = bench_data.at(i);
            plan.processor = parse_entry_processor(plan.entry);
            plan.timeout_seconds = parse_timeout_seconds(plan.entry);
            plan.timeout_enabled = plan.timeout_seconds >= 0.0;
            plan.case_id = get_json_field(plan.entry, {"case_id"});
            if (plan.case_id.empty()) {
                plan.case_id = get_json_field(plan.entry, {"id"});
            }
            plan.already_executed =
                plan.entry.contains("executed") && plan.entry["executed"].is_boolean() && plan.entry["executed"].get<bool>();
            plan.timeout_reached_before =
                plan.entry.contains("timeout_reached") &&
                plan.entry["timeout_reached"].is_boolean() &&
                plan.entry["timeout_reached"].get<bool>();
            plan.rerun_timeout_case = rerun_timeouts && plan.already_executed && plan.timeout_reached_before;

            if (plan.processor != processor) {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] SKIP"
                    << " " << empty_to_dash(plan.case_id)
                    << " processor=" << plan.processor
                    << " selected_processor=" << processor << "\n";
            } else if (plan.already_executed && !plan.rerun_timeout_case) {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] SKIP"
                    << " " << empty_to_dash(plan.case_id)
                    << " executed=true\n";
            } else {
                if (plan.rerun_timeout_case) {
                    std::cout
                        << "[" << (i + 1) << "/" << total_cases << "] RERUN_TIMEOUT"
                        << " " << empty_to_dash(plan.case_id)
                        << " executed=true timeout_reached=true\n";
                }
                runnable_indices.push_back(i);
            }

            plans.push_back(std::move(plan));
        }

        std::size_t reusable_interrupted_rows = 0;
        for (std::size_t plan_index : runnable_indices) {
            BenchCasePlan &plan = plans[plan_index];
            for (InterruptedCsvRow &interrupted_row : interrupted_csv_rows) {
                if (interrupted_row.used || !csv_row_matches_plan(interrupted_row.row, plan.entry)) {
                    continue;
                }

                interrupted_row.used = true;
                plan.replace_interrupted_csv_row = true;
                plan.replacement_csv_data_row = interrupted_row.data_row_index;
                ++reusable_interrupted_rows;
                break;
            }
        }

        if (reusable_interrupted_rows > 0) {
            std::cout
                << "Will overwrite " << reusable_interrupted_rows
                << " interrupted CSV row(s) instead of appending new rows.\n";
        }

        if (!runnable_indices.empty()) {
#ifdef _OPENMP
            std::cout
                << "Benchmark parallelism: up to " << omp_get_max_threads()
                << " OpenMP worker(s).\n";
#else
            std::cout << "Benchmark parallelism: OpenMP not enabled, running sequentially.\n";
#endif
        }

        const auto execute_case = [&](const BenchCasePlan &plan, int execution_id) {
            BenchCaseResult result;
            result.completed = true;
            result.index = plan.index;
            result.execution_id = execution_id;
            result.case_id = plan.case_id;
            result.status = "success";
            result.exit_code = 0;

            const auto start_tp = std::chrono::system_clock::now();
            const auto start_steady = std::chrono::steady_clock::now();
            const std::string run_date = format_now_date(start_tp);
            const std::string run_datetime = format_now_datetime(start_tp);

            const std::string log_file_name =
                "run_" + std::to_string(execution_id) + "_" +
                sanitize_filename(plan.case_id.empty() ? std::to_string(plan.index + 1) : plan.case_id) + ".log";
            const std::filesystem::path log_path = logs_dir / log_file_name;
            const std::filesystem::path temp_config_path =
                expanded_path.parent_path() /
                ("__bench_runtime_config_" + std::to_string(execution_id) + ".json");
            const std::filesystem::path temp_result_path =
                expanded_path.parent_path() /
                ("__bench_runtime_result_" + std::to_string(execution_id) + ".json");

            const auto cleanup_temp = [&]() {
                std::error_code ec;
                std::filesystem::remove(temp_config_path, ec);
                std::filesystem::remove(temp_result_path, ec);
            };

            std::string routing_steps;
            std::string error_excerpt;
            std::string resolved_graph_x;
            std::string resolved_graph_y;

            try {
                std::ofstream temp_stream(temp_config_path);
                if (!temp_stream.is_open()) {
                    throw std::runtime_error("Cannot write temporary config: " + temp_config_path.string());
                }
                temp_stream << plan.entry.dump(2) << '\n';
                temp_stream.close();

                std::error_code remove_ec;
                std::filesystem::remove(temp_result_path, remove_ec);

                const std::string worker_env =
                    "FTQC_BENCH_WORKER=1 FTQC_BENCH_RESULT_FILE=" +
                    shell_quote(temp_result_path.string()) + " ";

                std::string command;
                if (plan.timeout_enabled) {
                    std::ostringstream timeout_ss;
                    timeout_ss << std::fixed << std::setprecision(3) << plan.timeout_seconds;
                    command =
                        worker_env +
                        "timeout --signal=TERM --kill-after=1s " + timeout_ss.str() +
                        " " + shell_quote(executable) +
                        " --config " + shell_quote(temp_config_path.string()) +
                        " > " + shell_quote(log_path.string()) +
                        " 2>&1";
                } else {
                    command =
                        worker_env +
                        shell_quote(executable) +
                        " --config " + shell_quote(temp_config_path.string()) +
                        " > " + shell_quote(log_path.string()) +
                        " 2>&1";
                }

                const int system_rc = std::system(command.c_str());
                result.exit_code = decode_system_exit_code(system_rc);
                const bool interrupted_by_signal =
                    system_rc != -1 &&
                    WIFSIGNALED(system_rc) &&
                    (WTERMSIG(system_rc) == SIGINT || WTERMSIG(system_rc) == SIGTERM || WTERMSIG(system_rc) == SIGHUP);
                const bool interrupted_by_exit_code =
                    (result.exit_code == 130) || (result.exit_code == 143) || (result.exit_code == 129);
                result.interrupted =
                    (g_bench_interrupt_requested != 0) || interrupted_by_signal || interrupted_by_exit_code;
                if (result.interrupted && g_bench_interrupt_requested == 0) {
                    g_bench_interrupt_requested = 1;
                    if (interrupted_by_signal) {
                        g_bench_interrupt_signal = WTERMSIG(system_rc);
                    }
                }

                result.timeout_reached = !result.interrupted && plan.timeout_enabled && result.exit_code == 124;

                if (result.interrupted) {
                    result.status = "interrupted";
                    error_excerpt = "Execution interrupted by SIGINT (Ctrl+C)";
                } else if (result.timeout_reached) {
                    result.status = "timeout";
                    std::ostringstream timeout_ss;
                    timeout_ss << std::fixed << std::setprecision(3) << plan.timeout_seconds;
                    error_excerpt = "Execution exceeded timeout of " + timeout_ss.str() + "s";
                } else if (result.exit_code != 0) {
                    result.status = "failed";
                    const std::string worker_error = worker_error_from_result_file(temp_result_path);
                    error_excerpt = "Execution failed with exit code " + std::to_string(result.exit_code);
                    if (!worker_error.empty()) {
                        error_excerpt += ": " + worker_error;
                    }
                } else {
                    const benchmarkResult worker_result =
                        benchmark_result_from_worker_payload(read_benchmark_worker_payload(temp_result_path));
                    routing_steps = std::to_string(worker_result.routing_steps);
                    if (worker_result.resolved_graph_x >= 0) {
                        resolved_graph_x = std::to_string(worker_result.resolved_graph_x);
                    }
                    if (worker_result.resolved_graph_y >= 0) {
                        resolved_graph_y = std::to_string(worker_result.resolved_graph_y);
                    }
                }
            } catch (const std::exception &e) {
                result.status = "failed";
                result.exit_code = 1;
                error_excerpt = e.what();
            }

            cleanup_temp();

            const auto end_steady = std::chrono::steady_clock::now();
            const std::chrono::duration<double> elapsed = end_steady - start_steady;
            std::ostringstream duration_ss;
            duration_ss << std::fixed << std::setprecision(6) << elapsed.count();
            std::ostringstream duration_short_ss;
            duration_short_ss << std::fixed << std::setprecision(3) << elapsed.count() << "s";

            if (error_excerpt.empty() && result.status != "success") {
                error_excerpt = "Execution failed";
            }

            result.mark_entry_as_executed = (result.status != "interrupted");

            const std::string circuit = get_json_field(plan.entry, {"circuit"});
            std::string circuit_graph_label = get_json_field(plan.entry, {"circuit_graph_label"});
            if (circuit_graph_label.empty() && !circuit.empty() && !resolved_graph_x.empty() && !resolved_graph_y.empty()) {
                circuit_graph_label = circuit + "-" + resolved_graph_x + "x" + resolved_graph_y;
            }

            std::string routing_strategy_csv = get_json_field(
                plan.entry,
                {"routing_strategy", "routing-strategy", "routing_method", "routing-method", "routing"}
            );
            if (routing_strategy_csv.empty()) {
                routing_strategy_csv = "congestion";
            }
            std::string t_routing_mode_csv = get_json_field(
                plan.entry,
                {"t_routing_mode", "t-routing-mode"}
            );
            if (t_routing_mode_csv.empty()) {
                t_routing_mode_csv = "normal_t_routing";
            }

            const std::string mw = get_json_field(plan.entry, {"MAPPED_GAUSSIAN_WEIGHT", "mapped_gaussian_weight"});
            const std::string bw = get_json_field(plan.entry, {"BASE_GAUSSIAN_WEIGHT", "base_gaussian_weight"});
            const std::string sm = get_json_field(plan.entry, {"SIZE_MOLTIPLIER", "size_moltiplier", "SIZE_MULTIPLIER", "size_multiplier"});
            const std::string gc = get_json_field(plan.entry, {"GAUSSIAN_CONFIDENCE", "gaussian_confidence"});
            const std::string mh = get_json_field(plan.entry, {"MAGIC_HIGH", "magic_high"});
            const std::string ml = get_json_field(plan.entry, {"MAGIC_LOW", "magic_low"});
            const std::string ch = get_json_field(plan.entry, {"CNOT_HIGH", "cnot_high"});
            const std::string cl = get_json_field(plan.entry, {"CNOT_LOW", "cnot_low"});

            result.csv_row = {
                plan.case_id.empty() ? std::to_string(plan.index + 1) : plan.case_id,
                run_date,
                run_datetime,
                circuit,
                resolved_graph_x,
                resolved_graph_y,
                circuit_graph_label,
                get_json_field(plan.entry, {"mapping_type", "type"}),
                get_json_field(plan.entry, {"magic_aware_strategy"}),
                get_json_field(plan.entry, {"gaussian_strategy"}),
                mh,
                ml,
                ch,
                cl,
                mw,
                bw,
                sm,
                gc,
                get_json_field(plan.entry, {"safe_passage_strategy"}),
                get_json_field(plan.entry, {"magic_state_placement_strategy", "MagicStatePlacementStrategy"}),
                get_json_field(plan.entry, {"border_distance_percentage"}),
                get_json_field(plan.entry, {"number_of_magic_states"}),
                routing_strategy_csv,
                t_routing_mode_csv,
                routing_steps,
                result.timeout_reached ? "true" : "false",
                result.status,
                std::to_string(result.exit_code),
                duration_ss.str(),
                log_path.string(),
                limit_text(compact_line(error_excerpt), 300)
            };

            std::ostringstream progress;
            if (result.status == "success") {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] OK"
                    << " run#" << execution_id
                    << " id=" << empty_to_dash(plan.case_id)
                    << " routing_steps=" << empty_to_dash(routing_steps)
                    << " duration=" << duration_short_ss.str()
                    << " mw=" << empty_to_dash(mw)
                    << " bw=" << empty_to_dash(bw)
                    << " mh=" << empty_to_dash(mh)
                    << " ml=" << empty_to_dash(ml)
                    << " ch=" << empty_to_dash(ch)
                    << " cl=" << empty_to_dash(cl)
                    << " sm=" << empty_to_dash(sm)
                    << " gc=" << empty_to_dash(gc)
                    << " timeout_reached=" << (result.timeout_reached ? "true" : "false");
            } else if (result.status == "timeout") {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] TIMEOUT"
                    << " #" << execution_id
                    << " " << empty_to_dash(plan.case_id)
                    << " duration=" << duration_short_ss.str()
                    << " timeout_reached=true";
            } else if (result.status == "interrupted") {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] INTERRUPTED"
                    << " #" << execution_id
                    << " " << empty_to_dash(plan.case_id)
                    << " duration=" << duration_short_ss.str();
            } else {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] FAIL"
                    << " #" << execution_id
                    << " " << empty_to_dash(plan.case_id)
                    << " duration=" << duration_short_ss.str()
                    << " error=" << empty_to_dash(limit_text(compact_line(error_excerpt), 120));
            }
            progress << "\n";
            result.progress_line = progress.str();

            return result;
        };

        std::atomic<int> next_execution_id_counter(next_execution_id);
        std::atomic<bool> fatal_error(false);
        std::string fatal_error_message;

        const long long runnable_count = static_cast<long long>(runnable_indices.size());

#pragma omp parallel for schedule(dynamic, 1) if(runnable_count > 1)
        for (long long runnable_idx = 0; runnable_idx < runnable_count; ++runnable_idx) {
            if (fatal_error.load() || g_bench_interrupt_requested != 0) {
                continue;
            }

            const std::size_t plan_index = runnable_indices[static_cast<std::size_t>(runnable_idx)];
            const BenchCasePlan &plan = plans[plan_index];
            const int execution_id = next_execution_id_counter.fetch_add(1);
            BenchCaseResult result = execute_case(plan, execution_id);
            results[plan.index] = result;

#pragma omp critical(bench_commit)
            {
                if (!fatal_error.load()) {
                    try {
                        bench_data.at(result.index)["executed"] = result.mark_entry_as_executed;
                        bench_data.at(result.index)["timeout_reached"] = result.timeout_reached;
                        persist_expanded();
                        const BenchCasePlan &committed_plan = plans[result.index];
                        if (committed_plan.replace_interrupted_csv_row) {
                            write_csv::replace_row(
                                csv_path,
                                committed_plan.replacement_csv_data_row,
                                result.csv_row
                            );
                        } else {
                            write_csv::append_row(csv_path, result.csv_row);
                        }
                    } catch (const std::exception &e) {
                        fatal_error = true;
                        fatal_error_message = e.what();
                    }
                }

                if (!fatal_error.load()) {
                    std::cout << result.progress_line;
                    if (result.status == "interrupted" && !stop_message_printed) {
                        std::cout << "Stopping benchmark on Ctrl+C.\n";
                        stop_message_printed = true;
                    }
                }
            }
        }

        if (fatal_error.load()) {
            throw std::runtime_error(fatal_error_message);
        }
    } catch (...) {
        restore_signal_handlers();
        throw;
    }

    int final_exit_code = 0;
    if (g_bench_interrupt_requested != 0) {
        final_exit_code = 130;
        if (!stop_message_printed) {
            std::cout << "\nInterrupt received. Stopping benchmark loop.\n";
        }
    } else {
        for (std::size_t i = 0; i < total_cases; ++i) {
            const BenchCaseResult &result = results[i];
            if (!result.completed) {
                continue;
            }
            if (result.status == "interrupted") {
                final_exit_code = 130;
                break;
            }
            if (result.status == "failed" && final_exit_code == 0) {
                final_exit_code = result.exit_code;
            }
        }
    }

    restore_signal_handlers();
    return final_exit_code;
}
