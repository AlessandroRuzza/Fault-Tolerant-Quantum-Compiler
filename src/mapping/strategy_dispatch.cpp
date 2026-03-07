#include "mapping.hpp"

#include <cctype>

namespace {
struct StrategyAlias {
    const char* alias;
    Mapping::MappingStrategy strategy;
};

constexpr StrategyAlias kStrategyAliases[] = {
    {"dist_first", Mapping::MappingStrategy::DISTANCE_FIRST},
    {"distance_first", Mapping::MappingStrategy::DISTANCE_FIRST},
    {"center_spaced", Mapping::MappingStrategy::CENTER_SPACED},
    {"random", Mapping::MappingStrategy::RANDOM},
};

constexpr const char* kCanonicalStrategies = "distance_first|center_spaced|random";
}  // namespace

Mapping::MappingStrategy Mapping::mapping_strategy = Mapping::MappingStrategy::DISTANCE_FIRST;

std::string Mapping::normalize_strategy_name(const std::string& strategy_name) {
    std::string normalized;
    normalized.reserve(strategy_name.size());

    for (char ch : strategy_name) {
        normalized.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
    }

    return normalized;
}

std::string Mapping::strategy_to_string(MappingStrategy strategy) {
    switch (strategy) {
        case MappingStrategy::DISTANCE_FIRST:
            return "distance_first";
        case MappingStrategy::CENTER_SPACED:
            return "center_spaced";
        case MappingStrategy::RANDOM:
            return "random";
        default:
            return "distance_first";
    }
}

bool Mapping::set_mapping_strategy(const std::string& strategy_name) {
    const std::string normalized_name = normalize_strategy_name(strategy_name);

    for (const StrategyAlias& alias : kStrategyAliases) {
        if (normalized_name == alias.alias) {
            mapping_strategy = alias.strategy;
            return true;
        }
    }

    return false;
}

std::string Mapping::current_mapping_strategy_name() {
    return strategy_to_string(mapping_strategy);
}

std::string Mapping::available_mapping_strategies() {
    return kCanonicalStrategies;
}

void Mapping::pseudo_random_mapping(Qubit* qubit, int second_qubit) {
    switch (mapping_strategy) {
        case MappingStrategy::CENTER_SPACED:
            center_spaced_mapping(qubit, second_qubit);
            return;
        case MappingStrategy::RANDOM:
            random_mapping(qubit, second_qubit);
            return;
        case MappingStrategy::DISTANCE_FIRST:
        default:
            distance_first_mapping(qubit, second_qubit);
            return;
    }
}
