# wisq_compare — mappa unica


## Sottomissione sul cluster (PBS)

**Ogni pbs ha lo stesso nome del suo python** (es. `compare_wisq_parity.py` → `pbs/compare_wisq_parity.pbs`).

`compare-wisq.sh` sottomette un job per shard. **Tutto esplicito sulla riga di comando —
niente viene letto dall'ambiente** (un `export` dimenticato non può più cambiare il run).
**La flag di dimensione è OBBLIGATORIA**: scegli esattamente una tra `--our-dimension` e
`--wisq-native`, altrimenti non viene sottomesso niente.

```sh
# forma: compare-wisq.sh <--our-dimension|--wisq-native> [--offset N] [opzioni] <PBS_SCRIPT> <BENCH_PATH> <BENCH_JOBS>
scripts/wisq_compare/compare-wisq.sh --our-dimension compare_wisq_parity.pbs <bench> 28 --nproc 4 --mr-timeout 600
scripts/wisq_compare/compare-wisq.sh --wisq-native   compare_wisq_parity.pbs <bench> 28
scripts/wisq_compare/compare-wisq.sh --wisq-native --offset 4 compare_wisq_parity.pbs <bench> 28
scripts/wisq_compare/compare-wisq.sh --our-dimension gridrun_minimum_our_dimension.pbs <bench> 28 --nproc 4
```
- `--our-dimension` → `MODE=parity` (nostra griglia auto, WISQ ci si specchia)
- `--wisq-native` → `MODE=native` (WISQ costruisce la sua griglia, noi ci adeguiamo)
- `--offset N` (opzionale) → **in più** alla dimensione: sweep su `native+N` con parity arch,
  output `<bench>_runs.csv`. N è un **singolo intero** (`-v` di PBS non regge le liste con virgole);
  l'offset è misurato dalla **nativa di WISQ**, quindi si abbina naturalmente a `--wisq-native`.
- altre opzioni: `--nproc N` (shard), `--mr-timeout S`, `--walltime T`, `--mem M`

`MODE`/`OFFSETS` sono letti **solo** da `compare_wisq_parity.pbs`; gli altri pbs hanno la
dimensione intrinseca e li ignorano (passa la flag "giusta" solo per chiarezza).

Parametri specifici degli altri pbs (`compare_wisq_conn.pbs`→`SHRINK`,
`compare_random.pbs`→`GRID_FROM`, `gridrun_minimum_wisq_dimension.pbs`→`WISQ_WORKERS`) **non**
sono esposti qui: per variarli usa `qsub -v` diretto (i default nel pbs bastano se non li cambi).

### Deploy: gli script python stanno nell'immagine
I pbs **non montano più** gli script locali (`--bind $PWD/scripts` rimossi). Sul cluster
bastano quindi `compare-wisq.sh` + `pbs/`; i `.py` vengono da **`ftqc.sif`**, e `config/`/`qasms/`
sono seminati dall'immagine (`cp -an`). **⚠ Devi RICOSTRUIRE l'immagine ogni volta che modifichi
uno script python**, altrimenti i job girano la versione vecchia baked. (Non re-aggiungere i bind
`$PWD/scripts` se non vuoi tornare alla modalità "script locali").

---



Tutti gli script qui fanno **una sola cosa**: confrontano il nostro compiler con **WISQ**
sugli stessi circuiti. Quello che cambia tra uno script e l'altro sono **due assi**:

1. **Chi fissa la dimensione della griglia** — la nostra o quella di WISQ.
2. **Come si sceglie la griglia** — con una **formula** fissa, oppure con una **ricerca**
   del minimo su cui il compiler ci riesce davvero.

Se tieni a mente questi due assi, non serve altro: la tabella sotto è la traduzione di
ogni file in "quale domanda risponde".

## Entrypoint di confronto

| script | domanda a cui risponde | chi fissa la griglia | come sceglie il lato | pbs | CSV `<bench>_…` |
|---|---|---|---|---|---|
| `compare_wisq_parity.py` | baseline a **parità** (+ `--wisq-native`, + **`--offsets`**) | nostra auto / WISQ native / `native+offset` | formula | `compare_wisq_parity.pbs` (`MODE=parity\|native\|offset`) | `_wisq.csv` / `_runs.csv` |
| `gridrun_minimum_our_dimension.py` | qual è la **nostra** griglia minima, WISQ ci segue | nostra | **ricerca** (parti dal min, cresci +1 fino a successo) | `gridrun_minimum_our_dimension.pbs` | `_wisq3.csv` |
| `gridrun_minimum_wisq_dimension.py` | griglia minima **di WISQ**, noi ci adattiamo | WISQ | **ricerca** (scan `s` in su fino a successo WISQ) | `gridrun_minimum_wisq_dimension.pbs` | `_wisqmin.csv` |
| `compare_wisq_conn.py` | vinciamo su una griglia **più stretta** di WISQ? | `WISQ_native − SHRINK` | **ricerca** (footprint; colonne `dim_diff_side`, `grow_steps`) | `compare_wisq_conn.pbs` | `_wisqconn.csv` |
| `compare_random.py` | baseline **random/cube** vs WISQ (sub-comandi `run`/`report`) | WISQ native | — (legge la griglia dal baseline WISQ) | `compare_random.pbs` | `_ours.csv` |
| `gridrun_dimension_sweep.py` | come rispondono i **nostri** step al crescere della griglia (**niente WISQ**) | config (`x`,`y` per circuito) | — (legge la griglia dalla config, poi `+1` per lato × `--dimensions`) | `gridrun_dimension_sweep.pbs` | `_dims.csv` |

Gli script `gridrun_*`, `conn`, `random` **riusano** `compare_wisq_parity.py` come
libreria (`import compare_wisq_parity as cw2`: runner WISQ, builder d'arch, lettore .graph,
schema CSV). Non sono copie: `compare_wisq_parity.py` è il motore, gli altri sono varianti di
dimensionamento.

### Modalità offset (ex `compare_offset.py`, ora dentro il motore)
Lo sweep di offset è una **modalità di `compare_wisq_parity.py`**, non più uno script a parte.
Entrambi i compiler sono forzati su `side = wisq_native_side(n) + offset` (parità simmetrica,
`offset ≥ 0`); WISQ gira su un arch di parità a quel lato. Uso:
```sh
# run: una riga per (circuito, offset)
compare_wisq_parity.py --offsets 0,2,4,6,8 --bench config/<sweep>.json -o <out>_runs.csv --workers 28
# report: aggrega per offset (WIN/LOSS/TIE, geomean/median)
compare_wisq_parity.py --offset-report <out>_runs.csv --out-dir results/
```

### Sweep di dimensione dalla griglia minima (`gridrun_dimension_sweep.py`)
L'unico script qui che **non** chiama WISQ: misura solo come cambiano i nostri
`routing_steps` al variare del lato. È anche l'unico che prende la griglia **verbatim dalla
config** (`x`,`y` per circuito): il motore offset di `compare_wisq_parity.py` NON può farlo
— `_offset_base_dims` ricava la base a runtime (nostra auto / native WISQ) e ignora `x`,`y`,
e rifiuta gli offset negativi, quindi non sa partire *sotto* la nostra auto.
Metti in config la **minima** presa da un CSV che l'ha registrata (es.
`benchmarks/results/our_mingrid_from_wisq3.csv`, minime di connectivity) — **non ricalcolarla**
da un conteggio di qubit. Ogni passo cresce di `+1` per lato, quindi l'aspect ratio di partenza
è preservato (`12x13 → 13x14 → …`).

> **⚠ Il compilatore TRASPONE gli assi**: `x=8,y=9` in config → `resolved graph dimensions: 9x8`.
> Tutti i CSV registrano `my_x`/`my_y` parsati da `resolved …`, cioè le **risolte**: ridarle
> come `x`,`y` esegue la griglia **specchiata**. Su griglia quadrata è innocuo, su rettangolare
> no — `bwt_n37` mappa a `9x8` richiesto e va in `SafePassageException` a `8x9`, e gli step
> cambiano (33686 vs 33852). **Per riprodurre una griglia letta da un CSV: `x=my_y, y=my_x`.**
> Il CSV di questo script registra entrambe: `req_x`/`req_y` (richiesta, chiave di resume) e
> `my_x`/`my_y` (risolta, confrontabile con gli altri CSV). Un fallimento non ferma lo sweep: la riga è registrata con
`status=failed` e si prosegue (in fondo al range i fallimenti sono attesi).
```sh
qsub -v BENCH_PATH=dim_sweep_family_median_min,BENCH_JOBS=28 pbs/gridrun_dimension_sweep.pbs
# DIMENSIONS=30 di default; il resume è per (circuito, config, griglia) — my_x/my_y sono nel CSV
```

### Rinominati / fusi (per non ricascarci)
- `compare_wisq_2.py`        → `compare_wisq_parity.py`  (il motore/baseline a parità)
- `compare_wisq_mingrid.py`  → `gridrun_minimum_our_dimension.py`
- `compare_wisq_minsearch.py` → `gridrun_minimum_wisq_dimension.py`
- `compare_offset.py`        → **assorbito** in `compare_wisq_parity.py` (`--offsets` / `--offset-report`)

## Post-processing
- `extract_wisq.py` — consolida uno o più CSV di confronto in un "best-WISQ-per-circuito".
- `make_wisq_report.py` — generatore **unico** dei `.md` di confronto (riproduce i vecchi
  report fatti a mano).

## Runner locale (senza cluster)
`run_wisq.py` è il confronto singolo/all-circuits pilotato dai target `make`:
- `run-wisq.sh`  → `make run-wisq QASM="<name> …" [OUTPUT=<csv>] [MR_TIMEOUT=<s>]`
- `run-wisq-all.sh` → `make run-wisq-all [OUTPUT=<csv>] [MR_TIMEOUT=<s>] [WORKERS=<n>]`
