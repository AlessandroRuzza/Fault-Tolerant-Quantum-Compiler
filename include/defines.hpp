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

/*
############ BEHAVIORAL FLAGS ######################
*/
extern const bool MAGIC_STOPS_ROUTE;
extern const bool USE_S_GATES;
extern const bool ORDER_GATES_BY_MANHATTAN;
extern const int LAYERING_LOOKAHEAD;

} 

// Keep existing unqualified names to avoid touching all call sites.
using namespace compiler_flags;

#endif // DEFINES_HPP