#include "mapping.hpp"
#include "gaussian.hpp"
#include "circuit.hpp"
#include "qubit.hpp"
#include "graph.hpp"

#include <array>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>

#define MAPPED_GAUSSIAN_WEIGHT 0.8
#define MAGIC_HIGHEST 1.5
#define MAGIC_ABOVE_THRESHOLD 1.2
#define CNOT_ABOVE_THRESHOLD 1.5
#define MAGIC_BELOW_THRESHOLD 1.2
#define BASE_GAUSSIAN_WEIGHT 1


double compute_sigma(int radius, double confidence) {return radius / sqrt(-2 * log(1 - confidence));}
void update_weight(std::vector<Gaussian>& gaussians, double new_weight);
void update_inverse(std::vector<Gaussian>& gaussians, bool inverse);
void update_gaussians(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Graph& graph, const Mapping& mapping, int t_lower_bound, int t_upper_bound, int cnot_threshold);
Node computeNextMappingNode(std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Gaussian& baseline_gaussian, Graph& graph, const Qubit& qubit);


void Mapping::one_iteration_gaussian_mapping(Qubit* qubit, int* iterations, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, Gaussian& baseline_gaussian) {
    
    std::vector<Gaussian> cnot_gaussians;

    update_gaussians(qubit, mapped_gaussians, magic_gaussians, cnot_gaussians, graph, *this, T_lower_bound, T_upper_bound, CNOT_threshold);

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





void update_gaussians(Qubit* qubit, std::vector<Gaussian>& mapped_gaussians, std::vector<Gaussian>& magic_gaussians, std::vector<Gaussian>& cnot_gaussians, Graph& graph, const Mapping& mapping, int t_lower_bound, int t_upper_bound, int cnot_threshold) {

    if (PRINT_MAPPING) std::cout << "Mapping qubit " << qubit->getQubitID() << " with T_count = "
              << qubit->getTCount() << " and max CNOT count = "
              << qubit->getMaxCNOTCount() << "\n";

    if (qubit->getTCount() > qubit->getMaxCNOTCount()) {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on T_count" << "\n";
        update_weight(magic_gaussians, MAGIC_ABOVE_THRESHOLD);
        update_inverse(magic_gaussians, false);

    } else {
        if (MAPPING_VERBOSE) std::cout << "Mapping based on CNOT_count" << "\n";

        std::vector<int> highCnotQubits = qubit->highCnotQubits(cnot_threshold);

        std::cout << "Qubits with CNOT count above threshold (" << cnot_threshold << "): ";
        for (int i : highCnotQubits) {
            std::cout << i << " ";
        }
        
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
            update_weight(magic_gaussians, MAGIC_ABOVE_THRESHOLD);
            update_inverse(magic_gaussians, false);

        } else {
            update_weight(magic_gaussians, 0);
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

constexpr double kPlotLayerEpsilon = 1e-12;

const std::array<const char*, 8> kMappedPalette = {
    "#B455F5", "#9C6BFF", "#8A82FF", "#6FA0FF",
    "#58BBFF", "#49CFF5", "#3EDBE2", "#35E5CC"
};

const std::array<const char*, 8> kMagicPalette = {
    "#28B8D9", "#30C8E8", "#3AD9F2", "#52E4F7",
    "#6CECF9", "#87F2FA", "#A0F6FB", "#B8FAFC"
};

const std::array<const char*, 8> kCnotPalette = {
    "#F5A623", "#F7B133", "#F9BC45", "#FBC75A",
    "#FCD170", "#FEDA86", "#FFE39D", "#FFEBB4"
};

template <std::size_t N>
const char* palette_color(const std::array<const char*, N>& palette, std::size_t idx) {
    return palette[idx % palette.size()];
}

std::string gaussian_details(const Gaussian& gaussian) {
    std::ostringstream details;
    details << std::fixed << std::setprecision(2);
    details << "mx=" << gaussian.get_mean_x()
            << ",my=" << gaussian.get_mean_y()
            << ",sx=" << gaussian.get_sigma_x()
            << ",sy=" << gaussian.get_sigma_y()
            << ",w=" << gaussian.get_weight()
            << ",inv=" << (gaussian.is_inverse() ? 1 : 0);
    return details.str();
}

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

std::vector<std::filesystem::path> write_component_layers(
    const std::filesystem::path& out_dir,
    const std::string& prefix,
    const std::string& frame_idx,
    const std::vector<Gaussian>& gaussians,
    int width,
    int height,
    std::vector<std::string>* component_labels
) {
    std::vector<std::filesystem::path> component_paths;
    component_paths.reserve(gaussians.size());
    if (component_labels != nullptr) {
        component_labels->clear();
        component_labels->reserve(gaussians.size());
    }

    for (std::size_t i = 0; i < gaussians.size(); ++i) {
        const std::vector<Gaussian> single_layer{gaussians[i]};
        if (max_gaussian_value(single_layer, width, height) <= kPlotLayerEpsilon) {
            continue;
        }

        const std::filesystem::path component_path =
            out_dir / (prefix + "_" + frame_idx + "_" + std::to_string(i) + ".dat");
        write_gaussian_layer(component_path, single_layer, width, height);
        component_paths.push_back(component_path);
        if (component_labels != nullptr) {
            component_labels->push_back(gaussian_details(gaussians[i]));
        }
    }

    return component_paths;
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
    const std::filesystem::path total_dat = out_dir / ("total_" + idx + ".dat");
    const std::filesystem::path script_gp = out_dir / ("plot_" + idx + ".gp");
    const std::filesystem::path output_png = out_dir / ("gaussians_" + idx + ".png");
    const std::filesystem::path script_sum_gp = out_dir / ("plot_sum_" + idx + ".gp");
    const std::filesystem::path output_sum_png = out_dir / ("gaussians_sum_" + idx + ".png");

    const std::vector<Gaussian>& mapped_plot = mapped_gaussians;
    const std::vector<Gaussian>& magic_plot = magic_gaussians;
    const std::vector<Gaussian>& cnot_plot = cnot_gaussians;

    write_gaussian_layer(mapped_dat, mapped_plot, width, height);
    write_gaussian_layer(magic_dat, magic_plot, width, height);
    write_gaussian_layer(cnot_dat, cnot_plot, width, height);
    std::vector<Gaussian> baseline_layer{baseline_gaussian};
    write_gaussian_layer(baseline_dat, baseline_layer, width, height);

    std::vector<Gaussian> total_plot;
    total_plot.reserve(mapped_plot.size() + magic_plot.size() + cnot_plot.size() + baseline_layer.size());
    for (const Gaussian& g : mapped_plot) {
        total_plot.push_back(g);
    }
    for (const Gaussian& g : magic_plot) {
        total_plot.push_back(g);
    }
    for (const Gaussian& g : cnot_plot) {
        total_plot.push_back(g);
    }
    for (const Gaussian& g : baseline_layer) {
        total_plot.push_back(g);
    }
    write_gaussian_layer(total_dat, total_plot, width, height);

    std::vector<std::string> mapped_labels;
    std::vector<std::string> magic_labels;
    std::vector<std::string> cnot_labels;
    const auto mapped_components = write_component_layers(out_dir, "mapped_component", idx, mapped_plot, width, height, &mapped_labels);
    const auto magic_components = write_component_layers(out_dir, "magic_component", idx, magic_plot, width, height, &magic_labels);
    const auto cnot_components = write_component_layers(out_dir, "cnot_component", idx, cnot_plot, width, height, &cnot_labels);

    const double max_mapped = max_gaussian_value(mapped_plot, width, height);
    const double max_magic = max_gaussian_value(magic_plot, width, height);
    const double max_cnot = max_gaussian_value(cnot_plot, width, height);
    const double max_baseline = max_gaussian_value(baseline_layer, width, height);
    const double max_total = max_gaussian_value(total_plot, width, height);


    std::ofstream gp(script_gp);
    gp << "set terminal pngcairo size 1400,900\n";
    gp << "set output '" << output_png.string() << "'\n";
     gp << "set title 'Gaussian layers - frame " << idx << "'\n";
     gp << "set label 1 'qubit=" << qubit.getQubitID()
         << "  T=" << qubit.getTCount()
         << "  CNOTMax=" << qubit.getMaxCNOTCount()
         << "  mappedN=" << mapped_components.size()
         << "  magicN=" << magic_components.size()
         << "  cnotN=" << cnot_components.size()
         << "' at screen 0.02,0.95 front tc rgb '#111111'\n";
      gp << "set label 2 'max(mapped)=" << max_mapped
          << "  max(magic)=" << max_magic
          << "  max(cnot)=" << max_cnot
          << "  max(base)=" << max_baseline
          << "' at screen 0.02,0.92 front tc rgb '#111111'\n";
    gp << "set xlabel 'x'\n";
    gp << "set ylabel 'y'\n";
    gp << "set zlabel 'amplitude'\n";
    gp << "set key outside right top opaque\n";
    // NOTE: hidden3d can collapse visible mesh colors to a single style, making
    // legend colors appear inconsistent with plotted layers.
    gp << "set view 62,36\n";
    std::vector<std::string> plot_entries;
    plot_entries.reserve(mapped_components.size() + magic_components.size() + cnot_components.size() + 1);

    for (std::size_t i = 0; i < mapped_components.size(); ++i) {
        std::ostringstream entry;
        entry << "'" << mapped_components[i].string() << "' using 1:2:3 with lines lc rgb '"
              << palette_color(kMappedPalette, i) << "' lw 2 dt 1 title 'mapped[" << i << "] "
              << mapped_labels[i] << "'";
        plot_entries.push_back(entry.str());
    }

    for (std::size_t i = 0; i < magic_components.size(); ++i) {
        std::ostringstream entry;
        entry << "'" << magic_components[i].string() << "' using 1:2:3 with lines lc rgb '"
              << palette_color(kMagicPalette, i) << "' lw 2 dt 2 title 'magic[" << i << "] "
              << magic_labels[i] << "'";
        plot_entries.push_back(entry.str());
    }

    for (std::size_t i = 0; i < cnot_components.size(); ++i) {
        std::ostringstream entry;
        entry << "'" << cnot_components[i].string() << "' using 1:2:3 with lines lc rgb '"
              << palette_color(kCnotPalette, i) << "' lw 2 dt 3 title 'cnot[" << i << "] "
              << cnot_labels[i] << "'";
        plot_entries.push_back(entry.str());
    }

    {
        std::ostringstream entry;
        entry << "'" << baseline_dat.string() << "' using 1:2:3 with lines lc rgb '#222222' lw 2 dt 1 title 'baseline "
              << gaussian_details(baseline_gaussian) << "'";
        plot_entries.push_back(entry.str());
    }

    gp << "splot ";
    for (std::size_t i = 0; i < plot_entries.size(); ++i) {
        gp << plot_entries[i];
        if (i + 1 < plot_entries.size()) {
            gp << ",\\\n      ";
        } else {
            gp << "\n";
        }
    }
    gp.close();

    std::ofstream gp_sum(script_sum_gp);
    gp_sum << "set terminal pngcairo size 1400,900\n";
    gp_sum << "set output '" << output_sum_png.string() << "'\n";
    gp_sum << "set title 'Gaussian SUM - frame " << idx << "'\n";
    gp_sum << "set label 1 'qubit=" << qubit.getQubitID()
           << "  T=" << qubit.getTCount()
           << "  CNOTMax=" << qubit.getMaxCNOTCount()
           << "' at screen 0.02,0.95 front tc rgb '#111111'\n";
    gp_sum << "set label 2 'max(total)=" << max_total
           << "  max(mapped)=" << max_mapped
           << "  max(magic)=" << max_magic
           << "  max(cnot)=" << max_cnot
           << "  max(base)=" << max_baseline
           << "' at screen 0.02,0.92 front tc rgb '#111111'\n";
    gp_sum << "set xlabel 'x'\n";
    gp_sum << "set ylabel 'y'\n";
    gp_sum << "set zlabel 'amplitude'\n";
    gp_sum << "set key outside right top opaque\n";
    gp_sum << "set view 62,36\n";
    gp_sum << "splot '" << total_dat.string() << "' using 1:2:3 with lines lc rgb '#1F6FE5' lw 2 title 'all_gaussians_sum'\n";
    gp_sum.close();

    const std::string cmd_split = "gnuplot '" + script_gp.string() + "'";
    std::system(cmd_split.c_str());
    const std::string cmd_sum = "gnuplot '" + script_sum_gp.string() + "'";
    std::system(cmd_sum.c_str());
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
