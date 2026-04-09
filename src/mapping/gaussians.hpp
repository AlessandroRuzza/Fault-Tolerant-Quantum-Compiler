#define MAPPED_GAUSSIAN_WEIGHT 0.8
#define BASE_GAUSSIAN_WEIGHT 1






double compute_sigma(int radius, double confidence) {return radius / sqrt(-2 * log(1 - confidence));}


namespace Gaussians {

    Gaussian baseline_gaussian(const Graph& graph){
        return Gaussian (
            //mean
            graph.get_maxX() / 2,
            graph.get_maxY() / 2,

            //sigma
            compute_sigma(graph.get_maxX() / 2, 0.95),
            compute_sigma(graph.get_maxY() / 2, 0.95),

            //size
            graph.get_maxX(),
            graph.get_maxY() + 1,

            //weight
            BASE_GAUSSIAN_WEIGHT,

            //inverse
            false
        );
    }


    Gaussian mapped_gaussian(const Graph& graph, const Node& node) {
        return Gaussian(
            //mean
            node.coordX,
            node.coordY,

            //sigma
            compute_sigma(graph.get_maxX() / 2, 0.95),
            compute_sigma(graph.get_maxY() / 2, 0.95),

            //size
            graph.get_maxX(), 
            graph.get_maxY() + 1, 

            //weight
            MAPPED_GAUSSIAN_WEIGHT,

            //inverse
            true
        );

    }

    Gaussian magic_gaussian(const Graph& graph, int node_id) {
        return Gaussian(
            //mean
            graph.get_coordX(node_id),
            graph.get_coordY(node_id),

            //sigma
            compute_sigma(graph.get_maxX() / 2, 0.95),
            compute_sigma(graph.get_maxY() / 2, 0.95),

            //size
            graph.get_maxX(), 
            graph.get_maxY() + 1, 

            //weight
            0,

            //inverse
            false

        );

    }


    Gaussian cnot_gaussian(const Graph& graph, int node_id, double weight, bool inverse) {
        return Gaussian(
            //mean
            graph.get_coordX(node_id),
            graph.get_coordY(node_id),


            //sigma
            compute_sigma(graph.get_maxX() / 2 , 0.95),
            compute_sigma(graph.get_maxY() / 2 , 0.95),

            //size
            graph.get_maxX(), 
            graph.get_maxY() + 1, 

            //weight
            weight,

            //inverse
            inverse
        );
    }


}