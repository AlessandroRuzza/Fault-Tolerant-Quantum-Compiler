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

## Routing by magic-aware strategy

![Routing by magic-aware strategy](07_box_routing_by_magic_strategy.png)

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

## Routing heatmap: magic strategy x safe passage

![Routing heatmap: magic strategy x safe passage](15_heatmap_routing_magic_vs_safe.png)

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

- `09_scatter_density_vs_routing.png` (Density vs routing): no rows with valid numeric data_density_f and routing_steps_f
- `12_scatter_pressure_vs_elapsed.png` (Interaction pressure vs duration): no rows with valid numeric interaction_pressure_f and duration_s_f

## Top Gaussian Weight Configurations

Top 3 gaussian weight configurations per `circuit x graph-dimensions`. Each configuration is ranked by its best observed `routing_steps`, then by mean routing steps across the successful runs that used the same weight tuple.

Readable best-profile CSV export: `best_gaussian_weight_profile_by_circuit_dimension.csv`

Relative weight-gap CSV export: `best_gaussian_relative_weight_gaps.csv`

CSV export: `top_gaussian_weight_configs_by_circuit_dimension.csv`

## Best Mapping Table

Only circuit x graph-dimensions where `gaussian`, `homogeneous`, and `magic-aware` all appear in the runs. All configurations tied for the lowest routing steps are listed among successful runs with routing steps available.

CSV export: `best_mapping_by_circuit_dimension.csv`

| circuit x dimensions | best mapping | safe passage | magic placement | routing steps |
| --- | --- | --- | --- | ---: |
| adder_n64_transpiled-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 250 |
| adder_n64_transpiled-100x100 | magic-aware (center) | passage | center_circle(5%) | 250 |
| adder_n64_transpiled-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 250 |
| bb84_n8-100x100 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 15 |
| bigadder_n18_transpiled-100x100 | gaussian (coarse) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 161 |
| cat_n130-100x100 | homogeneous | connectivity | center_circle(5%) | 130 |
| cat_n130-100x100 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-100x100 | homogeneous | passage | center_circle(5%) | 130 |
| cat_n130-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 130 |
| cat_n130-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 130 |
| cat_n130-100x100 | magic-aware (center) | cube | center_circle(5%) | 130 |
| continuous_3_17_13-100x100 | gaussian (coarse) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | cube | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| dnn_n16-100x100 | homogeneous | connectivity | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | cube | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-100x100 | magic-aware (center) | cube | center_circle(5%) | 48 |
| example-100x100 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| ghz_n255-100x100 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-100x100 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_state_n23-100x100 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 23 |
| parallel-100x100 | gaussian (coarse) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 69 |
| qaoa_n6-100x100 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-100x100 | magic-aware (center) | cube | center_circle(5%) | 34 |
| qft_20-100x100 | homogeneous | connectivity | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | cube | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 76 |
| wstate_n27-100x100 | homogeneous | connectivity | center_circle(5%) | 34 |
| wstate_n27-100x100 | homogeneous | cube | center_circle(5%) | 34 |
| wstate_n27-100x100 | homogeneous | passage | center_circle(5%) | 34 |
| wstate_n27-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 34 |
| wstate_n27-100x100 | magic-aware (center) | cube | center_circle(5%) | 34 |
| wstate_n27-100x100 | magic-aware (center) | passage | center_circle(5%) | 34 |
| wstate_n27-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 34 |

## Best Mapping Table (All Families Exit Code 0)

Only circuit x graph-dimensions where `gaussian`, `homogeneous`, and `magic-aware` all appear among runs with `exit_code = 0`. All configurations tied for the lowest routing steps are listed only from those `exit_code = 0` runs.

CSV export: `best_mapping_by_circuit_dimension_all_families_exit0.csv`

| circuit x dimensions | best mapping | safe passage | magic placement | routing steps |
| --- | --- | --- | --- | ---: |
| bb84_n8-100x100 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 15 |
| bigadder_n18_transpiled-100x100 | gaussian (coarse) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 161 |
| continuous_3_17_13-100x100 | gaussian (coarse) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | cube | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| dnn_n16-100x100 | homogeneous | connectivity | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | cube | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-100x100 | magic-aware (center) | cube | center_circle(5%) | 48 |
| example-100x100 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| ghz_state_n23-100x100 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 23 |
| parallel-100x100 | gaussian (coarse) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 69 |
| qaoa_n6-100x100 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-100x100 | magic-aware (center) | cube | center_circle(5%) | 34 |
| qft_20-100x100 | homogeneous | connectivity | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | cube | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 76 |

