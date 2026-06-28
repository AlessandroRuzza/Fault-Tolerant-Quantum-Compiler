# Risultati WISQ-native MENO 3 — connectivity

**connectivity con i pesi finali** (gaussian/fine, safe_passage=connectivity, border=15, sigma=0.7, mapped=20, cnot_high=8, magic=0, ext=−15, bfs=0.70, center_circle, packing, smart_t_routing, patience=3).
Griglia fissa a `wisq_native_side −3` per lato; WISQ resta sulla sua griglia nativa come riferimento.
Dati: `conn_wisq_minus3_wisqconn.csv` — CSV corrente con **263 righe**. Esclusi da questa analisi: `knn_n25`, `test` → **261 circuiti**.

---

## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 261 | — |
| **Nostro mapping FALLISCE a −3** | 5 | — |
| **Mappiamo a −3 con successo** | 256 | — |
| ↳ WISQ va in timeout sulla sua nativa (noi vinciamo) | 20 | — |
| ↳ Entrambi completano | 236 | — |
|   ↳ Noi vinciamo su steps | 28 (ratio mediana 1.92×) | 25 (89%) |
|   ↳ Pareggio su steps | 117 | 112 (96%) |
|   ↳ WISQ vince su steps | 91 (ratio mediana 0.75×) | 91 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **160 / 261 (61.3%)** | — |
| ↳ Mappiamo a −3, WISQ va in timeout | 20 / 261 (7.7%) | — |
| ↳ Vinciamo su steps (WISQ completa) | 28 / 261 (10.7%) | — |
| ↳ Pareggio su steps, noi più veloci | 112 / 261 (42.9%) | — |
| | | |
| **SCONFITTE NOSTRE (mapping fallito a −3)** | **5 / 261 (1.9%)** | — |

Circuiti dove non mappiamo a −3: `adder_n4`, `bigadder_n18_transpiled`, `grover_n5`, `hhl_n10`, `qram_n20`.

---

## Footprint: quanto scendiamo sotto WISQ

| Δ lati sotto WISQ (`dim_diff_side`) | Circuiti |
|---|---|
| +3 | 252 (target) |
| −5 | 1 (`bv_n280`) |
| −1 | 1 (`multiplier_n75`) |
| +1 | 1 (`multiplier_n45`) |
| +5 | 1 (`grover_n10`) |

**Risparmio di qubit fisici** vs WISQ sui 256 successi: mediano **26.5%**, aggregato **20.7%** (area `my_x·my_y` vs `wisq_x·wisq_y`).

---

## Trade-off −3: routing steps persi vs qubit fisici risparmiati

Step su 236 circuiti dove entrambi completano; qubit fisici su tutti i 256 che mappiamo.

**A) Contro WISQ** (noi −3 vs WISQ nativa):

| | noi | WISQ nativa | differenza |
|---|--------|-------------|------------|
| Routing steps (aggregato) | 278.922 | 225.953 | **+23.4%** |
| Qubit fisici (aggregato) | 119.588 | 150.864 | **−20.7%** (31.276 in meno) |

Step per-circuito: WIN 28 / TIE 117 / LOSS 91, mediana +0%.

**B) Costo puro dello shrink** (noi −3 vs noi stessi a nativa, stessa config — `connectivity_summary_all`, 253 circuiti):

| | noi nativa | noi shrink | differenza |
|---|-----------|------------|------------|
| Routing steps (aggregato) | 7.047.927 | 7.109.037 | **+0.9%** |

Mediana **+0%**, **145/253 circuiti identici**.

---

## Cliff QFT — il vero collo di bottiglia (indipendente dalla dimensione)

Confronto nostri step / WISQ per dimensione, a −3, a −5 e a griglia piena (nativa).

| qft | griglia −3 | noi −3 | WISQ | **−3/W** | −5/W | nativa/W |
|---|---|---|---|---|---|---|
| qft_n5 | 6 | 14 | 14 | **1.0×** | 1.1× | 1.0× |
| qft_n10 | 8 | 34 | 34 | **1.0×** | 1.4× | 1.1× |
| qft_n18 | 10 | 75 | 71 | **1.1×** | 1.4× | 1.0× |
| qft_20 | 10 | 90 | 84 | **1.1×** | 1.8× | 1.0× |
| qft_n20 | 10 | 90 | 82 | **1.1×** | 1.7× | 1.0× |
| qft_n30 | 12 | 154 | 134 | **1.1×** | 2.0× | 1.1× |
| qft_n40 | 14 | 214 | 181 | **1.2×** | 1.8× | 1.1× |
| qft_n50 | 16 | 263 | 221 | **1.2×** | 1.6× | 1.2× |
| qft_n60 | 16 | 371 | 270 | **1.4×** | 2.5× | 1.2× |
| qft_n64 | 16 | 426 | 292 | **1.5×** | 3.2× | 1.2× |
| qft_n70 | 18 | 393 | 307 | **1.3×** | 1.6× | 1.2× |
| qft_n80 | 18 | 488 | 357 | **1.4×** | 2.6× | 1.3× |
| qft_n90 | 20 | 521 | 396 | **1.3×** | 1.5× | 1.2× |
| qft_n100 | 20 | 675 | 440 | **1.5×** | 1.8× | 1.2× |
| qft_n125 | 24 | 2608 | 532 | **4.9×** | 4.7× | 5.0× |
| qft_n128 | 24 | 2679 | 539 | **5.0×** | 4.8× | 5.0× |
| qft_n150 | 26 | 3083 | 631 | **4.9×** | 5.1× | 4.9× |
| qft_n175 | 28 | 3808 | 728 | **5.2×** | 5.0× | 5.2× |
| qft_n200 | 30 | 4270 | 826 | **5.2×** | 5.1× | 5.2× |
| qft_n300 | 36 | 6978 | 1247 | **5.6×** | 5.3× | 5.4× |
| qft_n320 | 36 | 9134 | — | **(WISQ timeout)** | — | — |
| qft_n400 | 40 | 9331 | 1672 | **5.6×** | 5.3× | 5.3× |

---

## −3 vs −5 — cosa cambia stringendo di 2 lati in meno

| metrica | **−3** | −5 |
|---|---|---|
| Mappano | **256** | 246 |
| MapFail | **5** | 12 |
| WISQ timeout (nostre vittorie) | **20** | 16 |
| Entrambi completano | 236 | 230 |
| Steps **WIN / TIE / LOSS** | **28 / 117 / 91** | 28 / 97 / 105 |
| Aggregato steps vs WISQ | **+23.4%** | +33.3% |
| Footprint (qubit risparmiati) | **−20.7%** | −33.2% |

**Diretto, stessi 226 circuiti both-complete in entrambi:** a −3 usiamo **-15.0%** di step rispetto a −5 (gap vs WISQ: −3 **+25.5%** contro −5 **+47.5%** su quel set).

---

## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 261 | — |
| Nostro mapping fallisce a −3 | 5 | — |
| **WISQ non finisce in 1h** | 65 | — |
| ↳ …ma anche noi sforiamo 1h → nessun vincitore | 10 | — |
| ↳ …noi finiamo entro 1h → **vittoria** | 55 | — |
| **Entrambi finiscono in 1h** | 196 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 1.92×) | 25 (89%) |
| ↳ Pareggio su steps | 116 | 111 (96%) |
| ↳ WISQ vince su steps | 52 (ratio mediana 0.79×) | 52 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **194 / 261 (74.3%)** | — |

---

## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 261 | — |
| Nostro mapping fallisce a −3 | 5 | — |
| **WISQ non finisce in 30min** | 79 | — |
| ↳ …ma anche noi sforiamo 30min → nessun vincitore | 11 | — |
| ↳ …noi finiamo entro 30min → **vittoria** | 68 | — |
| **Entrambi finiscono in 30min** | 182 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 1.92×) | 25 (89%) |
| ↳ Pareggio su steps | 114 | 109 (96%) |
| ↳ WISQ vince su steps | 40 (ratio mediana 0.80×) | 40 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **205 / 261 (78.5%)** | — |

---

## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 261 | — |
| Nostro mapping fallisce a −3 | 5 | — |
| **WISQ non finisce in 15min** | 93 | — |
| ↳ …ma anche noi sforiamo 15min → nessun vincitore | 13 | — |
| ↳ …noi finiamo entro 15min → **vittoria** | 80 | — |
| **Entrambi finiscono in 15min** | 168 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 1.92×) | 25 (89%) |
| ↳ Pareggio su steps | 109 | 104 (95%) |
| ↳ WISQ vince su steps | 31 (ratio mediana 0.81×) | 31 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **212 / 261 (81.2%)** | — |

---

## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 261 | — |
| Nostro mapping fallisce a −3 | 5 | — |
| **WISQ non finisce in 10min** | 98 | — |
| ↳ …ma anche noi sforiamo 10min → nessun vincitore | 16 | — |
| ↳ …noi finiamo entro 10min → **vittoria** | 82 | — |
| **Entrambi finiscono in 10min** | 163 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 1.92×) | 25 (89%) |
| ↳ Pareggio su steps | 109 | 104 (95%) |
| ↳ WISQ vince su steps | 26 (ratio mediana 0.83×) | 26 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **214 / 261 (82.0%)** | — |

---

## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 261 | — |
| Nostro mapping fallisce a −3 | 5 | — |
| **WISQ non finisce in 5min** | 109 | — |
| ↳ …ma anche noi sforiamo 5min → nessun vincitore | 17 | — |
| ↳ …noi finiamo entro 5min → **vittoria** | 92 | — |
| **Entrambi finiscono in 5min** | 152 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 1.92×) | 25 (89%) |
| ↳ Pareggio su steps | 106 | 101 (95%) |
| ↳ WISQ vince su steps | 18 (ratio mediana 0.87×) | 18 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **221 / 261 (84.7%)** | — |

---

## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Timeout imposto simmetricamente a entrambi.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 261 | — |
| Nostro mapping fallisce a −3 | 5 | — |
| **WISQ non finisce in 1min** | 136 | — |
| ↳ …ma anche noi sforiamo 1min → nessun vincitore | 38 | — |
| ↳ …noi finiamo entro 1min → **vittoria** | 98 | — |
| **Noi non finiamo, WISQ sì → sconfitta** | 3 | — |
| **Entrambi finiscono in 1min** | 122 | — |
| ↳ Noi vinciamo su steps | 24 (ratio mediana 1.81×) | 23 (96%) |
| ↳ Pareggio su steps | 91 | 87 (96%) |
| ↳ WISQ vince su steps | 7 (ratio mediana 0.93×) | 7 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **209 / 261 (80.1%)** | — |

---

## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (asimm.) | 236 | 20 | 0 | 0 | **160 (61.3%)** |
| 1 ora | 196 | 55 | 0 | 10 | **194 (74.3%)** |
| 30 minuti | 182 | 68 | 0 | 11 | **205 (78.5%)** |
| 15 minuti | 168 | 80 | 0 | 13 | **212 (81.2%)** |
| 10 minuti | 163 | 82 | 0 | 16 | **214 (82.0%)** |
| 5 minuti | 152 | 92 | 0 | 17 | **221 (84.7%)** ⟵ picco |
| 1 minuto | 122 | 98 | 3 | 38 | **209 (80.1%)** |

---

## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s` sui 256 circuiti che mappiamo a −3.

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 256 | 245 (96%) | 430× | 720× | 0.10× | 26700× |
| ↳ Dove vinciamo su steps | 28 | 25 (89%) | 150× | 176× | 0.10× | 440× |
| ↳ In pareggio su steps | 117 | 112 (96%) | 575× | 701× | 0.23× | 7062× |
| ↳ Dove WISQ vince su steps | 91 | 91 (100%) | 542× | 1005× | 13.87× | 26700× |
| ↳ WISQ in timeout | 20 | 17 (85%) | 21× | 298× | 0.39× | 2408× |

---

## Per famiglia di circuiti

**WISQ timeout** = `mr_timeout=12000s`. **MapFail** = il nostro mapping non riesce alla griglia shrinkata.

| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | MapFail −3 | Note |
|--------|---|-----|----------------|------|--------------|-----------|------|
| 19qubits | 2 | 0 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=19 |
| 53qubits | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=27–39 |
| adder | 5 | 0 | 3 (2 noi+veloci) | 0 | 0 | 2 | n=28–433 |
| bv | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=153 |
| bwt | 5 | 0 | 0 | 0 | 5 | 0 | n=21–133 |
| cat | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| dnn | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=16 |
| example | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=4 |
| factor247 | 1 | 0 | 0 | 0 | 1 | 0 | n=15 |
| fredkin | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| ghz | 18 | 0 | 18 (15 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| ghz_state | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=23–255 |
| graphstate | 17 | 10 | 7 (7 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| grover | 3 | 0 | 0 | 1 | 1 | 1 | n=10–20 |
| hhl | 1 | 0 | 0 | 0 | 0 | 1 |  |
| ising | 19 | 17 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=5–420 |
| multiplier | 11 | 0 | 4 (3 noi+veloci) | 3 | 4 | 0 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 0 | 4 (4 noi+veloci) | 15 | 1 | 0 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5 |
| qft | 22 | 0 | 2 (2 noi+veloci) | 19 | 1 | 0 | n=5–400 |
| qpe_n9 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=9 |
| qram | 1 | 0 | 0 | 0 | 0 | 1 |  |
| randomcircuit | 5 | 0 | 0 | 2 | 3 | 0 | n=50–500 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| square_root | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=14–32 |
| synth | 37 | 0 | 0 | 36 | 1 | 0 | n=50–200 |
| t_test | 2 | 0 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=8 |
| toffoli | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| vqe_real_amp | 17 | 0 | 17 (17 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| vqe_su2 | 17 | 0 | 17 (17 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| vqe_two_local | 17 | 0 | 1 (1 noi+veloci) | 13 | 3 | 0 | n=5–400 |
| vqe_uccsd | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=4–8 |
| wstate | 18 | 0 | 18 (18 noi+veloci) | 0 | 0 | 0 | n=5–400 |

---

## Per circuito (dettaglio)

**Δlati** = quanti lati sotto WISQ (`dim_diff_side`). **Steps**: WIN/=/LOSS. **MapFail** = mapping non riuscito.

| # | Circuit | Qubits | Grid (nostra) | Δlati | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|---------------|-------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 10×10 | +3 | 102 | 99 | 0.9706 | success | LOSS | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 10×10 | +3 | 286 | 286 | 1.0000 | success | = | noi +veloci |
| 3 | 53qubits_155gate_57layers | 27 | 12×12 | +3 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 4 | 53qubits_332gate_152layers | 39 | 14×14 | +3 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 12×12 | +3 | 24 | 24 | 1.0000 | success | = | noi +veloci |
| 6 | adder_n4 | — | — | — | — | — | — | error | **MapFail −3** | — |
| 7 | adder_n433 | 433 | 42×42 | +3 | 250 | 250 | 1.0000 | success | = | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 16×16 | +3 | 181 | 181 | 1.0000 | success | = | WISQ +veloce |
| 9 | bigadder_n18_transpiled | — | — | — | — | — | — | error | **MapFail −3** | — |
| 10 | bv_n280 | 153 | 34×34 | −5 | 152 | 152 | 1.0000 | success | = | noi +veloci |
| 11 | bwt_n177 | 133 | 24×24 | +3 | 257605 | — | — | failed | timeout | — |
| 12 | bwt_n21 | 21 | 10×10 | +3 | 116400 | — | — | failed | timeout | — |
| 13 | bwt_n37 | 28 | 12×12 | +3 | 33603 | — | — | failed | timeout | — |
| 14 | bwt_n57 | 43 | 14×14 | +3 | 65644 | — | — | failed | timeout | — |
| 15 | bwt_n97 | 73 | 18×18 | +3 | 129673 | — | — | failed | timeout | — |
| 16 | cat_n130 | 130 | 24×24 | +3 | 129 | 129 | 1.0000 | success | = | noi +veloci |
| 17 | cat_n260 | 260 | 34×34 | +3 | 259 | 259 | 1.0000 | success | = | noi +veloci |
| 18 | continuous_3_17_13 | 3 | 4×4 | +3 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 19 | dnn_n16 | 16 | 8×8 | +3 | 48 | 48 | 1.0000 | success | = | noi +veloci |
| 20 | example | 4 | 4×4 | +3 | 21 | 21 | 1.0000 | success | = | noi +veloci |
| 21 | factor247_n15 | 15 | 8×8 | +3 | 352856 | — | — | failed | timeout | — |
| 22 | fredkin_n3 | 3 | 4×4 | +3 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 23 | ghz_n10 | 10 | 8×8 | +3 | 9 | 9 | 1.0000 | success | = | noi +veloci |
| 24 | ghz_n100 | 100 | 20×20 | +3 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 25 | ghz_n125 | 125 | 24×24 | +3 | 124 | 124 | 1.0000 | success | = | WISQ +veloce |
| 26 | ghz_n150 | 150 | 26×26 | +3 | 149 | 149 | 1.0000 | success | = | WISQ +veloce |
| 27 | ghz_n175 | 175 | 28×28 | +3 | 174 | 174 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n20 | 20 | 10×10 | +3 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 29 | ghz_n200 | 200 | 30×30 | +3 | 199 | 199 | 1.0000 | success | = | noi +veloci |
| 30 | ghz_n255 | 255 | 32×32 | +3 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 31 | ghz_n30 | 30 | 12×12 | +3 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n300 | 300 | 36×36 | +3 | 299 | 299 | 1.0000 | success | = | noi +veloci |
| 33 | ghz_n40 | 40 | 14×14 | +3 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 34 | ghz_n400 | 400 | 40×40 | +3 | 399 | 399 | 1.0000 | success | = | noi +veloci |
| 35 | ghz_n5 | 5 | 6×6 | +3 | 4 | 4 | 1.0000 | success | = | WISQ +veloce |
| 36 | ghz_n50 | 50 | 16×16 | +3 | 49 | 49 | 1.0000 | success | = | noi +veloci |
| 37 | ghz_n60 | 60 | 16×16 | +3 | 59 | 59 | 1.0000 | success | = | noi +veloci |
| 38 | ghz_n70 | 70 | 18×18 | +3 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 39 | ghz_n80 | 80 | 18×18 | +3 | 79 | 79 | 1.0000 | success | = | noi +veloci |
| 40 | ghz_n90 | 90 | 20×20 | +3 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 41 | ghz_state_n23 | 23 | 10×10 | +3 | 22 | 22 | 1.0000 | success | = | noi +veloci |
| 42 | ghz_state_n255 | 255 | 32×32 | +3 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 43 | graphstate_n10 | 10 | 8×8 | +3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 44 | graphstate_n100 | 100 | 20×20 | +3 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 45 | graphstate_n125 | 125 | 24×24 | +3 | 5 | 8 | 1.6000 | success | **WIN** | noi +veloci |
| 46 | graphstate_n150 | 150 | 26×26 | +3 | 6 | 8 | 1.3333 | success | **WIN** | noi +veloci |
| 47 | graphstate_n175 | 175 | 28×28 | +3 | 7 | 9 | 1.2857 | success | **WIN** | noi +veloci |
| 48 | graphstate_n20 | 20 | 10×10 | +3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 49 | graphstate_n200 | 200 | 30×30 | +3 | 6 | 11 | 1.8333 | success | **WIN** | noi +veloci |
| 50 | graphstate_n30 | 30 | 12×12 | +3 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 51 | graphstate_n300 | 300 | 36×36 | +3 | 9 | 16 | 1.7778 | success | **WIN** | noi +veloci |
| 52 | graphstate_n40 | 40 | 14×14 | +3 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 53 | graphstate_n400 | 400 | 40×40 | +3 | 7 | 21 | 3.0000 | success | **WIN** | noi +veloci |
| 54 | graphstate_n5 | 5 | 6×6 | +3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 55 | graphstate_n50 | 50 | 16×16 | +3 | 5 | 5 | 1.0000 | success | = | noi +veloci |
| 56 | graphstate_n60 | 60 | 16×16 | +3 | 5 | 5 | 1.0000 | success | = | noi +veloci |
| 57 | graphstate_n70 | 70 | 18×18 | +3 | 5 | 7 | 1.4000 | success | **WIN** | noi +veloci |
| 58 | graphstate_n80 | 80 | 18×18 | +3 | 6 | 7 | 1.1667 | success | **WIN** | noi +veloci |
| 59 | graphstate_n90 | 90 | 20×20 | +3 | 5 | 7 | 1.4000 | success | **WIN** | noi +veloci |
| 60 | grover_n10 | 10 | 6×6 | +5 | 11127 | 11008 | 0.9893 | success | LOSS | noi +veloci |
| 61 | grover_n20 | 20 | 10×10 | +3 | 2146489 | — | — | failed | timeout | — |
| 62 | grover_n5 | — | — | — | — | — | — | error | **MapFail −3** | — |
| 63 | hhl_n10 | — | — | — | — | — | — | error | **MapFail −3** | — |
| 64 | ising_n10 | 10 | 8×8 | +3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 65 | ising_n100 | 100 | 20×20 | +3 | 4 | 13 | 3.2500 | success | **WIN** | noi +veloci |
| 66 | ising_n125 | 125 | 24×24 | +3 | 4 | 16 | 4.0000 | success | **WIN** | noi +veloci |
| 67 | ising_n150 | 150 | 26×26 | +3 | 4 | 18 | 4.5000 | success | **WIN** | noi +veloci |
| 68 | ising_n175 | 175 | 28×28 | +3 | 4 | 21 | 5.2500 | success | **WIN** | WISQ +veloce |
| 69 | ising_n20 | 20 | 10×10 | +3 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 70 | ising_n200 | 200 | 30×30 | +3 | 4 | 23 | 5.7500 | success | **WIN** | noi +veloci |
| 71 | ising_n26 | 26 | 12×12 | +3 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 72 | ising_n30 | 30 | 12×12 | +3 | 4 | 7 | 1.7500 | success | **WIN** | noi +veloci |
| 73 | ising_n300 | 300 | 36×36 | +3 | 4 | 32 | 8.0000 | success | **WIN** | noi +veloci |
| 74 | ising_n40 | 40 | 14×14 | +3 | 4 | 7 | 1.7500 | success | **WIN** | WISQ +veloce |
| 75 | ising_n400 | 400 | 40×40 | +3 | 4 | 40 | 10.0000 | success | **WIN** | noi +veloci |
| 76 | ising_n420 | 420 | 42×42 | +3 | 4 | 41 | 10.2500 | success | **WIN** | WISQ +veloce |
| 77 | ising_n5 | 5 | 6×6 | +3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 78 | ising_n50 | 50 | 16×16 | +3 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 79 | ising_n60 | 60 | 16×16 | +3 | 4 | 9 | 2.2500 | success | **WIN** | noi +veloci |
| 80 | ising_n70 | 70 | 18×18 | +3 | 4 | 9 | 2.2500 | success | **WIN** | noi +veloci |
| 81 | ising_n80 | 80 | 18×18 | +3 | 4 | 11 | 2.7500 | success | **WIN** | noi +veloci |
| 82 | ising_n90 | 90 | 20×20 | +3 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 83 | multiplier_n100 | 100 | 20×20 | +3 | 111981 | — | — | failed | timeout | — |
| 84 | multiplier_n15 | 9 | 6×6 | +3 | 12 | 12 | 1.0000 | success | = | noi +veloci |
| 85 | multiplier_n20 | 20 | 10×10 | +3 | 3990 | 3990 | 1.0000 | success | = | noi +veloci |
| 86 | multiplier_n200 | 200 | 30×30 | +3 | 450798 | — | — | failed | timeout | — |
| 87 | multiplier_n300 | 300 | 36×36 | +3 | 1018785 | — | — | failed | timeout | — |
| 88 | multiplier_n40 | 40 | 14×14 | +3 | 17335 | 17329 | 0.9997 | success | LOSS | noi +veloci |
| 89 | multiplier_n400 | 400 | 40×40 | +3 | 1818879 | — | — | failed | timeout | — |
| 90 | multiplier_n45 | 27 | 14×14 | +1 | 36 | 36 | 1.0000 | success | = | WISQ +veloce |
| 91 | multiplier_n60 | 60 | 16×16 | +3 | 39737 | 39730 | 0.9998 | success | LOSS | noi +veloci |
| 92 | multiplier_n75 | 45 | 18×18 | −1 | 60 | 60 | 1.0000 | success | = | noi +veloci |
| 93 | multiplier_n80 | 80 | 18×18 | +3 | 71399 | 71287 | 0.9984 | success | LOSS | noi +veloci |
| 94 | multiply_n13 | 6 | 6×6 | +3 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 95 | parallel | 8 | 6×6 | +3 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 96 | parallel_big | 20 | 10×10 | +3 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 97 | qaoa_n10 | 10 | 8×8 | +3 | 46 | 46 | 1.0000 | success | = | noi +veloci |
| 98 | qaoa_n100 | 100 | 20×20 | +3 | 1344 | 882 | 0.6562 | success | LOSS | noi +veloci |
| 99 | qaoa_n125 | 125 | 24×24 | +3 | 1678 | 1265 | 0.7539 | success | LOSS | noi +veloci |
| 100 | qaoa_n150 | 150 | 26×26 | +3 | 2331 | 1724 | 0.7396 | success | LOSS | noi +veloci |
| 101 | qaoa_n175 | 175 | 28×28 | +3 | 2939 | 2270 | 0.7724 | success | LOSS | noi +veloci |
| 102 | qaoa_n20 | 20 | 10×10 | +3 | 97 | 90 | 0.9278 | success | LOSS | noi +veloci |
| 103 | qaoa_n200 | 200 | 30×30 | +3 | 3651 | 2852 | 0.7812 | success | LOSS | noi +veloci |
| 104 | qaoa_n30 | 30 | 12×12 | +3 | 166 | 138 | 0.8313 | success | LOSS | noi +veloci |
| 105 | qaoa_n300 | 300 | 36×36 | +3 | 7361 | 5968 | 0.8108 | success | LOSS | noi +veloci |
| 106 | qaoa_n40 | 40 | 14×14 | +3 | 262 | 205 | 0.7824 | success | LOSS | noi +veloci |
| 107 | qaoa_n400 | 400 | 40×40 | +3 | 13016 | — | — | failed | timeout | — |
| 108 | qaoa_n5 | 5 | 6×6 | +3 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 109 | qaoa_n50 | 50 | 16×16 | +3 | 356 | 285 | 0.8006 | success | LOSS | noi +veloci |
| 110 | qaoa_n6 | 6 | 6×6 | +3 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 111 | qaoa_n60 | 60 | 16×16 | +3 | 538 | 389 | 0.7230 | success | LOSS | noi +veloci |
| 112 | qaoa_n64 | 64 | 16×16 | +3 | 616 | 422 | 0.6851 | success | LOSS | noi +veloci |
| 113 | qaoa_n6_transpiled | 6 | 6×6 | +3 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 114 | qaoa_n70 | 70 | 18×18 | +3 | 653 | 474 | 0.7259 | success | LOSS | noi +veloci |
| 115 | qaoa_n80 | 80 | 18×18 | +3 | 855 | 593 | 0.6936 | success | LOSS | noi +veloci |
| 116 | qaoa_n90 | 90 | 20×20 | +3 | 975 | 728 | 0.7467 | success | LOSS | noi +veloci |
| 117 | qec_en_n5 | 5 | 6×6 | +3 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 118 | qft_20 | 20 | 10×10 | +3 | 90 | 84 | 0.9333 | success | LOSS | noi +veloci |
| 119 | qft_n10 | 10 | 8×8 | +3 | 34 | 34 | 1.0000 | success | = | noi +veloci |
| 120 | qft_n100 | 100 | 20×20 | +3 | 675 | 440 | 0.6519 | success | LOSS | noi +veloci |
| 121 | qft_n125 | 125 | 24×24 | +3 | 2608 | 532 | 0.2040 | success | LOSS | noi +veloci |
| 122 | qft_n128 | 128 | 24×24 | +3 | 2679 | 539 | 0.2012 | success | LOSS | noi +veloci |
| 123 | qft_n150 | 150 | 26×26 | +3 | 3083 | 631 | 0.2047 | success | LOSS | noi +veloci |
| 124 | qft_n175 | 175 | 28×28 | +3 | 3808 | 728 | 0.1912 | success | LOSS | noi +veloci |
| 125 | qft_n18 | 18 | 10×10 | +3 | 75 | 71 | 0.9467 | success | LOSS | noi +veloci |
| 126 | qft_n20 | 20 | 10×10 | +3 | 90 | 82 | 0.9111 | success | LOSS | noi +veloci |
| 127 | qft_n200 | 200 | 30×30 | +3 | 4270 | 826 | 0.1934 | success | LOSS | noi +veloci |
| 128 | qft_n30 | 30 | 12×12 | +3 | 154 | 134 | 0.8701 | success | LOSS | noi +veloci |
| 129 | qft_n300 | 300 | 36×36 | +3 | 6978 | 1247 | 0.1787 | success | LOSS | noi +veloci |
| 130 | qft_n320 | 320 | 36×36 | +3 | 9134 | — | — | failed | timeout | — |
| 131 | qft_n40 | 40 | 14×14 | +3 | 214 | 181 | 0.8458 | success | LOSS | noi +veloci |
| 132 | qft_n400 | 400 | 40×40 | +3 | 9331 | 1672 | 0.1792 | success | LOSS | noi +veloci |
| 133 | qft_n5 | 5 | 6×6 | +3 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 134 | qft_n50 | 50 | 16×16 | +3 | 263 | 221 | 0.8403 | success | LOSS | noi +veloci |
| 135 | qft_n60 | 60 | 16×16 | +3 | 371 | 270 | 0.7278 | success | LOSS | noi +veloci |
| 136 | qft_n64 | 64 | 16×16 | +3 | 426 | 292 | 0.6854 | success | LOSS | noi +veloci |
| 137 | qft_n70 | 70 | 18×18 | +3 | 393 | 307 | 0.7812 | success | LOSS | noi +veloci |
| 138 | qft_n80 | 80 | 18×18 | +3 | 488 | 357 | 0.7316 | success | LOSS | noi +veloci |
| 139 | qft_n90 | 90 | 20×20 | +3 | 521 | 396 | 0.7601 | success | LOSS | noi +veloci |
| 140 | qpe_n9_transpiled | 9 | 6×6 | +3 | 42 | 42 | 1.0000 | success | = | noi +veloci |
| 141 | qram_n20 | — | — | — | — | — | — | error | **MapFail −3** | — |
| 142 | randomcircuit_n100 | 100 | 20×20 | +3 | 8799 | 4423 | 0.5027 | success | LOSS | noi +veloci |
| 143 | randomcircuit_n200 | 200 | 30×30 | +3 | 29983 | — | — | failed | timeout | — |
| 144 | randomcircuit_n400 | 400 | 40×40 | +3 | 241958 | — | — | failed | timeout | — |
| 145 | randomcircuit_n50 | 50 | 16×16 | +3 | 1831 | 1453 | 0.7936 | success | LOSS | noi +veloci |
| 146 | randomcircuit_n500 | 500 | 46×46 | +3 | 195087 | — | — | failed | timeout | — |
| 147 | seca_n11 | 11 | 8×8 | +3 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 148 | simon_n6 | 3 | 4×4 | +3 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 149 | square_root_n18 | 14 | 8×8 | +3 | 27 | 27 | 1.0000 | success | = | noi +veloci |
| 150 | square_root_n45 | 32 | 12×12 | +3 | 570 | 570 | 1.0000 | success | = | noi +veloci |
| 151 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 20×20 | +3 | 367 | 154 | 0.4196 | success | LOSS | noi +veloci |
| 152 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 20×20 | +3 | 389 | 149 | 0.3830 | success | LOSS | noi +veloci |
| 153 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 20×20 | +3 | 365 | 194 | 0.5315 | success | LOSS | noi +veloci |
| 154 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 20×20 | +3 | 460 | 190 | 0.4130 | success | LOSS | noi +veloci |
| 155 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 20×20 | +3 | 329 | 206 | 0.6261 | success | LOSS | noi +veloci |
| 156 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 20×20 | +3 | 469 | 207 | 0.4414 | success | LOSS | noi +veloci |
| 157 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 20×20 | +3 | 760 | 371 | 0.4882 | success | LOSS | noi +veloci |
| 158 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 20×20 | +3 | 738 | 382 | 0.5176 | success | LOSS | noi +veloci |
| 159 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 20×20 | +3 | 675 | 392 | 0.5807 | success | LOSS | noi +veloci |
| 160 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 20×20 | +3 | 665 | 397 | 0.5970 | success | LOSS | noi +veloci |
| 161 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 20×20 | +3 | 733 | 426 | 0.5812 | success | LOSS | noi +veloci |
| 162 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 20×20 | +3 | 667 | 431 | 0.6462 | success | LOSS | noi +veloci |
| 163 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 30×30 | +3 | 1571 | 401 | 0.2553 | success | LOSS | noi +veloci |
| 164 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 30×30 | +3 | 1278 | 389 | 0.3044 | success | LOSS | noi +veloci |
| 165 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 30×30 | +3 | 1568 | 605 | 0.3858 | success | LOSS | noi +veloci |
| 166 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 30×30 | +3 | 1435 | 609 | 0.4244 | success | LOSS | noi +veloci |
| 167 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 30×30 | +3 | 1626 | 647 | 0.3979 | success | LOSS | noi +veloci |
| 168 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 30×30 | +3 | 1586 | 654 | 0.4124 | success | LOSS | noi +veloci |
| 169 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 30×30 | +3 | 1763 | 1185 | 0.6721 | success | LOSS | noi +veloci |
| 170 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 30×30 | +3 | 1776 | 1185 | 0.6672 | success | LOSS | noi +veloci |
| 171 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 30×30 | +3 | 1770 | 1246 | 0.7040 | success | LOSS | noi +veloci |
| 172 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 30×30 | +3 | 1932 | — | — | failed | timeout | — |
| 173 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 30×30 | +3 | 2207 | 1412 | 0.6398 | success | LOSS | noi +veloci |
| 174 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 30×30 | +3 | 1893 | 1415 | 0.7475 | success | LOSS | noi +veloci |
| 175 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 16×16 | +3 | 92 | 60 | 0.6522 | success | LOSS | noi +veloci |
| 176 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 16×16 | +3 | 82 | 60 | 0.7317 | success | LOSS | noi +veloci |
| 177 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 16×16 | +3 | 91 | 70 | 0.7692 | success | LOSS | noi +veloci |
| 178 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 16×16 | +3 | 93 | 74 | 0.7957 | success | LOSS | noi +veloci |
| 179 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 16×16 | +3 | 92 | 70 | 0.7609 | success | LOSS | noi +veloci |
| 180 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 16×16 | +3 | 89 | 72 | 0.8090 | success | LOSS | noi +veloci |
| 181 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 16×16 | +3 | 130 | 108 | 0.8308 | success | LOSS | noi +veloci |
| 182 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 16×16 | +3 | 177 | 132 | 0.7458 | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 16×16 | +3 | 166 | 135 | 0.8133 | success | LOSS | noi +veloci |
| 184 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 16×16 | +3 | 180 | 147 | 0.8167 | success | LOSS | noi +veloci |
| 185 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 16×16 | +3 | 181 | 153 | 0.8453 | success | LOSS | noi +veloci |
| 186 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 16×16 | +3 | 180 | 147 | 0.8167 | success | LOSS | noi +veloci |
| 187 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 16×16 | +3 | 183 | 145 | 0.7923 | success | LOSS | noi +veloci |
| 188 | t_test | 8 | 6×6 | +3 | 110 | 110 | 1.0000 | success | = | noi +veloci |
| 189 | t_test2 | 8 | 6×6 | +3 | 3907 | 3904 | 0.9992 | success | LOSS | noi +veloci |
| 190 | toffoli_n3 | 3 | 4×4 | +3 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 191 | vqe_real_amp_n10 | 10 | 8×8 | +3 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 192 | vqe_real_amp_n100 | 100 | 20×20 | +3 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 193 | vqe_real_amp_n125 | 125 | 24×24 | +3 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 194 | vqe_real_amp_n150 | 150 | 26×26 | +3 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 195 | vqe_real_amp_n175 | 175 | 28×28 | +3 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 196 | vqe_real_amp_n20 | 20 | 10×10 | +3 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 197 | vqe_real_amp_n200 | 200 | 30×30 | +3 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 198 | vqe_real_amp_n30 | 30 | 12×12 | +3 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 199 | vqe_real_amp_n300 | 300 | 36×36 | +3 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 200 | vqe_real_amp_n40 | 40 | 14×14 | +3 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 201 | vqe_real_amp_n400 | 400 | 40×40 | +3 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 202 | vqe_real_amp_n5 | 5 | 6×6 | +3 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 203 | vqe_real_amp_n50 | 50 | 16×16 | +3 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 204 | vqe_real_amp_n60 | 60 | 16×16 | +3 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 205 | vqe_real_amp_n70 | 70 | 18×18 | +3 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 206 | vqe_real_amp_n80 | 80 | 18×18 | +3 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 207 | vqe_real_amp_n90 | 90 | 20×20 | +3 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 208 | vqe_su2_n10 | 10 | 8×8 | +3 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 209 | vqe_su2_n100 | 100 | 20×20 | +3 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 210 | vqe_su2_n125 | 125 | 24×24 | +3 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 211 | vqe_su2_n150 | 150 | 26×26 | +3 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 212 | vqe_su2_n175 | 175 | 28×28 | +3 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 213 | vqe_su2_n20 | 20 | 10×10 | +3 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 214 | vqe_su2_n200 | 200 | 30×30 | +3 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 215 | vqe_su2_n30 | 30 | 12×12 | +3 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 216 | vqe_su2_n300 | 300 | 36×36 | +3 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 217 | vqe_su2_n40 | 40 | 14×14 | +3 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 218 | vqe_su2_n400 | 400 | 40×40 | +3 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 219 | vqe_su2_n5 | 5 | 6×6 | +3 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 220 | vqe_su2_n50 | 50 | 16×16 | +3 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 221 | vqe_su2_n60 | 60 | 16×16 | +3 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 222 | vqe_su2_n70 | 70 | 18×18 | +3 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 223 | vqe_su2_n80 | 80 | 18×18 | +3 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 224 | vqe_su2_n90 | 90 | 20×20 | +3 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 225 | vqe_two_local_n10 | 10 | 8×8 | +3 | 40 | 37 | 0.9250 | success | LOSS | noi +veloci |
| 226 | vqe_two_local_n100 | 100 | 20×20 | +3 | 1765 | 1396 | 0.7909 | success | LOSS | noi +veloci |
| 227 | vqe_two_local_n125 | 125 | 24×24 | +3 | 2367 | 1959 | 0.8276 | success | LOSS | noi +veloci |
| 228 | vqe_two_local_n150 | 150 | 26×26 | +3 | 3214 | 2725 | 0.8479 | success | LOSS | noi +veloci |
| 229 | vqe_two_local_n175 | 175 | 28×28 | +3 | 4307 | 3526 | 0.8187 | success | LOSS | noi +veloci |
| 230 | vqe_two_local_n20 | 20 | 10×10 | +3 | 111 | 97 | 0.8739 | success | LOSS | noi +veloci |
| 231 | vqe_two_local_n200 | 200 | 30×30 | +3 | 5338 | — | — | failed | timeout | — |
| 232 | vqe_two_local_n30 | 30 | 12×12 | +3 | 211 | 185 | 0.8768 | success | LOSS | noi +veloci |
| 233 | vqe_two_local_n300 | 300 | 36×36 | +3 | 10983 | — | — | failed | timeout | — |
| 234 | vqe_two_local_n40 | 40 | 14×14 | +3 | 342 | 295 | 0.8626 | success | LOSS | noi +veloci |
| 235 | vqe_two_local_n400 | 400 | 40×40 | +3 | 18986 | — | — | failed | timeout | — |
| 236 | vqe_two_local_n5 | 5 | 6×6 | +3 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 237 | vqe_two_local_n50 | 50 | 16×16 | +3 | 476 | 409 | 0.8592 | success | LOSS | noi +veloci |
| 238 | vqe_two_local_n60 | 60 | 16×16 | +3 | 727 | 580 | 0.7978 | success | LOSS | noi +veloci |
| 239 | vqe_two_local_n70 | 70 | 18×18 | +3 | 874 | 733 | 0.8387 | success | LOSS | noi +veloci |
| 240 | vqe_two_local_n80 | 80 | 18×18 | +3 | 1185 | 950 | 0.8017 | success | LOSS | noi +veloci |
| 241 | vqe_two_local_n90 | 90 | 20×20 | +3 | 1374 | 1136 | 0.8268 | success | LOSS | noi +veloci |
| 242 | vqe_uccsd_n4 | 4 | 4×4 | +3 | 87 | 87 | 1.0000 | success | = | noi +veloci |
| 243 | vqe_uccsd_n8 | 8 | 6×6 | +3 | 5446 | 5446 | 1.0000 | success | = | noi +veloci |
| 244 | wstate_n10 | 10 | 8×8 | +3 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 245 | wstate_n100 | 100 | 20×20 | +3 | 101 | 101 | 1.0000 | success | = | noi +veloci |
| 246 | wstate_n125 | 125 | 24×24 | +3 | 126 | 126 | 1.0000 | success | = | noi +veloci |
| 247 | wstate_n150 | 150 | 26×26 | +3 | 151 | 151 | 1.0000 | success | = | noi +veloci |
| 248 | wstate_n175 | 175 | 28×28 | +3 | 176 | 176 | 1.0000 | success | = | noi +veloci |
| 249 | wstate_n20 | 20 | 10×10 | +3 | 21 | 21 | 1.0000 | success | = | noi +veloci |
| 250 | wstate_n200 | 200 | 30×30 | +3 | 201 | 201 | 1.0000 | success | = | noi +veloci |
| 251 | wstate_n27 | 27 | 12×12 | +3 | 28 | 28 | 1.0000 | success | = | noi +veloci |
| 252 | wstate_n30 | 30 | 12×12 | +3 | 31 | 31 | 1.0000 | success | = | noi +veloci |
| 253 | wstate_n300 | 300 | 36×36 | +3 | 301 | 301 | 1.0000 | success | = | noi +veloci |
| 254 | wstate_n40 | 40 | 14×14 | +3 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 255 | wstate_n400 | 400 | 40×40 | +3 | 401 | 401 | 1.0000 | success | = | noi +veloci |
| 256 | wstate_n5 | 5 | 6×6 | +3 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 257 | wstate_n50 | 50 | 16×16 | +3 | 51 | 51 | 1.0000 | success | = | noi +veloci |
| 258 | wstate_n60 | 60 | 16×16 | +3 | 61 | 61 | 1.0000 | success | = | noi +veloci |
| 259 | wstate_n70 | 70 | 18×18 | +3 | 71 | 71 | 1.0000 | success | = | noi +veloci |
| 260 | wstate_n80 | 80 | 18×18 | +3 | 81 | 81 | 1.0000 | success | = | noi +veloci |
| 261 | wstate_n90 | 90 | 20×20 | +3 | 91 | 91 | 1.0000 | success | = | noi +veloci |
