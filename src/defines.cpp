#include "defines.hpp"

namespace compiler_flags {

const bool PRINT_PARSING = false;
const bool PRINT_CIRCUIT = false;

const bool PRINT_MAPPING = true;
const bool PRINT_MAPPING_GRAPH = true;
const bool MAPPING_VERBOSE = true;

const bool PRINT_SAFE_PASSAGE = true;

const bool PRINT_LAYER = false;
const bool PRINT_ROUTING = false;
const bool PRINT_DRAW_ROUTING = false;
const bool PRINT_ROUTING_PROGRESS = false;

/*
############ BEHAVIORAL FLAGS ######################
*/
const bool MAGIC_STOPS_ROUTE = true;
const bool USE_S_GATES = false;
const bool ORDER_GATES_BY_MANHATTAN = false;
const int LAYERING_LOOKAHEAD = 5;

const bool WRITE_UNIVERSAL_QASM = true;

}
