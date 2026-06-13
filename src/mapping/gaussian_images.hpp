#include <stdlib.h>
#include <filesystem>

#include "gaussian.hpp"
#include "../helpers.hpp"


namespace GaussianMappingVisualization {


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

void write_external_layer(
    const std::filesystem::path& out_path,
    double external_weight,
    int width,
    int height
) {
    std::ofstream out(out_path);
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const bool on_border = (x == 0 || x == width - 1 || y == 0 || y == height - 1);
            out << x << " " << y << " " << (on_border ? external_weight : 0.0) << "\n";
        }
        out << "\n";
    }
}

void write_total_with_external(
    const std::filesystem::path& out_path,
    const std::vector<Gaussian>& gaussians,
    double external_weight,
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
            const bool on_border = (x == 0 || x == width - 1 || y == 0 || y == height - 1);
            if (on_border) {
                z += external_weight;
            }
            out << x << " " << y << " " << z << "\n";
        }
        out << "\n";
    }
}

double max_external_value(double external_weight, int width, int height) {
    if (width <= 0 || height <= 0) return 0.0;
    return external_weight; // flat value on border, 0 elsewhere
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
    const Qubit& qubit,
    double external_weight
) {
    // Frame writing is opt-in via FTQC_SAVE_FRAMES=1. Gating on "not a bench
    // worker" made every interactive gaussian run pay the gnuplot frames
    // inside the timed mapping region (measured ~670x on qft_n18), so manual
    // timings were meaningless and visualization/ was rewritten on every run.
    if (!env_flag_is_truthy("FTQC_SAVE_FRAMES")) {
        return;
    }

    static int frame_id = 0;

    const int width = graph.get_maxX() + 1;
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
    const std::filesystem::path external_dat = out_dir / ("external_" + idx + ".dat");
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
    write_external_layer(external_dat, external_weight, width, height);

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
    write_total_with_external(total_dat, total_plot, external_weight, width, height);

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
    const double max_external = max_external_value(external_weight, width, height);
    const double max_total = max_gaussian_value(total_plot, width, height) + (external_weight > 0.0 ? external_weight : 0.0);


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
          << "  ext_w=" << external_weight
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

    if (external_weight != 0.0) {
        std::ostringstream entry;
        entry << "'" << external_dat.string() << "' using 1:2:3 with lines lc rgb '#E53935' lw 2 dt 4 title 'external_weight="
              << external_weight << "'";
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
           << "  ext_w=" << external_weight
           << "' at screen 0.02,0.92 front tc rgb '#111111'\n";
    gp_sum << "set xlabel 'x'\n";
    gp_sum << "set ylabel 'y'\n";
    gp_sum << "set zlabel 'amplitude'\n";
    gp_sum << "set key outside right top opaque\n";
    gp_sum << "set view 62,36\n";
    gp_sum << "splot '" << total_dat.string() << "' using 1:2:3 with lines lc rgb '#1F6FE5' lw 2 title 'all\\_gaussians\\_sum'\n";
    gp_sum.close();

    const std::string cmd_split = "gnuplot '" + script_gp.string() + "'";
    std::system(cmd_split.c_str());
    const std::string cmd_sum = "gnuplot '" + script_sum_gp.string() + "'";
    std::system(cmd_sum.c_str());
}

} // namespace
