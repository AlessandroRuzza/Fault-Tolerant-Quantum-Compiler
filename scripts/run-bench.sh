#!/usr/bin/env sh
set -eu

binary_path="${1:-}"
bench_path="${2:-}"
rerun_timeouts="${3:-}"

if [ -z "$binary_path" ] || [ -z "$bench_path" ]; then
    echo "Usage: make run-bench BENCH_PATH=<path_or_name> [RERUN_TIMEOUTS=1]"
    exit 1
fi

if [ -n "$rerun_timeouts" ] && [ "$rerun_timeouts" != "0" ] && [ "$rerun_timeouts" != "false" ] && [ "$rerun_timeouts" != "False" ]; then
    "$binary_path" --bench_path "$bench_path" --rerun-timeouts
else
    "$binary_path" --bench_path "$bench_path"
fi
