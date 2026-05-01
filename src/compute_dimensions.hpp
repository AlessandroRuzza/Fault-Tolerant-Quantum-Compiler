#include <stdlib.h>
#include <string.h>

int compute_dimensions(int num_qubits, std::string safe_passage_strategy, 
    int number_of_magic_states, std::string type, double border_distance_percentage)
{

    float dimension = (num_qubits + number_of_magic_states) * 3.5;

    if (safe_passage_strategy == "cube") {
        double border = std::ceil((border_distance_percentage/100)*std::round(std::sqrt(dimension)));
        dimension = static_cast<int>(std::round(std::sqrt(dimension)));
        if (border < 3) {
            dimension += 3;
        }
        std::cout << "border: " << border << std::endl;
        return dimension;
    }
    

    else if (
        safe_passage_strategy == "passage" ||
        safe_passage_strategy == "passage_no_subgraphs" ||
        safe_passage_strategy == "connectivity"
    ) {
        if (type == "homogeneous") {
            dimension = dimension * 0.7;
        } else if (type == "gaussian") {
            dimension = dimension * 0.65;
        } else if (type == "magic_aware") {
            dimension = dimension * 0.7;
        }
    }

    return static_cast<int>(std::round(std::sqrt(dimension)));



    //
}
