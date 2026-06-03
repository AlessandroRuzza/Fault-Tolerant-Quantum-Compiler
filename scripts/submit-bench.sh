#!/usr/bin/env bash
#
# Submit one PBS job per processor so a benchmark is split across NPROC
# processes that all share the same config/ and benchmarks/results/. Each job
# runs a SINGLE process (run_ftqc.pbs) with BENCH_JOBS OpenMP threads and
# requests that many cores, so it fits the per-job queue limit; PBS schedules
# the jobs independently (possibly on different nodes).
#
# Process K runs only the cases whose process index == K, where the index is
# `expansion_position % NPROC`. The runs CSV is shared and its writes are
# flock-serialized, so concurrent appends/purges across the jobs are safe as
# long as benchmarks/results/ lives on a filesystem that honours flock (local /
# bind-mounted storage, or NFSv4 / Lustre mounted with locking).
#
# Usage:
#   scripts/submit-bench.sh <BENCH_PATH> <BENCH_JOBS> [NPROC=1]
#
# Run it from the repo root (same place you'd run qsub run_ftqc.pbs from), so
# the job's PBS_O_WORKDIR is the repo and the shared paths resolve.
#
# Env overrides:
#   PBS_SCRIPT   path to the PBS job script   (default: run_ftqc.pbs)
#   WALLTIME     wall-clock limit per job     (default: 48:00:00)
set -eu

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Uso: submit-bench.sh <BENCH_PATH> <BENCH_JOBS> [NPROC=1]" >&2
    exit 1
fi

BENCH_PATH="$1"
BENCH_JOBS="$2"
NPROC="${3:-1}"

PBS_SCRIPT="${PBS_SCRIPT:-run_ftqc.pbs}"
WALLTIME="${WALLTIME:-48:00:00}"

case "$NPROC" in
    ''|*[!0-9]*) echo "NPROC must be a positive integer, got '$NPROC'" >&2; exit 1 ;;
esac
[ "$NPROC" -ge 1 ] || { echo "NPROC must be >= 1" >&2; exit 1; }

echo "Submitting $NPROC job(s) for '$BENCH_PATH' (BENCH_JOBS=$BENCH_JOBS cores each, BENCH_PROCESS_COUNT=$NPROC)"

i=0
while [ "$i" -lt "$NPROC" ]; do
    qsub -l select=1:ncpus="$BENCH_JOBS" -l walltime="$WALLTIME" \
         -v BENCH_PATH="$BENCH_PATH",BENCH_JOBS="$BENCH_JOBS",BENCH_PROCESS_COUNT="$NPROC",PROCESSOR="$i" \
         "$PBS_SCRIPT"
    i=$((i + 1))
done
