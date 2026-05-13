#!/usr/bin/env sh
set -eu

binary_path="${1:-}"
bench_path="${2:-${BENCH_PATH:-}}"
rerun_timeouts="${3:-${RERUN_TIMEOUTS:-}}"
openmp_jobs="${4:-${OPENMP_JOBS:-}}"
cuda_jobs="${5:-${CUDA_JOBS:-}}"
bench_process_count="${6:-${BENCH_PROCESS_COUNT:-}}"
processor="${7:-${PROCESSOR:-}}"
allow_failures="${8:-${ALLOW_FAILURES:-}}"

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

if [ -z "$openmp_jobs" ]; then
    openmp_jobs="$(read_makeflag_var OPENMP_JOBS || true)"
fi

if [ -z "$cuda_jobs" ]; then
    cuda_jobs="$(read_makeflag_var CUDA_JOBS || true)"
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
    echo "Usage: make run-bench BENCH_PATH=<path_or_name> [RERUN_TIMEOUTS=1] [OPENMP_JOBS=<n>] [CUDA_JOBS=<n>] [BENCH_PROCESS_COUNT=<n>] [PROCESSOR=<n>] [ALLOW_FAILURES=True]"
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

run_binary() {
    set -- "$@" --bench_path "$bench_path"

    if [ -n "$bench_process_count" ]; then
        set -- "$@" --process-count "$bench_process_count"
    fi

    set -- "$@" --processor "$processor"

    if [ -n "$rerun_timeouts" ] && [ "$rerun_timeouts" != "0" ] && [ "$rerun_timeouts" != "false" ] && [ "$rerun_timeouts" != "False" ]; then
        set -- "$@" --rerun-timeouts
    fi

    if [ -n "$openmp_jobs" ] && [ -n "$cuda_jobs" ]; then
        env OMP_NUM_THREADS="$openmp_jobs" CUDA_JOBS="$cuda_jobs" "$@"
        return $?
    fi

    if [ -n "$openmp_jobs" ]; then
        env OMP_NUM_THREADS="$openmp_jobs" "$@"
        return $?
    fi

    if [ -n "$cuda_jobs" ]; then
        env CUDA_JOBS="$cuda_jobs" "$@"
        return $?
    fi

    "$@"
}

if run_binary "$binary_path"; then
    run_rc=0
else
    run_rc=$?
fi

if [ "$run_rc" -eq 0 ]; then
    exit 0
fi

if is_truthy "$allow_failures"; then
    echo "Benchmark failed with exit code $run_rc, but ALLOW_FAILURES=$allow_failures so exiting successfully."
    exit 0
fi

exit "$run_rc"
