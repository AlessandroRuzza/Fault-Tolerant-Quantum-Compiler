# Risultati WISQ-native MENO 5 — connectivity (2026-06-25)

Config: `data/config/conn_wisq_minus5.json` — 139 circuiti (n≤100), **connectivity con i pesi finali**
(`pesi_finali.md`: gaussian/fine, safe_passage=connectivity, border=15, sigma=0.7, mapped=20,
cnot_high=8, magic=0, ext=−15, bfs=0.70, center_circle, packing, smart_t_routing, patience=3).
**Differenza vs il run principale**: la griglia non è quella nativa di WISQ ma **fissa a `wisq_native_side − 5`
per lato**, una sola esecuzione per circuito (`SHRINK=5 MAX_GROW=0`, nessuna crescita: chi non ci sta è *failed*).
WISQ gira sempre sulla sua griglia nativa come riferimento.
Dati da: `conn_wisq_minus5_wisqconn.csv` — `--mr_timeout 12000` s. Colonna `dim_diff_side` = wisq_x − my_x.

---

## Tabella riassuntiva delle performance

Nuova categoria rispetto ai run a griglia nativa: **il nostro mapping può fallire** (griglia troppo
stretta per il safe passage). Quei circuiti sono sconfitte nette (non riusciamo a −5).

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 139 | — |
| Errore input (qasm mancante: knn_n25) | 1 | — |
| **Nostro mapping FALLISCE a −5** (floor fisico) | 5 | — |
| **Mappiamo a −5 con successo** | 133 | — |
| ↳ WISQ va in timeout sulla sua nativa (noi vinciamo) | 4 | — |
| ↳ Entrambi completano | 129 | — |
|   ↳ Noi vinciamo su steps | 14 (ratio mediana 1.62×) | 11 (79%) |
|   ↳ Pareggio su steps | 59 | 47 (80%) |
|   ↳ WISQ vince su steps | 56 (ratio mediana 0.57×) | 53 (95%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **65 / 139 (46.8%)** | — |
| ↳ Mappiamo a −5, WISQ va in timeout | 4 / 139 (2.9%) | — |
| ↳ Vinciamo su steps (WISQ completa) | 14 / 139 (10.1%) | — |
| ↳ Pareggio su steps, noi più veloci | 47 / 139 (33.8%) | — |
| | | |
| **SCONFITTE NOSTRE (mapping fallito a −5)** | **5 / 139 (3.6%)** | — |

Circuiti dove non mappiamo a −5 (tutti piccoli, wisq_native già stretta): `bigadder_n18_transpiled`, `factor247_n15`, `grover_n10`, `hhl_n10`, `qram_n20`.

---

## Footprint: quanto scendiamo sotto WISQ

Griglia richiesta: `wisq_native − 5` per lato, un solo tentativo (grow_steps = 0 su tutti i 133 successi).

| Δ lati sotto WISQ (`dim_diff_side`) | Circuiti |
|---|---|
| −5 | 131 (target) |
| −3 | 1 (`multiplier_n45`: il nostro mapper realizza 12×12 invece del 10×10 richiesto) |
| −1 | 1 (`multiplier_n75`: realizza 16×16 invece del 12×12 richiesto) |

WISQ gira **sempre** sulla sua griglia nativa piena `2⌈√n⌉+3` (verificato quadrata, 133/133): non è
toccato dallo shrink, è il riferimento. I 2 circuiti a Δ≠5 NON sono WISQ più stretto, ma il nostro
compilatore che internamente sceglie una griglia più grande della richiesta (grow_steps=0; stesso
quirk dei `multiplier_n45/n75` nel run −4).

**Risparmio di qubit fisici** vs WISQ sui successi: mediano **46%**, medio 50% (area `my_x·my_y` vs `wisq_x·wisq_y`).

**Qualità routing −4 vs −5** (step vs WISQ, dove entrambi completano):

| Griglia | n | Win | Tie | Loss | ratio mediana wisq/noi |
|---|---|---|---|---|---|
| −4 | 129 | 13 | 64 | 52 | 1.00 |
| **−5** | 129 | 14 | 59 | 56 | 1.00 |

La mediana resta **1.00**: metà dei circuiti pareggia o batte WISQ pur stando 5 lati sotto. Scendendo da −4 a −5 si perde solo un filo (qualche pareggio → sconfitta) + 5 circuiti piccoli che non mappano più.

---

## Trade-off −5: routing steps persi vs qubit fisici risparmiati

Il prezzo dello shrink a −5. Step su 129 circuiti dove entrambi completano, qubit (area `x·y`) su tutti i 133 che mappiamo.

**A) Contro WISQ** (noi −5 vs WISQ nativa):

| | noi −5 | WISQ nativa | differenza |
|---|--------|-------------|------------|
| Routing steps (aggregato) | 273.031 | 252.078 | **+8.3%** |
| Qubit fisici (aggregato) | 24.020 | 44.189 | **−45.6%** (20.169 in meno) |

Step per-circuito: WIN 14 / TIE 59 / LOSS 56, **mediana +0%** (il +8% è aggregato, tutto dai densi). Qubit per-circuito: mediana **−45.7%**, media −49.7%.

**B) Costo puro dello shrink** (noi −5 vs noi stessi a nativa, stessa config, 133 circuiti):

| | noi nativa | noi −5 | differenza |
|---|-----------|--------|------------|
| Routing steps (aggregato) | 2.759.037 | 2.851.735 | **+3.4%** |

Mediana **+0%**, **72/133 circuiti identici** (i strutturati — ghz, vqe, wstate, ising, graphstate — gli step non dipendono dalla griglia). Il prezzo è **concentrato sui densi**: `synth_n100` +210%, `qft_n64` +169%, `qaoa_n64` +151%, `randomcircuit_n50` +136%.

> **In una riga:** −46% di qubit fisici al costo di **+8% di routing step vs WISQ** (0% sul circuito mediano), ovvero **+3.4%** come costo puro dello shrink (noi vs noi). La media per-circuito "+30/37%" è gonfiata da circuiti piccoli/densi e NON è il numero da citare.

---

## Head-to-head a −5: WISQ forzato sulla NOSTRA griglia

Run di parità (`conn_wisq_minus5_parity_wisqconn.csv`, `WISQ_GRID=parity WISQ_MAX_GROW=0`): WISQ messo sulla **stessa identica griglia −5** (verificato `dim_diff_side=0`, nessuna crescita), per **misurare** se può routare lì invece di supporlo.

Sui 133 circuiti dove noi mappiamo a −5:

| WISQ a −5 (stessa griglia) | Circuiti |
|---|---|
| **failed** (non piazza i qubit) | **131** |
| success | 2 |

I 2 `success` sono `multiplier_n45` (12×12) e `multiplier_n75` (16×16) — gli unici dove il *nostro* mapper si era auto-allargato (−3/−1, non −5), quindi la griglia è abbastanza grande per il sublattice di WISQ. **Sui circuiti realmente a native−5, WISQ fallisce 131/131 (100%).** Dove ha potuto girare, testa a testa sugli step: `multiplier_n75` noi 60 vs WISQ 62 (**win**), `multiplier_n45` 36 vs 36 (pari).

Causa architetturale: il sublattice sparso di WISQ (data-qubit su ~1 cella su 4 + bordo magic) **non sta** in `native−5`; la nativa `2⌈√n⌉+3` è il suo minimo fisico. Il nostro mapping connectivity è ~4× più denso e routa dove WISQ non piazza nemmeno i qubit. **Non è una vittoria di routing, è di footprint**: comprimiamo l'hardware dove l'architettura di WISQ non è eseguibile.

---

## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

**Metodologia**: timeout **simmetrico** a entrambi i compilatori — conta solo chi finisce entro il budget. Le 5 mancate mappature a −5 e knn restano fuori (categorie fisse).

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 139 | — |
| Errore input (knn_n25) | 1 | — |
| Nostro mapping fallisce a −5 | 5 | — |
| **WISQ non finisce in 1h** | 15 (4 fail + 11 oltre 1h) | — |
| ↳ …ma anche noi sforiamo 1h → nessun vincitore | 0 | — |
| ↳ …noi finiamo entro 1h → **vittoria** | 15 | — |
| **Entrambi finiscono in 1h** | 118 | — |
| ↳ Noi vinciamo su steps | 14 (ratio mediana 1.62×) | 11 (79%) |
| ↳ Pareggio su steps | 59 | 47 (80%) |
| ↳ WISQ vince su steps | 45 (ratio mediana 0.57×) | 42 (93%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **76 / 139 (54.7%)** | — |
| ↳ Noi finiamo, WISQ no (>1h) | 15 / 139 (10.8%) | — |
| ↳ Noi vinciamo su steps | 14 / 139 (10.1%) | — |
| ↳ Pareggio su steps, noi più veloci | 47 / 139 (33.8%) | — |

---

## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Stessa metodologia (timeout simmetrico).

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 139 | — |
| Errore input (knn_n25) | 1 | — |
| Nostro mapping fallisce a −5 | 5 | — |
| **WISQ non finisce in 30min** | 20 (4 fail + 16 oltre 30min) | — |
| ↳ …ma anche noi sforiamo 30min → nessun vincitore | 0 | — |
| ↳ …noi finiamo entro 30min → **vittoria** | 20 | — |
| **Entrambi finiscono in 30min** | 113 | — |
| ↳ Noi vinciamo su steps | 14 (ratio mediana 1.62×) | 11 (79%) |
| ↳ Pareggio su steps | 59 | 47 (80%) |
| ↳ WISQ vince su steps | 40 (ratio mediana 0.57×) | 37 (92%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **81 / 139 (58.3%)** | — |
| ↳ Noi finiamo, WISQ no (>30min) | 20 / 139 (14.4%) | — |
| ↳ Noi vinciamo su steps | 14 / 139 (10.1%) | — |
| ↳ Pareggio su steps, noi più veloci | 47 / 139 (33.8%) | — |

---

## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Stessa metodologia.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 139 | — |
| Errore input (knn_n25) | 1 | — |
| Nostro mapping fallisce a −5 | 5 | — |
| **WISQ non finisce in 15min** | 28 (4 fail + 24 oltre 15min) | — |
| ↳ …ma anche noi sforiamo 15min → nessun vincitore | 0 | — |
| ↳ …noi finiamo entro 15min → **vittoria** | 28 | — |
| **Entrambi finiscono in 15min** | 105 | — |
| ↳ Noi vinciamo su steps | 14 (ratio mediana 1.62×) | 11 (79%) |
| ↳ Pareggio su steps | 59 | 47 (80%) |
| ↳ WISQ vince su steps | 32 (ratio mediana 0.61×) | 29 (91%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **89 / 139 (64.0%)** | — |
| ↳ Noi finiamo, WISQ no (>15min) | 28 / 139 (20.1%) | — |
| ↳ Noi vinciamo su steps | 14 / 139 (10.1%) | — |
| ↳ Pareggio su steps, noi più veloci | 47 / 139 (33.8%) | — |

---

## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Stessa metodologia.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 139 | — |
| Errore input (knn_n25) | 1 | — |
| Nostro mapping fallisce a −5 | 5 | — |
| **WISQ non finisce in 10min** | 33 (4 fail + 29 oltre 10min) | — |
| ↳ …ma anche noi sforiamo 10min → nessun vincitore | 0 | — |
| ↳ …noi finiamo entro 10min → **vittoria** | 33 | — |
| **Entrambi finiscono in 10min** | 100 | — |
| ↳ Noi vinciamo su steps | 14 (ratio mediana 1.62×) | 11 (79%) |
| ↳ Pareggio su steps | 59 | 47 (80%) |
| ↳ WISQ vince su steps | 27 (ratio mediana 0.61×) | 24 (89%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **94 / 139 (67.6%)** | — |
| ↳ Noi finiamo, WISQ no (>10min) | 33 / 139 (23.7%) | — |
| ↳ Noi vinciamo su steps | 14 / 139 (10.1%) | — |
| ↳ Pareggio su steps, noi più veloci | 47 / 139 (33.8%) | — |

---

## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Stessa metodologia.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 139 | — |
| Errore input (knn_n25) | 1 | — |
| Nostro mapping fallisce a −5 | 5 | — |
| **WISQ non finisce in 5min** | 41 (4 fail + 37 oltre 5min) | — |
| ↳ …ma anche noi sforiamo 5min → nessun vincitore | 0 | — |
| ↳ …noi finiamo entro 5min → **vittoria** | 41 | — |
| **Noi non finiamo, WISQ sì → sconfitta** (overhead gaussiano) | 5 | — |
| **Entrambi finiscono in 5min** | 87 | — |
| ↳ Noi vinciamo su steps | 13 (ratio mediana 1.75×) | 11 (85%) |
| ↳ Pareggio su steps | 55 | 46 (84%) |
| ↳ WISQ vince su steps | 19 (ratio mediana 0.63×) | 17 (89%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **100 / 139 (71.9%)** | — |
| ↳ Noi finiamo, WISQ no (>5min) | 41 / 139 (29.5%) | — |
| ↳ Noi vinciamo su steps | 13 / 139 (9.4%) | — |
| ↳ Pareggio su steps, noi più veloci | 46 / 139 (33.1%) | — |

---

## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Stessa metodologia. A 1 min l'overhead gaussiano sui circuiti banali inizia a costarci.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 139 | — |
| Errore input (knn_n25) | 1 | — |
| Nostro mapping fallisce a −5 | 5 | — |
| **WISQ non finisce in 1min** | 52 (4 fail + 48 oltre 1min) | — |
| ↳ …ma anche noi sforiamo 1min → nessun vincitore | 3 | — |
| ↳ …noi finiamo entro 1min → **vittoria** | 49 | — |
| **Noi non finiamo, WISQ sì → sconfitta** (overhead gaussiano) | 13 | — |
| **Entrambi finiscono in 1min** | 68 | — |
| ↳ Noi vinciamo su steps | 11 (ratio mediana 1.75×) | 11 (100%) |
| ↳ Pareggio su steps | 49 | 45 (92%) |
| ↳ WISQ vince su steps | 8 (ratio mediana 0.69×) | 8 (100%) |
| | | |
| **TOTALE VITTORIE NOSTRE** | **105 / 139 (75.5%)** ⟵ picco | — |
| ↳ Noi finiamo, WISQ no (>1min) | 49 / 139 (35.3%) | — |
| ↳ Noi vinciamo su steps | 11 / 139 (7.9%) | — |
| ↳ Pareggio su steps, noi più veloci | 45 / 139 (32.4%) | — |

---

## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (asimm.) | 129 | 4 | 0 | 0 | **65 (46.8%)** |
| 1 ora | 118 | 15 | 0 | 0 | **76 (54.7%)** |
| 30 min | 113 | 20 | 0 | 0 | **81 (58.3%)** |
| 15 min | 105 | 28 | 0 | 0 | **89 (64.0%)** |
| 10 min | 100 | 33 | 0 | 0 | **94 (67.6%)** |
| 5 min | 87 | 41 | 5 | 0 | **100 (71.9%)** |
| 1 min | 68 | 49 | 13 | 3 | **105 (75.5%)** ⟵ picco |

NB: oltre i 6 fuori (5 mapping-fail a −5 + knn) il tetto delle vittorie è 133. Stesso andamento dei due doc a griglia nativa (cresce stringendo il budget, picco, poi cala per il nostro overhead sui banali).

---

## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s` sui 133 circuiti che mappiamo a −5. Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). I timeout WISQ inclusi con la durata registrata (~12000 s).

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 133 | 115 (86%) | 485× | 745× | 0.01× | 19455× |
| ↳ Dove vinciamo su steps | 14 | 11 (79%) | 288× | 270× | 0.02× | 644× |
| ↳ In pareggio su steps | 59 | 47 (80%) | 433× | 500× | 0.01× | 2561× |
| ↳ Dove WISQ vince su steps | 56 | 53 (95%) | 624× | 1132× | 0.02× | 19455× |
| ↳ WISQ in timeout | 4 | 4 (100%) | 232× | 595× | 125.92× | 1790× |

---

## Per famiglia di circuiti

**WISQ timeout** = mr_timeout=12000s. **MapFail** = il nostro mapping non riesce a −5. Win/=/Loss sugli step dove entrambi completano.

| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | MapFail −5 | Err | Note |
|--------|---|-----|----------------|------|--------------|-----------|-----|------|
| 19qubits | 2 | 0 | 0 (0 noi+veloci) | 2 | 0 | 0 | 0 | n=19 |
| 53qubits | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | 0 | n=27–39 |
| adder | 3 | 0 | 2 (1 noi+veloci) | 0 | 0 | 1 | 0 | n=28–64 |
| bwt | 4 | 0 | 0 (0 noi+veloci) | 2 | 2 | 0 | 0 | n=21–73 |
| dnn | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | 0 | n=16 |
| factor247 | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | 0 |  |
| ghz | 10 | 0 | 10 (10 noi+veloci) | 0 | 0 | 0 | 0 | n=10–100 |
| ghz_state | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=23 |
| graphstate | 10 | 4 | 6 (4 noi+veloci) | 0 | 0 | 0 | 0 | n=10–100 |
| grover | 2 | 0 | 0 (0 noi+veloci) | 0 | 1 | 1 | 0 | n=20 |
| hhl | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | 0 |  |
| ising | 11 | 10 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=10–100 |
| knn | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 0 | 1 |  |
| multiplier | 8 | 0 | 3 (0 noi+veloci) | 4 | 1 | 0 | 0 | n=9–100 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=6 |
| qaoa | 11 | 0 | 0 (0 noi+veloci) | 11 | 0 | 0 | 0 | n=10–100 |
| qft | 12 | 0 | 0 (0 noi+veloci) | 12 | 0 | 0 | 0 | n=10–100 |
| qram | 1 | 0 | 0 (0 noi+veloci) | 0 | 0 | 1 | 0 |  |
| randomcircuit | 1 | 0 | 0 (0 noi+veloci) | 1 | 0 | 0 | 0 | n=50 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=11 |
| square_root | 2 | 0 | 1 (1 noi+veloci) | 1 | 0 | 0 | 0 | n=14–32 |
| synth | 12 | 0 | 0 (0 noi+veloci) | 12 | 0 | 0 | 0 | n=50–100 |
| vqe_real_amp | 10 | 0 | 10 (9 noi+veloci) | 0 | 0 | 0 | 0 | n=10–100 |
| vqe_su2 | 10 | 0 | 10 (8 noi+veloci) | 0 | 0 | 0 | 0 | n=10–100 |
| vqe_two_local | 10 | 0 | 0 (0 noi+veloci) | 10 | 0 | 0 | 0 | n=10–100 |
| wstate | 11 | 0 | 11 (8 noi+veloci) | 0 | 0 | 0 | 0 | n=10–100 |

---

## Per circuito (dettaglio)

**Δlati** = quanti lati sotto WISQ (`dim_diff_side`). **Steps**: WIN/=/LOSS sugli step. **MapFail** = mapping non riuscito a −5. **WISQ failed** = mr_timeout=12000s.

| # | Circuit | Qubits | Grid (nostra) | Δlati | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |
|---|---------|--------|---------------|-------|----------|------------|-------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 8×8 | −5 | 104 | 99 | 0.9519 | success | LOSS | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 8×8 | −5 | 288 | 286 | 0.9931 | success | LOSS | noi +veloci |
| 3 | 53qubits_155gate_57layers | 27 | 10×10 | −5 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 4 | 53qubits_332gate_152layers | 39 | 12×12 | −5 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 10×10 | −5 | 24 | 24 | 1.0000 | success | = | WISQ +veloce |
| 6 | adder_n64_transpiled | 64 | 14×14 | −5 | 181 | 181 | 1.0000 | success | = | noi +veloci |
| 7 | bigadder_n18_transpiled | — | — | — | — | — | — | — | **MapFail −5** | — |
| 8 | bwt_n21 | 21 | 8×8 | −5 | 116400 | — | — | failed | **WIN (timeout)** | — |
| 9 | bwt_n37 | 28 | 10×10 | −5 | 33639 | 33600 | 0.9988 | success | LOSS | noi +veloci |
| 10 | bwt_n57 | 43 | 12×12 | −5 | 65619 | 65600 | 0.9997 | success | LOSS | noi +veloci |
| 11 | bwt_n97 | 73 | 16×16 | −5 | 129710 | — | — | failed | **WIN (timeout)** | — |
| 12 | dnn_n16 | 16 | 6×6 | −5 | 71 | 53 | 0.7465 | success | LOSS | noi +veloci |
| 13 | factor247_n15 | — | — | — | — | — | — | — | **MapFail −5** | — |
| 14 | ghz_n10 | 10 | 6×6 | −5 | 9 | 9 | 1.0000 | success | = | noi +veloci |
| 15 | ghz_n100 | 100 | 18×18 | −5 | 99 | 99 | 1.0000 | success | = | noi +veloci |
| 16 | ghz_n20 | 20 | 8×8 | −5 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 17 | ghz_n30 | 30 | 10×10 | −5 | 29 | 29 | 1.0000 | success | = | noi +veloci |
| 18 | ghz_n40 | 40 | 12×12 | −5 | 39 | 39 | 1.0000 | success | = | noi +veloci |
| 19 | ghz_n50 | 50 | 14×14 | −5 | 49 | 49 | 1.0000 | success | = | noi +veloci |
| 20 | ghz_n60 | 60 | 14×14 | −5 | 59 | 59 | 1.0000 | success | = | noi +veloci |
| 21 | ghz_n70 | 70 | 16×16 | −5 | 69 | 69 | 1.0000 | success | = | noi +veloci |
| 22 | ghz_n80 | 80 | 16×16 | −5 | 79 | 79 | 1.0000 | success | = | noi +veloci |
| 23 | ghz_n90 | 90 | 18×18 | −5 | 89 | 89 | 1.0000 | success | = | noi +veloci |
| 24 | ghz_state_n23 | 23 | 8×8 | −5 | 22 | 22 | 1.0000 | success | = | noi +veloci |
| 25 | graphstate_n10 | 10 | 6×6 | −5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 26 | graphstate_n100 | 100 | 18×18 | −5 | 8 | 8 | 1.0000 | success | = | noi +veloci |
| 27 | graphstate_n20 | 20 | 8×8 | −5 | 4 | 4 | 1.0000 | success | = | WISQ +veloce |
| 28 | graphstate_n30 | 30 | 10×10 | −5 | 6 | 6 | 1.0000 | success | = | noi +veloci |
| 29 | graphstate_n40 | 40 | 12×12 | −5 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 30 | graphstate_n50 | 50 | 14×14 | −5 | 5 | 5 | 1.0000 | success | = | WISQ +veloce |
| 31 | graphstate_n60 | 60 | 14×14 | −5 | 5 | 5 | 1.0000 | success | = | noi +veloci |
| 32 | graphstate_n70 | 70 | 16×16 | −5 | 6 | 7 | 1.1667 | success | **WIN** | noi +veloci |
| 33 | graphstate_n80 | 80 | 16×16 | −5 | 6 | 7 | 1.1667 | success | **WIN** | noi +veloci |
| 34 | graphstate_n90 | 90 | 18×18 | −5 | 5 | 6 | 1.2000 | success | **WIN** | noi +veloci |
| 35 | grover_n10 | — | — | — | — | — | — | — | **MapFail −5** | — |
| 36 | grover_n20 | 20 | 8×8 | −5 | 2219760 | — | — | failed | **WIN (timeout)** | — |
| 37 | hhl_n10 | — | — | — | — | — | — | — | **MapFail −5** | — |
| 38 | ising_n10 | 10 | 6×6 | −5 | 4 | 4 | 1.0000 | success | = | noi +veloci |
| 39 | ising_n100 | 100 | 18×18 | −5 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 40 | ising_n20 | 20 | 8×8 | −5 | 4 | 5 | 1.2500 | success | **WIN** | noi +veloci |
| 41 | ising_n26 | 26 | 10×10 | −5 | 4 | 5 | 1.2500 | success | **WIN** | WISQ +veloce |
| 42 | ising_n30 | 30 | 10×10 | −5 | 4 | 6 | 1.5000 | success | **WIN** | WISQ +veloce |
| 43 | ising_n40 | 40 | 12×12 | −5 | 4 | 7 | 1.7500 | success | **WIN** | noi +veloci |
| 44 | ising_n50 | 50 | 14×14 | −5 | 4 | 8 | 2.0000 | success | **WIN** | noi +veloci |
| 45 | ising_n60 | 60 | 14×14 | −5 | 4 | 9 | 2.2500 | success | **WIN** | WISQ +veloce |
| 46 | ising_n70 | 70 | 16×16 | −5 | 4 | 10 | 2.5000 | success | **WIN** | noi +veloci |
| 47 | ising_n80 | 80 | 16×16 | −5 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 48 | ising_n90 | 90 | 18×18 | −5 | 4 | 12 | 3.0000 | success | **WIN** | noi +veloci |
| 49 | knn_n25 | — | — | — | — | — | — | error (input) | ERR | — |
| 50 | multiplier_n100 | 100 | 18×18 | −5 | 112834 | — | — | failed | **WIN (timeout)** | — |
| 51 | multiplier_n15 | 9 | 4×4 | −5 | 12 | 12 | 1.0000 | success | = | WISQ +veloce |
| 52 | multiplier_n20 | 20 | 8×8 | −5 | 4034 | 3990 | 0.9891 | success | LOSS | noi +veloci |
| 53 | multiplier_n40 | 40 | 12×12 | −5 | 17411 | 17329 | 0.9953 | success | LOSS | noi +veloci |
| 54 | multiplier_n45 | 27 | 12×12 | −3 | 36 | 36 | 1.0000 | success | = | WISQ +veloce |
| 55 | multiplier_n60 | 60 | 14×14 | −5 | 40114 | 39730 | 0.9904 | success | LOSS | noi +veloci |
| 56 | multiplier_n75 | 45 | 16×16 | −1 | 60 | 60 | 1.0000 | success | = | WISQ +veloce |
| 57 | multiplier_n80 | 80 | 16×16 | −5 | 72016 | 71289 | 0.9899 | success | LOSS | noi +veloci |
| 58 | multiply_n13 | 6 | 4×4 | −5 | 2 | 2 | 1.0000 | success | = | noi +veloci |
| 59 | qaoa_n10 | 10 | 6×6 | −5 | 50 | 46 | 0.9200 | success | LOSS | noi +veloci |
| 60 | qaoa_n100 | 100 | 18×18 | −5 | 1958 | 888 | 0.4535 | success | LOSS | noi +veloci |
| 61 | qaoa_n20 | 20 | 8×8 | −5 | 138 | 90 | 0.6522 | success | LOSS | noi +veloci |
| 62 | qaoa_n30 | 30 | 10×10 | −5 | 265 | 139 | 0.5245 | success | LOSS | WISQ +veloce |
| 63 | qaoa_n40 | 40 | 12×12 | −5 | 319 | 202 | 0.6332 | success | LOSS | noi +veloci |
| 64 | qaoa_n50 | 50 | 14×14 | −5 | 415 | 282 | 0.6795 | success | LOSS | noi +veloci |
| 65 | qaoa_n60 | 60 | 14×14 | −5 | 1091 | 381 | 0.3492 | success | LOSS | noi +veloci |
| 66 | qaoa_n64 | 64 | 14×14 | −5 | 1252 | 426 | 0.3403 | success | LOSS | noi +veloci |
| 67 | qaoa_n70 | 70 | 16×16 | −5 | 845 | 475 | 0.5621 | success | LOSS | noi +veloci |
| 68 | qaoa_n80 | 80 | 16×16 | −5 | 1590 | 587 | 0.3692 | success | LOSS | noi +veloci |
| 69 | qaoa_n90 | 90 | 18×18 | −5 | 1207 | 725 | 0.6007 | success | LOSS | noi +veloci |
| 70 | qft_n10 | 10 | 6×6 | −5 | 47 | 34 | 0.7234 | success | LOSS | WISQ +veloce |
| 71 | qft_n100 | 100 | 18×18 | −5 | 774 | 438 | 0.5659 | success | LOSS | noi +veloci |
| 72 | qft_n18 | 18 | 8×8 | −5 | 102 | 71 | 0.6961 | success | LOSS | noi +veloci |
| 73 | qft_n20 | 20 | 8×8 | −5 | 143 | 83 | 0.5804 | success | LOSS | noi +veloci |
| 74 | qft_n30 | 30 | 10×10 | −5 | 267 | 134 | 0.5019 | success | LOSS | noi +veloci |
| 75 | qft_n40 | 40 | 12×12 | −5 | 316 | 179 | 0.5665 | success | LOSS | noi +veloci |
| 76 | qft_n50 | 50 | 14×14 | −5 | 349 | 220 | 0.6304 | success | LOSS | noi +veloci |
| 77 | qft_n60 | 60 | 14×14 | −5 | 682 | 270 | 0.3959 | success | LOSS | noi +veloci |
| 78 | qft_n64 | 64 | 14×14 | −5 | 915 | 290 | 0.3169 | success | LOSS | noi +veloci |
| 79 | qft_n70 | 70 | 16×16 | −5 | 504 | 309 | 0.6131 | success | LOSS | noi +veloci |
| 80 | qft_n80 | 80 | 16×16 | −5 | 933 | 360 | 0.3859 | success | LOSS | noi +veloci |
| 81 | qft_n90 | 90 | 18×18 | −5 | 590 | 392 | 0.6644 | success | LOSS | noi +veloci |
| 82 | qram_n20 | — | — | — | — | — | — | — | **MapFail −5** | — |
| 83 | randomcircuit_n50 | 50 | 14×14 | −5 | 3565 | 1436 | 0.4028 | success | LOSS | noi +veloci |
| 84 | seca_n11 | 11 | 6×6 | −5 | 19 | 19 | 1.0000 | success | = | noi +veloci |
| 85 | square_root_n18 | 14 | 6×6 | −5 | 28 | 27 | 0.9643 | success | LOSS | WISQ +veloce |
| 86 | square_root_n45 | 32 | 10×10 | −5 | 570 | 570 | 1.0000 | success | = | noi +veloci |
| 87 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 18×18 | −5 | 762 | 154 | 0.2021 | success | LOSS | noi +veloci |
| 88 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 18×18 | −5 | 801 | 192 | 0.2397 | success | LOSS | noi +veloci |
| 89 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 18×18 | −5 | 563 | 204 | 0.3623 | success | LOSS | noi +veloci |
| 90 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 18×18 | −5 | 1433 | 386 | 0.2694 | success | LOSS | noi +veloci |
| 91 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 18×18 | −5 | 1057 | 392 | 0.3709 | success | LOSS | noi +veloci |
| 92 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 18×18 | −5 | 1087 | 432 | 0.3974 | success | LOSS | noi +veloci |
| 93 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 14×14 | −5 | 147 | 60 | 0.4082 | success | LOSS | noi +veloci |
| 94 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 14×14 | −5 | 144 | 68 | 0.4722 | success | LOSS | noi +veloci |
| 95 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 14×14 | −5 | 164 | 71 | 0.4329 | success | LOSS | noi +veloci |
| 96 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 14×14 | −5 | 265 | 133 | 0.5019 | success | LOSS | noi +veloci |
| 97 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 14×14 | −5 | 329 | 146 | 0.4438 | success | LOSS | noi +veloci |
| 98 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 14×14 | −5 | 233 | 142 | 0.6094 | success | LOSS | noi +veloci |
| 99 | vqe_real_amp_n10 | 10 | 6×6 | −5 | 13 | 13 | 1.0000 | success | = | noi +veloci |
| 100 | vqe_real_amp_n100 | 100 | 18×18 | −5 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 101 | vqe_real_amp_n20 | 20 | 8×8 | −5 | 23 | 23 | 1.0000 | success | = | noi +veloci |
| 102 | vqe_real_amp_n30 | 30 | 10×10 | −5 | 33 | 33 | 1.0000 | success | = | WISQ +veloce |
| 103 | vqe_real_amp_n40 | 40 | 12×12 | −5 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 104 | vqe_real_amp_n50 | 50 | 14×14 | −5 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 105 | vqe_real_amp_n60 | 60 | 14×14 | −5 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 106 | vqe_real_amp_n70 | 70 | 16×16 | −5 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 107 | vqe_real_amp_n80 | 80 | 16×16 | −5 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 108 | vqe_real_amp_n90 | 90 | 18×18 | −5 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 109 | vqe_su2_n10 | 10 | 6×6 | −5 | 13 | 13 | 1.0000 | success | = | WISQ +veloce |
| 110 | vqe_su2_n100 | 100 | 18×18 | −5 | 103 | 103 | 1.0000 | success | = | noi +veloci |
| 111 | vqe_su2_n20 | 20 | 8×8 | −5 | 23 | 23 | 1.0000 | success | = | WISQ +veloce |
| 112 | vqe_su2_n30 | 30 | 10×10 | −5 | 33 | 33 | 1.0000 | success | = | noi +veloci |
| 113 | vqe_su2_n40 | 40 | 12×12 | −5 | 43 | 43 | 1.0000 | success | = | noi +veloci |
| 114 | vqe_su2_n50 | 50 | 14×14 | −5 | 53 | 53 | 1.0000 | success | = | noi +veloci |
| 115 | vqe_su2_n60 | 60 | 14×14 | −5 | 63 | 63 | 1.0000 | success | = | noi +veloci |
| 116 | vqe_su2_n70 | 70 | 16×16 | −5 | 73 | 73 | 1.0000 | success | = | noi +veloci |
| 117 | vqe_su2_n80 | 80 | 16×16 | −5 | 83 | 83 | 1.0000 | success | = | noi +veloci |
| 118 | vqe_su2_n90 | 90 | 18×18 | −5 | 93 | 93 | 1.0000 | success | = | noi +veloci |
| 119 | vqe_two_local_n10 | 10 | 6×6 | −5 | 57 | 39 | 0.6842 | success | LOSS | noi +veloci |
| 120 | vqe_two_local_n100 | 100 | 18×18 | −5 | 2858 | 1397 | 0.4888 | success | LOSS | noi +veloci |
| 121 | vqe_two_local_n20 | 20 | 8×8 | −5 | 197 | 98 | 0.4975 | success | LOSS | noi +veloci |
| 122 | vqe_two_local_n30 | 30 | 10×10 | −5 | 373 | 184 | 0.4933 | success | LOSS | noi +veloci |
| 123 | vqe_two_local_n40 | 40 | 12×12 | −5 | 417 | 290 | 0.6954 | success | LOSS | noi +veloci |
| 124 | vqe_two_local_n50 | 50 | 14×14 | −5 | 618 | 413 | 0.6683 | success | LOSS | noi +veloci |
| 125 | vqe_two_local_n60 | 60 | 14×14 | −5 | 1514 | 580 | 0.3831 | success | LOSS | noi +veloci |
| 126 | vqe_two_local_n70 | 70 | 16×16 | −5 | 1080 | 728 | 0.6741 | success | LOSS | noi +veloci |
| 127 | vqe_two_local_n80 | 80 | 16×16 | −5 | 2298 | 948 | 0.4125 | success | LOSS | noi +veloci |
| 128 | vqe_two_local_n90 | 90 | 18×18 | −5 | 1618 | 1136 | 0.7021 | success | LOSS | noi +veloci |
| 129 | wstate_n10 | 10 | 6×6 | −5 | 11 | 11 | 1.0000 | success | = | WISQ +veloce |
| 130 | wstate_n100 | 100 | 18×18 | −5 | 101 | 101 | 1.0000 | success | = | noi +veloci |
| 131 | wstate_n20 | 20 | 8×8 | −5 | 21 | 21 | 1.0000 | success | = | WISQ +veloce |
| 132 | wstate_n27 | 27 | 10×10 | −5 | 28 | 28 | 1.0000 | success | = | noi +veloci |
| 133 | wstate_n30 | 30 | 10×10 | −5 | 31 | 31 | 1.0000 | success | = | noi +veloci |
| 134 | wstate_n40 | 40 | 12×12 | −5 | 41 | 41 | 1.0000 | success | = | noi +veloci |
| 135 | wstate_n50 | 50 | 14×14 | −5 | 51 | 51 | 1.0000 | success | = | noi +veloci |
| 136 | wstate_n60 | 60 | 14×14 | −5 | 61 | 61 | 1.0000 | success | = | noi +veloci |
| 137 | wstate_n70 | 70 | 16×16 | −5 | 71 | 71 | 1.0000 | success | = | noi +veloci |
| 138 | wstate_n80 | 80 | 16×16 | −5 | 81 | 81 | 1.0000 | success | = | noi +veloci |
| 139 | wstate_n90 | 90 | 18×18 | −5 | 91 | 91 | 1.0000 | success | = | WISQ +veloce |
