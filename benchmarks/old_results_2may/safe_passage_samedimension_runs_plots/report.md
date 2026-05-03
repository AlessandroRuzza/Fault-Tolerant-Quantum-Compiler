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

## Experiment set: all mappings

![Experiment set: all mappings](22_experiment_set_routing_all_mappings.png)

## Best Mapping Table

Only circuit x graph-dimensions where `gaussian`, `homogeneous`, and `magic-aware` all appear in the runs. All configurations tied for the lowest routing steps are listed among successful runs with routing steps available.

CSV export: `best_mapping_by_circuit_dimension.csv`

| circuit x dimensions | best mapping | safe passage | magic placement | routing steps |
| --- | --- | --- | --- | ---: |
| adder_n64_transpiled-19x19 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 255 |
| bb84_n8-6x6 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | homogeneous | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 161 |
| cat_n130-32x32 | gaussian (coarse) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | connectivity | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | passage | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | passage_no_subgraphs | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(5%) | 130 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| dnn_n16-10x10 | gaussian (coarse) | connectivity | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| example-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | homogeneous | connectivity | center_circle(5%) | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| ghz_n255-44x44 | homogeneous | connectivity | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-44x44 | homogeneous | passage_no_subgraphs | center_circle(5%) | 255 |
| ghz_state_n23-13x13 | gaussian (coarse) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| parallel-8x8 | homogeneous | passage_no_subgraphs | center_circle(5%) | 70 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 34 |
| qft_20-13x13 | magic-aware (center) | connectivity | center_circle(5%) | 161 |
| wstate_n27-12x12 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 34 |

## Best Mapping Table (All Families Exit Code 0)

Only circuit x graph-dimensions where `gaussian`, `homogeneous`, and `magic-aware` all appear among runs with `exit_code = 0`. All configurations tied for the lowest routing steps are listed only from those `exit_code = 0` runs.

CSV export: `best_mapping_by_circuit_dimension_all_families_exit0.csv`

| circuit x dimensions | best mapping | safe passage | magic placement | routing steps |
| --- | --- | --- | --- | ---: |
| adder_n64_transpiled-19x19 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 255 |
| bb84_n8-6x6 | gaussian (coarse) | connectivity | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 15 |
| bb84_n8-6x6 | magic-aware (center) | connectivity | center_circle(5%) | 15 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | homogeneous | passage_no_subgraphs | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | connectivity | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage | center_circle(5%) | 161 |
| bigadder_n18_transpiled-7x7 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 161 |
| cat_n130-32x32 | gaussian (coarse) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | connectivity | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | passage | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | passage_no_subgraphs | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(5%) | 130 |
| continuous_3_17_13-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 19 |
| dnn_n16-10x10 | gaussian (coarse) | connectivity | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 48 |
| dnn_n16-10x10 | homogeneous | passage_no_subgraphs | center_circle(5%) | 48 |
| example-5x5 | gaussian (coarse) | connectivity | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | homogeneous | connectivity | center_circle(5%) | 51 |
| example-5x5 | homogeneous | passage_no_subgraphs | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | connectivity | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | passage_no_subgraphs | center_circle(5%) | 51 |
| ghz_state_n23-13x13 | gaussian (coarse) | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | connectivity | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | passage_no_subgraphs | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | connectivity | center_circle(5%) | 23 |
| parallel-8x8 | homogeneous | passage_no_subgraphs | center_circle(5%) | 70 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage_no_subgraphs | center_circle(5%) | 34 |
| qft_20-13x13 | magic-aware (center) | connectivity | center_circle(5%) | 161 |

