# Pesi tunati — regime BFS

Riepilogo dei pesi gaussiani ottimi nel **regime BFS** (CNOT-BFS mapping order,
gate `density < bfs_density_threshold`, default **0.70**). Metrica di ottimizzazione:
`non_routed_layer_pct` mean-no-out (più basso = meglio). Dettagli e analisi in
[metric_analysis.txt](metric_analysis.txt).

## Comuni a tutte le configurazioni

| parametro | valore | note |
|---|---|---|
| `external_weight` | **≈ −15** (vedi nota) | NEGATIVO batte lo `0` storico ovunque; satura (cube da −5, noncube da −15) |
| `base_gaussian_weight` | **1** | |
| `bfs_density_threshold` | **0.70** | soglia densità BFS↔heap; post-fix BFS batte heap quasi ovunque (plateau ottimo 0.65–0.90, vedi [bfs threshold re-tune](#)); configurabile JSON/CLI, env `FTQC_BFS_DENSITY_THRESHOLD` override |
| `cnot_low` | **0** | verificato inerte sotto BFS (cl=0/0.5/1/1.5 → non_routed identico) |
| `number_of_magic_states` | **−1** | auto |
| magic placement | **center_circle + border%** | mai right_row |
| routing / t-routing | naive / smart_t_routing | |

## Per regime (geometria × strategia)

| regime | confidence | `cnot_high` | `mapped` | `magic_high` | `magic_low` |
|---|---|---|---|---|---|
| **coarse / cube** | **0.99999999** (8 nove) | 1.5 | **0** | dipende da border (sotto) | 0 |
| **coarse / noncube** | **0.999999999999** (12 nove; non satura) | 1.5 | 2.0 | dipende da border (sotto) | 0 |
| **fine / cube** | **0.9999** | 0.5 | **0** | dipende da border (sotto) | **1 se border ≤ 10**, altrimenti 0 |
| **fine / noncube** | **0.999999999999** (12 nove; non satura) | 0.5 | 1.5 | dipende da border (sotto) | 0 |

### `magic_high` per border (al `mapped` raccomandato della tabella sopra)

| regime | b=0 | b=5 | b=10 | b=20 | b=30 | andamento |
|---|---|---|---|---|---|---|
| **coarse / cube** | 0 | 0.2 | 0.2 | 0.2 | 1.6 | piatto basso |
| **coarse / noncube** | 0 | 0.2 | 0.8 | 0.8 | 0.2 | basso, nessun trend |
| **fine / cube** | 20* | 3 | 1.6 | 0 | 0 | decresce col border |
| **fine / noncube** | 3 | 1.6 | 0.4 | 0.4 | 0.2 | decresce col border |

\* fine/cube a b=0: l'argmin robusto è 20, MA la curva è piatta sopra ~1.6 (spread
~0.2pp = rumore: 1.6/3/6/12/20/30 sono in pratica equivalenti) e il minimo ASSOLUTO
di non_routed è a magic basso (magic_high=0.2, 13.72pp). Quindi a b=0 il valore non è
affidabile: tieni magic basso come negli altri border stretti.

In sintesi: **coarse** = magic_high piatto e basso (~0.2) a ogni border, sale a ~1.6 solo
a b=30 nel cube. **fine** = magic_high **decresce col border**, da ~1.6–3 a b=0 fino a ~0
a border largo. In tutti i casi magic alto (≥6) fa male, catastrofico nel noncube.

## Note di lettura

- **`cnot_high` = ginocchio + plateau.** Il valore conta come *minimo necessario*:
  `0` costa +3–4pp, sopra il ginocchio è piatto (valori alti né aiutano né fanno male).
  Non scendere sotto; il valore esatto dentro il plateau è indifferente.
- **`mapped`**: cube → `0` (vuole repulsione minima, è al pavimento). noncube → minimo
  interno genuino (conca ~1.5–2.0, peggio sia a 0 che a valori alti).
- **`magic_high`**: dipende dal border (vedi tabella). Coarse = piatto basso (~0.2);
  fine = decresce col border. Magic alto (≥6) fa male; nel **noncube è catastrofico**
  (+3–8pp).
- **`magic_low`**: il coarse non lo usa (inerte → 0). Nel fine ha effetto debole:
  `1` aiuta un po' solo in **fine/cube con border ≤ 10**; altrove `0` (alto fa male).
- **cube: `mapped=0` + `magic_high` basso.** La vecchia regola "border largo → magic alto"
  era un artefatto del tenere `mapped>0`; in assoluto `mapped=0 + magic basso` vince
  (−0.52pp coarse, −1.05pp fine).
- **`confidence`** (sweep 0.5→12 nove, pesi fissati):
  - **noncube** (coarse+fine): leva fortissima (da 0.5 a 6-nove ~−5/−6pp), poi continua a
    scendere **dolcemente fino al limite di rappresentazione — NON satura** (deep sweep:
    miglior bucket = 1e-13..1e-16). Oltre `1e-12` il guadagno è <0.1pp e **non loggabile**
    (il CSV tronca a ~12 cifre, e il double a 1e-16). => usa **0.999999999999 (12 nove)**:
    il valore più profondo ancora distinguibile, già al fondo del beneficio. Mai sotto 6 nove.
  - **coarse/cube**: monotòno ↓, **NON satura**: migliora fino a `0.99999999` (8 nove, max
    testato). Span piccolo (~0.4pp) ma sempre meglio salire.
  - **fine/cube**: conca con minimo a `0.9999`, poi **peggiora** lievemente (oltre 0.99999
    +0.1pp). NON spingere all'estremo: vuole confidence media.
- **`external_weight`** (sweep 0 → −30, pesi fissati + intorno altri pesi): **NEGATIVO
  vince ovunque**, lo `0` storico è battuto (i vecchi sweep testavano solo ≥0). Direzione
  univoca: più negativo = meglio, poi **SATURA in un plateau** (confermato estendendo a −30):
  - **noncube** (coarse+fine): leva FORTE, ~**−1.5/−2pp**. Satura entro **−15**
    (−15/−20/−30 identici, excess 0.12). Il "−15 ancora in discesa" del primo sweep era
    rumore: è plateau.
  - **cube**: leva debole (coarse ~−0.07pp, fine ~−0.27/−0.6pp), satura prestissimo (~**−5**).
  - **Robusto agli altri pesi** (controllato variando cnot/mapped/magic attorno all'ottimo).
  - **Raccomandazione: `external ≈ −15`** (plateau sicuro per tutti; −5 basta al cube).
    Oltre −20 inutile. Nota: a external molto negativo i noncube perdono qualche run per
    safe_passage_failed (non incide sull'ottimo).

## Attenzione

- **Niente d-scaling in regime BFS**: `cnot_high`/`mapped` sono piccole COSTANTI, non
  scalano con la dimensione (l'ordine BFS fa il lavoro strutturale). Le vecchie formule
  `peso ∝ dim` valgono solo nel regime heap (`density ≥ bfs_density_threshold`, ora 0.70).
- **`cnot` e `mapped` interagiscono** (cresta antagonista: mapped respinge, cnot attrae).
  Non scalare `mapped` da solo; tienili entrambi piccoli.
- **qft**: con la soglia a 0.70 quasi tutti i qft finiscono in regime BFS e vogliono
  `cnot` basso ~0.5–1 (qft_n50 dens 0.65 e qft_n64 dens 0.53 ora sono BFS — recuperati
  rispetto al vecchio 0.40 dove restavano heap). Restano heap solo i densissimi
  (randomcircuit ~0.97), che infatti preferiscono heap.
- **synth_d040** è completamente inerte sotto BFS (ottimo a pesi nulli): l'ordine basta.
