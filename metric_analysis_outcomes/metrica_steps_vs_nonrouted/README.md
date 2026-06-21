# Cambia l'ottimo dei pesi se si tuna su `routing_steps` / `parallelism` invece di `non_routed_layer_pct`?

**Analisi su TUTTI gli sweep di tuning pesi gaussiani in `data/results/`, `old_results_11june/`, `old_results_13june/`** (≈4 GB di CSV, 297 celle sweep×regime×parametro). Data: 2026-06-21.

---

## TL;DR (risposta breve)

1. **`parallelism` NON è una metrica indipendente da `routing_steps`.** Per costruzione `avg_parallelism = numGates / routing_steps` ([one_execution.hpp:600-602](../../src/one_execution.hpp#L600)), e `numGates` è costante per ogni circuito → **per ogni circuito, minimizzare routing_steps ≡ massimizzare parallelism, ranking identico** (verificato: `routing_steps × avg_parallelism` costante per 128/139 circuiti, le 11 eccezioni sono solo arrotondamenti tipo 14178.0 vs 14178.01). Quindi sotto c'è **un solo confronto**: `non_routed_layer_pct` (storico) vs `routing_steps` (= parallelism).

2. **Nel ~91% dei casi l'ottimo NON cambia in modo rilevante.** Su 297 celle: **63% ottimo identico**, **28% differisce solo tra valori adiacenti di plateau** (regret trascurabile), **9% (26 celle) differenza "consequential"** (regret non_routed >0.2pp *oppure* routing_steps >1%).

3. **Il set di pesi tunati resta valido anche per steps/parallelism.** Nessuna delle leve dominanti si ribalta: dimensione, `mapped` (mai piccolo), `sigma` (~0.5–0.7, mai minuscolo/enorme), `external` (negativo, satura), `cnot_low=0`, `border≠0` → **concordi su entrambe le metriche**.

4. **L'unica tensione sistematica** (piccola) è coerente con UN solo meccanismo fisico già documentato per `magic_high`: **routing_steps premia percorsi più corti / meno congestione**, quindi spinge l'ottimo verso **attrazione spaziale più debole/tigliata** — cnot_high più basso, sigma leggermente più stretto, magic_high leggermente >0, magic verso il bordo. **non_routed** premia la **fattibilità** (impacchettare i qubit interagenti) anche a costo di un filo di congestione. **Le due cose confliggono solo ai margini, con magnitudo piccola.**

---

## Metodologia

Per ogni file `*_runs.csv`, per ogni parametro-peso effettivamente variato (`magic_high, magic_low, cnot_high, cnot_low, mapped_gaussian_weight, gaussian_sigma`/`gaussian_confidence`, `border_distance_percentage, external_weight`):

- Split per **regime** = `gaussian_strategy` (coarse/fine) × cube/noncube (cube = `safe_passage=='cube'`).
- Solo `mapping_type=='gaussian'`, `status=='success'`, `non_routed≥0`, `routing_steps>0`.
- **Best-per-circuito marginale** (come nel tuning storico): per ogni `(regime, circuito, P=v)` si prende il run migliore su TUTTI gli altri parametri, **indipendentemente per ciascuna metrica** (min non_routed; e separatamente min routing_steps). Cioè: "se fisso P=v e ottimizzo tutto il resto per QUESTO circuito, qual è il miglior non_routed / il miglior routing_steps?".
- Solo circuiti presenti a **tutti** i valori di P (casi completi, confronto appaiato).
- Curva `non_routed`: media sui circuiti di `best_nr[c][v]` → argmin = **P\*_nr**.
- Curva `steps`: per circuito si normalizza `best_rs[c][v] / min_v(best_rs[c][·])` (overhead relativo, scale-fair fra circuiti di taglie diverse) → media → argmin = **P\*_steps**. Questa normalizzazione è esattamente l'ordinamento per parallelism (overhead = 1/parallelism normalizzato).
- **Regret** (la quantità che conta per la decisione):
  - `nr_regret` = quanto non_routed (pp) perdi adottando P\*_steps invece di P\*_nr.
  - `rs_regret` = quanto routing_steps (%) perdi tenendo P\*_nr invece di P\*_steps.
  - **consequential** se `nr_regret>0.2pp` **o** `rs_regret>1%`.

> ⚠️ Nota tecnica risolta: nei CSV recenti (`data/results/`) la colonna 17 si chiama **`gaussian_sigma`** (sigma assoluto), in quelli vecchi `gaussian_confidence`. Entrambe sono la stessa leva (σ della gaussiana) e sono incluse. `avg_parallelism` come colonna esiste solo nei CSV nuovi (`best_params_ofat`, `magic_high_finecube`, `magic_low_tune`, `nontuned_correlation`); ovunque la ricavo da routing_steps, che è equivalente.

Dettaglio completo cella-per-cella (curve incluse): vedi `appendix_results.txt`, `appendix_11june.txt`, `appendix_13june.txt` in questa cartella.

---

## Risultato globale

| set | celle | ottimo IDENTICO | DIFFER totale | di cui *consequential* | di cui entro-rumore |
|---|---|---|---|---|---|
| `data/results/` (autorevole) | 187 | 120 (64%) | 67 | **12** | 55 |
| `old_results_11june/` | 77 | 46 (60%) | 31 | **13** | 18 |
| `old_results_13june/` | 33 | 21 (64%) | 12 | **1** | 11 |
| **TOTALE** | **297** | **187 (63%)** | **110** | **26 (8.8%)** | **84 (28%)** |

Le 26 celle consequential per parametro: `mapped` 6, `cnot_high` 6, `magic_high` 5, `border` 5, `magic_low` 2, `gaussian_sigma` 2.

---

## I temi di divergenza (quando e perché differiscono)

Tutte le divergenze "vere" hanno **lo stesso segno e lo stesso meccanismo**: `routing_steps` vuole **meno attrazione/concentrazione spaziale** perché paga la congestione locale; `non_routed` vuole **più impacchettamento** perché conta i layer infattibili. Magnitudo sempre piccola.

### 1. `cnot_high` — steps vuole CNOT più DEBOLE *(il segnale più netto)*
Caso più chiaro: **`optimum_sweep` fine/noncube** (1.2M run, 47 circ):
```
nonrouted: piatto 3.01–3.18 su cnot 0–25 (min a 4=3.014), salto a 26+
steps(rel): cnot 0–1 = 1.013 ; cnot ≥2 = ~1.09  → +8% se cnot≥2
```
→ con mapped alto, alzare `cnot_high` oltre ~1 **non aiuta non_routed e costa ~8% routing_steps**. Stesso verso in `cnotlow` coarse/noncube (nr8→steps2, +1.1%), `corr_sweep`, `bfs_retune_cnotdim`. **non_routed è quasi piatto su cnot, steps preferisce il basso.** Regret non_routed quasi sempre <0.13pp.

### 2. `mapped_gaussian_weight` — divergenza solo agli ESTREMI / sulla cresta
`mapped` vive su una cresta senza ottimo isolato (già documentato). Dove le metriche divergono è agli estremi alti, in modo **regime-specifico e bidirezionale**:
```
mapped_sigma fine/noncube:  nr* =16 (3.857)  steps*=48   | nr +0.71pp, steps +5.08%
   nonrouted ha knee a 16 poi peggiora (32→4.60); steps cala monotono fino a 48 (1.035)
sigma_weights fine/noncube: nr* =25           steps*=1    | verso OPPOSTO
```
→ Le due metriche scelgono punti diversi della **cresta piatta**: non è un conflitto reale, è ambiguità del plateau. Nel range "sano" (mapped 8–20) **concordano** (coarse/noncube, fine/cube: regret 0.00).

### 3. `gaussian_sigma` — steps vuole σ leggermente più STRETTO
`ridge_sigma` coarse/cube nr0.7→steps0.5 (+1.18% steps); `sigma_regime` fine/noncube, `cnotlow` fine/noncube, `mapped_sigma` coarse/noncube: stesso verso (steps 0.5 vs nr 0.7). Un'eccezione (`sigma_regime` fine/cube, steps vuole 1.5). **Entrambe puniscono σ minuscolo (0.3) e σ enorme (≥2): l'ottimo largo 0.5–0.7 è condiviso**, steps lo tira di un gradino verso il basso. Regret ≤0.32pp / ≤1.18%.

### 4. `border_distance_percentage` — per lo più CONCORDE; divergenze piccole e di segno misto
Con i set grandi di circuiti **concorda** (`best_params_ofat` nc=139: nr25/steps25; `nontuned_correlation` nc=84: nr30/steps30; regret 0.00). Le divergenze sono solo nei set piccoli/curati (nc=14–47) e **non hanno verso stabile** (a volte steps vuole border più grande: `magic_tune_quick` coarse +2.2%; a volte più piccolo: `magic_tune_tbear` coarse/cube steps=5). → essenzialmente plateau; **0 catastrofico per entrambe**.

### 5. `magic_high` / `magic_low` — inerte/rumoroso (conferma del già noto)
`magic_high` ha argmin instabile (per-circ agreement spesso ~50%) e regret piccolo. Conferma esatta di quanto già in [pesi_tunati.md](../pesi_tunati.md): su non_routed è **inerte**, su routing_steps dà un **piccolo** guadagno (~0.3–0.5%) avvicinando i qubit-T alle magic. Es. `magic_tune_tbear` coarse/cube: nr*=0, steps*=4 (nr +0.21pp, steps +0.74%). Nei file PRE-fix (11june: `gaussian_magicknee/sweep`, `magic_retune`) la divergenza è ampia ma è **artefatto heap-rotto/mapped>0** (vedi pesi_tunati) — non valida per nessuna delle due metriche.

### 6. `external_weight`, `cnot_low` — CONCORDI in sostanza
- `external`: entrambe vogliono **negativo** e **saturano** subito; nel noncube 0→nr 7.97/steps 1.16×, −15→nr 5.59/steps 1.00× (concordi e forti). Le "differenze" (es. cube nr0 vs steps−15) sono su curve piatte → regret 0.00pp/0.15%.
- `cnot_low`: **0 ovunque** per entrambe (regret nullo); rare celle dove steps preferisce 1–2 sono entro rumore.

---

## Conclusione operativa

**Tunare su `routing_steps`/`parallelism` invece che su `non_routed_layer_pct` NON cambia il set di pesi raccomandato in modo materiale.** Il set di [pesi_tunati.md](../pesi_tunati.md) (σ≈0.7, mapped 15–20, cnot 6–8, magic 0/0, external −5, border 10–15, cnot_low 0, base 1) resta dentro l'ottimo (o sul plateau) anche per steps/parallelism.

Se in futuro si decidesse di **ottimizzare esplicitamente routing_steps/parallelism**, gli unici aggiustamenti suggeriti dai dati (tutti piccoli, tutti nello stesso verso "meno congestione"):

| parametro | per non_routed | se ottimizzi steps/parallelism | costo del cambio |
|---|---|---|---|
| `cnot_high` | 6–8 | **~1–2** (più basso) | fino a −8% steps; non_routed +≤0.13pp |
| `gaussian_sigma` | 0.7 | **~0.5** (più stretto) | ~−1% steps; non_routed +≤0.3pp |
| `magic_high` | 0 | **~0.25–1** (>0) | ~−0.3÷0.7% steps; non_routed +≤0.2pp |
| `mapped` | 15–20 | indifferente nel range sano (estremi = cresta) | — |
| `border`, `external`, `cnot_low`, `magic_low`, dimensione | identico | identico | 0 |

**Trade-off netto**: passare al regime "steps-ottimo" guadagna tipicamente **1–8% di routing_steps** (e quindi parallelism) costando **<0.3pp di non_routed** nella stragrande maggioranza dei casi. È la stessa tensione fattibilità-vs-lunghezza-percorso già osservata su `magic_high`, ora dimostrata generalizzarsi a `cnot_high` e `sigma`, ma **mai abbastanza forte da ribaltare una raccomandazione**.
