#!/usr/bin/env bash
# Scaling test: measure benchmark throughput (completed OK cases / minute) at
# several OpenMP thread counts, to see whether asking for N cores actually buys
# proportional throughput.
#
# It runs on a THROWAWAY COPY of the bench config (prefixed "_scaling_") so your
# real *_expanded.json, *.status.jsonl and *_runs.csv are never touched. Before
# each thread-count run it wipes the copy's state so every run starts fresh, then
# runs the binary for a fixed wall-clock budget and counts how many cases reached
# "OK" in that window.
#
# Must run in the SAME environment as a normal benchmark (inside the container /
# on the compute node), where the binary and its compiled config dir live.
#
# Usage:
#   scripts/scaling-test.sh [NAME] [BUDGET_SECONDS] [JOBS...]
# Examples:
#   scripts/scaling-test.sh                                  # defaults below
#   scripts/scaling-test.sh gaussian_weight_tuning_fine_cube 180 4 8 16 28
#
# Env overrides (auto-detected if unset):
#   BINARY      path to FaultTolerantQuantumCompiler
#   CONFIG_DIR  dir containing <name>.json (must be the binary's config dir)
#   RESULTS_DIR dir containing *_runs.csv  (default: <CONFIG_DIR>/../benchmarks/results)
#   LOG_DIR     where per-run logs go      (default: ./scaling_logs)

set -u

NAME="${1:-gaussian_weight_tuning_fine_cube}"
BUDGET="${2:-180}"
shift || true
shift || true
if [ "$#" -gt 0 ]; then
    JOBS="$*"
else
    JOBS="1 4 8 16 28"
fi

# --- locate binary -----------------------------------------------------------
pick_first() { for c in "$@"; do [ -n "$c" ] && [ -e "$c" ] && { printf '%s\n' "$c"; return 0; }; done; return 1; }

BINARY="${BINARY:-$(pick_first /app/build/FaultTolerantQuantumCompiler "$PWD/build/FaultTolerantQuantumCompiler" || true)}"
if [ -z "${BINARY:-}" ] || [ ! -x "$BINARY" ]; then
    echo "ERROR: binary not found/executable. Set BINARY=/path/to/FaultTolerantQuantumCompiler" >&2
    exit 1
fi

# --- locate config dir -------------------------------------------------------
CONFIG_DIR="${CONFIG_DIR:-$(pick_first /app/config "$PWD/config" || true)}"
if [ -z "${CONFIG_DIR:-}" ] || [ ! -f "$CONFIG_DIR/$NAME.json" ]; then
    echo "ERROR: $NAME.json not found under CONFIG_DIR. Set CONFIG_DIR to the binary's config dir." >&2
    exit 1
fi

EXECUTED_DIR="$CONFIG_DIR/executed"
ROOT="$(dirname "$CONFIG_DIR")"
RESULTS_DIR="${RESULTS_DIR:-$ROOT/benchmarks/results}"
LOG_DIR="${LOG_DIR:-$PWD/scaling_logs}"
mkdir -p "$EXECUTED_DIR" "$RESULTS_DIR" "$LOG_DIR"

# Make the throwaway name unique per job (host + pid) so concurrent scaling
# jobs writing to the same shared results dir never collide on the same
# config copy / expanded file / CSV — a collision corrupts the CSV and makes
# the binary abort on a header-mismatch check.
host_tag=$(hostname -s 2>/dev/null | tr -cd 'a-zA-Z0-9'); [ -z "$host_tag" ] && host_tag=h
SCN="_scaling_${NAME}_${host_tag}_$$"
cp -f "$CONFIG_DIR/$NAME.json" "$CONFIG_DIR/$SCN.json"

cleanup() {
    rm -f "$CONFIG_DIR/$SCN.json" \
          "$EXECUTED_DIR/${SCN}_expanded.json" \
          "$EXECUTED_DIR/${SCN}_expanded.status.jsonl" \
          "$RESULTS_DIR/${SCN}_runs.csv"
}
trap cleanup EXIT INT TERM

echo "Scaling test"
echo "  binary : $BINARY"
echo "  config : $CONFIG_DIR/$NAME.json  (copy: $SCN.json)"
echo "  budget : ${BUDGET}s per thread count"
echo "  jobs   : $JOBS"
echo "  logs   : $LOG_DIR"
echo

printf '%-6s %8s %8s %8s %10s %10s %10s\n' "JOBS" "OK" "TIMEOUT" "FAIL" "elapsed_s" "OK/min" "speedup"
printf '%-6s %8s %8s %8s %10s %10s %10s\n' "----" "--" "-------" "----" "---------" "------" "-------"

base_okpm=""
for J in $JOBS; do
    # reset throwaway state so every run starts from a clean sweep
    rm -f "$EXECUTED_DIR/${SCN}_expanded.json" \
          "$EXECUTED_DIR/${SCN}_expanded.status.jsonl" \
          "$RESULTS_DIR/${SCN}_runs.csv"

    log="$LOG_DIR/scaling_${NAME}_j${J}.log"
    start=$(date +%s)

    # Run the bench in its OWN process group (setsid) so we can time-box it and
    # then kill the WHOLE tree (parent + every worker subprocess) by pgid. This
    # prevents orphaned workers from a killed run bleeding CPU into the next run
    # — and it never touches other jobs on the node, which live in other pgids.
    setsid env OMP_NUM_THREADS="$J" "$BINARY" --bench_path "$SCN" --processor 0 \
        > "$log" 2>&1 &
    run_pid=$!
    pgid=$(ps -o pgid= -p "$run_pid" 2>/dev/null | tr -d ' ')
    [ -z "$pgid" ] && pgid="$run_pid"

    # Time-box watcher: TERM the group at BUDGET, KILL it after a short grace.
    (
        sleep "$BUDGET"
        kill -TERM -"$pgid" 2>/dev/null
        sleep 10
        kill -KILL -"$pgid" 2>/dev/null
    ) &
    killer=$!

    wait "$run_pid" 2>/dev/null
    end=$(date +%s)

    # Stop the watcher and guarantee no worker from this run survives.
    kill "$killer" 2>/dev/null
    wait "$killer" 2>/dev/null
    kill -KILL -"$pgid" 2>/dev/null
    sleep 1

    elapsed=$(( end - start ))
    [ "$elapsed" -lt 1 ] && elapsed=1
    # grep -c always prints a count; don't add `|| echo 0` (grep prints 0 itself
    # and exits 1 on no-match, which would yield a spurious second line).
    ok=$(grep -c '] OK' "$log" 2>/dev/null); ok=${ok:-0}
    to=$(grep -c '] TIMEOUT' "$log" 2>/dev/null); to=${to:-0}
    fail=$(grep -c '] FAIL' "$log" 2>/dev/null); fail=${fail:-0}

    okpm=$(awk -v ok="$ok" -v e="$elapsed" 'BEGIN{printf "%.1f", (e>0)? ok*60.0/e : 0}')
    if [ -z "$base_okpm" ]; then base_okpm="$okpm"; fi
    sp=$(awk -v a="$okpm" -v b="$base_okpm" 'BEGIN{printf "%.2fx", (b>0)? a/b : 0}')

    note=""
    if [ "$elapsed" -lt "$(( BUDGET * 9 / 10 ))" ]; then
        note="  <-- finished early: workload too small, OK/min capped by #cases not cores"
    fi
    printf '%-6s %8s %8s %8s %10s %10s %10s%s\n' "$J" "$ok" "$to" "$fail" "$elapsed" "$okpm" "$sp" "$note"
done

echo
echo "Read the OK/min and speedup columns. If 28 is not ~meaningfully higher than 8,"
echo "the per-case overhead (subprocess spawn + shared-FS temp json + critical-section"
echo "flush/CSV) dominates and extra cores are wasted."
