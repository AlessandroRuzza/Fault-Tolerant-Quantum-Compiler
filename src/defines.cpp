#include "defines.hpp"

namespace compiler_flags {

const bool PRINT_PARSING = false;
const bool PRINT_CIRCUIT = false;

const bool PRINT_MAPPING = false;
const bool PRINT_MAPPING_GRAPH = true;
const bool MAPPING_VERBOSE = false;

const bool PRINT_SAFE_PASSAGE = false;

const bool PRINT_LAYER = false;
const bool PRINT_ROUTING = false;
const bool PRINT_DRAW_ROUTING = true;
const bool PRINT_ROUTING_PROGRESS = false;

const bool PRINT_CACHE_METRICS = false; 
const bool PRINT_CIRCUIT_METRICS = false; 

/*
############ BEHAVIORAL FLAGS ######################
*/
const bool MAGIC_STOPS_ROUTE = true;
const bool USE_S_GATES = false;
const bool ORDER_GATES_BY_MANHATTAN = false;
const int LAYERING_LOOKAHEAD = 5;

const bool WRITE_UNIVERSAL_QASM = true;
const bool WRITE_GRAPH_FOR_WISQ = true;
const bool GRAPH_FOR_WISQ_USES_3x3_CUBE = true;

}
