# wisq3 — COMPLETO (winner post-hoc) ⚠ NON FAIR, NON same-grid


ATTENZIONE doppia: (1) per ogni circuito e' tenuta solo la combo VINCENTE (scelta a posteriori); (2) NON e' same-grid: noi sulla nostra griglia minima, WISQ su una griglia cresciuta (area mediana 1.68x). Solo riferimento.


Dati da: `all_circuits_8_variants_our_dimension_wisq3.csv` — **256 circuiti**.


---


## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| ↳ WISQ va in timeout (noi vinciamo) | 41 | — |
| ↳ Entrambi completano | 215 | — |
|   ↳ Noi vinciamo su steps | 48 (ratio mediana 1.50×) | 48 (100.0%) |
|   ↳ Pareggio su steps | 71 | 71 (100.0%) |
|   ↳ WISQ vince su steps | 96 (ratio mediana 0.32×) | 96 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **160 / 256 (62.5%)** | — |
| ↳ Noi completiamo, WISQ va in timeout | 41 / 256 (16.0%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 48 / 256 (18.8%) | — |
| ↳ Pareggio su steps, noi più veloci | 71 / 256 (27.7%) | — |

---


## Routing steps in aggregato (nostro vs WISQ)

Sui 215 circuiti dove **entrambi completano**:

| Metrica | Valore |
|---------|--------|
| Somma `my_routing_steps` | 438.588 |
| Somma `wisq_routing_steps` | 207.270 |
| **Rapporto dei totali (wisq / nostro)** | **0.47 → WISQ usa 52.7% di steps in meno** |
| Mediana di `ratio_wisq_over_mine` | 1.00 |
| Media di `ratio_wisq_over_mine` | 0.960 |

---


## Densità dei circuiti: dove vinciamo vs dove perdiamo

`cnot_interaction_density` = coppie-qubit CNOT distinte / coppie possibili `Q·(Q−1)/2` (0 = sparso/locale, 1 = ogni coppia interagisce). Calcolata dal QASM universale su 214/215 circuiti both-complete con QASM disponibile.

**Per esito sugli steps:**

| Esito (steps) | N | densità media | mediana | min | max |
|---|---|---|---|---|---|
| **Vinciamo** (WIN) | 47 | 0.120 | 0.030 | 0.005 | 1.000 |
| Pareggio (TIE) | 71 | 0.146 | 0.040 | 0.005 | 1.000 |
| **Perdiamo** (LOSS) | 96 | 0.440 | 0.400 | 0.005 | 1.000 |

**Win/Loss per fascia di densità** (sugli steps, both-complete):

| Densità `cid` | N | Win | Tie | Loss | Loss-rate (decisi) |
|---|---|---|---|---|---|
| < 0.15 | 113 | 39 | 52 | 22 | 36.1% |
| 0.15 – 0.40 | 27 | 3 | 7 | 17 | 85.0% |
| ≥ 0.40 | 74 | 5 | 12 | 57 | 91.9% |

---


## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 1 ora** | 72 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 2 | — |
| ↳ …noi finiamo → **vittoria** | 70 | — |
| **Entrambi finiscono in 1 ora** | 184 | — |
| ↳ Noi vinciamo su steps | 47 (ratio mediana 1.50×) | 47 (100.0%) |
| ↳ Pareggio su steps | 71 | 71 (100.0%) |
| ↳ WISQ vince su steps | 66 (ratio mediana 0.46×) | 66 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **188 / 256 (73.4%)** | — |

---


## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 30 minuti** | 81 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 4 | — |
| ↳ …noi finiamo → **vittoria** | 77 | — |
| **Entrambi finiscono in 30 minuti** | 175 | — |
| ↳ Noi vinciamo su steps | 47 (ratio mediana 1.50×) | 47 (100.0%) |
| ↳ Pareggio su steps | 71 | 71 (100.0%) |
| ↳ WISQ vince su steps | 57 (ratio mediana 0.50×) | 57 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **195 / 256 (76.2%)** | — |

---


## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 15 minuti** | 86 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 6 | — |
| ↳ …noi finiamo → **vittoria** | 80 | — |
| **Entrambi finiscono in 15 minuti** | 170 | — |
| ↳ Noi vinciamo su steps | 47 (ratio mediana 1.50×) | 47 (100.0%) |
| ↳ Pareggio su steps | 71 | 71 (100.0%) |
| ↳ WISQ vince su steps | 52 (ratio mediana 0.53×) | 52 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **198 / 256 (77.3%)** | — |

---


## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 10 minuti** | 94 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 6 | — |
| ↳ …noi finiamo → **vittoria** | 88 | — |
| **Entrambi finiscono in 10 minuti** | 162 | — |
| ↳ Noi vinciamo su steps | 47 (ratio mediana 1.50×) | 47 (100.0%) |
| ↳ Pareggio su steps | 71 | 71 (100.0%) |
| ↳ WISQ vince su steps | 44 (ratio mediana 0.59×) | 44 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **206 / 256 (80.5%)** | — |

---


## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 5 minuti** | 99 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 10 | — |
| ↳ …noi finiamo → **vittoria** | 89 | — |
| **Entrambi finiscono in 5 minuti** | 157 | — |
| ↳ Noi vinciamo su steps | 47 (ratio mediana 1.50×) | 47 (100.0%) |
| ↳ Pareggio su steps | 71 | 71 (100.0%) |
| ↳ WISQ vince su steps | 39 (ratio mediana 0.60×) | 39 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **207 / 256 (80.9%)** | — |

---


## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 1 minuto** | 126 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 20 | — |
| ↳ …noi finiamo → **vittoria** | 106 | — |
| **Entrambi finiscono in 1 minuto** | 130 | — |
| ↳ Noi vinciamo su steps | 43 (ratio mediana 1.50×) | 43 (100.0%) |
| ↳ Pareggio su steps | 66 | 66 (100.0%) |
| ↳ WISQ vince su steps | 21 (ratio mediana 0.90×) | 21 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **215 / 256 (84.0%)** | — |

---


## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (orig., asimm.) | 215 | 41 | 0 | 0 | **160 (62.5%)** |
| 1 ora | 184 | 70 | 0 | 2 | **188 (73.4%)** |
| 30 minuti | 175 | 77 | 0 | 4 | **195 (76.2%)** |
| 15 minuti | 170 | 80 | 0 | 6 | **198 (77.3%)** |
| 10 minuti | 162 | 88 | 0 | 6 | **206 (80.5%)** |
| 5 minuti | 157 | 89 | 0 | 10 | **207 (80.9%)** |
| 1 minuto | 130 | 106 | 0 | 20 | **215 (84.0%)** ⟵ picco |

---


## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s`. Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). I timeout WISQ sono inclusi con la durata registrata.

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 256 | 256 (100.0%) | 489× | 12194× | 2.35× | 706515× |
| ↳ Dove vinciamo su steps | 48 | 48 (100.0%) | 310× | 879× | 47.16× | 10556× |
| ↳ In pareggio su steps | 71 | 71 (100.0%) | 590× | 587× | 4.37× | 2334× |
| ↳ Dove WISQ vince su steps | 96 | 96 (100.0%) | 387× | 1147× | 16.37× | 34830× |
| ↳ WISQ in timeout | 41 | 41 (100.0%) | 2692× | 71409× | 2.35× | 706515× |

---


## Buffer di steps dipendente dalla velocità — win-rate vs WISQ

Analisi su `all_circuits_8_variants_our_dimension_wisq3.csv`. La metrica primaria sono i **routing steps**, il tempo è secondario: concediamo un buffer ε sugli steps che cresce con l'ordine di grandezza del vantaggio di tempo.

```
vinco  se   my_steps <= wisq_steps · (1 + ε)
ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time
α = 0.05 / log10(N)      (ancora: 5% di sforo steps ⇄ N× di velocità)
```

Baseline (steps primario, tempo solo spareggio) = **160/256 = 62.5%**.

| ancora | α | loss recuperati | vittorie | % |
|---|---:|---:|---:|---:|
| 5% ⇄ 20× | 0.0384 | 25 | 185 | 72.3% |
| 5% ⇄ 50× | 0.0294 | 24 | 184 | 71.9% |
| 5% ⇄ 100× | 0.0250 | 24 | 184 | 71.9% |
| 5% ⇄ 150× | 0.0230 | 23 | 183 | 71.5% |
| 5% ⇄ 200× | 0.0217 | 23 | 183 | 71.5% |
| 5% ⇄ 300× | 0.0202 | 23 | 183 | 71.5% |
| 5% ⇄ 400× | 0.0192 | 23 | 183 | 71.5% |
| 5% ⇄ 500× | 0.0185 | 22 | 182 | 71.1% |
| 5% ⇄ 750× | 0.0174 | 22 | 182 | 71.1% |
| 5% ⇄ 1000× | 0.0167 | 21 | 181 | 70.7% |
| 5% ⇄ 1500× | 0.0157 | 20 | 180 | 70.3% |
| 5% ⇄ 2000× | 0.0151 | 20 | 180 | 70.3% |
| 5% ⇄ 2500× | 0.0147 | 20 | 180 | 70.3% |
| 5% ⇄ 3000× | 0.0144 | 20 | 180 | 70.3% |
| 5% ⇄ 4000× | 0.0139 | 20 | 180 | 70.3% |
| 5% ⇄ 5000× | 0.0135 | 20 | 180 | 70.3% |

---


## Per famiglia di circuiti

**WISQ timeout** = WISQ non ha completato. **MapFail** = il nostro mapping non riesce. Win/=/Loss sono sugli steps dove entrambi completano.

| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | MapFail | Note |
|--------|---|-----|----------------|------|--------------|---------|------|
| 19qubits | 2 | 0 | 0 (0 noi+veloci) | 2 | 0 | 0 | n=19 |
| 53qubits | 2 | 0 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=27–39 |
| adder | 4 | 0 | 1 (1 noi+veloci) | 2 | 1 | 0 | n=4–433 |
| bigadder | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=18 |
| bv | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=153 |
| bwt | 4 | 0 | 0 (0 noi+veloci) | 1 | 3 | 0 | n=21–73 |
| cat | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| dnn | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=16 |
| factor247 | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=15 |
| fredkin | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=3 |
| ghz | 18 | 0 | 18 (18 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| ghz_state | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=23–255 |
| graphstate | 17 | 15 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| grover | 3 | 0 | 0 (0 noi+veloci) | 0 | 3 | 0 | n=5–20 |
| hhl | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=10 |
| ising | 19 | 18 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5–420 |
| multiplier | 11 | 3 | 0 (0 noi+veloci) | 2 | 6 | 0 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 2 | 2 (2 noi+veloci) | 14 | 2 | 0 | n=5–400 |
| qec_en | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=5 |
| qft | 22 | 0 | 1 (1 noi+veloci) | 20 | 1 | 0 | n=5–400 |
| qpe | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=9 |
| qram | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=9 |
| randomcircuit | 3 | 0 | 0 (0 noi+veloci) | 1 | 2 | 0 | n=50–200 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| square_root | 2 | 2 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=14–32 |
| synth | 37 | 0 | 0 (0 noi+veloci) | 21 | 16 | 0 | n=50–200 |
| t_test | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=8 |
| toffoli | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=3 |
| vqe_real_amp | 17 | 2 | 9 (9 noi+veloci) | 6 | 0 | 0 | n=5–400 |
| vqe_su2 | 17 | 0 | 11 (11 noi+veloci) | 6 | 0 | 0 | n=5–400 |
| vqe_two_local | 17 | 1 | 0 (0 noi+veloci) | 13 | 3 | 0 | n=5–400 |
| vqe_uccsd | 2 | 1 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=4–8 |
| wstate | 18 | 0 | 14 (14 noi+veloci) | 4 | 0 | 0 | n=5–400 |

---


## Per circuito (dettaglio)

**Steps**: WIN = noi meno routing steps, LOSS = WISQ meno, = pareggio. **Tempo** confronta le durate quando disponibili.

| # | Circuit | Qubits | Grid | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 7×7 | 108 | 101 | 0.9352 | success | LOSS | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 7×7 | 291 | 286 | 0.9828 | success | LOSS | noi +veloci |
| 3 | 53qubits_155gate_57layers | 27 | 7×8 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 4 | 53qubits_332gate_152layers | 39 | 10×10 | 44 | 41 | 0.9318 | success | LOSS | noi +veloci |
| 5 | adder_n28 | 28 | 8×8 | 24 | 24 | 1.0000 | success | = | noi +veloci |
| 6 | adder_n4 | 4 | 4×5 | 9 | — | — | failed | timeout | noi +veloci |
| 7 | adder_n433 | 433 | 29×30 | 311 | 250 | 0.8039 | success | LOSS | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 13×13 | 187 | 181 | 0.9679 | success | LOSS | noi +veloci |
| 9 | bigadder_n18_transpiled | 18 | 7×7 | 89 | 88 | 0.9888 | success | LOSS | noi +veloci |
| 10 | bv_n280 | 153 | 19×19 | 152 | 152 | 1.0000 | success | = | noi +veloci |
| 11 | bwt_n21 | 21 | 7×8 | 117200 | — | — | failed | timeout | noi +veloci |
| 12 | bwt_n37 | 28 | 8×9 | 36006 | 33603 | 0.9333 | success | LOSS | noi +veloci |
| 13 | bwt_n57 | 43 | 10×11 | 66355 | — | — | failed | timeout | noi +veloci |
| 14 | bwt_n97 | 73 | 13×14 | 132627 | — | — | failed | timeout | noi +veloci |
| 15 | cat_n130 | 130 | 16×17 | 129 | 129 | 1.0000 | success | = | noi +veloci |
| 16 | cat_n260 | 260 | 22×22 | 259 | 259 | 1.0000 | success | = | noi +veloci |
| 17 | continuous_3_17_13 | 3 | 2×2 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 18 | dnn_n16 | 16 | 5×5 | 48 | 77 | 1.6042 | success | **WIN** | noi +veloci |
| 19 | factor247_n15 | 15 | 7×7 | 371090 | — | — | failed | timeout | noi +veloci |
| 20 | fredkin_n3 | 3 | 3×4 | 10 | — | — | failed | timeout | noi +veloci |
| 21 | ghz_n10 | 10 | 4×5 | 9 | 9 | 1.0000 | success | = | noi +veloci |
| 22 | ghz_n100 | 100 | 14×15 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 23 | ghz_n125 | 125 | 16×16 | 124 | 124 | 1.0000 | success | = | noi +veloci |
| 24 | ghz_n150 | 150 | 17×18 | 149 | 149 | 1.0000 | success | = | noi +veloci |
| 25 | ghz_n175 | 175 | 18×19 | 174 | 174 | 1.0000 | success | = | noi +veloci |
| 26 | ghz_n20 | 20 | 7×7 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 27 | ghz_n200 | 200 | 21×21 | 199 | 199 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n255 | 255 | 22×22 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 29 | ghz_n30 | 30 | 8×9 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 30 | ghz_n300 | 300 | 24×25 | 299 | 299 | 1.0000 | success | = | noi +veloci |
| 31 | ghz_n40 | 40 | 9×10 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n400 | 400 | 27×28 | 399 | 399 | 1.0000 | success | = | noi +veloci |
| 33 | ghz_n5 | 5 | 3×3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 34 | ghz_n50 | 50 | 10×10 | 49 | 49 | 1.0000 | success | = | noi +veloci |
| 35 | ghz_n60 | 60 | 10×11 | 59 | 59 | 1.0000 | success | = | noi +veloci |
| 36 | ghz_n70 | 70 | 12×13 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 37 | ghz_n80 | 80 | 13×14 | 79 | 79 | 1.0000 | success | = | noi +veloci |
| 38 | ghz_n90 | 90 | 13×14 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 39 | ghz_state_n23 | 23 | 7×8 | 22 | 22 | 1.0000 | success | = | noi +veloci |
| 40 | ghz_state_n255 | 255 | 22×22 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 41 | graphstate_n10 | 10 | 5×5 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 42 | graphstate_n100 | 100 | 15×15 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 43 | graphstate_n125 | 125 | 16×17 | 6 | 10 | 1.6667 | success | **WIN** | noi +veloci |
| 44 | graphstate_n150 | 150 | 18×19 | 6 | 11 | 1.8333 | success | **WIN** | noi +veloci |
| 45 | graphstate_n175 | 175 | 20×21 | 10 | 12 | 1.2000 | success | **WIN** | noi +veloci |
| 46 | graphstate_n20 | 20 | 6×7 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 47 | graphstate_n200 | 200 | 20×21 | 11 | 14 | 1.2727 | success | **WIN** | noi +veloci |
| 48 | graphstate_n30 | 30 | 8×9 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 49 | graphstate_n300 | 300 | 25×26 | 13 | 18 | 1.3846 | success | **WIN** | noi +veloci |
| 50 | graphstate_n40 | 40 | 9×10 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 51 | graphstate_n400 | 400 | 29×29 | 13 | 24 | 1.8462 | success | **WIN** | noi +veloci |
| 52 | graphstate_n5 | 5 | 3×3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 53 | graphstate_n50 | 50 | 10×11 | 5 | 8 | 1.6000 | success | **WIN** | noi +veloci |
| 54 | graphstate_n60 | 60 | 11×12 | 6 | 7 | 1.1667 | success | **WIN** | noi +veloci |
| 55 | graphstate_n70 | 70 | 13×13 | 6 | 8 | 1.3333 | success | **WIN** | noi +veloci |
| 56 | graphstate_n80 | 80 | 13×13 | 6 | 9 | 1.5000 | success | **WIN** | noi +veloci |
| 57 | graphstate_n90 | 90 | 14×15 | 6 | 8 | 1.3333 | success | **WIN** | noi +veloci |
| 58 | grover_n10 | 10 | 5×6 | 11365 | — | — | failed | timeout | noi +veloci |
| 59 | grover_n20 | 20 | 7×8 | 2224867 | — | — | failed | timeout | noi +veloci |
| 60 | grover_n5 | 5 | 4×5 | 209 | — | — | failed | timeout | noi +veloci |
| 61 | hhl_n10 | 10 | 5×6 | 72042 | 72103 | 1.0008 | success | **WIN** | noi +veloci |
| 62 | ising_n10 | 10 | 4×5 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 63 | ising_n100 | 100 | 14×15 | 8 | 15 | 1.8750 | success | **WIN** | noi +veloci |
| 64 | ising_n125 | 125 | 16×16 | 6 | 19 | 3.1667 | success | **WIN** | noi +veloci |
| 65 | ising_n150 | 150 | 17×18 | 8 | 21 | 2.6250 | success | **WIN** | noi +veloci |
| 66 | ising_n175 | 175 | 18×19 | 10 | 23 | 2.3000 | success | **WIN** | noi +veloci |
| 67 | ising_n20 | 20 | 7×7 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 68 | ising_n200 | 200 | 21×21 | 10 | 30 | 3.0000 | success | **WIN** | noi +veloci |
| 69 | ising_n26 | 26 | 8×8 | 4 | 7 | 1.7500 | success | **WIN** | noi +veloci |
| 70 | ising_n30 | 30 | 8×9 | 4 | 9 | 2.2500 | success | **WIN** | noi +veloci |
| 71 | ising_n300 | 300 | 24×25 | 14 | 38 | 2.7143 | success | **WIN** | noi +veloci |
| 72 | ising_n40 | 40 | 9×10 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 73 | ising_n400 | 400 | 27×28 | 15 | 52 | 3.4667 | success | **WIN** | noi +veloci |
| 74 | ising_n420 | 420 | 29×29 | 10 | 50 | 5.0000 | success | **WIN** | noi +veloci |
| 75 | ising_n5 | 5 | 3×3 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 76 | ising_n50 | 50 | 10×10 | 4 | 11 | 2.7500 | success | **WIN** | noi +veloci |
| 77 | ising_n60 | 60 | 10×11 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 78 | ising_n70 | 70 | 12×13 | 4 | 14 | 3.5000 | success | **WIN** | noi +veloci |
| 79 | ising_n80 | 80 | 13×14 | 4 | 14 | 3.5000 | success | **WIN** | noi +veloci |
| 80 | ising_n90 | 90 | 13×14 | 4 | 16 | 4.0000 | success | **WIN** | noi +veloci |
| 81 | multiplier_n100 | 100 | 17×17 | 113356 | — | — | failed | timeout | noi +veloci |
| 82 | multiplier_n15 | 9 | 3×4 | 12 | 14 | 1.1667 | success | **WIN** | noi +veloci |
| 83 | multiplier_n20 | 20 | 7×8 | 4036 | 4017 | 0.9953 | success | LOSS | noi +veloci |
| 84 | multiplier_n200 | 200 | 23×23 | 457205 | — | — | failed | timeout | noi +veloci |
| 85 | multiplier_n300 | 300 | 28×28 | 1030664 | — | — | failed | timeout | noi +veloci |
| 86 | multiplier_n40 | 40 | 11×11 | 17500 | 17340 | 0.9909 | success | LOSS | noi +veloci |
| 87 | multiplier_n400 | 400 | 32×33 | 1831051 | — | — | failed | timeout | noi +veloci |
| 88 | multiplier_n45 | 27 | 6×6 | 36 | 37 | 1.0278 | success | **WIN** | noi +veloci |
| 89 | multiplier_n60 | 60 | 12×13 | 40719 | — | — | failed | timeout | noi +veloci |
| 90 | multiplier_n75 | 45 | 9×9 | 60 | 61 | 1.0167 | success | **WIN** | noi +veloci |
| 91 | multiplier_n80 | 80 | 15×15 | 73535 | — | — | failed | timeout | noi +veloci |
| 92 | multiply_n13 | 6 | 3×3 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 93 | parallel | 8 | 3×4 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 94 | parallel_big | 20 | 7×7 | 8 | 13 | 1.6250 | success | **WIN** | noi +veloci |
| 95 | qaoa_n10 | 10 | 5×6 | 48 | 50 | 1.0417 | success | **WIN** | noi +veloci |
| 96 | qaoa_n100 | 100 | 15×16 | 5106 | 1160 | 0.2272 | success | LOSS | noi +veloci |
| 97 | qaoa_n125 | 125 | 17×18 | 9412 | 1556 | 0.1653 | success | LOSS | noi +veloci |
| 98 | qaoa_n150 | 150 | 19×19 | 12679 | 2132 | 0.1682 | success | LOSS | noi +veloci |
| 99 | qaoa_n175 | 175 | 20×21 | 13272 | 2785 | 0.2098 | success | LOSS | noi +veloci |
| 100 | qaoa_n20 | 20 | 7×8 | 188 | 110 | 0.5851 | success | LOSS | noi +veloci |
| 101 | qaoa_n200 | 200 | 22×22 | 16993 | 3476 | 0.2046 | success | LOSS | noi +veloci |
| 102 | qaoa_n30 | 30 | 9×9 | 383 | 176 | 0.4595 | success | LOSS | noi +veloci |
| 103 | qaoa_n300 | 300 | 26×27 | 54584 | — | — | failed | timeout | noi +veloci |
| 104 | qaoa_n40 | 40 | 10×10 | 740 | 259 | 0.3500 | success | LOSS | noi +veloci |
| 105 | qaoa_n400 | 400 | 31×31 | 62384 | — | — | failed | timeout | noi +veloci |
| 106 | qaoa_n5 | 5 | 3×4 | 14 | 19 | 1.3571 | success | **WIN** | noi +veloci |
| 107 | qaoa_n50 | 50 | 11×12 | 1084 | 354 | 0.3266 | success | LOSS | noi +veloci |
| 108 | qaoa_n6 | 6 | 4×4 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 109 | qaoa_n60 | 60 | 12×12 | 1627 | 512 | 0.3147 | success | LOSS | noi +veloci |
| 110 | qaoa_n64 | 64 | 12×13 | 2137 | 583 | 0.2728 | success | LOSS | noi +veloci |
| 111 | qaoa_n6_transpiled | 6 | 4×4 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 112 | qaoa_n70 | 70 | 13×13 | 2592 | 618 | 0.2384 | success | LOSS | noi +veloci |
| 113 | qaoa_n80 | 80 | 14×14 | 3350 | 784 | 0.2340 | success | LOSS | noi +veloci |
| 114 | qaoa_n90 | 90 | 15×15 | 2967 | 949 | 0.3199 | success | LOSS | noi +veloci |
| 115 | qec_en_n5 | 5 | 3×4 | 11 | — | — | failed | timeout | noi +veloci |
| 116 | qft_20 | 20 | 7×7 | 228 | 113 | 0.4956 | success | LOSS | noi +veloci |
| 117 | qft_n10 | 10 | 5×5 | 52 | 43 | 0.8269 | success | LOSS | noi +veloci |
| 118 | qft_n100 | 100 | 15×15 | 2244 | 583 | 0.2598 | success | LOSS | noi +veloci |
| 119 | qft_n125 | 125 | 16×16 | 2635 | 654 | 0.2482 | success | LOSS | noi +veloci |
| 120 | qft_n128 | 128 | 16×16 | 2730 | 642 | 0.2352 | success | LOSS | noi +veloci |
| 121 | qft_n150 | 150 | 17×18 | 3340 | 752 | 0.2251 | success | LOSS | noi +veloci |
| 122 | qft_n175 | 175 | 18×19 | 4354 | 845 | 0.1941 | success | LOSS | noi +veloci |
| 123 | qft_n18 | 18 | 6×7 | 173 | 96 | 0.5549 | success | LOSS | noi +veloci |
| 124 | qft_n20 | 20 | 7×7 | 224 | 112 | 0.5000 | success | LOSS | noi +veloci |
| 125 | qft_n200 | 200 | 20×20 | 4423 | 943 | 0.2132 | success | LOSS | noi +veloci |
| 126 | qft_n30 | 30 | 9×9 | 312 | 186 | 0.5962 | success | LOSS | noi +veloci |
| 127 | qft_n300 | 300 | 24×24 | 8090 | 1390 | 0.1718 | success | LOSS | noi +veloci |
| 128 | qft_n320 | 320 | 28×28 | 50178 | — | — | failed | timeout | noi +veloci |
| 129 | qft_n40 | 40 | 10×10 | 606 | 246 | 0.4059 | success | LOSS | noi +veloci |
| 130 | qft_n400 | 400 | 27×28 | 10551 | 1851 | 0.1754 | success | LOSS | noi +veloci |
| 131 | qft_n5 | 5 | 3×4 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 132 | qft_n50 | 50 | 11×11 | 820 | 294 | 0.3585 | success | LOSS | noi +veloci |
| 133 | qft_n60 | 60 | 12×12 | 1190 | 382 | 0.3210 | success | LOSS | noi +veloci |
| 134 | qft_n64 | 64 | 12×13 | 1293 | 402 | 0.3109 | success | LOSS | noi +veloci |
| 135 | qft_n70 | 70 | 13×13 | 1357 | 394 | 0.2903 | success | LOSS | noi +veloci |
| 136 | qft_n80 | 80 | 14×14 | 1669 | 492 | 0.2948 | success | LOSS | noi +veloci |
| 137 | qft_n90 | 90 | 14×15 | 1984 | 497 | 0.2505 | success | LOSS | noi +veloci |
| 138 | qpe_n9_transpiled | 9 | 5×5 | 42 | 42 | 1.0000 | success | = | noi +veloci |
| 139 | qram_n20 | 9 | 4×5 | 10 | 9 | 0.9000 | success | LOSS | noi +veloci |
| 140 | randomcircuit_n100 | 100 | 17×17 | 22506 | — | — | failed | timeout | noi +veloci |
| 141 | randomcircuit_n200 | 200 | 22×23 | 106912 | — | — | failed | timeout | noi +veloci |
| 142 | randomcircuit_n50 | 50 | 11×12 | 6664 | 2288 | 0.3433 | success | LOSS | noi +veloci |
| 143 | seca_n11 | 11 | 5×5 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 144 | simon_n6 | 3 | 2×2 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 145 | square_root_n18 | 14 | 4×5 | 27 | 31 | 1.1481 | success | **WIN** | noi +veloci |
| 146 | square_root_n45 | 32 | 7×8 | 570 | 591 | 1.0368 | success | **WIN** | noi +veloci |
| 147 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 16×16 | 1317 | — | — | failed | timeout | noi +veloci |
| 148 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 16×17 | 1195 | — | — | failed | timeout | noi +veloci |
| 149 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 16×17 | 1206 | — | — | failed | timeout | noi +veloci |
| 150 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 17×17 | 1193 | — | — | failed | timeout | noi +veloci |
| 151 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 16×16 | 1206 | — | — | failed | timeout | noi +veloci |
| 152 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 16×17 | 1224 | — | — | failed | timeout | noi +veloci |
| 153 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 16×17 | 2468 | — | — | failed | timeout | noi +veloci |
| 154 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 16×16 | 2616 | 516 | 0.1972 | success | LOSS | noi +veloci |
| 155 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 16×16 | 2507 | — | — | failed | timeout | noi +veloci |
| 156 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 16×16 | 2520 | — | — | failed | timeout | noi +veloci |
| 157 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 16×17 | 2298 | — | — | failed | timeout | noi +veloci |
| 158 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 16×16 | 2537 | — | — | failed | timeout | noi +veloci |
| 159 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 22×23 | 5450 | 585 | 0.1073 | success | LOSS | noi +veloci |
| 160 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 22×23 | 5163 | 484 | 0.0937 | success | LOSS | noi +veloci |
| 161 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 23×23 | 5286 | 752 | 0.1423 | success | LOSS | noi +veloci |
| 162 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 23×23 | 5371 | 741 | 0.1380 | success | LOSS | noi +veloci |
| 163 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 22×23 | 5415 | 928 | 0.1714 | success | LOSS | noi +veloci |
| 164 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 23×23 | 5289 | 835 | 0.1579 | success | LOSS | noi +veloci |
| 165 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 22×23 | 11418 | 1567 | 0.1372 | success | LOSS | noi +veloci |
| 166 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 22×23 | 10185 | 1639 | 0.1609 | success | LOSS | noi +veloci |
| 167 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 22×23 | 11433 | 1743 | 0.1525 | success | LOSS | noi +veloci |
| 168 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 23×23 | 10030 | 1499 | 0.1495 | success | LOSS | noi +veloci |
| 169 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 23×23 | 10511 | 1653 | 0.1573 | success | LOSS | noi +veloci |
| 170 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 22×23 | 10191 | 1976 | 0.1939 | success | LOSS | noi +veloci |
| 171 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 11×11 | 359 | — | — | failed | timeout | noi +veloci |
| 172 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 11×12 | 298 | 71 | 0.2383 | success | LOSS | noi +veloci |
| 173 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 11×11 | 328 | 93 | 0.2835 | success | LOSS | noi +veloci |
| 174 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 12×12 | 276 | — | — | failed | timeout | noi +veloci |
| 175 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 11×12 | 282 | — | — | failed | timeout | noi +veloci |
| 176 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 11×12 | 347 | — | — | failed | timeout | noi +veloci |
| 177 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 12×12 | 390 | — | — | failed | timeout | noi +veloci |
| 178 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 11×12 | 620 | 168 | 0.2710 | success | LOSS | noi +veloci |
| 179 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 11×12 | 629 | 178 | 0.2830 | success | LOSS | noi +veloci |
| 180 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 11×12 | 679 | 188 | 0.2769 | success | LOSS | noi +veloci |
| 181 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 11×12 | 614 | 179 | 0.2915 | success | LOSS | noi +veloci |
| 182 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 11×12 | 624 | 185 | 0.2965 | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 11×12 | 633 | 186 | 0.2938 | success | LOSS | noi +veloci |
| 184 | t_test | 8 | 4×4 | 110 | 150 | 1.3636 | success | **WIN** | noi +veloci |
| 185 | toffoli_n3 | 3 | 3×4 | 11 | — | — | failed | timeout | noi +veloci |
| 186 | vqe_real_amp_n10 | 10 | 4×5 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 187 | vqe_real_amp_n100 | 100 | 14×15 | 105 | 103 | 0.9810 | success | LOSS | noi +veloci |
| 188 | vqe_real_amp_n125 | 125 | 16×16 | 128 | 129 | 1.0078 | success | **WIN** | noi +veloci |
| 189 | vqe_real_amp_n150 | 150 | 17×18 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 190 | vqe_real_amp_n175 | 175 | 18×19 | 180 | 178 | 0.9889 | success | LOSS | noi +veloci |
| 191 | vqe_real_amp_n20 | 20 | 7×7 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 192 | vqe_real_amp_n200 | 200 | 21×21 | 204 | 203 | 0.9951 | success | LOSS | noi +veloci |
| 193 | vqe_real_amp_n30 | 30 | 8×9 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 194 | vqe_real_amp_n300 | 300 | 24×25 | 306 | 303 | 0.9902 | success | LOSS | noi +veloci |
| 195 | vqe_real_amp_n40 | 40 | 9×10 | 45 | 43 | 0.9556 | success | LOSS | noi +veloci |
| 196 | vqe_real_amp_n400 | 400 | 27×28 | 405 | 403 | 0.9951 | success | LOSS | noi +veloci |
| 197 | vqe_real_amp_n5 | 5 | 3×3 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 198 | vqe_real_amp_n50 | 50 | 10×10 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 199 | vqe_real_amp_n60 | 60 | 10×11 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 200 | vqe_real_amp_n70 | 70 | 12×13 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 201 | vqe_real_amp_n80 | 80 | 13×14 | 83 | 84 | 1.0120 | success | **WIN** | noi +veloci |
| 202 | vqe_real_amp_n90 | 90 | 13×14 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 203 | vqe_su2_n10 | 10 | 4×5 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 204 | vqe_su2_n100 | 100 | 14×15 | 105 | 103 | 0.9810 | success | LOSS | noi +veloci |
| 205 | vqe_su2_n125 | 125 | 16×16 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 206 | vqe_su2_n150 | 150 | 17×18 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 207 | vqe_su2_n175 | 175 | 18×19 | 180 | 178 | 0.9889 | success | LOSS | noi +veloci |
| 208 | vqe_su2_n20 | 20 | 7×7 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 209 | vqe_su2_n200 | 200 | 21×21 | 204 | 203 | 0.9951 | success | LOSS | noi +veloci |
| 210 | vqe_su2_n30 | 30 | 8×9 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 211 | vqe_su2_n300 | 300 | 24×25 | 306 | 303 | 0.9902 | success | LOSS | noi +veloci |
| 212 | vqe_su2_n40 | 40 | 9×10 | 45 | 43 | 0.9556 | success | LOSS | noi +veloci |
| 213 | vqe_su2_n400 | 400 | 27×28 | 405 | 403 | 0.9951 | success | LOSS | noi +veloci |
| 214 | vqe_su2_n5 | 5 | 3×3 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 215 | vqe_su2_n50 | 50 | 10×10 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 216 | vqe_su2_n60 | 60 | 10×11 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 217 | vqe_su2_n70 | 70 | 12×13 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 218 | vqe_su2_n80 | 80 | 13×14 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 219 | vqe_su2_n90 | 90 | 13×14 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 220 | vqe_two_local_n10 | 10 | 5×5 | 70 | 52 | 0.7429 | success | LOSS | noi +veloci |
| 221 | vqe_two_local_n100 | 100 | 16×16 | 5169 | 1925 | 0.3724 | success | LOSS | noi +veloci |
| 222 | vqe_two_local_n125 | 125 | 17×18 | 8568 | 2529 | 0.2952 | success | LOSS | noi +veloci |
| 223 | vqe_two_local_n150 | 150 | 19×19 | 12942 | 3379 | 0.2611 | success | LOSS | noi +veloci |
| 224 | vqe_two_local_n175 | 175 | 20×21 | 17529 | 4386 | 0.2502 | success | LOSS | noi +veloci |
| 225 | vqe_two_local_n20 | 20 | 7×7 | 326 | 148 | 0.4540 | success | LOSS | noi +veloci |
| 226 | vqe_two_local_n200 | 200 | 22×22 | 27450 | — | — | failed | timeout | noi +veloci |
| 227 | vqe_two_local_n30 | 30 | 9×9 | 447 | 265 | 0.5928 | success | LOSS | noi +veloci |
| 228 | vqe_two_local_n300 | 300 | 27×27 | 61161 | — | — | failed | timeout | noi +veloci |
| 229 | vqe_two_local_n40 | 40 | 10×10 | 874 | 411 | 0.4703 | success | LOSS | noi +veloci |
| 230 | vqe_two_local_n400 | 400 | 31×31 | 93182 | — | — | failed | timeout | noi +veloci |
| 231 | vqe_two_local_n5 | 5 | 3×4 | 17 | 20 | 1.1765 | success | **WIN** | noi +veloci |
| 232 | vqe_two_local_n50 | 50 | 11×11 | 1914 | 558 | 0.2915 | success | LOSS | noi +veloci |
| 233 | vqe_two_local_n60 | 60 | 12×13 | 1982 | 829 | 0.4183 | success | LOSS | noi +veloci |
| 234 | vqe_two_local_n70 | 70 | 13×13 | 2851 | 975 | 0.3420 | success | LOSS | noi +veloci |
| 235 | vqe_two_local_n80 | 80 | 14×14 | 3785 | 1318 | 0.3482 | success | LOSS | noi +veloci |
| 236 | vqe_two_local_n90 | 90 | 15×15 | 5451 | 1489 | 0.2732 | success | LOSS | noi +veloci |
| 237 | vqe_uccsd_n4 | 4 | 2×3 | 87 | 88 | 1.0115 | success | **WIN** | noi +veloci |
| 238 | vqe_uccsd_n8 | 8 | 4×5 | 5452 | 5446 | 0.9989 | success | LOSS | noi +veloci |
| 239 | wstate_n10 | 10 | 4×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 240 | wstate_n100 | 100 | 14×15 | 102 | 101 | 0.9902 | success | LOSS | noi +veloci |
| 241 | wstate_n125 | 125 | 16×16 | 126 | 126 | 1.0000 | success | = | noi +veloci |
| 242 | wstate_n150 | 150 | 17×18 | 151 | 151 | 1.0000 | success | = | noi +veloci |
| 243 | wstate_n175 | 175 | 18×19 | 176 | 176 | 1.0000 | success | = | noi +veloci |
| 244 | wstate_n20 | 20 | 7×7 | 21 | 21 | 1.0000 | success | = | noi +veloci |
| 245 | wstate_n200 | 200 | 21×21 | 201 | 201 | 1.0000 | success | = | noi +veloci |
| 246 | wstate_n27 | 27 | 8×8 | 28 | 28 | 1.0000 | success | = | noi +veloci |
| 247 | wstate_n30 | 30 | 8×9 | 31 | 31 | 1.0000 | success | = | noi +veloci |
| 248 | wstate_n300 | 300 | 24×25 | 303 | 301 | 0.9934 | success | LOSS | noi +veloci |
| 249 | wstate_n40 | 40 | 9×10 | 42 | 41 | 0.9762 | success | LOSS | noi +veloci |
| 250 | wstate_n400 | 400 | 27×28 | 402 | 401 | 0.9975 | success | LOSS | noi +veloci |
| 251 | wstate_n5 | 5 | 3×3 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 252 | wstate_n50 | 50 | 10×10 | 51 | 51 | 1.0000 | success | = | noi +veloci |
| 253 | wstate_n60 | 60 | 10×11 | 61 | 61 | 1.0000 | success | = | noi +veloci |
| 254 | wstate_n70 | 70 | 12×13 | 71 | 71 | 1.0000 | success | = | noi +veloci |
| 255 | wstate_n80 | 80 | 13×14 | 81 | 81 | 1.0000 | success | = | noi +veloci |
| 256 | wstate_n90 | 90 | 13×14 | 91 | 91 | 1.0000 | success | = | noi +veloci |
