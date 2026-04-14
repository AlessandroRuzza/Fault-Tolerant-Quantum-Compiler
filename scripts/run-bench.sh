#!/usr/bin/env sh
set -eu

binary_path="${1:-}"
bench_path="${2:-}"

if [ -z "$binary_path" ] || [ -z "$bench_path" ]; then
    echo "Usage: make run-bench BENCH_PATH=<path_or_name>"
    exit 1
fi

"$binary_path" --bench_path "$bench_path"
