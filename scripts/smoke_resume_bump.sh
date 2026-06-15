#!/usr/bin/env bash
# Smoke test: stop a sweep, restart with a DIFFERENT process count, and verify
# already-completed cases are NOT re-executed.
#
# Regression target: when the process count changes the expanded file is
# regenerated, and the "executed" flags it carries over are only as fresh as the
# last clean persist_expanded() — an interrupted/hard-killed run leaves them
# stale (false). expand_config_variants() must overlay the per-case sidecar
# (<name>_expanded.status.jsonl), the incremental source of truth, so resume
# still skips finished work. This test fakes the stale-expanded condition by
# resetting every "executed" flag to false while leaving the sidecar intact,
# then bumps the process count and asserts zero re-execution.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BIN="build/FaultTolerantQuantumCompiler"
BENCH="smoke_resume"
CONFIG="config/${BENCH}.json"   # config/ is a symlink into the data submodule
EXEC_DIR="config/executed"
EXPANDED="${EXEC_DIR}/${BENCH}_expanded.json"
LEGACY_SIDECAR="${EXEC_DIR}/${BENCH}_expanded.status.jsonl"
CSV="benchmarks/results/${BENCH}_runs.csv"

[ -x "$BIN" ] || { echo "FAIL: $BIN not built. Run: cmake --build build --target FaultTolerantQuantumCompiler"; exit 1; }

# Generate a tiny self-contained config (toffoli_n3 keeps each case sub-second)
# so the test depends on nothing committed in the data submodule.
cat > "$CONFIG" <<'JSON'
{
  "circuit": "toffoli_n3",
  "type": "gaussian",
  "magic_aware_strategy": "distance",
  "gaussian_strategy": "coarse",
  "safe_passage_strategy": "connectivity",
  "MagicStatePlacementStrategy": "center_circle",
  "border_distance_percentage": 10.0,
  "MAGIC_HIGH": 1.6,
  "MAGIC_LOW": 0.0,
  "CNOT_HIGH": -1,
  "CNOT_LOW": -1,
  "MAPPED_GAUSSIAN_WEIGHT": -1,
  "BASE_GAUSSIAN_WEIGHT": 1.0,
  "EXTERNAL_WEIGHT": 0.0,
  "GAUSSIAN_SIGMA": [0.2, 0.3, 0.4],
  "number_of_magic_states": -1,
  "x": -1,
  "y": -1,
  "dimension_offset": 0,
  "routing_strategy": "naive",
  "t-routing-mode": "smart_t_routing",
  "repetition": 1,
  "timeout": 600,
  "timeout_reached": false
}
JSON

# Clean any state from a previous run of this smoke test.
rm -f "$EXPANDED" "$LEGACY_SIDECAR" "$CSV" "${EXEC_DIR}/${BENCH}_expanded.p"*.status.jsonl

run_proc() { # process_count processor logfile
  "$BIN" --bench_path "$BENCH" --process-count "$1" --processor "$2" >"$3" 2>&1
}

count_executed() { grep -cE '\] (OK|FAIL|SAFE_PASSAGE_FAILED|TIMEOUT)' "$1" || true; }
count_skipped()  { grep -c   'executed=true' "$1" || true; }

tmp="$(mktemp -d)"
# Leave no trace in the data submodule: drop the generated config and artifacts.
trap 'rm -rf "$tmp" "$CONFIG" "$EXPANDED" "$LEGACY_SIDECAR" "$CSV" "$CSV".lock "${EXEC_DIR}/${BENCH}_expanded.p"*.status.jsonl' EXIT

echo "== Pass 1: initial run, process-count=2 =="
run_proc 2 0 "$tmp/p2_0.log"
run_proc 2 1 "$tmp/p2_1.log"
exec1=$(( $(count_executed "$tmp/p2_0.log") + $(count_executed "$tmp/p2_1.log") ))
echo "   executed cases: $exec1"
[ "$exec1" -ge 1 ] || { echo "FAIL: first run executed nothing — test is vacuous."; cat "$tmp"/p2_*.log; exit 1; }

echo "== Check: each processor wrote its OWN sidecar, no shared file =="
for p in 0 1; do
  [ -s "${EXEC_DIR}/${BENCH}_expanded.p${p}.status.jsonl" ] \
    || { echo "FAIL: missing per-processor sidecar p${p}."; exit 1; }
done
[ ! -e "$LEGACY_SIDECAR" ] \
  || { echo "FAIL: a run wrote the shared legacy sidecar (concurrent-write hazard not fixed)."; exit 1; }
echo "   p0/p1 sidecars present, shared file absent."

echo "== Robustness: a corrupted legacy sidecar must be tolerated, not fatal =="
printf '{"i":0,"e":true,"t":fal{"i":1,corrupt\n' > "$LEGACY_SIDECAR"

echo "== Simulate an interrupted run: blank the expanded 'executed' flags, keep sidecars =="
python3 - "$EXPANDED" <<'PY'
import json, sys
p = sys.argv[1]
data = json.load(open(p))
for e in data:
    e["executed"] = False
    e["timeout_reached"] = False
json.dump(data, open(p, "w"), indent=2)
PY

echo "== Pass 2: resume with BUMPED process-count=4 =="
reexec=0
for p in 0 1 2 3; do
  run_proc 4 "$p" "$tmp/p4_$p.log"
  reexec=$(( reexec + $(count_executed "$tmp/p4_$p.log") ))
done
skipped=0
for p in 0 1 2 3; do skipped=$(( skipped + $(count_skipped "$tmp/p4_$p.log") )); done
echo "   re-executed cases: $reexec   (skipped executed=true: $skipped)"

if [ "$reexec" -ne 0 ]; then
  echo "FAIL: $reexec case(s) were re-executed after bumping process count."
  grep -hE '\] (OK|FAIL|SAFE_PASSAGE_FAILED|TIMEOUT)' "$tmp"/p4_*.log || true
  exit 1
fi
[ "$skipped" -ge "$exec1" ] || { echo "FAIL: expected >=${exec1} skips, got ${skipped}."; exit 1; }

echo "PASS: bump from 2 to 4 processes re-executed 0 cases (sidecar overlay works)."
