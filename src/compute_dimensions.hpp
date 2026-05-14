#include <stdlib.h>
#include <string.h>

int compute_dimensions(int num_qubits, std::string safe_passage_strategy,
    int number_of_magic_states, std::string type, double border_distance_percentage,
    int max_interaction_degree = -1)
{
    // degree_ratio in [0,1]: 0=sparse, 1=fully connected.
    // Default 0.6 when unknown (gives multiplier ≈ 4.0, conservative mid-range).
    const float degree_ratio = (max_interaction_degree >= 0 && num_qubits > 0)
        ? static_cast<float>(max_interaction_degree) / num_qubits
        : 0.6f;
    const float multiplier = 3.5f + 0.8f * degree_ratio;
    float dimension = (num_qubits + number_of_magic_states) * multiplier;

    if (safe_passage_strategy == "cube") {
        double border = std::ceil((border_distance_percentage/100)*std::round(std::sqrt(dimension)));
        dimension = static_cast<int>(std::ceil(std::sqrt(dimension))) + 1;
        std::cout << "border: " << border << std::endl;
        return dimension;
    }

    else if (
        safe_passage_strategy == "passage" ||
        safe_passage_strategy == "passage_no_subgraphs" ||
        safe_passage_strategy == "connectivity"
    ) {
        if (type == "homogeneous") {
            dimension = dimension * 0.60;
        } else if (type == "gaussian") {
            dimension = dimension * 0.55;
        } else if (type == "magic_aware") {
            dimension = dimension * 0.60;
        }
    }

    return static_cast<int>(std::round(std::sqrt(dimension) * (1.1 + border_distance_percentage/100.0)));
}

inline int compute_upper_dimensions(int num_qubits, int max_interaction_degree = -1) {
    return compute_dimensions(num_qubits, "cube", num_qubits, "homogeneous", 5.0, max_interaction_degree);
}

inline int compute_lower_dimensions(int num_qubits, int max_interaction_degree = -1) {
    return compute_dimensions(num_qubits, "connectivity", num_qubits*0.1, "gaussian", 0.0, max_interaction_degree);
}
