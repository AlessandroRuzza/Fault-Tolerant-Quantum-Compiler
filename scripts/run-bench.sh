#!/usr/bin/env sh
set -eu

binary_path="${1:-}"
bench_path="${2:-${BENCH_PATH:-}}"
rerun_timeouts="${3:-${RERUN_TIMEOUTS:-}}"
bench_jobs="${4:-${BENCH_JOBS:-}}"
bench_process_count="${5:-${BENCH_PROCESS_COUNT:-}}"
processor="${6:-${PROCESSOR:-}}"
allow_failures="${7:-${ALLOW_FAILURES:-}}"

read_makeflag_var() {
    key="$1"
    for token in ${MAKEFLAGS:-}; do
        case "$token" in
            "$key"=*)
                printf '%s\n' "${token#*=}"
                return 0
                ;;
        esac
    done
    return 1
}

if [ -z "$bench_path" ]; then
    bench_path="$(read_makeflag_var BENCH_PATH || true)"
fi

if [ -z "$rerun_timeouts" ]; then
    rerun_timeouts="$(read_makeflag_var RERUN_TIMEOUTS || true)"
fi

if [ -z "$bench_jobs" ]; then
    bench_jobs="$(read_makeflag_var BENCH_JOBS || true)"
fi

if [ -z "$bench_process_count" ]; then
    bench_process_count="$(read_makeflag_var BENCH_PROCESS_COUNT || true)"
fi

if [ -z "$processor" ]; then
    processor="$(read_makeflag_var PROCESSOR || true)"
fi

if [ -z "$allow_failures" ]; then
    allow_failures="$(read_makeflag_var ALLOW_FAILURES || true)"
fi

if [ -z "$processor" ]; then
    processor="0"
fi

if [ -z "$binary_path" ] || [ -z "$bench_path" ]; then
    echo "Usage: make run-bench BENCH_PATH=<path_or_name> [RERUN_TIMEOUTS=1] [BENCH_JOBS=<n>] [BENCH_PROCESS_COUNT=<n>] [PROCESSOR=<n>] [ALLOW_FAILURES=True]"
    exit 1
fi

is_truthy() {
    case "$1" in
        1|true|True|TRUE|yes|Yes|YES|on|On|ON)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Assemble the argv for the binary into the script's positional params,
# then exec so the binary replaces this shell. The binary then receives
# SIGINT/SIGTERM/SIGHUP directly and can write "interrupted" to the CSV.
# Caveat: with exec we can't honor ALLOW_FAILURES (we don't get to inspect
# the exit code), so when that flag is requested we fall back to child-process
# mode and forward signals via a trap.

set -- "$binary_path" --bench_path "$bench_path"

if [ -n "$bench_process_count" ]; then
    set -- "$@" --process-count "$bench_process_count"
fi

set -- "$@" --processor "$processor"

if [ -n "$rerun_timeouts" ] && [ "$rerun_timeouts" != "0" ] && [ "$rerun_timeouts" != "false" ] && [ "$rerun_timeouts" != "False" ]; then
    set -- "$@" --rerun-timeouts
fi

if is_truthy "$allow_failures"; then
    # Child-process mode with signal forwarding so the binary still writes
    # "interrupted" rows when Ctrl+C / docker stop arrives during a run.
    binary_pid=
    forward_signal() {
        if [ -n "$binary_pid" ]; then
            kill -"$1" "$binary_pid" 2>/dev/null || true
        fi
    }
    trap 'forward_signal TERM' TERM
    trap 'forward_signal INT' INT
    trap 'forward_signal HUP' HUP

    if [ -n "$bench_jobs" ]; then
        env OMP_NUM_THREADS="$bench_jobs" "$@" &
    else
        "$@" &
    fi
    binary_pid=$!
    # `wait` returns early when interrupted by a signal — loop until the
    # binary really exits.
    while kill -0 "$binary_pid" 2>/dev/null; do
        wait "$binary_pid" 2>/dev/null || true
    done
    wait "$binary_pid" 2>/dev/null
    run_rc=$?

    if [ "$run_rc" -eq 0 ]; then
        exit 0
    fi
    echo "Benchmark failed with exit code $run_rc, but ALLOW_FAILURES=$allow_failures so exiting successfully."
    exit 0
fi

# Default path: exec so signals go straight to the binary.
if [ -n "$bench_jobs" ]; then
    exec env OMP_NUM_THREADS="$bench_jobs" "$@"
fi
exec "$@"
