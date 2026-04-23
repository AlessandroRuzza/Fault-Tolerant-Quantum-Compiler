#ifndef DEFINES_HPP
#define DEFINES_HPP

namespace compiler_flags {

extern const bool PRINT_PARSING; // controls QASM parsing printing
extern const bool PRINT_CIRCUIT; // controls circuit printing

extern const bool PRINT_MAPPING; // controls mapping steps printing
extern const bool PRINT_MAPPING_GRAPH; // controls mapping graph printing
extern const bool MAPPING_VERBOSE; // controls verbose mapping logs

extern const bool PRINT_SAFE_PASSAGE; // controls safe passage checking printing

extern const bool PRINT_LAYER; // controls layered circuit printing
extern const bool PRINT_ROUTING; // controls routing steps printing
extern const bool PRINT_DRAW_ROUTING; // controls routing lattice drawing printing
extern const bool PRINT_ROUTING_PROGRESS; // controls routing progress printing

extern const bool MAGIC_STOPS_ROUTE;
extern const bool USE_S_GATES;

} // namespace compiler_flags

// Keep existing unqualified names to avoid touching all call sites.
using namespace compiler_flags;

// using compiler_flags::PRINT_PARSING;
// using compiler_flags::PRINT_CIRCUIT;
// using compiler_flags::PRINT_MAPPING;
// using compiler_flags::PRINT_MAPPING_GRAPH;
// using compiler_flags::MAPPING_VERBOSE;
// using compiler_flags::PRINT_SAFE_PASSAGE;
// using compiler_flags::PRINT_LAYER;
// using compiler_flags::PRINT_ROUTING;
// using compiler_flags::PRINT_DRAW_ROUTING;
// using compiler_flags::PRINT_ROUTING_PROGRESS;
// using compiler_flags::MAGIC_STOPS_ROUTE;
// using compiler_flags::USE_S_GATES;

#endif // DEFINES_HPP