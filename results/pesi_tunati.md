# Pesi tunati

## Comuni a tutte le configurazioni

| parametro | valore | note |
|---|---|---|
| `external_weight` | **negativo, ≈ −5** | qualsiasi negativo ≈ ottimo, satura subito; `0` costa ~−1.5pp nel noncube (cube basta −5; noncube plateau da ~−15) |
| `base_gaussian_weight` | **1** | |
| `bfs_density_threshold` | **0.70** | soglia densità BFS↔heap; post-fix BFS batte heap quasi ovunque (plateau ottimo 0.65–0.90); JSON/CLI, env `FTQC_BFS_DENSITY_THRESHOLD` override |
| `cnot_low` | **0** | inerte (0/0.5/1/1.5 → non_routed identico; ≥4 fa male) |
| `magic_low` | **0** | usato solo in `fine`; testato (`magic_low_tune`) → effetto nullo (vedi sezione magic) |
| `number_of_magic_states` | **−1** | auto |
| magic placement | **center_circle** |  |
| routing / | **naive**  | naive = miglior non_routed + **12–18× più veloce di packing** + mai timeout; packing solo se routing_steps è l'unico obiettivo (vedi §Tempo di compilazione) |
|t-routing|smart_t_routing||


## Connectivity

| parametro | valore ottimo | note |
|---|---|---|
| `gaussian_strategy` | **fine** | vince su griglie piccole, pareggia sulle grandi; non perde mai |
| `safe_passage_strategy` | **connectivity** | mai peggio di passage_no_subgraphs; inerte nel regime large-grid/border-15 |
| `border_distance_percentage` | **15–20** | plateau ottimo; 0 catastrofico, ≥25 peggiora |
| `routing_strategy` | **packing** *(ma 12–18× più lento, vedi §Tempo)* | minor routing_steps spec. su circuiti grandi (q4: 360 vs 374 naive); naive preferibile per non_routed_layer_pct (0.97 vs ~1.2) E per il tempo di compilazione |

Tutti gli altri parametri (gaussian, safe_passage, border) sono migliori per tutte e 3 le metriche (non_routed_layer_pct, routing_steps, avg_parallelism). Il solo trade-off è routing: packing vince su efficienza (steps), naive vince su fattibilità (non_routed) **e su tempo (vedi sotto)**.

**Pesi gaussiani (fine / noncube):**

| sigma | mapped | cnot_high | magic_high | border | non_routed best |
|---|---|---|---|---|---|
| **0.7** | **20** | **8** *(steps: **1–2**)* | 0 | 10–15 | ~3.30 |


## Cube

Sweep dedicato `cube_structural_sweep` (68k run, safe_passage=cube, pesi cube mapped15/cnot6/ext−5/magic0). Confronto con noncube:

| parametro | cube | uguale a noncube? |
|---|---|---|
| `gaussian_strategy` | **fine** — vince q2 (0.625 vs coarse 0.920 non_routed), pareggia q1/q3, perde marginale solo q4 (8.63 vs 8.55) | ✅ sì (fine vince sui piccoli, ~pari sui grandi) |
| `border_distance_percentage` | **~5–10** — ottimo a 5 (1.86 non_routed), plateau 5–15, degrada da 20; 0 catastrofico (2.44) | ⚠ **NO: cube vuole border più basso** (5–10 vs noncube 15–20) |
| `routing` per **non_routed** | **naive** domina nettissimo (0.625 vs congestion 2.41, naive_critical 2.79, packing 3.14) | ✅ sì, anzi più netto |
| `routing` per **routing_steps** (q4) | **naive_critical** migliore (313), poi packing 320, naive 326; congestion peggiore (387) | ⚠ **in cube naive_critical batte packing sugli steps** — e senza il costo di tempo di packing |
| `routing` tempo | naive/naive_critical ~2.3–2.8s (q4); packing/critical_packing ~43s (**15–19×**), molti timeout (792/823 run >60s vs naive 197) | ✅ stessa gerarchia |

**Pesi gaussiani (fine / cube):**

| sigma | mapped | cnot_high | magic_high | border | non_routed best |
|---|---|---|---|---|---|
| **0.7** | **15** | **6** | 0 *(insensibile; steps: ~0.5–1)* | **5–10** | ~2.88 |


# Spiegazioni

### Differenze cube vs noncube:
1. **border ottimo più basso**: cube ~5–10, noncube 15–20. Conferma la vecchia nota ("cube 5–15"). `border=5` è la scelta cube.
2. **routing_steps**: in cube il miglior compromesso è **`naive_critical`** (miglior steps q4 **e** veloce come naive), NON packing — packing in cube è sia più lento sia peggiore sugli steps. → in cube `naive_critical` è il vero sweet-spot se vuoi steps; `naive` resta il migliore per non_routed (metrica primaria).
3. **coarse/fine** e la **gerarchia di tempo** sono identici al noncube.

> ⚠ Cube è generalmente **più lento/difficile** del noncube: anche `naive` ha 197 run >60s (timeout inclusi) e non_routed q4 ~8.6 (vs noncube più basso). Dimensiona generosamente.

---

## Pesi gaussiane tunati per regime

`sigma`, `mapped`, `cnot_high` validati su `optimum_sweep` (48 circ; σ 0.2–4, mapped 10–60,
cnot=mapped/2.5 ±4, dim ×10). Sono **centri di plateau**: l'esatto valore conta poco (i pesi
spostano ≤1.4pp, la dimensione ~8pp). `external`, `magic_low`, `cnot_low` sono comuni a tutti
i regimi (vedi tabella in alto).

> Valori = ottimo per `non_routed_layer_pct`. **Tra parentesi `(steps: …)` l'ottimo per
> `routing_steps`/`parallelism` solo dove differisce** 


| regime | sigma | mapped | cnot_high | magic_high | border | non_routed best |
|---|---|---|---|---|---|---|
| coarse / cube    | **0.7** | **15** | **6** | 0 *(steps: ~0.5–1)* | **5–10** | ~2.87 |
| fine / cube      | **0.7** | **15** | **6** | 0 *(insensibile; steps: ~0.5–1)* | **5–10** | ~2.88 |
| coarse / noncube | **0.7** | **20** | **8** | 0 | 10–15 | ~3.29 |
| fine / noncube   | **0.7** | **20** | **8** *(steps: **1–2**)* | 0 | 10–15 | ~3.30 |

Differenze metrica (tutte piccole, stesso meccanismo "steps premia percorsi corti / meno congestione"):
**`cnot_high` fine/noncube** → 1–2 invece di 8 (cnot≥2 costa **+2.8% steps** a non_routed≈invariato);
**`magic_high` nel cube** → ~0.5–1 invece di 0 (guadagno ~0.3–0.7% steps; nel coarse/cube costa ~0.2pp
non_routed, in fine/cube quasi gratis); nel **noncube magic=0 per entrambe**. Anche `routing_strategy`
si ribalta: **packing** per steps (naive era meglio per non_routed — vedi tabella in alto).

### Modello sulla cresta mapped ↔ cnot ↔ σ

`mapped` e `cnot` non hanno un ottimo isolato: vivono su una **cresta** lungo la retta
`cnot = mapped / 2.5` (coppie basso-basso ↔ alto-alto equivalenti). **σ resta ≈ 0.7 costante lungo
la cresta** (`ridge_sigma_sweep`: mapped 1→40, esponente log-log ≈ 0). L'anti-correlazione
"mapped↑ → σ↓" vista off-cresta era solo un artefatto di sbilancio attrazione/repulsione a cnot
fisso — niente legge `σ = √(C/mapped)` (testata e respinta).

In sintesi: `σ ≈ 0.7`, `cnot = mapped/2.5`, `mapped ≈ 5–20` (noncube 5–20, cube 10–20; oltre 40
peggiora). Miglior non_routed sulla cresta: ~4.2–4.5 noncube, ~3.4–4.0 cube.

### magic_high & border (46 circuiti T-bearing)

Sweep dedicato `magic_tune_tbear` (46 circuiti **tutti con T gate** — sugli altri il segnale si
diluiva: solo ~21/48 hanno T). Aggregazione **best-per-circuito** (min su border/cnot/mapped/
external/sigma/dim) poi **media**. Effetto di `magic_high` per regime:

| regime | mh=0 | 0.2 | 0.5 | 1 | 2 | 4 | ottimo |
|---|---|---|---|---|---|---|---|
| coarse / connectivity | **6.310** | 6.577 | 6.627 | 6.684 | 6.979 | 7.002 | **0** (−0.69pp salendo) |
| coarse / cube         | **5.939** | 5.995 | 6.023 | 6.122 | 6.175 | 6.149 | **0** (−0.24pp) |
| fine / connectivity   | **6.453** | 6.772 | 6.770 | 6.833 | 7.009 | 7.156 | **0** (−0.70pp) |
| fine / cube           | 5.986 | 5.967 | 5.939 | 5.922 | 5.927 | 5.953 | **0** (curva piatta, ±0.06pp = rumore) |

- **`magic_high = 0` è l'ottimo ovunque.** Nel **noncube/connectivity** alzarlo **peggiora forte**
  (−0.7pp, vero segnale); nel **cube** lieve (−0.24pp). In **`fine/cube`** è **inerte**: il "≈1" letto
  qui era rumore della griglia rada, **smentito** dal sweep fitto `magic_high_finecube` (vedi sotto).
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

**Conferma fine/cube — `magic_high` è inerte** (`magic_high_finecube`: 9 valori 0→3 fitti, magic_low=0,
46 T-bearing). Confronto **appaiato per-circuito** vs mh=0: **media Δ ≤ 0.06pp ma std Δ ≈ 0.7pp**
(errore standard ≈ 0.10pp → ogni Δ entro ±1 SE da zero), **segno instabile** (0.25:−, 0.5:+, 0.75:−,
1:+, 1.25:+, 3:−), **win ≈ loss** (~23/14/9). La variabilità intrinseca di un circuito al variare di mh
è ~0.7pp di range: cambiare magic_high sballotta i circuiti in direzioni casuali che si annullano nella
media. → in fine/cube **nessun magic_high è distinguibile**: `0` è giusto perché è buono quanto tutto,
non perché batta 1. (Il "≈1" del tbear e il min nominale a 0.25 del finecube davano segni opposti — rumore.)

**`magic_low` — testato, effetto nullo** (`magic_low_tune`: regimi fine, 46 T-bearing). Il binario impone
**`magic_high ≥ magic_low`** ([mapping.hpp:510-511](../include/mapping.hpp#L510-L511)): le combo con
mh<ml (incl. `magic_high=0, magic_low>0`, la "rampa inversa") sono **rifiutate** e non testabili senza
modifica al codice (sono i ~30% di run `failed` per validazione, non incompletezza). Dove esplorabile
(mh∈{1,2}, fine/cube): ottimo debolissimo a **ml≈0.3** (−0.05/−0.10pp, dentro il rumore), degrada a
ml≥0.6; in fine/connectivity ml non aiuta (migliore resta mh=0). → **magic_low = 0**.

→ **magic_high = 0** (fine/cube: inerte, non "≈1"), **magic_low = 0**, **border ≈ 10–15**.

**Divergenza tra metriche in fine/cube** (`magic_high_finecube`, confronto appaiato, metrica `routing_steps` %Δ vs mh=0):
le due metriche **non concordano** in questo regime:

| metrica | effetto magic_high (fine/cube) | conclusione |
|---|---|---|
| `non_routed_layer_pct` | Δ ≤ 0.06pp, std 0.7pp, sign instabile, win≈loss | **INERTE** |
| `routing_steps` | Δ% = −0.2÷−0.6% costantemente negativo (tutti 8 valori), win 24–29 vs loss 10–14 (sign-test p≈0.003–0.02) | **magic aiuta ~0.3–0.5%** |

Il meccanismo è coerente: magic_high avvicina i qubit T-bearing alle magic → percorsi più corti (**meno step**) ma non riduce la congestione sui CNOT che causa i layer-split (**non_routed invariato**). Fine/connectivity è neutro su entrambe le metriche (~0%). **La metrica primaria è non_routed → magic=0 resta la raccomandazione. Se in futuro si ottimizza routing_steps, magic_high≈0.25–1 in fine/cube dà un piccolo guadagno (~0.3–0.5%).**

---

## Parametri strutturali (dati noncube) (coarse/fine · safe_passage · border · routing)

### coarse vs fine
Aggregato quasi pari (fine 2.74 / coarse 2.78 non_routed), ma il risultato è atteso: offset 6-12 campiona solo il regime a griglia grande, dove coarse e fine convergono. Disaggregando per quartile di dimensione: fine vince chiaro sulle griglie più piccole del range (q1/q2: fine 0.9/0.27 vs coarse 3.04/1.36) e pareggia sulle grandi. **Fine non perde mai → è la scelta.**

### safe_passage: connectivity vs passage_no_subgraphs
Sweep OFAT (baseline: naive, border 15, griglie grandi): **100% identico** — non_routed e routing_steps byte-identici su 1770/1770 configurazioni, anche dove non_routed > 0. Il baseline scelto è caduto nella zona inerte di safe_passage. Autorità principale: `nontuned_correlation_sweep` completo (border 0-30, offset 0-12), dove connectivity era marginalmente meglio (4.87 vs 5.54 non_routed) e mai peggio. **Usa connectivity; nel regime large-grid/border-15 la scelta è indifferente.**

---

## Tempo di compilazione (`duration_seconds`, sweep OFAT noncube, 70k run)

Within-cell (taglia/circuito fissi). **Routing è l'unico parametro che muove il tempo — e lo muove tantissimo**; tutti gli altri sono neutri.

| parametro | effetto sul tempo | nota |
|---|---|---|
| `routing_strategy` | **ENORME** | naive/naive_critical = baseline più veloce; congestion ~2.2–2.6×; **packing/critical_packing ~12–18× nella media**, con coda che va in **timeout** |
| `border` | **nullo** | mediana piatta a ogni border (solo `border=0` ha media più alta per i routing falliti che ritentano) |
| `gaussian` (coarse/fine) | **nullo** | ~1.0× identico |
| `safe_passage` | trascurabile | nella zona inerte (baseline border15/naive); passage_no_subgraphs forse lievemente più veloce ma baseline minuscolo |

**Costo di packing per taglia** (media `duration_seconds`, s):

| routing | q1 | q2 | q3 | q4 (grandi) | max | run >60s |
|---|---|---|---|---|---|---|
| naive | 0.44 | 0.27 | 0.62 | **2.31** | 30s | 0 |
| naive_critical | 0.44 | 0.28 | 0.64 | 2.53 | 32s | 0 |
| congestion | 0.96 | 0.59 | 1.33 | 6.02 | 79s | 26 |
| **packing** | 7.48 | 3.88 | 7.33 | **40.83** | **594s** | **610** |
| **critical_packing** | 7.51 | 3.88 | 7.28 | **40.31** | **599s** | **609** |

⚠ **Trade-off reale di packing:** sui circuiti grandi (q4) paghi **~17× il tempo (40s vs 2.3s) per un guadagno di ~4% sui routing_steps** (360 vs 374), e rischi il timeout (610 run >60s, max ~600s = timeout). packing/critical_packing sono ~13.5k run con coda pesante: la mediana è vicina a naive (i circuiti piccoli sono tutti rapidi) ma la **media è 12–18× più alta** per i grandi. → **per produzione, `naive` è la scelta robusta** (veloce, mai timeout, miglior non_routed); usa packing **solo** se routing_steps è l'unico obiettivo e i circuiti restano piccoli/medi.

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
| **magic_low ↔ magic_high** (solo `fine`) | **nessuna** | — | testato: effetto nullo (ml≈0.3 dà ≤0.1pp, dentro il rumore; ml≥0.6 peggiora). Vincolo codice `magic_high ≥ magic_low` → `mh=0, ml>0` non testabile. | `magic_low_tune` |

### B. Pesi ↔ dimensione (taglia griglia / padding)

| peso | dipendenza dalla taglia | nota |
|---|---|---|
| **mapped** | **FORTE, concorde** | assorbe quasi tutto lo scaling (piccole ~0–1 → grandi ~10–25). |
| **sigma** | media (cube) / cala (noncube) | griglie **strettissime → σ più largo** (fino ~3); è l'altra metà dello scaling nel cube. |
| **cnot / magic / external / base / border / cnot_low** | **assente** | costanti rispetto alla taglia (border plateau 15–20 ovunque). |

Anche le **strategie** dipendono dalla taglia (dati noncube):

| strategia | dipende dalla dimensione? | nota |
|---|---|---|
| `routing_strategy` | **sì** | packing batte naive solo su griglie grandi (q4); su piccole/medie pari o naive meglio. |
| `gaussian_strategy` (coarse/fine) | **sì** | vantaggio di fine concentrato sulle griglie piccole; pareggio sulle grandi. |
| `safe_passage_strategy` | **no** | inerte a tutte le dimensioni. |

> La **dimensione è la leva dominante in assoluto**: `non_routed` cala **~8–9pp noncube / ~2–3pp
> cube** da griglia stretta a larga, contro **≤1.4pp** di tutti i pesi messi insieme. → dimensiona
> generosamente la griglia (`dimension_offset 6–12`, regime large-grid) e **non** ri-tarare i pesi
> per taglia: lì mapped≈15–20 e σ≈0.7 valgono sempre. Sulla griglia nativa piccola senza offset
> l'ottimo di mapped crollerebbe verso 0–5.

### C. Pesi ↔ geometria / regime

| relazione | effetto | nota |
|---|---|---|
| **magic_high ↔ geometria** | sì | noncube/connectivity: alzarlo **danneggia forte** (−0.7pp, vero segnale); cube: lieve (−0.24pp); **`fine/cube`** **inerte su non_routed** (0→3 indistinguibili, ±0.06pp ≪ rumore 0.7pp; il "~1" del tbear era artefatto) ma **riduce routing_steps di ~0.3–0.5%** (win 24–29 vs loss 10–14, Δ% negativo su tutti 8 i valori testati). Le due metriche divergono: magic_high avvicina qubit T → percorsi corti (steps), ma non riduce congestione CNOT (non_routed). → fissa 0 se ottimizzi non_routed; usa 0.25–1 se ottimizzi steps. |
| **magic_high ↔ border** | **nessuna** (smentita) | `magic*=0` a **ogni** border. La vecchia "border largo→magic alto" era artefatto `mapped>0`/heap rotto. |
| **border ↔ pesi/dimensione** | trascurabile | ottimo **10–15** stabile ovunque; `border=0` catastrofico (+2–3pp), ≥25 peggiora. |
| **mapped ↔ geometria** | sì | **cube → mapped basso/0** (vuole repulsione minima); **noncube → conca interna ~15–20**. |

### D. Gerarchia delle leve (dalla più forte alla più debole)
1. **dimensione** (≫ tutto, ~8pp noncube) →
2. **posizione sulla cresta mapped↔cnot** (mapped 5–20, cnot=mapped/2.5) →
3. **external** (negativo, satura subito; ~1.5pp noncube) →
4. **border** (ottimo 10–15; 0 catastrofico) →
5. **sigma** (~0.7 costante sulla cresta; largo solo su griglie strette) →
6. **magic_high / magic_low / cnot_low** (inerti → fissa 0; in fine/cube magic_high è proprio indistinguibile, non "≈1").

**Regola pratica unica:** σ=0.7, `cnot=mapped/2.5` con mapped 15–20, external −5, border 10–15,
magic 0/0, cnot_low 0, base 1 — e **dimensiona la griglia con largo padding** (la vera leva).

---

# Tabelle riassuntive (solo valori)

| parametro | Connectivity | Cube |
|---|---|---|
| `type` | gaussian | gaussian |
| `external_weight` | −15 | −15 |
| `base_gaussian_weight` | 1 | 1 |
| `bfs_density_threshold` | 0.70 | 0.70 |
| `cnot_low` | 0 | 0 |
| `magic_low` | 0 | 0 |
| `number_of_magic_states` | −1 | −1 |
| magic placement | center_circle | center_circle |
| `routing_strategy` | packing | packing |
| t-routing | smart_t_routing | smart_t_routing |
| `gaussian_strategy` | fine | fine |
| `safe_passage_strategy` | connectivity | cube |
| `border_distance_percentage` | 15 | 5 |
| `sigma` | 0.7 | 0.7 |
| `mapped` | 20 | 15 |
| `cnot_high` | 8 | 6 |
| `magic_high` | 0 | 0.7 |
| `use_layer_cache` | true | true |
| `patience_threshold` | 3 | 3 |
