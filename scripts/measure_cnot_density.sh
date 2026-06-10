#!/usr/bin/env bash
# Measure the CNOT-graph density of one or more circuits by running the compiler
# with the opt-in DENSITY_PROBE (env FTQC_DENSITY_PROBE). Density is the fraction
# of qubit pairs sharing a CNOT and is what gaussian_mapping's CNOT-BFS gate keys
# on (BFS used iff density < FTQC_BFS_DENSITY_THRESHOLD, default 0.45).
#
# Usage:   scripts/measure_cnot_density.sh circuitA circuitB ...
# Output:  one "<circuit> density=<d> order=<BFS|heap> n=<n>" line per circuit,
#          sorted by density. Runs single-circuit (no bench), 4 at a time.
set -u
BIN=./build/FaultTolerantQuantumCompiler
[ -x "$BIN" ] || { echo "build first: cmake --build build -j4 --target FaultTolerantQuantumCompiler" >&2; exit 1; }

measure() {
  local c="$1"
  local out
  out=$(FTQC_DENSITY_PROBE=1 OMP_NUM_THREADS=1 "$BIN" \
        --circuit "$c" --type gaussian --gaussian-strategy fine --x 40 --y 40 \
        2>&1 </dev/null | grep DENSITY_PROBE | head -1)
  if [ -z "$out" ]; then
    printf '%-22s <empty/parse-failed>\n' "$c"
  else
    # DENSITY_PROBE n=NN density=DD order=OO
    local n d o
    n=$(sed -nE 's/.*n=([0-9]+).*/\1/p' <<<"$out")
    d=$(sed -nE 's/.*density=([0-9.eE+-]+).*/\1/p' <<<"$out")
    o=$(sed -nE 's/.*order=([A-Za-z]+).*/\1/p' <<<"$out")
    printf '%s\t%s\t%s\t%s\n' "$d" "$c" "$o" "$n"
  fi
}
export -f measure
export BIN

printf '%s\n' "$@" | xargs -P4 -I{} bash -c 'measure "{}"' \
  | sort -g \
  | awk -F'\t' 'NF==4{printf "%-22s density=%-10s order=%-5s n=%s\n",$2,$1,$3,$4; next}{print}'
