# Risultati WISQ-native MENO 5 — connectivity

**connectivity con i pesi finali** (gaussian/fine, safe_passage=connectivity, border=15, sigma=0.7, mapped=20, cnot_high=8, magic=0, ext=−15, bfs=0.70, center_circle, packing, smart_t_routing, patience=3).
Griglia fissa a `wisq_native_side −5` per lato; WISQ resta sulla sua griglia nativa come riferimento.
Dati: `conn_wisq_minus5_wisqconn_merged.csv` — CSV corrente con **258 righe**.

---

## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 258 | — |
| **Nostro mapping FALLISCE a −5** | 12 | — |
| **Mappiamo a −5 con successo** | 246 | — |
| ↳ WISQ va in timeout sulla sua nativa (noi vinciamo) | 16 | — |
| ↳ Entrambi completano | 230 | — |
|   ↳ Noi vinciamo su steps | 28 (ratio mediana 2.00×) | 24 (86%) |
|   ↳ Pareggio su steps | 97 | 83 (86%) |
|   ↳ WISQ vince su steps | 105 (ratio mediana 0.56×) | 101 (96%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **127 / 258 (49.2%)** | — |
| ↳ Mappiamo a −5, WISQ va in timeout | 16 / 258 (6.2%) | — |
| ↳ Vinciamo su steps (WISQ completa) | 28 / 258 (10.9%) | — |
| ↳ Pareggio su steps, noi più veloci | 83 / 258 (32.2%) | — |
| | | |
| **SCONFITTE NOSTRE (mapping fallito a −5)** | **12 / 258 (4.7%)** | — |

Circuiti dove non mappiamo a −5: `adder_n4`, `bigadder_n18_transpiled`, `factor247_n15`, `fredkin_n3`, `grover_n10`, `grover_n5`, `hhl_n10`, `qpe_n9_transpiled`, `qram_n20`, `toffoli_n3`, `vqe_uccsd_n4`, `vqe_uccsd_n8`.

---

## Footprint: quanto scendiamo sotto WISQ

| Δ lati sotto WISQ (`dim_diff_side`) | Circuiti |
|---|---|
| +5 | 243 (target) |
| −3 | 1 (`bv_n280`) |
| +1 | 1 (`multiplier_n75`) |
| +3 | 1 (`multiplier_n45`) |

**Risparmio di qubit fisici** vs WISQ sui 246 successi: mediano **42.0%**, aggregato **33.2%** (area `my_x·my_y` vs `wisq_x·wisq_y`).

---

## Trade-off −5: routing steps persi vs qubit fisici risparmiati

Step su 230 circuiti dove entrambi completano; qubit fisici su tutti i 246 che mappiamo.

**A) Contro WISQ** (noi −5 vs WISQ nativa):

| | noi | WISQ nativa | differenza |
|---|--------|-------------|------------|
| Routing steps (aggregato) | 410.661 | 308.116 | **+33.3%** |
| Qubit fisici (aggregato) | 98.776 | 147.782 | **−33.2%** (49.006 in meno) |

Step per-circuito: WIN 28 / TIE 97 / LOSS 105, mediana +0%.

**B) Costo puro dello shrink** (noi −5 vs noi stessi a nativa, stessa config — `connectivity_summary_all`, 246 circuiti):

| | noi nativa | noi shrink | differenza |
|---|-----------|------------|------------|
| Routing steps (aggregato) | 6.681.679 | 6.974.970 | **+4.4%** |

Mediana **+0%**, **124/246 circuiti identici**.

---

## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 258 | — |
| Nostro mapping fallisce a −5 | 12 | — |
| **WISQ non finisce in 1h** | 67 | — |
| ↳ …ma anche noi sforiamo 1h → nessun vincitore | 15 | — |
| ↳ …noi finiamo entro 1h → **vittoria** | 52 | — |
| **Entrambi finiscono in 1h** | 191 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 2.00×) | 24 (86%) |
| ↳ Pareggio su steps | 97 | 83 (86%) |
| ↳ WISQ vince su steps | 66 (ratio mediana 0.59×) | 62 (94%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **163 / 258 (63.2%)** | — |

---

## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 258 | — |
| Nostro mapping fallisce a −5 | 12 | — |
| **WISQ non finisce in 30min** | 75 | — |
| ↳ …ma anche noi sforiamo 30min → nessun vincitore | 17 | — |
| ↳ …noi finiamo entro 30min → **vittoria** | 58 | — |
| **Entrambi finiscono in 30min** | 183 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 2.00×) | 24 (86%) |
| ↳ Pareggio su steps | 96 | 82 (85%) |
| ↳ WISQ vince su steps | 59 (ratio mediana 0.60×) | 55 (93%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **168 / 258 (65.1%)** | — |

---

## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 258 | — |
| Nostro mapping fallisce a −5 | 12 | — |
| **WISQ non finisce in 15min** | 89 | — |
| ↳ …ma anche noi sforiamo 15min → nessun vincitore | 20 | — |
| ↳ …noi finiamo entro 15min → **vittoria** | 69 | — |
| **Entrambi finiscono in 15min** | 169 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 2.00×) | 24 (86%) |
| ↳ Pareggio su steps | 92 | 78 (85%) |
| ↳ WISQ vince su steps | 49 (ratio mediana 0.63×) | 45 (92%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **175 / 258 (67.8%)** | — |

---

## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 258 | — |
| Nostro mapping fallisce a −5 | 12 | — |
| **WISQ non finisce in 10min** | 99 | — |
| ↳ …ma anche noi sforiamo 10min → nessun vincitore | 21 | — |
| ↳ …noi finiamo entro 10min → **vittoria** | 78 | — |
| **Entrambi finiscono in 10min** | 159 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 2.00×) | 24 (86%) |
| ↳ Pareggio su steps | 90 | 76 (84%) |
| ↳ WISQ vince su steps | 41 (ratio mediana 0.63×) | 37 (90%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **182 / 258 (70.5%)** | — |

---

## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 258 | — |
| Nostro mapping fallisce a −5 | 12 | — |
| **WISQ non finisce in 5min** | 109 | — |
| ↳ …ma anche noi sforiamo 5min → nessun vincitore | 21 | — |
| ↳ …noi finiamo entro 5min → **vittoria** | 88 | — |
| **Noi non finiamo, WISQ sì → sconfitta** | 5 | — |
| **Entrambi finiscono in 5min** | 144 | — |
| ↳ Noi vinciamo su steps | 27 (ratio mediana 2.00×) | 24 (89%) |
| ↳ Pareggio su steps | 86 | 75 (87%) |
| ↳ WISQ vince su steps | 31 (ratio mediana 0.65×) | 28 (90%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **190 / 258 (73.6%)** | — |

---

## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 258 | — |
| Nostro mapping fallisce a −5 | 12 | — |
| **WISQ non finisce in 1min** | 138 | — |
| ↳ …ma anche noi sforiamo 1min → nessun vincitore | 42 | — |
| ↳ …noi finiamo entro 1min → **vittoria** | 96 | — |
| **Noi non finiamo, WISQ sì → sconfitta** | 15 | — |
| **Entrambi finiscono in 1min** | 105 | — |
| ↳ Noi vinciamo su steps | 22 (ratio mediana 1.88×) | 22 (100%) |
| ↳ Pareggio su steps | 67 | 62 (93%) |
| ↳ WISQ vince su steps | 16 (ratio mediana 0.77×) | 15 (94%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **180 / 258 (69.8%)** | — |

---

## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (asimm.) | 230 | 16 | 0 | 0 | **127 (49.2%)** |
| 1 ora | 191 | 52 | 0 | 15 | **163 (63.2%)** |
| 30 minuti | 183 | 58 | 0 | 17 | **168 (65.1%)** |
| 15 minuti | 169 | 69 | 0 | 20 | **175 (67.8%)** |
| 10 minuti | 159 | 78 | 0 | 21 | **182 (70.5%)** |
| 5 minuti | 144 | 88 | 5 | 21 | **190 (73.6%)** ⟵ picco |
| 1 minuto | 105 | 96 | 15 | 42 | **180 (69.8%)** |

---

## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s` sui 246 circuiti che mappiamo a −5.

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 246 | 222 (90%) | 394× | 590× | 0.01× | 19455× |
| ↳ Dove vinciamo su steps | 28 | 24 (86%) | 148× | 228× | 0.02× | 1183× |
| ↳ In pareggio su steps | 97 | 83 (86%) | 433× | 531× | 0.01× | 2561× |
| ↳ Dove WISQ vince su steps | 105 | 101 (96%) | 470× | 805× | 0.02× | 19455× |
| ↳ WISQ in timeout | 16 | 14 (88%) | 13× | 171× | 0.54× | 1790× |

---

## Per famiglia di circuiti

**WISQ timeout** = `mr_timeout=12000s`. **MapFail** = il nostro mapping non riesce alla griglia shrinkata.

| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | MapFail −5 | Note |
|--------|---|-----|----------------|------|--------------|-----------|------|
| 19qubits | 2 | 0 | 0 | 2 | 0 | 0 | n=19 |
| 53qubits | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=27–39 |
| adder | 5 | 0 | 3 (2 noi+veloci) | 0 | 0 | 2 | n=28–433 |
| bv | 1 | 0 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=153 |
| bwt | 5 | 0 | 0 | 2 | 3 | 0 | n=21–133 |
| cat | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| dnn | 1 | 0 | 0 | 1 | 0 | 0 | n=16 |
| factor247 | 1 | 0 | 0 | 0 | 0 | 1 |  |
| fredkin | 1 | 0 | 0 | 0 | 0 | 1 |  |
| ghz | 18 | 0 | 18 (18 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| ghz_state | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=23–255 |
| graphstate | 17 | 10 | 7 (5 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| grover | 3 | 0 | 0 | 0 | 1 | 2 | n=20 |
| hhl | 1 | 0 | 0 | 0 | 0 | 1 |  |
| ising | 19 | 17 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=5–420 |
| multiplier | 11 | 0 | 3 (0 noi+veloci) | 4 | 4 | 0 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 0 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 0 | 2 (2 noi+veloci) | 17 | 1 | 0 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5 |
| qft | 22 | 0 | 0 | 21 | 1 | 0 | n=5–400 |
| qpe_n9 | 1 | 0 | 0 | 0 | 0 | 1 |  |
| qram | 1 | 0 | 0 | 0 | 0 | 1 |  |
| randomcircuit | 4 | 0 | 0 | 2 | 2 | 0 | n=50–400 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| square_root | 2 | 0 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=14–32 |
| synth | 37 | 0 | 0 | 35 | 2 | 0 | n=50–200 |
| t_test | 1 | 0 | 0 | 1 | 0 | 0 | n=8 |
| toffoli | 1 | 0 | 0 | 0 | 0 | 1 |  |
| vqe_real_amp | 17 | 0 | 16 (15 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_su2 | 17 | 0 | 16 (14 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_two_local | 17 | 0 | 0 | 15 | 2 | 0 | n=5–400 |
| vqe_uccsd | 2 | 0 | 0 | 0 | 0 | 2 |  |
| wstate | 18 | 0 | 17 (14 noi+veloci) | 1 | 0 | 0 | n=5–400 |

---

## Per circuito (dettaglio)

**Δlati** = quanti lati sotto WISQ (`dim_diff_side`). **Steps**: WIN/=/LOSS. **MapFail** = mapping non riuscito.

| # | Circuit | Qubits | Grid (nostra) | Δlati | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|---------------|-------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 8×8 | +5 | 104 | 99 | 0.9519 | success | LOSS | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 8×8 | +5 | 288 | 286 | 0.9931 | success | LOSS | noi +veloci |
| 3 | 53qubits_155gate_57layers | 27 | 10×10 | +5 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 4 | 53qubits_332gate_152layers | 39 | 12×12 | +5 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 10×10 | +5 | 24 | 24 | 1.0000 | success | = | WISQ +veloce |
| 6 | adder_n4 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 7 | adder_n433 | 433 | 40×40 | +5 | 249 | 249 | 1.0000 | success | = | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 14×14 | +5 | 181 | 181 | 1.0000 | success | = | noi +veloci |
| 9 | bigadder_n18_transpiled | — | — | — | — | — | — | error | **MapFail −5** | — |
| 10 | bv_n280 | 153 | 32×32 | −3 | 152 | 152 | 1.0000 | success | = | WISQ +veloce |
| 11 | bwt_n177 | 133 | 22×22 | +5 | 258604 | — | — | failed | timeout | — |
| 12 | bwt_n21 | 21 | 8×8 | +5 | 116400 | — | — | failed | timeout | — |
| 13 | bwt_n37 | 28 | 10×10 | +5 | 33639 | 33600 | 0.9988 | success | LOSS | noi +veloci |
| 14 | bwt_n57 | 43 | 12×12 | +5 | 65619 | 65600 | 0.9997 | success | LOSS | noi +veloci |
| 15 | bwt_n97 | 73 | 16×16 | +5 | 129710 | — | — | failed | timeout | — |
| 16 | cat_n130 | 130 | 22×22 | +5 | 129 | 129 | 1.0000 | success | = | noi +veloci |
| 17 | cat_n260 | 260 | 32×32 | +5 | 259 | 259 | 1.0000 | success | = | noi +veloci |
| 18 | continuous_3_17_13 | 3 | 2×2 | +5 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 19 | dnn_n16 | 16 | 6×6 | +5 | 71 | 53 | 0.7465 | success | LOSS | noi +veloci |
| 20 | factor247_n15 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 21 | fredkin_n3 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 22 | ghz_n10 | 10 | 6×6 | +5 | 9 | 9 | 1.0000 | success | = | noi +veloci |
| 23 | ghz_n100 | 100 | 18×18 | +5 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 24 | ghz_n125 | 125 | 22×22 | +5 | 124 | 124 | 1.0000 | success | = | noi +veloci |
| 25 | ghz_n150 | 150 | 24×24 | +5 | 149 | 149 | 1.0000 | success | = | noi +veloci |
| 26 | ghz_n175 | 175 | 26×26 | +5 | 174 | 174 | 1.0000 | success | = | noi +veloci |
| 27 | ghz_n20 | 20 | 8×8 | +5 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n200 | 200 | 28×28 | +5 | 199 | 199 | 1.0000 | success | = | noi +veloci |
| 29 | ghz_n255 | 255 | 30×30 | +5 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 30 | ghz_n30 | 30 | 10×10 | +5 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 31 | ghz_n300 | 300 | 34×34 | +5 | 299 | 299 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n40 | 40 | 12×12 | +5 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 33 | ghz_n400 | 400 | 38×38 | +5 | 399 | 399 | 1.0000 | success | = | noi +veloci |
| 34 | ghz_n5 | 5 | 4×4 | +5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 35 | ghz_n50 | 50 | 14×14 | +5 | 49 | 49 | 1.0000 | success | = | noi +veloci |
| 36 | ghz_n60 | 60 | 14×14 | +5 | 59 | 59 | 1.0000 | success | = | noi +veloci |
| 37 | ghz_n70 | 70 | 16×16 | +5 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 38 | ghz_n80 | 80 | 16×16 | +5 | 79 | 79 | 1.0000 | success | = | noi +veloci |
| 39 | ghz_n90 | 90 | 18×18 | +5 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 40 | ghz_state_n23 | 23 | 8×8 | +5 | 22 | 22 | 1.0000 | success | = | noi +veloci |
| 41 | ghz_state_n255 | 255 | 30×30 | +5 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 42 | graphstate_n10 | 10 | 6×6 | +5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 43 | graphstate_n100 | 100 | 18×18 | +5 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 44 | graphstate_n125 | 125 | 22×22 | +5 | 5 | 8 | 1.6000 | success | **WIN** | noi +veloci |
| 45 | graphstate_n150 | 150 | 24×24 | +5 | 6 | 10 | 1.6667 | success | **WIN** | noi +veloci |
| 46 | graphstate_n175 | 175 | 26×26 | +5 | 7 | 10 | 1.4286 | success | **WIN** | noi +veloci |
| 47 | graphstate_n20 | 20 | 8×8 | +5 | 4 | 4 | 1.0000 | success | = | WISQ +veloce |
| 48 | graphstate_n200 | 200 | 28×28 | +5 | 6 | 12 | 2.0000 | success | **WIN** | noi +veloci |
| 49 | graphstate_n30 | 30 | 10×10 | +5 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 50 | graphstate_n300 | 300 | 34×34 | +5 | 9 | 14 | 1.5556 | success | **WIN** | noi +veloci |
| 51 | graphstate_n40 | 40 | 12×12 | +5 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 52 | graphstate_n400 | 400 | 38×38 | +5 | 7 | 22 | 3.1429 | success | **WIN** | noi +veloci |
| 53 | graphstate_n5 | 5 | 4×4 | +5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 54 | graphstate_n50 | 50 | 14×14 | +5 | 5 | 5 | 1.0000 | success | = | WISQ +veloce |
| 55 | graphstate_n60 | 60 | 14×14 | +5 | 5 | 5 | 1.0000 | success | = | noi +veloci |
| 56 | graphstate_n70 | 70 | 16×16 | +5 | 6 | 7 | 1.1667 | success | **WIN** | noi +veloci |
| 57 | graphstate_n80 | 80 | 16×16 | +5 | 6 | 7 | 1.1667 | success | **WIN** | noi +veloci |
| 58 | graphstate_n90 | 90 | 18×18 | +5 | 5 | 6 | 1.2000 | success | **WIN** | noi +veloci |
| 59 | grover_n10 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 60 | grover_n20 | 20 | 8×8 | +5 | 2219760 | — | — | failed | timeout | — |
| 61 | grover_n5 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 62 | hhl_n10 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 63 | ising_n10 | 10 | 6×6 | +5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 64 | ising_n100 | 100 | 18×18 | +5 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 65 | ising_n125 | 125 | 22×22 | +5 | 4 | 15 | 3.7500 | success | **WIN** | noi +veloci |
| 66 | ising_n150 | 150 | 24×24 | +5 | 4 | 20 | 5.0000 | success | **WIN** | noi +veloci |
| 67 | ising_n175 | 175 | 26×26 | +5 | 4 | 19 | 4.7500 | success | **WIN** | noi +veloci |
| 68 | ising_n20 | 20 | 8×8 | +5 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 69 | ising_n200 | 200 | 28×28 | +5 | 4 | 23 | 5.7500 | success | **WIN** | noi +veloci |
| 70 | ising_n26 | 26 | 10×10 | +5 | 4 | 5 | 1.2500 | success | **WIN** | WISQ +veloce |
| 71 | ising_n30 | 30 | 10×10 | +5 | 4 | 6 | 1.5000 | success | **WIN** | WISQ +veloce |
| 72 | ising_n300 | 300 | 34×34 | +5 | 4 | 32 | 8.0000 | success | **WIN** | noi +veloci |
| 73 | ising_n40 | 40 | 12×12 | +5 | 4 | 7 | 1.7500 | success | **WIN** | noi +veloci |
| 74 | ising_n400 | 400 | 38×38 | +5 | 4 | 40 | 10.0000 | success | **WIN** | WISQ +veloce |
| 75 | ising_n420 | 420 | 40×40 | +5 | 4 | 43 | 10.7500 | success | **WIN** | noi +veloci |
| 76 | ising_n5 | 5 | 4×4 | +5 | 6 | 4 | 0.6667 | success | LOSS | noi +veloci |
| 77 | ising_n50 | 50 | 14×14 | +5 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 78 | ising_n60 | 60 | 14×14 | +5 | 4 | 9 | 2.2500 | success | **WIN** | WISQ +veloce |
| 79 | ising_n70 | 70 | 16×16 | +5 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 80 | ising_n80 | 80 | 16×16 | +5 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 81 | ising_n90 | 90 | 18×18 | +5 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 82 | multiplier_n100 | 100 | 18×18 | +5 | 112834 | — | — | failed | timeout | — |
| 83 | multiplier_n15 | 9 | 4×4 | +5 | 12 | 12 | 1.0000 | success | = | WISQ +veloce |
| 84 | multiplier_n20 | 20 | 8×8 | +5 | 4034 | 3990 | 0.9891 | success | LOSS | noi +veloci |
| 85 | multiplier_n200 | 200 | 28×28 | +5 | 452514 | — | — | failed | timeout | — |
| 86 | multiplier_n300 | 300 | 34×34 | +5 | 1021923 | — | — | failed | timeout | — |
| 87 | multiplier_n40 | 40 | 12×12 | +5 | 17411 | 17329 | 0.9953 | success | LOSS | noi +veloci |
| 88 | multiplier_n400 | 400 | 38×38 | +5 | 1818886 | — | — | failed | timeout | — |
| 89 | multiplier_n45 | 27 | 12×12 | +3 | 36 | 36 | 1.0000 | success | = | WISQ +veloce |
| 90 | multiplier_n60 | 60 | 14×14 | +5 | 40114 | 39730 | 0.9904 | success | LOSS | noi +veloci |
| 91 | multiplier_n75 | 45 | 16×16 | +1 | 60 | 60 | 1.0000 | success | = | WISQ +veloce |
| 92 | multiplier_n80 | 80 | 16×16 | +5 | 72016 | 71289 | 0.9899 | success | LOSS | noi +veloci |
| 93 | multiply_n13 | 6 | 4×4 | +5 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 94 | parallel | 8 | 4×4 | +5 | 10 | 10 | 1.0000 | success | = | WISQ +veloce |
| 95 | parallel_big | 20 | 8×8 | +5 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 96 | qaoa_n10 | 10 | 6×6 | +5 | 50 | 46 | 0.9200 | success | LOSS | noi +veloci |
| 97 | qaoa_n100 | 100 | 18×18 | +5 | 1958 | 888 | 0.4535 | success | LOSS | noi +veloci |
| 98 | qaoa_n125 | 125 | 22×22 | +5 | 1912 | 1270 | 0.6642 | success | LOSS | noi +veloci |
| 99 | qaoa_n150 | 150 | 24×24 | +5 | 2685 | 1725 | 0.6425 | success | LOSS | noi +veloci |
| 100 | qaoa_n175 | 175 | 26×26 | +5 | 3363 | 2268 | 0.6744 | success | LOSS | noi +veloci |
| 101 | qaoa_n20 | 20 | 8×8 | +5 | 138 | 90 | 0.6522 | success | LOSS | noi +veloci |
| 102 | qaoa_n200 | 200 | 28×28 | +5 | 3995 | 2869 | 0.7181 | success | LOSS | noi +veloci |
| 103 | qaoa_n30 | 30 | 10×10 | +5 | 265 | 139 | 0.5245 | success | LOSS | WISQ +veloce |
| 104 | qaoa_n300 | 300 | 34×34 | +5 | 8650 | 5854 | 0.6768 | success | LOSS | noi +veloci |
| 105 | qaoa_n40 | 40 | 12×12 | +5 | 319 | 202 | 0.6332 | success | LOSS | noi +veloci |
| 106 | qaoa_n400 | 400 | 38×38 | +5 | 14936 | — | — | failed | timeout | — |
| 107 | qaoa_n5 | 5 | 4×4 | +5 | 16 | 14 | 0.8750 | success | LOSS | noi +veloci |
| 108 | qaoa_n50 | 50 | 14×14 | +5 | 415 | 282 | 0.6795 | success | LOSS | noi +veloci |
| 109 | qaoa_n6 | 6 | 4×4 | +5 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 110 | qaoa_n60 | 60 | 14×14 | +5 | 1091 | 381 | 0.3492 | success | LOSS | noi +veloci |
| 111 | qaoa_n64 | 64 | 14×14 | +5 | 1252 | 426 | 0.3403 | success | LOSS | noi +veloci |
| 112 | qaoa_n6_transpiled | 6 | 4×4 | +5 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 113 | qaoa_n70 | 70 | 16×16 | +5 | 845 | 475 | 0.5621 | success | LOSS | noi +veloci |
| 114 | qaoa_n80 | 80 | 16×16 | +5 | 1590 | 587 | 0.3692 | success | LOSS | noi +veloci |
| 115 | qaoa_n90 | 90 | 18×18 | +5 | 1207 | 725 | 0.6007 | success | LOSS | noi +veloci |
| 116 | qec_en_n5 | 5 | 4×4 | +5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 117 | qft_20 | 20 | 8×8 | +5 | 149 | 82 | 0.5503 | success | LOSS | noi +veloci |
| 118 | qft_n10 | 10 | 6×6 | +5 | 47 | 34 | 0.7234 | success | LOSS | WISQ +veloce |
| 119 | qft_n100 | 100 | 18×18 | +5 | 774 | 438 | 0.5659 | success | LOSS | noi +veloci |
| 120 | qft_n125 | 125 | 22×22 | +5 | 2518 | 531 | 0.2109 | success | LOSS | noi +veloci |
| 121 | qft_n128 | 128 | 22×22 | +5 | 2592 | 543 | 0.2095 | success | LOSS | noi +veloci |
| 122 | qft_n150 | 150 | 24×24 | +5 | 3223 | 632 | 0.1961 | success | LOSS | noi +veloci |
| 123 | qft_n175 | 175 | 26×26 | +5 | 3691 | 733 | 0.1986 | success | LOSS | noi +veloci |
| 124 | qft_n18 | 18 | 8×8 | +5 | 102 | 71 | 0.6961 | success | LOSS | noi +veloci |
| 125 | qft_n20 | 20 | 8×8 | +5 | 143 | 83 | 0.5804 | success | LOSS | noi +veloci |
| 126 | qft_n200 | 200 | 28×28 | +5 | 4275 | 832 | 0.1946 | success | LOSS | noi +veloci |
| 127 | qft_n30 | 30 | 10×10 | +5 | 267 | 134 | 0.5019 | success | LOSS | noi +veloci |
| 128 | qft_n300 | 300 | 34×34 | +5 | 6467 | 1228 | 0.1899 | success | LOSS | noi +veloci |
| 129 | qft_n320 | 320 | 34×34 | +5 | 10335 | — | — | failed | timeout | — |
| 130 | qft_n40 | 40 | 12×12 | +5 | 316 | 179 | 0.5665 | success | LOSS | noi +veloci |
| 131 | qft_n400 | 400 | 38×38 | +5 | 8862 | 1667 | 0.1881 | success | LOSS | noi +veloci |
| 132 | qft_n5 | 5 | 4×4 | +5 | 16 | 14 | 0.8750 | success | LOSS | noi +veloci |
| 133 | qft_n50 | 50 | 14×14 | +5 | 349 | 220 | 0.6304 | success | LOSS | noi +veloci |
| 134 | qft_n60 | 60 | 14×14 | +5 | 682 | 270 | 0.3959 | success | LOSS | noi +veloci |
| 135 | qft_n64 | 64 | 14×14 | +5 | 915 | 290 | 0.3169 | success | LOSS | noi +veloci |
| 136 | qft_n70 | 70 | 16×16 | +5 | 504 | 309 | 0.6131 | success | LOSS | noi +veloci |
| 137 | qft_n80 | 80 | 16×16 | +5 | 933 | 360 | 0.3859 | success | LOSS | noi +veloci |
| 138 | qft_n90 | 90 | 18×18 | +5 | 590 | 392 | 0.6644 | success | LOSS | noi +veloci |
| 139 | qpe_n9_transpiled | — | — | — | — | — | — | error | **MapFail −5** | — |
| 140 | qram_n20 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 141 | randomcircuit_n100 | 100 | 18×18 | +5 | 17534 | 4437 | 0.2531 | success | LOSS | noi +veloci |
| 142 | randomcircuit_n200 | 200 | 28×28 | +5 | 55519 | — | — | failed | timeout | — |
| 143 | randomcircuit_n400 | 400 | 38×38 | +5 | 310744 | — | — | failed | timeout | — |
| 144 | randomcircuit_n50 | 50 | 14×14 | +5 | 3565 | 1436 | 0.4028 | success | LOSS | noi +veloci |
| 145 | seca_n11 | 11 | 6×6 | +5 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 146 | simon_n6 | 3 | 2×2 | +5 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 147 | square_root_n18 | 14 | 6×6 | +5 | 28 | 27 | 0.9643 | success | LOSS | WISQ +veloce |
| 148 | square_root_n45 | 32 | 10×10 | +5 | 570 | 570 | 1.0000 | success | = | noi +veloci |
| 149 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 18×18 | +5 | 762 | 154 | 0.2021 | success | LOSS | noi +veloci |
| 150 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 18×18 | +5 | 946 | 148 | 0.1564 | success | LOSS | noi +veloci |
| 151 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 18×18 | +5 | 801 | 192 | 0.2397 | success | LOSS | noi +veloci |
| 152 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 18×18 | +5 | 890 | 192 | 0.2157 | success | LOSS | noi +veloci |
| 153 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 18×18 | +5 | 563 | 204 | 0.3623 | success | LOSS | noi +veloci |
| 154 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 18×18 | +5 | 927 | 207 | 0.2233 | success | LOSS | noi +veloci |
| 155 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 18×18 | +5 | 1486 | 376 | 0.2530 | success | LOSS | noi +veloci |
| 156 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 18×18 | +5 | 1433 | 386 | 0.2694 | success | LOSS | noi +veloci |
| 157 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 18×18 | +5 | 1039 | 395 | 0.3802 | success | LOSS | noi +veloci |
| 158 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 18×18 | +5 | 1057 | 392 | 0.3709 | success | LOSS | noi +veloci |
| 159 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 18×18 | +5 | 1799 | 426 | 0.2368 | success | LOSS | noi +veloci |
| 160 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 18×18 | +5 | 1087 | 432 | 0.3974 | success | LOSS | noi +veloci |
| 161 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 28×28 | +5 | 2911 | 436 | 0.1498 | success | LOSS | noi +veloci |
| 162 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 28×28 | +5 | 2967 | 412 | 0.1389 | success | LOSS | noi +veloci |
| 163 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 28×28 | +5 | 2939 | 619 | 0.2106 | success | LOSS | noi +veloci |
| 164 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 28×28 | +5 | 3032 | 613 | 0.2022 | success | LOSS | noi +veloci |
| 165 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 28×28 | +5 | 2956 | 648 | 0.2192 | success | LOSS | noi +veloci |
| 166 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 28×28 | +5 | 3002 | 655 | 0.2182 | success | LOSS | noi +veloci |
| 167 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 28×28 | +5 | 2179 | — | — | failed | timeout | — |
| 168 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 28×28 | +5 | 5877 | — | — | failed | timeout | — |
| 169 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 28×28 | +5 | 2177 | 1243 | 0.5710 | success | LOSS | noi +veloci |
| 170 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 28×28 | +5 | 5834 | 1258 | 0.2156 | success | LOSS | noi +veloci |
| 171 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 28×28 | +5 | 6079 | 1425 | 0.2344 | success | LOSS | noi +veloci |
| 172 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 28×28 | +5 | 2766 | 1418 | 0.5127 | success | LOSS | noi +veloci |
| 173 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 14×14 | +5 | 147 | 60 | 0.4082 | success | LOSS | noi +veloci |
| 174 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 14×14 | +5 | 147 | 59 | 0.4014 | success | LOSS | noi +veloci |
| 175 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 14×14 | +5 | 144 | 68 | 0.4722 | success | LOSS | noi +veloci |
| 176 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 14×14 | +5 | 120 | 73 | 0.6083 | success | LOSS | noi +veloci |
| 177 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 14×14 | +5 | 164 | 71 | 0.4329 | success | LOSS | noi +veloci |
| 178 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 14×14 | +5 | 132 | 71 | 0.5379 | success | LOSS | noi +veloci |
| 179 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 14×14 | +5 | 184 | 109 | 0.5924 | success | LOSS | noi +veloci |
| 180 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 14×14 | +5 | 265 | 133 | 0.5019 | success | LOSS | noi +veloci |
| 181 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 14×14 | +5 | 227 | 136 | 0.5991 | success | LOSS | noi +veloci |
| 182 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 14×14 | +5 | 329 | 146 | 0.4438 | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 14×14 | +5 | 235 | 153 | 0.6511 | success | LOSS | noi +veloci |
| 184 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 14×14 | +5 | 233 | 142 | 0.6094 | success | LOSS | noi +veloci |
| 185 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 14×14 | +5 | 230 | 149 | 0.6478 | success | LOSS | noi +veloci |
| 186 | t_test | 8 | 4×4 | +5 | 111 | 110 | 0.9910 | success | LOSS | noi +veloci |
| 187 | toffoli_n3 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 188 | vqe_real_amp_n10 | 10 | 6×6 | +5 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 189 | vqe_real_amp_n100 | 100 | 18×18 | +5 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 190 | vqe_real_amp_n125 | 125 | 22×22 | +5 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 191 | vqe_real_amp_n150 | 150 | 24×24 | +5 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 192 | vqe_real_amp_n175 | 175 | 26×26 | +5 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 193 | vqe_real_amp_n20 | 20 | 8×8 | +5 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 194 | vqe_real_amp_n200 | 200 | 28×28 | +5 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 195 | vqe_real_amp_n30 | 30 | 10×10 | +5 | 33 | 33 | 1.0000 | success | = | WISQ +veloce |
| 196 | vqe_real_amp_n300 | 300 | 34×34 | +5 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 197 | vqe_real_amp_n40 | 40 | 12×12 | +5 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 198 | vqe_real_amp_n400 | 400 | 38×38 | +5 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 199 | vqe_real_amp_n5 | 5 | 4×4 | +5 | 10 | 8 | 0.8000 | success | LOSS | noi +veloci |
| 200 | vqe_real_amp_n50 | 50 | 14×14 | +5 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 201 | vqe_real_amp_n60 | 60 | 14×14 | +5 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 202 | vqe_real_amp_n70 | 70 | 16×16 | +5 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 203 | vqe_real_amp_n80 | 80 | 16×16 | +5 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 204 | vqe_real_amp_n90 | 90 | 18×18 | +5 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 205 | vqe_su2_n10 | 10 | 6×6 | +5 | 13 | 13 | 1.0000 | success | = | WISQ +veloce |
| 206 | vqe_su2_n100 | 100 | 18×18 | +5 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 207 | vqe_su2_n125 | 125 | 22×22 | +5 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 208 | vqe_su2_n150 | 150 | 24×24 | +5 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 209 | vqe_su2_n175 | 175 | 26×26 | +5 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 210 | vqe_su2_n20 | 20 | 8×8 | +5 | 23 | 23 | 1.0000 | success | = | WISQ +veloce |
| 211 | vqe_su2_n200 | 200 | 28×28 | +5 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 212 | vqe_su2_n30 | 30 | 10×10 | +5 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 213 | vqe_su2_n300 | 300 | 34×34 | +5 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 214 | vqe_su2_n40 | 40 | 12×12 | +5 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 215 | vqe_su2_n400 | 400 | 38×38 | +5 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 216 | vqe_su2_n5 | 5 | 4×4 | +5 | 10 | 8 | 0.8000 | success | LOSS | noi +veloci |
| 217 | vqe_su2_n50 | 50 | 14×14 | +5 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 218 | vqe_su2_n60 | 60 | 14×14 | +5 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 219 | vqe_su2_n70 | 70 | 16×16 | +5 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 220 | vqe_su2_n80 | 80 | 16×16 | +5 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 221 | vqe_su2_n90 | 90 | 18×18 | +5 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 222 | vqe_two_local_n10 | 10 | 6×6 | +5 | 57 | 39 | 0.6842 | success | LOSS | noi +veloci |
| 223 | vqe_two_local_n100 | 100 | 18×18 | +5 | 2858 | 1397 | 0.4888 | success | LOSS | noi +veloci |
| 224 | vqe_two_local_n125 | 125 | 22×22 | +5 | 2630 | 1978 | 0.7521 | success | LOSS | noi +veloci |
| 225 | vqe_two_local_n150 | 150 | 24×24 | +5 | 3947 | 2738 | 0.6937 | success | LOSS | noi +veloci |
| 226 | vqe_two_local_n175 | 175 | 26×26 | +5 | 5003 | 3586 | 0.7168 | success | LOSS | noi +veloci |
| 227 | vqe_two_local_n20 | 20 | 8×8 | +5 | 197 | 98 | 0.4975 | success | LOSS | noi +veloci |
| 228 | vqe_two_local_n200 | 200 | 28×28 | +5 | 5990 | 4538 | 0.7576 | success | LOSS | noi +veloci |
| 229 | vqe_two_local_n30 | 30 | 10×10 | +5 | 373 | 184 | 0.4933 | success | LOSS | noi +veloci |
| 230 | vqe_two_local_n300 | 300 | 34×34 | +5 | 12190 | — | — | failed | timeout | — |
| 231 | vqe_two_local_n40 | 40 | 12×12 | +5 | 417 | 290 | 0.6954 | success | LOSS | noi +veloci |
| 232 | vqe_two_local_n400 | 400 | 38×38 | +5 | 21898 | — | — | failed | timeout | — |
| 233 | vqe_two_local_n5 | 5 | 4×4 | +5 | 20 | 17 | 0.8500 | success | LOSS | noi +veloci |
| 234 | vqe_two_local_n50 | 50 | 14×14 | +5 | 618 | 413 | 0.6683 | success | LOSS | noi +veloci |
| 235 | vqe_two_local_n60 | 60 | 14×14 | +5 | 1514 | 580 | 0.3831 | success | LOSS | noi +veloci |
| 236 | vqe_two_local_n70 | 70 | 16×16 | +5 | 1080 | 728 | 0.6741 | success | LOSS | noi +veloci |
| 237 | vqe_two_local_n80 | 80 | 16×16 | +5 | 2298 | 948 | 0.4125 | success | LOSS | noi +veloci |
| 238 | vqe_two_local_n90 | 90 | 18×18 | +5 | 1618 | 1136 | 0.7021 | success | LOSS | noi +veloci |
| 239 | vqe_uccsd_n4 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 240 | vqe_uccsd_n8 | — | — | — | — | — | — | error | **MapFail −5** | — |
| 241 | wstate_n10 | 10 | 6×6 | +5 | 11 | 11 | 1.0000 | success | = | WISQ +veloce |
| 242 | wstate_n100 | 100 | 18×18 | +5 | 101 | 101 | 1.0000 | success | = | noi +veloci |
| 243 | wstate_n125 | 125 | 22×22 | +5 | 126 | 126 | 1.0000 | success | = | noi +veloci |
| 244 | wstate_n150 | 150 | 24×24 | +5 | 151 | 151 | 1.0000 | success | = | noi +veloci |
| 245 | wstate_n175 | 175 | 26×26 | +5 | 176 | 176 | 1.0000 | success | = | noi +veloci |
| 246 | wstate_n20 | 20 | 8×8 | +5 | 21 | 21 | 1.0000 | success | = | WISQ +veloce |
| 247 | wstate_n200 | 200 | 28×28 | +5 | 201 | 201 | 1.0000 | success | = | noi +veloci |
| 248 | wstate_n27 | 27 | 10×10 | +5 | 28 | 28 | 1.0000 | success | = | noi +veloci |
| 249 | wstate_n30 | 30 | 10×10 | +5 | 31 | 31 | 1.0000 | success | = | noi +veloci |
| 250 | wstate_n300 | 300 | 34×34 | +5 | 301 | 301 | 1.0000 | success | = | noi +veloci |
| 251 | wstate_n40 | 40 | 12×12 | +5 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 252 | wstate_n400 | 400 | 38×38 | +5 | 401 | 401 | 1.0000 | success | = | noi +veloci |
| 253 | wstate_n5 | 5 | 4×4 | +5 | 7 | 6 | 0.8571 | success | LOSS | WISQ +veloce |
| 254 | wstate_n50 | 50 | 14×14 | +5 | 51 | 51 | 1.0000 | success | = | noi +veloci |
| 255 | wstate_n60 | 60 | 14×14 | +5 | 61 | 61 | 1.0000 | success | = | noi +veloci |
| 256 | wstate_n70 | 70 | 16×16 | +5 | 71 | 71 | 1.0000 | success | = | noi +veloci |
| 257 | wstate_n80 | 80 | 16×16 | +5 | 81 | 81 | 1.0000 | success | = | noi +veloci |
| 258 | wstate_n90 | 90 | 18×18 | +5 | 91 | 91 | 1.0000 | success | = | WISQ +veloce |
