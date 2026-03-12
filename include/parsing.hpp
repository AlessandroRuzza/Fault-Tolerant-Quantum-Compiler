#ifndef PARSING_HPP
#define PARSING_HPP

#include <string>

void print_usage(const char* executable);
void apply_config_overrides(int argc, char **argv, std::string& path, std::string& strategy, std::string& type, std::string& config_path);
void argument_parsing(int argc, char **argv, std::string& path, std::string& strategy, std::string& type);

#endif // PARSING_HPP
