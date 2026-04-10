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
    std::string& config_path,
    int& x,
    int& y,
    std::string& graph_path,
    std::string& magic_state_placement_strategy,
    int& number_of_magic_states,
    double& border_distance_percentage
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
    int& x,
    int& y,
    std::string& graph_path,
    std::string& magic_state_placement_strategy,
    int& number_of_magic_states,
    double& border_distance_percentage
);

#endif // PARSING_HPP
