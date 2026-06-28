# random vs WISQ (WISQ grid)

Both sides evaluated on WISQ's own grid (wisq_x/wisq_y), reused verbatim from `connectivity_summary_all_wisq.csv` — our compiler was forced onto exactly that grid, WISQ was NOT re-run (its native grid is strategy-independent). Lower routing_steps is better.

- Circuits: **258**  (decided: 242, n/a: 16)
- `random` WIN (fewer routing steps): **0**  LOSS: **192**  TIE: **50**
- Geomean `wisq/random` routing-step ratio (>1 ⇒ random better): **0.771**

| circuit | n_qubits | grid | random steps | wisq steps | wisq/random | verdict |
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
| qaoa_n5 | 5 | 9x9 | 18 | 14 | 0.778 | LOSS |
| qec_en_n5 | 5 | 9x9 | 11 | 11 | 1.000 | TIE |
| qft_n5 | 5 | 9x9 | 14 | 14 | 1.000 | TIE |
| vqe_real_amp_n5 | 5 | 9x9 | 10 | 8 | 0.800 | LOSS |
| vqe_su2_n5 | 5 | 9x9 | 8 | 8 | 1.000 | TIE |
| vqe_two_local_n5 | 5 | 9x9 | 17 | 17 | 1.000 | TIE |
| wstate_n5 | 5 | 9x9 | 6 | 6 | 1.000 | TIE |
| multiply_n13 | 6 | 9x9 | 2 | 2 | 1.000 | TIE |
| qaoa_n6 | 6 | 9x9 | 33 | 33 | 1.000 | TIE |
| qaoa_n6_transpiled | 6 | 9x9 | 39 | 33 | 0.846 | LOSS |
| parallel | 8 | 9x9 | 15 | 10 | 0.667 | LOSS |
| t_test | 8 | 9x9 | 110 | 110 | 1.000 | TIE |
| vqe_uccsd_n8 | 8 | 9x9 | 5451 | 5446 | 0.999 | LOSS |
| multiplier_n15 | 9 | 9x9 | 12 | 12 | 1.000 | TIE |
| qpe_n9_transpiled | 9 | 9x9 | 42 | 42 | 1.000 | TIE |
| qram_n20 | 9 | 9x9 | 8 | 8 | 1.000 | TIE |
| ghz_n10 | 10 | 11x11 | 9 | 9 | 1.000 | TIE |
| graphstate_n10 | 10 | 11x11 | 4 | 4 | 1.000 | TIE |
| grover_n10 | 10 | 11x11 | 11059 | 11008 | 0.995 | LOSS |
| hhl_n10 | 10 | 11x11 | 72049 | 72039 | 1.000 | LOSS |
| ising_n10 | 10 | 11x11 | 8 | 4 | 0.500 | LOSS |
| qaoa_n10 | 10 | 11x11 | 52 | 46 | 0.885 | LOSS |
| qft_n10 | 10 | 11x11 | 34 | 34 | 1.000 | TIE |
| vqe_real_amp_n10 | 10 | 11x11 | 14 | 13 | 0.929 | LOSS |
| vqe_su2_n10 | 10 | 11x11 | 16 | 13 | 0.812 | LOSS |
| vqe_two_local_n10 | 10 | 11x11 | 54 | 39 | 0.722 | LOSS |
| wstate_n10 | 10 | 11x11 | 12 | 11 | 0.917 | LOSS |
| seca_n11 | 11 | 11x11 | 19 | 19 | 1.000 | TIE |
| square_root_n18 | 14 | 11x11 | 40 | 27 | 0.675 | LOSS |
| factor247_n15 | 15 | 11x11 | 350583 |  |  | n/a |
| dnn_n16 | 16 | 11x11 | 118 | 52 | 0.441 | LOSS |
| bigadder_n18_transpiled | 18 | 13x13 | 93 | 88 | 0.946 | LOSS |
| qft_n18 | 18 | 13x13 | 80 | 71 | 0.887 | LOSS |
| 19qubits_511gate_153layers | 19 | 13x13 | 102 | 99 | 0.971 | LOSS |
| 19qubits_521gate_352layers | 19 | 13x13 | 287 | 286 | 0.997 | LOSS |
| grover_n20 | 19 | 13x13 | 2147625 |  |  | n/a |
| ghz_n20 | 20 | 13x13 | 19 | 19 | 1.000 | TIE |
| graphstate_n20 | 20 | 13x13 | 5 | 4 | 0.800 | LOSS |
| ising_n20 | 20 | 13x13 | 8 | 5 | 0.625 | LOSS |
| multiplier_n20 | 20 | 13x13 | 3990 | 3990 | 1.000 | TIE |
| parallel_big | 20 | 13x13 | 18 | 10 | 0.556 | LOSS |
| qaoa_n20 | 20 | 13x13 | 124 | 90 | 0.726 | LOSS |
| qft_20 | 20 | 13x13 | 115 | 82 | 0.713 | LOSS |
| qft_n20 | 20 | 13x13 | 102 | 82 | 0.804 | LOSS |
| vqe_real_amp_n20 | 20 | 13x13 | 27 | 23 | 0.852 | LOSS |
| vqe_su2_n20 | 20 | 13x13 | 24 | 23 | 0.958 | LOSS |
| vqe_two_local_n20 | 20 | 13x13 | 146 | 101 | 0.692 | LOSS |
| wstate_n20 | 20 | 13x13 | 24 | 21 | 0.875 | LOSS |
| bwt_n21 | 21 | 13x13 | 117200 |  |  | n/a |
| ghz_state_n23 | 23 | 13x13 | 22 | 22 | 1.000 | TIE |
| ising_n26 | 26 | 15x15 | 10 | 5 | 0.500 | LOSS |
| 53qubits_155gate_57layers | 27 | 15x15 | 23 | 23 | 1.000 | TIE |
| multiplier_n45 | 27 | 15x15 | 78 | 36 | 0.462 | LOSS |
| wstate_n27 | 27 | 15x15 | 29 | 28 | 0.966 | LOSS |
| adder_n28 | 28 | 15x15 | 26 | 24 | 0.923 | LOSS |
| bwt_n37 | 28 | 15x15 | 36024 | 33600 | 0.933 | LOSS |
| ghz_n30 | 30 | 15x15 | 29 | 29 | 1.000 | TIE |
| graphstate_n30 | 30 | 15x15 | 8 | 6 | 0.750 | LOSS |
| ising_n30 | 30 | 15x15 | 13 | 6 | 0.462 | LOSS |
| qaoa_n30 | 30 | 15x15 | 221 | 139 | 0.629 | LOSS |
| qft_n30 | 30 | 15x15 | 193 | 135 | 0.699 | LOSS |
| vqe_real_amp_n30 | 30 | 15x15 | 38 | 33 | 0.868 | LOSS |
| vqe_su2_n30 | 30 | 15x15 | 39 | 33 | 0.846 | LOSS |
| vqe_two_local_n30 | 30 | 15x15 | 250 | 189 | 0.756 | LOSS |
| wstate_n30 | 30 | 15x15 | 33 | 31 | 0.939 | LOSS |
| square_root_n45 | 32 | 15x15 | 1045 | 570 | 0.545 | LOSS |
| 53qubits_332gate_152layers | 39 | 17x17 | 41 | 41 | 1.000 | TIE |
| ghz_n40 | 40 | 17x17 | 39 | 39 | 1.000 | TIE |
| graphstate_n40 | 40 | 17x17 | 8 | 5 | 0.625 | LOSS |
| ising_n40 | 40 | 17x17 | 11 | 7 | 0.636 | LOSS |
| multiplier_n40 | 40 | 17x17 | 17334 | 17329 | 1.000 | LOSS |
| qaoa_n40 | 40 | 17x17 | 336 | 208 | 0.619 | LOSS |
| qft_n40 | 40 | 17x17 | 291 | 179 | 0.615 | LOSS |
| vqe_real_amp_n40 | 40 | 17x17 | 44 | 43 | 0.977 | LOSS |
| vqe_su2_n40 | 40 | 17x17 | 49 | 43 | 0.878 | LOSS |
| vqe_two_local_n40 | 40 | 17x17 | 416 | 285 | 0.685 | LOSS |
| wstate_n40 | 40 | 17x17 | 44 | 41 | 0.932 | LOSS |
| bwt_n57 | 43 | 17x17 | 67879 |  |  | n/a |
| multiplier_n75 | 45 | 17x17 | 178 | 60 | 0.337 | LOSS |
| ghz_n50 | 50 | 19x19 | 49 | 49 | 1.000 | TIE |
| graphstate_n50 | 50 | 19x19 | 9 | 5 | 0.556 | LOSS |
| ising_n50 | 50 | 19x19 | 15 | 8 | 0.533 | LOSS |
| qaoa_n50 | 50 | 19x19 | 468 | 283 | 0.605 | LOSS |
| qft_n50 | 50 | 19x19 | 346 | 221 | 0.639 | LOSS |
| randomcircuit_n50 | 50 | 19x19 | 1981 | 1426 | 0.720 | LOSS |
| synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 93 | 60 | 0.645 | LOSS |
| synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 96 | 58 | 0.604 | LOSS |
| synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 100 | 70 | 0.700 | LOSS |
| synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 92 | 75 | 0.815 | LOSS |
| synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 103 | 69 | 0.670 | LOSS |
| synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 95 | 70 | 0.737 | LOSS |
| synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 139 | 106 | 0.763 | LOSS |
| synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 190 | 136 | 0.716 | LOSS |
| synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 179 | 137 | 0.765 | LOSS |
| synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 212 | 145 | 0.684 | LOSS |
| synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 198 | 151 | 0.763 | LOSS |
| synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19x19 | 185 | 146 | 0.789 | LOSS |
| synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19x19 | 191 | 146 | 0.764 | LOSS |
| vqe_real_amp_n50 | 50 | 19x19 | 58 | 53 | 0.914 | LOSS |
| vqe_su2_n50 | 50 | 19x19 | 55 | 53 | 0.964 | LOSS |
| vqe_two_local_n50 | 50 | 19x19 | 591 | 403 | 0.682 | LOSS |
| wstate_n50 | 50 | 19x19 | 56 | 51 | 0.911 | LOSS |
| ghz_n60 | 60 | 19x19 | 59 | 59 | 1.000 | TIE |
| graphstate_n60 | 60 | 19x19 | 9 | 5 | 0.556 | LOSS |
| ising_n60 | 60 | 19x19 | 19 | 9 | 0.474 | LOSS |
| multiplier_n60 | 60 | 19x19 | 39756 | 39731 | 0.999 | LOSS |
| qaoa_n60 | 60 | 19x19 | 591 | 383 | 0.648 | LOSS |
| qft_n60 | 60 | 19x19 | 445 | 269 | 0.604 | LOSS |
| vqe_real_amp_n60 | 60 | 19x19 | 73 | 63 | 0.863 | LOSS |
| vqe_su2_n60 | 60 | 19x19 | 76 | 63 | 0.829 | LOSS |
| vqe_two_local_n60 | 60 | 19x19 | 885 | 580 | 0.655 | LOSS |
| wstate_n60 | 60 | 19x19 | 62 | 61 | 0.984 | LOSS |
| adder_n64_transpiled | 64 | 19x19 | 191 | 181 | 0.948 | LOSS |
| qaoa_n64 | 64 | 19x19 | 703 | 428 | 0.609 | LOSS |
| qft_n64 | 64 | 19x19 | 464 | 289 | 0.623 | LOSS |
| ghz_n70 | 70 | 21x21 | 69 | 69 | 1.000 | TIE |
| graphstate_n70 | 70 | 21x21 | 10 | 6 | 0.600 | LOSS |
| ising_n70 | 70 | 21x21 | 19 | 10 | 0.526 | LOSS |
| qaoa_n70 | 70 | 21x21 | 754 | 477 | 0.633 | LOSS |
| qft_n70 | 70 | 21x21 | 489 | 317 | 0.648 | LOSS |
| vqe_real_amp_n70 | 70 | 21x21 | 85 | 73 | 0.859 | LOSS |
| vqe_su2_n70 | 70 | 21x21 | 87 | 73 | 0.839 | LOSS |
| vqe_two_local_n70 | 70 | 21x21 | 1061 | 757 | 0.713 | LOSS |
| wstate_n70 | 70 | 21x21 | 72 | 71 | 0.986 | LOSS |
| bwt_n97 | 73 | 21x21 | 136993 |  |  | n/a |
| ghz_n80 | 80 | 21x21 | 79 | 79 | 1.000 | TIE |
| graphstate_n80 | 80 | 21x21 | 13 | 7 | 0.538 | LOSS |
| ising_n80 | 80 | 21x21 | 24 | 11 | 0.458 | LOSS |
| multiplier_n80 | 80 | 21x21 | 71387 | 71289 | 0.999 | LOSS |
| qaoa_n80 | 80 | 21x21 | 963 | 591 | 0.614 | LOSS |
| qft_n80 | 80 | 21x21 | 542 | 352 | 0.649 | LOSS |
| vqe_real_amp_n80 | 80 | 21x21 | 94 | 83 | 0.883 | LOSS |
| vqe_su2_n80 | 80 | 21x21 | 97 | 83 | 0.856 | LOSS |
| vqe_two_local_n80 | 80 | 21x21 | 1357 | 970 | 0.715 | LOSS |
| wstate_n80 | 80 | 21x21 | 84 | 81 | 0.964 | LOSS |
| ghz_n90 | 90 | 23x23 | 89 | 89 | 1.000 | TIE |
| graphstate_n90 | 90 | 23x23 | 10 | 7 | 0.700 | LOSS |
| ising_n90 | 90 | 23x23 | 23 | 13 | 0.565 | LOSS |
| qaoa_n90 | 90 | 23x23 | 1190 | 721 | 0.606 | LOSS |
| qft_n90 | 90 | 23x23 | 611 | 394 | 0.645 | LOSS |
| vqe_real_amp_n90 | 90 | 23x23 | 103 | 93 | 0.903 | LOSS |
| vqe_su2_n90 | 90 | 23x23 | 108 | 93 | 0.861 | LOSS |
| vqe_two_local_n90 | 90 | 23x23 | 1613 | 1134 | 0.703 | LOSS |
| wstate_n90 | 90 | 23x23 | 91 | 91 | 1.000 | TIE |
| ghz_n100 | 100 | 23x23 | 99 | 99 | 1.000 | TIE |
| graphstate_n100 | 100 | 23x23 | 14 | 8 | 0.571 | LOSS |
| ising_n100 | 100 | 23x23 | 26 | 14 | 0.538 | LOSS |
| multiplier_n100 | 100 | 23x23 | 111944 |  |  | n/a |
| qaoa_n100 | 100 | 23x23 | 1406 | 876 | 0.623 | LOSS |
| qft_n100 | 100 | 23x23 | 706 | 439 | 0.622 | LOSS |
| randomcircuit_n100 | 100 | 23x23 | 6365 | 4397 | 0.691 | LOSS |
| synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 305 | 141 | 0.462 | LOSS |
| synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 335 | 144 | 0.430 | LOSS |
| synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 331 | 196 | 0.592 | LOSS |
| synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 328 | 187 | 0.570 | LOSS |
| synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 322 | 208 | 0.646 | LOSS |
| synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 326 | 209 | 0.641 | LOSS |
| synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 636 | 384 | 0.604 | LOSS |
| synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 670 | 391 | 0.584 | LOSS |
| synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 650 | 393 | 0.605 | LOSS |
| synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 648 | 392 | 0.605 | LOSS |
| synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 23x23 | 644 | 426 | 0.661 | LOSS |
| synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 23x23 | 637 | 431 | 0.677 | LOSS |
| vqe_real_amp_n100 | 100 | 23x23 | 114 | 103 | 0.904 | LOSS |
| vqe_su2_n100 | 100 | 23x23 | 113 | 103 | 0.912 | LOSS |
| vqe_two_local_n100 | 100 | 23x23 | 1881 | 1391 | 0.740 | LOSS |
| wstate_n100 | 100 | 23x23 | 104 | 101 | 0.971 | LOSS |
| ghz_n125 | 125 | 27x27 | 124 | 124 | 1.000 | TIE |
| graphstate_n125 | 125 | 27x27 | 17 | 8 | 0.471 | LOSS |
| ising_n125 | 125 | 27x27 | 26 | 15 | 0.577 | LOSS |
| qaoa_n125 | 125 | 27x27 | 1945 | 1265 | 0.650 | LOSS |
| qft_n125 | 125 | 27x27 | 856 | 527 | 0.616 | LOSS |
| vqe_real_amp_n125 | 125 | 27x27 | 138 | 128 | 0.928 | LOSS |
| vqe_su2_n125 | 125 | 27x27 | 135 | 128 | 0.948 | LOSS |
| vqe_two_local_n125 | 125 | 27x27 | 2631 | 1993 | 0.758 | LOSS |
| wstate_n125 | 125 | 27x27 | 129 | 126 | 0.977 | LOSS |
| qft_n128 | 128 | 27x27 | 835 | 543 | 0.650 | LOSS |
| cat_n130 | 130 | 27x27 | 129 | 129 | 1.000 | TIE |
| bwt_n177 | 133 | 27x27 | 268925 |  |  | n/a |
| ghz_n150 | 150 | 29x29 | 149 | 149 | 1.000 | TIE |
| graphstate_n150 | 150 | 29x29 | 17 | 12 | 0.706 | LOSS |
| ising_n150 | 150 | 29x29 | 29 | 19 | 0.655 | LOSS |
| qaoa_n150 | 150 | 29x29 | 2682 | 1722 | 0.642 | LOSS |
| qft_n150 | 150 | 29x29 | 972 | 631 | 0.649 | LOSS |
| vqe_real_amp_n150 | 150 | 29x29 | 163 | 153 | 0.939 | LOSS |
| vqe_su2_n150 | 150 | 29x29 | 164 | 153 | 0.933 | LOSS |
| vqe_two_local_n150 | 150 | 29x29 | 3536 | 2732 | 0.773 | LOSS |
| wstate_n150 | 150 | 29x29 | 154 | 151 | 0.981 | LOSS |
| bv_n280 | 153 | 29x29 | 152 | 152 | 1.000 | TIE |
| ghz_n175 | 175 | 31x31 | 174 | 174 | 1.000 | TIE |
| graphstate_n175 | 175 | 31x31 | 20 | 10 | 0.500 | LOSS |
| ising_n175 | 175 | 31x31 | 33 | 20 | 0.606 | LOSS |
| qaoa_n175 | 175 | 31x31 | 3391 | 2259 | 0.666 | LOSS |
| qft_n175 | 175 | 31x31 | 1114 | 723 | 0.649 | LOSS |
| vqe_real_amp_n175 | 175 | 31x31 | 198 | 178 | 0.899 | LOSS |
| vqe_su2_n175 | 175 | 31x31 | 196 | 178 | 0.908 | LOSS |
| vqe_two_local_n175 | 175 | 31x31 | 4582 | 3552 | 0.775 | LOSS |
| wstate_n175 | 175 | 31x31 | 177 | 176 | 0.994 | LOSS |
| ghz_n200 | 200 | 33x33 | 199 | 199 | 1.000 | TIE |
| graphstate_n200 | 200 | 33x33 | 20 | 12 | 0.600 | LOSS |
| ising_n200 | 200 | 33x33 | 34 | 22 | 0.647 | LOSS |
| multiplier_n200 | 200 | 33x33 | 450314 |  |  | n/a |
| qaoa_n200 | 200 | 33x33 | 4193 | 2844 | 0.678 | LOSS |
| qft_n200 | 200 | 33x33 | 1272 | 822 | 0.646 | LOSS |
| randomcircuit_n200 | 200 | 33x33 | 17861 |  |  | n/a |
| synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 925 | 419 | 0.453 | LOSS |
| synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 894 | 384 | 0.430 | LOSS |
| synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 933 | 605 | 0.648 | LOSS |
| synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 948 | 605 | 0.638 | LOSS |
| synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 924 | 647 | 0.700 | LOSS |
| synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 935 | 647 | 0.692 | LOSS |
| synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 1857 | 1153 | 0.621 | LOSS |
| synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 1835 | 1161 | 0.633 | LOSS |
| synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 1879 | 1248 | 0.664 | LOSS |
| synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 1873 | 1251 | 0.668 | LOSS |
| synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 33x33 | 1879 | 1402 | 0.746 | LOSS |
| synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 33x33 | 1882 | 1405 | 0.747 | LOSS |
| vqe_real_amp_n200 | 200 | 33x33 | 213 | 203 | 0.953 | LOSS |
| vqe_su2_n200 | 200 | 33x33 | 212 | 203 | 0.958 | LOSS |
| vqe_two_local_n200 | 200 | 33x33 | 5824 | 4464 | 0.766 | LOSS |
| wstate_n200 | 200 | 33x33 | 208 | 201 | 0.966 | LOSS |
| ghz_n255 | 255 | 35x35 | 254 | 254 | 1.000 | TIE |
| ghz_state_n255 | 255 | 35x35 | 254 | 254 | 1.000 | TIE |
| cat_n260 | 260 | 37x37 | 259 | 259 | 1.000 | TIE |
| ghz_n300 | 300 | 39x39 | 299 | 299 | 1.000 | TIE |
| graphstate_n300 | 300 | 39x39 | 30 | 17 | 0.567 | LOSS |
| ising_n300 | 300 | 39x39 | 44 | 33 | 0.750 | LOSS |
| multiplier_n300 | 300 | 39x39 | 1014379 |  |  | n/a |
| qaoa_n300 | 300 | 39x39 | 7914 | 5908 | 0.747 | LOSS |
| qft_n300 | 300 | 39x39 | 1848 | 1224 | 0.662 | LOSS |
| vqe_real_amp_n300 | 300 | 39x39 | 326 | 303 | 0.929 | LOSS |
| vqe_su2_n300 | 300 | 39x39 | 320 | 303 | 0.947 | LOSS |
| vqe_two_local_n300 | 300 | 39x39 | 11288 |  |  | n/a |
| wstate_n300 | 300 | 39x39 | 306 | 301 | 0.984 | LOSS |
| qft_n320 | 320 | 39x39 | 8812 |  |  | n/a |
| ghz_n400 | 400 | 43x43 | 399 | 399 | 1.000 | TIE |
| graphstate_n400 | 400 | 43x43 | 32 | 20 | 0.625 | LOSS |
| ising_n400 | 400 | 43x43 | 56 | 42 | 0.750 | LOSS |
| multiplier_n400 | 400 | 43x43 | 1816509 |  |  | n/a |
| qaoa_n400 | 400 | 43x43 | 12848 |  |  | n/a |
| qft_n400 | 400 | 43x43 | 2439 | 1654 | 0.678 | LOSS |
| randomcircuit_n400 | 400 | 43x43 | 241582 |  |  | n/a |
| vqe_real_amp_n400 | 400 | 43x43 | 425 | 403 | 0.948 | LOSS |
| vqe_su2_n400 | 400 | 43x43 | 419 | 403 | 0.962 | LOSS |
| vqe_two_local_n400 | 400 | 43x43 | 18372 |  |  | n/a |
| wstate_n400 | 400 | 43x43 | 403 | 401 | 0.995 | LOSS |
| ising_n420 | 420 | 45x45 | 59 | 44 | 0.746 | LOSS |
| adder_n433 | 433 | 45x45 | 265 | 249 | 0.940 | LOSS |
