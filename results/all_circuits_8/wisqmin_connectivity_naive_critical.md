# wisqmin — connectivity + naive_critical (config FISSA)


Nostro compiler forzato sulla griglia MINIMA di WISQ (s*), config fissa a priori: safe_passage=connectivity, routing=naive_critical. Confronto same-grid.


Dati da: `connectivity_naive_critical_wisqmin.csv` — **257 circuiti**.


---


## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 257 | — |
| ↳ WISQ va in timeout (noi vinciamo) | 16 | — |
| ↳ Entrambi completano | 241 | — |
|   ↳ Noi vinciamo su steps | 59 (ratio mediana 1.50×) | 58 (98.3%) |
|   ↳ Pareggio su steps | 100 | 98 (98.0%) |
|   ↳ WISQ vince su steps | 82 (ratio mediana 0.78×) | 81 (98.8%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **173 / 257 (67.3%)** | — |
| ↳ Noi completiamo, WISQ va in timeout | 16 / 257 (6.2%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 59 / 257 (23.0%) | — |
| ↳ Pareggio su steps, noi più veloci | 98 / 257 (38.1%) | — |

---


## Routing steps in aggregato (nostro vs WISQ)

Sui 241 circuiti dove **entrambi completano**:

| Metrica | Valore |
|---------|--------|
| Somma `my_routing_steps` | 360.909 |
| Somma `wisq_routing_steps` | 314.968 |
| **Rapporto dei totali (wisq / nostro)** | **0.87 → WISQ usa 12.7% di steps in meno** |
| Mediana di `ratio_wisq_over_mine` | 1.00 |
| Media di `ratio_wisq_over_mine` | 1.268 |

---


## Densità dei circuiti: dove vinciamo vs dove perdiamo

`cnot_interaction_density` = coppie-qubit CNOT distinte / coppie possibili `Q·(Q−1)/2` (0 = sparso/locale, 1 = ogni coppia interagisce). Calcolata dal QASM universale su 240/241 circuiti both-complete con QASM disponibile.

**Per esito sugli steps:**

| Esito (steps) | N | densità media | mediana | min | max |
|---|---|---|---|---|---|
| **Vinciamo** (WIN) | 59 | 0.321 | 0.051 | 0.005 | 1.000 |
| Pareggio (TIE) | 100 | 0.171 | 0.036 | 0.005 | 1.000 |
| **Perdiamo** (LOSS) | 81 | 0.428 | 0.400 | 0.098 | 1.000 |

**Win/Loss per fascia di densità** (sugli steps, both-complete):

| Densità `cid` | N | Win | Tie | Loss | Loss-rate (decisi) |
|---|---|---|---|---|---|
| < 0.15 | 112 | 37 | 73 | 2 | 5.1% |
| 0.15 – 0.40 | 38 | 3 | 8 | 27 | 90.0% |
| ≥ 0.40 | 90 | 19 | 19 | 52 | 73.2% |

---


## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 257 | — |
| **WISQ non finisce in 1 ora** | 54 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 54 | — |
| **Entrambi finiscono in 1 ora** | 203 | — |
| ↳ Noi vinciamo su steps | 55 (ratio mediana 1.60×) | 54 (98.2%) |
| ↳ Pareggio su steps | 96 | 94 (97.9%) |
| ↳ WISQ vince su steps | 52 (ratio mediana 0.80×) | 51 (98.1%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **203 / 257 (79.0%)** | — |

---


## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 257 | — |
| **WISQ non finisce in 30 minuti** | 64 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 64 | — |
| **Entrambi finiscono in 30 minuti** | 193 | — |
| ↳ Noi vinciamo su steps | 55 (ratio mediana 1.60×) | 54 (98.2%) |
| ↳ Pareggio su steps | 95 | 93 (97.9%) |
| ↳ WISQ vince su steps | 43 (ratio mediana 0.85×) | 42 (97.7%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **212 / 257 (82.5%)** | — |

---


## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 257 | — |
| **WISQ non finisce in 15 minuti** | 80 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 80 | — |
| **Entrambi finiscono in 15 minuti** | 177 | — |
| ↳ Noi vinciamo su steps | 53 (ratio mediana 1.67×) | 52 (98.1%) |
| ↳ Pareggio su steps | 92 | 90 (97.8%) |
| ↳ WISQ vince su steps | 32 (ratio mediana 0.86×) | 31 (96.9%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **223 / 257 (86.8%)** | — |

---


## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 257 | — |
| **WISQ non finisce in 10 minuti** | 85 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 2 | — |
| ↳ …noi finiamo → **vittoria** | 83 | — |
| **Entrambi finiscono in 10 minuti** | 172 | — |
| ↳ Noi vinciamo su steps | 52 (ratio mediana 1.69×) | 51 (98.1%) |
| ↳ Pareggio su steps | 90 | 88 (97.8%) |
| ↳ WISQ vince su steps | 30 (ratio mediana 0.87×) | 29 (96.7%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **223 / 257 (86.8%)** | — |

---


## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 257 | — |
| **WISQ non finisce in 5 minuti** | 99 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 3 | — |
| ↳ …noi finiamo → **vittoria** | 96 | — |
| **Entrambi finiscono in 5 minuti** | 158 | — |
| ↳ Noi vinciamo su steps | 50 (ratio mediana 1.73×) | 49 (98.0%) |
| ↳ Pareggio su steps | 89 | 87 (97.8%) |
| ↳ WISQ vince su steps | 19 (ratio mediana 0.86×) | 18 (94.7%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **233 / 257 (90.7%)** | — |

---


## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 257 | — |
| **WISQ non finisce in 1 minuto** | 128 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 10 | — |
| ↳ …noi finiamo → **vittoria** | 118 | — |
| **Noi non finiamo, WISQ sì → sconfitta** | 1 | — |
| **Entrambi finiscono in 1 minuto** | 128 | — |
| ↳ Noi vinciamo su steps | 44 (ratio mediana 1.79×) | 43 (97.7%) |
| ↳ Pareggio su steps | 75 | 74 (98.7%) |
| ↳ WISQ vince su steps | 9 (ratio mediana 0.86×) | 8 (88.9%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **236 / 257 (91.8%)** | — |

---


## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (orig., asimm.) | 241 | 16 | 0 | 0 | **173 (67.3%)** |
| 1 ora | 203 | 54 | 0 | 0 | **203 (79.0%)** |
| 30 minuti | 193 | 64 | 0 | 0 | **212 (82.5%)** |
| 15 minuti | 177 | 80 | 0 | 0 | **223 (86.8%)** |
| 10 minuti | 172 | 83 | 0 | 2 | **223 (86.8%)** |
| 5 minuti | 158 | 96 | 0 | 3 | **233 (90.7%)** |
| 1 minuto | 128 | 118 | 1 | 10 | **236 (91.8%)** ⟵ picco |

---


## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s`. Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). I timeout WISQ sono inclusi con la durata registrata.

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 257 | 252 (98.1%) | 611× | 1518× | 0.11× | 75572× |
| ↳ Dove vinciamo su steps | 59 | 58 (98.3%) | 419× | 2576× | 0.29× | 75572× |
| ↳ In pareggio su steps | 100 | 98 (98.0%) | 599× | 1186× | 0.11× | 19685× |
| ↳ Dove WISQ vince su steps | 82 | 81 (98.8%) | 770× | 1116× | 0.24× | 5969× |
| ↳ WISQ in timeout | 16 | 15 (93.8%) | 140× | 1750× | 0.63× | 8126× |

---


## Buffer di steps dipendente dalla velocità — win-rate vs WISQ

Analisi su `connectivity_naive_critical_wisqmin.csv`. La metrica primaria sono i **routing steps**, il tempo è secondario: concediamo un buffer ε sugli steps che cresce con l'ordine di grandezza del vantaggio di tempo.

```
vinco  se   my_steps <= wisq_steps · (1 + ε)
ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time
α = 0.05 / log10(N)      (ancora: 5% di sforo steps ⇄ N× di velocità)
```

Baseline (steps primario, tempo solo spareggio) = **173/257 = 67.3%**.

| ancora | α | loss recuperati | vittorie | % |
|---|---:|---:|---:|---:|
| 5% ⇄ 20× | 0.0384 | 15 | 188 | 73.2% |
| 5% ⇄ 50× | 0.0294 | 10 | 183 | 71.2% |
| 5% ⇄ 100× | 0.0250 | 10 | 183 | 71.2% |
| 5% ⇄ 150× | 0.0230 | 10 | 183 | 71.2% |
| 5% ⇄ 200× | 0.0217 | 9 | 182 | 70.8% |
| 5% ⇄ 300× | 0.0202 | 9 | 182 | 70.8% |
| 5% ⇄ 400× | 0.0192 | 8 | 181 | 70.4% |
| 5% ⇄ 500× | 0.0185 | 8 | 181 | 70.4% |
| 5% ⇄ 750× | 0.0174 | 8 | 181 | 70.4% |
| 5% ⇄ 1000× | 0.0167 | 7 | 180 | 70.0% |
| 5% ⇄ 1500× | 0.0157 | 7 | 180 | 70.0% |
| 5% ⇄ 2000× | 0.0151 | 6 | 179 | 69.6% |
| 5% ⇄ 2500× | 0.0147 | 6 | 179 | 69.6% |
| 5% ⇄ 3000× | 0.0144 | 6 | 179 | 69.6% |
| 5% ⇄ 4000× | 0.0139 | 6 | 179 | 69.6% |
| 5% ⇄ 5000× | 0.0135 | 6 | 179 | 69.6% |

---


## Per famiglia di circuiti

**WISQ timeout** = WISQ non ha completato. **MapFail** = il nostro mapping non riesce. Win/=/Loss sono sugli steps dove entrambi completano.

| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | MapFail | Note |
|--------|---|-----|----------------|------|--------------|---------|------|
| 19qubits | 2 | 0 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=19 |
| 53qubits | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=27–39 |
| adder | 4 | 1 | 3 (3 noi+veloci) | 0 | 0 | 0 | n=4–433 |
| bigadder | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=18 |
| bv | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=153 |
| bwt | 5 | 0 | 0 (0 noi+veloci) | 0 | 5 | 0 | n=21–133 |
| cat | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| dnn | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=16 |
| factor247 | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=15 |
| fredkin | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| ghz | 18 | 0 | 18 (17 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| ghz_state | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=23–255 |
| graphstate | 17 | 14 | 3 (2 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| grover | 3 | 2 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=5–19 |
| hhl | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=10 |
| ising | 19 | 17 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=5–420 |
| multiplier | 11 | 1 | 5 (5 noi+veloci) | 1 | 4 | 0 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 1 | 2 (2 noi+veloci) | 16 | 1 | 0 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5 |
| qft | 22 | 6 | 1 (1 noi+veloci) | 14 | 1 | 0 | n=5–400 |
| qpe | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=9 |
| qram | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=9 |
| randomcircuit | 3 | 0 | 0 (0 noi+veloci) | 2 | 1 | 0 | n=50–200 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| square_root | 2 | 1 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=14–32 |
| synth | 37 | 0 | 0 (0 noi+veloci) | 37 | 0 | 0 | n=50–200 |
| t_test | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=8 |
| toffoli | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| vqe_real_amp | 17 | 1 | 15 (15 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_su2 | 17 | 2 | 14 (14 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_two_local | 17 | 8 | 1 (1 noi+veloci) | 6 | 2 | 0 | n=5–400 |
| vqe_uccsd | 2 | 1 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=4–8 |
| wstate | 18 | 0 | 17 (17 noi+veloci) | 1 | 0 | 0 | n=5–400 |

---


## Per circuito (dettaglio)

**Steps**: WIN = noi meno routing steps, LOSS = WISQ meno, = pareggio. **Tempo** confronta le durate quando disponibili.

| # | Circuit | Qubits | Grid | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 9×9 | 102 | 100 | 0.9804 | success | LOSS | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 9×9 | 286 | 286 | 1.0000 | success | = | noi +veloci |
| 3 | 53qubits_155gate_57layers | 27 | 11×11 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 4 | 53qubits_332gate_152layers | 39 | 17×17 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 11×11 | 24 | 24 | 1.0000 | success | = | noi +veloci |
| 6 | adder_n4 | 4 | 7×7 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 7 | adder_n433 | 433 | 41×41 | 249 | 251 | 1.0080 | success | **WIN** | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 15×15 | 181 | 181 | 1.0000 | success | = | noi +veloci |
| 9 | bigadder_n18_transpiled | 18 | 13×13 | 88 | 88 | 1.0000 | success | = | noi +veloci |
| 10 | bv_n280 | 153 | 33×33 | 152 | 152 | 1.0000 | success | = | noi +veloci |
| 11 | bwt_n177 | 133 | 27×27 | 257663 | — | — | failed | timeout | noi +veloci |
| 12 | bwt_n21 | 21 | 13×13 | 116400 | — | — | failed | timeout | noi +veloci |
| 13 | bwt_n37 | 28 | 15×15 | 33600 | — | — | failed | timeout | noi +veloci |
| 14 | bwt_n57 | 43 | 17×17 | 65606 | — | — | failed | timeout | noi +veloci |
| 15 | bwt_n97 | 73 | 21×21 | 129600 | — | — | failed | timeout | noi +veloci |
| 16 | cat_n130 | 130 | 23×23 | 129 | 129 | 1.0000 | success | = | noi +veloci |
| 17 | cat_n260 | 260 | 33×33 | 259 | 259 | 1.0000 | success | = | noi +veloci |
| 18 | continuous_3_17_13 | 3 | 3×3 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 19 | dnn_n16 | 16 | 7×7 | 48 | 82 | 1.7083 | success | **WIN** | noi +veloci |
| 20 | factor247_n15 | 15 | 11×11 | 349644 | — | — | failed | timeout | noi +veloci |
| 21 | fredkin_n3 | 3 | 6×6 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 22 | ghz_n10 | 10 | 7×7 | 9 | 9 | 1.0000 | success | = | noi +veloci |
| 23 | ghz_n100 | 100 | 19×19 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 24 | ghz_n125 | 125 | 23×23 | 124 | 124 | 1.0000 | success | = | noi +veloci |
| 25 | ghz_n150 | 150 | 25×25 | 149 | 149 | 1.0000 | success | = | noi +veloci |
| 26 | ghz_n175 | 175 | 27×27 | 174 | 174 | 1.0000 | success | = | noi +veloci |
| 27 | ghz_n20 | 20 | 9×9 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n200 | 200 | 29×29 | 199 | 199 | 1.0000 | success | = | noi +veloci |
| 29 | ghz_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 30 | ghz_n30 | 30 | 11×11 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 31 | ghz_n300 | 300 | 35×35 | 299 | 299 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n40 | 40 | 13×13 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 33 | ghz_n400 | 400 | 39×39 | 399 | 399 | 1.0000 | success | = | noi +veloci |
| 34 | ghz_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 35 | ghz_n50 | 50 | 15×15 | 49 | 49 | 1.0000 | success | = | WISQ +veloce |
| 36 | ghz_n60 | 60 | 15×15 | 59 | 59 | 1.0000 | success | = | noi +veloci |
| 37 | ghz_n70 | 70 | 17×17 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 38 | ghz_n80 | 80 | 17×17 | 79 | 79 | 1.0000 | success | = | noi +veloci |
| 39 | ghz_n90 | 90 | 19×19 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 40 | ghz_state_n23 | 23 | 9×9 | 22 | 22 | 1.0000 | success | = | noi +veloci |
| 41 | ghz_state_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 42 | graphstate_n10 | 10 | 7×7 | 4 | 4 | 1.0000 | success | = | WISQ +veloce |
| 43 | graphstate_n100 | 100 | 19×19 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 44 | graphstate_n125 | 125 | 23×23 | 5 | 12 | 2.4000 | success | **WIN** | noi +veloci |
| 45 | graphstate_n150 | 150 | 25×25 | 6 | 11 | 1.8333 | success | **WIN** | noi +veloci |
| 46 | graphstate_n175 | 175 | 27×27 | 7 | 13 | 1.8571 | success | **WIN** | noi +veloci |
| 47 | graphstate_n20 | 20 | 9×9 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 48 | graphstate_n200 | 200 | 29×29 | 6 | 13 | 2.1667 | success | **WIN** | noi +veloci |
| 49 | graphstate_n30 | 30 | 11×11 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 50 | graphstate_n300 | 300 | 35×35 | 9 | 20 | 2.2222 | success | **WIN** | noi +veloci |
| 51 | graphstate_n40 | 40 | 13×13 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 52 | graphstate_n400 | 400 | 39×39 | 7 | 23 | 3.2857 | success | **WIN** | noi +veloci |
| 53 | graphstate_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 54 | graphstate_n50 | 50 | 15×15 | 5 | 7 | 1.4000 | success | **WIN** | noi +veloci |
| 55 | graphstate_n60 | 60 | 15×15 | 5 | 7 | 1.4000 | success | **WIN** | noi +veloci |
| 56 | graphstate_n70 | 70 | 17×17 | 5 | 8 | 1.6000 | success | **WIN** | noi +veloci |
| 57 | graphstate_n80 | 80 | 17×17 | 6 | 10 | 1.6667 | success | **WIN** | noi +veloci |
| 58 | graphstate_n90 | 90 | 19×19 | 5 | 10 | 2.0000 | success | **WIN** | noi +veloci |
| 59 | grover_n10 | 10 | 8×8 | 11008 | 11017 | 1.0008 | success | **WIN** | noi +veloci |
| 60 | grover_n20 | 19 | 13×13 | 2146489 | — | — | failed | timeout | WISQ +veloce |
| 61 | grover_n5 | 5 | 6×6 | 209 | 211 | 1.0096 | success | **WIN** | noi +veloci |
| 62 | hhl_n10 | 10 | 11×11 | 72039 | 72039 | 1.0000 | success | = | noi +veloci |
| 63 | ising_n10 | 10 | 7×7 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 64 | ising_n100 | 100 | 19×19 | 4 | 19 | 4.7500 | success | **WIN** | noi +veloci |
| 65 | ising_n125 | 125 | 23×23 | 4 | 22 | 5.5000 | success | **WIN** | noi +veloci |
| 66 | ising_n150 | 150 | 25×25 | 4 | 21 | 5.2500 | success | **WIN** | noi +veloci |
| 67 | ising_n175 | 175 | 27×27 | 4 | 25 | 6.2500 | success | **WIN** | noi +veloci |
| 68 | ising_n20 | 20 | 9×9 | 4 | 8 | 2.0000 | success | **WIN** | WISQ +veloce |
| 69 | ising_n200 | 200 | 29×29 | 4 | 27 | 6.7500 | success | **WIN** | noi +veloci |
| 70 | ising_n26 | 26 | 11×11 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 71 | ising_n30 | 30 | 11×11 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 72 | ising_n300 | 300 | 35×35 | 4 | 37 | 9.2500 | success | **WIN** | noi +veloci |
| 73 | ising_n40 | 40 | 13×13 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 74 | ising_n400 | 400 | 39×39 | 4 | 47 | 11.7500 | success | **WIN** | noi +veloci |
| 75 | ising_n420 | 420 | 41×41 | 4 | 50 | 12.5000 | success | **WIN** | noi +veloci |
| 76 | ising_n5 | 5 | 5×5 | 6 | 4 | 0.6667 | success | LOSS | noi +veloci |
| 77 | ising_n50 | 50 | 15×15 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 78 | ising_n60 | 60 | 15×15 | 4 | 11 | 2.7500 | success | **WIN** | noi +veloci |
| 79 | ising_n70 | 70 | 17×17 | 4 | 14 | 3.5000 | success | **WIN** | noi +veloci |
| 80 | ising_n80 | 80 | 17×17 | 4 | 14 | 3.5000 | success | **WIN** | noi +veloci |
| 81 | ising_n90 | 90 | 19×19 | 4 | 16 | 4.0000 | success | **WIN** | noi +veloci |
| 82 | multiplier_n100 | 100 | 23×23 | 111762 | — | — | failed | timeout | noi +veloci |
| 83 | multiplier_n15 | 9 | 5×5 | 13 | 12 | 0.9231 | success | LOSS | noi +veloci |
| 84 | multiplier_n20 | 20 | 11×11 | 3990 | 3993 | 1.0008 | success | **WIN** | noi +veloci |
| 85 | multiplier_n200 | 200 | 33×33 | 450021 | — | — | failed | timeout | noi +veloci |
| 86 | multiplier_n300 | 300 | 39×39 | 1013834 | — | — | failed | timeout | noi +veloci |
| 87 | multiplier_n40 | 40 | 17×17 | 17329 | 17329 | 1.0000 | success | = | noi +veloci |
| 88 | multiplier_n400 | 400 | 43×43 | 1812187 | — | — | failed | timeout | noi +veloci |
| 89 | multiplier_n45 | 27 | 13×13 | 36 | 36 | 1.0000 | success | = | noi +veloci |
| 90 | multiplier_n60 | 60 | 19×19 | 39730 | 39730 | 1.0000 | success | = | noi +veloci |
| 91 | multiplier_n75 | 45 | 17×17 | 60 | 60 | 1.0000 | success | = | noi +veloci |
| 92 | multiplier_n80 | 80 | 21×21 | 71287 | 71287 | 1.0000 | success | = | noi +veloci |
| 93 | multiply_n13 | 6 | 5×5 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 94 | parallel | 8 | 5×5 | 10 | 13 | 1.3000 | success | **WIN** | noi +veloci |
| 95 | parallel_big | 20 | 9×9 | 8 | 14 | 1.7500 | success | **WIN** | noi +veloci |
| 96 | qaoa_n10 | 10 | 7×7 | 46 | 48 | 1.0435 | success | **WIN** | noi +veloci |
| 97 | qaoa_n100 | 100 | 19×19 | 1691 | 1167 | 0.6901 | success | LOSS | noi +veloci |
| 98 | qaoa_n125 | 125 | 23×23 | 2071 | 1649 | 0.7962 | success | LOSS | noi +veloci |
| 99 | qaoa_n150 | 150 | 25×25 | 2754 | 2173 | 0.7890 | success | LOSS | noi +veloci |
| 100 | qaoa_n175 | 175 | 27×27 | 3602 | 2812 | 0.7807 | success | LOSS | noi +veloci |
| 101 | qaoa_n20 | 20 | 9×9 | 109 | 109 | 1.0000 | success | = | noi +veloci |
| 102 | qaoa_n200 | 200 | 29×29 | 4537 | 3591 | 0.7915 | success | LOSS | noi +veloci |
| 103 | qaoa_n30 | 30 | 11×11 | 191 | 181 | 0.9476 | success | LOSS | noi +veloci |
| 104 | qaoa_n300 | 300 | 35×35 | 8960 | 7173 | 0.8006 | success | LOSS | noi +veloci |
| 105 | qaoa_n40 | 40 | 13×13 | 310 | 276 | 0.8903 | success | LOSS | noi +veloci |
| 106 | qaoa_n400 | 400 | 43×43 | 13750 | — | — | failed | timeout | noi +veloci |
| 107 | qaoa_n5 | 5 | 5×5 | 18 | 14 | 0.7778 | success | LOSS | noi +veloci |
| 108 | qaoa_n50 | 50 | 15×15 | 451 | 371 | 0.8226 | success | LOSS | noi +veloci |
| 109 | qaoa_n6 | 6 | 5×5 | 36 | 36 | 1.0000 | success | = | noi +veloci |
| 110 | qaoa_n60 | 60 | 15×15 | 715 | 511 | 0.7147 | success | LOSS | noi +veloci |
| 111 | qaoa_n64 | 64 | 15×15 | 895 | 582 | 0.6503 | success | LOSS | noi +veloci |
| 112 | qaoa_n6_transpiled | 6 | 5×5 | 36 | 33 | 0.9167 | success | LOSS | WISQ +veloce |
| 113 | qaoa_n70 | 70 | 17×17 | 799 | 639 | 0.7997 | success | LOSS | noi +veloci |
| 114 | qaoa_n80 | 80 | 17×17 | 1108 | 790 | 0.7130 | success | LOSS | noi +veloci |
| 115 | qaoa_n90 | 90 | 19×19 | 1229 | 958 | 0.7795 | success | LOSS | noi +veloci |
| 116 | qec_en_n5 | 5 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 117 | qft_20 | 20 | 9×9 | 103 | 113 | 1.0971 | success | **WIN** | noi +veloci |
| 118 | qft_n10 | 10 | 7×7 | 37 | 45 | 1.2162 | success | **WIN** | noi +veloci |
| 119 | qft_n100 | 100 | 19×19 | 767 | 591 | 0.7705 | success | LOSS | noi +veloci |
| 120 | qft_n125 | 125 | 23×23 | 2639 | 672 | 0.2546 | success | LOSS | noi +veloci |
| 121 | qft_n128 | 128 | 23×23 | 2708 | 697 | 0.2574 | success | LOSS | noi +veloci |
| 122 | qft_n150 | 150 | 25×25 | 3150 | 782 | 0.2483 | success | LOSS | noi +veloci |
| 123 | qft_n175 | 175 | 27×27 | 3774 | 898 | 0.2379 | success | LOSS | noi +veloci |
| 124 | qft_n18 | 18 | 9×9 | 78 | 100 | 1.2821 | success | **WIN** | noi +veloci |
| 125 | qft_n20 | 20 | 9×9 | 102 | 110 | 1.0784 | success | **WIN** | noi +veloci |
| 126 | qft_n200 | 200 | 29×29 | 4295 | 982 | 0.2286 | success | LOSS | noi +veloci |
| 127 | qft_n30 | 30 | 11×11 | 178 | 192 | 1.0787 | success | **WIN** | noi +veloci |
| 128 | qft_n300 | 300 | 35×35 | 6557 | 1389 | 0.2118 | success | LOSS | noi +veloci |
| 129 | qft_n320 | 320 | 39×39 | 8346 | — | — | failed | timeout | noi +veloci |
| 130 | qft_n40 | 40 | 13×13 | 277 | 244 | 0.8809 | success | LOSS | noi +veloci |
| 131 | qft_n400 | 400 | 39×39 | 9181 | 1869 | 0.2036 | success | LOSS | noi +veloci |
| 132 | qft_n5 | 5 | 5×5 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 133 | qft_n50 | 50 | 15×15 | 285 | 308 | 1.0807 | success | **WIN** | noi +veloci |
| 134 | qft_n60 | 60 | 15×15 | 414 | 368 | 0.8889 | success | LOSS | noi +veloci |
| 135 | qft_n64 | 64 | 15×15 | 479 | 407 | 0.8497 | success | LOSS | noi +veloci |
| 136 | qft_n70 | 70 | 17×17 | 438 | 424 | 0.9680 | success | LOSS | noi +veloci |
| 137 | qft_n80 | 80 | 17×17 | 562 | 473 | 0.8416 | success | LOSS | noi +veloci |
| 138 | qft_n90 | 90 | 19×19 | 598 | 528 | 0.8829 | success | LOSS | noi +veloci |
| 139 | qpe_n9_transpiled | 9 | 5×5 | 42 | 42 | 1.0000 | success | = | noi +veloci |
| 140 | qram_n20 | 9 | 5×5 | 8 | 9 | 1.1250 | success | **WIN** | noi +veloci |
| 141 | randomcircuit_n100 | 100 | 22×22 | 6063 | 4911 | 0.8100 | success | LOSS | noi +veloci |
| 142 | randomcircuit_n200 | 200 | 33×33 | 17552 | — | — | failed | timeout | noi +veloci |
| 143 | randomcircuit_n50 | 50 | 19×19 | 1632 | 1445 | 0.8854 | success | LOSS | noi +veloci |
| 144 | seca_n11 | 11 | 7×7 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 145 | simon_n6 | 3 | 3×3 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 146 | square_root_n18 | 14 | 7×7 | 27 | 27 | 1.0000 | success | = | noi +veloci |
| 147 | square_root_n45 | 32 | 11×11 | 570 | 571 | 1.0018 | success | **WIN** | noi +veloci |
| 148 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 288 | 167 | 0.5799 | success | LOSS | noi +veloci |
| 149 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 421 | 168 | 0.3990 | success | LOSS | noi +veloci |
| 150 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 328 | 217 | 0.6616 | success | LOSS | noi +veloci |
| 151 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 22×22 | 306 | 215 | 0.7026 | success | LOSS | noi +veloci |
| 152 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 327 | 232 | 0.7095 | success | LOSS | noi +veloci |
| 153 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 22×22 | 319 | 235 | 0.7367 | success | LOSS | noi +veloci |
| 154 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 617 | 430 | 0.6969 | success | LOSS | noi +veloci |
| 155 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 624 | 449 | 0.7196 | success | LOSS | noi +veloci |
| 156 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 640 | 460 | 0.7188 | success | LOSS | noi +veloci |
| 157 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 644 | 455 | 0.7065 | success | LOSS | noi +veloci |
| 158 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 665 | 519 | 0.7805 | success | LOSS | noi +veloci |
| 159 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 654 | 498 | 0.7615 | success | LOSS | noi +veloci |
| 160 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 817 | 367 | 0.4492 | success | LOSS | noi +veloci |
| 161 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 32×32 | 880 | 424 | 0.4818 | success | LOSS | noi +veloci |
| 162 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 926 | 601 | 0.6490 | success | LOSS | noi +veloci |
| 163 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 877 | 607 | 0.6921 | success | LOSS | noi +veloci |
| 164 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 31×31 | 1626 | 700 | 0.4305 | success | LOSS | noi +veloci |
| 165 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 949 | 670 | 0.7060 | success | LOSS | noi +veloci |
| 166 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 2023 | 1284 | 0.6347 | success | LOSS | noi +veloci |
| 167 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 29×29 | 2430 | 1288 | 0.5300 | success | LOSS | noi +veloci |
| 168 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 2029 | 1429 | 0.7043 | success | LOSS | noi +veloci |
| 169 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 30×30 | 2067 | 1336 | 0.6463 | success | LOSS | noi +veloci |
| 170 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 5597 | 1577 | 0.2818 | success | LOSS | noi +veloci |
| 171 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 29×29 | 2298 | 1574 | 0.6849 | success | LOSS | noi +veloci |
| 172 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 77 | 61 | 0.7922 | success | LOSS | noi +veloci |
| 173 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 18×18 | 70 | 60 | 0.8571 | success | LOSS | noi +veloci |
| 174 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 81 | 70 | 0.8642 | success | LOSS | noi +veloci |
| 175 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 84 | 75 | 0.8929 | success | LOSS | noi +veloci |
| 176 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 87 | 68 | 0.7816 | success | LOSS | noi +veloci |
| 177 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 81 | 71 | 0.8765 | success | LOSS | noi +veloci |
| 178 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 123 | 108 | 0.8780 | success | LOSS | noi +veloci |
| 179 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 156 | 133 | 0.8526 | success | LOSS | noi +veloci |
| 180 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 155 | 139 | 0.8968 | success | LOSS | noi +veloci |
| 181 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 18×18 | 166 | 162 | 0.9759 | success | LOSS | noi +veloci |
| 182 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 169 | 151 | 0.8935 | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 159 | 148 | 0.9308 | success | LOSS | noi +veloci |
| 184 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 155 | 146 | 0.9419 | success | LOSS | noi +veloci |
| 185 | t_test | 8 | 5×5 | 140 | 110 | 0.7857 | success | LOSS | noi +veloci |
| 186 | toffoli_n3 | 3 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 187 | vqe_real_amp_n10 | 10 | 7×7 | 13 | 15 | 1.1538 | success | **WIN** | noi +veloci |
| 188 | vqe_real_amp_n100 | 100 | 19×19 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 189 | vqe_real_amp_n125 | 125 | 23×23 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 190 | vqe_real_amp_n150 | 150 | 25×25 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 191 | vqe_real_amp_n175 | 175 | 27×27 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 192 | vqe_real_amp_n20 | 20 | 9×9 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 193 | vqe_real_amp_n200 | 200 | 29×29 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 194 | vqe_real_amp_n30 | 30 | 11×11 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 195 | vqe_real_amp_n300 | 300 | 35×35 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 196 | vqe_real_amp_n40 | 40 | 13×13 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 197 | vqe_real_amp_n400 | 400 | 39×39 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 198 | vqe_real_amp_n5 | 5 | 5×5 | 10 | 8 | 0.8000 | success | LOSS | noi +veloci |
| 199 | vqe_real_amp_n50 | 50 | 15×15 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 200 | vqe_real_amp_n60 | 60 | 15×15 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 201 | vqe_real_amp_n70 | 70 | 17×17 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 202 | vqe_real_amp_n80 | 80 | 17×17 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 203 | vqe_real_amp_n90 | 90 | 19×19 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 204 | vqe_su2_n10 | 10 | 7×7 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 205 | vqe_su2_n100 | 100 | 19×19 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 206 | vqe_su2_n125 | 125 | 23×23 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 207 | vqe_su2_n150 | 150 | 25×25 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 208 | vqe_su2_n175 | 175 | 27×27 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 209 | vqe_su2_n20 | 20 | 9×9 | 23 | 25 | 1.0870 | success | **WIN** | noi +veloci |
| 210 | vqe_su2_n200 | 200 | 29×29 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 211 | vqe_su2_n30 | 30 | 11×11 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 212 | vqe_su2_n300 | 300 | 35×35 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 213 | vqe_su2_n40 | 40 | 13×13 | 43 | 45 | 1.0465 | success | **WIN** | noi +veloci |
| 214 | vqe_su2_n400 | 400 | 39×39 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 215 | vqe_su2_n5 | 5 | 5×5 | 10 | 8 | 0.8000 | success | LOSS | noi +veloci |
| 216 | vqe_su2_n50 | 50 | 15×15 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 217 | vqe_su2_n60 | 60 | 15×15 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 218 | vqe_su2_n70 | 70 | 17×17 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 219 | vqe_su2_n80 | 80 | 17×17 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 220 | vqe_su2_n90 | 90 | 19×19 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 221 | vqe_two_local_n10 | 10 | 7×7 | 45 | 55 | 1.2222 | success | **WIN** | noi +veloci |
| 222 | vqe_two_local_n100 | 100 | 19×19 | 2174 | 1891 | 0.8698 | success | LOSS | noi +veloci |
| 223 | vqe_two_local_n125 | 125 | 23×23 | 2555 | 2600 | 1.0176 | success | **WIN** | noi +veloci |
| 224 | vqe_two_local_n150 | 150 | 25×25 | 3497 | 3568 | 1.0203 | success | **WIN** | noi +veloci |
| 225 | vqe_two_local_n175 | 175 | 27×27 | 4611 | 4556 | 0.9881 | success | LOSS | noi +veloci |
| 226 | vqe_two_local_n20 | 20 | 9×9 | 129 | 157 | 1.2171 | success | **WIN** | noi +veloci |
| 227 | vqe_two_local_n200 | 200 | 29×29 | 5706 | 5626 | 0.9860 | success | LOSS | noi +veloci |
| 228 | vqe_two_local_n30 | 30 | 11×11 | 260 | 272 | 1.0462 | success | **WIN** | noi +veloci |
| 229 | vqe_two_local_n300 | 300 | 39×39 | 10420 | — | — | failed | timeout | noi +veloci |
| 230 | vqe_two_local_n40 | 40 | 13×13 | 385 | 413 | 1.0727 | success | **WIN** | noi +veloci |
| 231 | vqe_two_local_n400 | 400 | 43×43 | 17089 | — | — | failed | timeout | noi +veloci |
| 232 | vqe_two_local_n5 | 5 | 5×5 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 233 | vqe_two_local_n50 | 50 | 15×15 | 541 | 576 | 1.0647 | success | **WIN** | noi +veloci |
| 234 | vqe_two_local_n60 | 60 | 15×15 | 1011 | 805 | 0.7962 | success | LOSS | noi +veloci |
| 235 | vqe_two_local_n70 | 70 | 17×17 | 1007 | 1011 | 1.0040 | success | **WIN** | noi +veloci |
| 236 | vqe_two_local_n80 | 80 | 17×17 | 1420 | 1349 | 0.9500 | success | LOSS | noi +veloci |
| 237 | vqe_two_local_n90 | 90 | 19×19 | 1587 | 1558 | 0.9817 | success | LOSS | noi +veloci |
| 238 | vqe_uccsd_n4 | 4 | 3×3 | 87 | 88 | 1.0115 | success | **WIN** | noi +veloci |
| 239 | vqe_uccsd_n8 | 8 | 5×5 | 5446 | 5446 | 1.0000 | success | = | noi +veloci |
| 240 | wstate_n10 | 10 | 7×7 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 241 | wstate_n100 | 100 | 19×19 | 101 | 101 | 1.0000 | success | = | noi +veloci |
| 242 | wstate_n125 | 125 | 23×23 | 126 | 126 | 1.0000 | success | = | noi +veloci |
| 243 | wstate_n150 | 150 | 25×25 | 151 | 151 | 1.0000 | success | = | noi +veloci |
| 244 | wstate_n175 | 175 | 27×27 | 176 | 176 | 1.0000 | success | = | noi +veloci |
| 245 | wstate_n20 | 20 | 9×9 | 21 | 21 | 1.0000 | success | = | noi +veloci |
| 246 | wstate_n200 | 200 | 29×29 | 201 | 201 | 1.0000 | success | = | noi +veloci |
| 247 | wstate_n27 | 27 | 11×11 | 28 | 28 | 1.0000 | success | = | noi +veloci |
| 248 | wstate_n30 | 30 | 11×11 | 31 | 31 | 1.0000 | success | = | noi +veloci |
| 249 | wstate_n300 | 300 | 35×35 | 301 | 301 | 1.0000 | success | = | noi +veloci |
| 250 | wstate_n40 | 40 | 13×13 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 251 | wstate_n400 | 400 | 39×39 | 401 | 401 | 1.0000 | success | = | noi +veloci |
| 252 | wstate_n5 | 5 | 5×5 | 7 | 6 | 0.8571 | success | LOSS | noi +veloci |
| 253 | wstate_n50 | 50 | 15×15 | 51 | 51 | 1.0000 | success | = | noi +veloci |
| 254 | wstate_n60 | 60 | 15×15 | 61 | 61 | 1.0000 | success | = | noi +veloci |
| 255 | wstate_n70 | 70 | 17×17 | 71 | 71 | 1.0000 | success | = | noi +veloci |
| 256 | wstate_n80 | 80 | 17×17 | 81 | 81 | 1.0000 | success | = | noi +veloci |
| 257 | wstate_n90 | 90 | 19×19 | 91 | 91 | 1.0000 | success | = | noi +veloci |
