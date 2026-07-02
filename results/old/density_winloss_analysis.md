# Analisi densità: dove vinciamo/perdiamo vs WISQ

Join di [`cache_metrics/all_circuits_cache_metrics.csv`](../data/results/cache_metrics/all_circuits_cache_metrics.csv) con [`connectivity_summary_all_wisq.csv`](../data/results/connectivity_summary_all_wisq.csv).
I CSV correnti hanno 258 circuiti; le tabelle sotto usano i **242 circuiti dove entrambi completano**.

WIN/LOSS sono sul numero di routing steps; `ratio` = `wisq_steps / my_steps` (>1 = vinciamo).

## Headline: soglia a cid ≈ 0.15

| Regime | N | WIN | TIE | LOSS | loss% | ratio mediano (wisq/noi) |
|---|---|---|---|---|---|---|
| **Sparso** (cid < 0.15) | 114 | 29 | 83 | 2 | 2% | 1.000 |
| **Denso** (cid ≥ 0.15) | 128 | 3 | 37 | 88 | 69% | 0.912 |

Sotto cid≈0.15 perdiamo raramente; sopra, le sconfitte sono il regime dominante e il rapporto mediano resta sotto 1.

## Spaccato per densità d'interazione (cid)

| cid bucket | N | WIN | TIE | LOSS | loss% | medRatio |
|---|---|---|---|---|---|---|
| [0, 0.05) | 85 | 22 | 63 | 0 | 0% | 1.000 |
| [0.05, 0.1) | 18 | 4 | 13 | 1 | 6% | 1.000 |
| [0.1, 0.2) | 14 | 3 | 8 | 3 | 21% | 1.000 |
| [0.2, 0.4) | 35 | 0 | 10 | 25 | 71% | 0.806 |
| [0.4, 0.7) | 58 | 2 | 18 | 38 | 66% | 0.882 |
| [0.7, 1.0] | 32 | 1 | 8 | 23 | 72% | 0.957 |

## Densità per-layer (`avg_cnot_per_layer`)

| cnot/layer | N | WIN | TIE | LOSS | loss% | medRatio |
|---|---|---|---|---|---|---|
| [0, 1.5) | 46 | 2 | 42 | 2 | 4% | 1.000 |
| [1.5, 2) | 27 | 0 | 26 | 1 | 4% | 1.000 |
| [2, 3) | 41 | 0 | 40 | 1 | 2% | 1.000 |
| [3, 5) | 7 | 0 | 4 | 3 | 43% | 1.000 |
| [5, 10) | 42 | 4 | 3 | 35 | 83% | 0.896 |
| [10, ∞) | 79 | 26 | 5 | 48 | 61% | 0.892 |

Il bucket ≥10 resta bimodale: le vittorie sono quasi tutte densi-locali (`ising`, `graphstate`), mentre le sconfitte sono densi non-locali (`synth`, `qaoa`, `vqe_two_local`, `randomcircuit`).

## Caso a parte: cliff QFT

Le sconfitte peggiori sono i QFT grandi: non è un effetto densità generico ma una patologia della strategia connectivity.

| family | conn medRatio | cube medRatio |
|---|---|---|
| qft | 0.834 | 0.861 |
| synth | 0.800 | 0.823 |
| qaoa | 0.850 | 0.875 |
| vqe_two_local | 0.921 | 0.990 |
| randomcircuit | 0.906 | 0.982 |

| qft n | conn | cube |
|---|---|---|
| 100 | 0.806 | 0.766 |
| 125 | 0.201 | 0.786 |
| 200 | 0.191 | 0.713 |
| 400 | 0.188 | 0.642 |

## In sintesi

- Vinciamo/pareggiamo su quasi tutto ciò che è sparso o denso-ma-locale.
- Perdiamo sui densi non-locali: `synth`, `qaoa` medio-grandi, `vqe_two_local`, `randomcircuit`.
- Il cliff QFT resta separato: `cube` riduce molto il problema, pur non eliminandolo del tutto.
