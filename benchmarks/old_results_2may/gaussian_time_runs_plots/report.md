# Benchmark Charts

Generated plot set from benchmark CSV files.

See also `summary.txt` for aggregate metrics.

## Overview dashboard

![Overview dashboard](00_overview_dashboard.png)

## Run status and exit codes

![Run status and exit codes](01_status_and_exit_codes.png)

## Circuit-level summary

![Circuit-level summary](02_circuit_summary_bars.png)

## Routing steps by circuit

![Routing steps by circuit](03_box_routing_by_circuit.png)

## Duration by circuit

![Duration by circuit](04_box_elapsed_by_circuit.png)

## Routing by magic placement

![Routing by magic placement](05_box_routing_by_placement.png)

## Routing by safe passage

![Routing by safe passage](06_box_routing_by_safe_passage.png)

## Duration vs routing

![Duration vs routing](08_scatter_elapsed_vs_routing_by_circuit.png)

## Duration vs qubits plus gates: cube median points

![Duration vs qubits plus gates: cube median points](32_runtime_vs_qubits_plus_gates_cube_with_timeouts.png)

## Duration vs qubits plus gates: connectivity median points

![Duration vs qubits plus gates: connectivity median points](32_runtime_vs_qubits_plus_gates_connectivity_with_timeouts.png)

## Duration vs qubits: cube median points

![Duration vs qubits: cube median points](33_runtime_vs_qubits_cube_with_timeouts.png)

## Duration vs qubits: connectivity median points

![Duration vs qubits: connectivity median points](33_runtime_vs_qubits_connectivity_with_timeouts.png)

## Duration vs gates: cube median points

![Duration vs gates: cube median points](34_runtime_vs_gates_cube_with_timeouts.png)

## Duration vs gates: connectivity median points

![Duration vs gates: connectivity median points](34_runtime_vs_gates_connectivity_with_timeouts.png)

## Duration vs graph size: cube median points

![Duration vs graph size: cube median points](35_runtime_vs_graph_nodes_cube_with_timeouts.png)

## Duration vs graph size: connectivity median points

![Duration vs graph size: connectivity median points](35_runtime_vs_graph_nodes_connectivity_with_timeouts.png)

## Duration vs qubits by size multiplier

![Duration vs qubits by size multiplier](36_runtime_vs_qubits_by_size_moltiplier.png)

## Duration vs qubits by gaussian confidence

![Duration vs qubits by gaussian confidence](37_runtime_vs_qubits_by_gaussian_confidence.png)

## Duration vs qubits by safe passage

![Duration vs qubits by safe passage](38_runtime_vs_qubits_by_safe_passage_strategy.png)

## Duration vs gates by size multiplier

![Duration vs gates by size multiplier](39_runtime_vs_gates_by_size_moltiplier.png)

## Duration vs gates by gaussian confidence

![Duration vs gates by gaussian confidence](40_runtime_vs_gates_by_gaussian_confidence.png)

## Duration vs gates by safe passage

![Duration vs gates by safe passage](41_runtime_vs_gates_by_safe_passage_strategy.png)

## Duration vs graph size by size multiplier

![Duration vs graph size by size multiplier](42_runtime_vs_graph_nodes_by_size_moltiplier.png)

## Duration vs graph size by gaussian confidence

![Duration vs graph size by gaussian confidence](43_runtime_vs_graph_nodes_by_gaussian_confidence.png)

## Duration vs graph size by safe passage

![Duration vs graph size by safe passage](44_runtime_vs_graph_nodes_by_safe_passage_strategy.png)

## Routing heatmap: safe passage x gaussian confidence

![Routing heatmap: safe passage x gaussian confidence](45_heatmap_routing_safe_passage_vs_gaussian_confidence.png)

## Routing heatmap: gaussian confidence x size multiplier

![Routing heatmap: gaussian confidence x size multiplier](46_heatmap_routing_gaussian_confidence_vs_size_moltiplier.png)

## Magic state parameter vs routing

![Magic state parameter vs routing](10_scatter_magic_states_vs_routing.png)

## Border distance vs routing

![Border distance vs routing](11_scatter_border_vs_routing_center_circle.png)

## Success heatmap: safe passage x placement (timeouts excluded)

![Success heatmap: safe passage x placement (timeouts excluded)](13_heatmap_success_safe_vs_placement_excluding_timeouts.png)

## Routing heatmap: safe passage x placement

![Routing heatmap: safe passage x placement](14_heatmap_routing_safe_vs_placement.png)

## Timeout heatmap: safe passage x placement

![Timeout heatmap: safe passage x placement](25_heatmap_timeout_safe_vs_placement.png)

## Success heatmap: safe passage x mapping type (timeouts excluded)

![Success heatmap: safe passage x mapping type (timeouts excluded)](23_heatmap_success_safe_vs_mapping_type_excluding_timeouts.png)

## Routing heatmap: safe passage x mapping type

![Routing heatmap: safe passage x mapping type](24_heatmap_routing_safe_vs_mapping_type.png)

## Timeout heatmap: safe passage x mapping type

![Timeout heatmap: safe passage x mapping type](26_heatmap_timeout_safe_vs_mapping_type.png)

## Success heatmap by grid size

![Success heatmap by grid size](16_heatmap_success_by_grid_xy.png)

## Experiment set: gaussian + homogeneous

![Experiment set: gaussian + homogeneous](17_experiment_set_routing_gaussian_homogeneous.png)

## Experiment set: magic-aware + homogeneous

![Experiment set: magic-aware + homogeneous](18_experiment_set_routing_magicaware_homogeneous.png)

## Routing by gaussian strategy

![Routing by gaussian strategy](19_box_routing_by_gaussian_strategy.png)

## Routing heatmap: gaussian strategy x placement

![Routing heatmap: gaussian strategy x placement](20_heatmap_routing_gaussian_strategy_vs_placement.png)

## Routing by gaussian weight combinations

![Routing by gaussian weight combinations](21_box_gaussian_weight_combinations_vs_routing.png)

## Best gaussian weight profile map

![Best gaussian weight profile map](30_heatmap_best_gaussian_weight_profiles.png)

## Best gaussian relative weight gaps

![Best gaussian relative weight gaps](31_heatmap_best_gaussian_relative_weight_gaps.png)

## Experiment set: all mappings

![Experiment set: all mappings](22_experiment_set_routing_all_mappings.png)

## Skipped Plots

- `07_box_routing_by_magic_strategy.png` (Routing by magic-aware strategy): no rows with valid numeric routing_steps_f
- `09_scatter_density_vs_routing.png` (Density vs routing): no rows with valid numeric data_density_f and routing_steps_f
- `12_scatter_pressure_vs_elapsed.png` (Interaction pressure vs duration): no rows with valid numeric interaction_pressure_f and duration_s_f
- `15_heatmap_routing_magic_vs_safe.png` (Routing heatmap: magic strategy x safe passage): no rows available for heatmap axes magic_aware_strategy x safe_passage_strategy

## Top Gaussian Weight Configurations

Top 3 gaussian weight configurations per `circuit x graph-dimensions`. Each configuration is ranked by its best observed `routing_steps`, then by mean routing steps across the successful runs that used the same weight tuple.

Readable best-profile CSV export: `best_gaussian_weight_profile_by_circuit_dimension.csv`

Relative weight-gap CSV export: `best_gaussian_relative_weight_gaps.csv`

CSV export: `top_gaussian_weight_configs_by_circuit_dimension.csv`

