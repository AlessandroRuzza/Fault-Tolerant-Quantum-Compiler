# Risultati sweep WISQ-native — connectivity (2026-06-25)

Config: `data/config/connectivity_summary_all.json` — tutti i 263 circuiti, parametri
**connectivity** dalla tabella riassuntiva di `pesi_finali.md` (gaussian/fine,
safe_passage=connectivity, border=15, sigma=0.7, mapped=20, cnot_high=8, cnot_low=0,
magic_high=0, magic_low=0, base=1, ext=−15, bfs=0.70, center_circle, packing,
smart_t_routing, patience=3).
Griglia WISQ-native (`wisq_native_side = 2⌈√n⌉+3`, flag `--wisq-native`; nessuna crescita griglia).
**Nessun fallback**: connectivity è già la strategia base (a differenza di cube, che ripiega su connectivity).
Dati da: `connectivity_summary_all_wisq.csv` — `--mr_timeout 12000` s.

---

## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ va in timeout** (mr_timeout=12000s) | 17 | — |
| ⚠ Sovrapposizione (noi ERR **e** WISQ timeout) | **0** — insiemi disgiunti | — |
| Entrambi completano | 244 | — |
| ↳ Noi vinciamo su steps | 32 (ratio mediana 1.94×) | 30 (94%) |
| ↳ Pareggio su steps | 121 | 104 (86%) |
| ↳ WISQ vince su steps | 91 (ratio mediana 0.85×) | 89 (98%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **153 / 263 (58.2%)** | — |
| ↳ Noi completiamo, WISQ va in timeout | 17 / 263 (6.5%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 32 / 263 (12.2%) | — |
| ↳ Pareggio su steps, noi più veloci | 104 / 263 (39.5%) | — |

> ⚠ Questa prima tabella è **asimmetrica** (mr_timeout=12000 s solo per WISQ; il nostro
> lato non ha cap). Con un budget **simmetrico** a 12000 s, 3 circuiti (`randomcircuit_n400/n500`,
> `multiplier_n400`) sforano anche da parte nostra → diventerebbero "nessun vincitore".
> Le tabelle a budget ridotto qui sotto applicano il timeout **simmetricamente a entrambi i compilatori**.

---

## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

**Metodologia** — il timeout è imposto **simmetricamente a entrambi i compilatori**: una
esecuzione "conta" solo se ha finito entro 3600 s. I run WISQ che completavano in >1h
diventano timeout → nostre vittorie; i circuiti che sforano 1h da entrambe le parti → nessun vincitore.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 1h** | 58 (17 fail + 41 oltre 1h) | — |
| ↳ …ma anche noi sforiamo 1h → nessun vincitore | 4 | — |
| ↳ …noi finiamo entro 1h → **vittoria** | 54 | — |
| **Entrambi finiscono in 1h** | 203 | — |
| ↳ Noi vinciamo su steps | 30 (ratio mediana 2.00×) | 28 (93%) |
| ↳ Pareggio su steps | 116 | 99 (85%) |
| ↳ WISQ vince su steps | 57 (ratio mediana 0.89×) | 55 (96%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **183 / 263 (69.6%)** | — |
| ↳ Noi finiamo, WISQ no (>1h) | 54 / 263 (20.5%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 30 / 263 (11.4%) | — |
| ↳ Pareggio su steps, noi più veloci | 99 / 263 (37.6%) | — |

---

## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Stessa metodologia (timeout simmetrico): conta solo chi finisce entro 1800 s.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 30min** | 66 (17 fail + 49 oltre 30min) | — |
| ↳ …ma anche noi sforiamo 30min → nessun vincitore | 6 | — |
| ↳ …noi finiamo entro 30min → **vittoria** | 60 | — |
| **Entrambi finiscono in 30min** | 195 | — |
| ↳ Noi vinciamo su steps | 30 (ratio mediana 2.00×) | 28 (93%) |
| ↳ Pareggio su steps | 116 | 99 (85%) |
| ↳ WISQ vince su steps | 49 (ratio mediana 0.90×) | 47 (96%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **189 / 263 (71.9%)** | — |
| ↳ Noi finiamo, WISQ no (>30min) | 60 / 263 (22.8%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 30 / 263 (11.4%) | — |
| ↳ Pareggio su steps, noi più veloci | 99 / 263 (37.6%) | — |

---

## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Stessa metodologia: conta solo chi finisce entro 900 s.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 15min** | 83 (17 fail + 66 oltre 15min) | — |
| ↳ …ma anche noi sforiamo 15min → nessun vincitore | 9 | — |
| ↳ …noi finiamo entro 15min → **vittoria** | 74 | — |
| **Entrambi finiscono in 15min** | 178 | — |
| ↳ Noi vinciamo su steps | 30 (ratio mediana 2.00×) | 28 (93%) |
| ↳ Pareggio su steps | 110 | 93 (85%) |
| ↳ WISQ vince su steps | 38 (ratio mediana 0.91×) | 36 (95%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **197 / 263 (74.9%)** | — |
| ↳ Noi finiamo, WISQ no (>15min) | 74 / 263 (28.1%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 30 / 263 (11.4%) | — |
| ↳ Pareggio su steps, noi più veloci | 93 / 263 (35.4%) | — |

---

## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Stessa metodologia: conta solo chi finisce entro 600 s.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 10min** | 90 (17 fail + 73 oltre 10min) | — |
| ↳ …ma anche noi sforiamo 10min → nessun vincitore | 10 | — |
| ↳ …noi finiamo entro 10min → **vittoria** | 80 | — |
| **Entrambi finiscono in 10min** | 171 | — |
| ↳ Noi vinciamo su steps | 30 (ratio mediana 2.00×) | 28 (93%) |
| ↳ Pareggio su steps | 110 | 93 (85%) |
| ↳ WISQ vince su steps | 31 (ratio mediana 0.91×) | 29 (94%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **203 / 263 (77.2%)** | — |
| ↳ Noi finiamo, WISQ no (>10min) | 80 / 263 (30.4%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 30 / 263 (11.4%) | — |
| ↳ Pareggio su steps, noi più veloci | 93 / 263 (35.4%) | — |

---

## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Stessa metodologia: conta solo chi finisce entro 300 s. È il **picco** di win-rate.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 5min** | 102 (17 fail + 85 oltre 5min) | — |
| ↳ …ma anche noi sforiamo 5min → nessun vincitore | 13 | — |
| ↳ …noi finiamo entro 5min → **vittoria** | 89 | — |
| **Entrambi finiscono in 5min** | 159 | — |
| ↳ Noi vinciamo su steps | 30 (ratio mediana 2.00×) | 28 (93%) |
| ↳ Pareggio su steps | 107 | 90 (84%) |
| ↳ WISQ vince su steps | 22 (ratio mediana 0.94×) | 20 (91%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **209 / 263 (79.5%)** ⟵ picco | — |
| ↳ Noi finiamo, WISQ no (>5min) | 89 / 263 (33.8%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 30 / 263 (11.4%) | — |
| ↳ Pareggio su steps, noi più veloci | 90 / 263 (34.2%) | — |

---

## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Stessa metodologia: conta solo chi finisce entro 60 s. A 1 min il nostro overhead di mapping
gaussiano comincia a costarci: alcuni circuiti banali (dove WISQ finisce in ~4 s) sforano i 60 s
dal nostro lato e diventano sconfitte; il win-rate scende sotto il picco dei 5 min.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 1min** | 129 (17 fail + 112 oltre 1min) | — |
| ↳ …ma anche noi sforiamo 1min → nessun vincitore | 35 | — |
| ↳ …noi finiamo entro 1min → **vittoria** | 94 | — |
| **Noi non finiamo, WISQ sì → sconfitta** (overhead gaussiano) | 14 | — |
| **Entrambi finiscono in 1min** | 118 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 2.00×) | 27 (96%) |
| ↳ Pareggio su steps | 83 | 78 (94%) |
| ↳ WISQ vince su steps | 7 (ratio mediana 0.96×) | 7 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **200 / 263 (76.0%)** | — |
| ↳ Noi finiamo, WISQ no (>1min) | 94 / 263 (35.7%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 28 / 263 (10.6%) | — |
| ↳ Pareggio su steps, noi più veloci | 78 / 263 (29.7%) | — |

---

## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (orig., asimm.) | 244 | 17 | 0 | 0 | **153 (58.2%)** |
| 1 ora | 203 | 54 | 0 | 4 | **183 (69.6%)** |
| 30 min | 195 | 60 | 0 | 6 | **189 (71.9%)** |
| 15 min | 178 | 74 | 0 | 9 | **197 (74.9%)** |
| 10 min | 171 | 80 | 0 | 10 | **203 (77.2%)** |
| **5 min** | 159 | 89 | 0 | 13 | **209 (79.5%)** ⟵ picco |
| 1 min | 118 | 94 | 14 | 35 | **200 (76.0%)** |

Stesso andamento del confronto cube: il win-rate cresce stringendo il budget (le sconfitte su
steps, lente lato WISQ, cadono nel bucket timeout) fino a un **picco a 5 min**, poi cala perché il
nostro overhead costante di mapping gaussiano fa sforare i circuiti banali che WISQ chiude in secondi.
Rispetto a cube, connectivity ha overhead più basso (nessun nostro timeout fino a 1 min, vs cube già a 5 min).

---

## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s` su 261 circuiti (tutti tranne i 2 errori nostri).
Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). I 17 circuiti in timeout WISQ
sono inclusi con la loro `wisq_duration` registrata (~12000 s, lower bound).

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 261 | 237 (91%) | 308× | 554× | 0.03× | 32092× |
| ↳ Circuiti dove vinciamo su steps | 32 | 30 (94%) | 190× | 228× | 0.14× | 645× |
| ↳ Circuiti in pareggio su steps | 121 | 104 (86%) | 534× | 865× | 0.03× | 32092× |
| ↳ Circuiti dove WISQ vince su steps | 91 | 89 (98%) | 305× | 330× | 0.08× | 3062× |
| ↳ WISQ in timeout | 17 | 14 (82%) | 12× | 152× | 0.43× | 1297× |

---

## Per famiglia di circuiti

**WISQ timeout** = WISQ ha girato fino a mr_timeout=12000s senza trovare soluzione. Win/=/Loss sono sul numero di routing steps fra i circuiti dove entrambi completano.

| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | Err | Note |
|--------|---|-----|----------------|------|--------------|-----|------|
| 19qubits | 2 | 0 | 1 (0 noi+veloci) | 1 | 0 | 0 | n=19 |
| 53qubits | 2 | 0 | 2 (1 noi+veloci) | 0 | 0 | 0 | n=27–39 |
| adder | 5 | 0 | 4 (2 noi+veloci) | 1 | 0 | 0 | n=4–433 |
| bv | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=153 |
| bwt | 5 | 0 | 1 (1 noi+veloci) | 0 | 4 | 0 | n=21–133 |
| cat | 2 | 0 | 2 (1 noi+veloci) | 0 | 0 | 0 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=3 |
| dnn | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=16 |
| example | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=4 |
| factor247 | 1 | 0 | 0 (0 noi+veloci) | 0 | 1 | 0 | n=15 |
| fredkin | 1 | 0 | 1 (0 noi+veloci) | 0 | 0 | 0 | n=3 |
| ghz | 18 | 0 | 18 (13 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| ghz_state | 2 | 0 | 2 (1 noi+veloci) | 0 | 0 | 0 | n=23–255 |
| graphstate | 17 | 10 | 7 (4 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| grover | 3 | 0 | 2 (2 noi+veloci) | 0 | 1 | 0 | n=5–20 |
| hhl | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | n=10 |
| ising | 19 | 17 | 2 (1 noi+veloci) | 0 | 0 | 0 | n=5–420 |
| knn | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 |  |
| multiplier | 11 | 2 | 5 (5 noi+veloci) | 0 | 4 | 0 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=6 |
| parallel | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 (0 noi+veloci) | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 0 | 4 (4 noi+veloci) | 15 | 1 | 0 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=5 |
| qft | 22 | 0 | 1 (1 noi+veloci) | 20 | 1 | 0 | n=5–400 |
| qpe_n9 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=9 |
| qram | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=9 |
| randomcircuit | 5 | 0 | 0 (0 noi+veloci) | 2 | 3 | 0 | n=50–500 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| square_root | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=14–32 |
| synth | 37 | 0 | 0 (0 noi+veloci) | 37 | 0 | 0 | n=50–200 |
| t_test | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=8 |
| test | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 |  |
| toffoli | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | n=3 |
| vqe_real_amp | 17 | 0 | 17 (17 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| vqe_su2 | 17 | 0 | 17 (17 noi+veloci) | 0 | 0 | 0 | n=5–400 |
| vqe_two_local | 17 | 1 | 1 (1 noi+veloci) | 13 | 2 | 0 | n=5–400 |
| vqe_uccsd | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | n=4–8 |
| wstate | 18 | 0 | 18 (18 noi+veloci) | 0 | 0 | 0 | n=5–400 |

---

## Per circuito (dettaglio)

**Steps**: WIN = noi meno routing steps, LOSS = WISQ meno steps, = = pareggio. **Tempo**: durata compilazione nostra vs WISQ (dove entrambi completano). **WISQ status `failed`** = raggiunto mr_timeout=12000s.

| # | Circuit | Qubits | Grid | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 13×13 | 102 | 99 | 0.9706 | success | LOSS | WISQ +veloce |
| 2 | 19qubits_521gate_352layers | 19 | 13×13 | 286 | 286 | 1.0000 | success | = | WISQ +veloce |
| 3 | 53qubits_155gate_57layers | 27 | 15×15 | 23 | 23 | 1.0000 | success | = | WISQ +veloce |
| 4 | 53qubits_332gate_152layers | 39 | 17×17 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 15×15 | 24 | 24 | 1.0000 | success | = | WISQ +veloce |
| 6 | adder_n4 | 4 | 7×7 | 8 | 8 | 1.0000 | success | = | WISQ +veloce |
| 7 | adder_n433 | 433 | 45×45 | 249 | 249 | 1.0000 | success | = | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 19×19 | 181 | 181 | 1.0000 | success | = | noi +veloci |
| 9 | bigadder_n18_transpiled | 18 | 7×7 | 90 | 88 | 0.9778 | success | LOSS | WISQ +veloce |
| 10 | bv_n280 | 153 | 37×37 | 152 | 152 | 1.0000 | success | = | noi +veloci |
| 11 | bwt_n177 | 133 | 27×27 | 257604 | — | — | failed | timeout | — |
| 12 | bwt_n21 | 21 | 13×13 | 116600 | — | — | failed | timeout | — |
| 13 | bwt_n37 | 28 | 15×15 | 33600 | 33600 | 1.0000 | success | = | noi +veloci |
| 14 | bwt_n57 | 43 | 17×17 | 65603 | — | — | failed | timeout | — |
| 15 | bwt_n97 | 73 | 21×21 | 129600 | — | — | failed | timeout | — |
| 16 | cat_n130 | 130 | 27×27 | 129 | 129 | 1.0000 | success | = | WISQ +veloce |
| 17 | cat_n260 | 260 | 37×37 | 259 | 259 | 1.0000 | success | = | noi +veloci |
| 18 | continuous_3_17_13 | 3 | 7×7 | 17 | 17 | 1.0000 | success | = | WISQ +veloce |
| 19 | dnn_n16 | 16 | 11×11 | 48 | 52 | 1.0833 | success | **WIN** | noi +veloci |
| 20 | example | 4 | 7×7 | 23 | 21 | 0.9130 | success | LOSS | noi +veloci |
| 21 | factor247_n15 | 15 | 11×11 | 349644 | — | — | failed | timeout | — |
| 22 | fredkin_n3 | 3 | 7×7 | 10 | 10 | 1.0000 | success | = | WISQ +veloce |
| 23 | ghz_n10 | 10 | 11×11 | 9 | 9 | 1.0000 | success | = | WISQ +veloce |
| 24 | ghz_n100 | 100 | 23×23 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 25 | ghz_n125 | 125 | 27×27 | 124 | 124 | 1.0000 | success | = | noi +veloci |
| 26 | ghz_n150 | 150 | 29×29 | 149 | 149 | 1.0000 | success | = | noi +veloci |
| 27 | ghz_n175 | 175 | 31×31 | 174 | 174 | 1.0000 | success | = | noi +veloci |
| 28 | ghz_n20 | 20 | 13×13 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 29 | ghz_n200 | 200 | 33×33 | 199 | 199 | 1.0000 | success | = | WISQ +veloce |
| 30 | ghz_n255 | 255 | 35×35 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 31 | ghz_n30 | 30 | 15×15 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 32 | ghz_n300 | 300 | 39×39 | 299 | 299 | 1.0000 | success | = | noi +veloci |
| 33 | ghz_n40 | 40 | 17×17 | 39 | 39 | 1.0000 | success | = | WISQ +veloce |
| 34 | ghz_n400 | 400 | 43×43 | 399 | 399 | 1.0000 | success | = | noi +veloci |
| 35 | ghz_n5 | 5 | 9×9 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 36 | ghz_n50 | 50 | 19×19 | 49 | 49 | 1.0000 | success | = | noi +veloci |
| 37 | ghz_n60 | 60 | 19×19 | 59 | 59 | 1.0000 | success | = | WISQ +veloce |
| 38 | ghz_n70 | 70 | 21×21 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 39 | ghz_n80 | 80 | 21×21 | 79 | 79 | 1.0000 | success | = | WISQ +veloce |
| 40 | ghz_n90 | 90 | 23×23 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 41 | ghz_state_n23 | 23 | 13×13 | 22 | 22 | 1.0000 | success | = | WISQ +veloce |
| 42 | ghz_state_n255 | 255 | 35×35 | 254 | 254 | 1.0000 | success | = | noi +veloci |
| 43 | graphstate_n10 | 10 | 11×11 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 44 | graphstate_n100 | 100 | 23×23 | 8 | 8 | 1.0000 | success | = | WISQ +veloce |
| 45 | graphstate_n125 | 125 | 27×27 | 5 | 8 | 1.6000 | success | **WIN** | noi +veloci |
| 46 | graphstate_n150 | 150 | 29×29 | 6 | 12 | 2.0000 | success | **WIN** | noi +veloci |
| 47 | graphstate_n175 | 175 | 31×31 | 7 | 10 | 1.4286 | success | **WIN** | WISQ +veloce |
| 48 | graphstate_n20 | 20 | 13×13 | 4 | 4 | 1.0000 | success | = | WISQ +veloce |
| 49 | graphstate_n200 | 200 | 33×33 | 6 | 12 | 2.0000 | success | **WIN** | noi +veloci |
| 50 | graphstate_n30 | 30 | 15×15 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 51 | graphstate_n300 | 300 | 39×39 | 9 | 17 | 1.8889 | success | **WIN** | noi +veloci |
| 52 | graphstate_n40 | 40 | 17×17 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 53 | graphstate_n400 | 400 | 43×43 | 7 | 20 | 2.8571 | success | **WIN** | noi +veloci |
| 54 | graphstate_n5 | 5 | 9×9 | 4 | 4 | 1.0000 | success | = | WISQ +veloce |
| 55 | graphstate_n50 | 50 | 19×19 | 5 | 5 | 1.0000 | success | = | noi +veloci |
| 56 | graphstate_n60 | 60 | 19×19 | 5 | 5 | 1.0000 | success | = | noi +veloci |
| 57 | graphstate_n70 | 70 | 21×21 | 5 | 6 | 1.2000 | success | **WIN** | noi +veloci |
| 58 | graphstate_n80 | 80 | 21×21 | 6 | 7 | 1.1667 | success | **WIN** | WISQ +veloce |
| 59 | graphstate_n90 | 90 | 23×23 | 5 | 7 | 1.4000 | success | **WIN** | noi +veloci |
| 60 | grover_n10 | 10 | 9×9 | 11008 | 11008 | 1.0000 | success | = | noi +veloci |
| 61 | grover_n20 | 20 | 13×13 | 2146489 | — | — | failed | timeout | — |
| 62 | grover_n5 | 5 | 7×7 | 209 | 209 | 1.0000 | success | = | noi +veloci |
| 63 | hhl_n10 | 10 | 7×7 | 72040 | 72039 | 1.0000 | success | LOSS | noi +veloci |
| 64 | ising_n10 | 10 | 11×11 | 4 | 4 | 1.0000 | success | = | WISQ +veloce |
| 65 | ising_n100 | 100 | 23×23 | 4 | 14 | 3.5000 | success | **WIN** | noi +veloci |
| 66 | ising_n125 | 125 | 27×27 | 4 | 15 | 3.7500 | success | **WIN** | noi +veloci |
| 67 | ising_n150 | 150 | 29×29 | 4 | 19 | 4.7500 | success | **WIN** | noi +veloci |
| 68 | ising_n175 | 175 | 31×31 | 4 | 20 | 5.0000 | success | **WIN** | noi +veloci |
| 69 | ising_n20 | 20 | 13×13 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 70 | ising_n200 | 200 | 33×33 | 4 | 22 | 5.5000 | success | **WIN** | noi +veloci |
| 71 | ising_n26 | 26 | 15×15 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 72 | ising_n30 | 30 | 15×15 | 4 | 6 | 1.5000 | success | **WIN** | noi +veloci |
| 73 | ising_n300 | 300 | 39×39 | 4 | 33 | 8.2500 | success | **WIN** | noi +veloci |
| 74 | ising_n40 | 40 | 17×17 | 4 | 7 | 1.7500 | success | **WIN** | noi +veloci |
| 75 | ising_n400 | 400 | 43×43 | 4 | 42 | 10.5000 | success | **WIN** | noi +veloci |
| 76 | ising_n420 | 420 | 45×45 | 4 | 44 | 11.0000 | success | **WIN** | noi +veloci |
| 77 | ising_n5 | 5 | 9×9 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 78 | ising_n50 | 50 | 19×19 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 79 | ising_n60 | 60 | 19×19 | 4 | 9 | 2.2500 | success | **WIN** | noi +veloci |
| 80 | ising_n70 | 70 | 21×21 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 81 | ising_n80 | 80 | 21×21 | 4 | 11 | 2.7500 | success | **WIN** | noi +veloci |
| 82 | ising_n90 | 90 | 23×23 | 4 | 13 | 3.2500 | success | **WIN** | noi +veloci |
| 83 | knn_n25 | — | — | — | — | — | error | ERR | — |
| 84 | multiplier_n100 | 100 | 23×23 | 111762 | — | — | failed | timeout | — |
| 85 | multiplier_n15 | 9 | 9×9 | 12 | 12 | 1.0000 | success | = | noi +veloci |
| 86 | multiplier_n20 | 20 | 13×13 | 3990 | 3990 | 1.0000 | success | = | noi +veloci |
| 87 | multiplier_n200 | 200 | 33×33 | 450019 | — | — | failed | timeout | — |
| 88 | multiplier_n300 | 300 | 39×39 | 1013844 | — | — | failed | timeout | — |
| 89 | multiplier_n40 | 40 | 17×17 | 17329 | 17329 | 1.0000 | success | = | noi +veloci |
| 90 | multiplier_n400 | 400 | 43×43 | 1803550 | — | — | failed | timeout | — |
| 91 | multiplier_n45 | 27 | 17×17 | 36 | 36 | 1.0000 | success | = | noi +veloci |
| 92 | multiplier_n60 | 60 | 19×19 | 39730 | 39731 | 1.0000 | success | **WIN** | noi +veloci |
| 93 | multiplier_n75 | 45 | 21×21 | 60 | 60 | 1.0000 | success | = | noi +veloci |
| 94 | multiplier_n80 | 80 | 21×21 | 71287 | 71289 | 1.0000 | success | **WIN** | noi +veloci |
| 95 | multiply_n13 | 6 | 9×9 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 96 | parallel | 8 | 9×9 | 10 | 10 | 1.0000 | success | = | noi +veloci |
| 97 | parallel_big | 20 | 13×13 | 8 | 10 | 1.2500 | success | **WIN** | noi +veloci |
| 98 | qaoa_n10 | 10 | 11×11 | 46 | 46 | 1.0000 | success | = | noi +veloci |
| 99 | qaoa_n100 | 100 | 23×23 | 1098 | 876 | 0.7978 | success | LOSS | noi +veloci |
| 100 | qaoa_n125 | 125 | 27×27 | 1569 | 1265 | 0.8062 | success | LOSS | noi +veloci |
| 101 | qaoa_n150 | 150 | 29×29 | 2131 | 1722 | 0.8081 | success | LOSS | noi +veloci |
| 102 | qaoa_n175 | 175 | 31×31 | 2819 | 2259 | 0.8013 | success | LOSS | noi +veloci |
| 103 | qaoa_n20 | 20 | 13×13 | 94 | 90 | 0.9574 | success | LOSS | noi +veloci |
| 104 | qaoa_n200 | 200 | 33×33 | 3569 | 2844 | 0.7969 | success | LOSS | noi +veloci |
| 105 | qaoa_n30 | 30 | 15×15 | 150 | 139 | 0.9267 | success | LOSS | noi +veloci |
| 106 | qaoa_n300 | 300 | 39×39 | 7093 | 5908 | 0.8329 | success | LOSS | noi +veloci |
| 107 | qaoa_n40 | 40 | 17×17 | 232 | 208 | 0.8966 | success | LOSS | noi +veloci |
| 108 | qaoa_n400 | 400 | 43×43 | 11742 | — | — | failed | timeout | — |
| 109 | qaoa_n5 | 5 | 9×9 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 110 | qaoa_n50 | 50 | 19×19 | 333 | 283 | 0.8498 | success | LOSS | noi +veloci |
| 111 | qaoa_n6 | 6 | 9×9 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 112 | qaoa_n60 | 60 | 19×19 | 469 | 383 | 0.8166 | success | LOSS | noi +veloci |
| 113 | qaoa_n64 | 64 | 19×19 | 499 | 428 | 0.8577 | success | LOSS | noi +veloci |
| 114 | qaoa_n6_transpiled | 6 | 9×9 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 115 | qaoa_n70 | 70 | 21×21 | 561 | 477 | 0.8503 | success | LOSS | noi +veloci |
| 116 | qaoa_n80 | 80 | 21×21 | 719 | 591 | 0.8220 | success | LOSS | noi +veloci |
| 117 | qaoa_n90 | 90 | 23×23 | 874 | 721 | 0.8249 | success | LOSS | noi +veloci |
| 118 | qec_en_n5 | 5 | 9×9 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 119 | qft_20 | 20 | 13×13 | 83 | 82 | 0.9880 | success | LOSS | noi +veloci |
| 120 | qft_n10 | 10 | 11×11 | 36 | 34 | 0.9444 | success | LOSS | noi +veloci |
| 121 | qft_n100 | 100 | 23×23 | 545 | 439 | 0.8055 | success | LOSS | noi +veloci |
| 122 | qft_n125 | 125 | 27×27 | 2622 | 527 | 0.2010 | success | LOSS | noi +veloci |
| 123 | qft_n128 | 128 | 27×27 | 2691 | 543 | 0.2018 | success | LOSS | noi +veloci |
| 124 | qft_n150 | 150 | 29×29 | 3077 | 631 | 0.2051 | success | LOSS | noi +veloci |
| 125 | qft_n175 | 175 | 31×31 | 3748 | 723 | 0.1929 | success | LOSS | noi +veloci |
| 126 | qft_n18 | 18 | 13×13 | 74 | 71 | 0.9595 | success | LOSS | noi +veloci |
| 127 | qft_n20 | 20 | 13×13 | 83 | 82 | 0.9880 | success | LOSS | noi +veloci |
| 128 | qft_n200 | 200 | 33×33 | 4295 | 822 | 0.1914 | success | LOSS | noi +veloci |
| 129 | qft_n30 | 30 | 15×15 | 144 | 135 | 0.9375 | success | LOSS | noi +veloci |
| 130 | qft_n300 | 300 | 39×39 | 6601 | 1224 | 0.1854 | success | LOSS | noi +veloci |
| 131 | qft_n320 | 320 | 39×39 | 8406 | — | — | failed | timeout | — |
| 132 | qft_n40 | 40 | 17×17 | 200 | 179 | 0.8950 | success | LOSS | noi +veloci |
| 133 | qft_n400 | 400 | 43×43 | 8820 | 1654 | 0.1875 | success | LOSS | noi +veloci |
| 134 | qft_n5 | 5 | 9×9 | 14 | 14 | 1.0000 | success | = | noi +veloci |
| 135 | qft_n50 | 50 | 19×19 | 259 | 221 | 0.8533 | success | LOSS | noi +veloci |
| 136 | qft_n60 | 60 | 19×19 | 315 | 269 | 0.8540 | success | LOSS | noi +veloci |
| 137 | qft_n64 | 64 | 19×19 | 340 | 289 | 0.8500 | success | LOSS | noi +veloci |
| 138 | qft_n70 | 70 | 21×21 | 380 | 317 | 0.8342 | success | LOSS | noi +veloci |
| 139 | qft_n80 | 80 | 21×21 | 444 | 352 | 0.7928 | success | LOSS | noi +veloci |
| 140 | qft_n90 | 90 | 23×23 | 480 | 394 | 0.8208 | success | LOSS | noi +veloci |
| 141 | qpe_n9_transpiled | 9 | 9×9 | 42 | 42 | 1.0000 | success | = | noi +veloci |
| 142 | qram_n20 | 9 | 7×7 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 143 | randomcircuit_n100 | 100 | 23×23 | 5066 | 4397 | 0.8679 | success | LOSS | noi +veloci |
| 144 | randomcircuit_n200 | 200 | 33×33 | 15543 | — | — | failed | timeout | — |
| 145 | randomcircuit_n400 | 400 | 43×43 | 241657 | — | — | failed | timeout | — |
| 146 | randomcircuit_n50 | 50 | 19×19 | 1510 | 1426 | 0.9444 | success | LOSS | noi +veloci |
| 147 | randomcircuit_n500 | 500 | 49×49 | 117675 | — | — | failed | timeout | — |
| 148 | seca_n11 | 11 | 11×11 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 149 | simon_n6 | 3 | 7×7 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 150 | square_root_n18 | 14 | 11×11 | 27 | 27 | 1.0000 | success | = | noi +veloci |
| 151 | square_root_n45 | 32 | 15×15 | 570 | 570 | 1.0000 | success | = | noi +veloci |
| 152 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 23×23 | 241 | 141 | 0.5851 | success | LOSS | noi +veloci |
| 153 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 23×23 | 238 | 144 | 0.6050 | success | LOSS | noi +veloci |
| 154 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 23×23 | 258 | 196 | 0.7597 | success | LOSS | noi +veloci |
| 155 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 23×23 | 263 | 187 | 0.7110 | success | LOSS | noi +veloci |
| 156 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 23×23 | 260 | 208 | 0.8000 | success | LOSS | noi +veloci |
| 157 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 23×23 | 271 | 209 | 0.7712 | success | LOSS | noi +veloci |
| 158 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 23×23 | 501 | 384 | 0.7665 | success | LOSS | noi +veloci |
| 159 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 23×23 | 513 | 391 | 0.7622 | success | LOSS | noi +veloci |
| 160 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 23×23 | 504 | 393 | 0.7798 | success | LOSS | noi +veloci |
| 161 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 23×23 | 498 | 392 | 0.7871 | success | LOSS | noi +veloci |
| 162 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 23×23 | 521 | 426 | 0.8177 | success | LOSS | noi +veloci |
| 163 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 23×23 | 506 | 431 | 0.8518 | success | LOSS | noi +veloci |
| 164 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 719 | 419 | 0.5828 | success | LOSS | noi +veloci |
| 165 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 709 | 384 | 0.5416 | success | LOSS | noi +veloci |
| 166 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 850 | 605 | 0.7118 | success | LOSS | noi +veloci |
| 167 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 820 | 605 | 0.7378 | success | LOSS | noi +veloci |
| 168 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 823 | 647 | 0.7861 | success | LOSS | noi +veloci |
| 169 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 868 | 647 | 0.7454 | success | LOSS | noi +veloci |
| 170 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 1516 | 1153 | 0.7606 | success | LOSS | noi +veloci |
| 171 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 1487 | 1161 | 0.7808 | success | LOSS | noi +veloci |
| 172 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 1505 | 1248 | 0.8292 | success | LOSS | noi +veloci |
| 173 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 1536 | 1251 | 0.8145 | success | LOSS | noi +veloci |
| 174 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 33×33 | 1577 | 1402 | 0.8890 | success | LOSS | noi +veloci |
| 175 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 1607 | 1405 | 0.8743 | success | LOSS | noi +veloci |
| 176 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 76 | 60 | 0.7895 | success | LOSS | noi +veloci |
| 177 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 70 | 58 | 0.8286 | success | LOSS | noi +veloci |
| 178 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 79 | 70 | 0.8861 | success | LOSS | noi +veloci |
| 179 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 80 | 75 | 0.9375 | success | LOSS | noi +veloci |
| 180 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 78 | 69 | 0.8846 | success | LOSS | noi +veloci |
| 181 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 77 | 70 | 0.9091 | success | LOSS | noi +veloci |
| 182 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 117 | 106 | 0.9060 | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 147 | 136 | 0.9252 | success | LOSS | noi +veloci |
| 184 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 157 | 137 | 0.8726 | success | LOSS | noi +veloci |
| 185 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 158 | 145 | 0.9177 | success | LOSS | noi +veloci |
| 186 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 163 | 151 | 0.9264 | success | LOSS | noi +veloci |
| 187 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 155 | 146 | 0.9419 | success | LOSS | noi +veloci |
| 188 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 154 | 146 | 0.9481 | success | LOSS | noi +veloci |
| 189 | t_test | 8 | 9×9 | 110 | 110 | 1.0000 | success | = | noi +veloci |
| 190 | t_test2 | 8 | 9×9 | 3904 | 3904 | 1.0000 | success | = | noi +veloci |
| 191 | test | — | — | — | — | — | error | ERR | — |
| 192 | toffoli_n3 | 3 | 7×7 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 193 | vqe_real_amp_n10 | 10 | 11×11 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 194 | vqe_real_amp_n100 | 100 | 23×23 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 195 | vqe_real_amp_n125 | 125 | 27×27 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 196 | vqe_real_amp_n150 | 150 | 29×29 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 197 | vqe_real_amp_n175 | 175 | 31×31 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 198 | vqe_real_amp_n20 | 20 | 13×13 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 199 | vqe_real_amp_n200 | 200 | 33×33 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 200 | vqe_real_amp_n30 | 30 | 15×15 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 201 | vqe_real_amp_n300 | 300 | 39×39 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 202 | vqe_real_amp_n40 | 40 | 17×17 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 203 | vqe_real_amp_n400 | 400 | 43×43 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 204 | vqe_real_amp_n5 | 5 | 9×9 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 205 | vqe_real_amp_n50 | 50 | 19×19 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 206 | vqe_real_amp_n60 | 60 | 19×19 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 207 | vqe_real_amp_n70 | 70 | 21×21 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 208 | vqe_real_amp_n80 | 80 | 21×21 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 209 | vqe_real_amp_n90 | 90 | 23×23 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 210 | vqe_su2_n10 | 10 | 11×11 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 211 | vqe_su2_n100 | 100 | 23×23 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 212 | vqe_su2_n125 | 125 | 27×27 | 128 | 128 | 1.0000 | success | = | noi +veloci |
| 213 | vqe_su2_n150 | 150 | 29×29 | 153 | 153 | 1.0000 | success | = | noi +veloci |
| 214 | vqe_su2_n175 | 175 | 31×31 | 178 | 178 | 1.0000 | success | = | noi +veloci |
| 215 | vqe_su2_n20 | 20 | 13×13 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 216 | vqe_su2_n200 | 200 | 33×33 | 203 | 203 | 1.0000 | success | = | noi +veloci |
| 217 | vqe_su2_n30 | 30 | 15×15 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 218 | vqe_su2_n300 | 300 | 39×39 | 303 | 303 | 1.0000 | success | = | noi +veloci |
| 219 | vqe_su2_n40 | 40 | 17×17 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 220 | vqe_su2_n400 | 400 | 43×43 | 403 | 403 | 1.0000 | success | = | noi +veloci |
| 221 | vqe_su2_n5 | 5 | 9×9 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 222 | vqe_su2_n50 | 50 | 19×19 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 223 | vqe_su2_n60 | 60 | 19×19 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 224 | vqe_su2_n70 | 70 | 21×21 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 225 | vqe_su2_n80 | 80 | 21×21 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 226 | vqe_su2_n90 | 90 | 23×23 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 227 | vqe_two_local_n10 | 10 | 11×11 | 40 | 39 | 0.9750 | success | LOSS | noi +veloci |
| 228 | vqe_two_local_n100 | 100 | 23×23 | 1560 | 1391 | 0.8917 | success | LOSS | noi +veloci |
| 229 | vqe_two_local_n125 | 125 | 27×27 | 2234 | 1993 | 0.8921 | success | LOSS | noi +veloci |
| 230 | vqe_two_local_n150 | 150 | 29×29 | 3006 | 2732 | 0.9088 | success | LOSS | noi +veloci |
| 231 | vqe_two_local_n175 | 175 | 31×31 | 3969 | 3552 | 0.8949 | success | LOSS | noi +veloci |
| 232 | vqe_two_local_n20 | 20 | 13×13 | 94 | 101 | 1.0745 | success | **WIN** | noi +veloci |
| 233 | vqe_two_local_n200 | 200 | 33×33 | 5010 | 4464 | 0.8910 | success | LOSS | noi +veloci |
| 234 | vqe_two_local_n30 | 30 | 15×15 | 193 | 189 | 0.9793 | success | LOSS | noi +veloci |
| 235 | vqe_two_local_n300 | 300 | 39×39 | 10532 | — | — | failed | timeout | — |
| 236 | vqe_two_local_n40 | 40 | 17×17 | 301 | 285 | 0.9468 | success | LOSS | noi +veloci |
| 237 | vqe_two_local_n400 | 400 | 43×43 | 17105 | — | — | failed | timeout | — |
| 238 | vqe_two_local_n5 | 5 | 9×9 | 17 | 17 | 1.0000 | success | = | noi +veloci |
| 239 | vqe_two_local_n50 | 50 | 19×19 | 440 | 403 | 0.9159 | success | LOSS | noi +veloci |
| 240 | vqe_two_local_n60 | 60 | 19×19 | 610 | 580 | 0.9508 | success | LOSS | noi +veloci |
| 241 | vqe_two_local_n70 | 70 | 21×21 | 793 | 757 | 0.9546 | success | LOSS | noi +veloci |
| 242 | vqe_two_local_n80 | 80 | 21×21 | 1053 | 970 | 0.9212 | success | LOSS | noi +veloci |
| 243 | vqe_two_local_n90 | 90 | 23×23 | 1272 | 1134 | 0.8915 | success | LOSS | noi +veloci |
| 244 | vqe_uccsd_n4 | 4 | 7×7 | 87 | 87 | 1.0000 | success | = | noi +veloci |
| 245 | vqe_uccsd_n8 | 8 | 9×9 | 5446 | 5446 | 1.0000 | success | = | noi +veloci |
| 246 | wstate_n10 | 10 | 11×11 | 11 | 11 | 1.0000 | success | = | noi +veloci |
| 247 | wstate_n100 | 100 | 23×23 | 101 | 101 | 1.0000 | success | = | noi +veloci |
| 248 | wstate_n125 | 125 | 27×27 | 126 | 126 | 1.0000 | success | = | noi +veloci |
| 249 | wstate_n150 | 150 | 29×29 | 151 | 151 | 1.0000 | success | = | noi +veloci |
| 250 | wstate_n175 | 175 | 31×31 | 176 | 176 | 1.0000 | success | = | noi +veloci |
| 251 | wstate_n20 | 20 | 13×13 | 21 | 21 | 1.0000 | success | = | noi +veloci |
| 252 | wstate_n200 | 200 | 33×33 | 201 | 201 | 1.0000 | success | = | noi +veloci |
| 253 | wstate_n27 | 27 | 15×15 | 28 | 28 | 1.0000 | success | = | noi +veloci |
| 254 | wstate_n30 | 30 | 15×15 | 31 | 31 | 1.0000 | success | = | noi +veloci |
| 255 | wstate_n300 | 300 | 39×39 | 301 | 301 | 1.0000 | success | = | noi +veloci |
| 256 | wstate_n40 | 40 | 17×17 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 257 | wstate_n400 | 400 | 43×43 | 401 | 401 | 1.0000 | success | = | noi +veloci |
| 258 | wstate_n5 | 5 | 9×9 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 259 | wstate_n50 | 50 | 19×19 | 51 | 51 | 1.0000 | success | = | noi +veloci |
| 260 | wstate_n60 | 60 | 19×19 | 61 | 61 | 1.0000 | success | = | noi +veloci |
| 261 | wstate_n70 | 70 | 21×21 | 71 | 71 | 1.0000 | success | = | noi +veloci |
| 262 | wstate_n80 | 80 | 21×21 | 81 | 81 | 1.0000 | success | = | noi +veloci |
| 263 | wstate_n90 | 90 | 23×23 | 91 | 91 | 1.0000 | success | = | noi +veloci |
