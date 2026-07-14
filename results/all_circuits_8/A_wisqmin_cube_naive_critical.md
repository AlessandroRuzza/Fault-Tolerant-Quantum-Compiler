# wisqmin — cube + naive_critical (config FISSA, same-grid)


FAIR. Config scelta a priori: safe_passage=cube, routing=naive_critical. Entrambi i compiler sulla STESSA griglia: s* = la griglia MINIMA su cui WISQ riesce a instradare. Confronto same-grid sugli step. 256 circuiti (esclusi randomcircuit_n400 e bwt_n177).


Dati da: `wisqmin_cube_naive_critical.csv` — **256 circuiti**.


---


## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **Nostro mapping FALLISCE** | 194 | — |
| **Mappiamo con successo** | 62 | — |
| ↳ WISQ va in timeout (noi vinciamo) | 5 | — |
| ↳ Entrambi completano | 57 | — |
|   ↳ Noi vinciamo su steps | 8 (ratio mediana 1.26×) | 8 (100.0%) |
|   ↳ Pareggio su steps | 27 | 27 (100.0%) |
|   ↳ WISQ vince su steps | 22 (ratio mediana 0.93×) | 22 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **40 / 256 (15.6%)** | — |
| ↳ Noi completiamo, WISQ va in timeout | 5 / 256 (2.0%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 8 / 256 (3.1%) | — |
| ↳ Pareggio su steps, noi più veloci | 27 / 256 (10.5%) | — |
| | | |
| **SCONFITTE (mapping fallito)** | **194 / 256 (75.8%)** | — |

Circuiti dove non mappiamo: `ghz_n60`, `graphstate_n70`, `ghz_n30`, `ghz_n80`, `ising_n80`, `ghz_n10`, `graphstate_n125`, `ising_n26`, `graphstate_n50`, `ising_n100`, `ghz_n175`, `qaoa_n10`, `graphstate_n90`, `ising_n150`, `simon_n6`, `qft_n10`, `qft_n18`, `graphstate_n300`, `ising_n300`, `ising_n10`, `ghz_n100`, `multiplier_n15`, `ghz_n90`, `ising_n30`, `graphstate_n40`, `graphstate_n60`, `53qubits_155gate_57layers`, `graphstate_n100`, `ising_n70`, `ghz_n70`, `ghz_n300`, `graphstate_n30`, `continuous_3_17_13`, `ghz_n150`, `ising_n50`, `adder_n28`, `ising_n60`, `qpe_n9_transpiled`, `square_root_n18`, `ising_n90`, `ising_n175`, `graphstate_n150`, `graphstate_n175`, `ising_n125`, `ghz_n400`, `seca_n11`, `graphstate_n400`, `graphstate_n20`, `ghz_state_n23`, `ghz_n125`, `ghz_state_n255`, `vqe_real_amp_n10`, `qft_n20`, `cat_n130`, `19qubits_511gate_153layers`, `ising_n400`, `ising_n420`, `ghz_n50`, `qft_n30`, `graphstate_n80`, `vqe_real_amp_n30`, `qaoa_n20`, `dnn_n16`, `qaoa_n30`, `qft_20`, `vqe_su2_n10`, `vqe_real_amp_n60`, `vqe_real_amp_n80`, `graphstate_n200`, `ghz_n255`, `vqe_su2_n50`, `vqe_real_amp_n50`, `vqe_su2_n70`, `vqe_su2_n125`, `cat_n260`, `vqe_real_amp_n90`, `vqe_real_amp_n100`, `adder_n64_transpiled`, `vqe_su2_n30`, `19qubits_521gate_352layers`, `vqe_two_local_n20`, `vqe_real_amp_n150`, `vqe_su2_n90`, `wstate_n10`, `vqe_su2_n80`, `vqe_real_amp_n175`, `t_test`, `qft_n40`, `vqe_su2_n150`, `vqe_real_amp_n125`, `vqe_uccsd_n4`, `vqe_real_amp_n70`, `wstate_n125`, `vqe_su2_n100`, `qft_n64`, `vqe_two_local_n30`, `qaoa_n50`, `wstate_n30`, `wstate_n60`, `qaoa_n40`, `vqe_su2_n175`, `vqe_su2_n60`, `wstate_n175`, `vqe_two_local_n10`, `wstate_n80`, `qft_n70`, `qft_n50`, `vqe_two_local_n40`, `wstate_n150`, `wstate_n27`, `qft_n60`, `adder_n433`, `vqe_real_amp_n300`, `wstate_n70`, `square_root_n45`, `qaoa_n64`, `qft_n100`, `vqe_su2_n300`, `vqe_two_local_n60`, `qft_n80`, `qaoa_n60`, `wstate_n400`, `qft_n90`, `wstate_n100`, `vqe_su2_n400`, `qft_n125`, `vqe_two_local_n50`, `wstate_n50`, `wstate_n90`, `vqe_two_local_n70`, `qaoa_n70`, `wstate_n300`, `qaoa_n90`, `vqe_real_amp_n400`, `qaoa_n80`, `qft_n128`, `qft_n175`, `vqe_two_local_n100`, `vqe_two_local_n80`, `qaoa_n100`, `qaoa_n125`, `qft_n300`, `qaoa_n150`, `vqe_two_local_n125`, `qaoa_n175`, `synth_n100_d020_mix050_t030_hf000_hm001_r2_s0`, `qft_n400`, `synth_n200_d040_mix000_t030_hf000_hm001_r2_s0`, `synth_n200_d040_mix100_t030_hf000_hm001_r2_s1`, `synth_n200_d040_mix000_t030_hf000_hm001_r2_s1`, `vqe_two_local_n90`, `synth_n100_d020_mix000_t030_hf000_hm001_r2_s0`, `synth_n200_d040_mix100_t030_hf000_hm001_r2_s0`, `synth_n100_d020_mix100_t030_hf000_hm001_r2_s0`, `synth_n100_d020_mix000_t030_hf000_hm001_r2_s1`, `vqe_two_local_n150`, `synth_n200_d040_mix050_t030_hf000_hm001_r2_s0`, `qaoa_n200`, `synth_n100_d040_mix100_t030_hf000_hm001_r2_s1`, `vqe_two_local_n200`, `synth_n100_d040_mix000_t030_hf000_hm001_r2_s0`, `synth_n100_d040_mix100_t030_hf000_hm001_r2_s0`, `synth_n100_d040_mix000_t030_hf000_hm001_r2_s1`, `vqe_two_local_n175`, `qaoa_n300`, `synth_n100_d040_mix050_t030_hf000_hm001_r2_s1`, `synth_n100_d040_mix050_t030_hf000_hm001_r2_s0`, `synth_n100_d020_mix050_t030_hf000_hm001_r2_s1`, `synth_n100_d020_mix100_t030_hf000_hm001_r2_s1`, `grover_n10`, `synth_n50_d020_mix000_t030_hf000_hm001_r2_s1`, `synth_n50_d040_mix050_t030_hf000_hm001_r2_s0`, `synth_n200_d040_mix050_t030_hf000_hm001_r2_s1`, `synth_n200_d020_mix100_t030_hf000_hm001_r2_s0`, `synth_n200_d020_mix000_t030_hf000_hm001_r2_s0`, `qft_n320`, `randomcircuit_n100`, `multiplier_n60`, `multiplier_n100`, `randomcircuit_n50`, `synth_n200_d020_mix050_t030_hf000_hm001_r2_s1`, `synth_n200_d020_mix050_t030_hf000_hm001_r2_s0`, `multiplier_n200`, `bwt_n57`, `qaoa_n400`, `vqe_two_local_n400`, `randomcircuit_n200`, `synth_n50_d020_mix100_t030_hf000_hm001_r2_s0`, `multiplier_n80`, `vqe_two_local_n300`, `synth_n200_d020_mix000_t030_hf000_hm001_r2_s1`, `synth_n200_d020_mix100_t030_hf000_hm001_r2_s1`, `multiplier_n400`, `multiplier_n300`.

---


## Routing steps in aggregato (nostro vs WISQ)

Sui 57 circuiti dove **entrambi completano**:

| Metrica | Valore |
|---------|--------|
| Somma `my_routing_steps` | 104.718 |
| Somma `wisq_routing_steps` | 103.598 |
| **Rapporto dei totali (wisq / nostro)** | **0.99 → WISQ usa 1.1% di steps in meno** |
| Mediana di `ratio_wisq_over_mine` | 1.00 |
| Media di `ratio_wisq_over_mine` | 1.038 |

---


## Densità dei circuiti: dove vinciamo vs dove perdiamo

`cnot_interaction_density` = coppie-qubit CNOT distinte / coppie possibili `Q·(Q−1)/2` (0 = sparso/locale, 1 = ogni coppia interagisce). Calcolata dal QASM universale su 57/57 circuiti both-complete con QASM disponibile.

**Per esito sugli steps:**

| Esito (steps) | N | densità media | mediana | min | max |
|---|---|---|---|---|---|
| **Vinciamo** (WIN) | 8 | 0.308 | 0.100 | 0.010 | 1.000 |
| Pareggio (TIE) | 27 | 0.354 | 0.400 | 0.010 | 1.000 |
| **Perdiamo** (LOSS) | 22 | 0.298 | 0.211 | 0.010 | 1.000 |

**Win/Loss per fascia di densità** (sugli steps, both-complete):

| Densità `cid` | N | Win | Tie | Loss | Loss-rate (decisi) |
|---|---|---|---|---|---|
| < 0.15 | 20 | 5 | 9 | 6 | 54.5% |
| 0.15 – 0.40 | 12 | 0 | 4 | 8 | 100.0% |
| ≥ 0.40 | 25 | 3 | 14 | 8 | 72.7% |

---


## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| Nostro mapping fallisce | 194 | — |
| **WISQ non finisce in 1 ora** | 10 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 10 | — |
| **Entrambi finiscono in 1 ora** | 52 | — |
| ↳ Noi vinciamo su steps | 7 (ratio mediana 1.43×) | 7 (100.0%) |
| ↳ Pareggio su steps | 25 | 25 (100.0%) |
| ↳ WISQ vince su steps | 20 (ratio mediana 0.93×) | 20 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **42 / 256 (16.4%)** | — |

---


## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| Nostro mapping fallisce | 194 | — |
| **WISQ non finisce in 30 minuti** | 10 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 10 | — |
| **Entrambi finiscono in 30 minuti** | 52 | — |
| ↳ Noi vinciamo su steps | 7 (ratio mediana 1.43×) | 7 (100.0%) |
| ↳ Pareggio su steps | 25 | 25 (100.0%) |
| ↳ WISQ vince su steps | 20 (ratio mediana 0.93×) | 20 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **42 / 256 (16.4%)** | — |

---


## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| Nostro mapping fallisce | 194 | — |
| **WISQ non finisce in 15 minuti** | 11 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 11 | — |
| **Entrambi finiscono in 15 minuti** | 51 | — |
| ↳ Noi vinciamo su steps | 7 (ratio mediana 1.43×) | 7 (100.0%) |
| ↳ Pareggio su steps | 25 | 25 (100.0%) |
| ↳ WISQ vince su steps | 19 (ratio mediana 0.93×) | 19 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **43 / 256 (16.8%)** | — |

---


## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| Nostro mapping fallisce | 194 | — |
| **WISQ non finisce in 10 minuti** | 11 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 11 | — |
| **Entrambi finiscono in 10 minuti** | 51 | — |
| ↳ Noi vinciamo su steps | 7 (ratio mediana 1.43×) | 7 (100.0%) |
| ↳ Pareggio su steps | 25 | 25 (100.0%) |
| ↳ WISQ vince su steps | 19 (ratio mediana 0.93×) | 19 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **43 / 256 (16.8%)** | — |

---


## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| Nostro mapping fallisce | 194 | — |
| **WISQ non finisce in 5 minuti** | 15 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 15 | — |
| **Entrambi finiscono in 5 minuti** | 47 | — |
| ↳ Noi vinciamo su steps | 7 (ratio mediana 1.43×) | 7 (100.0%) |
| ↳ Pareggio su steps | 25 | 25 (100.0%) |
| ↳ WISQ vince su steps | 15 (ratio mediana 0.93×) | 15 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **47 / 256 (18.4%)** | — |

---


## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| Nostro mapping fallisce | 194 | — |
| **WISQ non finisce in 1 minuto** | 24 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 24 | — |
| **Entrambi finiscono in 1 minuto** | 38 | — |
| ↳ Noi vinciamo su steps | 6 (ratio mediana 1.59×) | 6 (100.0%) |
| ↳ Pareggio su steps | 25 | 25 (100.0%) |
| ↳ WISQ vince su steps | 7 (ratio mediana 0.93×) | 7 (100.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **55 / 256 (21.5%)** | — |

---


## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (orig., asimm.) | 57 | 5 | 0 | 0 | **40 (15.6%)** |
| 1 ora | 52 | 10 | 0 | 0 | **42 (16.4%)** |
| 30 minuti | 52 | 10 | 0 | 0 | **42 (16.4%)** |
| 15 minuti | 51 | 11 | 0 | 0 | **43 (16.8%)** |
| 10 minuti | 51 | 11 | 0 | 0 | **43 (16.8%)** |
| 5 minuti | 47 | 15 | 0 | 0 | **47 (18.4%)** |
| 1 minuto | 38 | 24 | 0 | 0 | **55 (21.5%)** ⟵ picco |

---


## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s`. Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). I timeout WISQ sono inclusi con la durata registrata.

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 62 | 61 (98.4%) | 917× | 3017× | 0.61× | 32623× |
| ↳ Dove vinciamo su steps | 8 | 8 (100.0%) | 747× | 5695× | 195.05× | 32623× |
| ↳ In pareggio su steps | 27 | 27 (100.0%) | 659× | 1996× | 70.90× | 20741× |
| ↳ Dove WISQ vince su steps | 22 | 22 (100.0%) | 2506× | 3097× | 255.66× | 8463× |
| ↳ WISQ in timeout | 5 | 4 (80.0%) | 4390× | 3888× | 0.61× | 7777× |

---


## Buffer di steps dipendente dalla velocità — win-rate vs WISQ

Analisi su `wisqmin_cube_naive_critical.csv`. La metrica primaria sono i **routing steps**, il tempo è secondario: concediamo un buffer ε sugli steps che cresce con l'ordine di grandezza del vantaggio di tempo.

```
vinco  se   my_steps <= wisq_steps · (1 + ε)
ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time
α = 0.05 / log10(N)      (ancora: 5% di sforo steps ⇄ N× di velocità)
```

Baseline (steps primario, tempo solo spareggio) = **40/256 = 15.6%**.

| ancora | α | loss recuperati | vittorie | % |
|---|---:|---:|---:|---:|
| 5% ⇄ 20× | 0.0384 | 15 | 55 | 21.5% |
| 5% ⇄ 50× | 0.0294 | 14 | 54 | 21.1% |
| 5% ⇄ 100× | 0.0250 | 13 | 53 | 20.7% |
| 5% ⇄ 150× | 0.0230 | 12 | 52 | 20.3% |
| 5% ⇄ 200× | 0.0217 | 12 | 52 | 20.3% |
| 5% ⇄ 300× | 0.0202 | 10 | 50 | 19.5% |
| 5% ⇄ 400× | 0.0192 | 9 | 49 | 19.1% |
| 5% ⇄ 500× | 0.0185 | 9 | 49 | 19.1% |
| 5% ⇄ 750× | 0.0174 | 9 | 49 | 19.1% |
| 5% ⇄ 1000× | 0.0167 | 9 | 49 | 19.1% |
| 5% ⇄ 1500× | 0.0157 | 7 | 47 | 18.4% |
| 5% ⇄ 2000× | 0.0151 | 7 | 47 | 18.4% |
| 5% ⇄ 2500× | 0.0147 | 7 | 47 | 18.4% |
| 5% ⇄ 3000× | 0.0144 | 7 | 47 | 18.4% |
| 5% ⇄ 4000× | 0.0139 | 7 | 47 | 18.4% |
| 5% ⇄ 5000× | 0.0135 | 7 | 47 | 18.4% |

---


## Per famiglia di circuiti

**WISQ timeout** = WISQ non ha completato. **MapFail** = il nostro mapping non riesce. Win/=/Loss sono sugli steps dove entrambi completano.

| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | MapFail | Note |
|--------|---|-----|----------------|------|--------------|---------|------|
| 19qubits | 2 | 0 | 0 (0 noi+veloci) | 0 | 0 | 2 | n=19 |
| 53qubits | 2 | 0 | 1 (1 noi+veloci) | 0 | 0 | 1 | n=27–39 |
| adder | 4 | 0 | 1 (1 noi+veloci) | 0 | 0 | 3 | n=4–433 |
| bigadder | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=18 |
| bv | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=153 |
| bwt | 4 | 0 | 0 (0 noi+veloci) | 0 | 3 | 1 | n=21–73 |
| cat | 2 | 0 | 0 (0 noi+veloci) | 0 | 0 | 2 | n=130–260 |
| continuous_3_17 | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | n=3 |
| dnn | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | n=16 |
| factor247 | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=15 |
| fredkin | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| ghz | 18 | 0 | 4 (4 noi+veloci) | 0 | 0 | 14 | n=5–400 |
| ghz_state | 2 | 0 | 0 (0 noi+veloci) | 0 | 0 | 2 | n=23–255 |
| graphstate | 17 | 0 | 2 (2 noi+veloci) | 0 | 0 | 15 | n=5–400 |
| grover | 3 | 1 | 0 (0 noi+veloci) | 0 | 1 | 1 | n=5–19 |
| hhl | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=10 |
| ising | 19 | 3 | 1 (1 noi+veloci) | 0 | 0 | 15 | n=5–420 |
| multiplier | 11 | 1 | 3 (3 noi+veloci) | 0 | 0 | 7 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 1 | 2 (2 noi+veloci) | 0 | 0 | 17 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5 |
| qft | 22 | 0 | 0 (0 noi+veloci) | 3 | 0 | 19 | n=5–400 |
| qpe | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | n=9 |
| qram | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=9 |
| randomcircuit | 3 | 0 | 0 (0 noi+veloci) | 0 | 0 | 3 | n=50–200 |
| seca | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | n=11 |
| simon | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | n=3 |
| square_root | 2 | 0 | 0 (0 noi+veloci) | 0 | 0 | 2 | n=14–32 |
| synth | 37 | 0 | 0 (0 noi+veloci) | 10 | 0 | 27 | n=50–200 |
| t_test | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | n=8 |
| toffoli | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| vqe_real_amp | 17 | 0 | 2 (2 noi+veloci) | 2 | 0 | 13 | n=5–400 |
| vqe_su2 | 17 | 1 | 1 (1 noi+veloci) | 2 | 0 | 13 | n=5–400 |
| vqe_two_local | 17 | 0 | 0 (0 noi+veloci) | 1 | 0 | 16 | n=5–400 |
| vqe_uccsd | 2 | 0 | 0 (0 noi+veloci) | 1 | 0 | 1 | n=4–8 |
| wstate | 18 | 0 | 2 (2 noi+veloci) | 2 | 0 | 14 | n=5–400 |

---


## Per circuito (dettaglio)

**Steps**: WIN = noi meno routing steps, LOSS = WISQ meno, = pareggio. **Tempo** confronta le durate quando disponibili.

| # | Circuit | Qubits | Grid | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | — | — | 100 | — | success | **MapFail** | — |
| 2 | 19qubits_521gate_352layers | 19 | — | — | 286 | — | success | **MapFail** | — |
| 3 | 53qubits_155gate_57layers | 27 | — | — | 23 | — | success | **MapFail** | — |
| 4 | 53qubits_332gate_152layers | 39 | 17×17 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | — | — | 24 | — | success | **MapFail** | — |
| 6 | adder_n4 | 4 | 7×7 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 7 | adder_n433 | 433 | — | — | 251 | — | success | **MapFail** | — |
| 8 | adder_n64_transpiled | 64 | — | — | 181 | — | success | **MapFail** | — |
| 9 | bigadder_n18_transpiled | 18 | 13×13 | 88 | 88 | 1.0000 | success | = | noi +veloci |
| 10 | bv_n280 | 153 | 33×33 | 152 | 152 | 1.0000 | success | = | noi +veloci |
| 11 | bwt_n21 | 21 | 13×13 | 116400 | — | — | failed | timeout | noi +veloci |
| 12 | bwt_n37 | 28 | 15×15 | 33660 | — | — | failed | timeout | noi +veloci |
| 13 | bwt_n57 | 43 | — | — | — | — | failed | **MapFail** | — |
| 14 | bwt_n97 | 73 | 21×21 | 130808 | — | — | failed | timeout | noi +veloci |
| 15 | cat_n130 | 130 | — | — | 129 | — | success | **MapFail** | — |
| 16 | cat_n260 | 260 | — | — | 259 | — | success | **MapFail** | — |
| 17 | continuous_3_17_13 | 3 | — | — | 17 | — | success | **MapFail** | — |
| 18 | dnn_n16 | 16 | — | — | 82 | — | success | **MapFail** | — |
| 19 | factor247_n15 | 15 | 11×11 | 349644 | — | — | failed | timeout | noi +veloci |
| 20 | fredkin_n3 | 3 | 6×6 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 21 | ghz_n10 | 10 | — | — | 9 | — | success | **MapFail** | — |
| 22 | ghz_n100 | 100 | — | — | 99 | — | success | **MapFail** | — |
| 23 | ghz_n125 | 125 | — | — | 124 | — | success | **MapFail** | — |
| 24 | ghz_n150 | 150 | — | — | 149 | — | success | **MapFail** | — |
| 25 | ghz_n175 | 175 | — | — | 174 | — | success | **MapFail** | — |
| 26 | ghz_n20 | 20 | 9×9 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 27 | ghz_n200 | 200 | 29×29 | 199 | 199 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n255 | 255 | — | — | 254 | — | success | **MapFail** | — |
| 29 | ghz_n30 | 30 | — | — | 29 | — | success | **MapFail** | — |
| 30 | ghz_n300 | 300 | — | — | 299 | — | success | **MapFail** | — |
| 31 | ghz_n40 | 40 | 13×13 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n400 | 400 | — | — | 399 | — | success | **MapFail** | — |
| 33 | ghz_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 34 | ghz_n50 | 50 | — | — | 49 | — | success | **MapFail** | — |
| 35 | ghz_n60 | 60 | — | — | 59 | — | success | **MapFail** | — |
| 36 | ghz_n70 | 70 | — | — | 69 | — | success | **MapFail** | — |
| 37 | ghz_n80 | 80 | — | — | 79 | — | success | **MapFail** | — |
| 38 | ghz_n90 | 90 | — | — | 89 | — | success | **MapFail** | — |
| 39 | ghz_state_n23 | 23 | — | — | 22 | — | success | **MapFail** | — |
| 40 | ghz_state_n255 | 255 | — | — | 254 | — | success | **MapFail** | — |
| 41 | graphstate_n10 | 10 | 7×7 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 42 | graphstate_n100 | 100 | — | — | 10 | — | success | **MapFail** | — |
| 43 | graphstate_n125 | 125 | — | — | 12 | — | success | **MapFail** | — |
| 44 | graphstate_n150 | 150 | — | — | 11 | — | success | **MapFail** | — |
| 45 | graphstate_n175 | 175 | — | — | 13 | — | success | **MapFail** | — |
| 46 | graphstate_n20 | 20 | — | — | 6 | — | success | **MapFail** | — |
| 47 | graphstate_n200 | 200 | — | — | 13 | — | success | **MapFail** | — |
| 48 | graphstate_n30 | 30 | — | — | 6 | — | success | **MapFail** | — |
| 49 | graphstate_n300 | 300 | — | — | 20 | — | success | **MapFail** | — |
| 50 | graphstate_n40 | 40 | — | — | 6 | — | success | **MapFail** | — |
| 51 | graphstate_n400 | 400 | — | — | 23 | — | success | **MapFail** | — |
| 52 | graphstate_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 53 | graphstate_n50 | 50 | — | — | 7 | — | success | **MapFail** | — |
| 54 | graphstate_n60 | 60 | — | — | 7 | — | success | **MapFail** | — |
| 55 | graphstate_n70 | 70 | — | — | 8 | — | success | **MapFail** | — |
| 56 | graphstate_n80 | 80 | — | — | 10 | — | success | **MapFail** | — |
| 57 | graphstate_n90 | 90 | — | — | 10 | — | success | **MapFail** | — |
| 58 | grover_n10 | 10 | — | — | 11017 | — | success | **MapFail** | — |
| 59 | grover_n20 | 19 | 13×13 | 2146489 | — | — | failed | timeout | WISQ +veloce |
| 60 | grover_n5 | 5 | 6×6 | 209 | 211 | 1.0096 | success | **WIN** | noi +veloci |
| 61 | hhl_n10 | 10 | 11×11 | 72039 | 72039 | 1.0000 | success | = | noi +veloci |
| 62 | ising_n10 | 10 | — | — | 4 | — | success | **MapFail** | — |
| 63 | ising_n100 | 100 | — | — | 19 | — | success | **MapFail** | — |
| 64 | ising_n125 | 125 | — | — | 22 | — | success | **MapFail** | — |
| 65 | ising_n150 | 150 | — | — | 21 | — | success | **MapFail** | — |
| 66 | ising_n175 | 175 | — | — | 25 | — | success | **MapFail** | — |
| 67 | ising_n20 | 20 | 9×9 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 68 | ising_n200 | 200 | 29×29 | 9 | 27 | 3.0000 | success | **WIN** | noi +veloci |
| 69 | ising_n26 | 26 | — | — | 8 | — | success | **MapFail** | — |
| 70 | ising_n30 | 30 | — | — | 10 | — | success | **MapFail** | — |
| 71 | ising_n300 | 300 | — | — | 37 | — | success | **MapFail** | — |
| 72 | ising_n40 | 40 | 13×13 | 7 | 10 | 1.4286 | success | **WIN** | noi +veloci |
| 73 | ising_n400 | 400 | — | — | 47 | — | success | **MapFail** | — |
| 74 | ising_n420 | 420 | — | — | 50 | — | success | **MapFail** | — |
| 75 | ising_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 76 | ising_n50 | 50 | — | — | 12 | — | success | **MapFail** | — |
| 77 | ising_n60 | 60 | — | — | 11 | — | success | **MapFail** | — |
| 78 | ising_n70 | 70 | — | — | 14 | — | success | **MapFail** | — |
| 79 | ising_n80 | 80 | — | — | 14 | — | success | **MapFail** | — |
| 80 | ising_n90 | 90 | — | — | 16 | — | success | **MapFail** | — |
| 81 | multiplier_n100 | 100 | — | — | — | — | failed | **MapFail** | — |
| 82 | multiplier_n15 | 9 | — | — | 12 | — | success | **MapFail** | — |
| 83 | multiplier_n20 | 20 | 11×11 | 3990 | 3993 | 1.0008 | success | **WIN** | noi +veloci |
| 84 | multiplier_n200 | 200 | — | — | — | — | failed | **MapFail** | — |
| 85 | multiplier_n300 | 300 | — | — | — | — | failed | **MapFail** | — |
| 86 | multiplier_n40 | 40 | 17×17 | 17329 | 17329 | 1.0000 | success | = | noi +veloci |
| 87 | multiplier_n400 | 400 | — | — | — | — | failed | **MapFail** | — |
| 88 | multiplier_n45 | 27 | 13×13 | 36 | 36 | 1.0000 | success | = | noi +veloci |
| 89 | multiplier_n60 | 60 | — | — | 39730 | — | success | **MapFail** | — |
| 90 | multiplier_n75 | 45 | 17×17 | 60 | 60 | 1.0000 | success | = | noi +veloci |
| 91 | multiplier_n80 | 80 | — | — | 71287 | — | success | **MapFail** | — |
| 92 | multiply_n13 | 6 | 5×5 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 93 | parallel | 8 | 5×5 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 94 | parallel_big | 20 | 9×9 | 8 | 14 | 1.7500 | success | **WIN** | noi +veloci |
| 95 | qaoa_n10 | 10 | — | — | 48 | — | success | **MapFail** | — |
| 96 | qaoa_n100 | 100 | — | — | 1167 | — | success | **MapFail** | — |
| 97 | qaoa_n125 | 125 | — | — | 1649 | — | success | **MapFail** | — |
| 98 | qaoa_n150 | 150 | — | — | 2173 | — | success | **MapFail** | — |
| 99 | qaoa_n175 | 175 | — | — | 2812 | — | success | **MapFail** | — |
| 100 | qaoa_n20 | 20 | — | — | 109 | — | success | **MapFail** | — |
| 101 | qaoa_n200 | 200 | — | — | 3591 | — | success | **MapFail** | — |
| 102 | qaoa_n30 | 30 | — | — | 181 | — | success | **MapFail** | — |
| 103 | qaoa_n300 | 300 | — | — | 7173 | — | success | **MapFail** | — |
| 104 | qaoa_n40 | 40 | — | — | 276 | — | success | **MapFail** | — |
| 105 | qaoa_n400 | 400 | — | — | — | — | failed | **MapFail** | — |
| 106 | qaoa_n5 | 5 | 5×5 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 107 | qaoa_n50 | 50 | — | — | 371 | — | success | **MapFail** | — |
| 108 | qaoa_n6 | 6 | 5×5 | 33 | 36 | 1.0909 | success | **WIN** | noi +veloci |
| 109 | qaoa_n60 | 60 | — | — | 511 | — | success | **MapFail** | — |
| 110 | qaoa_n64 | 64 | — | — | 582 | — | success | **MapFail** | — |
| 111 | qaoa_n6_transpiled | 6 | 5×5 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 112 | qaoa_n70 | 70 | — | — | 639 | — | success | **MapFail** | — |
| 113 | qaoa_n80 | 80 | — | — | 790 | — | success | **MapFail** | — |
| 114 | qaoa_n90 | 90 | — | — | 958 | — | success | **MapFail** | — |
| 115 | qec_en_n5 | 5 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 116 | qft_20 | 20 | — | — | 113 | — | success | **MapFail** | — |
| 117 | qft_n10 | 10 | — | — | 45 | — | success | **MapFail** | — |
| 118 | qft_n100 | 100 | — | — | 591 | — | success | **MapFail** | — |
| 119 | qft_n125 | 125 | — | — | 672 | — | success | **MapFail** | — |
| 120 | qft_n128 | 128 | — | — | 697 | — | success | **MapFail** | — |
| 121 | qft_n150 | 150 | 25×25 | 1203 | 782 | 0.6500 | success | LOSS | noi +veloci |
| 122 | qft_n175 | 175 | — | — | 898 | — | success | **MapFail** | — |
| 123 | qft_n18 | 18 | — | — | 100 | — | success | **MapFail** | — |
| 124 | qft_n20 | 20 | — | — | 110 | — | success | **MapFail** | — |
| 125 | qft_n200 | 200 | 29×29 | 1587 | 982 | 0.6188 | success | LOSS | noi +veloci |
| 126 | qft_n30 | 30 | — | — | 192 | — | success | **MapFail** | — |
| 127 | qft_n300 | 300 | — | — | 1389 | — | success | **MapFail** | — |
| 128 | qft_n320 | 320 | — | — | — | — | failed | **MapFail** | — |
| 129 | qft_n40 | 40 | — | — | 244 | — | success | **MapFail** | — |
| 130 | qft_n400 | 400 | — | — | 1869 | — | success | **MapFail** | — |
| 131 | qft_n5 | 5 | 5×5 | 16 | 14 | 0.8750 | success | LOSS | noi +veloci |
| 132 | qft_n50 | 50 | — | — | 308 | — | success | **MapFail** | — |
| 133 | qft_n60 | 60 | — | — | 368 | — | success | **MapFail** | — |
| 134 | qft_n64 | 64 | — | — | 407 | — | success | **MapFail** | — |
| 135 | qft_n70 | 70 | — | — | 424 | — | success | **MapFail** | — |
| 136 | qft_n80 | 80 | — | — | 473 | — | success | **MapFail** | — |
| 137 | qft_n90 | 90 | — | — | 528 | — | success | **MapFail** | — |
| 138 | qpe_n9_transpiled | 9 | — | — | 42 | — | success | **MapFail** | — |
| 139 | qram_n20 | 9 | 5×5 | 10 | 9 | 0.9000 | success | LOSS | noi +veloci |
| 140 | randomcircuit_n100 | 100 | — | — | 4911 | — | success | **MapFail** | — |
| 141 | randomcircuit_n200 | 200 | — | — | — | — | failed | **MapFail** | — |
| 142 | randomcircuit_n50 | 50 | — | — | 1445 | — | success | **MapFail** | — |
| 143 | seca_n11 | 11 | — | — | 19 | — | success | **MapFail** | — |
| 144 | simon_n6 | 3 | — | — | 2 | — | success | **MapFail** | — |
| 145 | square_root_n18 | 14 | — | — | 27 | — | success | **MapFail** | — |
| 146 | square_root_n45 | 32 | — | — | 571 | — | success | **MapFail** | — |
| 147 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | — | — | 167 | — | success | **MapFail** | — |
| 148 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | — | — | 168 | — | success | **MapFail** | — |
| 149 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | — | — | 217 | — | success | **MapFail** | — |
| 150 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | — | — | 215 | — | success | **MapFail** | — |
| 151 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | — | — | 232 | — | success | **MapFail** | — |
| 152 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | — | — | 235 | — | success | **MapFail** | — |
| 153 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | — | — | 430 | — | success | **MapFail** | — |
| 154 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | — | — | 449 | — | success | **MapFail** | — |
| 155 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | — | — | 460 | — | success | **MapFail** | — |
| 156 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | — | — | 455 | — | success | **MapFail** | — |
| 157 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | — | — | 519 | — | success | **MapFail** | — |
| 158 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | — | — | 498 | — | success | **MapFail** | — |
| 159 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | — | — | 367 | — | success | **MapFail** | — |
| 160 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | — | — | 424 | — | success | **MapFail** | — |
| 161 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | — | — | 601 | — | success | **MapFail** | — |
| 162 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | — | — | 607 | — | success | **MapFail** | — |
| 163 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | — | — | 700 | — | success | **MapFail** | — |
| 164 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | — | — | 670 | — | success | **MapFail** | — |
| 165 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | — | — | 1284 | — | success | **MapFail** | — |
| 166 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | — | — | 1288 | — | success | **MapFail** | — |
| 167 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | — | — | 1429 | — | success | **MapFail** | — |
| 168 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | — | — | 1336 | — | success | **MapFail** | — |
| 169 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | — | — | 1577 | — | success | **MapFail** | — |
| 170 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | — | — | 1574 | — | success | **MapFail** | — |
| 171 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 84 | 61 | 0.7262 | success | LOSS | noi +veloci |
| 172 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | — | — | 60 | — | success | **MapFail** | — |
| 173 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 75 | 70 | 0.9333 | success | LOSS | noi +veloci |
| 174 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 78 | 75 | 0.9615 | success | LOSS | noi +veloci |
| 175 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | — | — | 68 | — | success | **MapFail** | — |
| 176 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 76 | 71 | 0.9342 | success | LOSS | noi +veloci |
| 177 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 119 | 108 | 0.9076 | success | LOSS | noi +veloci |
| 178 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 155 | 133 | 0.8581 | success | LOSS | noi +veloci |
| 179 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 149 | 139 | 0.9329 | success | LOSS | noi +veloci |
| 180 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | — | — | 162 | — | success | **MapFail** | — |
| 181 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 169 | 151 | 0.8935 | success | LOSS | noi +veloci |
| 182 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 157 | 148 | 0.9427 | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 155 | 146 | 0.9419 | success | LOSS | noi +veloci |
| 184 | t_test | 8 | — | — | 110 | — | success | **MapFail** | — |
| 185 | toffoli_n3 | 3 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 186 | vqe_real_amp_n10 | 10 | — | — | 15 | — | success | **MapFail** | — |
| 187 | vqe_real_amp_n100 | 100 | — | — | 103 | — | success | **MapFail** | — |
| 188 | vqe_real_amp_n125 | 125 | — | — | 128 | — | success | **MapFail** | — |
| 189 | vqe_real_amp_n150 | 150 | — | — | 153 | — | success | **MapFail** | — |
| 190 | vqe_real_amp_n175 | 175 | — | — | 178 | — | success | **MapFail** | — |
| 191 | vqe_real_amp_n20 | 20 | 9×9 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 192 | vqe_real_amp_n200 | 200 | 29×29 | 206 | 203 | 0.9854 | success | LOSS | noi +veloci |
| 193 | vqe_real_amp_n30 | 30 | — | — | 33 | — | success | **MapFail** | — |
| 194 | vqe_real_amp_n300 | 300 | — | — | 303 | — | success | **MapFail** | — |
| 195 | vqe_real_amp_n40 | 40 | 13×13 | 46 | 43 | 0.9348 | success | LOSS | noi +veloci |
| 196 | vqe_real_amp_n400 | 400 | — | — | 403 | — | success | **MapFail** | — |
| 197 | vqe_real_amp_n5 | 5 | 5×5 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 198 | vqe_real_amp_n50 | 50 | — | — | 53 | — | success | **MapFail** | — |
| 199 | vqe_real_amp_n60 | 60 | — | — | 63 | — | success | **MapFail** | — |
| 200 | vqe_real_amp_n70 | 70 | — | — | 73 | — | success | **MapFail** | — |
| 201 | vqe_real_amp_n80 | 80 | — | — | 83 | — | success | **MapFail** | — |
| 202 | vqe_real_amp_n90 | 90 | — | — | 93 | — | success | **MapFail** | — |
| 203 | vqe_su2_n10 | 10 | — | — | 13 | — | success | **MapFail** | — |
| 204 | vqe_su2_n100 | 100 | — | — | 103 | — | success | **MapFail** | — |
| 205 | vqe_su2_n125 | 125 | — | — | 128 | — | success | **MapFail** | — |
| 206 | vqe_su2_n150 | 150 | — | — | 153 | — | success | **MapFail** | — |
| 207 | vqe_su2_n175 | 175 | — | — | 178 | — | success | **MapFail** | — |
| 208 | vqe_su2_n20 | 20 | 9×9 | 23 | 25 | 1.0870 | success | **WIN** | noi +veloci |
| 209 | vqe_su2_n200 | 200 | 29×29 | 206 | 203 | 0.9854 | success | LOSS | noi +veloci |
| 210 | vqe_su2_n30 | 30 | — | — | 33 | — | success | **MapFail** | — |
| 211 | vqe_su2_n300 | 300 | — | — | 303 | — | success | **MapFail** | — |
| 212 | vqe_su2_n40 | 40 | 13×13 | 46 | 45 | 0.9783 | success | LOSS | noi +veloci |
| 213 | vqe_su2_n400 | 400 | — | — | 403 | — | success | **MapFail** | — |
| 214 | vqe_su2_n5 | 5 | 5×5 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 215 | vqe_su2_n50 | 50 | — | — | 53 | — | success | **MapFail** | — |
| 216 | vqe_su2_n60 | 60 | — | — | 63 | — | success | **MapFail** | — |
| 217 | vqe_su2_n70 | 70 | — | — | 73 | — | success | **MapFail** | — |
| 218 | vqe_su2_n80 | 80 | — | — | 83 | — | success | **MapFail** | — |
| 219 | vqe_su2_n90 | 90 | — | — | 93 | — | success | **MapFail** | — |
| 220 | vqe_two_local_n10 | 10 | — | — | 55 | — | success | **MapFail** | — |
| 221 | vqe_two_local_n100 | 100 | — | — | 1891 | — | success | **MapFail** | — |
| 222 | vqe_two_local_n125 | 125 | — | — | 2600 | — | success | **MapFail** | — |
| 223 | vqe_two_local_n150 | 150 | — | — | 3568 | — | success | **MapFail** | — |
| 224 | vqe_two_local_n175 | 175 | — | — | 4556 | — | success | **MapFail** | — |
| 225 | vqe_two_local_n20 | 20 | — | — | 157 | — | success | **MapFail** | — |
| 226 | vqe_two_local_n200 | 200 | — | — | 5626 | — | success | **MapFail** | — |
| 227 | vqe_two_local_n30 | 30 | — | — | 272 | — | success | **MapFail** | — |
| 228 | vqe_two_local_n300 | 300 | — | — | — | — | failed | **MapFail** | — |
| 229 | vqe_two_local_n40 | 40 | — | — | 413 | — | success | **MapFail** | — |
| 230 | vqe_two_local_n400 | 400 | — | — | — | — | failed | **MapFail** | — |
| 231 | vqe_two_local_n5 | 5 | 5×5 | 20 | 17 | 0.8500 | success | LOSS | noi +veloci |
| 232 | vqe_two_local_n50 | 50 | — | — | 576 | — | success | **MapFail** | — |
| 233 | vqe_two_local_n60 | 60 | — | — | 805 | — | success | **MapFail** | — |
| 234 | vqe_two_local_n70 | 70 | — | — | 1011 | — | success | **MapFail** | — |
| 235 | vqe_two_local_n80 | 80 | — | — | 1349 | — | success | **MapFail** | — |
| 236 | vqe_two_local_n90 | 90 | — | — | 1558 | — | success | **MapFail** | — |
| 237 | vqe_uccsd_n4 | 4 | — | — | 88 | — | success | **MapFail** | — |
| 238 | vqe_uccsd_n8 | 8 | 5×5 | 5447 | 5446 | 0.9998 | success | LOSS | noi +veloci |
| 239 | wstate_n10 | 10 | — | — | 11 | — | success | **MapFail** | — |
| 240 | wstate_n100 | 100 | — | — | 101 | — | success | **MapFail** | — |
| 241 | wstate_n125 | 125 | — | — | 126 | — | success | **MapFail** | — |
| 242 | wstate_n150 | 150 | — | — | 151 | — | success | **MapFail** | — |
| 243 | wstate_n175 | 175 | — | — | 176 | — | success | **MapFail** | — |
| 244 | wstate_n20 | 20 | 9×9 | 21 | 21 | 1.0000 | success | = | noi +veloci |
| 245 | wstate_n200 | 200 | 29×29 | 203 | 201 | 0.9901 | success | LOSS | noi +veloci |
| 246 | wstate_n27 | 27 | — | — | 28 | — | success | **MapFail** | — |
| 247 | wstate_n30 | 30 | — | — | 31 | — | success | **MapFail** | — |
| 248 | wstate_n300 | 300 | — | — | 301 | — | success | **MapFail** | — |
| 249 | wstate_n40 | 40 | 13×13 | 42 | 41 | 0.9762 | success | LOSS | noi +veloci |
| 250 | wstate_n400 | 400 | — | — | 401 | — | success | **MapFail** | — |
| 251 | wstate_n5 | 5 | 5×5 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 252 | wstate_n50 | 50 | — | — | 51 | — | success | **MapFail** | — |
| 253 | wstate_n60 | 60 | — | — | 61 | — | success | **MapFail** | — |
| 254 | wstate_n70 | 70 | — | — | 71 | — | success | **MapFail** | — |
| 255 | wstate_n80 | 80 | — | — | 81 | — | success | **MapFail** | — |
| 256 | wstate_n90 | 90 | — | — | 91 | — | success | **MapFail** | — |
