#!/usr/bin/env sh
set -eu

REPO_ROOT="$PWD"
PYTHON="${REPO_ROOT}/.env/bin/python"
SCRIPT="${REPO_ROOT}/scripts/run_wisq.py"

qasm="${1:-${QASM:-}}"
output="${2:-${OUTPUT:-}}"
mr_timeout="${3:-${MR_TIMEOUT:-}}"

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

if [ -z "$qasm" ]; then
    qasm="$(read_makeflag_var QASM || true)"
fi

if [ -z "$output" ]; then
    output="$(read_makeflag_var OUTPUT || true)"
fi

if [ -z "$mr_timeout" ]; then
    mr_timeout="$(read_makeflag_var MR_TIMEOUT || true)"
fi

if [ -z "$qasm" ]; then
    echo "Usage: make run-wisq QASM=\"<name> [name2 ...]\" [OUTPUT=<csv>] [MR_TIMEOUT=<secs>]"
    exit 1
fi

resolve_qasm() {
    name="$1"
    case "$name" in
        *_universal.qasm) ;;
        *.qasm) name="${name%.qasm}_universal.qasm" ;;
        *) name="${name}_universal.qasm" ;;
    esac
    printf '%s' "${REPO_ROOT}/universal_set_qasms/${name}"
}

set -- "$PYTHON" "$SCRIPT" --qasm
for name in $qasm; do
    set -- "$@" "$(resolve_qasm "$name")"
done

if [ -n "$output" ]; then
    set -- "$@" --output "$output" --append
fi

if [ -n "$mr_timeout" ]; then
    set -- "$@" --mr_timeout "$mr_timeout"
fi

exec "$@"
