# Cube vs Connectivity — è il safe_passage o solo la dimensione?

Due sweep (config in `data/config/`):
- **`cube_vs_conn_dim_sweep`**: 139 circuiti dell'ultima esecuzione cube_ext, regime **connectivity
  tunato** (border 15, mapped 20, cnot 8) e **cube tunato** (border 5, mapped 15, cnot 6),
  `dimension_offset ∈ [-5…+10]`. 4448 run.
- **`conn_high_dim_dense`**: follow-up, sola connectivity a `dimension_offset ∈ [+11…+15]` sui 32
  circuiti densi il cui ottimo cube cadeva sopra la griglia max sweepata da connectivity. 160 run.

`knn_n25` escluso (safe_passage_failed a ogni griglia per entrambi) → analisi su **138 circuiti**.
Asse di confronto = **`graph_x` assoluto** (la griglia reale nel CSV): a offset 0 cube auto-dimensiona
**+3 lati** rispetto a connectivity (gap misurato: media 3.02, mediana 3).

## TL;DR
**A parità di griglia assoluta cube e connectivity sono per lo più equivalenti; la vera (e unica
forte) leva è la dimensione.** Cube non è "migliore": ha solo un auto-sizer più generoso (+3 lati) e
una frontiera di feasibility più alta. Connectivity è più efficiente in spazio (raggiunge lo stesso
risultato con ~4 lati in meno) e scende dove cube fallisce. `routing_steps` non dipende dal
safe_passage. Resta un **vantaggio cube modesto e circuit-specifico** su alcune famiglie dense
(multiplier, bwt, randomcircuit, strutturati, gran parte dei synth) — **non** su qft/qaoa/vqe.

![panoramica](cube_vs_conn_dimension.png)

## 1. Verdetto a PARI griglia assoluta (138 circuiti)

Per ogni circuito: griglia (più piccola) dove cube tocca il suo minimo `non_routed`; connectivity
alla **stessa griglia assoluta**; vincitore = metrica migliore.

| metrica | pari | cube meglio | connectivity meglio |
|---|---|---|---|
| **non_routed** | **117** | 18 | 3 |
| **routing_steps** | **127** | 8 | 3 |

- **Pareggi esatti** su entrambe le metriche per qft (n20-n90), qaoa (n20-n80), vqe_two_local,
  e tutti i facili/strutturati (ghz, graphstate, ising, wstate, vqe_real_amp/su2, adder…).
- **I 18 cube-meglio** (non_routed) sono dense/strutturati con consistenza per-famiglia:
  **multiplier** (n60/n80/n100, tutte), **bwt** (n37/n97), randomcircuit_n50, qft_n100,
  19qubits_511gate, 53qubits_332gate, e 9 synth. → su queste famiglie la struttura del cube paga
  davvero (effetto piccolo ma sistematico, 18 vs 3).
- **I 3 connectivity-meglio** sono solo synth_n100 (d020_mix000: conn 3.25 vs cube 5.41; d040_mix000;
  d040_mix050) — i circuiti random, dove lo scarto va in entrambe le direzioni.

A livello di singola cella (circuito×griglia) il quadro è ancora più piatto: **73% di pareggi esatti**,
Δnon_routed medio cube−conn **+0.037pp**.

Dettaglio: [per_circuit_verdict_final.csv](per_circuit_verdict_final.csv),
[per_circuit_dense_closed.csv](per_circuit_dense_closed.csv).

## 2. La leva è la dimensione, non la strategia

A parità d'auto-size (offset 0) cube sembra meglio (nr 3.82 vs 4.74) ma usa **+3 lati di griglia**;
a pari griglia il vantaggio sparisce (§1). Quantificazione:

**Δ dimensione a pari risultato** (griglia-lato per raggiungere lo stesso `non_routed`, paired):

| non_routed ≤ | grid conn | grid cube | Δ (cube−conn) |
|---|---|---|---|
| 4 | 11.9 | 15.4 | +3.5 |
| 2 | 10.5 | 14.5 | +4.0 |
| 1 | 10.5 | 14.6 | +4.1 |
| 0.5 | 10.6 | 14.8 | +4.1 |

→ **cube serve ~+4 lati** per lo stesso risultato (~costante). In celle: per nr≤2, ~210 vs ~110 →
cube usa **~1.9× i qubit fisici**. Quel +4 è tutto **frontiera di feasibility**: la griglia minima
fattibile è in media **+4.9 più grande per cube** (mediana +5); a pari griglia *dove entrambi girano*
la qualità è uguale.

## 3. Quanto posso scendere di griglia (partendo dalla griglia WISQ/auto-cube)

![shrink](shrink_from_wisq_grid.png)

`rel` = lati rispetto alla griglia WISQ (auto di cube); `rel<0` = più piccola.

| rel | CONN feas% | CONN non_routed | CUBE feas% |
|---|---|---|---|
| 0 (WISQ) | 100 | 1.89 | 100 |
| −1 | 99 | 2.23 | **85** |
| −2 | 100 | 2.75 | **42** |
| −4 | 100 | 5.54 | 1 |
| −5 | 95 | 7.13 | 0 |
| −6 | 68 | 10.3 | 0 |

- **Connectivity**: scendi in sicurezza **fino a −4 lati** (100% feasible, mediana non_routed=0); −5 è
  il ginocchio; da −6 crolla. Per-circuito: mediana 5 lati di margine (entro +1pp), i densi meno.
- **Cube**: non può scendere — già a −1 fallisce il 15%, a −2 il 58%. Inchiodato alla griglia WISQ.
- Pratica: con connectivity scendi ~4 lati (es. 17→13) = **~−40% qubit fisici a prestazioni invariate**.

## 4. routing_steps

Indipendente dal safe_passage: 127/138 pari, e nel sottoinsieme con `non_routed` uguale (97 circ)
**97/97 pari** (Δ mediano 0.0%). Piatto anche con la dimensione (~costante nel regime fattibile).
Gli unici scarti seguono il `non_routed` (meno layer falliti = meno serializzazione = meno step).
Coerente con `parallelism ≡ 1/routing_steps`.

## Conclusione operativa
**Usa connectivity e dimensiona sul target di `non_routed`.** Cube non compra un vantaggio
algoritmico generale — solo una griglia di default più grande e una frontiera più alta. Connectivity
pareggia cube a pari griglia ovunque (tranne un edge cube minore su multiplier/bwt/synth/strutturati)
ed è più efficiente in spazio (~4 lati / ~−40% qubit). Se ti servono quelle famiglie dense specifiche
al massimo della qualità a griglia data, cube dà un piccolo guadagno.

**Caveat:** confronto tra i due pacchetti *interi* (border 15 vs 5 incluso, che gioca *contro*
connectivity → conclusione conservativa). Per isolare il solo algoritmo safe_passage servirebbe un
test a border uguale (non fatto: quei border sono gli ottimi rispettivi).
