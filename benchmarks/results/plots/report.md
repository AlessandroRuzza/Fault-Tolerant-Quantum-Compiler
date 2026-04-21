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

## Success heatmap: safe passage x placement

![Success heatmap: safe passage x placement](13_heatmap_success_safe_vs_placement.png)

## Routing heatmap: safe passage x placement

![Routing heatmap: safe passage x placement](14_heatmap_routing_safe_vs_placement.png)

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
| adder_n64_transpiled-18x18 | magic-aware (distance) | passage | center_circle(0%) | 246 |
| adder_n64_transpiled-19x19 | magic-aware (distance) | passage | center_circle(0%) | 246 |
| adder_n64_transpiled-21x21 | magic-aware (distance) | cube | center_circle(0%) | 246 |
| adder_n64_transpiled-21x21 | magic-aware (random) | cube | center_circle(0%) | 246 |
| adder_n64_transpiled-22x22 | gaussian (fine) | cube | center_circle(5%) | 248 |
| adder_n64_transpiled-23x23 | gaussian (coarse) | cube | center_circle(0%) | 248 |
| adder_n64_transpiled-23x23 | gaussian (fine) | cube | center_circle(0%) | 248 |
| adder_n64_transpiled-24x24 | gaussian (coarse) | cube | center_circle(5%) | 248 |
| adder_n64_transpiled-24x24 | gaussian (fine) | cube | center_circle(5%) | 248 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-7x7 | homogeneous | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | homogeneous | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | right_row | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | right_row | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | right_row | 15 |
| bb84_n8-8x8 | homogeneous | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | homogeneous | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | right_row | 15 |
| bigadder_n18_transpiled-6x6 | gaussian (coarse) | passage | center_circle(0%) | 157 |
| bigadder_n18_transpiled-6x6 | gaussian (coarse) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-6x6 | gaussian (fine) | passage | center_circle(0%) | 157 |
| bigadder_n18_transpiled-6x6 | gaussian (fine) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | gaussian (coarse) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | gaussian (fine) | passage | center_circle(5%) | 157 |
| bigadder_n18_transpiled-7x7 | homogeneous | passage | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (coarse) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | center_circle(0%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | center_circle(5%) | 157 |
| bigadder_n18_transpiled-8x8 | gaussian (fine) | cube | right_row | 157 |
| bigadder_n18_transpiled-8x8 | homogeneous | cube | center_circle(0%) | 157 |
| cat_n130-26x26 | homogeneous | passage | center_circle(0%) | 130 |
| cat_n130-26x26 | homogeneous | passage | right_row | 130 |
| cat_n130-26x26 | magic-aware (distance) | passage | center_circle(0%) | 130 |
| cat_n130-26x26 | magic-aware (distance) | passage | right_row | 130 |
| cat_n130-26x26 | magic-aware (random) | passage | center_circle(0%) | 130 |
| cat_n130-26x26 | magic-aware (random) | passage | right_row | 130 |
| cat_n130-27x27 | homogeneous | passage | center_circle(0%) | 130 |
| cat_n130-27x27 | homogeneous | passage | right_row | 130 |
| cat_n130-27x27 | magic-aware (distance) | passage | center_circle(0%) | 130 |
| cat_n130-27x27 | magic-aware (distance) | passage | right_row | 130 |
| cat_n130-27x27 | magic-aware (random) | passage | center_circle(0%) | 130 |
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
| cat_n130-32x32 | homogeneous | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (coarse) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (fine) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-34x34 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | homogeneous | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (distance) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (random) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (random) | cube | right_row | 130 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | right_row | 19 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-10x10 | homogeneous | passage | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-12x12 | magic-aware (center) | cube | center_circle(5%) | 48 |
| example-5x5 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | cube | right_row | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage | right_row | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | cube | right_row | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | passage | right_row | 51 |
| example-5x5 | homogeneous | cube | center_circle(0%) | 51 |
| example-5x5 | homogeneous | cube | right_row | 51 |
| example-5x5 | homogeneous | passage | center_circle(0%) | 51 |
| example-5x5 | homogeneous | passage | center_circle(5%) | 51 |
| example-5x5 | homogeneous | passage | right_row | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | cube | right_row | 51 |
| example-5x5 | magic-aware (center) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | passage | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | passage | right_row | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | cube | right_row | 51 |
| example-5x5 | magic-aware (distance) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | passage | center_circle(5%) | 51 |
| example-5x5 | magic-aware (distance) | passage | right_row | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage | center_circle(5%) | 51 |
| example-5x5 | magic-aware (random) | passage | right_row | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (coarse) | cube | right_row | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (fine) | cube | right_row | 51 |
| example-6x6 | homogeneous | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (center) | cube | right_row | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (distance) | cube | right_row | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (random) | cube | right_row | 51 |
| ghz_n255-36x36 | homogeneous | passage | center_circle(0%) | 255 |
| ghz_n255-36x36 | homogeneous | passage | right_row | 255 |
| ghz_n255-36x36 | magic-aware (distance) | passage | center_circle(0%) | 255 |
| ghz_n255-36x36 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-36x36 | magic-aware (random) | passage | center_circle(0%) | 255 |
| ghz_n255-36x36 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-37x37 | homogeneous | passage | center_circle(5%) | 255 |
| ghz_n255-37x37 | homogeneous | passage | right_row | 255 |
| ghz_n255-37x37 | magic-aware (distance) | passage | center_circle(5%) | 255 |
| ghz_n255-37x37 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-37x37 | magic-aware (random) | passage | center_circle(5%) | 255 |
| ghz_n255-37x37 | magic-aware (random) | passage | right_row | 255 |
| ghz_n255-38x38 | homogeneous | passage | center_circle(0%) | 255 |
| ghz_n255-38x38 | homogeneous | passage | right_row | 255 |
| ghz_n255-38x38 | magic-aware (distance) | passage | center_circle(0%) | 255 |
| ghz_n255-38x38 | magic-aware (distance) | passage | right_row | 255 |
| ghz_n255-38x38 | magic-aware (random) | passage | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-43x43 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | homogeneous | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-47x47 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | homogeneous | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | right_row | 255 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | right_row | 23 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | center_circle(0%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | center_circle(0%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | right_row | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | right_row | 34 |
| qft_20-10x10 | gaussian (fine) | passage | right_row | 127 |
| qft_20-10x10 | magic-aware (distance) | passage | center_circle(0%) | 127 |
| qft_20-11x11 | gaussian (fine) | passage | right_row | 129 |
| qft_20-12x12 | gaussian (coarse) | cube | right_row | 103 |
| qft_20-13x13 | gaussian (coarse) | cube | center_circle(5%) | 98 |
| wstate_n27-12x12 | gaussian (fine) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-12x12 | homogeneous | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | homogeneous | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | right_row | 34 |

## Best Mapping Table (All Families Exit Code 0)

Only circuit x graph-dimensions where `gaussian`, `homogeneous`, and `magic-aware` all appear among runs with `exit_code = 0`. All configurations tied for the lowest routing steps are listed only from those `exit_code = 0` runs.

CSV export: `best_mapping_by_circuit_dimension_all_families_exit0.csv`

| circuit x dimensions | best mapping | safe passage | magic placement | routing steps |
| --- | --- | --- | --- | ---: |
| adder_n64_transpiled-18x18 | magic-aware (distance) | passage | center_circle(0%) | 246 |
| adder_n64_transpiled-19x19 | magic-aware (distance) | passage | center_circle(0%) | 246 |
| adder_n64_transpiled-21x21 | magic-aware (distance) | cube | center_circle(0%) | 246 |
| adder_n64_transpiled-21x21 | magic-aware (random) | cube | center_circle(0%) | 246 |
| adder_n64_transpiled-22x22 | gaussian (fine) | cube | center_circle(5%) | 248 |
| adder_n64_transpiled-23x23 | gaussian (coarse) | cube | center_circle(0%) | 248 |
| adder_n64_transpiled-23x23 | gaussian (fine) | cube | center_circle(0%) | 248 |
| adder_n64_transpiled-24x24 | gaussian (coarse) | cube | center_circle(5%) | 248 |
| adder_n64_transpiled-24x24 | gaussian (fine) | cube | center_circle(5%) | 248 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-6x6 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-6x6 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-6x6 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (coarse) | passage | right_row | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | gaussian (fine) | passage | right_row | 15 |
| bb84_n8-7x7 | homogeneous | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | homogeneous | passage | center_circle(5%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (center) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (distance) | passage | right_row | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | center_circle(0%) | 15 |
| bb84_n8-7x7 | magic-aware (random) | passage | right_row | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (coarse) | cube | right_row | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | gaussian (fine) | cube | right_row | 15 |
| bb84_n8-8x8 | homogeneous | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | homogeneous | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (center) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (distance) | cube | right_row | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(0%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | center_circle(5%) | 15 |
| bb84_n8-8x8 | magic-aware (random) | cube | right_row | 15 |
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
| cat_n130-32x32 | homogeneous | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | homogeneous | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(0%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | center_circle(5%) | 130 |
| cat_n130-32x32 | magic-aware (random) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (coarse) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | gaussian (coarse) | cube | right_row | 130 |
| cat_n130-34x34 | gaussian (fine) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | gaussian (fine) | cube | right_row | 130 |
| cat_n130-34x34 | homogeneous | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | homogeneous | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (center) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (distance) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (distance) | cube | right_row | 130 |
| cat_n130-34x34 | magic-aware (random) | cube | center_circle(5%) | 130 |
| cat_n130-34x34 | magic-aware (random) | cube | right_row | 130 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (coarse) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | gaussian (fine) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | homogeneous | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (center) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (distance) | passage | right_row | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(0%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | center_circle(5%) | 19 |
| continuous_3_17_13-4x4 | magic-aware (random) | passage | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (coarse) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | gaussian (fine) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | homogeneous | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (center) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (distance) | cube | right_row | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(0%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | center_circle(5%) | 19 |
| continuous_3_17_13-5x5 | magic-aware (random) | cube | right_row | 19 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(0%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-9x9 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (coarse) | passage | right_row | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | center_circle(5%) | 48 |
| dnn_n16-10x10 | gaussian (fine) | passage | right_row | 48 |
| dnn_n16-10x10 | homogeneous | passage | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(0%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | center_circle(5%) | 48 |
| dnn_n16-11x11 | magic-aware (center) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (coarse) | cube | right_row | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | center_circle(5%) | 48 |
| dnn_n16-12x12 | gaussian (fine) | cube | right_row | 48 |
| dnn_n16-12x12 | magic-aware (center) | cube | center_circle(5%) | 48 |
| example-5x5 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | cube | right_row | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (coarse) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (coarse) | passage | right_row | 51 |
| example-5x5 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | cube | right_row | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(0%) | 51 |
| example-5x5 | gaussian (fine) | passage | center_circle(5%) | 51 |
| example-5x5 | gaussian (fine) | passage | right_row | 51 |
| example-5x5 | homogeneous | cube | center_circle(0%) | 51 |
| example-5x5 | homogeneous | cube | right_row | 51 |
| example-5x5 | homogeneous | passage | center_circle(0%) | 51 |
| example-5x5 | homogeneous | passage | center_circle(5%) | 51 |
| example-5x5 | homogeneous | passage | right_row | 51 |
| example-5x5 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | cube | right_row | 51 |
| example-5x5 | magic-aware (center) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (center) | passage | center_circle(5%) | 51 |
| example-5x5 | magic-aware (center) | passage | right_row | 51 |
| example-5x5 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | cube | right_row | 51 |
| example-5x5 | magic-aware (distance) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (distance) | passage | center_circle(5%) | 51 |
| example-5x5 | magic-aware (distance) | passage | right_row | 51 |
| example-5x5 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage | center_circle(0%) | 51 |
| example-5x5 | magic-aware (random) | passage | center_circle(5%) | 51 |
| example-5x5 | magic-aware (random) | passage | right_row | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (coarse) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (coarse) | cube | right_row | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(0%) | 51 |
| example-6x6 | gaussian (fine) | cube | center_circle(5%) | 51 |
| example-6x6 | gaussian (fine) | cube | right_row | 51 |
| example-6x6 | homogeneous | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (center) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (center) | cube | right_row | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (distance) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (distance) | cube | right_row | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(0%) | 51 |
| example-6x6 | magic-aware (random) | cube | center_circle(5%) | 51 |
| example-6x6 | magic-aware (random) | cube | right_row | 51 |
| ghz_n255-43x43 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-43x43 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | homogeneous | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-43x43 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | homogeneous | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(0%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-45x45 | magic-aware (random) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (coarse) | cube | right_row | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | gaussian (fine) | cube | right_row | 255 |
| ghz_n255-47x47 | homogeneous | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | homogeneous | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (center) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (distance) | cube | right_row | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | center_circle(5%) | 255 |
| ghz_n255-47x47 | magic-aware (random) | cube | right_row | 255 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(0%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | center_circle(5%) | 23 |
| ghz_state_n23-11x11 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (coarse) | passage | right_row | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | gaussian (fine) | passage | right_row | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | homogeneous | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (distance) | passage | right_row | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | center_circle(5%) | 23 |
| ghz_state_n23-12x12 | magic-aware (random) | passage | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-13x13 | magic-aware (random) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (coarse) | cube | right_row | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | gaussian (fine) | cube | right_row | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | homogeneous | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (center) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (distance) | cube | right_row | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(0%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | center_circle(5%) | 23 |
| ghz_state_n23-14x14 | magic-aware (random) | cube | right_row | 23 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | center_circle(0%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | center_circle(0%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | center_circle(5%) | 34 |
| qaoa_n6-5x5 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-5x5 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (coarse) | passage | right_row | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | gaussian (fine) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (center) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | center_circle(5%) | 34 |
| qaoa_n6-6x6 | magic-aware (distance) | passage | right_row | 34 |
| qaoa_n6-6x6 | magic-aware (random) | passage | right_row | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (coarse) | cube | right_row | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | gaussian (fine) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (center) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (distance) | cube | right_row | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(0%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | center_circle(5%) | 34 |
| qaoa_n6-7x7 | magic-aware (random) | cube | right_row | 34 |
| qft_20-10x10 | gaussian (fine) | passage | right_row | 127 |
| qft_20-10x10 | magic-aware (distance) | passage | center_circle(0%) | 127 |
| qft_20-11x11 | gaussian (fine) | passage | right_row | 129 |
| qft_20-12x12 | gaussian (coarse) | cube | right_row | 103 |
| qft_20-13x13 | gaussian (coarse) | cube | center_circle(5%) | 98 |
| wstate_n27-12x12 | gaussian (fine) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | gaussian (fine) | passage | right_row | 34 |
| wstate_n27-12x12 | homogeneous | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | homogeneous | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (center) | passage | right_row | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (distance) | passage | center_circle(5%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(0%) | 34 |
| wstate_n27-12x12 | magic-aware (random) | passage | center_circle(5%) | 34 |
| wstate_n27-14x14 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-14x14 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | homogeneous | cube | right_row | 34 |
| wstate_n27-14x14 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-14x14 | magic-aware (random) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (coarse) | cube | right_row | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | gaussian (fine) | cube | right_row | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | homogeneous | cube | right_row | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (center) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (distance) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(0%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | center_circle(5%) | 34 |
| wstate_n27-15x15 | magic-aware (random) | cube | right_row | 34 |

