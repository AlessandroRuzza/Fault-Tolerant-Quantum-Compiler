# random / cube / WISQ — analisi confronto (griglia di WISQ)

Generato il 2026-06-28. Tutti i metodi valutati sulla **stessa griglia di WISQ** (`wisq_x`/`wisq_y` letti da `connectivity_summary_all_wisq.csv`, WISQ non rieseguito). Metrica = `routing_steps`, **più basso = meglio**.

- 258 circuiti · 516 run del nostro compilatore (258 `random` + 258 `cube`), tutti riusciti (4 `cube` ricaduti su connectivity). 16 circuiti **n/a** = WISQ in timeout nel baseline.

## 1. Sintesi delle tre comparazioni

| confronto | A meglio | B meglio | pari | n/a | geomean B/A |
|---|---|---|---|---|---|
| **random** vs **WISQ** | 0 | 192 | 50 | 16 | 0.771 |
| **cube** vs **WISQ** | 19 | 128 | 95 | 16 | 0.887 |
| **random** vs **cube** | 76 | 132 | 50 | 0 | 0.876 |

*(geomean B/A > 1 ⇒ A usa meno step; A = primo metodo della riga.)*

**Lettura.** `random` non batte mai WISQ a parità di griglia (è un *floor*, ~23% di step in più). `cube` recupera circa metà del divario (~11% dietro WISQ). `random` vs `cube`: cube vince su più circuiti (132 vs 76), ma la mediana è 1.0 — il segnale è nelle code (vedi famiglie).

## 2. random vs cube per famiglia

| famiglia | random meglio | cube meglio | pari | geomean cube/random | chi domina |
|---|---|---|---|---|---|
| synth | 4 | 31 | 2 | 0.90 | **cube** |
| qft | 21 | 0 | 1 | 1.10 | **random** |
| qaoa | 18 | 1 | 1 | 1.05 | **random** |
| ising | 0 | 18 | 1 | 0.30 | **cube** |
| ghz | 0 | 0 | 18 | 1.00 | **—** |
| wstate | 0 | 16 | 2 | 0.96 | **cube** |
| graphstate | 2 | 11 | 4 | 0.75 | **cube** |
| vqe_real_amp | 0 | 17 | 0 | 0.90 | **cube** |
| vqe_su | 0 | 16 | 1 | 0.90 | **cube** |
| vqe_two_local | 15 | 1 | 1 | 1.11 | **random** |
| multiplier | 4 | 6 | 1 | 0.89 | **cube** |
| bwt | 1 | 4 | 0 | 0.98 | **cube** |
| adder | 2 | 1 | 1 | 1.00 | **random** |
| randomcircuit | 0 | 4 | 0 | 0.86 | **cube** |
| grover | 2 | 0 | 1 | 1.01 | **random** |
| cat | 0 | 0 | 2 | 1.00 | **—** |
| ghz_state | 0 | 0 | 2 | 1.00 | **—** |
| square_root | 0 | 2 | 0 | 0.70 | **cube** |
| vqe_uccsd | 0 | 1 | 1 | 1.00 | **cube** |

**cube stravince** dove c'è località da sfruttare: `ising` (geomean 0.30, fino a 10×), `vqe_real_amp`/`vqe_su`, `wstate`, `graphstate`, `square_root`, `synth`. **random batte cube** sui circuiti densi/all-to-all: `qft` (21-0), `qaoa` (18-1), `vqe_two_local` (15-1) — lì il mapping intelligente non trova località e lo spread casuale fa meglio.

## 3. Candidati per `random` con repetition

Domanda: nei circuiti dove **cube perde contro WISQ**, `random` si avvicina? Se sì, girare `random` con repetition (best-of-N seed) potrebbe recuperare la sconfitta. `random_mapping` è stocastico (mt19937 non seedato), quindi questi sono **un singolo campione**: la repetition prende il minimo su N estrazioni.

Circuiti dove cube perde vs WISQ (cube>wisq, wisq success): **128**.

### A) random GIÀ ≤ WISQ — repetition vince quasi sicuro (7)

Random già pareggia WISQ mentre cube perde: con repetition può consolidare o superare.

| circuito | wisq | cube | random |
|---|---|---|---|
| 53qubits_332gate_152layers | 41 | 44 | **41** |
| graphstate_n10 | 4 | 5 | **4** |
| multiplier_n20 | 3990 | 3997 | **3990** |
| qaoa_n6 | 33 | 39 | **33** |
| qft_n10 | 34 | 45 | **34** |
| qram_n20 | 8 | 10 | **8** |
| seca_n11 | 19 | 23 | **19** |

### B) random < cube ed entro +30% di WISQ — repetition promettente (15)

| circuito | wisq | cube | random | random/wisq | cube/wisq |
|---|---|---|---|---|---|
| multiplier_n40 | 17329 | 17349 | 17334 | 1.00 | 1.00 |
| multiplier_n80 | 71289 | 71441 | 71387 | 1.00 | 1.00 |
| 19qubits_521gate_352layers | 286 | 292 | 287 | 1.00 | 1.02 |
| grover_n10 | 11008 | 11329 | 11059 | 1.00 | 1.03 |
| 19qubits_511gate_153layers | 99 | 107 | 102 | 1.03 | 1.08 |
| adder_n64_transpiled | 181 | 196 | 191 | 1.06 | 1.08 |
| bigadder_n18_transpiled | 88 | 96 | 93 | 1.06 | 1.09 |
| adder_n28 | 24 | 27 | 26 | 1.08 | 1.12 |
| qft_n18 | 71 | 107 | 80 | 1.13 | 1.51 |
| qaoa_n10 | 46 | 57 | 52 | 1.13 | 1.24 |
| qft_n20 | 82 | 125 | 102 | 1.24 | 1.52 |
| graphstate_n20 | 4 | 7 | 5 | 1.25 | 1.75 |
| synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 146 | 202 | 185 | 1.27 | 1.38 |
| vqe_two_local_n175 | 3552 | 5187 | 4582 | 1.29 | 1.46 |
| vqe_two_local_n150 | 2732 | 4049 | 3536 | 1.29 | 1.48 |

### C) gli altri 106 cube-loss: random NON si avvicina abbastanza

Per lo più i giganti `qaoa`/`qft`/`vqe_two_local` (n≥100): random migliora su cube ma resta 1.3–1.5× WISQ — la repetition difficilmente colma un divario così grande. Non prioritari.

**Conclusione operativa.** I candidati veri per `random`+repetition sono i **~22 circuiti dei gruppi A+B**, concentrati su `qft` piccoli/medi (n10/n18/n20), `qaoa` piccoli (n6/n10), `graphstate`, `qram`, e qualche near-tie (`multiplier`, `adder`, `19qubits`). Consiglio: seed fisso + N=5–10 ripetizioni su questo sottoinsieme, tenere il minimo per circuito.

