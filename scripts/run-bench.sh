#!/usr/bin/env sh
set -eu

binary_path="${1:-}"
bench_path="${2:-${BENCH_PATH:-}}"
rerun_timeouts="${3:-${RERUN_TIMEOUTS:-}}"
bench_jobs="${4:-${BENCH_JOBS:-}}"
bench_process_count="${5:-${BENCH_PROCESS_COUNT:-}}"
processor="${6:-${PROCESSOR:-}}"

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

if [ -z "$processor" ]; then
    processor="0"
fi

if [ -z "$binary_path" ] || [ -z "$bench_path" ]; then
    echo "Usage: make run-bench BENCH_PATH=<path_or_name> [RERUN_TIMEOUTS=1] [BENCH_JOBS=<n>] [BENCH_PROCESS_COUNT=<n>] [PROCESSOR=<n>]"
    exit 1
fi

run_binary() {
    set -- "$@" --bench_path "$bench_path"

    if [ -n "$bench_process_count" ]; then
        set -- "$@" --process-count "$bench_process_count"
    fi

    set -- "$@" --processor "$processor"

    if [ -n "$rerun_timeouts" ] && [ "$rerun_timeouts" != "0" ] && [ "$rerun_timeouts" != "false" ] && [ "$rerun_timeouts" != "False" ]; then
        set -- "$@" --rerun-timeouts
    fi

    if [ -n "$bench_jobs" ]; then
        exec env OMP_NUM_THREADS="$bench_jobs" "$@"
    fi

    exec "$@"
}

run_binary "$binary_path"
