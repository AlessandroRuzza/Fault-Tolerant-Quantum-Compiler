#include "one_execution.hpp"
#include "expand_config_variants.hpp"
#include "helpers.hpp"
#include "parsing.hpp"
#include "write_csv.hpp"
#include "exceptions.hpp"

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

#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <mutex>
#include <spawn.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

#ifdef _OPENMP
#include <omp.h>
#endif


namespace {
constexpr const char *kBenchResultFileEnv = "FTQC_BENCH_RESULT_FILE";

volatile std::sig_atomic_t g_bench_interrupt_requested = 0;
volatile std::sig_atomic_t g_bench_interrupt_signal = 0;

// Worker subprocess registry. Each OpenMP thread that spawns a worker
// registers its PID here so handle_bench_interrupt() can forward the signal.
// Access from regular threads is mutex-protected; the signal handler reads
// without the mutex (each slot is sig_atomic_t and aligned, so a torn read
// is impossible — at worst it sees 0 or the PID, both of which are safe).
constexpr std::size_t kMaxBenchWorkers = 256;
volatile std::sig_atomic_t g_worker_pids[kMaxBenchWorkers] = {};
std::mutex g_worker_pids_mutex;

void register_worker_pid(pid_t pid) {
    std::lock_guard<std::mutex> lock(g_worker_pids_mutex);
    for (std::size_t i = 0; i < kMaxBenchWorkers; ++i) {
        if (g_worker_pids[i] == 0) {
            g_worker_pids[i] = static_cast<std::sig_atomic_t>(pid);
            return;
        }
    }
}

void unregister_worker_pid(pid_t pid) {
    std::lock_guard<std::mutex> lock(g_worker_pids_mutex);
    for (std::size_t i = 0; i < kMaxBenchWorkers; ++i) {
        if (g_worker_pids[i] == static_cast<std::sig_atomic_t>(pid)) {
            g_worker_pids[i] = 0;
            return;
        }
    }
}

void handle_bench_interrupt(int signal_number) {
    g_bench_interrupt_requested = 1;
    g_bench_interrupt_signal = signal_number;
    // Forward to every currently-registered worker subprocess so they exit
    // promptly instead of running to completion while the parent is blocked
    // in waitpid(). kill() is async-signal-safe.
    for (std::size_t i = 0; i < kMaxBenchWorkers; ++i) {
        const pid_t worker_pid = static_cast<pid_t>(g_worker_pids[i]);
        if (worker_pid > 0) {
            kill(worker_pid, signal_number);
        }
    }
}

// --- Worker-side timeout handler -------------------------------------------
//
// When this process runs as a benchmark worker, the runner wraps it in
// `timeout --signal=TERM`. Without a handler, that SIGTERM discards every
// repetition completed so far. We cache the result-file path up front and, on
// SIGTERM, persist the best completed repetition (mirrored in g_partial_* by
// one_execution) using only async-signal-safe calls (open/write/close/_exit
// and hand-rolled integer formatting — no malloc, no stdio, no JSON lib).
char g_worker_result_path[4096] = {0};

void as_append_cstr(char *buf, std::size_t &pos, std::size_t cap, const char *s) {
    while (*s != '\0' && pos < cap) {
        buf[pos++] = *s++;
    }
}

void as_append_int(char *buf, std::size_t &pos, std::size_t cap, long value) {
    if (value < 0) {
        if (pos < cap) buf[pos++] = '-';
        value = -value;
    }
    char digits[24];
    int n = 0;
    if (value == 0) {
        digits[n++] = '0';
    }
    while (value > 0 && n < 24) {
        digits[n++] = static_cast<char>('0' + (value % 10));
        value /= 10;
    }
    while (n > 0 && pos < cap) {
        buf[pos++] = digits[--n];
    }
}

void as_append_int_field(char *buf, std::size_t &pos, std::size_t cap,
                         const char *key, long value) {
    as_append_cstr(buf, pos, cap, key);
    as_append_int(buf, pos, cap, value);
}

void handle_worker_timeout(int /*signal_number*/) {
    if (g_partial_has_result == 0 || g_worker_result_path[0] == '\0') {
        // Nothing completed yet — behave like a plain timeout (write nothing).
        _exit(124);
    }

    char buf[1024];
    std::size_t pos = 0;
    const std::size_t cap = sizeof(buf);
    as_append_cstr(buf, pos, cap,
                   "{\"status\":\"timeout_partial\",\"routing_steps\":");
    as_append_int(buf, pos, cap, g_partial_routing_steps);
    as_append_int_field(buf, pos, cap, ",\"completed_repetitions\":",
                        g_partial_completed_repetitions);
    if (g_partial_resolved_graph_x >= 0)
        as_append_int_field(buf, pos, cap, ",\"resolved_graph_x\":", g_partial_resolved_graph_x);
    if (g_partial_resolved_graph_y >= 0)
        as_append_int_field(buf, pos, cap, ",\"resolved_graph_y\":", g_partial_resolved_graph_y);
    if (g_partial_num_qubits >= 0)
        as_append_int_field(buf, pos, cap, ",\"num_qubits\":", g_partial_num_qubits);
    if (g_partial_max_interaction_degree >= 0)
        as_append_int_field(buf, pos, cap, ",\"max_interaction_degree\":", g_partial_max_interaction_degree);
    if (g_partial_resolved_n_magic >= 0)
        as_append_int_field(buf, pos, cap, ",\"resolved_number_of_magic_states\":", g_partial_resolved_n_magic);
    if (g_partial_non_routed_micro >= 0)
        as_append_int_field(buf, pos, cap, ",\"non_routed_layer_micro\":", g_partial_non_routed_micro);
    as_append_cstr(buf, pos, cap, "}\n");

    const int fd = open(g_worker_result_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd >= 0) {
        std::size_t off = 0;
        while (off < pos) {
            const ssize_t written = write(fd, buf + off, pos - off);
            if (written <= 0) break;
            off += static_cast<std::size_t>(written);
        }
        close(fd);
    }
    _exit(124);
}

// Spawn `/bin/sh -c "command"` and wait, exposing the worker PID to the signal
// handler via the worker registry. Returns the same integer std::system()
// would (waitpid-style status on success, -1 on spawn setup error).
//
// Uses posix_spawn() rather than fork()+exec(): the benchmark parent holds a
// multi-GB JSON DOM (all expanded cases), and a plain fork() of such a large
// address space is expensive and serializes on the kernel mm lock — which caps
// parallel scaling when many OpenMP threads spawn workers at once. glibc's
// posix_spawn() uses clone(CLONE_VM|CLONE_VFORK), so it does NOT copy the page
// tables and stays cheap regardless of parent size.
int spawn_worker_and_wait(const std::string &command) {
    // /bin/sh -c "command" keeps shell semantics (redirection, timeout
    // chaining, env prefix) intact, identical to the previous execl() child.
    char arg_sh[] = "sh";
    char arg_c[] = "-c";
    std::vector<char> cmd_buf(command.begin(), command.end());
    cmd_buf.push_back('\0');
    char *const argv[] = {arg_sh, arg_c, cmd_buf.data(), nullptr};

    pid_t pid = 0;
    const int spawn_rc =
        posix_spawn(&pid, "/bin/sh", nullptr, nullptr, argv, environ);
    if (spawn_rc != 0) {
        return -1;
    }
    register_worker_pid(pid);
    int status = 0;
    pid_t waited;
    do {
        waited = waitpid(pid, &status, 0);
    } while (waited == -1 && errno == EINTR);
    unregister_worker_pid(pid);
    if (waited == -1) {
        return -1;
    }
    return status;
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
        {"avg_parallelism", result.avg_parallelism},
        {"max_parallelism", result.max_parallelism}
    };

    if (result.resolved_graph_x >= 0 && result.resolved_graph_y >= 0) {
        payload["resolved_graph_x"] = result.resolved_graph_x;
        payload["resolved_graph_y"] = result.resolved_graph_y;
    }
    if (result.num_qubits >= 0) {
        payload["num_qubits"] = result.num_qubits;
    }
    if (result.max_interaction_degree >= 0) {
        payload["max_interaction_degree"] = result.max_interaction_degree;
    }
    if (result.non_routed_layer_pct >= 0.0) {
        payload["non_routed_layer_pct"] = result.non_routed_layer_pct;
    }
    if (result.resolved_number_of_magic_states >= 0) {
        payload["resolved_number_of_magic_states"] = result.resolved_number_of_magic_states;
    }
    if (result.min_routing_steps >= 0) {
        payload["min_routing_steps"] = result.min_routing_steps;
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
    if (payload.contains("max_parallelism") && payload.at("max_parallelism").is_number()) {
        result.max_parallelism = payload.at("max_parallelism").get<double>();
    }
    if (payload.contains("resolved_graph_x") && payload.at("resolved_graph_x").is_number_integer()) {
        result.resolved_graph_x = payload.at("resolved_graph_x").get<int>();
    }
    if (payload.contains("resolved_graph_y") && payload.at("resolved_graph_y").is_number_integer()) {
        result.resolved_graph_y = payload.at("resolved_graph_y").get<int>();
    }
    if (payload.contains("num_qubits") && payload.at("num_qubits").is_number_integer()) {
        result.num_qubits = payload.at("num_qubits").get<int>();
    }
    if (payload.contains("max_interaction_degree") && payload.at("max_interaction_degree").is_number_integer()) {
        result.max_interaction_degree = payload.at("max_interaction_degree").get<int>();
    }
    if (payload.contains("non_routed_layer_pct") && payload.at("non_routed_layer_pct").is_number()) {
        result.non_routed_layer_pct = payload.at("non_routed_layer_pct").get<double>();
    }
    if (payload.contains("resolved_number_of_magic_states") &&
        payload.at("resolved_number_of_magic_states").is_number_integer()) {
        result.resolved_number_of_magic_states = payload.at("resolved_number_of_magic_states").get<int>();
    }
    if (payload.contains("min_routing_steps") && payload.at("min_routing_steps").is_number_integer()) {
        result.min_routing_steps = payload.at("min_routing_steps").get<int>();
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
    } catch (const SafePassageException &e) {
        try_write_benchmark_error_file(e.what());
        std::cerr << "Safe Passage Error: " << e.what() << '\n';
        return 2;
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

    // As a benchmark worker, arm the timeout handler so a SIGTERM from the
    // runner's `timeout` persists the best completed repetition instead of
    // discarding the whole run. Cache the result-file path now (getenv in a
    // signal handler is not async-signal-safe).
    if (benchmark_worker_mode_enabled()) {
        const char *result_path = std::getenv(kBenchResultFileEnv);
        if (result_path != nullptr && *result_path != '\0') {
            std::strncpy(g_worker_result_path, result_path, sizeof(g_worker_result_path) - 1);
            g_worker_result_path[sizeof(g_worker_result_path) - 1] = '\0';
            std::signal(SIGTERM, handle_worker_timeout);
        }
    }

    std::string path = (std::filesystem::path(PROJECT_ROOT) / "qasms" / "example.qasm").string();
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
    double external_weight = 0.0;
    // CNOT-graph density below which CNOT-BFS mapping order is used (>= falls
    // back to the priority heap). Tuned to 0.70 post-fix (BFS beats heap almost
    // everywhere); configurable via JSON/CLI, env FTQC_BFS_DENSITY_THRESHOLD wins.
    double bfs_density_threshold = 0.70;
    // Direct, absolute gaussian sigma (stddev, same on both axes, graph-independent),
    // used verbatim by every gaussian. Replaced gaussian_confidence. Must be > 0;
    // sweep optimum ~0.4 in the coarse/connectivity regime.
    double gaussian_sigma = 0.4;
    // Anchored to PROJECT_ROOT, not the CWD: the old CWD-relative default
    // loaded the config from build/ but silently fell back to hardcoded
    // defaults when launched from anywhere else — a reproducibility trap.
    std::string config_path =
        (std::filesystem::path(PROJECT_ROOT) / "config" / "0_compiler_config.json").string();
    std::string graph_path = "";
    std::string magic_state_placement_strategy = "center_circle";
    int number_of_magic_states = -1;  // -1 = proportional to circuit (max_t_in_layer)
    double number_of_magic_states_multiplier = 0.0;
    double border_distance_percentage = 10.0;
    int x = 10;
    int y = 11;
    int dimension_offset = 0;  // signed delta on auto-computed grid (x<0 mode)
    std::string routing_strategy = "naive_critical";
    std::string t_routing_mode = "normal_t_routing";
    int patience_threshold = 3;
    bool use_layer_cache = true;
    bool metrics_only = false;
    int repetition_count = 1;
    bool use_layer_cache_explicit = false;
    double cnot_formula_scale = 1.0;
    double mapped_formula_scale = 1.0;
    bool packing_commute = false;  // commutation-aware frontier; only packing/critical_packing

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
        external_weight,
        bfs_density_threshold,
        gaussian_sigma,
        config_path,
        x,
        y,
        dimension_offset,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        number_of_magic_states_multiplier,
        border_distance_percentage,
        routing_strategy,
        t_routing_mode,
        patience_threshold,
        use_layer_cache,
        repetition_count,
        use_layer_cache_explicit,
        cnot_formula_scale,
        mapped_formula_scale,
        packing_commute
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
        external_weight,
        bfs_density_threshold,
        gaussian_sigma,
        x,
        y,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        number_of_magic_states_multiplier,
        border_distance_percentage,
        routing_strategy,
        t_routing_mode,
        patience_threshold,
        use_layer_cache,
        metrics_only,
        repetition_count,
        use_layer_cache_explicit,
        packing_commute
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
    std::cout << "EXTERNAL_WEIGHT: " << external_weight << std::endl;
    std::cout << "gaussian_sigma: " << gaussian_sigma << std::endl;
    std::cout << "bfs_density_threshold: " << bfs_density_threshold << std::endl;
    std::cout << "safe passage strategy: " << safe_passage_strategy << std::endl;
    std::cout << "MagicStatePlacementStrategy: " << magic_state_placement_strategy << std::endl;
    if (number_of_magic_states_multiplier > 0.0) {
        std::cout << "number_of_magic_states: qubits*" << number_of_magic_states_multiplier
                  << " (resolved at runtime)" << std::endl;
    } else if (number_of_magic_states == -1) {
        std::cout << "number_of_magic_states: proportional (max_t_in_layer, resolved at runtime)" << std::endl;
    } else {
        std::cout << "number_of_magic_states: " << number_of_magic_states << std::endl;
    }
    std::cout << "border_distance_percentage: " << border_distance_percentage << std::endl;
    std::cout << "routing strategy: " << routing_strategy << std::endl;
    std::cout << "packing_commute: " << (packing_commute ? "true" : "false") << std::endl;
    std::cout << "use_layer_cache: " << (use_layer_cache ? "true" : "false") << std::endl;
    std::cout << "metrics_only: " << (metrics_only ? "true" : "false") << std::endl;
    if (!graph_path.empty()) {
        std::cout << "graph path: " << graph_path << std::endl;
    } else {
        std::cout << "graph dimensions: " << x << "x" << y << std::endl;
        if (x < 0) {
            std::cout << "dimension_offset: " << dimension_offset << std::endl;
        }
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
        external_weight,
        bfs_density_threshold,
        gaussian_sigma,
        x,
        y,
        dimension_offset,
        graph_path,
        magic_state_placement_strategy,
        number_of_magic_states,
        number_of_magic_states_multiplier,
        border_distance_percentage,
        routing_strategy,
        t_routing_mode,
        patience_threshold,
        use_layer_cache,
        metrics_only,
        repetition_count,
        use_layer_cache_explicit,
        cnot_formula_scale,
        mapped_formula_scale,
        packing_commute
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

struct DimCsvEntry {
    int max_x = 0;
    int max_y = 0;
    int min_x = 0;
    int min_y = 0;
    std::string note;
};

static std::unordered_map<std::string, DimCsvEntry> load_dimensions_csv(const std::filesystem::path &path) {
    std::unordered_map<std::string, DimCsvEntry> map;
    std::ifstream f(path);
    if (!f.is_open()) return map;
    std::string line;
    std::getline(f, line); // skip header
    while (std::getline(f, line)) {
        if (line.empty()) continue;
        std::istringstream ss(line);
        std::string circuit, max_x, max_y, min_x, min_y, note;
        std::getline(ss, circuit, ',');
        std::getline(ss, max_x, ',');
        std::getline(ss, max_y, ',');
        std::getline(ss, min_x, ',');
        std::getline(ss, min_y, ',');
        std::getline(ss, note);
        if (circuit.empty()) continue;
        DimCsvEntry e;
        try { e.max_x = std::stoi(max_x); } catch (...) {}
        try { e.max_y = std::stoi(max_y); } catch (...) {}
        try { e.min_x = std::stoi(min_x); } catch (...) {}
        try { e.min_y = std::stoi(min_y); } catch (...) {}
        e.note = note;
        map[circuit] = e;
    }
    return map;
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

    // Each processor writes its OWN sidecar file (never a shared append) so
    // concurrent jobs on a networked filesystem can't corrupt each other's
    // lines; resume merges every per-processor file plus the legacy single file.
    const std::filesystem::path sidecar_dir = expanded_path.parent_path();
    const std::string sidecar_stem = expanded_path.stem().string();
    const std::filesystem::path sidecar_write_path =
        sidecar_dir / (sidecar_stem + ".p" + std::to_string(processor) + ".status.jsonl");

    const std::filesystem::path project_root(PROJECT_ROOT);
    const std::filesystem::path results_dir = project_root / "benchmarks" / "results";
    const std::unordered_map<std::string, DimCsvEntry> dim_csv =
        load_dimensions_csv(project_root / "config" / "dimensions.csv");
    std::filesystem::create_directories(results_dir);

    const std::string csv_file_name = sanitize_filename(bench_name) + "_runs.csv";
    const std::filesystem::path csv_path = results_dir / csv_file_name;
    write_csv::ensure_initialized(csv_path, write_csv::kBenchmarkRunsCsvHeader);

    // Purge stale "interrupted" rows left by a previous aborted run. Those cases
    // are re-executed by the resume logic (sidecar / expanded "executed" flag),
    // so the leftover rows carry no result and would otherwise pile up as
    // duplicates. Column 26 is the "status" field of the runs CSV.
    //
    // Only processor 0 purges: when a benchmark is split across several
    // processes they all share one CSV, and a single cleaner avoids N
    // concurrent full-file rewrites (it removes every processor's stale rows,
    // not just its own).
    if (processor == 0) {
        if (const std::size_t purged =
                write_csv::remove_rows_with_status(csv_path, 26, "interrupted");
            purged > 0) {
            std::cout << "Removed " << purged
                      << " stale interrupted CSV row(s) from a previous run.\n";
        }
    }

    int next_execution_id = write_csv::read_max_execution_id(csv_path) + 1;

    // Per-case worker config/result files are transient (written, read by the
    // worker subprocess, then removed). Default them to a local temp dir
    // (node-local on clusters) so thousands of tiny writes don't hammer shared
    // storage and serialize the parallel loop; BENCH_TMPDIR overrides. Falls
    // back to the bench dir only if no temp dir is usable.
    const std::filesystem::path runtime_dir = [&]() -> std::filesystem::path {
        std::error_code ec;
        if (const char *env = std::getenv("BENCH_TMPDIR"); env != nullptr && *env != '\0') {
            std::filesystem::path p(env);
            std::filesystem::create_directories(p, ec);
            if (!ec) {
                return p;
            }
        }
        const std::filesystem::path tmp = std::filesystem::temp_directory_path(ec);
        if (!ec && !tmp.empty()) {
            std::filesystem::create_directories(tmp, ec);
            if (!ec) {
                return tmp;
            }
        }
        return expanded_path.parent_path();
    }();

    auto persist_expanded = [&]() {
        // Write to a PID-unique temp then atomically rename, so when several
        // processes share this expanded file (one per --processor) a concurrent
        // persist can't leave it half-written. Last writer wins; the resume
        // truth lives in the sidecar, so a stale "executed" snapshot here is
        // harmless.
        const std::filesystem::path tmp_path =
            expanded_path.string() + ".tmp." + std::to_string(static_cast<long long>(::getpid()));
        {
            std::ofstream out(tmp_path);
            if (!out.is_open()) {
                throw std::runtime_error("Cannot write expanded bench file: " + tmp_path.string());
            }
            out << bench_data.dump(2) << '\n';
        }
        std::filesystem::rename(tmp_path, expanded_path);
    };

    const std::size_t total_cases = bench_data.size();

    // Sidecar: per-case execution state written as one JSONL line per case.
    // Replaces per-case persist_expanded() (was O(n) per case → O(n²) total).
    // Resume reads every per-processor sidecar plus the legacy single file.
    const std::unordered_map<std::size_t, SidecarStatus> sidecar =
        read_sidecar_status(sidecar_dir, sidecar_stem);
    std::ofstream sidecar_out(sidecar_write_path, std::ios::app);
    if (!sidecar_out.is_open()) {
        throw std::runtime_error("Cannot open sidecar status file: " + sidecar_write_path.string());
    }

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
        std::string case_id;
        int processor = 0;
        double timeout_seconds = -1.0;
        bool timeout_enabled = false;
        bool already_executed = false;
        bool timeout_reached_before = false;
        bool rerun_timeout_case = false;
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

        const auto is_sentinel_dim = [](const std::string &v) {
            if (v.empty()) return false;
            try {
                return std::stoi(v) <= 0;
            } catch (...) {
                return false;
            }
        };

        for (std::size_t i = 0; i < total_cases; ++i) {
            if (!bench_data.at(i).is_object()) {
                throw std::runtime_error("Bench entry " + std::to_string(i + 1) + " must be a JSON object.");
            }

            const json &entry = bench_data.at(i);
            BenchCasePlan plan;
            plan.index = i;
            plan.processor = parse_entry_processor(entry);
            plan.timeout_seconds = parse_timeout_seconds(entry);
            plan.timeout_enabled = plan.timeout_seconds >= 0.0;
            plan.case_id = get_json_field(entry, {"case_id"});
            if (plan.case_id.empty()) {
                plan.case_id = get_json_field(entry, {"id"});
            }
            {
                const auto sc_it = sidecar.find(i);
                if (sc_it != sidecar.end()) {
                    plan.already_executed      = sc_it->second.executed;
                    plan.timeout_reached_before = sc_it->second.timeout_reached;
                } else {
                    plan.already_executed =
                        entry.contains("executed") && entry["executed"].is_boolean() && entry["executed"].get<bool>();
                    plan.timeout_reached_before =
                        entry.contains("timeout_reached") &&
                        entry["timeout_reached"].is_boolean() &&
                        entry["timeout_reached"].get<bool>();
                }
            }
            plan.rerun_timeout_case = rerun_timeouts && plan.already_executed && plan.timeout_reached_before;

            const std::string plan_type = plan_field(entry, {"mapping_type", "type"});
            const std::string plan_safe_passage_strategy = plan_field(entry, {"safe_passage_strategy"});

            if (plan.processor != processor) {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] SKIP"
                    << " id=" << empty_to_dash(plan.case_id)
                    << " safe_passage_strategy=" << empty_to_dash(plan_safe_passage_strategy)
                    << " type=" << empty_to_dash(plan_type)
                    << " processor=" << plan.processor
                    << " selected_processor=" << processor << "\n";
            } else if (plan.already_executed && !plan.rerun_timeout_case) {
                std::cout
                    << "[" << (i + 1) << "/" << total_cases << "] SKIP"
                    << " id=" << empty_to_dash(plan.case_id)
                    << " safe_passage_strategy=" << empty_to_dash(plan_safe_passage_strategy)
                    << " type=" << empty_to_dash(plan_type)
                    << " executed=true\n";
            } else {
                if (plan.rerun_timeout_case) {
                    std::cout
                        << "[" << (i + 1) << "/" << total_cases << "] RERUN_TIMEOUT"
                        << " id=" << empty_to_dash(plan.case_id)
                        << " safe_passage_strategy=" << empty_to_dash(plan_safe_passage_strategy)
                        << " type=" << empty_to_dash(plan_type)
                        << " executed=true\n";
                }
                runnable_indices.push_back(i);
            }

            plans.push_back(std::move(plan));
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
            const json &entry = bench_data.at(plan.index);
            BenchCaseResult result;
            result.completed = true;
            result.index = plan.index;
            result.execution_id = execution_id;
            result.case_id = plan.case_id;
            result.status = "success";
            result.exit_code = 0;

            const auto format_pct = [](double value) {
                std::ostringstream ss;
                ss << std::fixed << std::setprecision(4) << value;
                return ss.str();
            };

            const auto start_tp = std::chrono::system_clock::now();
            const auto start_steady = std::chrono::steady_clock::now();
            const std::string run_date = format_now_date(start_tp);
            const std::string run_datetime = format_now_datetime(start_tp);

            const std::filesystem::path temp_config_path =
                runtime_dir /
                ("__bench_runtime_config_" + std::to_string(execution_id) + ".json");
            const std::filesystem::path temp_result_path =
                runtime_dir /
                ("__bench_runtime_result_" + std::to_string(execution_id) + ".json");

            const auto cleanup_temp = [&]() {
                std::error_code ec;
                std::filesystem::remove(temp_config_path, ec);
                std::filesystem::remove(temp_result_path, ec);
            };

            std::string routing_steps;
            std::string non_routed_pct;
            std::string avg_parallelism_str;
            std::string max_parallelism_str;
            std::string min_routing_steps_str;
            std::string error_excerpt;
            std::string resolved_graph_x;
            std::string resolved_graph_y;
            std::string resolved_n_magic;
            int resolved_num_qubits = -1;
            int resolved_max_degree = -1;
            const std::string planned_x = plan_field(entry, {"x", "graph_x"});
            const std::string planned_y = plan_field(entry, {"y", "graph_y"});
            if (!planned_x.empty() && !is_sentinel_dim(planned_x)) {
                resolved_graph_x = planned_x;
            }
            if (!planned_y.empty() && !is_sentinel_dim(planned_y)) {
                resolved_graph_y = planned_y;
            }

            // For dimension 0, look up upper/lower dims from dimensions.csv.
            // If the circuit is missing or has invalid dimensions, skip the run.
            const DimCsvEntry *dim_entry_ptr = nullptr;
            if (planned_x == "0") {
                const std::string circuit_key = get_json_field(entry, {"circuit"});
                const auto it = dim_csv.find(circuit_key);
                if (it == dim_csv.end()) {
                    result.status = "skipped";
                    result.mark_entry_as_executed = false;
                    std::cout << "dimensions.csv: no entry for circuit '" << circuit_key << "', skipping.\n";
                    return result;
                }
                dim_entry_ptr = &it->second;
                if (dim_entry_ptr->max_x <= 0 || dim_entry_ptr->max_y <= 0) {
                    result.status = "skipped";
                    result.mark_entry_as_executed = false;
                    std::cout << "dimensions.csv: circuit '" << circuit_key
                              << "' has zero/invalid upper dims (note: " << dim_entry_ptr->note << "), skipping.\n";
                    return result;
                }
            }

            try {
                json run_entry = entry;
                if (planned_x == "0" && dim_entry_ptr) {
                    run_entry["x"] = dim_entry_ptr->max_x;
                    run_entry["y"] = dim_entry_ptr->max_y;
                }

                std::ofstream temp_stream(temp_config_path);
                if (!temp_stream.is_open()) {
                    throw std::runtime_error("Cannot write temporary config: " + temp_config_path.string());
                }
                temp_stream << run_entry.dump(2) << '\n';
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
                        " > /dev/null 2>&1";
                } else {
                    command =
                        worker_env +
                        shell_quote(executable) +
                        " --config " + shell_quote(temp_config_path.string()) +
                        " > /dev/null 2>&1";
                }

                const int system_rc = spawn_worker_and_wait(command);
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
                } else if (result.timeout_reached || result.exit_code == 137) {
                    result.status = "timeout";
                    std::ostringstream timeout_ss;
                    timeout_ss << std::fixed << std::setprecision(3) << plan.timeout_seconds;
                    error_excerpt = "Execution exceeded timeout of " + timeout_ss.str() + "s";

                    // Recover the best completed repetition if the worker's
                    // timeout handler managed to persist it before being killed.
                    // The row stays status="timeout"; a populated routing_steps
                    // is the signal that a partial best was salvaged.
                    try {
                        if (std::filesystem::exists(temp_result_path)) {
                            const json partial = read_benchmark_worker_payload(temp_result_path);
                            if (partial.contains("routing_steps") &&
                                partial.at("routing_steps").is_number_integer()) {
                                routing_steps = std::to_string(partial.at("routing_steps").get<int>());
                                if (partial.contains("non_routed_layer_micro") &&
                                    partial.at("non_routed_layer_micro").is_number_integer()) {
                                    const double pct =
                                        partial.at("non_routed_layer_micro").get<long long>() / 1.0e6;
                                    if (pct >= 0.0) {
                                        non_routed_pct = format_pct(pct);
                                    }
                                }
                                if (partial.contains("resolved_graph_x") &&
                                    partial.at("resolved_graph_x").is_number_integer()) {
                                    resolved_graph_x = std::to_string(partial.at("resolved_graph_x").get<int>());
                                }
                                if (partial.contains("resolved_graph_y") &&
                                    partial.at("resolved_graph_y").is_number_integer()) {
                                    resolved_graph_y = std::to_string(partial.at("resolved_graph_y").get<int>());
                                }
                                if (partial.contains("num_qubits") &&
                                    partial.at("num_qubits").is_number_integer()) {
                                    resolved_num_qubits = partial.at("num_qubits").get<int>();
                                }
                                if (partial.contains("max_interaction_degree") &&
                                    partial.at("max_interaction_degree").is_number_integer()) {
                                    resolved_max_degree = partial.at("max_interaction_degree").get<int>();
                                }
                                if (partial.contains("resolved_number_of_magic_states") &&
                                    partial.at("resolved_number_of_magic_states").is_number_integer()) {
                                    resolved_n_magic =
                                        std::to_string(partial.at("resolved_number_of_magic_states").get<int>());
                                }
                                int completed = 0;
                                if (partial.contains("completed_repetitions") &&
                                    partial.at("completed_repetitions").is_number_integer()) {
                                    completed = partial.at("completed_repetitions").get<int>();
                                }
                                error_excerpt += " (saved best of " + std::to_string(completed) +
                                                 " completed repetition(s): routing_steps=" + routing_steps + ")";
                            }
                        }
                    } catch (const std::exception &) {
                        // No usable partial result; leave routing_steps empty.
                    }
                } else if (result.exit_code == 2) {
                    result.status = "safe_passage_failed";
                    const std::string worker_error = worker_error_from_result_file(temp_result_path);
                    error_excerpt = "Safe passage check failed";
                    if (!worker_error.empty()) {
                        error_excerpt += ": " + worker_error;
                    }
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
                    if (worker_result.non_routed_layer_pct >= 0.0) {
                        non_routed_pct = format_pct(worker_result.non_routed_layer_pct);
                    }
                    avg_parallelism_str = std::to_string(worker_result.avg_parallelism);
                    max_parallelism_str = std::to_string(worker_result.max_parallelism);
                    if (worker_result.min_routing_steps >= 0) {
                        min_routing_steps_str = std::to_string(worker_result.min_routing_steps);
                    }
                    if (worker_result.resolved_graph_x >= 0) {
                        resolved_graph_x = std::to_string(worker_result.resolved_graph_x);
                    }
                    if (worker_result.resolved_graph_y >= 0) {
                        resolved_graph_y = std::to_string(worker_result.resolved_graph_y);
                    }
                    resolved_num_qubits = worker_result.num_qubits;
                    resolved_max_degree = worker_result.max_interaction_degree;
                    if (worker_result.resolved_number_of_magic_states >= 0) {
                        resolved_n_magic = std::to_string(worker_result.resolved_number_of_magic_states);
                    }
                }
            } catch (const std::exception &e) {
                result.status = "failed";
                result.exit_code = 1;
                error_excerpt = e.what();
            }

            cleanup_temp();

            // ---- mid-dimension run (only when x == 0 and main run succeeded) ----
            // mid dims are auto-computed as (min+max)/2 so dimensions.csv stays unchanged.
            std::string mid_x_str;
            std::string mid_y_str;
            std::string mid_duration_str;
            std::string mid_routing_steps_str;
            std::string mid_status_str;
            std::string mid_non_routed_pct_str;

            if (planned_x == "0" && result.status == "success" && dim_entry_ptr != nullptr
                && dim_entry_ptr->min_x > 0 && dim_entry_ptr->min_y > 0
                && dim_entry_ptr->max_x > 0 && dim_entry_ptr->max_y > 0) {
                const int mid_dim_x = (dim_entry_ptr->min_x + dim_entry_ptr->max_x) / 2;
                const int mid_dim_y = (dim_entry_ptr->min_y + dim_entry_ptr->max_y) / 2;
                mid_x_str = std::to_string(mid_dim_x);
                mid_y_str = std::to_string(mid_dim_y);

                const std::filesystem::path temp_mid_config =
                    runtime_dir /
                    ("__bench_runtime_mid_config_" + std::to_string(execution_id) + ".json");
                const std::filesystem::path temp_mid_result =
                    runtime_dir /
                    ("__bench_runtime_mid_result_" + std::to_string(execution_id) + ".json");

                const auto cleanup_mid = [&]() {
                    std::error_code ec;
                    std::filesystem::remove(temp_mid_config, ec);
                    std::filesystem::remove(temp_mid_result, ec);
                };

                try {
                    json mid_entry = entry;
                    mid_entry["x"] = mid_dim_x;
                    mid_entry["y"] = mid_dim_y;

                    std::ofstream mid_stream(temp_mid_config);
                    if (!mid_stream.is_open()) {
                        throw std::runtime_error("Cannot write mid config: " + temp_mid_config.string());
                    }
                    mid_stream << mid_entry.dump(2) << '\n';
                    mid_stream.close();

                    std::error_code remove_ec;
                    std::filesystem::remove(temp_mid_result, remove_ec);

                    const std::string mid_worker_env =
                        "FTQC_BENCH_WORKER=1 FTQC_BENCH_RESULT_FILE=" +
                        shell_quote(temp_mid_result.string()) + " ";

                    std::string mid_cmd;
                    if (plan.timeout_enabled) {
                        std::ostringstream timeout_ss;
                        timeout_ss << std::fixed << std::setprecision(3) << plan.timeout_seconds;
                        mid_cmd =
                            mid_worker_env +
                            "timeout --signal=TERM --kill-after=1s " + timeout_ss.str() +
                            " " + shell_quote(executable) +
                            " --config " + shell_quote(temp_mid_config.string()) +
                            " > /dev/null 2>&1";
                    } else {
                        mid_cmd =
                            mid_worker_env +
                            shell_quote(executable) +
                            " --config " + shell_quote(temp_mid_config.string()) +
                            " > /dev/null 2>&1";
                    }

                    const auto mid_start = std::chrono::steady_clock::now();
                    const int mid_rc = spawn_worker_and_wait(mid_cmd);
                    const auto mid_end = std::chrono::steady_clock::now();
                    const int mid_exit = decode_system_exit_code(mid_rc);

                    const std::chrono::duration<double> mid_elapsed = mid_end - mid_start;
                    std::ostringstream mid_dur_ss;
                    mid_dur_ss << std::fixed << std::setprecision(6) << mid_elapsed.count();
                    mid_duration_str = mid_dur_ss.str();

                    if (mid_exit == 0) {
                        const benchmarkResult mid_worker =
                            benchmark_result_from_worker_payload(read_benchmark_worker_payload(temp_mid_result));
                        mid_routing_steps_str = std::to_string(mid_worker.routing_steps);
                        if (mid_worker.non_routed_layer_pct >= 0.0) {
                            mid_non_routed_pct_str = format_pct(mid_worker.non_routed_layer_pct);
                        }
                        mid_status_str = "success";
                    } else if (mid_exit == 2) {
                        mid_status_str = "safe_passage_failed";
                    } else if (mid_exit == 124) {
                        mid_status_str = "timeout";
                    } else {
                        mid_status_str = "failed";
                    }
                } catch (...) {}

                cleanup_mid();
            }
            // -----------------------------------------------------------------------

            // ---- lower-dimension run (only when x == 0 and main run succeeded) ----
            std::string lower_x_str;
            std::string lower_y_str;
            std::string lower_duration_str;
            std::string lower_routing_steps_str;
            std::string lower_status_str;
            std::string lower_non_routed_pct_str;

            if (planned_x == "0" && result.status == "success" && dim_entry_ptr != nullptr
                && dim_entry_ptr->min_x > 0 && dim_entry_ptr->min_y > 0) {
                const int lower_dim_x = dim_entry_ptr->min_x;
                const int lower_dim_y = dim_entry_ptr->min_y;
                lower_x_str = std::to_string(lower_dim_x);
                lower_y_str = std::to_string(lower_dim_y);

                const std::filesystem::path temp_lower_config =
                    runtime_dir /
                    ("__bench_runtime_lower_config_" + std::to_string(execution_id) + ".json");
                const std::filesystem::path temp_lower_result =
                    runtime_dir /
                    ("__bench_runtime_lower_result_" + std::to_string(execution_id) + ".json");

                const auto cleanup_lower = [&]() {
                    std::error_code ec;
                    std::filesystem::remove(temp_lower_config, ec);
                    std::filesystem::remove(temp_lower_result, ec);
                };

                try {
                    json lower_entry = entry;
                    lower_entry["x"] = lower_dim_x;
                    lower_entry["y"] = lower_dim_y;

                    std::ofstream lower_stream(temp_lower_config);
                    if (!lower_stream.is_open()) {
                        throw std::runtime_error("Cannot write lower config: " + temp_lower_config.string());
                    }
                    lower_stream << lower_entry.dump(2) << '\n';
                    lower_stream.close();

                    std::error_code remove_ec;
                    std::filesystem::remove(temp_lower_result, remove_ec);

                    const std::string lower_worker_env =
                        "FTQC_BENCH_WORKER=1 FTQC_BENCH_RESULT_FILE=" +
                        shell_quote(temp_lower_result.string()) + " ";

                    std::string lower_cmd;
                    if (plan.timeout_enabled) {
                        std::ostringstream timeout_ss;
                        timeout_ss << std::fixed << std::setprecision(3) << plan.timeout_seconds;
                        lower_cmd =
                            lower_worker_env +
                            "timeout --signal=TERM --kill-after=1s " + timeout_ss.str() +
                            " " + shell_quote(executable) +
                            " --config " + shell_quote(temp_lower_config.string()) +
                            " > /dev/null 2>&1";
                    } else {
                        lower_cmd =
                            lower_worker_env +
                            shell_quote(executable) +
                            " --config " + shell_quote(temp_lower_config.string()) +
                            " > /dev/null 2>&1";
                    }

                    const auto lower_start = std::chrono::steady_clock::now();
                    const int lower_rc = spawn_worker_and_wait(lower_cmd);
                    const auto lower_end = std::chrono::steady_clock::now();
                    const int lower_exit = decode_system_exit_code(lower_rc);

                    const std::chrono::duration<double> lower_elapsed = lower_end - lower_start;
                    std::ostringstream lower_dur_ss;
                    lower_dur_ss << std::fixed << std::setprecision(6) << lower_elapsed.count();
                    lower_duration_str = lower_dur_ss.str();

                    if (lower_exit == 0) {
                        const benchmarkResult lower_worker =
                            benchmark_result_from_worker_payload(read_benchmark_worker_payload(temp_lower_result));
                        lower_routing_steps_str = std::to_string(lower_worker.routing_steps);
                        if (lower_worker.non_routed_layer_pct >= 0.0) {
                            lower_non_routed_pct_str = format_pct(lower_worker.non_routed_layer_pct);
                        }
                        lower_status_str = "success";
                    } else if (lower_exit == 2) {
                        lower_status_str = "safe_passage_failed";
                    } else if (lower_exit == 124) {
                        lower_status_str = "timeout";
                    } else {
                        lower_status_str = "failed";
                    }
                } catch (...) {}

                cleanup_lower();
            }
            // -----------------------------------------------------------------------

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

            const std::string circuit = get_json_field(entry, {"circuit"});
            if (resolved_graph_x.empty() && !planned_x.empty() && !is_sentinel_dim(planned_x)) {
                resolved_graph_x = planned_x;
            }
            if (resolved_graph_y.empty() && !planned_y.empty() && !is_sentinel_dim(planned_y)) {
                resolved_graph_y = planned_y;
            }
            std::string circuit_graph_label = get_json_field(entry, {"circuit_graph_label"});
            if (circuit_graph_label.empty() && !circuit.empty() && !resolved_graph_x.empty() && !resolved_graph_y.empty()) {
                circuit_graph_label = circuit + "-" + resolved_graph_x + "x" + resolved_graph_y;
            }

            std::string routing_strategy_csv = get_json_field(
                entry,
                {"routing_strategy", "routing-strategy", "routing_method", "routing-method", "routing"}
            );
            if (routing_strategy_csv.empty()) {
                routing_strategy_csv = "naive_critical";
            }
            std::string t_routing_mode_csv = get_json_field(
                entry,
                {"t_routing_mode", "t-routing-mode"}
            );
            if (t_routing_mode_csv.empty()) {
                t_routing_mode_csv = "normal_t_routing";
            }

            const std::string mw = get_json_field(entry, {"MAPPED_GAUSSIAN_WEIGHT", "mapped_gaussian_weight"});
            const std::string bw = get_json_field(entry, {"BASE_GAUSSIAN_WEIGHT", "base_gaussian_weight"});
            const std::string mh = get_json_field(entry, {"MAGIC_HIGH", "magic_high"});
            const std::string ml = get_json_field(entry, {"MAGIC_LOW", "magic_low"});
            const std::string ch = get_json_field(entry, {"CNOT_HIGH", "cnot_high"});
            const std::string cl = get_json_field(entry, {"CNOT_LOW", "cnot_low"});
            const std::string ew = get_json_field(entry, {"EXTERNAL_WEIGHT", "external_weight"});
            const std::string gs = get_json_field(entry, {"GAUSSIAN_SIGMA", "gaussian_sigma"});
            const std::string mapping_type_csv = get_json_field(entry, {"mapping_type", "type"});
            const std::string safe_passage_strategy_csv = get_json_field(entry, {"safe_passage_strategy"});

            result.csv_row = {
                plan.case_id.empty() ? std::to_string(plan.index + 1) : plan.case_id,
                run_date,
                run_datetime,
                circuit,
                resolved_graph_x,
                resolved_graph_y,
                circuit_graph_label,
                mapping_type_csv,
                get_json_field(entry, {"magic_aware_strategy"}),
                get_json_field(entry, {"gaussian_strategy"}),
                mh,
                ml,
                ch,
                cl,
                mw,
                bw,
                gs,  // gaussian_sigma (column 16, replaced gaussian_confidence)
                safe_passage_strategy_csv,
                get_json_field(entry, {"magic_state_placement_strategy", "MagicStatePlacementStrategy"}),
                get_json_field(entry, {"border_distance_percentage"}),
                get_json_field(entry, {"number_of_magic_states"}),
                routing_strategy_csv,
                t_routing_mode_csv,
                get_json_field(entry, {"use_layer_cache", "use-layer-cache"}).empty() ? "true" : get_json_field(entry, {"use_layer_cache", "use-layer-cache"}),
                routing_steps,
                result.timeout_reached ? "true" : "false",
                result.status,
                std::to_string(result.exit_code),
                duration_ss.str(),
                "",
                limit_text(compact_line(error_excerpt), 300),
                mid_x_str,
                mid_y_str,
                mid_duration_str,
                mid_routing_steps_str,
                mid_status_str,
                lower_x_str,
                lower_y_str,
                lower_duration_str,
                lower_routing_steps_str,
                lower_status_str,
                non_routed_pct,
                mid_non_routed_pct_str,
                lower_non_routed_pct_str,
                resolved_n_magic,
                ew.empty() ? "0" : ew,
                avg_parallelism_str,
                max_parallelism_str,
                min_routing_steps_str
            };

            std::ostringstream progress;
            const auto append_progress_details = [&]() {
                progress
                    << " id=" << empty_to_dash(plan.case_id)
                    << " routing_steps=" << empty_to_dash(routing_steps)
                    << " non_routed_pct=" << empty_to_dash(non_routed_pct)
                    << " duration=" << duration_short_ss.str()
                    << " safe_passage_strategy=" << empty_to_dash(safe_passage_strategy_csv)
                    << " type=" << empty_to_dash(mapping_type_csv);
            };

            if (result.status == "success") {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] OK";
                append_progress_details();
            } else if (result.status == "timeout") {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] TIMEOUT";
                append_progress_details();
            } else if (result.status == "safe_passage_failed") {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] SAFE_PASSAGE_FAILED";
                append_progress_details();
                progress << " error=" << empty_to_dash(limit_text(compact_line(error_excerpt), 120));
            } else if (result.status == "interrupted") {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] INTERRUPTED";
                append_progress_details();
            } else {
                progress
                    << "[" << (plan.index + 1) << "/" << total_cases << "] FAIL";
                append_progress_details();
                progress << " error=" << empty_to_dash(limit_text(compact_line(error_excerpt), 120));
            }
            progress << "\n";
            result.progress_line = progress.str();

            return result;
        };

        std::atomic<int> next_execution_id_counter(next_execution_id);
        std::atomic<bool> fatal_error(false);
        std::string fatal_error_message;

        const long long runnable_count = static_cast<long long>(runnable_indices.size());

        // Flush the sidecar after every case so a hard kill (e.g. qdel sending
        // SIGKILL past its grace window) loses at most the single in-flight case,
        // which just re-runs on resume. flush() is a write() to the OS, not an
        // fsync, so it survives process death without touching the disk — cheap,
        // and dwarfed by the per-case write_csv::append_row() already done here.
        // Each processor owns its sidecar file, so this never contends across
        // jobs. (A final flush after the loop also covers the graceful path.)

        // Per-configuration timing summary (printed once at the end).
        const auto bench_loop_start = std::chrono::steady_clock::now();
        double total_case_seconds = 0.0;
        long long executed_case_count = 0;

#pragma omp parallel for schedule(dynamic, 1) if(runnable_count > 1)
        for (long long runnable_idx = 0; runnable_idx < runnable_count; ++runnable_idx) {
            if (fatal_error.load() || g_bench_interrupt_requested != 0) {
                continue;
            }

            const std::size_t plan_index = runnable_indices[static_cast<std::size_t>(runnable_idx)];
            const BenchCasePlan &plan = plans[plan_index];
            const int execution_id = next_execution_id_counter.fetch_add(1);
            const auto case_start = std::chrono::steady_clock::now();
            BenchCaseResult result = execute_case(plan, execution_id);
            const double case_seconds =
                std::chrono::duration<double>(std::chrono::steady_clock::now() - case_start).count();
            results[plan.index] = result;

#pragma omp critical(bench_commit)
            {
                total_case_seconds += case_seconds;
                ++executed_case_count;
                if (!fatal_error.load()) {
                    try {
                        bench_data.at(result.index)["executed"] = result.mark_entry_as_executed;
                        bench_data.at(result.index)["timeout_reached"] = result.timeout_reached;
                        sidecar_out
                            << json({{"i", result.index},
                                     {"e", result.mark_entry_as_executed},
                                     {"t", result.timeout_reached}}).dump()
                            << '\n';
                        sidecar_out.flush();
                        write_csv::append_row(csv_path, result.csv_row);
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

        sidecar_out.flush();

        if (executed_case_count > 0) {
            const double bench_loop_seconds =
                std::chrono::duration<double>(std::chrono::steady_clock::now() - bench_loop_start).count();
            std::cout << std::fixed << std::setprecision(2)
                      << "\n=== Timing summary ===\n"
                      << "configurations executed: " << executed_case_count << "\n"
                      << "average time per configuration: "
                      << (total_case_seconds / static_cast<double>(executed_case_count)) << " s\n"
                      << "total wall time (loop): " << bench_loop_seconds << " s\n";
        }

        if (fatal_error.load()) {
            throw std::runtime_error(fatal_error_message);
        }
    } catch (...) {
        restore_signal_handlers();
        throw;
    }

    // Write the expanded file once now that all cases are done.
    try { persist_expanded(); } catch (const std::exception &e) {
        std::cerr << "Warning: failed to persist expanded bench file: " << e.what() << '\n';
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
