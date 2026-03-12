#include "parsing.hpp"

#include "mapping.hpp"

#include <algorithm>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>

#include <nlohmann/json.hpp>

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

void validate_strategy(const std::string& value, const char* executable) {
    const std::vector<std::string> valid_strategies = Mapping::get_available_mapping_strategies();
    if (std::find(valid_strategies.begin(), valid_strategies.end(), value) == valid_strategies.end()) {
        std::cerr << "Invalid mapping strategy: " << value << "\n";
        print_usage(executable);
        throw std::runtime_error("Invalid mapping strategy: " + value);
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
    std::cout << "Usage: " << executable
              << " --circuit [circuit_name|circuit_name.qasm|full_path_to_qasm] "
              << "[--strategy [" << Mapping::available_mapping_strategies() << "]]\n"
              << "[--type [" << Mapping::available_mapping_types() << "]]\n"
              << "[--x <integer>]\n"
              << "[--y <integer>]\n"
              << "[--graph <graph_path>]\n"
              << "[--config <json_file_path>]\n"
              << "Configuration precedence:\n"
              << "  1) hardcoded defaults\n"
              << "  2) config file \n"
              << "  3) CLI options\n"
              << "   or: " << executable << " --help\n";
}

void apply_config_overrides(
    int argc,
    char **argv,
    std::string& path,
    std::string& strategy,
    std::string& type,
    std::string& config_path,
    int& x,
    int& y,
    std::string& graph_path
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

    if (config_json.contains("strategy")) {
        if (!config_json["strategy"].is_string()) {
            throw std::runtime_error("Config key 'strategy' must be a string");
        }
        strategy = config_json["strategy"].get<std::string>();
        validate_strategy(strategy, argv[0]);
    }

    if (config_json.contains("type")) {
        if (!config_json["type"].is_string()) {
            throw std::runtime_error("Config key 'type' must be a string");
        }
        type = config_json["type"].get<std::string>();
        validate_type(type, argv[0]);
    }

    if (config_json.contains("x")) {
        if (!config_json["x"].is_number_integer()) {
            throw std::runtime_error("Config key 'x' must be an integer");
        }
        x = config_json["x"].get<int>();
        if (x <= 0) {
            throw std::runtime_error("Config key 'x' must be > 0");
        }
    }

    if (config_json.contains("y")) {
        if (!config_json["y"].is_number_integer()) {
            throw std::runtime_error("Config key 'y' must be an integer");
        }
        y = config_json["y"].get<int>();
        if (y <= 0) {
            throw std::runtime_error("Config key 'y' must be > 0");
        }
    }

    if (config_json.contains("graph")) {
        if (!config_json["graph"].is_string()) {
            throw std::runtime_error("Config key 'graph' must be a string");
        }
        graph_path = resolve_config_graph_path(config_json["graph"].get<std::string>(), resolved_config_path);
    }
}

void argument_parsing(
    int argc,
    char **argv,
    std::string& path,
    std::string& strategy,
    std::string& type,
    int& x,
    int& y,
    std::string& graph_path
) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--help") {
            print_usage(argv[0]);
            exit(0);
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

        if (arg == "--strategy") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --strategy\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --strategy");
            }

            strategy = argv[++i];
            validate_strategy(strategy, argv[0]);
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

        if (arg == "--x") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --x\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --x");
            }
            x = parse_positive_integer(argv[++i], "--x");
            continue;
        }

        if (arg == "--y") {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for --y\n";
                print_usage(argv[0]);
                throw std::runtime_error("Missing value for --y");
            }
            y = parse_positive_integer(argv[++i], "--y");
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

        std::cerr << "Unknown option '" << arg << "'\n";
        print_usage(argv[0]);
        throw std::runtime_error("Unknown option: " + arg);
    }
}
