#include <cmath>
#include <limits>
#include <stdexcept>

// gaussian_sigma is the direct, absolute standard deviation of every gaussian,
// the same on both axes and independent of the grid size. It replaced the old
// gaussian_confidence parameter (which derived a per-axis, grid-scaled sigma via
// sigma = radius / sqrt(-2 ln(1 - confidence)) and was floored near confidence=1
// by double precision). Validity (> 0, finite) is enforced by the Gaussian ctor.

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

    Gaussian baseline_gaussian(const Graph& graph, double base_gaussian_weight, double gaussian_sigma){
        return Gaussian (
            //mean
            graph.get_maxX() / 2,
            graph.get_maxY() / 2,

            //sigma (direct, absolute, same on both axes)
            gaussian_sigma,
            gaussian_sigma,

            //size — full grid so gaussian_at has no artificial cutoff inside the grid
            graph.get_maxX() + 1,
            graph.get_maxY() + 1,

            //weight
            base_gaussian_weight,

            //inverse
            false
        );
    }


    Gaussian mapped_gaussian(const Graph& graph, const Node& node, double mapped_gaussian_weight, double gaussian_sigma) {
        return Gaussian(
            //mean
            node.coordX,
            node.coordY,

            //sigma (direct, absolute, same on both axes)
            gaussian_sigma,
            gaussian_sigma,

            //size
            graph.get_maxX() + 1,
            graph.get_maxY() + 1,

            //weight
            mapped_gaussian_weight,

            //inverse
            true
        );

    }

    Gaussian magic_gaussian(const Graph& graph, int node_id, double gaussian_sigma) {
        return Gaussian(
            //mean
            graph.get_coordX(node_id),
            graph.get_coordY(node_id),

            //sigma (direct, absolute, same on both axes)
            gaussian_sigma,
            gaussian_sigma,

            //size
            graph.get_maxX() + 1,
            graph.get_maxY() + 1,

            //weight
            0,

            //inverse
            false

        );

    }


    Gaussian cnot_gaussian(const Graph& graph, int node_id, double weight, bool inverse, double gaussian_sigma) {
        return Gaussian(
            //mean
            graph.get_coordX(node_id),
            graph.get_coordY(node_id),

            //sigma (direct, absolute, same on both axes)
            gaussian_sigma,
            gaussian_sigma,

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
