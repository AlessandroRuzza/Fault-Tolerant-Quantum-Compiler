#include <cmath>
#include <limits>
#include <stdexcept>

inline double compute_sigma(int radius, double gaussian_confidence) {
    if (!std::isfinite(gaussian_confidence) || gaussian_confidence <= 0.0 || gaussian_confidence >= 1.0) {
        throw std::invalid_argument("gaussian_confidence must be a finite number in (0, 1)");
    }
    return radius / std::sqrt(-2 * std::log(1 - gaussian_confidence));
}


namespace Gaussians {

    inline int scaled_gaussian_size(int base_size, double size_moltiplier) {
        if (!std::isfinite(size_moltiplier) || size_moltiplier < 0.0) {
            throw std::invalid_argument("size_moltiplier must be a finite number >= 0");
        }

        const double scaled = std::ceil(static_cast<double>(base_size) * size_moltiplier);
        if (scaled > static_cast<double>(std::numeric_limits<int>::max())) {
            throw std::overflow_error("scaled gaussian size is too large");
        }

        if (scaled < 1.0) {
            return 1;
        }

        return static_cast<int>(scaled);
    }

    Gaussian baseline_gaussian(const Graph& graph, double base_gaussian_weight, double gaussian_confidence){
        return Gaussian (
            //mean
            graph.get_maxX() / 2,
            graph.get_maxY() / 2,

            //sigma
            compute_sigma(graph.get_maxX() / 2, gaussian_confidence),
            compute_sigma(graph.get_maxY() / 2, gaussian_confidence),

            //size — full grid so gaussian_at has no artificial cutoff inside the grid
            graph.get_maxX() + 1,
            graph.get_maxY() + 1,

            //weight
            base_gaussian_weight,

            //inverse
            false
        );
    }


    Gaussian mapped_gaussian(const Graph& graph, const Node& node, double mapped_gaussian_weight, double gaussian_confidence) {
        return Gaussian(
            //mean
            node.coordX,
            node.coordY,

            //sigma
            compute_sigma(graph.get_maxX() / 2, gaussian_confidence),
            compute_sigma(graph.get_maxY() / 2, gaussian_confidence),

            //size
            graph.get_maxX() + 1,
            graph.get_maxY() + 1,

            //weight
            mapped_gaussian_weight,

            //inverse
            true
        );

    }

    Gaussian magic_gaussian(const Graph& graph, int node_id, double gaussian_confidence) {
        return Gaussian(
            //mean
            graph.get_coordX(node_id),
            graph.get_coordY(node_id),

            //sigma
            compute_sigma(graph.get_maxX() / 2, gaussian_confidence),
            compute_sigma(graph.get_maxY() / 2, gaussian_confidence),

            //size
            graph.get_maxX() + 1,
            graph.get_maxY() + 1,

            //weight
            0,

            //inverse
            false

        );

    }


    Gaussian cnot_gaussian(const Graph& graph, int node_id, double weight, bool inverse, double gaussian_confidence) {
        return Gaussian(
            //mean
            graph.get_coordX(node_id),
            graph.get_coordY(node_id),

            //sigma
            compute_sigma(graph.get_maxX() / 2, gaussian_confidence),
            compute_sigma(graph.get_maxY() / 2, gaussian_confidence),

            //size
            graph.get_maxX() + 1,
            graph.get_maxY() + 1,

            //weight
            weight,

            //inverse
            inverse
        );
    }


}
