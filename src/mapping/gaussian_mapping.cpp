#include "mapping.hpp"
#include "gaussian.hpp"
#include "circuit.hpp"
#include "qubit.hpp"
#include "graph.hpp"

#include <cstdlib>
#include <filesystem>
#include <fstream>

#define MAPPED_GAUSSIAN_WEIGHT 0.8
#define MAGIC_HIGHEST 1.5
#define MAGIC_ABOVE_THRESHOLD 1.2
#define CNOT_ABOVE_THRESHOLD 1.5
#define MAGIC_BELOW_THRESHOLD 1.2
#define BASE_GAUSSIAN_WEIGHT 1


//TODO
#define CNOT_THRESHOLD 1

double compute_sigma(int radius, double confidence) {return radius / sqrt(-2 * log(1 - confidence));}
void update_weight(std::vector<Gaussian>& gaussians, double new_weight);
void update_inverse(std::vector<Gaussian>& gaussians, bool inverse);
void update_gaussians(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Graph& graph, const Mapping& mapping, int t_lower_bound, int t_upper_bound);
Node computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit);


void Mapping::one_iteration_gaussian_mapping(Qubit* qubit, int* iterations, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, Gaussian& baseline_gaussian) {
    
    std::vector<Gaussian> cnot_gaussians;

    update_gaussians(qubit, mapped_gaussians, magic_gaussians, cnot_gaussians, graph, *this, T_lower_bound, T_upper_bound);

    Node best_node = computeNextMappingNode(mapped_gaussians, magic_gaussians, cnot_gaussians, baseline_gaussian, graph, *qubit);
    map_qubit_to_node(qubit->getQubitID(), best_node.id, 0);

    mapped_gaussians.push_back(Gaussian(
        //mean
        best_node.coordX,
        best_node.coordY,

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
    ));


    (*iterations)++;

}


void Mapping::gaussian_mapping() {
    if (PRINT_MAPPING) std::cout << "\n\n";
    
    std::vector<Gaussian> mapped_gaussians;
    std::vector<Gaussian> magic_gaussians;

    Gaussian baseline_gaussian(
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
    
    for (int node_id : graph.get_magic_state_ids()) {
        magic_gaussians.push_back(Gaussian(
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
        ));
    }
    
    int total_qubits = circuit.getNumQubits();
    int iterations = 0;

    while (circuit.getHeapSize() > 0 && iterations < maximum_iterations) {
        if (MAPPING_VERBOSE) circuit.print_qubit_heap();
        Qubit* qubit = circuit.popFromHeap();
        if (qubit == nullptr) {
            continue;
        }
        if (get_mapped_node(qubit->getQubitID()) != -1) {
            continue; // already mapped as a side effect of mapping a related qubit
        }
        try {
            one_iteration_gaussian_mapping(qubit, &iterations, mapped_gaussians, magic_gaussians, baseline_gaussian);
        } catch (const std::exception& e) {
            throw std::runtime_error(
                "Failed to map qubit " + std::to_string(qubit->getQubitID()) + ": " + e.what()
            );
        }
        if (PRINT_MAPPING) std::cout << "Mapped qubits: " << iterations << "/" << total_qubits << "\n\n";
    }
}



void update_weight(std::vector<Gaussian>& gaussians, double new_weight) {
    for (Gaussian& g : gaussians) {
        g.update_weight(new_weight);
    }
}


void update_inverse(std::vector<Gaussian>& gaussians, bool inverse) {
    for (Gaussian& g : gaussians) {
        g.update_inverse(inverse);
    }
}





void update_gaussians(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Graph& graph, const Mapping& mapping, int t_lower_bound, int t_upper_bound) {

    if (PRINT_MAPPING) std::cout << "Mapping qubit " << qubit->getQubitID() << " with T_count = "
              << qubit->getTCount() << " and max CNOT count = "
              << qubit->getMaxCNOTCount() << "\n";

    if (qubit->getTCount() > qubit->getMaxCNOTCount()) {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on T_count" << "\n";
        update_weight(magic_gaussians, MAGIC_ABOVE_THRESHOLD);

    } else {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on CNOT_count" << "\n";

        std::vector<int> highCnotQubits = qubit->highCnotQubits(CNOT_THRESHOLD);
        
        for (int i : highCnotQubits) {
            int second_qubit_mapped_node = mapping.get_mapped_node(i);
            if (second_qubit_mapped_node != -1){
                cnot_gaussians.push_back(Gaussian(
                    //mean
                    graph.get_coordX(second_qubit_mapped_node),
                    graph.get_coordY(second_qubit_mapped_node),


                    //sigma
                    compute_sigma(graph.get_maxX() / 2 , 0.95),
                    compute_sigma(graph.get_maxY() / 2 , 0.95),

                    //size
                    graph.get_maxX(), 
                    graph.get_maxY() + 1, 

                    //weight
                    CNOT_ABOVE_THRESHOLD,

                    //inverse
                    false
                ));
            }
        }


        if (qubit->getTCount() < t_lower_bound) {
            if (MAPPING_VERBOSE) std::cout << "mapping far from magic states because second qubit is not "
                             "mapped and T_count is low\n";
            update_weight(magic_gaussians, MAGIC_BELOW_THRESHOLD);
            update_inverse(magic_gaussians, true);
        } else if (qubit->getTCount() > t_upper_bound) {
            update_weight(mapped_gaussians, MAGIC_ABOVE_THRESHOLD);
        }

        
    }
}

double max_gaussian_value(const std::vector<Gaussian>& gaussians, int width, int height) {
    double max_value = 0.0;
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            double z = 0.0;
            for (const Gaussian& g : gaussians) {
                z += g.gaussian_at(x, y);
            }
            if (z > max_value) {
                max_value = z;
            }
        }
    }
    return max_value;
}






namespace {

void write_gaussian_layer(
    const std::filesystem::path& out_path,
    const std::vector<Gaussian>& gaussians,
    int width,
    int height
) {
    std::ofstream out(out_path);
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            double z = 0.0;
            for (const Gaussian& g : gaussians) {
                z += g.gaussian_at(x, y);
            }
            out << x << " " << y << " " << z << "\n";
        }
        out << "\n";
    }
}

void save_gaussian_frame(
    const std::vector<Gaussian>& mapped_gaussians,
    const std::vector<Gaussian>& magic_gaussians,
    const std::vector<Gaussian>& cnot_gaussians,
    const Gaussian& baseline_gaussian,
    const Graph& graph,
    const Qubit& qubit
) {
    static int frame_id = 0;

    const int width = graph.get_maxX();
    const int height = graph.get_maxY() + 1;
    if (width <= 0 || height <= 0) {
        return;
    }

    const std::filesystem::path out_dir = std::filesystem::path(PROJECT_ROOT) / "visualization" / "gaussian_frames";
    std::filesystem::create_directories(out_dir);

    const std::string idx = std::to_string(frame_id++);
    const std::filesystem::path mapped_dat = out_dir / ("mapped_" + idx + ".dat");
    const std::filesystem::path magic_dat = out_dir / ("magic_" + idx + ".dat");
    const std::filesystem::path cnot_dat = out_dir / ("cnot_" + idx + ".dat");
    const std::filesystem::path baseline_dat = out_dir / ("baseline_" + idx + ".dat");
    const std::filesystem::path script_gp = out_dir / ("plot_" + idx + ".gp");
    const std::filesystem::path output_png = out_dir / ("gaussians_" + idx + ".png");

    std::vector<Gaussian> mapped_plot = mapped_gaussians;
    std::vector<Gaussian> magic_plot = magic_gaussians;
    std::vector<Gaussian> cnot_plot = cnot_gaussians;

    // Visualization only: show direct Gaussian peaks instead of inverse surfaces.
    update_inverse(mapped_plot, false);
    update_inverse(magic_plot, false);
    update_inverse(cnot_plot, false);

    write_gaussian_layer(mapped_dat, mapped_plot, width, height);
    write_gaussian_layer(magic_dat, magic_plot, width, height);
    write_gaussian_layer(cnot_dat, cnot_plot, width, height);
    std::vector<Gaussian> baseline_layer{baseline_gaussian};
    write_gaussian_layer(baseline_dat, baseline_layer, width, height);

    const double max_mapped = max_gaussian_value(mapped_plot, width, height);
    const double max_magic = max_gaussian_value(magic_plot, width, height);
    const double max_cnot = max_gaussian_value(cnot_plot, width, height);
    const double max_baseline = max_gaussian_value(baseline_layer, width, height);


    std::ofstream gp(script_gp);
    gp << "set terminal pngcairo size 1400,900\n";
    gp << "set output '" << output_png.string() << "'\n";
     gp << "set title 'Gaussian layers - frame " << idx << "'\n";
     gp << "set label 1 'qubit=" << qubit.getQubitID()
         << "  T=" << qubit.getTCount()
         << "  CNOTMax=" << qubit.getMaxCNOTCount()
         << "' at screen 0.02,0.95 front tc rgb '#111111'\n";
      gp << "set label 2 'max(mapped)=" << max_mapped
          << "  max(magic)=" << max_magic
          << "  max(cnot)=" << max_cnot
          << "  max(base)=" << max_baseline
          << "' at screen 0.02,0.92 front tc rgb '#111111'\n";
    gp << "set xlabel 'x'\n";
    gp << "set ylabel 'y'\n";
    gp << "set zlabel 'amplitude'\n";
    gp << "set key outside\n";
    gp << "set hidden3d\n";
    gp << "set view 62,36\n";
     gp << "set style line 1 lc rgb '#B455F5' lw 2\n";
     gp << "set style line 2 lc rgb '#28B8D9' lw 2\n";
     gp << "set style line 3 lc rgb '#F5A623' lw 2\n";
     gp << "set style line 4 lc rgb '#222222' lw 2\n";
     gp << "splot '" << mapped_dat.string() << "' using 1:2:3 with lines ls 1 title 'mapped',\\\n";
     gp << "      '" << magic_dat.string() << "' using 1:2:3 with lines ls 2 title 'magic',\\\n";
     gp << "      '" << cnot_dat.string() << "' using 1:2:3 with lines ls 3 title 'cnot',\\\n";
     gp << "      '" << baseline_dat.string() << "' using 1:2:3 with lines ls 4 title 'baseline'\n";
    gp.close();

    const std::string cmd = "gnuplot '" + script_gp.string() + "'";
    std::system(cmd.c_str());
}

} // namespace




Node Mapping::computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit) {
    
    save_gaussian_frame(mapped_gaussians, magic_gaussians, cnot_gaussians, baseline_gaussian, graph, qubit);

    // Compute the combined Gaussian influence for each node and select the best one
    const std::vector<Node> nodes = graph.get_nodes();
    if (nodes.empty()) {
        throw std::runtime_error("Graph has no nodes");
    }

    Node best_node = nodes.front();
    double best_score = -std::numeric_limits<double>::infinity();
    const std::vector<int> magic_ids = graph.get_magic_state_ids();

    for (const Node& node : graph.get_nodes()) {
        

        if (node.occupied) {
            continue;
        }
        if (std::find(magic_ids.begin(), magic_ids.end(), node.id) != magic_ids.end()) {
            continue;
        }

        bool is_safe = check_safe_passage(node);
        if (!is_safe) {
            continue;
        }


        double score = 0.0;

        for (const Gaussian& g : mapped_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }
        for (const Gaussian& g : magic_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }
        for (const Gaussian& g : cnot_gaussians) {
            score += g.gaussian_at(node.coordX, node.coordY);
        }

        score += baseline_gaussian.gaussian_at(node.coordX, node.coordY);

        if (score > best_score) {
            best_score = score;
            best_node = node;
        }
    }

    return best_node;
}
