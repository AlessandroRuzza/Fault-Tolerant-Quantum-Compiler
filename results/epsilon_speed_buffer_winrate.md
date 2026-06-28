# Buffer di steps dipendente dalla velocità — win-rate vs WISQ

Analisi su `data/results/cube_summary_all_wisq_dinuovo.csv` (**258 circuiti** nel CSV corrente potato). Stesso dataset di [cube_wisq_results.md](cube_wisq_results.md).

## Idea

La metrica primaria sono i **routing steps**, il tempo è secondaria. Concediamo un buffer ε sugli steps che cresce con l'ordine di grandezza del vantaggio di tempo:

```
vinco  se   my_steps <= wisq_steps · (1 + ε)
ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time
```

- Se `speedup ≤ 1` (siamo più lenti) → `ε = 0`.
- ε si applica **solo ai veri loss** (`my_steps > wisq_steps`).

## Calibrazione ad ancora

α è fissato da un'ancora "5% di sforo sugli steps ⇄ N× di velocità": `α = 0.05 / log10(N)`.

## Win-rate per ancora

Baseline (steps primario, tempo solo come spareggio) = **156/258 = 60.5%**.

| ancora | α | loss recuperati | vittorie | % |
|---|---:|---:|---:|---:|
| 5% ⇄ 20× | 0.0384 | 37 | 193 | 74.8% |
| 5% ⇄ 50× | 0.0294 | 31 | 187 | 72.5% |
| 5% ⇄ 100× | 0.0250 | 28 | 184 | 71.3% |
| 5% ⇄ 150× | 0.0230 | 28 | 184 | 71.3% |
| 5% ⇄ 200× | 0.0217 | 27 | 183 | 70.9% |
| 5% ⇄ 300× | 0.0202 | 27 | 183 | 70.9% |
| 5% ⇄ 400× | 0.0192 | 24 | 180 | 69.8% |
| 5% ⇄ 500× | 0.0185 | 24 | 180 | 69.8% |
| 5% ⇄ 750× | 0.0174 | 23 | 179 | 69.4% |
| 5% ⇄ 1000× | 0.0167 | 22 | 178 | 69.0% |
| 5% ⇄ 1500× | 0.0157 | 22 | 178 | 69.0% |
| 5% ⇄ 2000× | 0.0151 | 22 | 178 | 69.0% |
| 5% ⇄ 2500× | 0.0147 | 22 | 178 | 69.0% |
| 5% ⇄ 3000× | 0.0144 | 22 | 178 | 69.0% |
| 5% ⇄ 4000× | 0.0139 | 20 | 176 | 68.2% |
| 5% ⇄ 5000× | 0.0135 | 20 | 176 | 68.2% |

## Note

- Oltre i ~200× la curva si appiattisce: i loss recuperabili sono quasi tutti sotto i ~5% di sforo.
- I timeout WISQ sono vittorie a prescindere e non dipendono dal buffer.
