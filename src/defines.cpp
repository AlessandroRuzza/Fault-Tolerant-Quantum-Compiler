#include "defines.hpp"

#include <cctype>
#include <cstdlib>
#include <string>

namespace compiler_flags {

namespace {
// True when running as a benchmark worker (FTQC_BENCH_WORKER set to a truthy
// value). The parent process discards worker stdout, so every debug-print flag
// below is ANDed with kPrintAllowed and thereby forced off in that mode: the
// string formatting and O(N) graph scans behind these flags would otherwise
// inflate the timed mapping/routing regions for output nobody reads. Mirrors
// benchmark_worker_mode_enabled() in helpers.hpp, kept local to avoid pulling
// that heavy header (nlohmann/json) into this tiny translation unit.
bool bench_worker_mode() {
    const char* raw = std::getenv("FTQC_BENCH_WORKER");
    if (raw == nullptr || raw[0] == '\0') {
        return false;
    }
    std::string value(raw);
    for (char& c : value) {
        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    }
    return value != "0" && value != "false" && value != "no" && value != "off";
}
const bool kPrintAllowed = !bench_worker_mode();
} // namespace

// Debug-print flags. Each is ANDed with kPrintAllowed so it is automatically
// suppressed in benchmark-worker mode regardless of the value set here.
const bool PRINT_PARSING = kPrintAllowed && false;
const bool PRINT_CIRCUIT = kPrintAllowed && false;

const bool PRINT_MAPPING = kPrintAllowed && false;
const bool PRINT_MAPPING_GRAPH = kPrintAllowed && false;
const bool MAPPING_VERBOSE = kPrintAllowed && false;

const bool PRINT_SAFE_PASSAGE = kPrintAllowed && false;

const bool PRINT_LAYER = kPrintAllowed && false;
const bool PRINT_ROUTING = kPrintAllowed && false;
const bool PRINT_DRAW_ROUTING = kPrintAllowed && false;
const bool PRINT_ROUTING_PROGRESS = kPrintAllowed && false;

const bool PRINT_CACHE_METRICS = kPrintAllowed && false;
const bool PRINT_CIRCUIT_METRICS = kPrintAllowed && false;

/*
############ BEHAVIORAL FLAGS ######################
*/
const bool MAGIC_STOPS_ROUTE = true;
const bool USE_S_GATES = false;
const bool ORDER_GATES_BY_MANHATTAN = false;
const int LAYERING_LOOKAHEAD = 5;

const bool WRITE_UNIVERSAL_QASM = true;
const bool WRITE_GRAPH_FOR_WISQ = true;
const bool GRAPH_FOR_WISQ_USES_3x3_CUBE = true;

}
