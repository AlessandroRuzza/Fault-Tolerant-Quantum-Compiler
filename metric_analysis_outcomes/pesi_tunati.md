# Pesi tunati — regime BFS

## Comuni a tutte le configurazioni

| parametro | valore | note |
|---|---|---|
| `external_weight` | **negativo, ≈ −5** | qualsiasi negativo ≈ ottimo, satura subito; `0` costa ~−1.5pp nel noncube (cube basta −5; noncube plateau da ~−15) |
| `base_gaussian_weight` | **1** | |
| `bfs_density_threshold` | **0.70** | soglia densità BFS↔heap; post-fix BFS batte heap quasi ovunque (plateau ottimo 0.65–0.90); JSON/CLI, env `FTQC_BFS_DENSITY_THRESHOLD` override |
| `cnot_low` | **0** | inerte (0/0.5/1/1.5 → non_routed identico; ≥4 fa male) |
| `magic_low` | **0** | usato solo in `fine`; gap aperto (vedi sezione magic) |
| `number_of_magic_states` | **−1** | auto |
| magic placement | **center_circle + border%** | mai right_row |
| routing / t-routing | naive / smart_t_routing | |

## Valori tunati per regime

`sigma`, `mapped`, `cnot_high` validati su `optimum_sweep` (48 circ; σ 0.2–4, mapped 10–60,
cnot=mapped/2.5 ±4, dim ×10). Sono **centri di plateau**: l'esatto valore conta poco (i pesi
spostano ≤1.4pp, la dimensione ~8pp). `external`, `magic_low`, `cnot_low` sono comuni a tutti
i regimi (vedi tabella in alto).

| regime | sigma | mapped | cnot_high | magic_high | border | non_routed best |
|---|---|---|---|---|---|---|
| coarse / cube    | **0.7** | **15** | **6** | 0 | 10–15 | ~2.87 |
| fine / cube      | **0.7** | **15** | **6** | 0 *(≈1 di un soffio)* | 10–15 | ~2.88 |
| coarse / noncube | **0.7** | **20** | **8** | 0 | 10–15 | ~3.29 |
| fine / noncube   | **0.7** | **20** | **8** | 0 | 10–15 | ~3.30 |

Set unico robusto: **σ=0.7, mapped=20, cnot=8, magic 0/0, border 10–15, external −5, base 1**.
Marginali: σ ottimo 0.65–0.75 (0.2 degenera, ≥3 troppo diffuso); mapped plateau 10–30 (≥40 nessun
guadagno; cube piatto); cnot piatto attorno a ~mapped/2.5.

## Modello sulla cresta mapped ↔ cnot ↔ σ

`mapped` e `cnot` non hanno un ottimo isolato: vivono su una **cresta** lungo la retta
`cnot = mapped / 2.5` (coppie basso-basso ↔ alto-alto equivalenti). **σ resta ≈ 0.7 costante lungo
la cresta** (`ridge_sigma_sweep`: mapped 1→40, esponente log-log ≈ 0). L'anti-correlazione
"mapped↑ → σ↓" vista off-cresta era solo un artefatto di sbilancio attrazione/repulsione a cnot
fisso — niente legge `σ = √(C/mapped)` (testata e respinta).

In sintesi: `σ ≈ 0.7`, `cnot = mapped/2.5`, `mapped ≈ 5–20` (noncube 5–20, cube 10–20; oltre 40
peggiora). Miglior non_routed sulla cresta: ~4.2–4.5 noncube, ~3.4–4.0 cube.

## magic_high & border (46 circuiti T-bearing)

Sweep dedicato `magic_tune_tbear` (46 circuiti **tutti con T gate** — sugli altri il segnale si
diluiva: solo ~21/48 hanno T). Aggregazione **best-per-circuito** (min su border/cnot/mapped/
external/sigma/dim) poi **media**. Effetto di `magic_high` per regime:

| regime | mh=0 | 0.2 | 0.5 | 1 | 2 | 4 | ottimo |
|---|---|---|---|---|---|---|---|
| coarse / connectivity | **6.310** | 6.577 | 6.627 | 6.684 | 6.979 | 7.002 | **0** (−0.69pp salendo) |
| coarse / cube         | **5.939** | 5.995 | 6.023 | 6.122 | 6.175 | 6.149 | **0** (−0.24pp) |
| fine / connectivity   | **6.453** | 6.772 | 6.770 | 6.833 | 7.009 | 7.156 | **0** (−0.70pp) |
| fine / cube           | 5.986 | 5.967 | 5.939 | **5.922** | 5.927 | 5.953 | **≈1** (+0.06pp, conca piatta) |

- **`magic_high = 0` è l'ottimo in 3 regimi su 4**, e alzarlo **peggiora monotonicamente** — forte nel
  **noncube/connectivity** (−0.7pp), lieve nel **cube** (−0.24pp). **Unica eccezione: `fine/cube`**:
  conca piatta con ottimo a `magic_high ≈ 1` (guadagno minuscolo, ~0.06pp).
- **`border` ha un ottimo netto ~10–15** (cube 5–15, noncube 10–20): `border=0` è **catastrofico**
  (+2–3pp), ≥25 peggiora. Marginali (T-bearing): noncube 10:7.18 / 15:7.20; cube 5:6.35 / 15:6.52.

**Perché magic_high non aiuta (verifica codice 2026-06-20, nessun bug)**: la metrica (`naive` →
`QubitRouter`) **conta i T-gate** in `first_exposure` ([routing.cpp:514](../src/routing.cpp#L514)),
`weight=0` dà davvero contributo nullo ([gaussian.cpp:39-48](../src/gaussian.cpp#L39-L48)), e le
magic_gaussians **entrano** nello score. Il meccanismo funziona ma non serve perché (1)
`center_circle` mette le magic già al centro, dove il **baseline** tira comunque (ridondanza); (2)
l'attrazione è verso la **somma** di tutte le magic (il centroide), non verso la più vicina → ammucchia
i qubit al centro → congestione che danneggia il routing dei **CNOT** (la maggioranza dei gate anche
nei T-bearing); (3) i T-gate vanno comunque alla magic libera più vicina via Dijkstra.

**⚠ Gap aperto — `magic_low`**: in `magic_tune_tbear` `magic_low` è stato tenuto **fisso a 0** in tutti
i blocchi. È stato variato ≠0 solo in `external_magic_sweep` (non ristretto ai T-bearing, non focalizzato
su `fine`) dove 0.5/1 peggioravano ~0.1–0.2pp. Ma `magic_low` agisce **solo in `fine`** (in `coarse` è
ignorato, vedi [gaussian_mapping.cpp:424-428](../src/mapping/gaussian_mapping.cpp#L424-L428)) e
rimodella la banda di T attorno alla media — incl. il caso `magic_high=0, magic_low>0` (rampa inversa).
Dato che **`fine/cube` è l'unico regime dove magic aiuta**, `magic_low>0` lì è genuinamente non testato.
→ sweep dedicato `magic_low_tune` (solo regimi fine, 46 T-bearing) preparato, da lanciare.

→ **magic_high = 0** (fissa e dimentica; `fine/cube` ≈ 1 di un soffio), **border ≈ 10–15**,
**magic_low = 0** (da confermare con `magic_low_tune`).

---

## Matrice completa delle correlazioni (riepilogo unico)

Consolidamento di **tutte** le relazioni trovate finora sul binario sigma (espande il
riepilogo breve qui sopra). Forza = quanto una variabile sposta l'ottimo dell'altra;
direzione = concorde (↗ insieme) / opposta (↘ una sale, l'altra scende) / nessuna.

### A. Pesi ↔ pesi

| relazione | forza | direzione | cosa significa in pratica | sweep |
|---|---|---|---|---|
| **mapped ↔ cnot** | **FORTE** | **concorde** | cresta antagonista: `mapped ≈ 2.5·cnot`. Non c'è un ottimo singolo ma una **cresta di coppie equivalenti** (basso-basso ↔ alto-alto). Tararli **insieme**, mai mapped da solo. | `sigma_weights`, `optimum_sweep`, `mapped_sigma_sweep` |
| **mapped ↔ sigma** | FORTE off-cresta, **NULLA sulla cresta** | opposta (apparente) | l'anti-correlazione "mapped↑→σ↓" è un **artefatto** di sbilancio attrazione/repulsione a cnot fisso. **Sulla cresta σ resta ≈0.7 costante** a ogni mapped (esponente log-log ≈0). Niente legge `σ=√(C/mapped)` (respinta). | `sigma_dim`, `mapped_sigma_sweep`, `ridge_sigma_sweep` |
| **sigma ↔ cnot** | debole/assente | — | σ lo governa `mapped`, non `cnot`. Nel range sano di cnot σ* non si muove (~0.7). → si può fissare cnot e co-tarare solo `mapped×σ`. | `sigma_weights` |
| **external ↔ mapped** | debole/**ridondante** | concorde-funzionale | entrambi **repulsivi**: con external negativo, mapped alto smette di far male; a external=0 mapped alto peggiora. Col mapped alto basta pochissimo external. | `corr_sweep`, `optimum_neighborhood` |
| **external ↔ sigma / cnot** | **nessuna** | — | external è un knob **indipendente** che satura subito (qualsiasi negativo −1÷−5 ≈ ottimo; `0` costa ~−1.5pp noncube). | `corr_sweep`, `external_magic_sweep` |
| **magic_high ↔ tutto** (mapped/cnot/sigma/external) | **nessuna** | — | nessun ottimo si sposta variando magic_high → **fissa basso e ignora**. | `corr_sweep` |
| **cnot_low ↔ tutto** | **nessuna** | — | disaccoppiato e **inerte** (0–2 identici; ≥4 fa male). | `cnotlow_sweep`, `external_magic_sweep` |
| **magic_low ↔ magic_high** (solo `fine`) | **GAP** | — | mai testato ≠0 sui T-bearing nei regimi fine; rimodella la banda di T centrale (incl. `magic_high=0, magic_low>0`). | `magic_low_tune` (pendente) |

### B. Pesi ↔ dimensione (taglia griglia / padding)

| peso | dipendenza dalla taglia | nota |
|---|---|---|
| **mapped** | **FORTE, concorde** | assorbe quasi tutto lo scaling (piccole ~0–1 → grandi ~10–25). |
| **sigma** | media (cube) / cala (noncube) | griglie **strettissime → σ più largo** (fino ~3); è l'altra metà dello scaling nel cube. |
| **cnot / magic / border / cnot_low** | **assente** | costanti rispetto alla taglia. |

> La **dimensione è la leva dominante in assoluto**: `non_routed` cala **~8–9pp noncube / ~2–3pp
> cube** da griglia stretta a larga, contro **≤1.4pp** di tutti i pesi messi insieme. → dimensiona
> generosamente la griglia e **non** ri-tarare i pesi per taglia.

### C. Pesi ↔ geometria / regime

| relazione | effetto | nota |
|---|---|---|
| **magic_high ↔ geometria** | sì | noncube/connectivity: alzarlo **danneggia forte** (−0.7pp); cube: lieve (−0.24pp); **`fine/cube`** unica conca con ottimo a **~1** (+0.06pp). |
| **magic_high ↔ border** | **nessuna** (smentita) | `magic*=0` a **ogni** border. La vecchia "border largo→magic alto" era artefatto `mapped>0`/heap rotto. |
| **border ↔ pesi/dimensione** | trascurabile | ottimo **10–15** stabile ovunque; `border=0` catastrofico (+2–3pp), ≥25 peggiora. |
| **mapped ↔ geometria** | sì | **cube → mapped basso/0** (vuole repulsione minima); **noncube → conca interna ~15–20**. |

### D. Gerarchia delle leve (dalla più forte alla più debole)
1. **dimensione** (≫ tutto, ~8pp noncube) →
2. **posizione sulla cresta mapped↔cnot** (mapped 5–20, cnot=mapped/2.5) →
3. **external** (negativo, satura subito; ~1.5pp noncube) →
4. **border** (ottimo 10–15; 0 catastrofico) →
5. **sigma** (~0.7 costante sulla cresta; largo solo su griglie strette) →
6. **magic_high / magic_low / cnot_low** (≈inerti: fissa 0, salvo fine/cube magic≈1).

**Regola pratica unica:** σ=0.7, `cnot=mapped/2.5` con mapped 15–20, external −5, border 10–15,
magic 0/0, cnot_low 0, base 1 — e **dimensiona la griglia con largo padding** (la vera leva).
