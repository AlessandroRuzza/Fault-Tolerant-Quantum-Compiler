#!/usr/bin/env bash
#
# Submit dello sweep BFS-threshold DISCRIMINANTE sul cluster PBS.
# Una soglia = una config (bfs_disc_<tag>) + un valore di FTQC_BFS_DENSITY_THRESHOLD.
# La soglia entra nel container via APPTAINERENV_FTQC_BFS_DENSITY_THRESHOLD:
# apptainer auto-inoltra le env host col prefisso APPTAINERENV_ (e SINGULARITYENV_
# per apptainer/singularity vecchi) DENTRO il container, togliendo il prefisso.
# => NON serve modificare run_ftqc.pbs.
#
# Ogni soglia e' splittata su NPROC processi (come submit-bench.sh): stessa config/
# e benchmarks/results/ condivise, CSV flock-serializzato.
#
# PREREQUISITI sul cluster ($PBS_O_WORKDIR):
#   - ftqc.sif POST-FIX (la pubblicata e' pre-fix; il push lo fai tu)
#   - config/bfs_disc_*.json presenti (commit nel submodule data + pull)
#
# Uso:
#   scripts/submit_bfs_threshold_disc_cluster.sh <BENCH_JOBS> [NPROC=1]
# Env override: WALLTIME (24:00:00), MEM (64gb), PBS_SCRIPT (run_ftqc.pbs)
set -eu

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "Uso: submit_bfs_threshold_disc_cluster.sh <BENCH_JOBS> [NPROC=1]" >&2
    exit 1
fi

BENCH_JOBS="$1"
NPROC="${2:-1}"
PBS_SCRIPT="${PBS_SCRIPT:-run_ftqc.pbs}"
WALLTIME="${WALLTIME:-24:00:00}"
MEM="${MEM:-64gb}"

case "$NPROC" in ''|*[!0-9]*) echo "NPROC intero positivo, ricevuto '$NPROC'" >&2; exit 1 ;; esac
[ "$NPROC" -ge 1 ] || { echo "NPROC >= 1" >&2; exit 1; }

# tag della config  ->  valore soglia. Deve combaciare con gen_bfs_threshold_disc_configs.py
TAGS="heap 040 045 050 055 065 080 090 100"
val_for() {
    case "$1" in
        heap) echo "-1.0" ;;
        040)  echo "0.40" ;;
        045)  echo "0.45" ;;
        050)  echo "0.50" ;;
        055)  echo "0.55" ;;
        065)  echo "0.65" ;;
        080)  echo "0.80" ;;
        090)  echo "0.90" ;;
        100)  echo "1.00" ;;
    esac
}

echo "Submit sweep discriminante: 9 soglie x $NPROC proc (ncpus=$BENCH_JOBS, mem=$MEM, walltime=$WALLTIME)"

for tag in $TAGS; do
    cfg="bfs_disc_${tag}"
    thr="$(val_for "$tag")"
    i=0
    while [ "$i" -lt "$NPROC" ]; do
        qsub -l select=1:ncpus="$BENCH_JOBS":mem="$MEM" -l walltime="$WALLTIME" \
             -v BENCH_PATH="$cfg",BENCH_JOBS="$BENCH_JOBS",BENCH_PROCESS_COUNT="$NPROC",PROCESSOR="$i",APPTAINERENV_FTQC_BFS_DENSITY_THRESHOLD="$thr",SINGULARITYENV_FTQC_BFS_DENSITY_THRESHOLD="$thr" \
             "$PBS_SCRIPT"
        i=$((i + 1))
    done
    echo "  sottomessa soglia $thr ($cfg) x $NPROC"
done

echo "FATTO. Risultati in benchmarks/results/bfs_disc_*_runs.csv (o data/results/ secondo i bind)."
