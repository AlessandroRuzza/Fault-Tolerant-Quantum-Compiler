# Percorso di tuning dei pesi gaussiani — da `confidence` a `sigma`

Report del lavoro svolto: passaggio dal parametro `gaussian_confidence` al parametro
diretto `GAUSSIAN_SIGMA`, indagine sul perché i pesi ottimi erano cambiati, e
caratterizzazione completa delle correlazioni tra i pesi (mapped, cnot, sigma),
con la dimensione e il border. Metrica di ottimizzazione: **`non_routed_layer_pct`**
(più basso = meglio), aggregata come *best-per-circuito* (min sugli assi nuisance,
es. dimensione) poi *media sui circuiti*.

> Riepilogo operativo dei pesi → [pesi_tunati.md](pesi_tunati.md). Questo file è il
> *diario* di come ci siamo arrivati.

## Sintesi degli sweep

| # | Sweep | Run | Assi variati | Scopo | Risultato chiave |
|---|---|---|---|---|---|
| 2 | `sigma_sweep` | ~150 | sigma | ottimo σ vs floor confidence | σ≈0.4–0.45 (−0.92pp); <0.25 degenera |
| 3 | `sigma_regime_sweep` | 46 080 | σ×dim×mapped×cnot, 4 regimi | primo multi-regime | σ regime-dipendente |
| 5 | `revalidation_sweep` | 503 445 | cnot×mapped×magic (confidence) | re-tune binario fixato | outlier 16/30/15 respinti |
| 6 | `sigma_weights_sweep` | 846 720 | σ{.6,.7}×cnot×mapped×magic×dim | pesi sotto sigma | mapped/cnot alti; mapped scala con dim |
| 7 | `sigma_dim_sweep` | 275 616 | σ×dim×mapped×cnot×border | dimensione + border | σ dipende da taglia (cube); border 10–20 |
| 9 | `mapped_sigma_sweep` | 37 120 | mapped×σ (cnot fisso) | fit legge σ(mapped) | **legge √ respinta** |
| 10 | `ridge_sigma_sweep` | 27 840 | (mapped, cnot=mapped/2.5)×σ | σ lungo la cresta | **σ≈0.7 costante** |
| 12 | `optimum_sweep` | 1 140 480 | intorno completo, 48 circ | validazione finale | da lanciare |

(Totale eseguito ≈ **1.74 M** run; `optimum_sweep` ancora da lanciare. Figure in `figures/`.)

---

## 0. Punto di partenza e motivazione

`gaussian_confidence` alimentava **solo** `compute_sigma`:

```
sigma = radius / sqrt(-2 · ln(1 - confidence)),   radius = maxX/2 (semi-lato griglia)
```

Il tuning precedente mostrava che il metric migliora **monotonicamente** con
`confidence → 1` (cioè `sigma → 0`), ma confidence **satura** al più grande double < 1
(`0.9999999999999999`, con `1−c ≈ 1.1e-16`), che floora sigma a **`0.117 · radius`**.
Quindi l'ottimo "vero" (sigma più piccolo) era **irraggiungibile** per limite di
rappresentazione, e per griglie grandi il floor era grossolano (sigma ∝ raggio).

**Decisione:** esporre `sigma` direttamente (assoluto, in celle), bypassando il floor.

---

## 1. Modifica del codice: `confidence` → `GAUSSIAN_SIGMA`

- Nuovo parametro `GAUSSIAN_SIGMA` (JSON / CLI `--gaussian-sigma`), usato verbatim come
  `sigma_x = sigma_y` per ogni gaussiana: **assoluto, isotropo, indipendente dalla griglia**.
- Su richiesta, `gaussian_confidence` è stato **rimosso del tutto** (non retrocompatibile):
  `compute_sigma` eliminata, `--gaussian-confidence` → "Unknown option", default sigma 0.4 →
  poi 0.7 quando il modello si è chiarito.
- CSV: colonna 16 **rinominata** `gaussian_confidence`→`gaussian_sigma` in-place (header V17 +
  migrazione che azzera i vecchi valori confidence, testata, non corrompe i file).
- File toccati: `gaussians.hpp`, `gaussian_mapping.cpp`, `mapping.hpp`, `one_execution.hpp`,
  `main.cpp`, `parsing.{hpp,cpp}`, `write_csv.hpp`, `0_compiler_config.json`.

---

## 2. Sweep `sigma_sweep` — trovare il sigma ottimo vs il floor di confidence

**Perché:** confermare che esiste un ottimo di sigma sotto il floor e quantificarlo.
**Config:** 9 circuiti density-spanning, regime coarse/connectivity, pesi di default,
sigma su griglia + il caso `−1` = baseline confidence al floor.
**Risultati:**
- Optimum **sigma ≈ 0.4–0.45** (media non_routed 7.20 vs floor 8.12, **−0.92pp**; fino a
  **−3pp** su qaoa/qft densi).
- **sigma ≲ 0.25 degenera**: la gaussiana collassa sulla cella centrale (delta) → risultati
  identici tra loro e pessimi; a ≤0.2 `randomcircuit_n50` dà `safe_passage_failed` (fallimento
  pulito, non bug).
- Il floor di confidence per quelle griglie = 0.52–1.11 → **0.4 è sotto il floor ovunque**
  (irraggiungibile prima). Il guadagno cresce con la taglia della griglia.

![Fig.1 — ottimo di sigma](figures/fig1_sigma_optimum.png)

*Fig.1 — `non_routed` vs `sigma`: minimo a σ≈0.45, banda grigia = degenerazione (σ≲0.25),
banda arancio = sigma raggiungibili da confidence (il floor 0.52–1.11): l'ottimo sta sotto.*

---

## 3. Sweep `sigma_regime_sweep` — i 4 regimi

**Perché:** il tuning è strutturato in 4 regimi `gaussian_strategy {coarse,fine} ×
geometria {cube,noncube}` (cube → safe_passage `cube`, noncube → `connectivity`).
**Config:** file unico con array di 4 blocchi, **46 080 run**; sigma 0.2–2.0 × dim × mapped ×
cnot, magic fisso.
**Risultati:** ottimo di sigma regime-dipendente e rumoroso (cube tende a sigma più largo,
noncube più stretto). Prime avvisaglie che sigma, pesi e dimensione interagiscono.

---

## 4. Indagine: perché i pesi ottimi erano cambiati? (finetune vs revalidation)

**Domanda dell'utente:** nel finetune emergevano pesi estremi (heap `magic_high=30`,
`cnot=16`; noncube `mapped=15`) — tutti al **bordo griglia**. Perché?

**Metodo:** confronto **finetune** (binario PRE-fix) vs **revalidation** (binario HEAD,
commit `8d18733`: A* routing + `rebuildHeap` per-ripetizione + soglia BFS 0.40→0.70),
isolando gli **stessi circuiti densi** (qaoa/qft/random).

**Risultati:**
- Finetune: i densi in regime **heap** railano `magic_high→30`, `cnot→16`.
- Revalidation: gli estremi **spariscono o si invertono** (16/30 ora peggiorano) e il
  livello migliora (coarse/noncube densi 15.6 → 10.5; fine/cube 11.4 → 9.7).

**Causa (3 modifiche accoppiate):**
1. **bug `rebuildHeap`**: la priority-heap che ordina il mapping in regime heap veniva
   consumata e **non ricostruita per ripetizione** → ordine rotto sui densi; i pesi estremi
   compensavano l'ordine rotto distorcendo lo score. Fixata → non servono più → estremi
   tornano dannosi. (Colpisce SOLO heap.)
2. **soglia 0.40→0.70**: qaoa/qft passano heap→BFS (ordine robusto) → la popolazione che
   chiedeva estremi si riduce.
3. **routing A***: meno bisogno di repulsione estrema (`mapped`) per evitare congestione.

**Conclusione:** gli estremi del finetune erano **artefatti** del binario rotto; ogni tuning
pre-`8d18733` (incluso il vecchio [pesi_tunati.md](pesi_tunati.md)) **sovrastima** la
sensibilità ai pesi.

![Fig.5 — finetune vs revalidation](figures/fig5_finetune_vs_reval.png)

*Fig.5 — circuiti densi, fine/cube: sul binario PRE-fix (rosso) `magic_high` alto migliora
(railava a 30); sul binario fixato (blu) è piatto/peggiora e il livello crolla (11→8).
Gli estremi erano compensazione dell'heap rotto, non veri ottimi.*

---

## 5. Analisi `revalidation` (binario confidence, heap fixato)

**Config esistente:** 503k run, 48 circuiti, `cnot × mapped × magic` per regime.
**Risultati:** outlier respinti; segnali veri = noncube `mapped ≥ 2` + `magic 0.2–0.4`;
**cube quasi insensibile ai pesi** (~3.75); cnot plateau sopra ~1.5. Conferma il punto 4.

---

## 6. Sweep `sigma_weights_sweep` — ri-tarare i pesi SOTTO sigma

**Perché:** ri-tarare i pesi sul binario nuovo con sigma pinnato nella banda sana (0.6/0.7).
**Config:** **846 720 run** (deduplicato a 812 049): sigma {0.6,0.7}, cnot_high
[0,1,2,3,5,10,45], mapped [0,0.5,1,2,3,5,10,25], magic_high [0,0.2,0.4,1,3,15,40],
magic_low {0,1} nei fine, dim 7, border 10, 30 circuiti.
**Risultati (best combo per regime):**

| regime | sigma | cnot | mapped | magic | non_routed |
|---|---|---|---|---|---|
| coarse/noncube | 0.6 | 10 | 25 | 0.2 | 4.62 |
| coarse/cube | 0.7 | 10 | 10 | 0 | 3.81 |
| fine/noncube | 0.7 | 10 | 25 | 0.4 | 4.41 |
| fine/cube | 0.7 | 3 | 10 | 15 | 3.45 |

- `mapped` e `cnot` railano **alti** (mapped 10–25, cnot ~10) — molto più dell'era confidence
  (mapped 2–5). Outlier `cnot=45`/`magic≥15` confermati cattivi.
- **`mapped` scala con la dimensione** (cramped → ~0, roomy → 10–25).

---

## 7. Sweep `sigma_dim_sweep` — dimensione e border

**Perché:** isolare la dipendenza dalla dimensione e testare il border.
**Config:** **275 616 run**: sigma 0.3–4 (11) × dim 9 × mapped {5,10,20} × cnot (2/regime) ×
border {0,10,20,30}, magic fisso, 29 circuiti.
**Risultati:**
- **sigma × dim**: **cube** forte (cramped σ 0.3–0.4 → roomy ~1; fine/cube picco 2–4 a taglie
  medie), **noncube** mite (~1.3 → ~0.7 sulle grandi). [Correzione di una mia affermazione
  precedente errata ("sigma costante"): sigma DIPENDE dalla taglia, soprattutto nel cube.]
- **border**: `0` è il peggiore; sweet spot **~10–20**; `30` ricala. Vale anche con magic fisso.
- **border ↔ altri pesi**: trascurabile (cnot/sigma/mapped non si spostano col border).

![Fig.6 — mapped vs dimensione](figures/fig6_mapped_vs_dim.png)

*Fig.6 — `mapped` ottimo per bucket di taglia (σ pinned 0.6/0.7): cresce con la griglia
(cramped→0, roomy→10–25) in tutti i regimi. La dimensione la assorbe `mapped`.*

---

## 8. Le correlazioni tra pesi

Misurate con `analyze_mapped_corr.py`, `analyze_weight_vs_dim.py`, ecc.

- **mapped ↔ cnot — FORTE, stessa direzione.** `best mapped` cresce con cnot → **cresta
  `mapped ≈ 2.5 · cnot`** (coppie equivalenti lungo la diagonale; per questo "railavano"
  insieme). È la cresta antagonista (mapped respinge, cnot attrae).
- **mapped ↔ sigma — anti-correlazione apparente** (a cnot fisso: mapped 5→σ2.5, 20→σ0.7).
- **sigma ↔ cnot — debole/assente.**
- **pesi ↔ dimensione**: la assorbe **mapped** (scala con la griglia) e in parte **sigma**
  (nel cube); **cnot/magic/border indipendenti** dalla taglia.

![Fig.2 — cresta mapped↔cnot](figures/fig2_mapped_cnot_ridge.png)

*Fig.2 — heatmap `non_routed` su (mapped, cnot), coarse/noncube: valle diagonale lungo la
**cresta `mapped=2.5·cnot`** (linea rossa). Coppie basso-basso e alto-alto sono equivalenti;
`mapped=0` (riga in basso) è pessimo.*

![Fig.3 — mapped×sigma](figures/fig3_mapped_sigma.png)

*Fig.3 — heatmap `non_routed` su (mapped, sigma), coarse/noncube: ★ = miglior σ per mapped.
A cnot fisso l'ottimo di σ scende all'aumentare di mapped (anti-correlazione apparente —
poi spiegata come artefatto off-cresta, vedi Fig.4).*

---

## 9. Sweep `mapped_sigma_sweep` — fit della legge σ(mapped) → RESPINTA

**Perché:** trovare un'equazione tipo `cnot=mapped/2.5` anche per σ–mapped. Ipotesi fisica:
"massa gaussiana costante" `mapped·σ² = C` ⇒ `σ ∝ 1/√mapped`.
**Config:** **37 120 run**: mapped [0.5..48] × sigma [0.3..3] × dim 4, **cnot fisso 5**,
magic/border fissi, 29 circuiti.
**Risultati — legge RESPINTA:**
- Fit log-log esponente **≈ −0.15 ÷ −0.19** (non −0.5); `C = mapped·σ²` **non è costante**.
- **Confound:** con `cnot=5` fisso, la cresta `mapped≈2.5·cnot` pinna l'ottimo di mapped a
  **~8–16**; oltre peggiora. Quindi σ(mapped) era misurato fuori cresta.

---

## 10. Sweep `ridge_sigma_sweep` — σ LUNGO la cresta → la risposta

**Perché:** misurare σ muovendosi **sulla cresta** (cnot accoppiato a mapped), così il
bilancio attrazione/repulsione resta mantenuto e si vede il vero comportamento di σ.
**Config:** **27 840 run**: coppie `(mapped, cnot=mapped/2.5)` per mapped {1,2.5,5,10,20,40}
(object-list per tenerle accoppiate), sigma 0.3–3, dim 4, magic/border fissi, 29 circuiti.
**Risultati — σ COSTANTE:**
- `σ* ≈ 0.7` (0.7–1.0) a **qualunque** mapped; esponente log-log **≈ 0** → nessuna dipendenza.
- **L'anti-correlazione σ↔mapped era un artefatto off-cresta:** a cnot fisso σ compensava lo
  sbilancio; sulla cresta non deve compensare → resta costante.

![Fig.4 — sigma dentro/fuori la cresta](figures/fig4_sigma_ridge.png)

*Fig.4 — miglior σ vs mapped: **sulla cresta** (verde, cnot=mapped/2.5) σ è costante ≈0.7 a
qualunque mapped; **fuori cresta** (rosso, cnot fisso) σ cala da 2.5 a 0.7. L'anti-correlazione
era compensazione dello sbilancio, non una vera dipendenza σ(mapped).*

---

## 11. Modello finale

```
σ        ≈ 0.7            (costante, ~universale)
cnot     = mapped / 2.5   (cresta antagonista)
mapped   ≈ 5–20           (posizione sulla cresta; cube ~10–20; oltre 40 peggiora)
magic    basso            (coarse 0–0.2; fine debole)
border   ≈ 10
external ≈ −15,  base = 1
```

Miglior non_routed sulla cresta: ~4.2–4.5 noncube, ~3.4–4.0 cube. La dimensione la assorbe
principalmente `mapped` (e in parte σ nel cube); cnot/magic/border non scalano con la taglia.

**Punto operativo per regime** (best combo osservata; `sigma_weights_sweep` per i pesi,
confermata da `ridge_sigma_sweep` per σ):

| regime | σ | cnot | mapped | magic_high | magic_low | border | external | non_routed |
|---|---|---|---|---|---|---|---|---|
| coarse / cube | 0.7 | ~10 (=2.5·mapped) | ~10 | 0 | 0 | 10 | −15 | **3.81** |
| coarse / noncube | 0.7 | ~8 | ~20 | 0.2 | 0 | 10 | −15 | **4.62** |
| fine / cube | 0.7 | ~4 | ~10 | basso (≈1) | 1 | 10 | −15 | **3.45** |
| fine / noncube | 0.7 | ~8 | ~20 | 0.4 | 0 | 10 | −15 | **4.41** |

I `cube` sono strutturalmente migliori dei `noncube` (~3.5 vs ~4.5): la safe-passage `cube`
su griglia quadrata fa gran parte del lavoro, e lì i pesi contano poco. La cresta dà coppie
equivalenti: i valori di mapped/cnot sopra sono *un punto* sulla cresta, non l'unico ottimo.

---

## 12. Validazione finale — `optimum_sweep` (preparato, da lanciare)

**Perché:** validare il punto operativo esplorando un **intorno** delle linee guida, e
spingere mapped in alto (era ottimo ma non certo).
**Config:** **1 140 480 run** (48 circuiti × 4 regimi): sigma 0.40–0.90 (step .05), mapped
10–60, cnot = mapped/2.5 **±4 step 1** (intorno), dim ×10, magic/border/external fissi.
**Stato:** generato, non eseguito (lo lancia l'utente).

---

## Appendice A — Metodo, dati e figure

Gli script Python di generazione config e di analisi erano **usa-e-getta** e sono stati
cancellati dopo l'uso: il valore è in questo documento, nei `.md` e nelle figure. Restano:
- **config** in `data/config/*.json` (i sweep);
- **risultati** dei sweep in `data/results/*_runs.csv`;
- **figure** in `metric_analysis_outcomes/figures/`: `fig1_sigma_optimum`, `fig2_mapped_cnot_ridge`,
  `fig3_mapped_sigma`, `fig4_sigma_ridge`, `fig5_finetune_vs_reval`, `fig6_mapped_vs_dim`.

**Metodologia di analisi** (riproducibile): per ogni combinazione di pesi, **best-per-circuito**
(min sugli assi nuisance: dimensione e gli assi non in esame) poi **media sui circuiti** con
copertura piena. Mai medie pesate sul numero di righe (robuste ai duplicati da resume).
Per le domande su **magic** filtrare ai soli circuiti **T-bearing** (`resolved_n_magic > 0`),
altrimenti il segnale è diluito dai circuiti senza T.

## Appendice B — Note di igiene dei dati

- **Duplicati da resume:** rilanciare/riprendere uno sweep ri-esegue casi già fatti e
  **appende righe duplicate** (valori identici). Innocui per analisi min-based, ma il CSV va
  **deduplicato** (chiave = tutte le colonne tranne id/date/durate/log_file). Es.
  `sigma_weights_sweep` 968k → 812k; `sigma_dim_sweep` ~275k (363 dup).
- **`knn_n25`:** `status=success` ma `non_routed` vuoto (nessun layer routabile) → escluso
  dalle analisi.
- **Metodologia:** sempre *best-per-circuito* (min sugli assi nuisance) poi *media sui
  circuiti*; mai medie pesate sul numero di righe (robuste ai duplicati).
- **Bucket di dimensione grandi** spesso con pochi circuiti (offset estremi collassano o
  falliscono safe_passage) → meno affidabili; fidarsi dei bucket centrali.
