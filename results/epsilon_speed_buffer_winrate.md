# Buffer di steps dipendente dalla velocità — win-rate vs WISQ

Analisi su `data/results/cube_summary_all_wisq_dinuovo.csv` (263 circuiti,
sweep cube WISQ-native, `mr_timeout=12000s`). Stesso dataset di
[cube_wisq_results.md](cube_wisq_results.md).

## Idea

La metrica primaria sono i **routing steps**, il tempo è secondaria. Siccome siamo
quasi sempre molto più veloci (mediana ~417× sui circuiti contesi), concediamo un
**buffer ε** sugli steps che cresce con l'ordine di grandezza del vantaggio di tempo:

```
vinco  se   my_steps <= wisq_steps · (1 + ε)
ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time
```

- `log10` perché gli speedup vanno da ~32× a ~2000×: il buffer deve dipendere
  dall'ordine di grandezza, non dal valore lineare.
- Se `speedup ≤ 1` (siamo più lenti) → `ε = 0`: nessun buffer, nessuna vittoria
  regalata.
- ε si applica **solo ai veri loss** (`my_steps > wisq_steps`); la baseline resta
  identica al report cube.

## Calibrazione ad ancora

α è fissato da un'ancora "5% di sforo sugli steps ⇄ N× di velocità":
`α = 0.05 / log10(N)`. Più alta è N, più stretto è il buffer.

## Win-rate per ancora

Baseline (steps primario, tempo solo come spareggio) = **158/263 = 60.1%**.

| ancora | α | loss recuperati | vittorie | % |
|---|---:|---:|---:|---:|
| 5% ⇄ 20× | 0.0384 | 37 | 195 | 74.1% |
| 5% ⇄ 50× | 0.0294 | 31 | 189 | 71.9% |
| 5% ⇄ 100× | 0.0250 | 28 | 186 | 70.7% |
| 5% ⇄ 150× | 0.0230 | 28 | 186 | 70.7% |
| 5% ⇄ 200× | 0.0217 | 27 | 185 | 70.3% |
| 5% ⇄ 300× | 0.0202 | 27 | 185 | 70.3% |
| 5% ⇄ 400× | 0.0192 | 24 | 182 | 69.2% |
| 5% ⇄ 500× | 0.0185 | 24 | 182 | 69.2% |
| 5% ⇄ 750× | 0.0174 | 23 | 181 | 68.8% |
| 5% ⇄ 1000× | 0.0167 | 22 | 180 | 68.4% |
| 5% ⇄ 1500× | 0.0157 | 22 | 180 | 68.4% |
| 5% ⇄ 2000× | 0.0151 | 22 | 180 | 68.4% |
| 5% ⇄ 2500× | 0.0147 | 22 | 180 | 68.4% |
| 5% ⇄ 3000× | 0.0144 | 22 | 180 | 68.4% |
| 5% ⇄ 4000× | 0.0139 | 20 | 178 | 67.7% |
| 5% ⇄ 5000× | 0.0135 | 20 | 178 | 67.7% |

## Note

- Oltre i ~200× la curva si appiattisce: i loss recuperabili sono quasi tutti
  sotto i ~5% di sforo, mentre i loss "veri" (synth densi `d020`, qft grandi
  `n300/n400`) hanno +50…117% di steps e nessuna soglia ragionevole li copre.
- I 17 timeout WISQ + i 2 nostri errori non dipendono dal buffer (i primi sono
  vittorie a prescindere, i secondi mai).
