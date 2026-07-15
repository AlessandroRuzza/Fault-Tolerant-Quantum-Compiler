# Gauss vs Random — solo placement (connectivity + naive_critical, same-grid)


Confronto **same-grid** sulla griglia **wisqmin** (la minima su cui il baseline instrada). Entrambi i lati sono prodotti dal NOSTRO compilatore con `safe_passage=connectivity` e router `naive_critical`: cambia **solo il placement**. **noi** = placement gaussiano (le esecuzioni del .md `A_wisqmin_connectivity_naive_critical.md`); la colonna **random** = placement casuale (`random_at_wisqmin_grid_ours.csv`). Griglia identica per-circuito (verificato). `random` in *timeout* = il placement casuale non riesce a mappare. Metrica primaria: routing steps (meno è meglio).


Dati da: `gauss_vs_random_sidebyside.csv` — **256 circuiti**.


---


## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| ↳ random va in timeout (noi vinciamo) | 13 | — |
| ↳ Entrambi completano | 243 | — |
|   ↳ Noi vinciamo su steps | 184 (ratio mediana 1.14×) | 61 (33.2%) |
|   ↳ Pareggio su steps | 43 | 30 (69.8%) |
|   ↳ random vince su steps | 16 (ratio mediana 0.83×) | 4 (25.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **227 / 256 (88.7%)** | — |
| ↳ Noi completiamo, random va in timeout | 13 / 256 (5.1%) | — |
| ↳ Noi vinciamo su steps (random completa) | 184 / 256 (71.9%) | — |
| ↳ Pareggio su steps, noi più veloci | 30 / 256 (11.7%) | — |

---


## Routing steps in aggregato (nostro vs random)

Sui 243 circuiti dove **entrambi completano**:

| Metrica | Valore |
|---------|--------|
| Somma `my_routing_steps` | 4.819.915 |
| Somma `wisq_routing_steps` | 4.825.530 |
| **Rapporto dei totali (wisq / nostro)** | **1.00 → random usa 0.1% di steps in più** |
| Mediana di `ratio_wisq_over_mine` | 1.09 |
| Media di `ratio_wisq_over_mine` | 1.664 |

---


## Densità dei circuiti: dove vinciamo vs dove perdiamo

`cnot_interaction_density` = coppie-qubit CNOT distinte / coppie possibili `Q·(Q−1)/2` (0 = sparso/locale, 1 = ogni coppia interagisce). Calcolata dal QASM universale su 243/243 circuiti both-complete con QASM disponibile.

**Per esito sugli steps:**

| Esito (steps) | N | densità media | mediana | min | max |
|---|---|---|---|---|---|
| **Vinciamo** (WIN) | 184 | 0.311 | 0.200 | 0.005 | 1.000 |
| Pareggio (TIE) | 43 | 0.240 | 0.087 | 0.005 | 1.000 |
| **Perdiamo** (LOSS) | 16 | 0.352 | 0.292 | 0.098 | 1.000 |

**Win/Loss per fascia di densità** (sugli steps, both-complete):

| Densità `cid` | N | Win | Tie | Loss | Loss-rate (decisi) |
|---|---|---|---|---|---|
| < 0.15 | 115 | 87 | 26 | 2 | 2.2% |
| 0.15 – 0.40 | 38 | 24 | 5 | 9 | 27.3% |
| ≥ 0.40 | 90 | 73 | 12 | 5 | 6.4% |

---


## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **random non finisce in 1 ora** | 13 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 13 | — |
| **Entrambi finiscono in 1 ora** | 243 | — |
| ↳ Noi vinciamo su steps | 184 (ratio mediana 1.14×) | 61 (33.2%) |
| ↳ Pareggio su steps | 43 | 30 (69.8%) |
| ↳ random vince su steps | 16 (ratio mediana 0.83×) | 4 (25.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **227 / 256 (88.7%)** | — |

---


## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **random non finisce in 30 minuti** | 13 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 13 | — |
| **Entrambi finiscono in 30 minuti** | 243 | — |
| ↳ Noi vinciamo su steps | 184 (ratio mediana 1.14×) | 61 (33.2%) |
| ↳ Pareggio su steps | 43 | 30 (69.8%) |
| ↳ random vince su steps | 16 (ratio mediana 0.83×) | 4 (25.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **227 / 256 (88.7%)** | — |

---


## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **random non finisce in 15 minuti** | 13 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 13 | — |
| **Entrambi finiscono in 15 minuti** | 243 | — |
| ↳ Noi vinciamo su steps | 184 (ratio mediana 1.14×) | 61 (33.2%) |
| ↳ Pareggio su steps | 43 | 30 (69.8%) |
| ↳ random vince su steps | 16 (ratio mediana 0.83×) | 4 (25.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **227 / 256 (88.7%)** | — |

---


## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **random non finisce in 10 minuti** | 13 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 0 | — |
| ↳ …noi finiamo → **vittoria** | 13 | — |
| **Noi non finiamo, random sì → sconfitta** | 2 | — |
| **Entrambi finiscono in 10 minuti** | 241 | — |
| ↳ Noi vinciamo su steps | 182 (ratio mediana 1.14×) | 61 (33.5%) |
| ↳ Pareggio su steps | 43 | 30 (69.8%) |
| ↳ random vince su steps | 16 (ratio mediana 0.83×) | 4 (25.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **225 / 256 (87.9%)** | — |

---


## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **random non finisce in 5 minuti** | 23 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 1 | — |
| ↳ …noi finiamo → **vittoria** | 22 | — |
| **Noi non finiamo, random sì → sconfitta** | 2 | — |
| **Entrambi finiscono in 5 minuti** | 231 | — |
| ↳ Noi vinciamo su steps | 176 (ratio mediana 1.14×) | 55 (31.2%) |
| ↳ Pareggio su steps | 39 | 26 (66.7%) |
| ↳ random vince su steps | 16 (ratio mediana 0.83×) | 4 (25.0%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **224 / 256 (87.5%)** | — |

---


## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Timeout imposto simmetricamente: conta solo chi finisce entro il budget.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti analizzati** | 256 | — |
| **random non finisce in 1 minuto** | 41 | — |
| ↳ …ma anche noi sforiamo → nessun vincitore | 2 | — |
| ↳ …noi finiamo → **vittoria** | 39 | — |
| **Noi non finiamo, random sì → sconfitta** | 9 | — |
| **Entrambi finiscono in 1 minuto** | 206 | — |
| ↳ Noi vinciamo su steps | 159 (ratio mediana 1.14×) | 43 (27.0%) |
| ↳ Pareggio su steps | 35 | 23 (65.7%) |
| ↳ random vince su steps | 12 (ratio mediana 0.56×) | 2 (16.7%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **221 / 256 (86.3%)** | — |

---


## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | random timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (orig., asimm.) | 243 | 13 | 0 | 0 | **227 (88.7%)** |
| 1 ora | 243 | 13 | 0 | 0 | **227 (88.7%)** ⟵ picco |
| 30 minuti | 243 | 13 | 0 | 0 | **227 (88.7%)** |
| 15 minuti | 243 | 13 | 0 | 0 | **227 (88.7%)** |
| 10 minuti | 241 | 13 | 2 | 0 | **225 (87.9%)** |
| 5 minuti | 231 | 22 | 2 | 1 | **224 (87.5%)** |
| 1 minuto | 206 | 39 | 9 | 2 | **221 (86.3%)** |

---


## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s`. Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). I timeout random sono inclusi con la durata registrata.

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout random)** | 243 | 95 (39.1%) | 1× | 972× | 0.00× | 30927× |
| ↳ Dove vinciamo su steps | 184 | 61 (33.2%) | 1× | 653× | 0.00× | 27833× |
| ↳ In pareggio su steps | 43 | 30 (69.8%) | 1× | 2613× | 0.00× | 30927× |
| ↳ Dove random vince su steps | 16 | 4 (25.0%) | 0× | 237× | 0.01× | 3732× |
| ↳ random in timeout | 0 | — | — | — | — | — |

---


## Buffer di steps dipendente dalla velocità — win-rate vs random

Analisi su `gauss_vs_random_sidebyside.csv`. La metrica primaria sono i **routing steps**, il tempo è secondario: concediamo un buffer ε sugli steps che cresce con l'ordine di grandezza del vantaggio di tempo.

```
vinco  se   my_steps <= wisq_steps · (1 + ε)
ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time
α = 0.05 / log10(N)      (ancora: 5% di sforo steps ⇄ N× di velocità)
```

Baseline (steps primario, tempo solo spareggio) = **227/256 = 88.7%**.

| ancora | α | loss recuperati | vittorie | % |
|---|---:|---:|---:|---:|
| 5% ⇄ 20× | 0.0384 | 2 | 229 | 89.5% |
| 5% ⇄ 50× | 0.0294 | 2 | 229 | 89.5% |
| 5% ⇄ 100× | 0.0250 | 2 | 229 | 89.5% |
| 5% ⇄ 150× | 0.0230 | 2 | 229 | 89.5% |
| 5% ⇄ 200× | 0.0217 | 2 | 229 | 89.5% |
| 5% ⇄ 300× | 0.0202 | 2 | 229 | 89.5% |
| 5% ⇄ 400× | 0.0192 | 2 | 229 | 89.5% |
| 5% ⇄ 500× | 0.0185 | 2 | 229 | 89.5% |
| 5% ⇄ 750× | 0.0174 | 2 | 229 | 89.5% |
| 5% ⇄ 1000× | 0.0167 | 2 | 229 | 89.5% |
| 5% ⇄ 1500× | 0.0157 | 2 | 229 | 89.5% |
| 5% ⇄ 2000× | 0.0151 | 2 | 229 | 89.5% |
| 5% ⇄ 2500× | 0.0147 | 2 | 229 | 89.5% |
| 5% ⇄ 3000× | 0.0144 | 2 | 229 | 89.5% |
| 5% ⇄ 4000× | 0.0139 | 2 | 229 | 89.5% |
| 5% ⇄ 5000× | 0.0135 | 2 | 229 | 89.5% |

---


## Per famiglia di circuiti

**random timeout** = random non ha completato. **MapFail** = il nostro mapping non riesce. Win/=/Loss sono sugli steps dove entrambi completano.

| Family | N | Win | = (noi+veloci) | Loss | random timeout | MapFail | Note |
|--------|---|-----|----------------|------|--------------|---------|------|
| 19qubits | 2 | 1 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=19 |
| 53qubits | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=27–39 |
| adder | 4 | 3 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=4–433 |
| bigadder | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=18 |
| bv | 1 | 0 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=153 |
| bwt | 4 | 4 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=21–73 |
| cat | 2 | 0 | 2 (1 noi+veloci) | 0 | 0 | 0 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| dnn | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=16 |
| factor247 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=15 |
| fredkin | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| ghz | 18 | 0 | 18 (12 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| ghz_state | 2 | 0 | 2 (1 noi+veloci) | 0 | 0 | 0 | n=23–255 |
| graphstate | 17 | 16 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| grover | 3 | 2 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=5–19 |
| hhl | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=10 |
| ising | 19 | 19 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=5–420 |
| multiplier | 11 | 8 | 0 (0 noi+veloci) | 2 | 1 | 0 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 19 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5 |
| qft | 22 | 14 | 0 (0 noi+veloci) | 8 | 0 | 0 | n=5–400 |
| qpe | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=9 |
| qram | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=9 |
| randomcircuit | 3 | 2 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=50–200 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=3 |
| square_root | 2 | 2 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=14–32 |
| synth | 37 | 27 | 0 (0 noi+veloci) | 1 | 9 | 0 | n=50–200 |
| t_test | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=8 |
| toffoli | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| vqe_real_amp | 17 | 16 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_su2 | 17 | 15 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| vqe_two_local | 17 | 16 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=5–400 |
| vqe_uccsd | 2 | 1 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=4–8 |
| wstate | 18 | 15 | 2 (0 noi+veloci) | 1 | 0 | 0 | n=5–400 |

---


## Per circuito (dettaglio)

**Steps**: WIN = noi meno routing steps, LOSS = random meno, = pareggio. **Tempo** confronta le durate quando disponibili.

| # | Circuit | Qubits | Grid | My steps | random steps | Ratio | random status | Steps | Tempo |
|---|---------|--------|------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 9×9 | 102 | 101 | 0.9902 | success | LOSS | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 9×9 | 286 | 288 | 1.0070 | success | **WIN** | random +veloce |
| 3 | 53qubits_155gate_57layers | 27 | 11×11 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 4 | 53qubits_332gate_152layers | 39 | 17×17 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 11×11 | 24 | 24 | 1.0000 | success | = | noi +veloci |
| 6 | adder_n4 | 4 | 7×7 | 8 | 9 | 1.1250 | success | **WIN** | noi +veloci |
| 7 | adder_n433 | 433 | 41×41 | 249 | 260 | 1.0442 | success | **WIN** | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 15×15 | 181 | 192 | 1.0608 | success | **WIN** | random +veloce |
| 9 | bigadder_n18_transpiled | 18 | 13×13 | 88 | 88 | 1.0000 | success | = | noi +veloci |
| 10 | bv_n280 | 153 | 33×33 | 152 | 152 | 1.0000 | success | = | random +veloce |
| 11 | bwt_n21 | 21 | 13×13 | 116400 | 116800 | 1.0034 | success | **WIN** | random +veloce |
| 12 | bwt_n37 | 28 | 15×15 | 33600 | 34198 | 1.0178 | success | **WIN** | random +veloce |
| 13 | bwt_n57 | 43 | 17×17 | 65606 | 68020 | 1.0368 | success | **WIN** | random +veloce |
| 14 | bwt_n97 | 73 | 21×21 | 129600 | 136285 | 1.0516 | success | **WIN** | noi +veloci |
| 15 | cat_n130 | 130 | 23×23 | 129 | 129 | 1.0000 | success | = | noi +veloci |
| 16 | cat_n260 | 260 | 33×33 | 259 | 259 | 1.0000 | success | = | random +veloce |
| 17 | continuous_3_17_13 | 3 | 3×3 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 18 | dnn_n16 | 16 | 7×7 | 48 | 130 | 2.7083 | success | **WIN** | noi +veloci |
| 19 | factor247_n15 | 15 | 11×11 | 349644 | 349644 | 1.0000 | success | = | noi +veloci |
| 20 | fredkin_n3 | 3 | 6×6 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 21 | ghz_n10 | 10 | 7×7 | 9 | 9 | 1.0000 | success | = | noi +veloci |
| 22 | ghz_n100 | 100 | 19×19 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 23 | ghz_n125 | 125 | 23×23 | 124 | 124 | 1.0000 | success | = | noi +veloci |
| 24 | ghz_n150 | 150 | 25×25 | 149 | 149 | 1.0000 | success | = | random +veloce |
| 25 | ghz_n175 | 175 | 27×27 | 174 | 174 | 1.0000 | success | = | random +veloce |
| 26 | ghz_n20 | 20 | 9×9 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 27 | ghz_n200 | 200 | 29×29 | 199 | 199 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | success | = | random +veloce |
| 29 | ghz_n30 | 30 | 11×11 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 30 | ghz_n300 | 300 | 35×35 | 299 | 299 | 1.0000 | success | = | random +veloce |
| 31 | ghz_n40 | 40 | 13×13 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n400 | 400 | 39×39 | 399 | 399 | 1.0000 | success | = | random +veloce |
| 33 | ghz_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 34 | ghz_n50 | 50 | 15×15 | 49 | 49 | 1.0000 | success | = | random +veloce |
| 35 | ghz_n60 | 60 | 15×15 | 59 | 59 | 1.0000 | success | = | noi +veloci |
| 36 | ghz_n70 | 70 | 17×17 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 37 | ghz_n80 | 80 | 17×17 | 79 | 79 | 1.0000 | success | = | noi +veloci |
| 38 | ghz_n90 | 90 | 19×19 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 39 | ghz_state_n23 | 23 | 9×9 | 22 | 22 | 1.0000 | success | = | noi +veloci |
| 40 | ghz_state_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | success | = | random +veloce |
| 41 | graphstate_n10 | 10 | 7×7 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 42 | graphstate_n100 | 100 | 19×19 | 8 | 17 | 2.1250 | success | **WIN** | noi +veloci |
| 43 | graphstate_n125 | 125 | 23×23 | 5 | 17 | 3.4000 | success | **WIN** | noi +veloci |
| 44 | graphstate_n150 | 150 | 25×25 | 6 | 19 | 3.1667 | success | **WIN** | noi +veloci |
| 45 | graphstate_n175 | 175 | 27×27 | 7 | 21 | 3.0000 | success | **WIN** | random +veloce |
| 46 | graphstate_n20 | 20 | 9×9 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 47 | graphstate_n200 | 200 | 29×29 | 6 | 22 | 3.6667 | success | **WIN** | random +veloce |
| 48 | graphstate_n30 | 30 | 11×11 | 6 | 7 | 1.1667 | success | **WIN** | noi +veloci |
| 49 | graphstate_n300 | 300 | 35×35 | 9 | 30 | 3.3333 | success | **WIN** | random +veloce |
| 50 | graphstate_n40 | 40 | 13×13 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 51 | graphstate_n400 | 400 | 39×39 | 7 | 34 | 4.8571 | success | **WIN** | noi +veloci |
| 52 | graphstate_n5 | 5 | 5×5 | 4 | 4 | 1.0000 | success | = | random +veloce |
| 53 | graphstate_n50 | 50 | 15×15 | 5 | 12 | 2.4000 | success | **WIN** | noi +veloci |
| 54 | graphstate_n60 | 60 | 15×15 | 5 | 14 | 2.8000 | success | **WIN** | noi +veloci |
| 55 | graphstate_n70 | 70 | 17×17 | 5 | 11 | 2.2000 | success | **WIN** | noi +veloci |
| 56 | graphstate_n80 | 80 | 17×17 | 6 | 15 | 2.5000 | success | **WIN** | random +veloce |
| 57 | graphstate_n90 | 90 | 19×19 | 5 | 16 | 3.2000 | success | **WIN** | random +veloce |
| 58 | grover_n10 | 10 | 8×8 | 11008 | 11025 | 1.0015 | success | **WIN** | noi +veloci |
| 59 | grover_n20 | 19 | 13×13 | 2146489 | 2147057 | 1.0003 | success | **WIN** | noi +veloci |
| 60 | grover_n5 | 5 | 6×6 | 209 | — | — | error | timeout | — |
| 61 | hhl_n10 | 10 | 11×11 | 72039 | 72039 | 1.0000 | success | = | noi +veloci |
| 62 | ising_n10 | 10 | 7×7 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 63 | ising_n100 | 100 | 19×19 | 4 | 30 | 7.5000 | success | **WIN** | noi +veloci |
| 64 | ising_n125 | 125 | 23×23 | 4 | 30 | 7.5000 | success | **WIN** | noi +veloci |
| 65 | ising_n150 | 150 | 25×25 | 4 | 34 | 8.5000 | success | **WIN** | random +veloce |
| 66 | ising_n175 | 175 | 27×27 | 4 | 34 | 8.5000 | success | **WIN** | random +veloce |
| 67 | ising_n20 | 20 | 9×9 | 4 | 8 | 2.0000 | success | **WIN** | random +veloce |
| 68 | ising_n200 | 200 | 29×29 | 4 | 40 | 10.0000 | success | **WIN** | random +veloce |
| 69 | ising_n26 | 26 | 11×11 | 4 | 11 | 2.7500 | success | **WIN** | random +veloce |
| 70 | ising_n30 | 30 | 11×11 | 4 | 13 | 3.2500 | success | **WIN** | noi +veloci |
| 71 | ising_n300 | 300 | 35×35 | 4 | 55 | 13.7500 | success | **WIN** | random +veloce |
| 72 | ising_n40 | 40 | 13×13 | 4 | 17 | 4.2500 | success | **WIN** | noi +veloci |
| 73 | ising_n400 | 400 | 39×39 | 4 | 60 | 15.0000 | success | **WIN** | random +veloce |
| 74 | ising_n420 | 420 | 41×41 | 4 | 65 | 16.2500 | success | **WIN** | random +veloce |
| 75 | ising_n5 | 5 | 5×5 | 6 | 8 | 1.3333 | success | **WIN** | noi +veloci |
| 76 | ising_n50 | 50 | 15×15 | 4 | 16 | 4.0000 | success | **WIN** | random +veloce |
| 77 | ising_n60 | 60 | 15×15 | 4 | 22 | 5.5000 | success | **WIN** | noi +veloci |
| 78 | ising_n70 | 70 | 17×17 | 4 | 19 | 4.7500 | success | **WIN** | noi +veloci |
| 79 | ising_n80 | 80 | 17×17 | 4 | 29 | 7.2500 | success | **WIN** | noi +veloci |
| 80 | ising_n90 | 90 | 19×19 | 4 | 28 | 7.0000 | success | **WIN** | random +veloce |
| 81 | multiplier_n100 | 100 | 23×23 | 111762 | 111814 | 1.0005 | success | **WIN** | random +veloce |
| 82 | multiplier_n15 | 9 | 5×5 | 13 | 12 | 0.9231 | success | LOSS | noi +veloci |
| 83 | multiplier_n20 | 20 | 11×11 | 3990 | 4001 | 1.0028 | success | **WIN** | random +veloce |
| 84 | multiplier_n200 | 200 | 33×33 | 450021 | 450014 | 1.0000 | success | LOSS | random +veloce |
| 85 | multiplier_n300 | 300 | 39×39 | 1013834 | 1013996 | 1.0002 | success | **WIN** | random +veloce |
| 86 | multiplier_n40 | 40 | 17×17 | 17329 | 17339 | 1.0006 | success | **WIN** | noi +veloci |
| 87 | multiplier_n400 | 400 | 43×43 | 1812187 | — | — | error | timeout | — |
| 88 | multiplier_n45 | 27 | 13×13 | 36 | 78 | 2.1667 | success | **WIN** | noi +veloci |
| 89 | multiplier_n60 | 60 | 19×19 | 39730 | 39754 | 1.0006 | success | **WIN** | random +veloce |
| 90 | multiplier_n75 | 45 | 17×17 | 60 | 149 | 2.4833 | success | **WIN** | noi +veloci |
| 91 | multiplier_n80 | 80 | 21×21 | 71287 | 71314 | 1.0004 | success | **WIN** | random +veloce |
| 92 | multiply_n13 | 6 | 5×5 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 93 | parallel | 8 | 5×5 | 10 | 15 | 1.5000 | success | **WIN** | noi +veloci |
| 94 | parallel_big | 20 | 9×9 | 8 | 24 | 3.0000 | success | **WIN** | noi +veloci |
| 95 | qaoa_n10 | 10 | 7×7 | 46 | 54 | 1.1739 | success | **WIN** | noi +veloci |
| 96 | qaoa_n100 | 100 | 19×19 | 1691 | 1808 | 1.0692 | success | **WIN** | random +veloce |
| 97 | qaoa_n125 | 125 | 23×23 | 2071 | 2488 | 1.2014 | success | **WIN** | random +veloce |
| 98 | qaoa_n150 | 150 | 25×25 | 2754 | 3247 | 1.1790 | success | **WIN** | random +veloce |
| 99 | qaoa_n175 | 175 | 27×27 | 3602 | 4255 | 1.1813 | success | **WIN** | random +veloce |
| 100 | qaoa_n20 | 20 | 9×9 | 109 | 140 | 1.2844 | success | **WIN** | noi +veloci |
| 101 | qaoa_n200 | 200 | 29×29 | 4537 | 5162 | 1.1378 | success | **WIN** | random +veloce |
| 102 | qaoa_n30 | 30 | 11×11 | 191 | 256 | 1.3403 | success | **WIN** | random +veloce |
| 103 | qaoa_n300 | 300 | 35×35 | 8960 | 9772 | 1.0906 | success | **WIN** | random +veloce |
| 104 | qaoa_n40 | 40 | 13×13 | 310 | 385 | 1.2419 | success | **WIN** | random +veloce |
| 105 | qaoa_n400 | 400 | 43×43 | 13750 | 15261 | 1.1099 | success | **WIN** | random +veloce |
| 106 | qaoa_n5 | 5 | 5×5 | 18 | 20 | 1.1111 | success | **WIN** | noi +veloci |
| 107 | qaoa_n50 | 50 | 15×15 | 451 | 576 | 1.2772 | success | **WIN** | random +veloce |
| 108 | qaoa_n6 | 6 | 5×5 | 36 | 51 | 1.4167 | success | **WIN** | noi +veloci |
| 109 | qaoa_n60 | 60 | 15×15 | 715 | 763 | 1.0671 | success | **WIN** | random +veloce |
| 110 | qaoa_n64 | 64 | 15×15 | 895 | 860 | 0.9609 | success | LOSS | random +veloce |
| 111 | qaoa_n6_transpiled | 6 | 5×5 | 36 | 38 | 1.0556 | success | **WIN** | random +veloce |
| 112 | qaoa_n70 | 70 | 17×17 | 799 | 994 | 1.2441 | success | **WIN** | random +veloce |
| 113 | qaoa_n80 | 80 | 17×17 | 1108 | 1207 | 1.0894 | success | **WIN** | random +veloce |
| 114 | qaoa_n90 | 90 | 19×19 | 1229 | 1456 | 1.1847 | success | **WIN** | random +veloce |
| 115 | qec_en_n5 | 5 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 116 | qft_20 | 20 | 9×9 | 103 | 126 | 1.2233 | success | **WIN** | random +veloce |
| 117 | qft_n10 | 10 | 7×7 | 37 | 43 | 1.1622 | success | **WIN** | noi +veloci |
| 118 | qft_n100 | 100 | 19×19 | 767 | 762 | 0.9935 | success | LOSS | noi +veloci |
| 119 | qft_n125 | 125 | 23×23 | 2639 | 866 | 0.3282 | success | LOSS | random +veloce |
| 120 | qft_n128 | 128 | 23×23 | 2708 | 871 | 0.3216 | success | LOSS | random +veloce |
| 121 | qft_n150 | 150 | 25×25 | 3150 | 1014 | 0.3219 | success | LOSS | random +veloce |
| 122 | qft_n175 | 175 | 27×27 | 3774 | 1150 | 0.3047 | success | LOSS | random +veloce |
| 123 | qft_n18 | 18 | 9×9 | 78 | 111 | 1.4231 | success | **WIN** | noi +veloci |
| 124 | qft_n20 | 20 | 9×9 | 102 | 140 | 1.3725 | success | **WIN** | random +veloce |
| 125 | qft_n200 | 200 | 29×29 | 4295 | 1315 | 0.3062 | success | LOSS | random +veloce |
| 126 | qft_n30 | 30 | 11×11 | 178 | 213 | 1.1966 | success | **WIN** | random +veloce |
| 127 | qft_n300 | 300 | 35×35 | 6557 | 1789 | 0.2728 | success | LOSS | random +veloce |
| 128 | qft_n320 | 320 | 39×39 | 8346 | 8882 | 1.0642 | success | **WIN** | random +veloce |
| 129 | qft_n40 | 40 | 13×13 | 277 | 306 | 1.1047 | success | **WIN** | random +veloce |
| 130 | qft_n400 | 400 | 39×39 | 9181 | 2332 | 0.2540 | success | LOSS | random +veloce |
| 131 | qft_n5 | 5 | 5×5 | 14 | 16 | 1.1429 | success | **WIN** | noi +veloci |
| 132 | qft_n50 | 50 | 15×15 | 285 | 379 | 1.3298 | success | **WIN** | noi +veloci |
| 133 | qft_n60 | 60 | 15×15 | 414 | 450 | 1.0870 | success | **WIN** | random +veloce |
| 134 | qft_n64 | 64 | 15×15 | 479 | 484 | 1.0104 | success | **WIN** | random +veloce |
| 135 | qft_n70 | 70 | 17×17 | 438 | 516 | 1.1781 | success | **WIN** | random +veloce |
| 136 | qft_n80 | 80 | 17×17 | 562 | 609 | 1.0836 | success | **WIN** | random +veloce |
| 137 | qft_n90 | 90 | 19×19 | 598 | 662 | 1.1070 | success | **WIN** | random +veloce |
| 138 | qpe_n9_transpiled | 9 | 5×5 | 42 | 42 | 1.0000 | success | = | noi +veloci |
| 139 | qram_n20 | 9 | 5×5 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 140 | randomcircuit_n100 | 100 | 22×22 | 6063 | — | — | error | timeout | — |
| 141 | randomcircuit_n200 | 200 | 33×33 | 17552 | 19123 | 1.0895 | success | **WIN** | random +veloce |
| 142 | randomcircuit_n50 | 50 | 19×19 | 1632 | 1936 | 1.1863 | success | **WIN** | random +veloce |
| 143 | seca_n11 | 11 | 7×7 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 144 | simon_n6 | 3 | 3×3 | 2 | 2 | 1.0000 | success | = | random +veloce |
| 145 | square_root_n18 | 14 | 7×7 | 27 | 61 | 2.2593 | success | **WIN** | noi +veloci |
| 146 | square_root_n45 | 32 | 11×11 | 570 | 1707 | 2.9947 | success | **WIN** | noi +veloci |
| 147 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 288 | 373 | 1.2951 | success | **WIN** | random +veloce |
| 148 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 421 | 371 | 0.8812 | success | LOSS | random +veloce |
| 149 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 328 | 363 | 1.1067 | success | **WIN** | random +veloce |
| 150 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 22×22 | 306 | — | — | error | timeout | — |
| 151 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 327 | 362 | 1.1070 | success | **WIN** | random +veloce |
| 152 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 22×22 | 319 | — | — | error | timeout | — |
| 153 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 617 | 714 | 1.1572 | success | **WIN** | random +veloce |
| 154 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 624 | 735 | 1.1779 | success | **WIN** | random +veloce |
| 155 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 640 | 698 | 1.0906 | success | **WIN** | random +veloce |
| 156 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 644 | 717 | 1.1134 | success | **WIN** | random +veloce |
| 157 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 21×21 | 665 | 718 | 1.0797 | success | **WIN** | random +veloce |
| 158 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 21×21 | 654 | 705 | 1.0780 | success | **WIN** | noi +veloci |
| 159 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 817 | 993 | 1.2154 | success | **WIN** | random +veloce |
| 160 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 32×32 | 880 | 984 | 1.1182 | success | **WIN** | noi +veloci |
| 161 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 926 | 936 | 1.0108 | success | **WIN** | random +veloce |
| 162 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 877 | 942 | 1.0741 | success | **WIN** | random +veloce |
| 163 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 31×31 | 1626 | — | — | error | timeout | — |
| 164 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 949 | 965 | 1.0169 | success | **WIN** | random +veloce |
| 165 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 2023 | — | — | error | timeout | — |
| 166 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 29×29 | 2430 | — | — | error | timeout | — |
| 167 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 2029 | — | — | error | timeout | — |
| 168 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 30×30 | 2067 | — | — | error | timeout | — |
| 169 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 29×29 | 5597 | — | — | error | timeout | — |
| 170 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 29×29 | 2298 | — | — | error | timeout | — |
| 171 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 77 | 97 | 1.2597 | success | **WIN** | random +veloce |
| 172 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 18×18 | 70 | 103 | 1.4714 | success | **WIN** | random +veloce |
| 173 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 81 | 98 | 1.2099 | success | **WIN** | random +veloce |
| 174 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 84 | 111 | 1.3214 | success | **WIN** | random +veloce |
| 175 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 87 | 98 | 1.1264 | success | **WIN** | random +veloce |
| 176 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 81 | 102 | 1.2593 | success | **WIN** | random +veloce |
| 177 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 123 | 163 | 1.3252 | success | **WIN** | noi +veloci |
| 178 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 156 | 200 | 1.2821 | success | **WIN** | random +veloce |
| 179 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 155 | 207 | 1.3355 | success | **WIN** | random +veloce |
| 180 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 18×18 | 166 | 215 | 1.2952 | success | **WIN** | random +veloce |
| 181 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 169 | 204 | 1.2071 | success | **WIN** | random +veloce |
| 182 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 159 | 214 | 1.3459 | success | **WIN** | random +veloce |
| 183 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 155 | 195 | 1.2581 | success | **WIN** | random +veloce |
| 184 | t_test | 8 | 5×5 | 140 | — | — | error | timeout | — |
| 185 | toffoli_n3 | 3 | 5×5 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 186 | vqe_real_amp_n10 | 10 | 7×7 | 13 | 14 | 1.0769 | success | **WIN** | noi +veloci |
| 187 | vqe_real_amp_n100 | 100 | 19×19 | 103 | 111 | 1.0777 | success | **WIN** | random +veloce |
| 188 | vqe_real_amp_n125 | 125 | 23×23 | 128 | 132 | 1.0312 | success | **WIN** | noi +veloci |
| 189 | vqe_real_amp_n150 | 150 | 25×25 | 153 | 160 | 1.0458 | success | **WIN** | random +veloce |
| 190 | vqe_real_amp_n175 | 175 | 27×27 | 178 | 182 | 1.0225 | success | **WIN** | random +veloce |
| 191 | vqe_real_amp_n20 | 20 | 9×9 | 23 | 27 | 1.1739 | success | **WIN** | noi +veloci |
| 192 | vqe_real_amp_n200 | 200 | 29×29 | 203 | 208 | 1.0246 | success | **WIN** | random +veloce |
| 193 | vqe_real_amp_n30 | 30 | 11×11 | 33 | 35 | 1.0606 | success | **WIN** | random +veloce |
| 194 | vqe_real_amp_n300 | 300 | 35×35 | 303 | 314 | 1.0363 | success | **WIN** | noi +veloci |
| 195 | vqe_real_amp_n40 | 40 | 13×13 | 43 | 48 | 1.1163 | success | **WIN** | random +veloce |
| 196 | vqe_real_amp_n400 | 400 | 39×39 | 403 | 409 | 1.0149 | success | **WIN** | random +veloce |
| 197 | vqe_real_amp_n5 | 5 | 5×5 | 10 | 8 | 0.8000 | success | LOSS | random +veloce |
| 198 | vqe_real_amp_n50 | 50 | 15×15 | 53 | 57 | 1.0755 | success | **WIN** | noi +veloci |
| 199 | vqe_real_amp_n60 | 60 | 15×15 | 63 | 73 | 1.1587 | success | **WIN** | random +veloce |
| 200 | vqe_real_amp_n70 | 70 | 17×17 | 73 | 83 | 1.1370 | success | **WIN** | random +veloce |
| 201 | vqe_real_amp_n80 | 80 | 17×17 | 83 | 91 | 1.0964 | success | **WIN** | random +veloce |
| 202 | vqe_real_amp_n90 | 90 | 19×19 | 93 | 104 | 1.1183 | success | **WIN** | noi +veloci |
| 203 | vqe_su2_n10 | 10 | 7×7 | 13 | 19 | 1.4615 | success | **WIN** | noi +veloci |
| 204 | vqe_su2_n100 | 100 | 19×19 | 103 | 109 | 1.0583 | success | **WIN** | random +veloce |
| 205 | vqe_su2_n125 | 125 | 23×23 | 128 | 133 | 1.0391 | success | **WIN** | random +veloce |
| 206 | vqe_su2_n150 | 150 | 25×25 | 153 | 158 | 1.0327 | success | **WIN** | random +veloce |
| 207 | vqe_su2_n175 | 175 | 27×27 | 178 | 184 | 1.0337 | success | **WIN** | random +veloce |
| 208 | vqe_su2_n20 | 20 | 9×9 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 209 | vqe_su2_n200 | 200 | 29×29 | 203 | 209 | 1.0296 | success | **WIN** | random +veloce |
| 210 | vqe_su2_n30 | 30 | 11×11 | 33 | 38 | 1.1515 | success | **WIN** | noi +veloci |
| 211 | vqe_su2_n300 | 300 | 35×35 | 303 | 316 | 1.0429 | success | **WIN** | random +veloce |
| 212 | vqe_su2_n40 | 40 | 13×13 | 43 | 48 | 1.1163 | success | **WIN** | random +veloce |
| 213 | vqe_su2_n400 | 400 | 39×39 | 403 | 410 | 1.0174 | success | **WIN** | random +veloce |
| 214 | vqe_su2_n5 | 5 | 5×5 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 215 | vqe_su2_n50 | 50 | 15×15 | 53 | 59 | 1.1132 | success | **WIN** | random +veloce |
| 216 | vqe_su2_n60 | 60 | 15×15 | 63 | 67 | 1.0635 | success | **WIN** | random +veloce |
| 217 | vqe_su2_n70 | 70 | 17×17 | 73 | 77 | 1.0548 | success | **WIN** | random +veloce |
| 218 | vqe_su2_n80 | 80 | 17×17 | 83 | 91 | 1.0964 | success | **WIN** | random +veloce |
| 219 | vqe_su2_n90 | 90 | 19×19 | 93 | 96 | 1.0323 | success | **WIN** | random +veloce |
| 220 | vqe_two_local_n10 | 10 | 7×7 | 45 | 66 | 1.4667 | success | **WIN** | random +veloce |
| 221 | vqe_two_local_n100 | 100 | 19×19 | 2174 | 2191 | 1.0078 | success | **WIN** | random +veloce |
| 222 | vqe_two_local_n125 | 125 | 23×23 | 2555 | 2994 | 1.1718 | success | **WIN** | random +veloce |
| 223 | vqe_two_local_n150 | 150 | 25×25 | 3497 | 3968 | 1.1347 | success | **WIN** | random +veloce |
| 224 | vqe_two_local_n175 | 175 | 27×27 | 4611 | 5013 | 1.0872 | success | **WIN** | random +veloce |
| 225 | vqe_two_local_n20 | 20 | 9×9 | 129 | 163 | 1.2636 | success | **WIN** | noi +veloci |
| 226 | vqe_two_local_n200 | 200 | 29×29 | 5706 | 6284 | 1.1013 | success | **WIN** | random +veloce |
| 227 | vqe_two_local_n30 | 30 | 11×11 | 260 | 326 | 1.2538 | success | **WIN** | random +veloce |
| 228 | vqe_two_local_n300 | 300 | 39×39 | 10420 | 11471 | 1.1009 | success | **WIN** | random +veloce |
| 229 | vqe_two_local_n40 | 40 | 13×13 | 385 | 496 | 1.2883 | success | **WIN** | random +veloce |
| 230 | vqe_two_local_n400 | 400 | 43×43 | 17089 | 18894 | 1.1056 | success | **WIN** | random +veloce |
| 231 | vqe_two_local_n5 | 5 | 5×5 | 17 | 20 | 1.1765 | success | **WIN** | random +veloce |
| 232 | vqe_two_local_n50 | 50 | 15×15 | 541 | 675 | 1.2477 | success | **WIN** | noi +veloci |
| 233 | vqe_two_local_n60 | 60 | 15×15 | 1011 | 984 | 0.9733 | success | LOSS | random +veloce |
| 234 | vqe_two_local_n70 | 70 | 17×17 | 1007 | 1180 | 1.1718 | success | **WIN** | random +veloce |
| 235 | vqe_two_local_n80 | 80 | 17×17 | 1420 | 1550 | 1.0915 | success | **WIN** | random +veloce |
| 236 | vqe_two_local_n90 | 90 | 19×19 | 1587 | 1797 | 1.1323 | success | **WIN** | random +veloce |
| 237 | vqe_uccsd_n4 | 4 | 3×3 | 87 | 88 | 1.0115 | success | **WIN** | noi +veloci |
| 238 | vqe_uccsd_n8 | 8 | 5×5 | 5446 | 5446 | 1.0000 | success | = | noi +veloci |
| 239 | wstate_n10 | 10 | 7×7 | 11 | 11 | 1.0000 | success | = | random +veloce |
| 240 | wstate_n100 | 100 | 19×19 | 101 | 103 | 1.0198 | success | **WIN** | random +veloce |
| 241 | wstate_n125 | 125 | 23×23 | 126 | 130 | 1.0317 | success | **WIN** | random +veloce |
| 242 | wstate_n150 | 150 | 25×25 | 151 | 154 | 1.0199 | success | **WIN** | random +veloce |
| 243 | wstate_n175 | 175 | 27×27 | 176 | 178 | 1.0114 | success | **WIN** | random +veloce |
| 244 | wstate_n20 | 20 | 9×9 | 21 | 21 | 1.0000 | success | = | random +veloce |
| 245 | wstate_n200 | 200 | 29×29 | 201 | 202 | 1.0050 | success | **WIN** | random +veloce |
| 246 | wstate_n27 | 27 | 11×11 | 28 | 29 | 1.0357 | success | **WIN** | noi +veloci |
| 247 | wstate_n30 | 30 | 11×11 | 31 | 35 | 1.1290 | success | **WIN** | random +veloce |
| 248 | wstate_n300 | 300 | 35×35 | 301 | 302 | 1.0033 | success | **WIN** | random +veloce |
| 249 | wstate_n40 | 40 | 13×13 | 41 | 42 | 1.0244 | success | **WIN** | noi +veloci |
| 250 | wstate_n400 | 400 | 39×39 | 401 | 404 | 1.0075 | success | **WIN** | random +veloce |
| 251 | wstate_n5 | 5 | 5×5 | 7 | 6 | 0.8571 | success | LOSS | noi +veloci |
| 252 | wstate_n50 | 50 | 15×15 | 51 | 53 | 1.0392 | success | **WIN** | random +veloce |
| 253 | wstate_n60 | 60 | 15×15 | 61 | 63 | 1.0328 | success | **WIN** | noi +veloci |
| 254 | wstate_n70 | 70 | 17×17 | 71 | 72 | 1.0141 | success | **WIN** | noi +veloci |
| 255 | wstate_n80 | 80 | 17×17 | 81 | 83 | 1.0247 | success | **WIN** | random +veloce |
| 256 | wstate_n90 | 90 | 19×19 | 91 | 93 | 1.0220 | success | **WIN** | noi +veloci |
