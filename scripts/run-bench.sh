#!/usr/bin/env sh
set -eu

binary_path="${1:-}"
bench_path="${2:-${BENCH_PATH:-}}"
rerun_timeouts="${3:-${RERUN_TIMEOUTS:-}}"
bench_jobs="${4:-${BENCH_JOBS:-}}"

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

if [ -z "$binary_path" ] || [ -z "$bench_path" ]; then
    echo "Usage: make run-bench BENCH_PATH=<path_or_name> [RERUN_TIMEOUTS=1] [BENCH_JOBS=<n>]"
    exit 1
fi

run_binary() {
    if [ -n "$bench_jobs" ]; then
        exec env OMP_NUM_THREADS="$bench_jobs" "$@"
    fi

    exec "$@"
}

if [ -n "$rerun_timeouts" ] && [ "$rerun_timeouts" != "0" ] && [ "$rerun_timeouts" != "false" ] && [ "$rerun_timeouts" != "False" ]; then
    run_binary "$binary_path" --bench_path "$bench_path" --rerun-timeouts
else
    run_binary "$binary_path" --bench_path "$bench_path"
fi
