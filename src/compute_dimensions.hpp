#include <stdlib.h>
#include <string.h>

int compute_dimensions(int num_qubits, std::string safe_passage_strategy, 
    int number_of_magic_states, std::string type, double border_distance_percentage)
{

    float dimension = (num_qubits + number_of_magic_states) * 3.5;
    
    if (safe_passage_strategy == "cube"){
        //return dimension;
    }

    else if (safe_passage_strategy == "passage") {
        if (type == "homogeneous") {
            dimension = dimension * 0.7;
        } else if (type == "gaussian") {
            dimension = dimension * 0.65;
        } else if (type == "magic_aware") {
            dimension = dimension * 0.7;
        }
    }

    return static_cast<int>(std::round(std::sqrt(dimension) * (1.1 + border_distance_percentage/100.0)));
}

