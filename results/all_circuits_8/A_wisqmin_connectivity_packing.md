# wisqmin — connectivity + packing (config FISSA, same-grid)


FAIR. Config scelta a priori: safe_passage=connectivity, routing=packing. Entrambi i compiler sulla STESSA griglia: s* = la griglia MINIMA su cui WISQ riesce a instradare. Confronto same-grid sugli step. 256 circuiti (esclusi randomcircuit_n400 e bwt_n177).


Dati da: `wisqmin_connectivity_packing.csv` — **256 circuiti**.


---


## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| ↳ WISQ va in timeout (noi vinciamo) | 15 | — |
| ↳ Entrambi completano | 241 | — |
|   ↳ Noi vinciamo su steps | 65 (ratio mediana 1.30×) | 65 (100.0%) |
|   ↳ Pareggio su steps | 100 | 99 (99.0%) |
|   ↳ WISQ vince su steps | 76 (ratio mediana 0.82×) | 76 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **179 / 256 (69.9%)** | — |
| ↳ Noi completiamo, WISQ va in timeout | 15 / 256 (5.9%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 65 / 256 (25.4%) | — |
| ↳ Pareggio su steps, noi più veloci | 99 / 256 (38.7%) | — |

---


## Routing steps in aggregato (nostro vs WISQ)

Sui 241 circuiti dove **entrambi completano**:

| Metrica | Valore |
|---------|--------|
| Somma `my_routing_steps` | 353.683 |
| Somma `wisq_routing_steps` | 314.968 |
| **Rapporto dei totali (wisq / nostro)** | **0.89 → WISQ usa 10.9% di steps in meno** |
| Mediana di `ratio_wisq_over_mine` | 1.00 |
| Media di `ratio_wisq_over_mine` | 1.284 |

---


## Densità dei circuiti: dove vinciamo vs dove perdiamo

`cnot_interaction_density` = coppie-qubit CNOT distinte / coppie possibili `Q·(Q−1)/2` (0 = sparso/locale, 1 = ogni coppia interagisce). Calcolata dal QASM universale su 240/241 circuiti both-complete con QASM disponibile.

**Per esito sugli steps:**

| Esito (steps) | N | densità media | mediana | min | max |
|---|---|---|---|---|---|
| **Vinciamo** (WIN) | 65 | 0.359 | 0.100 | 0.005 | 1.000 |
| Pareggio (TIE) | 100 | 0.171 | 0.036 | 0.005 | 1.000 |
| **Perdiamo** (LOSS) | 75 | 0.404 | 0.400 | 0.098 | 1.000 |

**Win/Loss per fascia di densità** (sugli steps, both-complete):

| Densità `cid` | N | Win | Tie | Loss | Loss-rate (decisi) |
|---|---|---|---|---|---|
| < 0.15 | 112 | 37 | 73 | 2 | 5.1% |
| 0.15 – 0.40 | 38 | 3 | 8 | 27 | 90.0% |
| ≥ 0.40 | 90 | 25 | 19 | 46 | 64.8% |

---


## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 1 ora** | 53 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 2 | — |
| ↳ …noi finiamo → **vittoria** | 51 | — |
| **Entrambi finiscono in 1 ora** | 203 | — |
| ↳ Noi vinciamo su steps | 58 (ratio mediana 1.50×) | 58 (100.0%) |
| ↳ Pareggio su steps | 96 | 95 (99.0%) |
| ↳ WISQ vince su steps | 49 (ratio mediana 0.84×) | 49 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **204 / 256 (79.7%)** | — |

---


## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 30 minuti** | 63 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 5 | — |
| ↳ …noi finiamo → **vittoria** | 58 | — |
| **Entrambi finiscono in 30 minuti** | 193 | — |
| ↳ Noi vinciamo su steps | 58 (ratio mediana 1.50×) | 58 (100.0%) |
| ↳ Pareggio su steps | 95 | 94 (98.9%) |
| ↳ WISQ vince su steps | 40 (ratio mediana 0.86×) | 40 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **210 / 256 (82.0%)** | — |

---


## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 15 minuti** | 79 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 7 | — |
| ↳ …noi finiamo → **vittoria** | 72 | — |
| **Entrambi finiscono in 15 minuti** | 177 | — |
| ↳ Noi vinciamo su steps | 56 (ratio mediana 1.55×) | 56 (100.0%) |
| ↳ Pareggio su steps | 92 | 91 (98.9%) |
| ↳ WISQ vince su steps | 29 (ratio mediana 0.89×) | 29 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **219 / 256 (85.5%)** | — |

---


## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 10 minuti** | 84 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 7 | — |
| ↳ …noi finiamo → **vittoria** | 77 | — |
| **Entrambi finiscono in 10 minuti** | 172 | — |
| ↳ Noi vinciamo su steps | 55 (ratio mediana 1.60×) | 55 (100.0%) |
| ↳ Pareggio su steps | 90 | 89 (98.9%) |
| ↳ WISQ vince su steps | 27 (ratio mediana 0.90×) | 27 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **221 / 256 (86.3%)** | — |

---


## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 5 minuti** | 98 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 9 | — |
| ↳ …noi finiamo → **vittoria** | 89 | — |
| **Entrambi finiscono in 5 minuti** | 158 | — |
| ↳ Noi vinciamo su steps | 52 (ratio mediana 1.69×) | 52 (100.0%) |
| ↳ Pareggio su steps | 89 | 88 (98.9%) |
| ↳ WISQ vince su steps | 17 (ratio mediana 0.89×) | 17 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **229 / 256 (89.5%)** | — |

---


## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **WISQ non finisce in 1 minuto** | 127 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 27 | — |
| ↳ …noi finiamo → **vittoria** | 100 | — |
| **Entrambi finiscono in 1 minuto** | 129 | — |
| ↳ Noi vinciamo su steps | 45 (ratio mediana 1.75×) | 45 (100.0%) |
| ↳ Pareggio su steps | 75 | 74 (98.7%) |
| ↳ WISQ vince su steps | 9 (ratio mediana 0.86×) | 9 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **219 / 256 (85.5%)** | — |

---


## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (orig., asimm.) | 241 | 15 | 0 | 0 | **179 (69.9%)** |
| 1 ora | 203 | 51 | 0 | 2 | **204 (79.7%)** |
| 30 minuti | 193 | 58 | 0 | 5 | **210 (82.0%)** |
| 15 minuti | 177 | 72 | 0 | 7 | **219 (85.5%)** |
| 10 minuti | 172 | 77 | 0 | 7 | **221 (86.3%)** |
| 5 minuti | 158 | 89 | 0 | 9 | **229 (89.5%)** ⟵ picco |
| 1 minuto | 129 | 100 | 0 | 27 | **219 (85.5%)** |

---


## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s`. Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). I timeout WISQ sono inclusi con la durata registrata.

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 256 | 253 (98.8%) | 466× | 696× | 0.05× | 18536× |
| ↳ Dove vinciamo su steps | 65 | 65 (100.0%) | 383× | 1006× | 1.40× | 18536× |
| ↳ In pareggio su steps | 100 | 99 (99.0%) | 643× | 765× | 0.29× | 5255× |
| ↳ Dove WISQ vince su steps | 76 | 76 (100.0%) | 357× | 432× | 1.17× | 3409× |
| ↳ WISQ in timeout | 15 | 13 (86.7%) | 11× | 225× | 0.05× | 1483× |

---


## Buffer di steps dipendente dalla velocità — win-rate vs WISQ

Analisi su `wisqmin_connectivity_packing.csv`. La metrica primaria sono i **routing steps**, il tempo è secondario: concediamo un buffer ε sugli steps che cresce con l'ordine di grandezza del vantaggio di tempo.

```
vinco  se   my_steps <= wisq_steps · (1 + ε)
ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time
α = 0.05 / log10(N)      (ancora: 5% di sforo steps ⇄ N× di velocità)
```

Baseline (steps primario, tempo solo spareggio) = **179/256 = 69.9%**.

| ancora | α | loss recuperati | vittorie | % |
|---|---:|---:|---:|---:|
| 5% ⇄ 20× | 0.0384 | 19 | 198 | 77.3% |
| 5% ⇄ 50× | 0.0294 | 11 | 190 | 74.2% |
| 5% ⇄ 100× | 0.0250 | 6 | 185 | 72.3% |
| 5% ⇄ 150× | 0.0230 | 6 | 185 | 72.3% |
| 5% ⇄ 200× | 0.0217 | 6 | 185 | 72.3% |
| 5% ⇄ 300× | 0.0202 | 6 | 185 | 72.3% |
| 5% ⇄ 400× | 0.0192 | 5 | 184 | 71.9% |
| 5% ⇄ 500× | 0.0185 | 5 | 184 | 71.9% |
| 5% ⇄ 750× | 0.0174 | 5 | 184 | 71.9% |
| 5% ⇄ 1000× | 0.0167 | 4 | 183 | 71.5% |
| 5% ⇄ 1500× | 0.0157 | 4 | 183 | 71.5% |
| 5% ⇄ 2000× | 0.0151 | 3 | 182 | 71.1% |
| 5% ⇄ 2500× | 0.0147 | 3 | 182 | 71.1% |
| 5% ⇄ 3000× | 0.0144 | 3 | 182 | 71.1% |
| 5% ⇄ 4000× | 0.0139 | 3 | 182 | 71.1% |
| 5% ⇄ 5000× | 0.0135 | 3 | 182 | 71.1% |

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
| bwt | 4 | 0 | 0 (0 noi+veloci) | 0 | 4 | 0 | n=21–73 |
| cat | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=3 |
| dnn | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=16 |
| factor247 | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=15 |
| fredkin | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| ghz | 18 | 0 | 18 (18 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| ghz_state | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=23–255 |
| graphstate | 17 | 14 | 3 (3 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| grover | 3 | 2 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=5–19 |
| hhl | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=10 |
| ising | 19 | 17 | 1 (1 noi+veloci) | 1 | 0 | 0 | n=5–420 |
| multiplier | 11 | 1 | 5 (5 noi+veloci) | 1 | 4 | 0 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 3 | 2 (2 noi+veloci) | 14 | 1 | 0 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5 |
| qft | 22 | 6 | 1 (1 noi+veloci) | 14 | 1 | 0 | n=5–400 |
| qpe | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=9 |
| qram | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=9 |
| randomcircuit | 3 | 0 | 0 (0 noi+veloci) | 2 | 1 | 0 | n=50–200 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| square_root | 2 | 1 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=14–32 |
| synth | 37 | 1 | 0 (0 noi+veloci) | 36 | 0 | 0 | n=50–200 |
| t_test | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=8 |
| toffoli | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| vqe_real_amp | 17 | 1 | 15 (15 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_su2 | 17 | 2 | 14 (14 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_two_local | 17 | 11 | 1 (1 noi+veloci) | 3 | 2 | 0 | n=5–400 |
| vqe_uccsd | 2 | 1 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=4–8 |
| wstate | 18 | 0 | 17 (17 noi+veloci) | 1 | 0 | 0 | n=5–400 |

---


## Per circuito (dettaglio)

**Steps**: WIN = noi meno routing steps, LOSS = WISQ meno, = pareggio. **Tempo** confronta le durate quando disponibili.

| # | Circuit | Qubits | Grid | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 9×9 | 103 | 100 | 0.9709 | success | LOSS | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 9×9 | 286 | 286 | 1.0000 | success | = | noi +veloci |
| 3 | 53qubits_155gate_57layers | 27 | 11×11 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 4 | 53qubits_332gate_152layers | 39 | 17×17 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 11×11 | 24 | 24 | 1.0000 | success | = | noi +veloci |
| 6 | adder_n4 | 4 | 7×7 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 7 | adder_n433 | 433 | 41×41 | 250 | 251 | 1.0040 | success | **WIN** | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 15×15 | 181 | 181 | 1.0000 | success | = | noi +veloci |
| 9 | bigadder_n18_transpiled | 18 | 13×13 | 88 | 88 | 1.0000 | success | = | noi +veloci |
| 10 | bv_n280 | 153 | 33×33 | 152 | 152 | 1.0000 | success | = | noi +veloci |
| 11 | bwt_n21 | 21 | 13×13 | 116600 | — | — | failed | timeout | noi +veloci |
| 12 | bwt_n37 | 28 | 15×15 | 33600 | — | — | failed | timeout | noi +veloci |
| 13 | bwt_n57 | 43 | 17×17 | 65603 | — | — | failed | timeout | noi +veloci |
| 14 | bwt_n97 | 73 | 21×21 | 129600 | — | — | failed | timeout | noi +veloci |
| 15 | cat_n130 | 130 | 23×23 | 129 | 129 | 1.0000 | success | = | noi +veloci |
| 16 | cat_n260 | 260 | 33×33 | 259 | 259 | 1.0000 | success | = | noi +veloci |
| 17 | continuous_3_17_13 | 3 | 3×3 | 17 | 17 | 1.0000 | success | = | WISQ +veloce |
| 18 | dnn_n16 | 16 | 7×7 | 48 | 82 | 1.7083 | success | **WIN** | noi +veloci |
| 19 | factor247_n15 | 15 | 11×11 | 349644 | — | — | failed | timeout | noi +veloci |
| 20 | fredkin_n3 | 3 | 6×6 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 21 | ghz_n10 | 10 | 7×7 | 9 | 9 | 1.0000 | success | = | noi +veloci |
| 22 | ghz_n100 | 100 | 19×19 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 23 | ghz_n125 | 125 | 23×23 | 124 | 124 | 1.0000 | success | = | noi +veloci |
| 24 | ghz_n150 | 150 | 25×25 | 149 | 149 | 1.0000 | success | = | noi +veloci |
| 25 | ghz_n175 | 175 | 27×27 | 174 | 174 | 1.0000 | success | = | noi +veloci |
| 26 | ghz_n20 | 20 | 9×9 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 27 | ghz_n200 | 200 | 29×29 | 199 | 199 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 29 | ghz_n30 | 30 | 11×11 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 30 | ghz_n300 | 300 | 35×35 | 299 | 299 | 1.0000 | success | = | noi +veloci |
| 31 | ghz_n40 | 40 | 13×13 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n400 | 400 | 39×39 | 399 | 399 | 1.0000 | success | = | noi +veloci |
| 33 | ghz_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 34 | ghz_n50 | 50 | 15×15 | 49 | 49 | 1.0000 | success | = | noi +veloci |
| 35 | ghz_n60 | 60 | 15×15 | 59 | 59 | 1.0000 | success | = | noi +veloci |
| 36 | ghz_n70 | 70 | 17×17 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 37 | ghz_n80 | 80 | 17×17 | 79 | 79 | 1.0000 | success | = | noi +veloci |
| 38 | ghz_n90 | 90 | 19×19 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 39 | ghz_state_n23 | 23 | 9×9 | 22 | 22 | 1.0000 | success | = | noi +veloci |
| 40 | ghz_state_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 41 | graphstate_n10 | 10 | 7×7 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 42 | graphstate_n100 | 100 | 19×19 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 43 | graphstate_n125 | 125 | 23×23 | 5 | 12 | 2.4000 | success | **WIN** | noi +veloci |
| 44 | graphstate_n150 | 150 | 25×25 | 6 | 11 | 1.8333 | success | **WIN** | noi +veloci |
| 45 | graphstate_n175 | 175 | 27×27 | 7 | 13 | 1.8571 | success | **WIN** | noi +veloci |
| 46 | graphstate_n20 | 20 | 9×9 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 47 | graphstate_n200 | 200 | 29×29 | 6 | 13 | 2.1667 | success | **WIN** | noi +veloci |
| 48 | graphstate_n30 | 30 | 11×11 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 49 | graphstate_n300 | 300 | 35×35 | 9 | 20 | 2.2222 | success | **WIN** | noi +veloci |
| 50 | graphstate_n40 | 40 | 13×13 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 51 | graphstate_n400 | 400 | 39×39 | 7 | 23 | 3.2857 | success | **WIN** | noi +veloci |
| 52 | graphstate_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 53 | graphstate_n50 | 50 | 15×15 | 5 | 7 | 1.4000 | success | **WIN** | noi +veloci |
| 54 | graphstate_n60 | 60 | 15×15 | 5 | 7 | 1.4000 | success | **WIN** | noi +veloci |
| 55 | graphstate_n70 | 70 | 17×17 | 5 | 8 | 1.6000 | success | **WIN** | noi +veloci |
| 56 | graphstate_n80 | 80 | 17×17 | 6 | 10 | 1.6667 | success | **WIN** | noi +veloci |
| 57 | graphstate_n90 | 90 | 19×19 | 5 | 10 | 2.0000 | success | **WIN** | noi +veloci |
| 58 | grover_n10 | 10 | 8×8 | 11008 | 11017 | 1.0008 | success | **WIN** | noi +veloci |
| 59 | grover_n20 | 19 | 13×13 | 2146489 | — | — | failed | timeout | WISQ +veloce |
| 60 | grover_n5 | 5 | 6×6 | 209 | 211 | 1.0096 | success | **WIN** | noi +veloci |
| 61 | hhl_n10 | 10 | 11×11 | 72039 | 72039 | 1.0000 | success | = | noi +veloci |
| 62 | ising_n10 | 10 | 7×7 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 63 | ising_n100 | 100 | 19×19 | 4 | 19 | 4.7500 | success | **WIN** | noi +veloci |
| 64 | ising_n125 | 125 | 23×23 | 4 | 22 | 5.5000 | success | **WIN** | noi +veloci |
| 65 | ising_n150 | 150 | 25×25 | 4 | 21 | 5.2500 | success | **WIN** | noi +veloci |
| 66 | ising_n175 | 175 | 27×27 | 4 | 25 | 6.2500 | success | **WIN** | noi +veloci |
| 67 | ising_n20 | 20 | 9×9 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 68 | ising_n200 | 200 | 29×29 | 4 | 27 | 6.7500 | success | **WIN** | noi +veloci |
| 69 | ising_n26 | 26 | 11×11 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 70 | ising_n30 | 30 | 11×11 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 71 | ising_n300 | 300 | 35×35 | 4 | 37 | 9.2500 | success | **WIN** | noi +veloci |
| 72 | ising_n40 | 40 | 13×13 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 73 | ising_n400 | 400 | 39×39 | 4 | 47 | 11.7500 | success | **WIN** | noi +veloci |
| 74 | ising_n420 | 420 | 41×41 | 4 | 50 | 12.5000 | success | **WIN** | noi +veloci |
| 75 | ising_n5 | 5 | 5×5 | 6 | 4 | 0.6667 | success | LOSS | noi +veloci |
| 76 | ising_n50 | 50 | 15×15 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 77 | ising_n60 | 60 | 15×15 | 4 | 11 | 2.7500 | success | **WIN** | noi +veloci |
| 78 | ising_n70 | 70 | 17×17 | 4 | 14 | 3.5000 | success | **WIN** | noi +veloci |
| 79 | ising_n80 | 80 | 17×17 | 4 | 14 | 3.5000 | success | **WIN** | noi +veloci |
| 80 | ising_n90 | 90 | 19×19 | 4 | 16 | 4.0000 | success | **WIN** | noi +veloci |
| 81 | multiplier_n100 | 100 | 23×23 | 111762 | — | — | failed | timeout | noi +veloci |
| 82 | multiplier_n15 | 9 | 5×5 | 13 | 12 | 0.9231 | success | LOSS | noi +veloci |
| 83 | multiplier_n20 | 20 | 11×11 | 3990 | 3993 | 1.0008 | success | **WIN** | noi +veloci |
| 84 | multiplier_n200 | 200 | 33×33 | 450019 | — | — | failed | timeout | noi +veloci |
| 85 | multiplier_n300 | 300 | 39×39 | 1013844 | — | — | failed | timeout | noi +veloci |
| 86 | multiplier_n40 | 40 | 17×17 | 17329 | 17329 | 1.0000 | success | = | noi +veloci |
| 87 | multiplier_n400 | 400 | 43×43 | 1811712 | — | — | failed | timeout | WISQ +veloce |
| 88 | multiplier_n45 | 27 | 13×13 | 36 | 36 | 1.0000 | success | = | noi +veloci |
| 89 | multiplier_n60 | 60 | 19×19 | 39730 | 39730 | 1.0000 | success | = | noi +veloci |
| 90 | multiplier_n75 | 45 | 17×17 | 60 | 60 | 1.0000 | success | = | noi +veloci |
| 91 | multiplier_n80 | 80 | 21×21 | 71287 | 71287 | 1.0000 | success | = | noi +veloci |
| 92 | multiply_n13 | 6 | 5×5 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 93 | parallel | 8 | 5×5 | 10 | 13 | 1.3000 | success | **WIN** | noi +veloci |
| 94 | parallel_big | 20 | 9×9 | 8 | 14 | 1.7500 | success | **WIN** | noi +veloci |
| 95 | qaoa_n10 | 10 | 7×7 | 46 | 48 | 1.0435 | success | **WIN** | noi +veloci |
| 96 | qaoa_n100 | 100 | 19×19 | 1484 | 1167 | 0.7864 | success | LOSS | noi +veloci |
| 97 | qaoa_n125 | 125 | 23×23 | 1767 | 1649 | 0.9332 | success | LOSS | noi +veloci |
| 98 | qaoa_n150 | 150 | 25×25 | 2349 | 2173 | 0.9251 | success | LOSS | noi +veloci |
| 99 | qaoa_n175 | 175 | 27×27 | 3101 | 2812 | 0.9068 | success | LOSS | noi +veloci |
| 100 | qaoa_n20 | 20 | 9×9 | 102 | 109 | 1.0686 | success | **WIN** | noi +veloci |
| 101 | qaoa_n200 | 200 | 29×29 | 3893 | 3591 | 0.9224 | success | LOSS | noi +veloci |
| 102 | qaoa_n30 | 30 | 11×11 | 181 | 181 | 1.0000 | success | = | noi +veloci |
| 103 | qaoa_n300 | 300 | 35×35 | 7724 | 7173 | 0.9287 | success | LOSS | noi +veloci |
| 104 | qaoa_n40 | 40 | 13×13 | 274 | 276 | 1.0073 | success | **WIN** | noi +veloci |
| 105 | qaoa_n400 | 400 | 43×43 | 11742 | — | — | failed | timeout | noi +veloci |
| 106 | qaoa_n5 | 5 | 5×5 | 18 | 14 | 0.7778 | success | LOSS | noi +veloci |
| 107 | qaoa_n50 | 50 | 15×15 | 381 | 371 | 0.9738 | success | LOSS | noi +veloci |
| 108 | qaoa_n6 | 6 | 5×5 | 36 | 36 | 1.0000 | success | = | noi +veloci |
| 109 | qaoa_n60 | 60 | 15×15 | 612 | 511 | 0.8350 | success | LOSS | noi +veloci |
| 110 | qaoa_n64 | 64 | 15×15 | 798 | 582 | 0.7293 | success | LOSS | noi +veloci |
| 111 | qaoa_n6_transpiled | 6 | 5×5 | 36 | 33 | 0.9167 | success | LOSS | noi +veloci |
| 112 | qaoa_n70 | 70 | 17×17 | 699 | 639 | 0.9142 | success | LOSS | noi +veloci |
| 113 | qaoa_n80 | 80 | 17×17 | 950 | 790 | 0.8316 | success | LOSS | noi +veloci |
| 114 | qaoa_n90 | 90 | 19×19 | 1072 | 958 | 0.8937 | success | LOSS | noi +veloci |
| 115 | qec_en_n5 | 5 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 116 | qft_20 | 20 | 9×9 | 97 | 113 | 1.1649 | success | **WIN** | noi +veloci |
| 117 | qft_n10 | 10 | 7×7 | 40 | 45 | 1.1250 | success | **WIN** | noi +veloci |
| 118 | qft_n100 | 100 | 19×19 | 771 | 591 | 0.7665 | success | LOSS | noi +veloci |
| 119 | qft_n125 | 125 | 23×23 | 2618 | 672 | 0.2567 | success | LOSS | noi +veloci |
| 120 | qft_n128 | 128 | 23×23 | 2687 | 697 | 0.2594 | success | LOSS | noi +veloci |
| 121 | qft_n150 | 150 | 25×25 | 3140 | 782 | 0.2490 | success | LOSS | noi +veloci |
| 122 | qft_n175 | 175 | 27×27 | 3759 | 898 | 0.2389 | success | LOSS | noi +veloci |
| 123 | qft_n18 | 18 | 9×9 | 79 | 100 | 1.2658 | success | **WIN** | noi +veloci |
| 124 | qft_n20 | 20 | 9×9 | 98 | 110 | 1.1224 | success | **WIN** | noi +veloci |
| 125 | qft_n200 | 200 | 29×29 | 4291 | 982 | 0.2289 | success | LOSS | noi +veloci |
| 126 | qft_n30 | 30 | 11×11 | 179 | 192 | 1.0726 | success | **WIN** | noi +veloci |
| 127 | qft_n300 | 300 | 35×35 | 6559 | 1389 | 0.2118 | success | LOSS | noi +veloci |
| 128 | qft_n320 | 320 | 39×39 | 8406 | — | — | failed | timeout | noi +veloci |
| 129 | qft_n40 | 40 | 13×13 | 285 | 244 | 0.8561 | success | LOSS | noi +veloci |
| 130 | qft_n400 | 400 | 39×39 | 9200 | 1869 | 0.2032 | success | LOSS | noi +veloci |
| 131 | qft_n5 | 5 | 5×5 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 132 | qft_n50 | 50 | 15×15 | 282 | 308 | 1.0922 | success | **WIN** | noi +veloci |
| 133 | qft_n60 | 60 | 15×15 | 399 | 368 | 0.9223 | success | LOSS | noi +veloci |
| 134 | qft_n64 | 64 | 15×15 | 473 | 407 | 0.8605 | success | LOSS | noi +veloci |
| 135 | qft_n70 | 70 | 17×17 | 431 | 424 | 0.9838 | success | LOSS | noi +veloci |
| 136 | qft_n80 | 80 | 17×17 | 563 | 473 | 0.8401 | success | LOSS | noi +veloci |
| 137 | qft_n90 | 90 | 19×19 | 578 | 528 | 0.9135 | success | LOSS | noi +veloci |
| 138 | qpe_n9_transpiled | 9 | 5×5 | 42 | 42 | 1.0000 | success | = | noi +veloci |
| 139 | qram_n20 | 9 | 5×5 | 8 | 9 | 1.1250 | success | **WIN** | noi +veloci |
| 140 | randomcircuit_n100 | 100 | 22×22 | 5404 | 4911 | 0.9088 | success | LOSS | noi +veloci |
| 141 | randomcircuit_n200 | 200 | 33×33 | 15543 | — | — | failed | timeout | noi +veloci |
| 142 | randomcircuit_n50 | 50 | 19×19 | 1510 | 1445 | 0.9570 | success | LOSS | noi +veloci |
| 143 | seca_n11 | 11 | 7×7 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 144 | simon_n6 | 3 | 3×3 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 145 | square_root_n18 | 14 | 7×7 | 27 | 27 | 1.0000 | success | = | noi +veloci |
| 146 | square_root_n45 | 32 | 11×11 | 570 | 571 | 1.0018 | success | **WIN** | noi +veloci |
| 147 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 272 | 167 | 0.6140 | success | LOSS | noi +veloci |
| 148 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 406 | 168 | 0.4138 | success | LOSS | noi +veloci |
| 149 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 320 | 217 | 0.6781 | success | LOSS | noi +veloci |
| 150 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 22×22 | 292 | 215 | 0.7363 | success | LOSS | noi +veloci |
| 151 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 304 | 232 | 0.7632 | success | LOSS | noi +veloci |
| 152 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 22×22 | 303 | 235 | 0.7756 | success | LOSS | noi +veloci |
| 153 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 576 | 430 | 0.7465 | success | LOSS | noi +veloci |
| 154 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 584 | 449 | 0.7688 | success | LOSS | noi +veloci |
| 155 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 603 | 460 | 0.7629 | success | LOSS | noi +veloci |
| 156 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 610 | 455 | 0.7459 | success | LOSS | noi +veloci |
| 157 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 623 | 519 | 0.8331 | success | LOSS | noi +veloci |
| 158 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 610 | 498 | 0.8164 | success | LOSS | noi +veloci |
| 159 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 719 | 367 | 0.5104 | success | LOSS | noi +veloci |
| 160 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 32×32 | 785 | 424 | 0.5401 | success | LOSS | noi +veloci |
| 161 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 850 | 601 | 0.7071 | success | LOSS | noi +veloci |
| 162 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 820 | 607 | 0.7402 | success | LOSS | noi +veloci |
| 163 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 31×31 | 1627 | 700 | 0.4302 | success | LOSS | noi +veloci |
| 164 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 868 | 670 | 0.7719 | success | LOSS | noi +veloci |
| 165 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 1879 | 1284 | 0.6833 | success | LOSS | noi +veloci |
| 166 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 29×29 | 2246 | 1288 | 0.5735 | success | LOSS | noi +veloci |
| 167 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 1901 | 1429 | 0.7517 | success | LOSS | noi +veloci |
| 168 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 30×30 | 1932 | 1336 | 0.6915 | success | LOSS | noi +veloci |
| 169 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 5653 | 1577 | 0.2790 | success | LOSS | noi +veloci |
| 170 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 29×29 | 2102 | 1574 | 0.7488 | success | LOSS | noi +veloci |
| 171 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 76 | 61 | 0.8026 | success | LOSS | noi +veloci |
| 172 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 18×18 | 70 | 60 | 0.8571 | success | LOSS | noi +veloci |
| 173 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 79 | 70 | 0.8861 | success | LOSS | noi +veloci |
| 174 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 80 | 75 | 0.9375 | success | LOSS | noi +veloci |
| 175 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 78 | 68 | 0.8718 | success | LOSS | noi +veloci |
| 176 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 77 | 71 | 0.9221 | success | LOSS | noi +veloci |
| 177 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 117 | 108 | 0.9231 | success | LOSS | noi +veloci |
| 178 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 147 | 133 | 0.9048 | success | LOSS | noi +veloci |
| 179 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 157 | 139 | 0.8854 | success | LOSS | noi +veloci |
| 180 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 18×18 | 159 | 162 | 1.0189 | success | **WIN** | noi +veloci |
| 181 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 163 | 151 | 0.9264 | success | LOSS | noi +veloci |
| 182 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 155 | 148 | 0.9548 | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 154 | 146 | 0.9481 | success | LOSS | noi +veloci |
| 184 | t_test | 8 | 5×5 | 121 | 110 | 0.9091 | success | LOSS | noi +veloci |
| 185 | toffoli_n3 | 3 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 186 | vqe_real_amp_n10 | 10 | 7×7 | 13 | 15 | 1.1538 | success | **WIN** | noi +veloci |
| 187 | vqe_real_amp_n100 | 100 | 19×19 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 188 | vqe_real_amp_n125 | 125 | 23×23 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 189 | vqe_real_amp_n150 | 150 | 25×25 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 190 | vqe_real_amp_n175 | 175 | 27×27 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 191 | vqe_real_amp_n20 | 20 | 9×9 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 192 | vqe_real_amp_n200 | 200 | 29×29 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 193 | vqe_real_amp_n30 | 30 | 11×11 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 194 | vqe_real_amp_n300 | 300 | 35×35 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 195 | vqe_real_amp_n40 | 40 | 13×13 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 196 | vqe_real_amp_n400 | 400 | 39×39 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 197 | vqe_real_amp_n5 | 5 | 5×5 | 10 | 8 | 0.8000 | success | LOSS | noi +veloci |
| 198 | vqe_real_amp_n50 | 50 | 15×15 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 199 | vqe_real_amp_n60 | 60 | 15×15 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 200 | vqe_real_amp_n70 | 70 | 17×17 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 201 | vqe_real_amp_n80 | 80 | 17×17 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 202 | vqe_real_amp_n90 | 90 | 19×19 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 203 | vqe_su2_n10 | 10 | 7×7 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 204 | vqe_su2_n100 | 100 | 19×19 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 205 | vqe_su2_n125 | 125 | 23×23 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 206 | vqe_su2_n150 | 150 | 25×25 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 207 | vqe_su2_n175 | 175 | 27×27 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 208 | vqe_su2_n20 | 20 | 9×9 | 23 | 25 | 1.0870 | success | **WIN** | noi +veloci |
| 209 | vqe_su2_n200 | 200 | 29×29 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 210 | vqe_su2_n30 | 30 | 11×11 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 211 | vqe_su2_n300 | 300 | 35×35 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 212 | vqe_su2_n40 | 40 | 13×13 | 43 | 45 | 1.0465 | success | **WIN** | noi +veloci |
| 213 | vqe_su2_n400 | 400 | 39×39 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 214 | vqe_su2_n5 | 5 | 5×5 | 10 | 8 | 0.8000 | success | LOSS | noi +veloci |
| 215 | vqe_su2_n50 | 50 | 15×15 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 216 | vqe_su2_n60 | 60 | 15×15 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 217 | vqe_su2_n70 | 70 | 17×17 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 218 | vqe_su2_n80 | 80 | 17×17 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 219 | vqe_su2_n90 | 90 | 19×19 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 220 | vqe_two_local_n10 | 10 | 7×7 | 44 | 55 | 1.2500 | success | **WIN** | noi +veloci |
| 221 | vqe_two_local_n100 | 100 | 19×19 | 2094 | 1891 | 0.9031 | success | LOSS | noi +veloci |
| 222 | vqe_two_local_n125 | 125 | 23×23 | 2500 | 2600 | 1.0400 | success | **WIN** | noi +veloci |
| 223 | vqe_two_local_n150 | 150 | 25×25 | 3383 | 3568 | 1.0547 | success | **WIN** | noi +veloci |
| 224 | vqe_two_local_n175 | 175 | 27×27 | 4482 | 4556 | 1.0165 | success | **WIN** | noi +veloci |
| 225 | vqe_two_local_n20 | 20 | 9×9 | 123 | 157 | 1.2764 | success | **WIN** | noi +veloci |
| 226 | vqe_two_local_n200 | 200 | 29×29 | 5564 | 5626 | 1.0111 | success | **WIN** | noi +veloci |
| 227 | vqe_two_local_n30 | 30 | 11×11 | 253 | 272 | 1.0751 | success | **WIN** | noi +veloci |
| 228 | vqe_two_local_n300 | 300 | 39×39 | 10532 | — | — | failed | timeout | noi +veloci |
| 229 | vqe_two_local_n40 | 40 | 13×13 | 366 | 413 | 1.1284 | success | **WIN** | noi +veloci |
| 230 | vqe_two_local_n400 | 400 | 43×43 | 17105 | — | — | failed | timeout | noi +veloci |
| 231 | vqe_two_local_n5 | 5 | 5×5 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 232 | vqe_two_local_n50 | 50 | 15×15 | 518 | 576 | 1.1120 | success | **WIN** | noi +veloci |
| 233 | vqe_two_local_n60 | 60 | 15×15 | 967 | 805 | 0.8325 | success | LOSS | noi +veloci |
| 234 | vqe_two_local_n70 | 70 | 17×17 | 963 | 1011 | 1.0498 | success | **WIN** | noi +veloci |
| 235 | vqe_two_local_n80 | 80 | 17×17 | 1362 | 1349 | 0.9905 | success | LOSS | noi +veloci |
| 236 | vqe_two_local_n90 | 90 | 19×19 | 1527 | 1558 | 1.0203 | success | **WIN** | noi +veloci |
| 237 | vqe_uccsd_n4 | 4 | 3×3 | 87 | 88 | 1.0115 | success | **WIN** | noi +veloci |
| 238 | vqe_uccsd_n8 | 8 | 5×5 | 5446 | 5446 | 1.0000 | success | = | noi +veloci |
| 239 | wstate_n10 | 10 | 7×7 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 240 | wstate_n100 | 100 | 19×19 | 101 | 101 | 1.0000 | success | = | noi +veloci |
| 241 | wstate_n125 | 125 | 23×23 | 126 | 126 | 1.0000 | success | = | noi +veloci |
| 242 | wstate_n150 | 150 | 25×25 | 151 | 151 | 1.0000 | success | = | noi +veloci |
| 243 | wstate_n175 | 175 | 27×27 | 176 | 176 | 1.0000 | success | = | noi +veloci |
| 244 | wstate_n20 | 20 | 9×9 | 21 | 21 | 1.0000 | success | = | noi +veloci |
| 245 | wstate_n200 | 200 | 29×29 | 201 | 201 | 1.0000 | success | = | noi +veloci |
| 246 | wstate_n27 | 27 | 11×11 | 28 | 28 | 1.0000 | success | = | noi +veloci |
| 247 | wstate_n30 | 30 | 11×11 | 31 | 31 | 1.0000 | success | = | noi +veloci |
| 248 | wstate_n300 | 300 | 35×35 | 301 | 301 | 1.0000 | success | = | noi +veloci |
| 249 | wstate_n40 | 40 | 13×13 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 250 | wstate_n400 | 400 | 39×39 | 401 | 401 | 1.0000 | success | = | noi +veloci |
| 251 | wstate_n5 | 5 | 5×5 | 7 | 6 | 0.8571 | success | LOSS | noi +veloci |
| 252 | wstate_n50 | 50 | 15×15 | 51 | 51 | 1.0000 | success | = | noi +veloci |
| 253 | wstate_n60 | 60 | 15×15 | 61 | 61 | 1.0000 | success | = | noi +veloci |
| 254 | wstate_n70 | 70 | 17×17 | 71 | 71 | 1.0000 | success | = | noi +veloci |
| 255 | wstate_n80 | 80 | 17×17 | 81 | 81 | 1.0000 | success | = | noi +veloci |
| 256 | wstate_n90 | 90 | 19×19 | 91 | 91 | 1.0000 | success | = | noi +veloci |
