#ifndef PARSING_HPP
#define PARSING_HPP

#include <string>

void print_usage(const char* executable);
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
    double& size_moltiplier,
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
);
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
    double& size_moltiplier,
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
);

#endif // PARSING_HPP
