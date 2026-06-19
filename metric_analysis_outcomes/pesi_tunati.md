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

## Correlazione sigma ↔ mapped (binario GAUSSIAN_SIGMA, post-confidence)

Sul binario con `GAUSSIAN_SIGMA` (sigma assoluto al posto di confidence), `sigma` e
`mapped` sono in **anti-correlazione netta**: mapped basso vuole sigma largo, mapped
alto vuole sigma stretto. `sigma*` (miglior sigma) per valore di `mapped`, per regime
(sweep `sigma_dim_sweep`, 29 circuiti, best-per-circuito su cnot/border/dim):

| regime | mapped 5 | mapped 10 | mapped 20 |
|---|---|---|---|
| coarse / noncube | σ 2.5 | σ 1.0 | σ 0.7 |
| coarse / cube | σ 1.0 | σ 0.7 | σ 0.7 |
| fine / noncube | σ 1.6 | σ 0.7 | σ 0.7 |
| fine / cube | σ 1.3 | σ 0.7 | σ 0.7 |

**NB (correzione):** quel "mapped alto ≥20 + σ 0.7" vale solo perché in `sigma_dim` mapped
era agganciato a cnot alto. Lo sweep denso `mapped_sigma_sweep` (mapped 0.5→48 × σ 0.3→3,
**cnot fisso a 5**) mostra che:
- l'**ottimo di mapped non ha vita propria**: con cnot=5 il minimo è a **mapped ≈ 8–16**
  (noncube) / basso (cube); oltre (32,48) **peggiora** → lo decide la cresta `mapped≈2.5·cnot`.
- **NON esiste una legge σ(mapped)** tipo `σ=√(C/mapped)`: testata e respinta (fit log-log
  esponente **≈ −0.15÷−0.19**, non −0.5; `C=mapped·σ²` cresce, non è costante).
- `σ` è una **regolazione secondaria debole** (~0.7–1.3 su quasi tutto il range di mapped),
  non legata a mapped da una formula.

Quindi: il knob libero vero è la **posizione sulla cresta mapped↔cnot**; `σ` ~0.7–1.3 a parte.
Vanno comunque tarati insieme (mapped↔cnot stessa direzione; mapped↔σ opposta ma blanda).

#### Conferma: σ SULLA cresta è costante (`ridge_sigma_sweep`)

Misurando σ **lungo la cresta** (cnot=mapped/2.5, mapped 1→40, σ 0.3→3), σ* resta **≈ 0.7**
a ogni mapped (esponente log-log ≈ 0.00÷−0.11 → nessuna dipendenza). L'"anti-correlazione
σ↔mapped" vista prima era un **artefatto off-cresta**: alzando mapped a cnot fisso, σ
compensava lo sbilancio; sulla cresta il bilancio attrazione/repulsione è mantenuto e σ
non si muove.

**Modello finale (binario sigma):**
- `σ ≈ 0.7` (costante, ~universale);
- `cnot = mapped / 2.5` (cresta);
- `mapped ≈ 5–20` (posizione migliore sulla cresta: noncube ~5–20, cube ~10–20; oltre 40 peggiora);
- `magic` basso, `border ≈ 10`, `external ≈ −15`, `base = 1`.

Miglior non_routed sulla cresta: ~4.2–4.5 noncube, ~3.4–4.0 cube.

#### Valori tunati per regime — `sigma`, `mapped`, `cnot_high`

Validati su `optimum_sweep` (48 circ; σ 0.2–4, mapped 10–60, cnot=mapped/2.5 ±4, dim ×10).
Sono **centri di plateau** (l'esatto valore conta poco: i pesi spostano ≤1.4pp, la dimensione
~8pp — vedi sotto):

| regime | sigma | mapped | cnot_high | (magic_high / magic_low) | non_routed best |
|---|---|---|---|---|---|
| coarse / cube    | **0.7** | **15** | **6**  | 0 / 0     | ~2.87 |
| fine / cube      | **0.7** | **15** | **6**  | 0 / 1     | ~2.88 |
| coarse / noncube | **0.7** | **20** | **8**  | 0.2 / 0   | ~3.29 |
| fine / noncube   | **0.7** | **20** | **8**  | 0.4 / 0   | ~3.30 |

Set unico robusto: **σ=0.7, mapped=20, cnot=8** (magic basso, border 10, external −5 = qualsiasi
negativo, satura subito; base 1).
Validazione marginali: σ ottimo 0.65–0.75 (σ=0.2 degenera, σ≥3 troppo diffuso); mapped plateau
10–30 (≥40 nessun guadagno; cube piatto); cnot piatto nella zona ~mapped/2.5.

#### Dipendenza dalla dimensione (taglia griglia / padding)
La **dimensione domina**: `non_routed` cala col padding di **~8–9pp noncube**, **~2–3pp cube**
(da cramped a roomy). I **pesi** invece pesano poco: usare il set globale fisso sopra invece di
ri-tarare i pesi per ogni taglia costa **≤1.4pp** (solo griglie piccole noncube; <0.3pp nel cube,
<0.2pp dalle griglie medie in su). → **non adattare i pesi alla taglia; dimensiona generosamente
la griglia.** Unica eccezione: griglie strettissime vogliono σ più largo (fino a ~3).

#### external, magic, cnot_low (binario sigma, ai pesi tunati)

Da `corr_sweep` (external×magic_high×mapped×cnot_high×sigma) + `external_magic_sweep` (external 15
valori + magic_h×magic_l + cnot_low, ai pesi tunati) + `cnotlow_sweep`:

| param | valore | note |
|---|---|---|
| **external** | **qualsiasi negativo (−1 ÷ −5)** | satura **subito**: ai pesi tunati −1 ≈ −30 (tutti ~uguali); `0` costa **~−1.5pp**. NB: col mapped alto basta pochissimo external (sono ridondanti) — niente più bisogno del vecchio −15 |
| **magic_high** | **0** (fine: 0–1) | inerte/lieve danno; coarse 0; **fine/cube** preferisce ~1 di un soffio |
| **magic_low** | **0** | confermato ovunque (0.5/1 peggiorano ~0.1–0.2pp), anche fine/cube |
| **cnot_low** | **0** | INERTE: 0–2 danno non_routed identico; ≥4 fa male; non avvicinare a cnot_high |

**Correlazioni di external e magic_high** (da `corr_sweep`):
- `external` ↔ `sigma`: **nessuna** (σ*=0.7 a ogni external); ↔ `cnot_high`: **nessuna**; ↔ `mapped`:
  **debole/ridondante** (external e mapped sono entrambi "repulsivi": con external negativo mapped
  alto smette di far male; a external=0 mapped alto peggiora).
- `magic_high` ↔ tutto (`mapped`/`cnot_high`/`sigma`/`external`): **nessuna** — nessun ottimo si
  sposta al variare di magic_high. È un parametro da **fissare basso e ignorare**.
- `cnot_low` ↔ tutto: **nessuna** — disaccoppiato, non sposta gli ottimi degli altri.

In pratica: **external = −1÷−5** (knob indipendente, satura subito), **magic_high ≈ 0** (fine/cube ~1),
**magic_low = 0**, **cnot_low = 0**. Nessuno di questi richiede co-tuning con sigma/mapped/cnot.

### Correlazione sigma ↔ cnot — DEBOLE

A differenza di mapped, il `sigma` ottimo è quasi **indipendente da cnot**. `best σ` per cnot:

| regime | cnot 0.5 | 1.5 | 3 | 6 | (cnot 5 / 10, run nuova) |
|---|---|---|---|---|---|
| coarse / noncube | 0.5 | 0.7 | 0.5 | *(2)* | 0.7 / 1.3 |
| coarse / cube | 1.5 | 1.5 | 1.5 | 1.5 | 0.7 / 0.7 |
| fine / noncube | 0.7 | 0.7 | 0.6 | *(2)* | 0.7 / 0.7 |
| fine / cube | 0.8 | 0.6 | 0.7 | *(2)* | 0.7 / 0.7 |

\*cnot=6 è degenere (non_routed +5–6pp): il "σ=2" è rumore tra opzioni pessime, non un ottimo.

Nel range sano di cnot il sigma ottimo non si muove (~0.5–0.7 noncube, ~1.5 cube run vecchia /
~0.7 run nuova). Unico accenno: coarse/noncube, cnot 5→10 alza σ 0.7→1.3. **Conclusione: il
sigma lo governa `mapped`, non `cnot`** → si può fissare cnot a un buon valore e co-tarare solo
`mapped × sigma`.

### Correlazione mapped ↔ cnot — FORTE positiva (cresta antagonista)

`best mapped` per cnot (da `sigma_weights`, esclusi cnot 0 e 45 degeneri):

| regime | cnot 1 | 2 | 3 | 5 | 10 |
|---|---|---|---|---|---|
| coarse / noncube | 2 | 5 | 5 | 10 | 25 |
| coarse / cube | 1 | 0.5 | 0.5 | 10 | 10 |
| fine / noncube | 3 | 5 | 10 | 10 | 25 |
| fine / cube | 1 | 10 | 10 | 10 | 25 |

La tabella 2D mapped×cnot ha una **valle diagonale**: il minimo corre lungo mapped e cnot che
crescono **insieme**. Nel noncube il rapporto è **mapped ≈ 2.5·cnot** (cnot 2→mapped 5,
cnot 10→mapped 25, stesso non_routed ~4.3). Quindi non c'è un singolo ottimo ma una **cresta di
coppie equivalenti**: basso-basso (cnot 2 / mapped 5) o alto-alto (cnot 10 / mapped 25) rendono
uguale → ecco perché "railano" insieme.

### Correlazione pesi ↔ dimensione (taglia griglia)

`peso*` per taglia (piccola→grande); mapped/cnot da `sigma_weights`, sigma da `sigma_dim`:

| peso | piccole | medie | grandi | dipendenza |
|---|---|---|---|---|
| **mapped** | 0–1 | 10 | **10–25** | **FORTE** (scala su con la griglia) |
| **sigma** cube | 0.3–0.4 | 0.7–1.3 (fine: picco 2–4) | ~0.7–1 | media-forte |
| **sigma** noncube | ~1.3 | ~1.3 | ~0.7 | media (cala) |
| **cnot** | ~1–5 (piatto) | ~1–5 | ~1–5 | **assente** (cnot 45 sempre male) |
| **magic** | basso | basso | basso | assente |
| **border** | ~10–20 | ~10–20 | ~10–20 (accenno ↑) | trascurabile |

**La dimensione la assorbe il duo anti-correlato `mapped ↔ sigma`:** dove sigma è fisso stretto
(0.6/0.7) lo scaling va tutto su `mapped` (0→25); dove i pesi sono medi, una parte la prende
`sigma` (cube 0.3→1). `cnot`, `magic`, `border` **non dipendono dalla taglia**.

### Riepilogo correlazioni (binario sigma)
- **mapped ↔ cnot**: forte, **stessa direzione** (cresta mapped≈2.5·cnot).
- **mapped ↔ sigma**: forte, **opposta** (mapped alto → sigma stretto ~0.7).
- **sigma ↔ cnot**: debole/assente (sigma lo fissa mapped).
- **pesi ↔ dimensione**: la assorbe **mapped** (e in parte **sigma** nel cube); cnot/magic/border indipendenti.
