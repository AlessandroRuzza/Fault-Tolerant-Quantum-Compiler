# Risultati sweep WISQ-native — cube (2026-06-24)

Config: `data/config/cube_summary_all.json` — tutti i 263 circuiti, parametri cube
dalla tabella riassuntiva di `pesi_tunati.md` (gaussian/fine, safe_passage=cube,
border=5, sigma=0.7, mapped=15, cnot_high=6, magic_high=0.7, magic_low=0,
ext=−15, bfs=0.70, center_circle, packing, smart_t_routing).
Griglia WISQ-native (`wisq_native_side = 2⌈√n⌉+3`).
Fallback: se cube fallisce mapping → retry con connectivity (border=15, mapped=20, cnot=8, magic=0, ext=−15, σ=0.7).
Dati da: `cube_summary_all_wisq_dinuovo.csv` — `--mr_timeout 12000` s (3h20m per circuito).

---

## Tabella riassuntiva delle performance

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ va in timeout** (mr_timeout=12000s) | 17 | — |
| ⚠ Sovrapposizione (noi ERR **e** WISQ timeout) | **0** — insiemi disgiunti | — |
| Entrambi completano | 244 | — |
| ↳ Noi vinciamo su steps | 48 (ratio mediana 1.50×) | — |
| ↳ Pareggio su steps | 110 | 93 (85%) |
| ↳ WISQ vince su steps | 86 (ratio mediana 0.87×) | — |
| **Fallback connectivity attivato** | 47 | — |
| ↳ Fallback: noi vinciamo su steps | 10 | — |
| ↳ Fallback: pareggio | 17 | 17 (100%) |
| ↳ Fallback: WISQ vince su steps | 7 | — |
| ↳ Fallback: WISQ va in timeout | 13 | — |
| Fallback fallito (anche conn fallisce) | 0 | — |
| | | |
| **TOTALE VITTORIE NOSTRE** | **158 / 263 (60.1%)** | — |
| ↳ Noi completiamo, WISQ va in timeout | 17 / 263 (6.5%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 48 / 263 (18.3%) | — |
| ↳ Pareggio su steps, noi più veloci | 93 / 263 (35.4%) | — |

---

## Tabella riassuntiva — budget wall-clock 1 ora (3600 s)

**Metodologia** — qui il timeout è imposto **simmetricamente a entrambi i compilatori**:
un'esecuzione "conta" solo se ha finito entro 3600 s (`my_duration_s`/`wisq_duration_s`),
altrimenti è un timeout. Rispetto al run reale (mr_timeout=12000 s solo per WISQ):
i run WISQ che avevano completato in >1h diventano timeout → nostre vittorie (noi finiamo
entro 1h su tutti); i 4 circuiti giganti `multiplier_n300/n400`, `randomcircuit_n400/n500`
sforano 1h **da entrambe le parti** → nessun vincitore.

> ⚠ La tabella originale a 12000 s conta 17 timeout WISQ / 158 vittorie perché il nostro
> lato non aveva un cap hard. Con un budget **simmetrico** a 12000 s, 3 di quei circuiti
> (`multiplier_n400`, `randomcircuit_n400/n500`) sforano anche da parte nostra → 14 timeout / 155 vittorie.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 1h** | 55 (17 fail + 38 oltre 1h) | — |
| ↳ …ma anche noi sforiamo 1h → nessun vincitore | 4 | — |
| ↳ …noi finiamo entro 1h → **vittoria** | 51 | — |
| ⚠ Sovrapposizione (noi ERR **e** WISQ timeout) | **0** — insiemi disgiunti | — |
| **Entrambi finiscono in 1h** | 206 | — |
| ↳ Noi vinciamo su steps | 43 (ratio mediana 1.67×) | 35 (81%) |
| ↳ Pareggio su steps | 105 | 88 (84%) |
| ↳ WISQ vince su steps | 58 (ratio mediana 0.92×) | 57 (98%) |
| **Fallback connectivity attivato** | 47 | — |
| ↳ Fallback: noi vinciamo su steps | 8 | — |
| ↳ Fallback: pareggio | 16 | 16 (100%) |
| ↳ Fallback: WISQ vince su steps | 1 | — |
| ↳ Fallback: WISQ non finisce in 1h | 22 (18 vittoria + 4 nessun vincitore) | — |
| | | |
| **TOTALE VITTORIE NOSTRE** | **182 / 263 (69.2%)** | — |
| ↳ Noi finiamo, WISQ no (>1h) | 51 / 263 (19.4%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 43 / 263 (16.3%) | — |
| ↳ Pareggio su steps, noi più veloci | 88 / 263 (33.5%) | — |

---

## Tabella riassuntiva — budget wall-clock 30 minuti (1800 s)

Stessa metodologia (timeout simmetrico): conta solo chi finisce entro 1800 s. I 4 circuiti
giganti sforano 30 min da entrambe le parti → nessun vincitore.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 30min** | 66 (17 fail + 49 oltre 30min) | — |
| ↳ …ma anche noi sforiamo 30min → nessun vincitore | 4 | — |
| ↳ …noi finiamo entro 30min → **vittoria** | 62 | — |
| ⚠ Sovrapposizione (noi ERR **e** WISQ timeout) | **0** — insiemi disgiunti | — |
| **Entrambi finiscono in 30min** | 195 | — |
| ↳ Noi vinciamo su steps | 42 (ratio mediana 1.76×) | 34 (81%) |
| ↳ Pareggio su steps | 105 | 88 (84%) |
| ↳ WISQ vince su steps | 48 (ratio mediana 0.93×) | 47 (98%) |
| **Fallback connectivity attivato** | 47 | — |
| ↳ Fallback: noi vinciamo su steps | 8 | — |
| ↳ Fallback: pareggio | 16 | 16 (100%) |
| ↳ Fallback: WISQ vince su steps | 1 | — |
| ↳ Fallback: WISQ non finisce in 30min | 22 (18 vittoria + 4 nessun vincitore) | — |
| | | |
| **TOTALE VITTORIE NOSTRE** | **192 / 263 (73.0%)** | — |
| ↳ Noi finiamo, WISQ no (>30min) | 62 / 263 (23.6%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 42 / 263 (16.0%) | — |
| ↳ Pareggio su steps, noi più veloci | 88 / 263 (33.5%) | — |

---

## Tabella riassuntiva — budget wall-clock 15 minuti (900 s)

Stessa metodologia (timeout simmetrico): conta solo chi finisce entro 900 s. A 15 min
i circuiti che sforano **da entrambe le parti** salgono a 7 (`qaoa_n400`, `vqe_two_local_n400`,
`multiplier_n200/n300/n400`, `randomcircuit_n400/n500`) → nessun vincitore.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 15min** | 79 (17 fail + 62 oltre 15min) | — |
| ↳ …ma anche noi sforiamo 15min → nessun vincitore | 7 | — |
| ↳ …noi finiamo entro 15min → **vittoria** | 72 | — |
| ⚠ Sovrapposizione (noi ERR **e** WISQ timeout) | **0** — insiemi disgiunti | — |
| **Entrambi finiscono in 15min** | 182 | — |
| ↳ Noi vinciamo su steps | 42 (ratio mediana 1.76×) | 34 (81%) |
| ↳ Pareggio su steps | 101 | 84 (83%) |
| ↳ WISQ vince su steps | 39 (ratio mediana 0.95×) | 38 (97%) |
| **Fallback connectivity attivato** | 47 | — |
| ↳ Fallback: noi vinciamo su steps | 8 | — |
| ↳ Fallback: pareggio | 12 | 12 (100%) |
| ↳ Fallback: WISQ vince su steps | 1 | — |
| ↳ Fallback: WISQ non finisce in 15min | 26 (19 vittoria + 7 nessun vincitore) | — |
| | | |
| **TOTALE VITTORIE NOSTRE** | **198 / 263 (75.3%)** | — |
| ↳ Noi finiamo, WISQ no (>15min) | 72 / 263 (27.4%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 42 / 263 (16.0%) | — |
| ↳ Pareggio su steps, noi più veloci | 84 / 263 (31.9%) | — |

---

## Tabella riassuntiva — budget wall-clock 10 minuti (600 s)

Stessa metodologia (timeout simmetrico): conta solo chi finisce entro 600 s. Sforano da
entrambe le parti 9 circuiti → nessun vincitore. **Da qui in giù compare un nuovo effetto**:
il nostro overhead di mapping gaussiano (~300–480 s costanti anche su circuiti banali) inizia
ad avvicinarsi al budget; a 10 min non ci penalizza ancora (0 nostri timeout), ma vedi 5 e 1 min.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 10min** | 85 (17 fail + 68 oltre 10min) | — |
| ↳ …ma anche noi sforiamo 10min → nessun vincitore | 9 | — |
| ↳ …noi finiamo entro 10min → **vittoria** | 76 | — |
| Noi non finiamo, WISQ sì → sconfitta | 0 | — |
| **Entrambi finiscono in 10min** | 176 | — |
| ↳ Noi vinciamo su steps | 42 (ratio mediana 1.76×) | 34 (81%) |
| ↳ Pareggio su steps | 100 | 83 (83%) |
| ↳ WISQ vince su steps | 34 (ratio mediana 0.96×) | 33 (97%) |
| **Fallback connectivity attivato** | 47 | — |
| ↳ Fallback: noi vinciamo su steps | 8 | — |
| ↳ Fallback: pareggio | 11 | 11 (100%) |
| ↳ Fallback: WISQ vince su steps | 1 | — |
| ↳ Fallback: WISQ non finisce in 10min | 27 (18 vittoria + 9 nessun vincitore) | — |
| | | |
| **TOTALE VITTORIE NOSTRE** | **201 / 263 (76.4%)** | — |
| ↳ Noi finiamo, WISQ no (>10min) | 76 / 263 (28.9%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 42 / 263 (16.0%) | — |
| ↳ Pareggio su steps, noi più veloci | 83 / 263 (31.6%) | — |

---

## Tabella riassuntiva — budget wall-clock 5 minuti (300 s)

Stessa metodologia. Qui l'overhead gaussiano comincia a costarci: **10 circuiti banali**
(`ghz_n10/n30/n100`, `example`, `parallel`, `cat_n130`, `graphstate_n60/n100`, `53qubits_155gate`,
`adder_n64_transpiled`) — dove WISQ finisce in ~4 s — superano i 300 s dal nostro lato e
diventano sconfitte. Nonostante ciò il bilancio è ancora il migliore (picco) perché i molti
circuiti grandi dove WISQ sfora 5 min pesano di più.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 5min** | 99 (17 fail + 82 oltre 5min) | — |
| ↳ …ma anche noi sforiamo 5min → nessun vincitore | 11 | — |
| ↳ …noi finiamo entro 5min → **vittoria** | 88 | — |
| **Noi non finiamo, WISQ sì → sconfitta** (overhead gaussiano) | 10 | — |
| **Entrambi finiscono in 5min** | 152 | — |
| ↳ Noi vinciamo su steps | 40 (ratio mediana 1.87×) | 33 (83%) |
| ↳ Pareggio su steps | 88 | 80 (91%) |
| ↳ WISQ vince su steps | 24 (ratio mediana 0.97×) | 23 (96%) |
| **Fallback connectivity attivato** | 47 | — |
| ↳ Fallback: noi vinciamo su steps | 8 | — |
| ↳ Fallback: pareggio | 9 | 9 (100%) |
| ↳ Fallback: WISQ vince su steps | 1 | — |
| ↳ Fallback: WISQ non finisce in 5min | 29 (18 vittoria + 11 nessun vincitore) | — |
| | | |
| **TOTALE VITTORIE NOSTRE** | **208 / 263 (79.1%)** ⟵ picco | — |
| ↳ Noi finiamo, WISQ no (>5min) | 88 / 263 (33.5%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 40 / 263 (15.2%) | — |
| ↳ Pareggio su steps, noi più veloci | 80 / 263 (30.4%) | — |

---

## Tabella riassuntiva — budget wall-clock 1 minuto (60 s)

Stessa metodologia. A 1 min l'overhead gaussiano ci penalizza pesantemente: **23 circuiti**
(quasi tutti piccoli/strutturati — ghz, graphstate, ising, dnn, qaoa_n20…) li perdiamo perché
WISQ li chiude in pochi secondi mentre noi superiamo i 60 s. Il win-rate **scende** sotto il
picco dei 5 min. 30 circuiti grandi sforano da entrambe le parti.

| Categoria | Circuiti | Di cui noi +veloci |
|-----------|----------|--------------------|
| **Totale circuiti** | 263 | — |
| Errore nostro (input mancante) | 2 | — |
| **WISQ non finisce in 1min** | 127 (17 fail + 110 oltre 1min) | — |
| ↳ …ma anche noi sforiamo 1min → nessun vincitore | 30 | — |
| ↳ …noi finiamo entro 1min → **vittoria** | 97 | — |
| **Noi non finiamo, WISQ sì → sconfitta** (overhead gaussiano) | 23 | — |
| **Entrambi finiscono in 1min** | 111 | — |
| ↳ Noi vinciamo su steps | 28 (ratio mediana 2.00×) | 28 (100%) |
| ↳ Pareggio su steps | 72 | 70 (97%) |
| ↳ WISQ vince su steps | 11 (ratio mediana 0.98×) | 11 (100%) |
| **Fallback connectivity attivato** | 47 | — |
| ↳ Fallback: noi vinciamo su steps | 7 | — |
| ↳ Fallback: pareggio | 6 | 6 (100%) |
| ↳ Fallback: WISQ vince su steps | 0 | — |
| ↳ Fallback: WISQ non finisce / noi timeout | 34 (18 vittoria + 15 nessun vincitore + 1 sconfitta) | — |
| | | |
| **TOTALE VITTORIE NOSTRE** | **195 / 263 (74.1%)** | — |
| ↳ Noi finiamo, WISQ no (>1min) | 97 / 263 (36.9%) | — |
| ↳ Noi vinciamo su steps (WISQ completa) | 28 / 263 (10.6%) | — |
| ↳ Pareggio su steps, noi più veloci | 70 / 263 (26.6%) | — |

---

## Andamento del win-rate al variare del budget wall-clock

| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |
|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|
| 12000 s (orig., asimm.) | 244 | 17 | 0 | 0 | **158 (60.1%)** |
| 1 ora | 206 | 51 | 0 | 4 | 182 (69.2%) |
| 30 min | 195 | 62 | 0 | 4 | 192 (73.0%) |
| 15 min | 182 | 72 | 0 | 7 | 198 (75.3%) |
| 10 min | 176 | 76 | 0 | 9 | 201 (76.4%) |
| **5 min** | 152 | 88 | 10 | 11 | **208 (79.1%) ⟵ picco** |
| 1 min | 111 | 97 | 23 | 30 | 195 (74.1%) |

Il win-rate cresce stringendo il budget (le sconfitte su steps, lente lato WISQ, cadono nel
bucket timeout) fino a un **picco ~79% a 5 min**, poi cala: sotto i 5 min il nostro overhead
costante di mapping gaussiano (~300–480 s) ci fa sforare i circuiti banali che WISQ chiude in
secondi. Tagliare quell'overhead sui circuiti piccoli sposterebbe il picco più in basso.

---

## Tempo di compilazione (wall-clock)

Confronto `my_duration_s` vs `wisq_duration_s` su 261 circuiti (tutti tranne i 2 errori nostri).
Speedup = `wisq_duration / my_duration` — valori >1 significano che siamo più veloci.
I 17 circuiti in timeout WISQ sono **inclusi** con wisq_duration = 12000s (lower bound —
lo speedup reale su quei circuiti è ancora più alto, quindi la media è conservativa).

| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |
|-----------|---|----------------|-----------------|---------------|-----|-----|
| **Tutti (inclusi timeout WISQ)** | 261 | **232 (89%)** | **302×** | 656× | 0.01× | 40282× |
| ↳ Circuiti dove vinciamo su steps | 48 | 40 (83%) | 140× | 184× | 0.01× | 542× |
| ↳ Circuiti in pareggio su steps | 110 | 93 (85%) | 367× | 1054× | 0.01× | 40282× |
| ↳ Circuiti dove WISQ vince su steps | 86 | 85 (99%) | 417× | 505× | 0.11× | 1999× |
| ↳ WISQ in timeout (wisq_duration = 12000s, lower bound) | 17 | 14 (82%) | 19× | 181× | 0.44× | 1160× |

**Dove siamo più lenti** (~26 circuiti): quasi esclusivamente piccoli/triviali
(`example`, `ghz_n10–n100`, `parallel`, `ising_n10–n70`, `graphstate_n20–n60`, …)
dove WISQ completa in pochi secondi e il nostro overhead di mapping gaussiano pesa di più.

---

## Per famiglia di circuiti

**WISQ timeout** = WISQ ha girato fino a mr_timeout=12000s senza trovare soluzione.
| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | Err | Fallback conn | Note |
|--------|---|-----|----------------|------|--------------|-----|---------------|------|
| 19qubits | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | 0 | n=19–19 |
| 53qubits | 2 | 0 | 2 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=27–39 |
| adder | 5 | 0 | 5 (4 noi+veloci) | 0 | 0 | 0 | 1 | n=4–433 |
| bv | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=153 |
| bwt | 5 | 0 | 0 | 1 | 4 | 0 | 2 | n=21–133 |
| cat | 2 | 0 | 2 (1 noi+veloci) | 0 | 0 | 0 | 1 | n=130–260 |
| continuous_3_17 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=3 |
| dnn | 1 | 1 | 0 | 0 | 0 | 0 | 0 | n=16 |
| example | 1 | 0 | 1 | 0 | 0 | 0 | 0 | n=4 |
| factor247 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | n=15 |
| fredkin | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=3 |
| ghz | 18 | 0 | 18 (11 noi+veloci) | 0 | 0 | 0 | 4 | n=5–400 |
| ghz_state | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | 1 | n=23–255 |
| graphstate | 17 | 12 | 5 (3 noi+veloci) | 0 | 0 | 0 | 4 | n=5–400 |
| grover | 3 | 0 | 2 (2 noi+veloci) | 0 | 1 | 0 | 0 | n=5–20 |
| hhl | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=10 |
| ising | 19 | 17 | 2 (1 noi+veloci) | 0 | 0 | 0 | 4 | n=5–420 |
| knn | 1 | 0 | 0 | 0 | 0 | 1 | 0 |  |
| multiplier | 11 | 3 | 4 (3 noi+veloci) | 0 | 4 | 0 | 4 | n=9–400 |
| multiply | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=6 |
| parallel | 1 | 0 | 1 | 0 | 0 | 0 | 0 | n=8 |
| parallel_big | 1 | 1 | 0 | 0 | 0 | 0 | 0 | n=20 |
| qaoa | 20 | 0 | 4 (3 noi+veloci) | 15 | 1 | 0 | 3 | n=5–400 |
| qec_en | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=5 |
| qft | 22 | 6 | 1 (1 noi+veloci) | 14 | 1 | 0 | 1 | n=5–400 |
| qpe_n9 | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=9 |
| qram | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=9 |
| randomcircuit | 5 | 1 | 0 | 1 | 3 | 0 | 3 | n=50–500 |
| seca | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=11 |
| simon | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=3 |
| square_root | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | 0 | n=14–32 |
| synth | 37 | 2 | 0 | 35 | 0 | 0 | 7 | n=50–200 |
| t_test | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | 1 | n=8–8 |
| test | 1 | 0 | 0 | 0 | 0 | 1 | 0 |  |
| toffoli | 1 | 0 | 1 (1 noi+veloci) | 0 | 0 | 0 | 0 | n=3 |
| vqe_real_amp | 17 | 0 | 13 (13 noi+veloci) | 4 | 0 | 0 | 3 | n=5–400 |
| vqe_su2 | 17 | 0 | 13 (13 noi+veloci) | 4 | 0 | 0 | 3 | n=5–400 |
| vqe_two_local | 17 | 5 | 1 (1 noi+veloci) | 9 | 2 | 0 | 2 | n=5–400 |
| vqe_uccsd | 2 | 0 | 2 (2 noi+veloci) | 0 | 0 | 0 | 0 | n=4–8 |
| wstate | 18 | 0 | 15 (15 noi+veloci) | 3 | 0 | 0 | 3 | n=5–400 |

---

## Per circuito (dettaglio)

**Steps**: WIN = noi usiamo meno routing steps, LOSS = WISQ usa meno steps, = = pareggio.
**Tempo**: confronto durata compilazione nostra vs WISQ (solo dove entrambi completano).
**Fallback**: `connectivity` = cube ha fallito il mapping, usato connectivity; vuoto = cube ok.
**WISQ status `failed`** = WISQ ha raggiunto mr_timeout=12000s senza completare il routing.

| # | Circuit | Qubits | Grid | My steps | WISQ steps | Ratio | Fallback | WISQ status | Steps | Tempo |
|---|---------|--------|------|----------|------------|-------|----------|-------------|-------|-------|
| 1 | 19qubits_511gate_153layers | 19 | 12×12 | 99 | 99 | 1.0000 |  | success | = | noi +veloci |
| 2 | 19qubits_521gate_352layers | 19 | 12×12 | 286 | 286 | 1.0000 |  | success | = | noi +veloci |
| 3 | 53qubits_155gate_57layers | 27 | 14×14 | 23 | 23 | 1.0000 |  | success | = | WISQ +veloce |
| 4 | 53qubits_332gate_152layers | 39 | 17×17 | 41 | 41 | 1.0000 |  | success | = | noi +veloci |
| 5 | adder_n28 | 28 | 14×14 | 24 | 24 | 1.0000 |  | success | = | noi +veloci |
| 6 | adder_n4 | 4 | 10×10 | 8 | 8 | 1.0000 |  | success | = | noi +veloci |
| 7 | adder_n433 | 433 | 40×40 | 249 | 249 | 1.0000 | connectivity | success | = | noi +veloci |
| 8 | adder_n64_transpiled | 64 | 19×19 | 181 | 181 | 1.0000 |  | success | = | WISQ +veloce |
| 9 | bigadder_n18_transpiled | 18 | 12×12 | 88 | 88 | 1.0000 |  | success | = | noi +veloci |
| 10 | bv_n280 | 153 | 29×29 | 152 | 152 | 1.0000 |  | success | = | noi +veloci |
| 11 | bwt_n177 | 133 | 27×27 | 257604 | — | — | connectivity | failed | timeout | — |
| 12 | bwt_n21 | 21 | 13×13 | 116400 | — | — |  | failed | timeout | — |
| 13 | bwt_n37 | 28 | 15×15 | 33621 | 33607 | 0.9996 |  | success | LOSS | noi +veloci |
| 14 | bwt_n57 | 43 | 17×17 | 65603 | — | — | connectivity | failed | timeout | — |
| 15 | bwt_n97 | 73 | 21×21 | 130803 | — | — |  | failed | timeout | — |
| 16 | cat_n130 | 130 | 25×25 | 129 | 129 | 1.0000 |  | success | = | WISQ +veloce |
| 17 | cat_n260 | 260 | 31×31 | 259 | 259 | 1.0000 | connectivity | success | = | noi +veloci |
| 18 | continuous_3_17_13 | 3 | 7×7 | 17 | 17 | 1.0000 |  | success | = | noi +veloci |
| 19 | dnn_n16 | 16 | 11×11 | 48 | 70 | 1.4583 |  | success | **WIN** | WISQ +veloce |
| 20 | example | 4 | 9×9 | 21 | 21 | 1.0000 |  | success | = | WISQ +veloce |
| 21 | factor247_n15 | 15 | 11×11 | 349644 | — | — |  | failed | timeout | — |
| 22 | fredkin_n3 | 3 | 8×8 | 10 | 10 | 1.0000 |  | success | = | noi +veloci |
| 23 | ghz_n10 | 10 | 10×10 | 9 | 9 | 1.0000 |  | success | = | WISQ +veloce |
| 24 | ghz_n100 | 100 | 22×22 | 99 | 99 | 1.0000 |  | success | = | WISQ +veloce |
| 25 | ghz_n125 | 125 | 24×24 | 124 | 124 | 1.0000 |  | success | = | noi +veloci |
| 26 | ghz_n150 | 150 | 24×24 | 149 | 149 | 1.0000 | connectivity | success | = | noi +veloci |
| 27 | ghz_n175 | 175 | 28×28 | 174 | 174 | 1.0000 |  | success | = | WISQ +veloce |
| 28 | ghz_n20 | 20 | 12×12 | 19 | 19 | 1.0000 |  | success | = | WISQ +veloce |
| 29 | ghz_n200 | 200 | 30×30 | 199 | 199 | 1.0000 |  | success | = | noi +veloci |
| 30 | ghz_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | connectivity | success | = | noi +veloci |
| 31 | ghz_n30 | 30 | 14×14 | 29 | 29 | 1.0000 |  | success | = | WISQ +veloce |
| 32 | ghz_n300 | 300 | 33×33 | 299 | 299 | 1.0000 | connectivity | success | = | noi +veloci |
| 33 | ghz_n40 | 40 | 15×15 | 39 | 39 | 1.0000 |  | success | = | noi +veloci |
| 34 | ghz_n400 | 400 | 38×38 | 399 | 399 | 1.0000 | connectivity | success | = | noi +veloci |
| 35 | ghz_n5 | 5 | 8×8 | 4 | 4 | 1.0000 |  | success | = | noi +veloci |
| 36 | ghz_n50 | 50 | 17×17 | 49 | 49 | 1.0000 |  | success | = | WISQ +veloce |
| 37 | ghz_n60 | 60 | 18×18 | 59 | 59 | 1.0000 |  | success | = | noi +veloci |
| 38 | ghz_n70 | 70 | 19×19 | 69 | 69 | 1.0000 |  | success | = | noi +veloci |
| 39 | ghz_n80 | 80 | 20×20 | 79 | 79 | 1.0000 |  | success | = | WISQ +veloce |
| 40 | ghz_n90 | 90 | 21×21 | 89 | 89 | 1.0000 |  | success | = | noi +veloci |
| 41 | ghz_state_n23 | 23 | 13×13 | 22 | 22 | 1.0000 |  | success | = | noi +veloci |
| 42 | ghz_state_n255 | 255 | 31×31 | 254 | 254 | 1.0000 | connectivity | success | = | noi +veloci |
| 43 | graphstate_n10 | 10 | 10×10 | 4 | 4 | 1.0000 |  | success | = | noi +veloci |
| 44 | graphstate_n100 | 100 | 22×22 | 8 | 8 | 1.0000 |  | success | = | WISQ +veloce |
| 45 | graphstate_n125 | 125 | 24×24 | 6 | 10 | 1.6667 |  | success | **WIN** | noi +veloci |
| 46 | graphstate_n150 | 150 | 24×24 | 6 | 13 | 2.1667 | connectivity | success | **WIN** | noi +veloci |
| 47 | graphstate_n175 | 175 | 25×25 | 7 | 13 | 1.8571 | connectivity | success | **WIN** | noi +veloci |
| 48 | graphstate_n20 | 20 | 12×12 | 4 | 4 | 1.0000 |  | success | = | WISQ +veloce |
| 49 | graphstate_n200 | 200 | 30×30 | 6 | 13 | 2.1667 |  | success | **WIN** | noi +veloci |
| 50 | graphstate_n30 | 30 | 14×14 | 6 | 6 | 1.0000 |  | success | = | noi +veloci |
| 51 | graphstate_n300 | 300 | 33×33 | 9 | 17 | 1.8889 | connectivity | success | **WIN** | noi +veloci |
| 52 | graphstate_n40 | 40 | 15×15 | 4 | 6 | 1.5000 |  | success | **WIN** | WISQ +veloce |
| 53 | graphstate_n400 | 400 | 38×38 | 7 | 24 | 3.4286 | connectivity | success | **WIN** | noi +veloci |
| 54 | graphstate_n5 | 5 | 8×8 | 4 | 4 | 1.0000 |  | success | = | noi +veloci |
| 55 | graphstate_n50 | 50 | 17×17 | 5 | 7 | 1.4000 |  | success | **WIN** | WISQ +veloce |
| 56 | graphstate_n60 | 60 | 18×18 | 5 | 6 | 1.2000 |  | success | **WIN** | WISQ +veloce |
| 57 | graphstate_n70 | 70 | 19×19 | 6 | 8 | 1.3333 |  | success | **WIN** | noi +veloci |
| 58 | graphstate_n80 | 80 | 20×20 | 6 | 8 | 1.3333 |  | success | **WIN** | noi +veloci |
| 59 | graphstate_n90 | 90 | 21×21 | 5 | 10 | 2.0000 |  | success | **WIN** | noi +veloci |
| 60 | grover_n10 | 10 | 11×11 | 11008 | 11008 | 1.0000 |  | success | = | noi +veloci |
| 61 | grover_n20 | 20 | 13×13 | 2146489 | — | — |  | failed | timeout | — |
| 62 | grover_n5 | 5 | 10×10 | 209 | 209 | 1.0000 |  | success | = | noi +veloci |
| 63 | hhl_n10 | 10 | 10×10 | 72039 | 72039 | 1.0000 |  | success | = | noi +veloci |
| 64 | ising_n10 | 10 | 10×10 | 4 | 4 | 1.0000 |  | success | = | WISQ +veloce |
| 65 | ising_n100 | 100 | 22×22 | 6 | 15 | 2.5000 |  | success | **WIN** | noi +veloci |
| 66 | ising_n125 | 125 | 24×24 | 4 | 18 | 4.5000 |  | success | **WIN** | noi +veloci |
| 67 | ising_n150 | 150 | 24×24 | 4 | 21 | 5.2500 | connectivity | success | **WIN** | WISQ +veloce |
| 68 | ising_n175 | 175 | 28×28 | 6 | 20 | 3.3333 |  | success | **WIN** | noi +veloci |
| 69 | ising_n20 | 20 | 12×12 | 4 | 6 | 1.5000 |  | success | **WIN** | noi +veloci |
| 70 | ising_n200 | 200 | 30×30 | 6 | 27 | 4.5000 |  | success | **WIN** | noi +veloci |
| 71 | ising_n26 | 26 | 13×13 | 4 | 8 | 2.0000 |  | success | **WIN** | WISQ +veloce |
| 72 | ising_n30 | 30 | 14×14 | 4 | 8 | 2.0000 |  | success | **WIN** | noi +veloci |
| 73 | ising_n300 | 300 | 33×33 | 4 | 37 | 9.2500 | connectivity | success | **WIN** | noi +veloci |
| 74 | ising_n40 | 40 | 15×15 | 4 | 8 | 2.0000 |  | success | **WIN** | noi +veloci |
| 75 | ising_n400 | 400 | 38×38 | 4 | 50 | 12.5000 | connectivity | success | **WIN** | noi +veloci |
| 76 | ising_n420 | 420 | 39×39 | 4 | 50 | 12.5000 | connectivity | success | **WIN** | noi +veloci |
| 77 | ising_n5 | 5 | 8×8 | 4 | 4 | 1.0000 |  | success | = | noi +veloci |
| 78 | ising_n50 | 50 | 17×17 | 6 | 9 | 1.5000 |  | success | **WIN** | noi +veloci |
| 79 | ising_n60 | 60 | 18×18 | 4 | 10 | 2.5000 |  | success | **WIN** | WISQ +veloce |
| 80 | ising_n70 | 70 | 19×19 | 4 | 12 | 3.0000 |  | success | **WIN** | WISQ +veloce |
| 81 | ising_n80 | 80 | 20×20 | 4 | 13 | 3.2500 |  | success | **WIN** | noi +veloci |
| 82 | ising_n90 | 90 | 21×21 | 6 | 13 | 2.1667 |  | success | **WIN** | noi +veloci |
| 83 | knn_n25 | — | — | — | — | — |  | error | ERR | — |
| 84 | multiplier_n100 | 100 | 23×23 | 111762 | — | — | connectivity | failed | timeout | — |
| 85 | multiplier_n15 | 9 | 9×9 | 12 | 12 | 1.0000 |  | success | = | noi +veloci |
| 86 | multiplier_n20 | 20 | 13×13 | 3990 | 3990 | 1.0000 |  | success | = | noi +veloci |
| 87 | multiplier_n200 | 200 | 33×33 | 450019 | — | — | connectivity | failed | timeout | — |
| 88 | multiplier_n300 | 300 | 39×39 | 1013844 | — | — | connectivity | failed | timeout | — |
| 89 | multiplier_n40 | 40 | 17×17 | 17329 | 17329 | 1.0000 |  | success | = | noi +veloci |
| 90 | multiplier_n400 | 400 | 43×43 | 1811334 | — | — | connectivity | failed | timeout | — |
| 91 | multiplier_n45 | 27 | 13×13 | 36 | 36 | 1.0000 |  | success | = | WISQ +veloce |
| 92 | multiplier_n60 | 60 | 22×22 | 39730 | 39732 | 1.0001 |  | success | **WIN** | noi +veloci |
| 93 | multiplier_n75 | 45 | 16×16 | 60 | 62 | 1.0333 |  | success | **WIN** | noi +veloci |
| 94 | multiplier_n80 | 80 | 25×25 | 71287 | 71330 | 1.0006 |  | success | **WIN** | noi +veloci |
| 95 | multiply_n13 | 6 | 8×8 | 2 | 2 | 1.0000 |  | success | = | noi +veloci |
| 96 | parallel | 8 | 9×9 | 10 | 10 | 1.0000 |  | success | = | WISQ +veloce |
| 97 | parallel_big | 20 | 12×12 | 8 | 12 | 1.5000 |  | success | **WIN** | noi +veloci |
| 98 | qaoa_n10 | 10 | 10×10 | 46 | 46 | 1.0000 |  | success | = | noi +veloci |
| 99 | qaoa_n100 | 100 | 23×23 | 1327 | 1075 | 0.8101 |  | success | LOSS | noi +veloci |
| 100 | qaoa_n125 | 125 | 26×26 | 1731 | 1365 | 0.7886 |  | success | LOSS | noi +veloci |
| 101 | qaoa_n150 | 150 | 28×28 | 2723 | 1894 | 0.6956 |  | success | LOSS | noi +veloci |
| 102 | qaoa_n175 | 175 | 30×30 | 3334 | 2427 | 0.7280 |  | success | LOSS | noi +veloci |
| 103 | qaoa_n20 | 20 | 12×12 | 92 | 90 | 0.9783 |  | success | LOSS | WISQ +veloce |
| 104 | qaoa_n200 | 200 | 29×29 | 3893 | 3555 | 0.9132 | connectivity | success | LOSS | noi +veloci |
| 105 | qaoa_n30 | 30 | 14×14 | 157 | 149 | 0.9490 |  | success | LOSS | noi +veloci |
| 106 | qaoa_n300 | 300 | 39×39 | 7093 | 5883 | 0.8294 | connectivity | success | LOSS | noi +veloci |
| 107 | qaoa_n40 | 40 | 16×16 | 250 | 216 | 0.8640 |  | success | LOSS | noi +veloci |
| 108 | qaoa_n400 | 400 | 43×43 | 11742 | — | — | connectivity | failed | timeout | — |
| 109 | qaoa_n5 | 5 | 8×8 | 14 | 14 | 1.0000 |  | success | = | noi +veloci |
| 110 | qaoa_n50 | 50 | 18×18 | 345 | 295 | 0.8551 |  | success | LOSS | noi +veloci |
| 111 | qaoa_n6 | 6 | 8×8 | 33 | 33 | 1.0000 |  | success | = | WISQ +veloce |
| 112 | qaoa_n60 | 60 | 19×19 | 459 | 450 | 0.9804 |  | success | LOSS | noi +veloci |
| 113 | qaoa_n64 | 64 | 20×20 | 492 | 450 | 0.9146 |  | success | LOSS | noi +veloci |
| 114 | qaoa_n6_transpiled | 6 | 8×8 | 33 | 33 | 1.0000 |  | success | = | noi +veloci |
| 115 | qaoa_n70 | 70 | 20×20 | 600 | 525 | 0.8750 |  | success | LOSS | noi +veloci |
| 116 | qaoa_n80 | 80 | 21×21 | 775 | 663 | 0.8555 |  | success | LOSS | noi +veloci |
| 117 | qaoa_n90 | 90 | 22×22 | 1045 | 803 | 0.7684 |  | success | LOSS | noi +veloci |
| 118 | qec_en_n5 | 5 | 9×9 | 11 | 11 | 1.0000 |  | success | = | noi +veloci |
| 119 | qft_20 | 20 | 13×13 | 83 | 103 | 1.2410 |  | success | **WIN** | noi +veloci |
| 120 | qft_n10 | 10 | 10×10 | 35 | 34 | 0.9714 |  | success | LOSS | noi +veloci |
| 121 | qft_n100 | 100 | 23×23 | 687 | 526 | 0.7656 |  | success | LOSS | noi +veloci |
| 122 | qft_n125 | 125 | 25×25 | 841 | 661 | 0.7860 |  | success | LOSS | noi +veloci |
| 123 | qft_n128 | 128 | 25×25 | 880 | 646 | 0.7341 |  | success | LOSS | noi +veloci |
| 124 | qft_n150 | 150 | 27×27 | 1005 | 759 | 0.7552 |  | success | LOSS | noi +veloci |
| 125 | qft_n175 | 175 | 29×29 | 1157 | 858 | 0.7416 |  | success | LOSS | noi +veloci |
| 126 | qft_n18 | 18 | 12×12 | 70 | 71 | 1.0143 |  | success | **WIN** | noi +veloci |
| 127 | qft_n20 | 20 | 13×13 | 83 | 92 | 1.1084 |  | success | **WIN** | noi +veloci |
| 128 | qft_n200 | 200 | 31×31 | 1339 | 955 | 0.7132 |  | success | LOSS | noi +veloci |
| 129 | qft_n30 | 30 | 15×15 | 144 | 159 | 1.1042 |  | success | **WIN** | noi +veloci |
| 130 | qft_n300 | 300 | 36×36 | 2093 | 1297 | 0.6197 |  | success | LOSS | noi +veloci |
| 131 | qft_n320 | 320 | 39×39 | 8406 | — | — | connectivity | failed | timeout | — |
| 132 | qft_n40 | 40 | 17×17 | 200 | 204 | 1.0200 |  | success | **WIN** | noi +veloci |
| 133 | qft_n400 | 400 | 41×41 | 2886 | 1854 | 0.6424 |  | success | LOSS | noi +veloci |
| 134 | qft_n5 | 5 | 8×8 | 14 | 14 | 1.0000 |  | success | = | noi +veloci |
| 135 | qft_n50 | 50 | 18×18 | 266 | 244 | 0.9173 |  | success | LOSS | noi +veloci |
| 136 | qft_n60 | 60 | 19×19 | 324 | 347 | 1.0710 |  | success | **WIN** | noi +veloci |
| 137 | qft_n64 | 64 | 19×19 | 377 | 364 | 0.9655 |  | success | LOSS | noi +veloci |
| 138 | qft_n70 | 70 | 20×20 | 396 | 335 | 0.8460 |  | success | LOSS | noi +veloci |
| 139 | qft_n80 | 80 | 21×21 | 490 | 422 | 0.8612 |  | success | LOSS | noi +veloci |
| 140 | qft_n90 | 90 | 22×22 | 569 | 418 | 0.7346 |  | success | LOSS | noi +veloci |
| 141 | qpe_n9_transpiled | 9 | 10×10 | 42 | 42 | 1.0000 |  | success | = | noi +veloci |
| 142 | qram_n20 | 9 | 9×9 | 8 | 8 | 1.0000 |  | success | = | noi +veloci |
| 143 | randomcircuit_n100 | 100 | 28×28 | 4077 | 3928 | 0.9635 |  | success | LOSS | noi +veloci |
| 144 | randomcircuit_n200 | 200 | 33×33 | 15543 | — | — | connectivity | failed | timeout | — |
| 145 | randomcircuit_n400 | 400 | 43×43 | 240587 | — | — | connectivity | failed | timeout | — |
| 146 | randomcircuit_n50 | 50 | 21×21 | 1424 | 1425 | 1.0007 |  | success | **WIN** | noi +veloci |
| 147 | randomcircuit_n500 | 500 | 49×49 | 119803 | — | — | connectivity | failed | timeout | — |
| 148 | seca_n11 | 11 | 10×10 | 19 | 19 | 1.0000 |  | success | = | noi +veloci |
| 149 | simon_n6 | 3 | 7×7 | 2 | 2 | 1.0000 |  | success | = | noi +veloci |
| 150 | square_root_n18 | 14 | 11×11 | 27 | 27 | 1.0000 |  | success | = | noi +veloci |
| 151 | square_root_n45 | 32 | 14×14 | 570 | 570 | 1.0000 |  | success | = | noi +veloci |
| 152 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s0 | 100 | 25×25 | 261 | 156 | 0.5977 |  | success | LOSS | noi +veloci |
| 153 | synth_n100_d020_mix000_t030_hf000_hm001_r2_s1 | 100 | 26×26 | 246 | 144 | 0.5854 |  | success | LOSS | noi +veloci |
| 154 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s0 | 100 | 25×25 | 294 | 203 | 0.6905 |  | success | LOSS | noi +veloci |
| 155 | synth_n100_d020_mix050_t030_hf000_hm001_r2_s1 | 100 | 26×26 | 259 | 189 | 0.7297 |  | success | LOSS | noi +veloci |
| 156 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s0 | 100 | 25×25 | 250 | 217 | 0.8680 |  | success | LOSS | noi +veloci |
| 157 | synth_n100_d020_mix100_t030_hf000_hm001_r2_s1 | 100 | 26×26 | 290 | 207 | 0.7138 |  | success | LOSS | noi +veloci |
| 158 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s0 | 100 | 26×26 | 499 | 349 | 0.6994 |  | success | LOSS | noi +veloci |
| 159 | synth_n100_d040_mix000_t030_hf000_hm001_r2_s1 | 100 | 25×25 | 533 | 392 | 0.7355 |  | success | LOSS | noi +veloci |
| 160 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s0 | 100 | 25×25 | 511 | 423 | 0.8278 |  | success | LOSS | noi +veloci |
| 161 | synth_n100_d040_mix050_t030_hf000_hm001_r2_s1 | 100 | 25×25 | 526 | 403 | 0.7662 |  | success | LOSS | noi +veloci |
| 162 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s0 | 100 | 26×26 | 508 | 389 | 0.7657 |  | success | LOSS | noi +veloci |
| 163 | synth_n100_d040_mix100_t030_hf000_hm001_r2_s1 | 100 | 25×25 | 538 | 446 | 0.8290 |  | success | LOSS | noi +veloci |
| 164 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s0 | 200 | 30×30 | 1571 | 724 | 0.4609 | connectivity | success | LOSS | noi +veloci |
| 165 | synth_n200_d020_mix000_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 709 | 379 | 0.5346 | connectivity | success | LOSS | noi +veloci |
| 166 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s0 | 200 | 31×31 | 1113 | 1692 | 1.5202 | connectivity | success | **WIN** | noi +veloci |
| 167 | synth_n200_d020_mix050_t030_hf000_hm001_r2_s1 | 200 | 31×31 | 1095 | 1247 | 1.1388 | connectivity | success | **WIN** | noi +veloci |
| 168 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s0 | 200 | 31×31 | 1627 | 937 | 0.5759 | connectivity | success | LOSS | noi +veloci |
| 169 | synth_n200_d020_mix100_t030_hf000_hm001_r2_s1 | 200 | 33×33 | 868 | 644 | 0.7419 | connectivity | success | LOSS | noi +veloci |
| 170 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s0 | 200 | 34×34 | 1812 | 1125 | 0.6209 |  | success | LOSS | noi +veloci |
| 171 | synth_n200_d040_mix000_t030_hf000_hm001_r2_s1 | 200 | 35×35 | 1706 | 1148 | 0.6729 |  | success | LOSS | noi +veloci |
| 172 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s0 | 200 | 34×34 | 1765 | 1207 | 0.6839 |  | success | LOSS | noi +veloci |
| 173 | synth_n200_d040_mix050_t030_hf000_hm001_r2_s1 | 200 | 35×35 | 1708 | 1257 | 0.7359 |  | success | LOSS | noi +veloci |
| 174 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s0 | 200 | 35×35 | 1779 | 1434 | 0.8061 |  | success | LOSS | noi +veloci |
| 175 | synth_n200_d040_mix100_t030_hf000_hm001_r2_s1 | 200 | 35×35 | 1688 | 1389 | 0.8229 |  | success | LOSS | noi +veloci |
| 176 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 74 | 62 | 0.8378 |  | success | LOSS | noi +veloci |
| 177 | synth_n50_d020_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 67 | 57 | 0.8507 |  | success | LOSS | noi +veloci |
| 178 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 75 | 70 | 0.9333 |  | success | LOSS | noi +veloci |
| 179 | synth_n50_d020_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 76 | 74 | 0.9737 |  | success | LOSS | noi +veloci |
| 180 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 78 | 70 | 0.8974 | connectivity | success | LOSS | noi +veloci |
| 181 | synth_n50_d020_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 74 | 73 | 0.9865 |  | success | LOSS | noi +veloci |
| 182 | synth_n50_d030_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 114 | 106 | 0.9298 |  | success | LOSS | noi +veloci |
| 183 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 144 | 130 | 0.9028 |  | success | LOSS | noi +veloci |
| 184 | synth_n50_d040_mix000_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 150 | 138 | 0.9200 |  | success | LOSS | noi +veloci |
| 185 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 154 | 144 | 0.9351 |  | success | LOSS | noi +veloci |
| 186 | synth_n50_d040_mix050_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 163 | 150 | 0.9202 |  | success | LOSS | noi +veloci |
| 187 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s0 | 50 | 19×19 | 157 | 144 | 0.9172 |  | success | LOSS | noi +veloci |
| 188 | synth_n50_d040_mix100_t030_hf000_hm001_r2_s1 | 50 | 19×19 | 152 | 145 | 0.9539 |  | success | LOSS | noi +veloci |
| 189 | t_test | 8 | 12×12 | 110 | 110 | 1.0000 |  | success | = | noi +veloci |
| 190 | t_test2 | 8 | 9×9 | 3904 | 3904 | 1.0000 | connectivity | success | = | noi +veloci |
| 191 | test | — | — | — | — | — |  | error | ERR | — |
| 192 | toffoli_n3 | 3 | 8×8 | 11 | 11 | 1.0000 |  | success | = | noi +veloci |
| 193 | vqe_real_amp_n10 | 10 | 10×10 | 13 | 13 | 1.0000 |  | success | = | noi +veloci |
| 194 | vqe_real_amp_n100 | 100 | 22×22 | 104 | 103 | 0.9904 |  | success | LOSS | noi +veloci |
| 195 | vqe_real_amp_n125 | 125 | 24×24 | 128 | 128 | 1.0000 |  | success | = | noi +veloci |
| 196 | vqe_real_amp_n150 | 150 | 24×24 | 153 | 153 | 1.0000 | connectivity | success | = | noi +veloci |
| 197 | vqe_real_amp_n175 | 175 | 28×28 | 179 | 178 | 0.9944 |  | success | LOSS | noi +veloci |
| 198 | vqe_real_amp_n20 | 20 | 12×12 | 23 | 23 | 1.0000 |  | success | = | noi +veloci |
| 199 | vqe_real_amp_n200 | 200 | 30×30 | 203 | 203 | 1.0000 |  | success | = | noi +veloci |
| 200 | vqe_real_amp_n30 | 30 | 14×14 | 33 | 33 | 1.0000 |  | success | = | noi +veloci |
| 201 | vqe_real_amp_n300 | 300 | 33×33 | 303 | 303 | 1.0000 | connectivity | success | = | noi +veloci |
| 202 | vqe_real_amp_n40 | 40 | 15×15 | 43 | 43 | 1.0000 |  | success | = | noi +veloci |
| 203 | vqe_real_amp_n400 | 400 | 38×38 | 403 | 403 | 1.0000 | connectivity | success | = | noi +veloci |
| 204 | vqe_real_amp_n5 | 5 | 8×8 | 8 | 8 | 1.0000 |  | success | = | noi +veloci |
| 205 | vqe_real_amp_n50 | 50 | 17×17 | 55 | 53 | 0.9636 |  | success | LOSS | noi +veloci |
| 206 | vqe_real_amp_n60 | 60 | 18×18 | 63 | 63 | 1.0000 |  | success | = | noi +veloci |
| 207 | vqe_real_amp_n70 | 70 | 19×19 | 73 | 73 | 1.0000 |  | success | = | noi +veloci |
| 208 | vqe_real_amp_n80 | 80 | 20×20 | 83 | 83 | 1.0000 |  | success | = | noi +veloci |
| 209 | vqe_real_amp_n90 | 90 | 21×21 | 95 | 93 | 0.9789 |  | success | LOSS | noi +veloci |
| 210 | vqe_su2_n10 | 10 | 10×10 | 13 | 13 | 1.0000 |  | success | = | noi +veloci |
| 211 | vqe_su2_n100 | 100 | 22×22 | 104 | 103 | 0.9904 |  | success | LOSS | noi +veloci |
| 212 | vqe_su2_n125 | 125 | 24×24 | 128 | 128 | 1.0000 |  | success | = | noi +veloci |
| 213 | vqe_su2_n150 | 150 | 24×24 | 153 | 153 | 1.0000 | connectivity | success | = | noi +veloci |
| 214 | vqe_su2_n175 | 175 | 28×28 | 179 | 178 | 0.9944 |  | success | LOSS | noi +veloci |
| 215 | vqe_su2_n20 | 20 | 12×12 | 23 | 23 | 1.0000 |  | success | = | noi +veloci |
| 216 | vqe_su2_n200 | 200 | 30×30 | 203 | 203 | 1.0000 |  | success | = | noi +veloci |
| 217 | vqe_su2_n30 | 30 | 14×14 | 33 | 33 | 1.0000 |  | success | = | noi +veloci |
| 218 | vqe_su2_n300 | 300 | 33×33 | 303 | 303 | 1.0000 | connectivity | success | = | noi +veloci |
| 219 | vqe_su2_n40 | 40 | 15×15 | 43 | 43 | 1.0000 |  | success | = | noi +veloci |
| 220 | vqe_su2_n400 | 400 | 38×38 | 403 | 403 | 1.0000 | connectivity | success | = | noi +veloci |
| 221 | vqe_su2_n5 | 5 | 8×8 | 8 | 8 | 1.0000 |  | success | = | noi +veloci |
| 222 | vqe_su2_n50 | 50 | 17×17 | 55 | 53 | 0.9636 |  | success | LOSS | noi +veloci |
| 223 | vqe_su2_n60 | 60 | 18×18 | 63 | 63 | 1.0000 |  | success | = | noi +veloci |
| 224 | vqe_su2_n70 | 70 | 19×19 | 73 | 73 | 1.0000 |  | success | = | noi +veloci |
| 225 | vqe_su2_n80 | 80 | 20×20 | 83 | 83 | 1.0000 |  | success | = | noi +veloci |
| 226 | vqe_su2_n90 | 90 | 21×21 | 95 | 93 | 0.9789 |  | success | LOSS | noi +veloci |
| 227 | vqe_two_local_n10 | 10 | 10×10 | 40 | 39 | 0.9750 |  | success | LOSS | noi +veloci |
| 228 | vqe_two_local_n100 | 100 | 24×24 | 1620 | 1471 | 0.9080 |  | success | LOSS | noi +veloci |
| 229 | vqe_two_local_n125 | 125 | 27×27 | 2360 | 2312 | 0.9797 |  | success | LOSS | noi +veloci |
| 230 | vqe_two_local_n150 | 150 | 29×29 | 3253 | 3144 | 0.9665 |  | success | LOSS | noi +veloci |
| 231 | vqe_two_local_n175 | 175 | 31×31 | 4384 | 4231 | 0.9651 |  | success | LOSS | noi +veloci |
| 232 | vqe_two_local_n20 | 20 | 13×13 | 94 | 124 | 1.3191 |  | success | **WIN** | noi +veloci |
| 233 | vqe_two_local_n200 | 200 | 33×33 | 5443 | 5253 | 0.9651 |  | success | LOSS | noi +veloci |
| 234 | vqe_two_local_n30 | 30 | 15×15 | 193 | 198 | 1.0259 |  | success | **WIN** | noi +veloci |
| 235 | vqe_two_local_n300 | 300 | 39×39 | 10532 | — | — | connectivity | failed | timeout | — |
| 236 | vqe_two_local_n40 | 40 | 17×17 | 301 | 379 | 1.2591 |  | success | **WIN** | noi +veloci |
| 237 | vqe_two_local_n400 | 400 | 43×43 | 17105 | — | — | connectivity | failed | timeout | — |
| 238 | vqe_two_local_n5 | 5 | 8×8 | 17 | 17 | 1.0000 |  | success | = | noi +veloci |
| 239 | vqe_two_local_n50 | 50 | 18×18 | 441 | 462 | 1.0476 |  | success | **WIN** | noi +veloci |
| 240 | vqe_two_local_n60 | 60 | 20×20 | 594 | 593 | 0.9983 |  | success | LOSS | noi +veloci |
| 241 | vqe_two_local_n70 | 70 | 21×21 | 794 | 903 | 1.1373 |  | success | **WIN** | noi +veloci |
| 242 | vqe_two_local_n80 | 80 | 22×22 | 1044 | 1008 | 0.9655 |  | success | LOSS | noi +veloci |
| 243 | vqe_two_local_n90 | 90 | 23×23 | 1380 | 1366 | 0.9899 |  | success | LOSS | noi +veloci |
| 244 | vqe_uccsd_n4 | 4 | 7×7 | 87 | 87 | 1.0000 |  | success | = | noi +veloci |
| 245 | vqe_uccsd_n8 | 8 | 9×9 | 5446 | 5446 | 1.0000 |  | success | = | noi +veloci |
| 246 | wstate_n10 | 10 | 10×10 | 11 | 11 | 1.0000 |  | success | = | noi +veloci |
| 247 | wstate_n100 | 100 | 22×22 | 101 | 101 | 1.0000 |  | success | = | noi +veloci |
| 248 | wstate_n125 | 125 | 24×24 | 126 | 126 | 1.0000 |  | success | = | noi +veloci |
| 249 | wstate_n150 | 150 | 24×24 | 151 | 151 | 1.0000 | connectivity | success | = | noi +veloci |
| 250 | wstate_n175 | 175 | 28×28 | 176 | 176 | 1.0000 |  | success | = | noi +veloci |
| 251 | wstate_n20 | 20 | 12×12 | 21 | 21 | 1.0000 |  | success | = | noi +veloci |
| 252 | wstate_n200 | 200 | 30×30 | 201 | 201 | 1.0000 |  | success | = | noi +veloci |
| 253 | wstate_n27 | 27 | 13×13 | 29 | 28 | 0.9655 |  | success | LOSS | noi +veloci |
| 254 | wstate_n30 | 30 | 14×14 | 31 | 31 | 1.0000 |  | success | = | noi +veloci |
| 255 | wstate_n300 | 300 | 33×33 | 301 | 301 | 1.0000 | connectivity | success | = | noi +veloci |
| 256 | wstate_n40 | 40 | 15×15 | 41 | 41 | 1.0000 |  | success | = | noi +veloci |
| 257 | wstate_n400 | 400 | 38×38 | 401 | 401 | 1.0000 | connectivity | success | = | noi +veloci |
| 258 | wstate_n5 | 5 | 8×8 | 6 | 6 | 1.0000 |  | success | = | noi +veloci |
| 259 | wstate_n50 | 50 | 17×17 | 52 | 51 | 0.9808 |  | success | LOSS | noi +veloci |
| 260 | wstate_n60 | 60 | 18×18 | 61 | 61 | 1.0000 |  | success | = | noi +veloci |
| 261 | wstate_n70 | 70 | 19×19 | 71 | 71 | 1.0000 |  | success | = | noi +veloci |
| 262 | wstate_n80 | 80 | 20×20 | 81 | 81 | 1.0000 |  | success | = | noi +veloci |
| 263 | wstate_n90 | 90 | 21×21 | 92 | 91 | 0.9891 |  | success | LOSS | noi +veloci |