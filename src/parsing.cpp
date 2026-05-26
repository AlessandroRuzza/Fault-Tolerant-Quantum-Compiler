#include "parsing.hpp"

#include "mapping.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

#include <nlohmann/json.hpp>

#ifndef FTOQC_HAS_BOOST_ROUTER
#define FTOQC_HAS_BOOST_ROUTER 0
#endif

namespace {

using json = nlohmann::json;


std::string resolve_cli_circuit_path(const std::string& circuit_arg) {
    std::filesystem::path candidate(circuit_arg);

    if (!candidate.has_extension()) {
        candidate += ".qasm";
    }

    if (!candidate.has_parent_path() && !candidate.is_absolute()) {
        std::filesystem::path root(PROJECT_ROOT);
        candidate = root / "qasms" / candidate;
    }

    return candidate.lexically_normal().string();
}

std::string resolve_cli_graph_path(const std::string& graph_arg) {
    std::filesystem::path candidate(graph_arg);

    if (!candidate.has_extension()) {
        candidate += ".json";
    }

    if (!candidate.has_parent_path() && !candidate.is_absolute()) {
        std::filesystem::path root(PROJECT_ROOT);
        candidate = root / "graphs" / candidate;
    }

    return candidate.lexically_normal().string();
}

std::string resolve_config_graph_path(
    const std::string& graph_arg,
    const std::filesystem::path& resolved_config_path
) {
    std::filesystem::path candidate(graph_arg);

    if (!candidate.has_extension()) {
        candidate += ".json";
    }

    if (!candidate.is_absolute()) {
        if (!candidate.has_parent_path()) {
            std::filesystem::path root(PROJECT_ROOT);
            candidate = root / "graphs" / candidate;
        } else {
            candidate = resolved_config_path.parent_path() / candidate;
        }
    }

    return candidate.lexically_normal().string();
}

int parse_positive_integer(const std::string& value, const char* flag_name) {
    int parsed_value = 0;
    try {
        parsed_value = std::stoi(value);
    } catch (const std::exception&) {
        throw std::runtime_error("Invalid integer value for " + std::string(flag_name) + ": " + value);
    }

    if (parsed_value <= 0) {
        throw std::runtime_error(std::string(flag_name) + " must be > 0");
    }

    return parsed_value;
}

bool is_effectively_integer(double value) {
    constexpr double kEpsilon = 1e-9;
    return std::fabs(value - std::round(value)) < kEpsilon;
}

void assign_magic_state_count_or_multiplier(
    double parsed_value,
    const std::string& source_name,
    int& number_of_magic_states,
    double& number_of_magic_states_multiplier,
    bool t_states_proportional = false
) {
    // When T_states_proportional is true, number_of_magic_states is computed
    // at runtime from the circuit; a placeholder value of 0 in the config is valid.
    if (t_states_proportional && parsed_value == 0.0) {
        number_of_magic_states = 0;
        number_of_magic_states_multiplier = 0.0;
        return;
    }

    if (!std::isfinite(parsed_value) || parsed_value <= 0.0) {
        throw std::runtime_error(source_name + " must be a finite number > 0");
    }

    if (is_effectively_integer(parsed_value)) {
        const double rounded = std::round(parsed_value);
        if (rounded > static_cast<double>(std::numeric_limits<int>::max())) {
            throw std::runtime_error(source_name + " is too large");
        }
        number_of_magic_states = static_cast<int>(rounded);
        number_of_magic_states_multiplier = 0.0;
        return;
    }

    number_of_magic_states_multiplier = parsed_value;
}

double parse_non_negative_double(const std::string& value, const char* flag_name) {
    double parsed_value = 0.0;
    try {
        parsed_value = std::stod(value);
    } catch (const std::exception&) {
        throw std::runtime_error("Invalid floating-point value for " + std::string(flag_name) + ": " + value);
    }

    if (!std::isfinite(parsed_value) || parsed_value < 0.0) {
        throw std::runtime_error(std::string(flag_name) + " must be a finite number >= 0");
    }

    return parsed_value;
}

double parse_finite_double(const std::string& value, const char* flag_name) {
    double parsed_value = 0.0;
    try {
        parsed_value = std::stod(value);
    } catch (const std::exception&) {
        throw std::runtime_error("Invalid floating-point value for " + std::string(flag_name) + ": " + value);
    }

    if (!std::isfinite(parsed_value)) {
        throw std::runtime_error(std::string(flag_name) + " must be a finite number");
    }

    return parsed_value;
}

double parse_gaussian_confidence(const std::string& value, const char* flag_name) {
    double parsed_value = 0.0;
    try {
        parsed_value = std::stod(value);
    } catch (const std::exception&) {
        throw std::runtime_error("Invalid floating-point value for " + std::string(flag_name) + ": " + value);
    }

    if (!std::isfinite(parsed_value) || parsed_value <= 0.0 || parsed_value >= 1.0) {
        throw std::runtime_error(std::string(flag_name) + " must be a finite number in (0, 1)");
    }

    return parsed_value;
}

double parse_percentage_0_100(const std::string& value, const char* flag_name) {
    const double parsed_value = parse_non_negative_double(value, flag_name);
    if (parsed_value > 100.0) {
        throw std::runtime_error(std::string(flag_name) + " must be <= 100");
    }
    return parsed_value;
}

std::string normalize_magic_state_placement_strategy(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    std::replace(value.begin(), value.end(), '-', '_');
    if (value == "passage_no_subgraph" || value == "no_subgraph" || value == "no_subgraphs" ) return "passage_no_subgraphs";
    return value;
}

std::string normalize_routing_method(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    std::replace(value.begin(), value.end(), '-', '_');
    if (value == "congestion_aware" || value == "congestionaware" ) return "congestion";
    if (value == "simple" ) return "naive";
    return value;
}

std::string normalize_t_routing_mode(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    std::replace(value.begin(), value.end(), '-', '_');
    return value;
}

void validate_routing_method(const std::string& value, const char* executable) {
    const std::string normalized = normalize_routing_method(value);
    const std::vector<std::string> valid_methods = {"congestion", "naive", "boost"};
    if (std::find(valid_methods.begin(), valid_methods.end(), normalized) == valid_methods.end()) {
        std::cerr << "Invalid routing method: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid routing method: " + value);
    }

#if !FTOQC_HAS_BOOST_ROUTER
    if (normalized == "boost") {
        std::cerr << "Routing method 'boost' requires Boost support, but this binary was built without Boost.\n";
        print_usage(executable);
        throw std::runtime_error("Routing method 'boost' requires Boost support");
    }
#endif
}

void validate_t_routing_mode(const std::string& value, const char* executable) {
    const std::string normalized = normalize_t_routing_mode(value);
    const std::vector<std::string> valid_modes = {"normal_t_routing", "smart_t_routing"};
    if (std::find(valid_modes.begin(), valid_modes.end(), normalized) == valid_modes.end()) {
        std::cerr << "Invalid t routing mode: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid t routing mode: " + value);
    }
}

void validate_magic_aware_strategy(const std::string& value, const char* executable) {
    const std::vector<std::string> valid_strategies = Mapping::get_available_mapping_strategies();
    if (std::find(valid_strategies.begin(), valid_strategies.end(), value) == valid_strategies.end()) {
        std::cerr << "Invalid magic-aware strategy: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid magic-aware strategy: " + value);
    }
}

void validate_type(const std::string& value, const char* executable) {
    const std::vector<std::string> valid_types = Mapping::get_available_mapping_types();
    if (std::find(valid_types.begin(), valid_types.end(), value) == valid_types.end()) {
        std::cerr << "Invalid mapping type: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid mapping type: " + value);
    }
}

void validate_gaussian_strategy(const std::string& value, const char* executable) {
    const std::vector<std::string> valid_strategies = Mapping::get_available_gaussian_strategies();
    if (std::find(valid_strategies.begin(), valid_strategies.end(), value) == valid_strategies.end()) {
        std::cerr << "Invalid gaussian strategy: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid gaussian strategy: " + value);
    }
}

void validate_safe_passage_strategy(const std::string& value, const char* executable) {
    const std::vector<std::string> valid_strategies = Mapping::get_available_safe_passage_strategies();
    if (std::find(valid_strategies.begin(), valid_strategies.end(), value) == valid_strategies.end()) {
        std::cerr << "Invalid safe passage strategy: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid safe passage strategy: " + value);
    }
}

void validate_magic_state_placement_strategy(std::string value, const char* executable) {
    value = normalize_magic_state_placement_strategy(std::move(value));
    if (value == "rightrow") {
        value = "right_row";
    }

    const std::vector<std::string> valid_strategies =
        Graph::get_available_magic_state_placement_strategies();
    if (std::find(valid_strategies.begin(), valid_strategies.end(), value) == valid_strategies.end()) {
        std::cerr << "Invalid MagicStatePlacementStrategy: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid MagicStatePlacementStrategy: " + value);
    }
}

std::filesystem::path extract_config_path(int argc, char **argv, std::string& config_path) {

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--help") {
            return config_path;
        }

        if (arg == "--config") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --config\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --config");
            }
            config_path = argv[++i];
        }
    }

    return config_path;
}

} // namespace

void print_usage(const char* executable) {
    std::cout << "Usage: " << executable << "\n"
              << "[--circuit [circuit_name|circuit_name.qasm|full_path_to_qasm]]\n"
              << "[--magic-aware-strategy [" << Mapping::available_mapping_strategies() << "]]\n"
              << "[--type [" << Mapping::available_mapping_types() << "]]\n"
              << "[--repetition <int>=1]\n"
              << "[--gaussian-strategy [" << Mapping::available_gaussian_strategies() << "]]\n"
              << "[--safe-passage [" << Mapping::available_safe_passage_strategies() << "]]\n"
              << "[--magic-state-placement-strategy [" << Graph::available_magic_state_placement_strategies() << "]]\n"
              << "[--number-of-magic-states <integer|float> >0]\n"
              << "[--border-distance-percentage <float> in [0,100]]\n"
              << "[--magic-high <float>=0]\n"
              << "[--magic-low <float>=0]\n"
              << "[--cnot-high <float>=0]\n"
              << "[--cnot-low <float>=0]\n"
              << "[--mapped-gaussian-weight <float>=0]\n"
              << "[--base-gaussian-weight <float>=0]\n"
              << "[--size-moltiplier <float> >=0, default=1]\n"
              << "[--gaussian-confidence <float> in (0,1), default=0.95]\n"
#if FTOQC_HAS_BOOST_ROUTER
              << "[--routing-strategy [congestion|naive|boost]]\n"
#else
              << "[--routing-strategy [congestion|naive]] (boost unavailable in this build)\n"
#endif
              << "[--t-routing-mode [normal_t_routing|smart_t_routing]]\n"
              << "[--patience-threshold <integer>=0]\n"
              << "[--x <integer>]\n"
              << "[--y <integer>]\n"
              << "[--graph <graph_path>]\n"
              << "[--config <json_file_path>]\n"
              << "Configuration precedence:\n"
              << "  1) CLI options\n"
              << "  2) config file \n"
              << "  3) hardcoded defaults\n"
              << "   or: " << executable << " --help\n";
}

void apply_config_overrides(
    int argc,
    char **argv,
    std::string& path,
    std::string& magic_aware_strategy,
    std::string& type,
    std::string& gaussian_strategy,
    std::string& safe_passage_strategy,
    double& magic_high,
    double& magic_low,
    double& cnot_high,
    double& cnot_low,
    double& mapped_gaussian_weight,
    double& base_gaussian_weight,
    double& gaussian_confidence,
    double& external_weight,
    std::string& config_path,
    int& x,
    int& y,
    std::string& graph_path,
    std::string& magic_state_placement_strategy,
    int& number_of_magic_states,
    double& number_of_magic_states_multiplier,
    double& border_distance_percentage,
    std::string& routing_method,
    std::string& t_routing_mode,
    int& patience_threshold,
    bool& use_layer_cache,
    int& repetition_count,
    bool& t_states_proportional
) {
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--help") {
            return;
        }
    }

    const std::filesystem::path resolved_config_path = extract_config_path(argc, argv, config_path);
    config_path = resolved_config_path.lexically_normal().string();

    if (!std::filesystem::exists(resolved_config_path)) {
        return;
    }

    std::ifstream config_stream(resolved_config_path);
    if (!config_stream) {
        throw std::runtime_error("Cannot open config file: " + resolved_config_path.string());
    }

    json config_json;
    config_stream >> config_json;
    if (!config_json.is_object()) {
        throw std::runtime_error("Config file must contain a JSON object: " + resolved_config_path.string());
    }

    const auto load_non_negative_double_from_config = [&](const char* key, double& target) {
        if (!config_json.contains(key)) {
            return false;
        }
        if (!config_json[key].is_number()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be numeric");
        }
        const double value = config_json[key].get<double>();
        if (!std::isfinite(value) || value < 0.0) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be a finite number >= 0");
        }
        target = value;
        return true;
    };

    if (config_json.contains("circuit")) {
        if (!config_json["circuit"].is_string()) {
            throw std::runtime_error("Config key 'circuit' must be a string");
        }

        const std::string circuit_arg = config_json["circuit"].get<std::string>();
        std::filesystem::path candidate(circuit_arg);

        if (!candidate.has_extension()) {
            candidate += ".qasm";
        }

        if (!candidate.is_absolute()) {
            if (!candidate.has_parent_path()) {
                std::filesystem::path root(PROJECT_ROOT);
                candidate = root / "qasms" / candidate;
            } else {
                candidate = resolved_config_path.parent_path() / candidate;
            }
        }

        path = candidate.lexically_normal().string();
    }

    if (config_json.contains("magic_aware_strategy")) {
        if (!config_json["magic_aware_strategy"].is_string()) {
            throw std::runtime_error("Config key 'magic_aware_strategy' must be a string");
        }
        magic_aware_strategy = config_json["magic_aware_strategy"].get<std::string>();
        validate_magic_aware_strategy(magic_aware_strategy, argv[0]);
    }

    if (config_json.contains("type")) {
        if (!config_json["type"].is_string()) {
            throw std::runtime_error("Config key 'type' must be a string");
        }
        type = config_json["type"].get<std::string>();
        validate_type(type, argv[0]);
    }

    if (config_json.contains("gaussian_strategy")) {
        if (!config_json["gaussian_strategy"].is_string()) {
            throw std::runtime_error("Config key 'gaussian_strategy' must be a string");
        }
        gaussian_strategy = config_json["gaussian_strategy"].get<std::string>();
        validate_gaussian_strategy(gaussian_strategy, argv[0]);
    }

    if (!load_non_negative_double_from_config("MAGIC_HIGH", magic_high)) {
        load_non_negative_double_from_config("magic_high", magic_high);
    }
    if (!load_non_negative_double_from_config("MAGIC_LOW", magic_low)) {
        load_non_negative_double_from_config("magic_low", magic_low);
    }
    if (!load_non_negative_double_from_config("CNOT_HIGH", cnot_high)) {
        load_non_negative_double_from_config("cnot_high", cnot_high);
    }
    if (!load_non_negative_double_from_config("CNOT_LOW", cnot_low)) {
        load_non_negative_double_from_config("cnot_low", cnot_low);
    }
    if (!load_non_negative_double_from_config("MAPPED_GAUSSIAN_WEIGHT", mapped_gaussian_weight)) {
        load_non_negative_double_from_config("mapped_gaussian_weight", mapped_gaussian_weight);
    }
    if (!load_non_negative_double_from_config("BASE_GAUSSIAN_WEIGHT", base_gaussian_weight)) {
        load_non_negative_double_from_config("base_gaussian_weight", base_gaussian_weight);
    }
    const auto load_finite_double_from_config = [&](const char* key, double& target) {
        if (!config_json.contains(key)) {
            return false;
        }
        if (!config_json[key].is_number()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be numeric");
        }
        const double value = config_json[key].get<double>();
        if (!std::isfinite(value)) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be a finite number");
        }
        target = value;
        return true;
    };
    if (!load_finite_double_from_config("EXTERNAL_WEIGHT", external_weight)) {
        load_finite_double_from_config("external_weight", external_weight);
    }

    const auto load_gaussian_confidence_from_config = [&](const char* key) {
        if (!config_json.contains(key)) {
            return false;
        }
        if (!config_json[key].is_number()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be numeric");
        }
        const double value = config_json[key].get<double>();
        if (!std::isfinite(value) || value <= 0.0 || value >= 1.0) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be a finite number in (0, 1)");
        }
        gaussian_confidence = value;
        return true;
    };

    if (!load_gaussian_confidence_from_config("GAUSSIAN_CONFIDENCE")) {
        load_gaussian_confidence_from_config("gaussian_confidence");
    }

    if (config_json.contains("safe_passage_strategy")) {
        if (!config_json["safe_passage_strategy"].is_string()) {
            throw std::runtime_error("Config key 'safe_passage_strategy' must be a string");
        }
        const std::string configured_safe_passage_strategy =
            config_json["safe_passage_strategy"].get<std::string>();
        validate_safe_passage_strategy(configured_safe_passage_strategy, argv[0]);
        safe_passage_strategy = configured_safe_passage_strategy;
    }

    const auto set_magic_state_placement_strategy_from_config = [&](const char* key) {
        if (!config_json.contains(key)) {
            return false;
        }
        if (!config_json[key].is_string()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be a string");
        }
        std::string parsed_strategy = config_json[key].get<std::string>();
        parsed_strategy = normalize_magic_state_placement_strategy(parsed_strategy);
        if (parsed_strategy == "rightrow") {
            parsed_strategy = "right_row";
        }
        validate_magic_state_placement_strategy(parsed_strategy, argv[0]);
        magic_state_placement_strategy = parsed_strategy;
        return true;
    };

    if (!set_magic_state_placement_strategy_from_config("MagicStatePlacementStrategy")) {
        set_magic_state_placement_strategy_from_config("magic_state_placement_strategy");
    }

    if (config_json.contains("T_states_proportional") || config_json.contains("t_states_proportional")) {
        const char* key = config_json.contains("T_states_proportional") ? "T_states_proportional" : "t_states_proportional";
        if (!config_json[key].is_boolean()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be a boolean");
        }
        t_states_proportional = config_json[key].get<bool>();
    }

    const auto set_number_of_magic_states_from_config = [&](const char* key) {
        if (!config_json.contains(key)) {
            return false;
        }
        if (!config_json[key].is_number()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be numeric");
        }
        const double parsed_value = config_json[key].get<double>();
        assign_magic_state_count_or_multiplier(
            parsed_value,
            std::string("Config key '") + key + "'",
            number_of_magic_states,
            number_of_magic_states_multiplier,
            t_states_proportional
        );
        return true;
    };

    if (!set_number_of_magic_states_from_config("number_of_magic_states")) {
        set_number_of_magic_states_from_config("NumberOfMagicStates");
    }

    const auto set_border_distance_percentage_from_config = [&](const char* key) {
        if (!config_json.contains(key)) {
            return false;
        }
        if (!config_json[key].is_number()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be numeric");
        }
        const double parsed_value = config_json[key].get<double>();
        if (!std::isfinite(parsed_value) || parsed_value < 0.0 || parsed_value > 100.0) {
            throw std::runtime_error(
                std::string("Config key '") + key + "' must be a finite number in [0,100]"
            );
        }
        border_distance_percentage = parsed_value;
        return true;
    };

    if (!set_border_distance_percentage_from_config("border_distance_percentage")) {
        set_border_distance_percentage_from_config("BorderDistancePercentage");
    }

    // Sentinels: x>0 explicit; 0 -> low/mid/high from dimensions.csv;
    // -n (n>=1) -> compute_dimensions(...) + (n-1).
    if (config_json.contains("x")) {
        if (!config_json["x"].is_number_integer()) {
            throw std::runtime_error("Config key 'x' must be an integer");
        }
        x = config_json["x"].get<int>();
    }

    if (config_json.contains("y")) {
        if (!config_json["y"].is_number_integer()) {
            throw std::runtime_error("Config key 'y' must be an integer");
        }
        y = config_json["y"].get<int>();
    }

    if (config_json.contains("graph")) {
        if (!config_json["graph"].is_string()) {
            throw std::runtime_error("Config key 'graph' must be a string");
        }
        graph_path = resolve_config_graph_path(config_json["graph"].get<std::string>(), resolved_config_path);
    }

    if (config_json.contains("routing_strategy") || config_json.contains("routing-strategy")) {
        const std::string rm = config_json.contains("routing_strategy") ?
            config_json["routing_strategy"].get<std::string>() :
            config_json["routing-strategy"].get<std::string>();
        std::string normalized = normalize_routing_method(rm);
        validate_routing_method(normalized, argv[0]);
        routing_method = normalized;
    }
    else if (config_json.contains("routing")) {
        const std::string rm = config_json["routing"].get<std::string>();
        std::string normalized = normalize_routing_method(rm);
        validate_routing_method(normalized, argv[0]);
        routing_method = normalized;
    }
    else if (config_json.contains("routing_method") || config_json.contains("routing-method")) {
        const std::string rm = config_json.contains("routing_method") ?
            config_json["routing_method"].get<std::string>() :
            config_json["routing-method"].get<std::string>();
        std::string normalized = normalize_routing_method(rm);
        validate_routing_method(normalized, argv[0]);
        routing_method = normalized;
    }

    if (config_json.contains("t_routing_mode") || config_json.contains("t-routing-mode")) {
        const std::string configured_mode = config_json.contains("t_routing_mode") ?
            config_json["t_routing_mode"].get<std::string>() :
            config_json["t-routing-mode"].get<std::string>();
        t_routing_mode = normalize_t_routing_mode(configured_mode);
        validate_t_routing_mode(t_routing_mode, argv[0]);
    }

    if (config_json.contains("patience_threshold") || config_json.contains("patience-threshold")) {
        const char* key = config_json.contains("patience_threshold") ? "patience_threshold" : "patience-threshold";
        if (!config_json[key].is_number_integer()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be an integer");
        }
        patience_threshold = config_json[key].get<int>();
        if (patience_threshold < 0) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be >= 0");
        }
    }

    if (config_json.contains("use_layer_cache") || config_json.contains("use-layer-cache")) {
        const char* key = config_json.contains("use_layer_cache") ? "use_layer_cache" : "use-layer-cache";
        if (!config_json[key].is_boolean()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be a boolean");
        }
        use_layer_cache = config_json[key].get<bool>();
    }

    if (config_json.contains("repetition") || config_json.contains("random_repetition") || config_json.contains("random-repetition")) {
        const char* key = config_json.contains("repetition") ? "repetition" : config_json.contains("random_repetition") ? "random_repetition" : "random-repetition";
        if (!config_json[key].is_number_integer()) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be a boolean");
        }
        repetition_count = config_json[key].get<int>();
        if (repetition_count <= 0) {
            throw std::runtime_error(std::string("Config key '") + key + "' must be > 0");
        }
    }

}

void argument_parsing(
    int argc,
    char **argv,
    std::string& path,
    std::string& magic_aware_strategy,
    std::string& type,
    std::string& gaussian_strategy,
    std::string& safe_passage_strategy,
    double& magic_high,
    double& magic_low,
    double& cnot_high,
    double& cnot_low,
    double& mapped_gaussian_weight,
    double& base_gaussian_weight,
    double& gaussian_confidence,
    double& external_weight,
    int& x,
    int& y,
    std::string& graph_path,
    std::string& magic_state_placement_strategy,
    int& number_of_magic_states,
    double& number_of_magic_states_multiplier,
    double& border_distance_percentage,
    std::string& routing_method,
    std::string& t_routing_mode,
    int& patience_threshold,
    bool& use_layer_cache,
    bool& metrics_only,
    int& repetition
) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--help") {
            print_usage(argv[0]);
            exit(0);
        }

        if (arg == "--metrics-only") {
            metrics_only = true;
            continue;
        }

        if (arg == "--config") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --config\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --config");
            }
            ++i;
            continue;
        }

        if (arg == "--circuit") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --circuit\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --circuit");
            }
            path = resolve_cli_circuit_path(argv[++i]);
            continue;
        }

        if (arg == "--magic-aware-strategy" || arg == "--magic_aware_strategy") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --magic-aware-strategy\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --magic-aware-strategy");
            }

            magic_aware_strategy = argv[++i];
            validate_magic_aware_strategy(magic_aware_strategy, argv[0]);
            continue;
        }

        if (arg == "--type") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --type\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --type");
            }
            type = argv[++i];
            validate_type(type, argv[0]);
            continue;
        }

        if (arg == "--gaussian-strategy" || arg == "--gaussian_strategy") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --gaussian-strategy\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --gaussian-strategy");
            }
            gaussian_strategy = argv[++i];
            validate_gaussian_strategy(gaussian_strategy, argv[0]);
            continue;
        }

        if (arg == "--magic-high" || arg == "--magic_high") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --magic-high\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --magic-high");
            }
            magic_high = parse_non_negative_double(argv[++i], "--magic-high");
            continue;
        }

        if (arg == "--magic-low" || arg == "--magic_low") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --magic-low\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --magic-low");
            }
            magic_low = parse_non_negative_double(argv[++i], "--magic-low");
            continue;
        }

        if (arg == "--cnot-high" || arg == "--cnot_high") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --cnot-high\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --cnot-high");
            }
            cnot_high = parse_non_negative_double(argv[++i], "--cnot-high");
            continue;
        }

        if (arg == "--cnot-low" || arg == "--cnot_low") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --cnot-low\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --cnot-low");
            }
            cnot_low = parse_non_negative_double(argv[++i], "--cnot-low");
            continue;
        }

        if (arg == "--mapped-gaussian-weight" || arg == "--mapped_gaussian_weight") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --mapped-gaussian-weight\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --mapped-gaussian-weight");
            }
            mapped_gaussian_weight = parse_non_negative_double(argv[++i], "--mapped-gaussian-weight");
            continue;
        }

        if (arg == "--base-gaussian-weight" || arg == "--base_gaussian_weight") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --base-gaussian-weight\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --base-gaussian-weight");
            }
            base_gaussian_weight = parse_non_negative_double(argv[++i], "--base-gaussian-weight");
            continue;
        }

        if (arg == "--external-weight" || arg == "--external_weight") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --external-weight\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --external-weight");
            }
            external_weight = parse_finite_double(argv[++i], "--external-weight");
            continue;
        }

        if (arg == "--gaussian-confidence" || arg == "--gaussian_confidence") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --gaussian-confidence\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --gaussian-confidence");
            }
            gaussian_confidence = parse_gaussian_confidence(argv[++i], "--gaussian-confidence");
            continue;
        }

        if (arg == "--safe-passage") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --safe-passage\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --safe-passage");
            }
            const std::string cli_safe_passage_strategy = argv[++i];
            validate_safe_passage_strategy(cli_safe_passage_strategy, argv[0]);
            safe_passage_strategy = cli_safe_passage_strategy;
            continue;
        }

        if (arg == "--magic-state-placement-strategy" ||
            arg == "--magic_state_placement_strategy" ||
            arg == "--MagicStatePlacementStrategy") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --magic-state-placement-strategy\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --magic-state-placement-strategy");
            }
            magic_state_placement_strategy = normalize_magic_state_placement_strategy(argv[++i]);
            if (magic_state_placement_strategy == "rightrow") {
                magic_state_placement_strategy = "right_row";
            }
            validate_magic_state_placement_strategy(magic_state_placement_strategy, argv[0]);
            continue;
        }

        if (arg == "--number-of-magic-states" ||
            arg == "--number_of_magic_states" ||
            arg == "--NumberOfMagicStates") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --number-of-magic-states\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --number-of-magic-states");
            }
            const double parsed_value = parse_non_negative_double(argv[++i], "--number-of-magic-states");
            assign_magic_state_count_or_multiplier(
                parsed_value,
                "--number-of-magic-states",
                number_of_magic_states,
                number_of_magic_states_multiplier
            );
            continue;
        }

        if (arg == "--border-distance-percentage" ||
            arg == "--border_distance_percentage" ||
            arg == "--BorderDistancePercentage") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --border-distance-percentage\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --border-distance-percentage");
            }
            border_distance_percentage = parse_percentage_0_100(argv[++i], "--border-distance-percentage");
            continue;
        }

        if (arg == "--x") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --x\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --x");
            }
            // -1 means compute from circuit dimensions
            if (x != -1) {
                x = parse_positive_integer(argv[++i], "--x");
            }
            continue;
        }

        if (arg == "--y") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --y\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --y");
            }
            // -1 means compute from circuit dimensions
            if (y != -1) {
                y = parse_positive_integer(argv[++i], "--y");
            }
            continue;
        }

        if (arg == "--graph") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --graph\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --graph");
            }
            graph_path = resolve_cli_graph_path(argv[++i]);
            continue;
        }

        if (arg == "--routing-strategy" || arg == "--routing_strategy" || arg == "--routing-method" || arg == "--routing_method" || arg == "--routing" ) {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --routing-strategy\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --routing-strategy");
            }
            routing_method = normalize_routing_method(argv[++i]);
            validate_routing_method(routing_method, argv[0]);
            continue;
        }

        if (arg == "--t-routing-mode" || arg == "--t_routing_mode") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --t-routing-mode\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --t-routing-mode");
            }
            t_routing_mode = normalize_t_routing_mode(argv[++i]);
            validate_t_routing_mode(t_routing_mode, argv[0]);
            continue;
        }

        if (arg == "--patience-threshold" || arg == "--patience_threshold") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --patience-threshold\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --patience-threshold");
            }
            try {
                patience_threshold = std::stoi(argv[++i]);
            } catch (const std::exception&) {
                throw std::runtime_error("Invalid integer value for --patience-threshold: " + std::string(argv[i]));
            }
            if (patience_threshold < 0) {
                throw std::runtime_error("--patience-threshold must be >= 0");
            }
            continue;
        }

        if (arg == "--use-layer-cache" || arg == "--use_layer_cache") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --use-layer-cache\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --use-layer-cache");
            }
            const std::string val = argv[++i];
            if (val == "true" || val == "1") {
                use_layer_cache = true;
            } else if (val == "false" || val == "0") {
                use_layer_cache = false;
            } else {
                throw std::runtime_error("Invalid boolean value for --repetition: " + val);
            }
            
            continue;
        }
        
        if (arg == "--repetition" || arg == "--random_repetition" || arg == "--random-repetition"|| arg == "--repeat" || arg == "--rep") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --repetition\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --repetition");
            }
            try {
                repetition = std::stoi(argv[++i]);
            } catch (const std::exception&) {
                throw std::runtime_error("Invalid integer value for --repetition: " + std::string(argv[i]));
            }
            if (repetition <= 0) {
                throw std::runtime_error("--repetition must be > 0");
            }
            continue;
        }

        std::cerr << "Unknown option '" << arg << "'\n";
        print_usage(argv[0]);
        throw std::runtime_error("Unknown option: " + arg);
    }
}
