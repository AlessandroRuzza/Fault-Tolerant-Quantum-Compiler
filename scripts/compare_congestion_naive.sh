#!/usr/bin/env bash
set -uo pipefail

usage() {
	cat <<'USAGE'
Usage: compare_congestion_naive.sh <circuit.qasm>
Runs `FaultTolerantQuantumCompiler` with `--routing naive` and `--routing congestion`
from the repository `build/` directory and compares the final "Total routing steps: N" values.
USAGE
	exit 2
}

if [ $# -lt 1 ]; then
	usage
fi

circuit="$1.qasm"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$REPO_ROOT/build"

if [ ! -d "$BUILD_DIR" ]; then
	echo "Build directory not found: $BUILD_DIR" >&2
	exit 1
fi

ORIG_PWD="$(pwd)"
cd "$BUILD_DIR" || { echo "Failed to cd to $BUILD_DIR" >&2; exit 1; }

tmp_naive=$(mktemp /tmp/compare_naive.XXXXXX)
tmp_cong=$(mktemp /tmp/compare_cong.XXXXXX)

cleanup() {
	rm -f "$tmp_naive" "$tmp_cong"
	cd "$ORIG_PWD" >/dev/null || true
}
trap cleanup EXIT

echo "Running naive routing..."
./FaultTolerantQuantumCompiler --circuit "$circuit" --routing naive >"$tmp_naive" 2>&1 || echo "Naive run exited non-zero, logs kept in $tmp_naive"

echo "Running congestion routing..."
./FaultTolerantQuantumCompiler --circuit "$circuit" --routing congestion >"$tmp_cong" 2>&1 || echo "Congestion run exited non-zero, logs kept in $tmp_cong"

extract_steps() {
	local file="$1"
	local steps
	# Match lines like:
	#   Total routing steps: 192
	#   Total routing steps (naive): 192
	#   Total routing steps (congestion): 196
	# Capture the last integer on the matched line; group 3 holds the number when
	# parentheses are present or absent.
	steps=$(grep -E 'Total routing steps' "$file" | tail -n1 | sed -E 's/.*Total routing steps( \((naive|congestion)\))?: *([0-9]+).*/\3/')
	if [ -z "$steps" ]; then
		steps=$(grep -E 'Total routing steps' "$file" | tail -n1 | grep -Eo '[0-9]+' | tail -n1 || true)
	fi
	if [ -z "$steps" ]; then
		printf 'N/A'
	else
		printf '%s' "$steps"
	fi
}

naive_steps=$(extract_steps "$tmp_naive")
cong_steps=$(extract_steps "$tmp_cong")

echo "Results for circuit: $circuit"
printf '  %-12s %s\n' "naive:" "$naive_steps"
printf '  %-12s %s\n' "congestion:" "$cong_steps"

is_integer() {
	[[ "$1" =~ ^[0-9]+$ ]]
}

if is_integer "$naive_steps" && is_integer "$cong_steps"; then
	diff=$((cong_steps - naive_steps))
	if [ $diff -gt 0 ]; then
		echo "Congestion used MORE steps by $diff"
	elif [ $diff -lt 0 ]; then
		echo "Congestion used FEWER steps by $((-diff))"
	else
		echo "Both used the SAME number of steps ($naive_steps)"
	fi
else
	echo "Could not extract numeric step counts from logs. Showing last 30 lines of each log:"
	echo "---- Naive log (last 30 lines) ----"
	tail -n 30 "$tmp_naive"
	echo "---- Congestion log (last 30 lines) ----"
	tail -n 30 "$tmp_cong"
	exit 3
fi

exit 0

