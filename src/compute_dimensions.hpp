#include <stdlib.h>
#include <string.h>

int compute_dimensions(int num_qubits, std::string safe_passage_strategy, 
    int number_of_magic_states, std::string type)
{

    int dimension = std::sqrt((num_qubits + number_of_magic_states) * 3.5);
    if (safe_passage_strategy == "cube"){
        return dimension;
    }

    else if (safe_passage_strategy == "passage") {
        if (type == "homogeneous") {
            return static_cast<int>(std::round(dimension * 0.8));
        } else {
            return static_cast<int>(std::round(dimension * 0.8));
        }
    }

    return dimension;

}

