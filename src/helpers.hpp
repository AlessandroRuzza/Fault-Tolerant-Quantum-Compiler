#pragma once

#include <chrono>
#include <cctype>
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

using json = nlohmann::json;


inline bool extract_bench_path_arg(int argc, char **argv, std::string &bench_path) {
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        
        if (arg == "--bench_path" || arg == "--bench-path" || arg == "--bench") {
            if (i + 1 >= argc) {
                throw std::runtime_error("Missing value for --bench_path");
            }
            bench_path = argv[i + 1];
            if (arg.rfind("--", 0) || arg.rfind("-", 0)) {
                throw std::runtime_error("Missing value for --bench_path");
            }
            return true;
        }
        
        
        std::string prefix = "--bench_path=";
        if (arg.rfind(prefix, 0) == 0) {
            bench_path = arg.substr(prefix.size());
            if (bench_path.empty()) {
                throw std::runtime_error("Missing value for --bench_path");
            }
            return true;
        }

        prefix = "--bench-path=";
        if (arg.rfind(prefix, 0) == 0) {
            bench_path = arg.substr(prefix.size());
            if (bench_path.empty()) {
                throw std::runtime_error("Missing value for --bench-path");
            }
            return true;
        }

        prefix = "--bench=";
        if (arg.rfind(prefix, 0) == 0) {
            bench_path = arg.substr(prefix.size());
            if (bench_path.empty()) {
                throw std::runtime_error("Missing value for --bench-path");
            }
            return true;
        }
    }

    return false;
}

inline bool extract_rerun_timeouts_arg(int argc, char **argv) {
    const auto parse_bool_value = [](std::string value) {
        for (char &c : value) {
            c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        }
        if (value == "1" || value == "true" || value == "yes" || value == "on") {
            return true;
        }
        if (value == "0" || value == "false" || value == "no" || value == "off") {
            return false;
        }
        throw std::runtime_error("Invalid value for --rerun-timeouts: " + value);
    };

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--rerun-timeouts" || arg == "--rerun_timeouts") {
            return true;
        }

        const std::string prefix_dash = "--rerun-timeouts=";
        if (arg.rfind(prefix_dash, 0) == 0) {
            return parse_bool_value(arg.substr(prefix_dash.size()));
        }

        const std::string prefix_underscore = "--rerun_timeouts=";
        if (arg.rfind(prefix_underscore, 0) == 0) {
            return parse_bool_value(arg.substr(prefix_underscore.size()));
        }
    }

    return false;
}

inline std::string extract_bench_name(const std::string &bench_path_arg) {
    std::filesystem::path p(bench_path_arg);
    if (p.has_extension()) {
        p = p.stem();
    }
    return p.filename().string();
}

inline bool env_flag_is_truthy(const char *name) {
    const char *raw_value = std::getenv(name);
    if (raw_value == nullptr || *raw_value == '\0') {
        return false;
    }

    std::string value(raw_value);
    for (char &c : value) {
        c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    }

    return value != "0" && value != "false" && value != "no" && value != "off";
}

inline bool benchmark_worker_mode_enabled() {
    return env_flag_is_truthy("FTQC_BENCH_WORKER");
}

inline bool benchmark_artifacts_enabled() {
    return !benchmark_worker_mode_enabled();
}


inline std::string format_now_date(const std::chrono::system_clock::time_point &tp) {
    const std::time_t tt = std::chrono::system_clock::to_time_t(tp);
    std::tm tm {};
#if defined(_WIN32)
    localtime_s(&tm, &tt);
#else
    localtime_r(&tt, &tm);
#endif
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d");
    return oss.str();
}

inline std::string format_now_datetime(const std::chrono::system_clock::time_point &tp) {
    const std::time_t tt = std::chrono::system_clock::to_time_t(tp);
    std::tm tm {};
#if defined(_WIN32)
    localtime_s(&tm, &tt);
#else
    localtime_r(&tt, &tm);
#endif
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d %H:%M:%S");
    return oss.str();
}

inline std::string sanitize_filename(std::string value) {
    for (char &c : value) {
        const unsigned char uc = static_cast<unsigned char>(c);
        if (!std::isalnum(uc) && c != '_' && c != '-' && c != '.') {
            c = '_';
        }
    }
    if (value.empty()) {
        value = "case";
    }
    return value;
}

inline std::string compact_line(std::string s) {
    for (char &c : s) {
        if (c == '\n' || c == '\r' || c == '\t') {
            c = ' ';
        }
    }
    return s;
}

inline std::string limit_text(const std::string &s, std::size_t max_len) {
    if (s.size() <= max_len) {
        return s;
    }
    return s.substr(0, max_len);
}

inline std::string empty_to_dash(const std::string &s) {
    return s.empty() ? "-" : s;
}

inline std::string json_value_to_string(const json &value) {
    if (value.is_null()) {
        return "";
    }
    if (value.is_string()) {
        return value.get<std::string>();
    }
    if (value.is_boolean()) {
        return value.get<bool>() ? "true" : "false";
    }
    if (value.is_number_integer() || value.is_number_unsigned()) {
        return std::to_string(value.get<long long>());
    }
    if (value.is_number_float()) {
        std::ostringstream oss;
        oss << std::setprecision(12) << value.get<double>();
        return oss.str();
    }
    return value.dump();
}

inline std::string get_json_field(const json &obj, const std::vector<std::string> &keys) {
    for (const std::string &key : keys) {
        if (obj.contains(key)) {
            return json_value_to_string(obj.at(key));
        }
    }
    return "";
}

class ScopedStreamRedirect {
public:
    ScopedStreamRedirect() : old_cout_(std::cout.rdbuf(buffer_.rdbuf())), old_cerr_(std::cerr.rdbuf(buffer_.rdbuf())) {}

    ~ScopedStreamRedirect() {
        std::cout.rdbuf(old_cout_);
        std::cerr.rdbuf(old_cerr_);
    }

    std::string str() const { return buffer_.str(); }

private:
    std::ostringstream buffer_;
    std::streambuf *old_cout_;
    std::streambuf *old_cerr_;
};
