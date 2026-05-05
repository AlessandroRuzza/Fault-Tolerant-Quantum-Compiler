#!/usr/bin/env sh
set -eu

REPO_ROOT="$PWD"
PYTHON="${REPO_ROOT}/.env/bin/python"
SCRIPT="${REPO_ROOT}/scripts/run_wisq.py"
QASM_DIR="${REPO_ROOT}/universal_set_qasms"

output="${1:-${OUTPUT:-}}"
mr_timeout="${2:-${MR_TIMEOUT:-}}"

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

if [ -z "$output" ]; then
    output="$(read_makeflag_var OUTPUT || true)"
fi

if [ -z "$mr_timeout" ]; then
    mr_timeout="$(read_makeflag_var MR_TIMEOUT || true)"
fi

set -- "$PYTHON" "$SCRIPT" --qasm "$QASM_DIR"/*.qasm

if [ -n "$output" ]; then
    set -- "$@" --output "$output" --append
fi

if [ -n "$mr_timeout" ]; then
    set -- "$@" --mr_timeout "$mr_timeout"
fi

exec "$@"
