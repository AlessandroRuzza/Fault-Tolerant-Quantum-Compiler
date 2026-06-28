# cube vs WISQ (WISQ grid)

Both sides evaluated on WISQ's own grid (wisq_x/wisq_y), reused verbatim from `connectivity_summary_all_wisq.csv` — our compiler was forced onto exactly that grid, WISQ was NOT re-run (its native grid is strategy-independent). Lower routing_steps is better.

- Circuits: **258**  (decided: 242, n/a: 16)
- `cube` WIN (fewer routing steps): **19**  LOSS: **128**  TIE: **95**
- Geomean `wisq/cube` routing-step ratio (>1 ⇒ cube better): **0.887**

| circuit | n_qubits | grid | cube steps | wisq steps | wisq/cube | verdict |
|---|---|---|---|---|---|---|
| continuous_3_17_13 | 3 | 7x7 | 17 | 17 | 1.000 | TIE |
| fredkin_n3 | 3 | 7x7 | 10 | 10 | 1.000 | TIE |
| simon_n6 | 3 | 7x7 | 2 | 2 | 1.000 | TIE |
| toffoli_n3 | 3 | 7x7 | 11 | 11 | 1.000 | TIE |
| adder_n4 | 4 | 7x7 | 8 | 8 | 1.000 | TIE |
| vqe_uccsd_n4 | 4 | 7x7 | 87 | 87 | 1.000 | TIE |
| ghz_n5 | 5 | 9x9 | 4 | 4 | 1.000 | TIE |
| graphstate_n5 | 5 | 9x9 | 4 | 4 | 1.000 | TIE |
| grover_n5 | 5 | 9x9 | 209 | 209 | 1.000 | TIE |
| ising_n5 | 5 | 9x9 | 4 | 4 | 1.000 | TIE |
| qaoa_n5 | 5 | 9x9 | 16 | 14 | 0.875 | LOSS |
| qec_en_n5 | 5 | 9x9 | 11 | 11 | 1.000 | TIE |
| qft_n5 | 5 | 9x9 | 14 | 14 | 1.000 | TIE |
| vqe_real_amp_n5 | 5 | 9x9 | 8 | 8 | 1.000 | TIE |
| vqe_su2_n5 | 5 | 9x9 | 8 | 8 | 1.000 | TIE |
| vqe_two_local_n5 | 5 | 9x9 | 17 | 17 | 1.000 | TIE |
| wstate_n5 | 5 | 9x9 | 6 | 6 | 1.000 | TIE |
| multiply_n13 | 6 | 9x9 | 2 | 2 | 1.000 | TIE |
| qaoa_n6 | 6 | 9x9 | 39 | 33 | 0.846 | LOSS |
| qaoa_n6_transpiled | 6 | 9x9 | 39 | 33 | 0.846 | LOSS |
| parallel | 8 | 9x9 | 10 | 10 | 1.000 | TIE |
| t_test | 8 | 9x9 | 110 | 110 | 1.000 | TIE |
| vqe_uccsd_n8 | 8 | 9x9 | 5448 | 5446 | 1.000 | LOSS |
| multiplier_n15 | 9 | 9x9 | 12 | 12 | 1.000 | TIE |
| qpe_n9_transpiled | 9 | 9x9 | 42 | 42 | 1.000 | TIE |
| qram_n20 | 9 | 9x9 | 10 | 8 | 0.800 | LOSS |
| ghz_n10 | 10 | 11x11 | 9 | 9 | 1.000 | TIE |
| graphstate_n10 | 10 | 11x11 | 5 | 4 | 0.800 | LOSS |
| grover_n10 | 10 | 11x11 | 11329 | 11008 | 0.972 | LOSS |
| hhl_n10 | 10 | 11x11 | 72045 | 72039 | 1.000 | LOSS |
| ising_n10 | 10 | 11x11 | 5 | 4 | 0.800 | LOSS |
| qaoa_n10 | 10 | 11x11 | 57 | 46 | 0.807 | LOSS |
| qft_n10 | 10 | 11x11 | 45 | 34 | 0.756 | LOSS |
| vqe_real_amp_n10 | 10 | 11x11 | 13 | 13 | 1.000 | TIE |
| vqe_su2_n10 | 10 | 11x11 | 13 | 13 | 1.000 | TIE |
| vqe_two_local_n10 | 10 | 11x11 | 48 | 39 | 0.812 | LOSS |
| wstate_n10 | 10 | 11x11 | 11 | 11 | 1.000 | TIE |
| seca_n11 | 11 | 11x11 | 23 | 19 | 0.826 | LOSS |
| square_root_n18 | 14 | 11x11 | 29 | 27 | 0.931 | LOSS |
| factor247_n15 | 15 | 11x11 | 353076 |  |  | n/a |
| dnn_n16 | 16 | 11x11 | 118 | 52 | 0.441 | LOSS |
| bigadder_n18_transpiled | 18 | 13x13 | 96 | 88 | 0.917 | LOSS |
| qft_n18 | 18 | 13x13 | 107 | 71 | 0.664 | LOSS |
| 19qubits_511gate_153layers | 19 | 13x13 | 107 | 99 | 0.925 | LOSS |
| 19qubits_521gate_352layers | 19 | 13x13 | 292 | 286 | 0.979 | LOSS |
| grover_n20 | 19 | 13x13 | 2163529 |  |  | n/a |
| ghz_n20 | 20 | 13x13 | 19 | 19 | 1.000 | TIE |
| graphstate_n20 | 20 | 13x13 | 7 | 4 | 0.571 | LOSS |
| ising_n20 | 20 | 13x13 | 6 | 5 | 0.833 | LOSS |
| multiplier_n20 | 20 | 13x13 | 3997 | 3990 | 0.998 | LOSS |
| parallel_big | 20 | 13x13 | 10 | 10 | 1.000 | TIE |
| qaoa_n20 | 20 | 13x13 | 125 | 90 | 0.720 | LOSS |
| qft_20 | 20 | 13x13 | 122 | 82 | 0.672 | LOSS |
| qft_n20 | 20 | 13x13 | 125 | 82 | 0.656 | LOSS |
| vqe_real_amp_n20 | 20 | 13x13 | 23 | 23 | 1.000 | TIE |
| vqe_su2_n20 | 20 | 13x13 | 23 | 23 | 1.000 | TIE |
| vqe_two_local_n20 | 20 | 13x13 | 156 | 101 | 0.647 | LOSS |
| wstate_n20 | 20 | 13x13 | 21 | 21 | 1.000 | TIE |
| bwt_n21 | 21 | 13x13 | 120800 |  |  | n/a |
| ghz_state_n23 | 23 | 13x13 | 22 | 22 | 1.000 | TIE |
| ising_n26 | 26 | 15x15 | 6 | 5 | 0.833 | LOSS |
| 53qubits_155gate_57layers | 27 | 15x15 | 23 | 23 | 1.000 | TIE |
| multiplier_n45 | 27 | 15x15 | 41 | 36 | 0.878 | LOSS |
| wstate_n27 | 27 | 15x15 | 28 | 28 | 1.000 | TIE |
| adder_n28 | 28 | 15x15 | 27 | 24 | 0.889 | LOSS |
| bwt_n37 | 28 | 15x15 | 35209 | 33600 | 0.954 | LOSS |
| ghz_n30 | 30 | 15x15 | 29 | 29 | 1.000 | TIE |
| graphstate_n30 | 30 | 15x15 | 7 | 6 | 0.857 | LOSS |
| ising_n30 | 30 | 15x15 | 6 | 6 | 1.000 | TIE |
| qaoa_n30 | 30 | 15x15 | 240 | 139 | 0.579 | LOSS |
| qft_n30 | 30 | 15x15 | 225 | 135 | 0.600 | LOSS |
| vqe_real_amp_n30 | 30 | 15x15 | 33 | 33 | 1.000 | TIE |
| vqe_su2_n30 | 30 | 15x15 | 33 | 33 | 1.000 | TIE |
| vqe_two_local_n30 | 30 | 15x15 | 307 | 189 | 0.616 | LOSS |
| wstate_n30 | 30 | 15x15 | 31 | 31 | 1.000 | TIE |
| square_root_n45 | 32 | 15x15 | 712 | 570 | 0.801 | LOSS |
| 53qubits_332gate_152layers | 39 | 17x17 | 44 | 41 | 0.932 | LOSS |
| ghz_n40 | 40 | 17x17 | 39 | 39 | 1.000 | TIE |
| graphstate_n40 | 40 | 17x17 | 8 | 5 | 0.625 | LOSS |
| ising_n40 | 40 | 17x17 | 6 | 7 | 1.167 | WIN |
| multiplier_n40 | 40 | 17x17 | 17349 | 17329 | 0.999 | LOSS |
| qaoa_n40 | 40 | 17x17 | 361 | 208 | 0.576 | LOSS |
| qft_n40 | 40 | 17x17 | 311 | 179 | 0.576 | LOSS |
| vqe_real_amp_n40 | 40 | 17x17 | 43 | 43 | 1.000 | TIE |
| vqe_su2_n40 | 40 | 17x17 | 43 | 43 | 1.000 | TIE |
| vqe_two_local_n40 | 40 | 17x17 | 498 | 285 | 0.572 | LOSS |
| wstate_n40 | 40 | 17x17 | 41 | 41 | 1.000 | TIE |
| bwt_n57 | 43 | 17x17 | 65874 |  |  | n/a |
| multiplier_n75 | 45 | 17x17 | 90 | 60 | 0.667 | LOSS |
| ghz_n50 | 50 | 19x19 | 49 | 49 | 1.000 | TIE |
| graphstate_n50 | 50 | 19x19 | 8 | 5 | 0.625 | LOSS |
| ising_n50 | 50 | 19x19 | 6 | 8 | 1.333 | WIN |
| qaoa_n50 | 50 | 19x19 | 515 | 283 | 0.550 | LOSS |
| qft_n50 | 50 | 19x19 | 377 | 221 | 0.586 | LOSS |
| randomcircuit_n50 | 50 | 19x19 | 1813 | 1426 | 0.787 | LOSS |
| synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 75 | 60 | 0.800 | LOSS |
| synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 76 | 58 | 0.763 | LOSS |
| synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 91 | 70 | 0.769 | LOSS |
| synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 91 | 75 | 0.824 | LOSS |
| synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 89 | 69 | 0.775 | LOSS |
| synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 92 | 70 | 0.761 | LOSS |
| synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 143 | 106 | 0.741 | LOSS |
| synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 180 | 136 | 0.756 | LOSS |
| synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 192 | 137 | 0.714 | LOSS |
| synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 186 | 145 | 0.780 | LOSS |
| synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 200 | 151 | 0.755 | LOSS |
| synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 202 | 146 | 0.723 | LOSS |
| synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 191 | 146 | 0.764 | LOSS |
| vqe_real_amp_n50 | 50 | 19x19 | 53 | 53 | 1.000 | TIE |
| vqe_su2_n50 | 50 | 19x19 | 53 | 53 | 1.000 | TIE |
| vqe_two_local_n50 | 50 | 19x19 | 704 | 403 | 0.572 | LOSS |
| wstate_n50 | 50 | 19x19 | 51 | 51 | 1.000 | TIE |
| ghz_n60 | 60 | 19x19 | 59 | 59 | 1.000 | TIE |
| graphstate_n60 | 60 | 19x19 | 9 | 5 | 0.556 | LOSS |
| ising_n60 | 60 | 19x19 | 6 | 9 | 1.500 | WIN |
| multiplier_n60 | 60 | 19x19 | 39741 | 39731 | 1.000 | LOSS |
| qaoa_n60 | 60 | 19x19 | 668 | 383 | 0.573 | LOSS |
| qft_n60 | 60 | 19x19 | 452 | 269 | 0.595 | LOSS |
| vqe_real_amp_n60 | 60 | 19x19 | 63 | 63 | 1.000 | TIE |
| vqe_su2_n60 | 60 | 19x19 | 63 | 63 | 1.000 | TIE |
| vqe_two_local_n60 | 60 | 19x19 | 957 | 580 | 0.606 | LOSS |
| wstate_n60 | 60 | 19x19 | 61 | 61 | 1.000 | TIE |
| adder_n64_transpiled | 64 | 19x19 | 196 | 181 | 0.923 | LOSS |
| qaoa_n64 | 64 | 19x19 | 727 | 428 | 0.589 | LOSS |
| qft_n64 | 64 | 19x19 | 485 | 289 | 0.596 | LOSS |
| ghz_n70 | 70 | 21x21 | 69 | 69 | 1.000 | TIE |
| graphstate_n70 | 70 | 21x21 | 9 | 6 | 0.667 | LOSS |
| ising_n70 | 70 | 21x21 | 6 | 10 | 1.667 | WIN |
| qaoa_n70 | 70 | 21x21 | 855 | 477 | 0.558 | LOSS |
| qft_n70 | 70 | 21x21 | 519 | 317 | 0.611 | LOSS |
| vqe_real_amp_n70 | 70 | 21x21 | 73 | 73 | 1.000 | TIE |
| vqe_su2_n70 | 70 | 21x21 | 73 | 73 | 1.000 | TIE |
| vqe_two_local_n70 | 70 | 21x21 | 1215 | 757 | 0.623 | LOSS |
| wstate_n70 | 70 | 21x21 | 71 | 71 | 1.000 | TIE |
| bwt_n97 | 73 | 21x21 | 130530 |  |  | n/a |
| ghz_n80 | 80 | 21x21 | 79 | 79 | 1.000 | TIE |
| graphstate_n80 | 80 | 21x21 | 10 | 7 | 0.700 | LOSS |
| ising_n80 | 80 | 21x21 | 6 | 11 | 1.833 | WIN |
| multiplier_n80 | 80 | 21x21 | 71441 | 71289 | 0.998 | LOSS |
| qaoa_n80 | 80 | 21x21 | 1033 | 591 | 0.572 | LOSS |
| qft_n80 | 80 | 21x21 | 591 | 352 | 0.596 | LOSS |
| vqe_real_amp_n80 | 80 | 21x21 | 83 | 83 | 1.000 | TIE |
| vqe_su2_n80 | 80 | 21x21 | 83 | 83 | 1.000 | TIE |
| vqe_two_local_n80 | 80 | 21x21 | 1538 | 970 | 0.631 | LOSS |
| wstate_n80 | 80 | 21x21 | 81 | 81 | 1.000 | TIE |
| ghz_n90 | 90 | 23x23 | 89 | 89 | 1.000 | TIE |
| graphstate_n90 | 90 | 23x23 | 10 | 7 | 0.700 | LOSS |
| ising_n90 | 90 | 23x23 | 6 | 13 | 2.167 | WIN |
| qaoa_n90 | 90 | 23x23 | 1246 | 721 | 0.579 | LOSS |
| qft_n90 | 90 | 23x23 | 644 | 394 | 0.612 | LOSS |
| vqe_real_amp_n90 | 90 | 23x23 | 93 | 93 | 1.000 | TIE |
| vqe_su2_n90 | 90 | 23x23 | 93 | 93 | 1.000 | TIE |
| vqe_two_local_n90 | 90 | 23x23 | 1781 | 1134 | 0.637 | LOSS |
| wstate_n90 | 90 | 23x23 | 91 | 91 | 1.000 | TIE |
| ghz_n100 | 100 | 23x23 | 99 | 99 | 1.000 | TIE |
| graphstate_n100 | 100 | 23x23 | 10 | 8 | 0.800 | LOSS |
| ising_n100 | 100 | 23x23 | 6 | 14 | 2.333 | WIN |
| multiplier_n100 | 100 | 23x23 | 111923 |  |  | n/a |
| qaoa_n100 | 100 | 23x23 | 1472 | 876 | 0.595 | LOSS |
| qft_n100 | 100 | 23x23 | 714 | 439 | 0.615 | LOSS |
| randomcircuit_n100 | 100 | 23x23 | 6277 | 4397 | 0.700 | LOSS |
| synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 217 | 141 | 0.650 | LOSS |
| synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 220 | 144 | 0.655 | LOSS |
| synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 298 | 196 | 0.658 | LOSS |
| synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 299 | 187 | 0.625 | LOSS |
| synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 310 | 208 | 0.671 | LOSS |
| synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 326 | 209 | 0.641 | LOSS |
| synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 559 | 384 | 0.687 | LOSS |
| synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 571 | 391 | 0.685 | LOSS |
| synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 588 | 393 | 0.668 | LOSS |
| synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 594 | 392 | 0.660 | LOSS |
| synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 610 | 426 | 0.698 | LOSS |
| synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 606 | 431 | 0.711 | LOSS |
| vqe_real_amp_n100 | 100 | 23x23 | 103 | 103 | 1.000 | TIE |
| vqe_su2_n100 | 100 | 23x23 | 103 | 103 | 1.000 | TIE |
| vqe_two_local_n100 | 100 | 23x23 | 2164 | 1391 | 0.643 | LOSS |
| wstate_n100 | 100 | 23x23 | 101 | 101 | 1.000 | TIE |
| ghz_n125 | 125 | 27x27 | 124 | 124 | 1.000 | TIE |
| graphstate_n125 | 125 | 27x27 | 9 | 8 | 0.889 | LOSS |
| ising_n125 | 125 | 27x27 | 7 | 15 | 2.143 | WIN |
| qaoa_n125 | 125 | 27x27 | 2063 | 1265 | 0.613 | LOSS |
| qft_n125 | 125 | 27x27 | 869 | 527 | 0.606 | LOSS |
| vqe_real_amp_n125 | 125 | 27x27 | 128 | 128 | 1.000 | TIE |
| vqe_su2_n125 | 125 | 27x27 | 128 | 128 | 1.000 | TIE |
| vqe_two_local_n125 | 125 | 27x27 | 3009 | 1993 | 0.662 | LOSS |
| wstate_n125 | 125 | 27x27 | 126 | 126 | 1.000 | TIE |
| qft_n128 | 128 | 27x27 | 894 | 543 | 0.607 | LOSS |
| cat_n130 | 130 | 27x27 | 129 | 129 | 1.000 | TIE |
| bwt_n177 | 133 | 27x27 | 258748 |  |  | n/a |
| ghz_n150 | 150 | 29x29 | 149 | 149 | 1.000 | TIE |
| graphstate_n150 | 150 | 29x29 | 10 | 12 | 1.200 | WIN |
| ising_n150 | 150 | 29x29 | 6 | 19 | 3.167 | WIN |
| qaoa_n150 | 150 | 29x29 | 2751 | 1722 | 0.626 | LOSS |
| qft_n150 | 150 | 29x29 | 1024 | 631 | 0.616 | LOSS |
| vqe_real_amp_n150 | 150 | 29x29 | 153 | 153 | 1.000 | TIE |
| vqe_su2_n150 | 150 | 29x29 | 153 | 153 | 1.000 | TIE |
| vqe_two_local_n150 | 150 | 29x29 | 4049 | 2732 | 0.675 | LOSS |
| wstate_n150 | 150 | 29x29 | 151 | 151 | 1.000 | TIE |
| bv_n280 | 153 | 29x29 | 152 | 152 | 1.000 | TIE |
| ghz_n175 | 175 | 31x31 | 174 | 174 | 1.000 | TIE |
| graphstate_n175 | 175 | 31x31 | 9 | 10 | 1.111 | WIN |
| ising_n175 | 175 | 31x31 | 6 | 20 | 3.333 | WIN |
| qaoa_n175 | 175 | 31x31 | 3472 | 2259 | 0.651 | LOSS |
| qft_n175 | 175 | 31x31 | 1178 | 723 | 0.614 | LOSS |
| vqe_real_amp_n175 | 175 | 31x31 | 178 | 178 | 1.000 | TIE |
| vqe_su2_n175 | 175 | 31x31 | 178 | 178 | 1.000 | TIE |
| vqe_two_local_n175 | 175 | 31x31 | 5187 | 3552 | 0.685 | LOSS |
| wstate_n175 | 175 | 31x31 | 176 | 176 | 1.000 | TIE |
| ghz_n200 | 200 | 33x33 | 199 | 199 | 1.000 | TIE |
| graphstate_n200 | 200 | 33x33 | 11 | 12 | 1.091 | WIN |
| ising_n200 | 200 | 33x33 | 6 | 22 | 3.667 | WIN |
| multiplier_n200 | 200 | 33x33 | 450263 |  |  | n/a |
| qaoa_n200 | 200 | 33x33 | 4314 | 2844 | 0.659 | LOSS |
| qft_n200 | 200 | 33x33 | 1342 | 822 | 0.613 | LOSS |
| randomcircuit_n200 | 200 | 33x33 | 17102 |  |  | n/a |
| synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 614 | 419 | 0.682 | LOSS |
| synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 596 | 384 | 0.644 | LOSS |
| synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 858 | 605 | 0.705 | LOSS |
| synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 868 | 605 | 0.697 | LOSS |
| synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 888 | 647 | 0.729 | LOSS |
| synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 881 | 647 | 0.734 | LOSS |
| synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 1645 | 1153 | 0.701 | LOSS |
| synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 1592 | 1161 | 0.729 | LOSS |
| synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 1729 | 1248 | 0.722 | LOSS |
| synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 1675 | 1251 | 0.747 | LOSS |
| synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 1783 | 1402 | 0.786 | LOSS |
| synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 1816 | 1405 | 0.774 | LOSS |
| vqe_real_amp_n200 | 200 | 33x33 | 203 | 203 | 1.000 | TIE |
| vqe_su2_n200 | 200 | 33x33 | 203 | 203 | 1.000 | TIE |
| vqe_two_local_n200 | 200 | 33x33 | 6391 | 4464 | 0.698 | LOSS |
| wstate_n200 | 200 | 33x33 | 201 | 201 | 1.000 | TIE |
| ghz_n255 | 255 | 35x35 | 254 | 254 | 1.000 | TIE |
| ghz_state_n255 | 255 | 35x35 | 254 | 254 | 1.000 | TIE |
| cat_n260 | 260 | 37x37 | 259 | 259 | 1.000 | TIE |
| ghz_n300 | 300 | 39x39 | 299 | 299 | 1.000 | TIE |
| graphstate_n300 | 300 | 39x39 | 13 | 17 | 1.308 | WIN |
| ising_n300 | 300 | 39x39 | 6 | 33 | 5.500 | WIN |
| multiplier_n300 | 300 | 39x39 | 1014412 |  |  | n/a |
| qaoa_n300 | 300 | 39x39 | 8130 | 5908 | 0.727 | LOSS |
| qft_n300 | 300 | 39x39 | 2000 | 1224 | 0.612 | LOSS |
| vqe_real_amp_n300 | 300 | 39x39 | 303 | 303 | 1.000 | TIE |
| vqe_su2_n300 | 300 | 39x39 | 303 | 303 | 1.000 | TIE |
| vqe_two_local_n300 | 300 | 39x39 | 12348 |  |  | n/a |
| wstate_n300 | 300 | 39x39 | 301 | 301 | 1.000 | TIE |
| qft_n320 | 320 | 39x39 | 10997 |  |  | n/a |
| ghz_n400 | 400 | 43x43 | 399 | 399 | 1.000 | TIE |
| graphstate_n400 | 400 | 43x43 | 11 | 20 | 1.818 | WIN |
| ising_n400 | 400 | 43x43 | 7 | 42 | 6.000 | WIN |
| multiplier_n400 | 400 | 43x43 | 1815598 |  |  | n/a |
| qaoa_n400 | 400 | 43x43 | 12992 |  |  | n/a |
| qft_n400 | 400 | 43x43 | 2658 | 1654 | 0.622 | LOSS |
| randomcircuit_n400 | 400 | 43x43 | 149699 |  |  | n/a |
| vqe_real_amp_n400 | 400 | 43x43 | 403 | 403 | 1.000 | TIE |
| vqe_su2_n400 | 400 | 43x43 | 403 | 403 | 1.000 | TIE |
| vqe_two_local_n400 | 400 | 43x43 | 19691 |  |  | n/a |
| wstate_n400 | 400 | 43x43 | 401 | 401 | 1.000 | TIE |
| ising_n420 | 420 | 45x45 | 6 | 44 | 7.333 | WIN |
| adder_n433 | 433 | 45x45 | 252 | 249 | 0.988 | LOSS |
