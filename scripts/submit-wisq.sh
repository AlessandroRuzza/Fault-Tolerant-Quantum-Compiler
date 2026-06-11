#!/usr/bin/env bash
#
# Submit one PBS job per processor for a compare_wisq_2.py benchmark sweep.
# Works exactly like submit-bench.sh but targets run_wisq.pbs.
#
# Usage:
#   scripts/submit-wisq.sh <BENCH_PATH> <BENCH_JOBS> [NPROC=1]
#
# Example:
#   scripts/submit-wisq.sh qaoa_best_gaussian 28 4
#     → submits 4 jobs, each using 28 threads, sharing one output CSV
#
# Env overrides:
#   PBS_SCRIPT   path to the PBS job script   (default: run_wisq.pbs)
#   WALLTIME     wall-clock limit per job     (default: 48:00:00)
#   MEM          memory reserved per job      (default: 64gb)
set -eu

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Uso: submit-wisq.sh <BENCH_PATH> <BENCH_JOBS> [NPROC=1]" >&2
    exit 1
fi

BENCH_PATH="$1"
BENCH_JOBS="$2"
NPROC="${3:-1}"

PBS_SCRIPT="${PBS_SCRIPT:-run_wisq.pbs}"
WALLTIME="${WALLTIME:-48:00:00}"
MEM="${MEM:-64gb}"

case "$NPROC" in
    ''|*[!0-9]*) echo "NPROC must be a positive integer, got '$NPROC'" >&2; exit 1 ;;
esac
[ "$NPROC" -ge 1 ] || { echo "NPROC must be >= 1" >&2; exit 1; }

echo "Submitting $NPROC wisq job(s) for '$BENCH_PATH' (BENCH_JOBS=$BENCH_JOBS cores + $MEM each, BENCH_PROCESS_COUNT=$NPROC)"

i=0
while [ "$i" -lt "$NPROC" ]; do
    qsub -l select=1:ncpus="$BENCH_JOBS":mem="$MEM" -l walltime="$WALLTIME" \
         -v BENCH_PATH="$BENCH_PATH",BENCH_JOBS="$BENCH_JOBS",BENCH_PROCESS_COUNT="$NPROC",PROCESSOR="$i" \
         "$PBS_SCRIPT"
    i=$((i + 1))
done
