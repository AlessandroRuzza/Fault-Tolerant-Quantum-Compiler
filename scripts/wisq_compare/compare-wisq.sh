#!/usr/bin/env bash
#
# Submit one PBS job per shard for a wisq_compare sweep. Everything is EXPLICIT on the
# command line — nothing is read from the environment, so a stray `export` can never
# silently change a run.
#
# Usage:
#   compare-wisq.sh <--our-dimension|--wisq-native> [--offset N] [options] <PBS_SCRIPT> <BENCH_PATH> <BENCH_JOBS>
#
#   <PBS_SCRIPT>   job file (bare name resolved under pbs/, or a path), e.g.
#                  compare_wisq_parity.pbs, gridrun_minimum_our_dimension.pbs
#   <BENCH_PATH>   config basename -> config/<BENCH_PATH>.json
#   <BENCH_JOBS>   cpus per job (= python --workers)
#
# Dimension (REQUIRED — pick EXACTLY ONE; without it nothing is submitted):
#   --our-dimension  our compiler auto-sizes the grid, WISQ mirrors it   (MODE=parity)
#   --wisq-native    WISQ builds its own native grid, we match its side  (MODE=native)
#
# Options:
#   --offset N       ALSO run an offset sweep: both compilers forced onto
#                    (WISQ native side + N) on a parity arch, one row per (circuit,
#                    offset). N is a single non-negative integer (PBS -v cannot carry a
#                    comma list). With --offset the run writes <bench>_runs.csv.
#   --nproc N        shards / parallel jobs sharing the same CSV (default 1)
#   --mr-timeout S   WISQ mapping/routing timeout in seconds (default 300)
#   --walltime T     wall-clock limit per job (default 48:00:00)
#   --mem M          memory reserved per job (default 64gb)
#   -h, --help       show this header
#
# MODE / OFFSETS are read only by compare_wisq_parity.pbs; the other pbs have their
# dimension baked in and ignore them (pass the matching dimension flag for clarity).
#
# Examples:
#   compare-wisq.sh --our-dimension compare_wisq_parity.pbs qaoa_best 28 --nproc 4
#   compare-wisq.sh --wisq-native   compare_wisq_parity.pbs qaoa_best 28
#   compare-wisq.sh --wisq-native --offset 4 compare_wisq_parity.pbs qaoa_best 28
set -eu

NPROC=1
MR_TIMEOUT=300
WALLTIME=48:00:00
MEM=64gb
MODE=""       # set ONLY by --our-dimension / --wisq-native; required (no default)
OFFSET=""     # optional; single non-negative integer
POS=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        --nproc)         NPROC="$2"; shift 2 ;;
        --mr-timeout)    MR_TIMEOUT="$2"; shift 2 ;;
        --walltime)      WALLTIME="$2"; shift 2 ;;
        --mem)           MEM="$2"; shift 2 ;;
        --offset)        OFFSET="$2"; shift 2 ;;
        --our-dimension)
            if [ -n "$MODE" ]; then echo "conflicting dimension flags (--our-dimension after --$MODE)" >&2; exit 1; fi
            MODE=parity; shift ;;
        --wisq-native)
            if [ -n "$MODE" ]; then echo "conflicting dimension flags (--wisq-native after --$MODE)" >&2; exit 1; fi
            MODE=native; shift ;;
        -h|--help)       grep '^#' "$0" | sed '1d; s/^#\{0,1\} \{0,1\}//'; exit 0 ;;
        --*)             echo "unknown option: $1" >&2; exit 1 ;;
        *)               POS+=("$1"); shift ;;
    esac
done

# Dimension is mandatory: refuse to submit anything without an explicit choice.
if [ -z "$MODE" ]; then
    echo "ERROR: a dimension flag is required — pass --our-dimension OR --wisq-native." >&2
    echo "       (nothing submitted; run with --help)" >&2
    exit 1
fi

if [ -n "$OFFSET" ]; then
    case "$OFFSET" in
        ''|*[!0-9]*) echo "--offset must be a single non-negative integer, got '$OFFSET'" >&2; exit 1 ;;
    esac
fi

if [ "${#POS[@]}" -ne 3 ]; then
    echo "Usage: compare-wisq.sh <--our-dimension|--wisq-native> [--offset N] [opts] <PBS_SCRIPT> <BENCH_PATH> <BENCH_JOBS>" >&2
    echo "       (run with --help for the full option list)" >&2
    exit 1
fi
PBS_SCRIPT="${POS[0]}"
BENCH_PATH="${POS[1]}"
BENCH_JOBS="${POS[2]}"

case "$NPROC" in
    ''|*[!0-9]*) echo "--nproc must be a positive integer, got '$NPROC'" >&2; exit 1 ;;
esac
[ "$NPROC" -ge 1 ] || { echo "--nproc must be >= 1" >&2; exit 1; }

# Resolve the pbs file: accept a bare name under pbs/ or an explicit path.
if [ -f "$PBS_SCRIPT" ]; then
    PBS_FILE="$PBS_SCRIPT"
elif [ -f "pbs/$PBS_SCRIPT" ]; then
    PBS_FILE="pbs/$PBS_SCRIPT"
else
    echo "pbs script not found: '$PBS_SCRIPT' (looked here and under pbs/)" >&2
    exit 1
fi

echo "Submitting $NPROC job(s): $PBS_FILE  bench=$BENCH_PATH jobs=$BENCH_JOBS mode=$MODE offset=${OFFSET:-none} mr_timeout=${MR_TIMEOUT}s walltime=$WALLTIME mem=$MEM"

i=0
while [ "$i" -lt "$NPROC" ]; do
    qsub -l select=1:ncpus="$BENCH_JOBS":mem="$MEM" -l walltime="$WALLTIME" \
         -v BENCH_PATH="$BENCH_PATH",BENCH_JOBS="$BENCH_JOBS",BENCH_PROCESS_COUNT="$NPROC",PROCESSOR="$i",MR_TIMEOUT="$MR_TIMEOUT",MODE="$MODE",OFFSETS="$OFFSET" \
         "$PBS_FILE"
    i=$((i + 1))
done
