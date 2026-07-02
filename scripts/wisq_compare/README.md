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
`compare_random.pbs`→`GRID_FROM`, `gridrun_gaussian__wisq_dimension.pbs`→`WISQ_WORKERS`) **non**
sono esposti qui: per variarli usa `qsub -v` diretto (i default nel pbs bastano se non li cambi).

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
| `gridrun_gaussian__wisq_dimension.py` | griglia minima **di WISQ**, noi ci adattiamo | WISQ | **ricerca** (scan `s` in su fino a successo WISQ) | `gridrun_gaussian__wisq_dimension.pbs` | `_wisqmin.csv` |
| `compare_wisq_conn.py` | vinciamo su una griglia **più stretta** di WISQ? | `WISQ_native − SHRINK` | **ricerca** (footprint; colonne `dim_diff_side`, `grow_steps`) | `compare_wisq_conn.pbs` | `_wisqconn.csv` |
| `compare_random.py` | baseline **random/cube** vs WISQ (sub-comandi `run`/`report`) | WISQ native | — (legge la griglia dal baseline WISQ) | `compare_random.pbs` | `_ours.csv` |

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

### Rinominati / fusi (per non ricascarci)
- `compare_wisq_2.py`        → `compare_wisq_parity.py`  (il motore/baseline a parità)
- `compare_wisq_mingrid.py`  → `gridrun_minimum_our_dimension.py`
- `compare_wisq_minsearch.py` → `gridrun_gaussian__wisq_dimension.py`
- `compare_offset.py`        → **assorbito** in `compare_wisq_parity.py` (`--offsets` / `--offset-report`)

## Post-processing
- `extract_wisq.py` — consolida uno o più CSV di confronto in un "best-WISQ-per-circuito".
- `make_wisq_report.py` — generatore **unico** dei `.md` di confronto (riproduce i vecchi
  report fatti a mano).

## Runner locale (senza cluster)
`run_wisq.py` è il confronto singolo/all-circuits pilotato dai target `make`:
- `run-wisq.sh`  → `make run-wisq QASM="<name> …" [OUTPUT=<csv>] [MR_TIMEOUT=<s>]`
- `run-wisq-all.sh` → `make run-wisq-all [OUTPUT=<csv>] [MR_TIMEOUT=<s>] [WORKERS=<n>]`
