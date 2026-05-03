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
| adder_n64_transpiled-17x17 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 258 |
| adder_n64_transpiled-17x17 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 258 |
| adder_n64_transpiled-17x17 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 258 |
| adder_n64_transpiled-18x18 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 251 |
| adder_n64_transpiled-19x19 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 251 |
| adder_n64_transpiled-19x19 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 251 |
| adder_n64_transpiled-19x19 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 251 |
| adder_n64_transpiled-20x20 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 253 |
| adder_n64_transpiled-20x20 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 253 |
| adder_n64_transpiled-20x20 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 253 |
| adder_n64_transpiled-21x21 | gaussian (fine) | cube | center_circle(0%) | 247 |
| adder_n64_transpiled-21x21 | magic-aware (distance) | cube | center_circle(0%) | 247 |
| adder_n64_transpiled-22x22 | gaussian (fine) | cube | center_circle(10%) | 247 |
| adder_n64_transpiled-23x23 | gaussian (fine) | cube | center_circle(0%) | 246 |
| adder_n64_transpiled-23x23 | gaussian (fine) | cube | center_circle(10%) | 246 |
| adder_n64_transpiled-24x24 | gaussian (fine) | cube | center_circle(5%) | 247 |
| adder_n64_transpiled-25x25 | gaussian (coarse) | cube | center_circle(10%) | 250 |
| adder_n64_transpiled-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 250 |
| adder_n64_transpiled-100x100 | magic-aware (center) | passage | center_circle(5%) | 250 |
| adder_n64_transpiled-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 250 |
| bb84_n8-6x6 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-6x6 | homogeneous | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage | right_row | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | homogeneous | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | homogeneous | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | right_row | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | right_row | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | right_row | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | right_row | 15 |
| bb84_n8-8x8 | homogeneous | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | homogeneous | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | right_row | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | right_row | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | right_row | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | right_row | 15 |
| bb84_n8-9x9 | gaussian (coarse) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (coarse) | connectivity | right_row | 15 |
| bb84_n8-9x9 | gaussian (coarse) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (coarse) | cube | right_row | 15 |
| bb84_n8-9x9 | gaussian (fine) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (fine) | connectivity | right_row | 15 |
| bb84_n8-9x9 | gaussian (fine) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (fine) | cube | right_row | 15 |
| bb84_n8-9x9 | magic-aware (center) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (center) | connectivity | right_row | 15 |
| bb84_n8-9x9 | magic-aware (center) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (center) | cube | right_row | 15 |
| bb84_n8-9x9 | magic-aware (distance) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (distance) | connectivity | right_row | 15 |
| bb84_n8-9x9 | magic-aware (distance) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (distance) | cube | right_row | 15 |
| bb84_n8-9x9 | magic-aware (random) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (random) | connectivity | right_row | 15 |
| bb84_n8-9x9 | magic-aware (random) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (random) | cube | right_row | 15 |
| bb84_n8-100x100 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 15 |
| bigadder_n18_transpiled-6x6 | gaussian (coarse) | passage | right_row | 161 |
| bigadder_n18_transpiled-6x6 | gaussian (fine) | passage | right_row | 161 |
| bigadder_n18_transpiled-6x6 | magic-aware (distance) | passage | right_row | 161 |
| bigadder_n18_transpiled-6x6 | magic-aware (random) | passage | right_row | 161 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | gaussian (fine) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage | right_row | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (distance) | passage | right_row | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (random) | passage | right_row | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (distance) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (distance) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (distance) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (random) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (random) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (random) | cube | right_row | 157 |
| bigadder_n18_transpiled-100x100 | gaussian (coarse) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 161 |
| cat_n130-26x26 | homogeneous | passage | center_circle(0%) | 130 |
| cat_n130-26x26 | homogeneous | passage | right_row | 130 |
| cat_n130-26x26 | magic-aware (distance) | passage | center_circle(0%) | 130 |
| cat_n130-26x26 | magic-aware (distance) | passage | right_row | 130 |
| cat_n130-26x26 | magic-aware (random) | passage | right_row | 130 |
| cat_n130-27x27 | homogeneous | passage | center_circle(0%) | 130 |
| cat_n130-27x27 | homogeneous | passage | right_row | 130 |
| cat_n130-27x27 | magic-aware (distance) | passage | center_circle(0%) | 130 |
| cat_n130-27x27 | magic-aware (distance) | passage | right_row | 130 |
| cat_n130-27x27 | magic-aware (random) | passage | right_row | 130 |
| cat_n130-31x31 | gaussian (coarse) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-31x31 | gaussian (fine) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-31x31 | homogeneous | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | homogeneous | cube | right_row | 130 |
| cat_n130-31x31 | magic-aware (center) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-31x31 | magic-aware (distance) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-31x31 | magic-aware (random) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | magic-aware (random) | cube | right_row | 130 |
| cat_n130-32x32 | gaussian (coarse) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | gaussian (coarse) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-32x32 | gaussian (fine) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | gaussian (fine) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-32x32 | homogeneous | connectivity | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | right_row | 130 |
| cat_n130-32x32 | homogeneous | passage | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | passage_no_subgraphs | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-34x34 | homogeneous | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (random) | cube | right_row | 130 |
| cat_n130-100x100 | homogeneous | connectivity | center_circle(5%) | 130 |
| cat_n130-100x100 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-100x100 | homogeneous | passage | center_circle(5%) | 130 |
| cat_n130-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 130 |
| cat_n130-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 130 |
| cat_n130-100x100 | magic-aware (center) | cube | center_circle(5%) | 130 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | right_row | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage_no_subgraphs | right_row | 19 |
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
| dnn_n16-8x8 | gaussian (coarse) | passage | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-9x9 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | connectivity | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | connectivity | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | cube | center_circle(0%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(10%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | connectivity | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | cube | center_circle(0%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | center_circle(10%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-10x10 | homogeneous | passage_no_subgraphs | center_circle(10%) | 48 |
| dnn_n16-10x10 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | magic-aware (center) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | connectivity | right_row | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(10%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-11x11 | gaussian (fine) | connectivity | right_row | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(10%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-11x11 | homogeneous | connectivity | right_row | 48 |
| dnn_n16-11x11 | homogeneous | cube | right_row | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | right_row | 48 |
| dnn_n16-11x11 | magic-aware (random) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (coarse) | connectivity | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | connectivity | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | connectivity | right_row | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (fine) | connectivity | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | connectivity | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | connectivity | right_row | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-12x12 | homogeneous | cube | right_row | 48 |
| dnn_n16-12x12 | magic-aware (center) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | magic-aware (center) | cube | right_row | 48 |
| dnn_n16-100x100 | homogeneous | connectivity | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | cube | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-100x100 | magic-aware (center) | cube | center_circle(5%) | 48 |
| example-4x4 | gaussian (coarse) | passage | right_row | 51 |
| example-4x4 | gaussian (coarse) | passage_no_subgraphs | right_row | 51 |
| example-4x4 | gaussian (fine) | passage | center_circle(10%) | 51 |
| example-4x4 | gaussian (fine) | passage | center_circle(5%) | 51 |
| example-4x4 | gaussian (fine) | passage | right_row | 51 |
| example-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-4x4 | gaussian (fine) | passage_no_subgraphs | right_row | 51 |
| example-4x4 | magic-aware (distance) | passage | center_circle(0%) | 51 |
| example-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-4x4 | magic-aware (random) | passage | center_circle(0%) | 51 |
| example-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | connectivity | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | connectivity | right_row | 51 |
| example-5x5 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | cube | center_circle(10%) | 51 |
| example-5x5 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | cube | right_row | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(10%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage | right_row | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | gaussian (fine) | connectivity | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | connectivity | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | connectivity | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | connectivity | right_row | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | cube | right_row | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | passage | right_row | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | homogeneous | connectivity | center_circle(0%) | 51 |
| example-5x5 | homogeneous | connectivity | center_circle(5%) | 51 |
| example-5x5 | homogeneous | cube | center_circle(0%) | 51 |
| example-5x5 | homogeneous | cube | right_row | 51 |
| example-5x5 | homogeneous | passage | center_circle(0%) | 51 |
| example-5x5 | homogeneous | passage | right_row | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | right_row | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(10%) | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | cube | right_row | 51 |
| example-5x5 | magic-aware (center) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | passage | right_row | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | magic-aware (distance) | connectivity | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(10%) | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(5%) | 51 |
| example-5x5 | magic-aware (distance) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | magic-aware (random) | connectivity | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | connectivity | right_row | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(10%) | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(5%) | 51 |
| example-5x5 | magic-aware (random) | cube | right_row | 51 |
| example-5x5 | magic-aware (random) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage | right_row | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | right_row | 51 |
| example-6x6 | gaussian (coarse) | connectivity | center_circle(0%) | 51 |
| example-6x6 | gaussian (coarse) | connectivity | center_circle(10%) | 51 |
| example-6x6 | gaussian (coarse) | connectivity | center_circle(5%) | 51 |
| example-6x6 | gaussian (coarse) | connectivity | right_row | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(10%) | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (coarse) | cube | right_row | 51 |
| example-6x6 | gaussian (fine) | connectivity | center_circle(0%) | 51 |
| example-6x6 | gaussian (fine) | connectivity | center_circle(10%) | 51 |
| example-6x6 | gaussian (fine) | connectivity | center_circle(5%) | 51 |
| example-6x6 | gaussian (fine) | connectivity | right_row | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(10%) | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (fine) | cube | right_row | 51 |
| example-6x6 | homogeneous | connectivity | center_circle(0%) | 51 |
| example-6x6 | homogeneous | connectivity | center_circle(10%) | 51 |
| example-6x6 | homogeneous | connectivity | center_circle(5%) | 51 |
| example-6x6 | homogeneous | cube | center_circle(0%) | 51 |
| example-6x6 | homogeneous | cube | center_circle(10%) | 51 |
| example-6x6 | homogeneous | cube | center_circle(5%) | 51 |
| example-6x6 | homogeneous | cube | right_row | 51 |
| example-6x6 | magic-aware (center) | connectivity | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | connectivity | center_circle(10%) | 51 |
| example-6x6 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-6x6 | magic-aware (center) | connectivity | right_row | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(10%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (center) | cube | right_row | 51 |
| example-6x6 | magic-aware (distance) | connectivity | center_circle(0%) | 51 |
| example-6x6 | magic-aware (distance) | connectivity | center_circle(10%) | 51 |
| example-6x6 | magic-aware (distance) | connectivity | center_circle(5%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(10%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (distance) | cube | right_row | 51 |
| example-6x6 | magic-aware (random) | connectivity | center_circle(0%) | 51 |
| example-6x6 | magic-aware (random) | connectivity | center_circle(10%) | 51 |
| example-6x6 | magic-aware (random) | connectivity | center_circle(5%) | 51 |
| example-6x6 | magic-aware (random) | connectivity | right_row | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(10%) | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (random) | cube | right_row | 51 |
| example-100x100 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| ghz_n255-34x34 | homogeneous | passage | center_circle(0%) | 255 |
| ghz_n255-34x34 | homogeneous | passage | right_row | 255 |
| ghz_n255-34x34 | homogeneous | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-34x34 | homogeneous | passage_no_subgraphs | right_row | 255 |
| ghz_n255-34x34 | magic-aware (distance) | passage | center_circle(0%) | 255 |
| ghz_n255-34x34 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-34x34 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-34x34 | magic-aware (distance) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-34x34 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-34x34 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-34x34 | magic-aware (random) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-35x35 | homogeneous | passage | right_row | 255 |
| ghz_n255-35x35 | homogeneous | passage_no_subgraphs | right_row | 255 |
| ghz_n255-35x35 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-35x35 | magic-aware (distance) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-35x35 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-35x35 | magic-aware (random) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-36x36 | homogeneous | passage | center_circle(0%) | 255 |
| ghz_n255-36x36 | homogeneous | passage | right_row | 255 |
| ghz_n255-36x36 | homogeneous | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-36x36 | homogeneous | passage_no_subgraphs | right_row | 255 |
| ghz_n255-36x36 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-36x36 | magic-aware (distance) | passage | center_circle(0%) | 255 |
| ghz_n255-36x36 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-36x36 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-36x36 | magic-aware (distance) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-36x36 | magic-aware (random) | passage | center_circle(0%) | 255 |
| ghz_n255-36x36 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-36x36 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-36x36 | magic-aware (random) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-37x37 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-37x37 | homogeneous | passage | right_row | 255 |
| ghz_n255-37x37 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-37x37 | homogeneous | passage_no_subgraphs | right_row | 255 |
| ghz_n255-37x37 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-37x37 | magic-aware (distance) | passage | center_circle(5%) | 255 |
| ghz_n255-37x37 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-37x37 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-37x37 | magic-aware (distance) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-37x37 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-37x37 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-37x37 | magic-aware (random) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-38x38 | homogeneous | passage | center_circle(0%) | 255 |
| ghz_n255-38x38 | homogeneous | passage | right_row | 255 |
| ghz_n255-38x38 | homogeneous | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-38x38 | homogeneous | passage_no_subgraphs | right_row | 255 |
| ghz_n255-38x38 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-38x38 | magic-aware (distance) | passage | center_circle(0%) | 255 |
| ghz_n255-38x38 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-38x38 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-38x38 | magic-aware (distance) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-38x38 | magic-aware (random) | passage | center_circle(0%) | 255 |
| ghz_n255-38x38 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-38x38 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 255 |
| ghz_n255-38x38 | magic-aware (random) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-40x40 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-40x40 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-40x40 | homogeneous | connectivity | center_circle(0%) | 255 |
| ghz_n255-40x40 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-40x40 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | homogeneous | cube | right_row | 255 |
| ghz_n255-40x40 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-40x40 | homogeneous | passage | right_row | 255 |
| ghz_n255-40x40 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | homogeneous | passage_no_subgraphs | right_row | 255 |
| ghz_n255-40x40 | magic-aware (center) | connectivity | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-40x40 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | connectivity | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-40x40 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-42x42 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-42x42 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-42x42 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-42x42 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-42x42 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | homogeneous | cube | right_row | 255 |
| ghz_n255-42x42 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-42x42 | magic-aware (distance) | connectivity | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-42x42 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-42x42 | magic-aware (random) | connectivity | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-42x42 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-43x43 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-43x43 | homogeneous | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-43x43 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | homogeneous | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (center) | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (distance) | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (random) | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-44x44 | gaussian (coarse) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-44x44 | gaussian (fine) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-44x44 | homogeneous | connectivity | center_circle(10%) | 255 |
| ghz_n255-44x44 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-44x44 | homogeneous | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | cube | right_row | 255 |
| ghz_n255-44x44 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-44x44 | magic-aware (center) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-44x44 | magic-aware (distance) | connectivity | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-44x44 | magic-aware (distance) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-44x44 | magic-aware (random) | connectivity | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-44x44 | magic-aware (random) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-45x45 | homogeneous | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (center) | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (distance) | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (random) | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | center_circle(10%) | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-47x47 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-47x47 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | homogeneous | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (center) | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | center_circle(10%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (distance) | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (random) | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-49x49 | gaussian (coarse) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-49x49 | gaussian (fine) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-49x49 | homogeneous | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-49x49 | homogeneous | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | homogeneous | cube | right_row | 255 |
| ghz_n255-49x49 | magic-aware (center) | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (center) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-49x49 | magic-aware (distance) | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-49x49 | magic-aware (distance) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-49x49 | magic-aware (random) | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-49x49 | magic-aware (random) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-100x100 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-100x100 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | homogeneous | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-10x10 | homogeneous | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | homogeneous | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-15x15 | gaussian (coarse) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-15x15 | homogeneous | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | homogeneous | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (center) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (center) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-100x100 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 23 |
| parallel-8x8 | gaussian (coarse) | cube | center_circle(5%) | 65 |
| parallel-8x8 | gaussian (fine) | cube | center_circle(5%) | 65 |
| parallel-100x100 | gaussian (coarse) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 69 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | cube | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | cube | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (fine) | cube | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | cube | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | cube | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | cube | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | cube | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | right_row | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | right_row | 34 |
| qaoa_n6-7x7 | homogeneous | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | right_row | 34 |
| qaoa_n6-100x100 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-100x100 | magic-aware (center) | cube | center_circle(5%) | 34 |
| qft_20-9x9 | gaussian (fine) | passage_no_subgraphs | right_row | 145 |
| qft_20-10x10 | magic-aware (random) | passage_no_subgraphs | right_row | 127 |
| qft_20-11x11 | magic-aware (random) | passage_no_subgraphs | right_row | 109 |
| qft_20-12x12 | gaussian (coarse) | cube | right_row | 105 |
| qft_20-13x13 | gaussian (coarse) | cube | right_row | 100 |
| qft_20-14x14 | gaussian (coarse) | cube | right_row | 108 |
| qft_20-100x100 | homogeneous | connectivity | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | cube | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 76 |
| wstate_n27-11x11 | gaussian (fine) | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-11x11 | homogeneous | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | homogeneous | passage | right_row | 34 |
| wstate_n27-11x11 | homogeneous | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | homogeneous | passage_no_subgraphs | right_row | 34 |
| wstate_n27-11x11 | magic-aware (center) | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-11x11 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (distance) | passage | right_row | 34 |
| wstate_n27-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage | right_row | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | homogeneous | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | homogeneous | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | homogeneous | passage | right_row | 34 |
| wstate_n27-12x12 | homogeneous | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-12x12 | homogeneous | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | homogeneous | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | homogeneous | connectivity | center_circle(0%) | 34 |
| wstate_n27-13x13 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-13x13 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | homogeneous | cube | right_row | 34 |
| wstate_n27-13x13 | homogeneous | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | homogeneous | passage | right_row | 34 |
| wstate_n27-13x13 | homogeneous | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | homogeneous | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | cube | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | connectivity | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-14x14 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | center_circle(0%) | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(5%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-14x14 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (center) | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | center_circle(0%) | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | center_circle(5%) | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (center) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-16x16 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-16x16 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-16x16 | gaussian (fine) | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-16x16 | homogeneous | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-16x16 | homogeneous | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | homogeneous | cube | right_row | 34 |
| wstate_n27-16x16 | magic-aware (center) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-16x16 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-16x16 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-16x16 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-16x16 | magic-aware (random) | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (random) | cube | right_row | 34 |
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
| adder_n64_transpiled-17x17 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 258 |
| adder_n64_transpiled-17x17 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 258 |
| adder_n64_transpiled-17x17 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 258 |
| adder_n64_transpiled-18x18 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 251 |
| adder_n64_transpiled-19x19 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 251 |
| adder_n64_transpiled-19x19 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 251 |
| adder_n64_transpiled-19x19 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 251 |
| adder_n64_transpiled-20x20 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 253 |
| adder_n64_transpiled-20x20 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 253 |
| adder_n64_transpiled-20x20 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 253 |
| adder_n64_transpiled-21x21 | gaussian (fine) | cube | center_circle(0%) | 247 |
| adder_n64_transpiled-21x21 | magic-aware (distance) | cube | center_circle(0%) | 247 |
| adder_n64_transpiled-22x22 | gaussian (fine) | cube | center_circle(10%) | 247 |
| adder_n64_transpiled-23x23 | gaussian (fine) | cube | center_circle(0%) | 246 |
| adder_n64_transpiled-23x23 | gaussian (fine) | cube | center_circle(10%) | 246 |
| adder_n64_transpiled-24x24 | gaussian (fine) | cube | center_circle(5%) | 247 |
| adder_n64_transpiled-25x25 | gaussian (coarse) | cube | center_circle(10%) | 250 |
| bb84_n8-6x6 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-6x6 | homogeneous | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage | right_row | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | homogeneous | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | homogeneous | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage_no_subgraphs | right_row | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | connectivity | right_row | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | right_row | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | connectivity | right_row | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | right_row | 15 |
| bb84_n8-8x8 | homogeneous | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | homogeneous | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | connectivity | right_row | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | connectivity | right_row | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | connectivity | right_row | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(10%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | right_row | 15 |
| bb84_n8-9x9 | gaussian (coarse) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (coarse) | connectivity | right_row | 15 |
| bb84_n8-9x9 | gaussian (coarse) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (coarse) | cube | right_row | 15 |
| bb84_n8-9x9 | gaussian (fine) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (fine) | connectivity | right_row | 15 |
| bb84_n8-9x9 | gaussian (fine) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | gaussian (fine) | cube | right_row | 15 |
| bb84_n8-9x9 | magic-aware (center) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (center) | connectivity | right_row | 15 |
| bb84_n8-9x9 | magic-aware (center) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (center) | cube | right_row | 15 |
| bb84_n8-9x9 | magic-aware (distance) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (distance) | connectivity | right_row | 15 |
| bb84_n8-9x9 | magic-aware (distance) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (distance) | cube | right_row | 15 |
| bb84_n8-9x9 | magic-aware (random) | connectivity | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (random) | connectivity | right_row | 15 |
| bb84_n8-9x9 | magic-aware (random) | cube | center_circle(10%) | 15 |
| bb84_n8-9x9 | magic-aware (random) | cube | right_row | 15 |
| bb84_n8-100x100 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage | center_circle(5%) | 15 |
| bb84_n8-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 15 |
| bigadder_n18_transpiled-6x6 | gaussian (coarse) | passage | right_row | 161 |
| bigadder_n18_transpiled-6x6 | gaussian (fine) | passage | right_row | 161 |
| bigadder_n18_transpiled-6x6 | magic-aware (distance) | passage | right_row | 161 |
| bigadder_n18_transpiled-6x6 | magic-aware (random) | passage | right_row | 161 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | gaussian (fine) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage | right_row | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (distance) | passage | right_row | 157 |
| bigadder_n18_transpiled-7x7 | magic-aware (random) | passage | right_row | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (distance) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (distance) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (distance) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (random) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (random) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | magic-aware (random) | cube | right_row | 157 |
| bigadder_n18_transpiled-100x100 | gaussian (coarse) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | cube | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 161 |
| cat_n130-31x31 | gaussian (coarse) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-31x31 | gaussian (fine) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-31x31 | homogeneous | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | homogeneous | cube | right_row | 130 |
| cat_n130-31x31 | magic-aware (center) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-31x31 | magic-aware (distance) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-31x31 | magic-aware (random) | cube | center_circle(0%) | 130 |
| cat_n130-31x31 | magic-aware (random) | cube | right_row | 130 |
| cat_n130-32x32 | gaussian (coarse) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | gaussian (coarse) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-32x32 | gaussian (fine) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | gaussian (fine) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-32x32 | homogeneous | connectivity | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | right_row | 130 |
| cat_n130-32x32 | homogeneous | passage | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | passage_no_subgraphs | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-34x34 | homogeneous | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (random) | cube | right_row | 130 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | right_row | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | passage_no_subgraphs | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | connectivity | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | passage_no_subgraphs | right_row | 19 |
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
| dnn_n16-8x8 | gaussian (coarse) | passage | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (coarse) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-8x8 | gaussian (fine) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-9x9 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | connectivity | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | connectivity | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | cube | center_circle(0%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(10%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | connectivity | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | cube | center_circle(0%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | center_circle(10%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage_no_subgraphs | right_row | 48 |
| dnn_n16-10x10 | homogeneous | passage_no_subgraphs | center_circle(10%) | 48 |
| dnn_n16-10x10 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | magic-aware (center) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | connectivity | right_row | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(10%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-11x11 | gaussian (fine) | connectivity | right_row | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(10%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-11x11 | homogeneous | connectivity | right_row | 48 |
| dnn_n16-11x11 | homogeneous | cube | right_row | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | right_row | 48 |
| dnn_n16-11x11 | magic-aware (random) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (coarse) | connectivity | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | connectivity | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | connectivity | right_row | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (fine) | connectivity | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | connectivity | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | connectivity | right_row | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | center_circle(10%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-12x12 | homogeneous | cube | right_row | 48 |
| dnn_n16-12x12 | magic-aware (center) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | magic-aware (center) | cube | right_row | 48 |
| dnn_n16-100x100 | homogeneous | connectivity | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | cube | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage | center_circle(5%) | 48 |
| dnn_n16-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-100x100 | magic-aware (center) | cube | center_circle(5%) | 48 |
| example-4x4 | gaussian (coarse) | passage | right_row | 51 |
| example-4x4 | gaussian (coarse) | passage_no_subgraphs | right_row | 51 |
| example-4x4 | gaussian (fine) | passage | center_circle(10%) | 51 |
| example-4x4 | gaussian (fine) | passage | center_circle(5%) | 51 |
| example-4x4 | gaussian (fine) | passage | right_row | 51 |
| example-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-4x4 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-4x4 | gaussian (fine) | passage_no_subgraphs | right_row | 51 |
| example-4x4 | magic-aware (distance) | passage | center_circle(0%) | 51 |
| example-4x4 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-4x4 | magic-aware (random) | passage | center_circle(0%) | 51 |
| example-4x4 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | connectivity | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | connectivity | right_row | 51 |
| example-5x5 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | cube | center_circle(10%) | 51 |
| example-5x5 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | cube | right_row | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(10%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage | right_row | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | gaussian (fine) | connectivity | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | connectivity | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | connectivity | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | connectivity | right_row | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | cube | right_row | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | passage | right_row | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | homogeneous | connectivity | center_circle(0%) | 51 |
| example-5x5 | homogeneous | connectivity | center_circle(5%) | 51 |
| example-5x5 | homogeneous | cube | center_circle(0%) | 51 |
| example-5x5 | homogeneous | cube | right_row | 51 |
| example-5x5 | homogeneous | passage | center_circle(0%) | 51 |
| example-5x5 | homogeneous | passage | right_row | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | right_row | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(10%) | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | cube | right_row | 51 |
| example-5x5 | magic-aware (center) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | passage | right_row | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | magic-aware (distance) | connectivity | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(10%) | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(5%) | 51 |
| example-5x5 | magic-aware (distance) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (distance) | passage_no_subgraphs | right_row | 51 |
| example-5x5 | magic-aware (random) | connectivity | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | connectivity | right_row | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(10%) | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(5%) | 51 |
| example-5x5 | magic-aware (random) | cube | right_row | 51 |
| example-5x5 | magic-aware (random) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage | right_row | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (random) | passage_no_subgraphs | right_row | 51 |
| example-6x6 | gaussian (coarse) | connectivity | center_circle(0%) | 51 |
| example-6x6 | gaussian (coarse) | connectivity | center_circle(10%) | 51 |
| example-6x6 | gaussian (coarse) | connectivity | center_circle(5%) | 51 |
| example-6x6 | gaussian (coarse) | connectivity | right_row | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(10%) | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (coarse) | cube | right_row | 51 |
| example-6x6 | gaussian (fine) | connectivity | center_circle(0%) | 51 |
| example-6x6 | gaussian (fine) | connectivity | center_circle(10%) | 51 |
| example-6x6 | gaussian (fine) | connectivity | center_circle(5%) | 51 |
| example-6x6 | gaussian (fine) | connectivity | right_row | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(10%) | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (fine) | cube | right_row | 51 |
| example-6x6 | homogeneous | connectivity | center_circle(0%) | 51 |
| example-6x6 | homogeneous | connectivity | center_circle(10%) | 51 |
| example-6x6 | homogeneous | connectivity | center_circle(5%) | 51 |
| example-6x6 | homogeneous | cube | center_circle(0%) | 51 |
| example-6x6 | homogeneous | cube | center_circle(10%) | 51 |
| example-6x6 | homogeneous | cube | center_circle(5%) | 51 |
| example-6x6 | homogeneous | cube | right_row | 51 |
| example-6x6 | magic-aware (center) | connectivity | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | connectivity | center_circle(10%) | 51 |
| example-6x6 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-6x6 | magic-aware (center) | connectivity | right_row | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(10%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (center) | cube | right_row | 51 |
| example-6x6 | magic-aware (distance) | connectivity | center_circle(0%) | 51 |
| example-6x6 | magic-aware (distance) | connectivity | center_circle(10%) | 51 |
| example-6x6 | magic-aware (distance) | connectivity | center_circle(5%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(10%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (distance) | cube | right_row | 51 |
| example-6x6 | magic-aware (random) | connectivity | center_circle(0%) | 51 |
| example-6x6 | magic-aware (random) | connectivity | center_circle(10%) | 51 |
| example-6x6 | magic-aware (random) | connectivity | center_circle(5%) | 51 |
| example-6x6 | magic-aware (random) | connectivity | right_row | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(10%) | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (random) | cube | right_row | 51 |
| example-100x100 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-100x100 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage | center_circle(5%) | 51 |
| example-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| ghz_n255-40x40 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-40x40 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-40x40 | homogeneous | connectivity | center_circle(0%) | 255 |
| ghz_n255-40x40 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-40x40 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | homogeneous | cube | right_row | 255 |
| ghz_n255-40x40 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-40x40 | homogeneous | passage | right_row | 255 |
| ghz_n255-40x40 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | homogeneous | passage_no_subgraphs | right_row | 255 |
| ghz_n255-40x40 | magic-aware (center) | connectivity | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-40x40 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | connectivity | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-40x40 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (distance) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-40x40 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-40x40 | magic-aware (random) | passage_no_subgraphs | right_row | 255 |
| ghz_n255-42x42 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-42x42 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-42x42 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-42x42 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-42x42 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | homogeneous | cube | right_row | 255 |
| ghz_n255-42x42 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-42x42 | magic-aware (distance) | connectivity | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-42x42 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-42x42 | magic-aware (random) | connectivity | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-42x42 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-42x42 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-43x43 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-43x43 | homogeneous | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-43x43 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | homogeneous | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (center) | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (distance) | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (random) | connectivity | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-44x44 | gaussian (coarse) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-44x44 | gaussian (fine) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-44x44 | homogeneous | connectivity | center_circle(10%) | 255 |
| ghz_n255-44x44 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-44x44 | homogeneous | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | cube | right_row | 255 |
| ghz_n255-44x44 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_n255-44x44 | magic-aware (center) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-44x44 | magic-aware (distance) | connectivity | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-44x44 | magic-aware (distance) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-44x44 | magic-aware (random) | connectivity | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-44x44 | magic-aware (random) | cube | center_circle(10%) | 255 |
| ghz_n255-44x44 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-45x45 | homogeneous | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (center) | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (distance) | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (random) | connectivity | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | connectivity | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | center_circle(10%) | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-47x47 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-47x47 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | homogeneous | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (center) | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | center_circle(10%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (distance) | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (random) | connectivity | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-49x49 | gaussian (coarse) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-49x49 | gaussian (fine) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-49x49 | homogeneous | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | homogeneous | connectivity | right_row | 255 |
| ghz_n255-49x49 | homogeneous | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | homogeneous | cube | right_row | 255 |
| ghz_n255-49x49 | magic-aware (center) | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (center) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-49x49 | magic-aware (distance) | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (distance) | connectivity | right_row | 255 |
| ghz_n255-49x49 | magic-aware (distance) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-49x49 | magic-aware (random) | connectivity | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (random) | connectivity | right_row | 255 |
| ghz_n255-49x49 | magic-aware (random) | cube | center_circle(10%) | 255 |
| ghz_n255-49x49 | magic-aware (random) | cube | right_row | 255 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (coarse) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-10x10 | gaussian (fine) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | homogeneous | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-10x10 | homogeneous | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | homogeneous | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (distance) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-10x10 | magic-aware (random) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage_no_subgraphs | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(10%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(10%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-15x15 | gaussian (coarse) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-15x15 | homogeneous | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | homogeneous | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | homogeneous | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (center) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (center) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | connectivity | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | connectivity | right_row | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | cube | center_circle(10%) | 23 |
| ghz_state_n23-15x15 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-100x100 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage | center_circle(5%) | 23 |
| ghz_state_n23-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 23 |
| parallel-8x8 | gaussian (coarse) | cube | center_circle(5%) | 65 |
| parallel-8x8 | gaussian (fine) | cube | center_circle(5%) | 65 |
| parallel-100x100 | gaussian (coarse) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | connectivity | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | cube | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage | center_circle(5%) | 69 |
| parallel-100x100 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 69 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | cube | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | cube | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (fine) | cube | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | cube | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | cube | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | cube | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | connectivity | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | cube | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | right_row | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | right_row | 34 |
| qaoa_n6-7x7 | homogeneous | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | connectivity | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(10%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | right_row | 34 |
| qaoa_n6-100x100 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-100x100 | magic-aware (center) | cube | center_circle(5%) | 34 |
| qft_20-9x9 | gaussian (fine) | passage_no_subgraphs | right_row | 145 |
| qft_20-10x10 | magic-aware (random) | passage_no_subgraphs | right_row | 127 |
| qft_20-11x11 | magic-aware (random) | passage_no_subgraphs | right_row | 109 |
| qft_20-12x12 | gaussian (coarse) | cube | right_row | 105 |
| qft_20-13x13 | gaussian (coarse) | cube | right_row | 100 |
| qft_20-14x14 | gaussian (coarse) | cube | right_row | 108 |
| qft_20-100x100 | homogeneous | connectivity | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | cube | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage | center_circle(5%) | 76 |
| qft_20-100x100 | homogeneous | passage_no_subgraphs | center_circle(5%) | 76 |
| wstate_n27-11x11 | gaussian (fine) | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-11x11 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-11x11 | homogeneous | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | homogeneous | passage | right_row | 34 |
| wstate_n27-11x11 | homogeneous | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | homogeneous | passage_no_subgraphs | right_row | 34 |
| wstate_n27-11x11 | magic-aware (center) | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-11x11 | magic-aware (center) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (distance) | passage | right_row | 34 |
| wstate_n27-11x11 | magic-aware (distance) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage | right_row | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-11x11 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | homogeneous | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | homogeneous | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | homogeneous | passage | right_row | 34 |
| wstate_n27-12x12 | homogeneous | passage_no_subgraphs | center_circle(0%) | 34 |
| wstate_n27-12x12 | homogeneous | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | homogeneous | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | gaussian (fine) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | homogeneous | connectivity | center_circle(0%) | 34 |
| wstate_n27-13x13 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-13x13 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | homogeneous | cube | right_row | 34 |
| wstate_n27-13x13 | homogeneous | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | homogeneous | passage | right_row | 34 |
| wstate_n27-13x13 | homogeneous | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | homogeneous | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | cube | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (center) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | connectivity | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage | right_row | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (distance) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage | right_row | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage_no_subgraphs | center_circle(10%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage_no_subgraphs | center_circle(5%) | 34 |
| wstate_n27-13x13 | magic-aware (random) | passage_no_subgraphs | right_row | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-14x14 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | center_circle(0%) | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(5%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-14x14 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (center) | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | center_circle(5%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | center_circle(10%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | center_circle(0%) | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | center_circle(5%) | 34 |
| wstate_n27-15x15 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (center) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | connectivity | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(10%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-16x16 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-16x16 | gaussian (fine) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | gaussian (fine) | connectivity | right_row | 34 |
| wstate_n27-16x16 | gaussian (fine) | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-16x16 | homogeneous | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | homogeneous | connectivity | right_row | 34 |
| wstate_n27-16x16 | homogeneous | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | homogeneous | cube | right_row | 34 |
| wstate_n27-16x16 | magic-aware (center) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (center) | connectivity | right_row | 34 |
| wstate_n27-16x16 | magic-aware (distance) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (distance) | connectivity | right_row | 34 |
| wstate_n27-16x16 | magic-aware (distance) | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (distance) | cube | right_row | 34 |
| wstate_n27-16x16 | magic-aware (random) | connectivity | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (random) | connectivity | right_row | 34 |
| wstate_n27-16x16 | magic-aware (random) | cube | center_circle(10%) | 34 |
| wstate_n27-16x16 | magic-aware (random) | cube | right_row | 34 |

