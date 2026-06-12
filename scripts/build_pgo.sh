#!/usr/bin/env bash
#
# build_pgo.sh — Profile-Guided Optimization build for FaultTolerantQuantumCompiler.
#
# Two phases:
#   1. Build an instrumented binary (-fprofile-generate) and run the `profile`
#      benchmark to collect profile data (.gcda counters).
#   2. Rebuild optimized (-fprofile-use + LTO) using that profile data.
#
# The bench runner defaults to $(nproc) OpenMP workers; the training run below
# pins OMP_NUM_THREADS=1 so a single worker process executes the cases serially
# (clean, deterministic profile counters). Compiler build parallelism (-j) is
# separate and still uses all cores.
#
# Usage:
#   scripts/build_pgo.sh [BENCH] [MARCH]
#     BENCH  benchmark config name to train on   (default: profile)
#     MARCH  -march value                        (default: native; use e.g.
#            x86-64-v3 for portable / cluster builds)
#
# Env overrides:
#   CXX            C++ compiler                  (default: cmake's choice)
#   PGO_DATA       profile data dir              (default: /tmp/ftqc-pgo)
#   BUILD_DIR      final optimized build dir     (default: build)
#   GEN_BUILD_DIR  instrumented build dir        (default: build-pgo-gen)
#   JOBS           compile parallelism           (default: nproc)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BENCH="${1:-profile}"
MARCH="${2:-native}"
PGO_DATA="${PGO_DATA:-/tmp/ftqc-pgo}"
BUILD_DIR="${BUILD_DIR:-build}"
GEN_BUILD_DIR="${GEN_BUILD_DIR:-build-pgo-gen}"
JOBS="${JOBS:-$(nproc)}"
EXE="FaultTolerantQuantumCompiler"

CXX_ARG=()
if [[ -n "${CXX:-}" ]]; then
    CXX_ARG=(-DCMAKE_CXX_COMPILER="$CXX")
fi

echo "==> PGO build for '$EXE'"
echo "    bench=$BENCH  march=$MARCH  profile-data=$PGO_DATA  jobs=$JOBS"

# Start from clean profile data so stale counters can't leak in.
rm -rf "$PGO_DATA"
mkdir -p "$PGO_DATA"

# ---------------------------------------------------------------------------
# Phase 1: instrumented build
# ---------------------------------------------------------------------------
echo "==> [1/3] Configuring + building instrumented binary ($GEN_BUILD_DIR)"
rm -rf "$GEN_BUILD_DIR"
cmake -S . -B "$GEN_BUILD_DIR" -DCMAKE_BUILD_TYPE=Release \
    "${CXX_ARG[@]}" \
    -DCMAKE_CXX_FLAGS="-march=$MARCH -fprofile-generate=$PGO_DATA" \
    -DCMAKE_EXE_LINKER_FLAGS="-fprofile-generate=$PGO_DATA"
cmake --build "$GEN_BUILD_DIR" -j "$JOBS"

# ---------------------------------------------------------------------------
# Phase 2: training run (single worker)
# ---------------------------------------------------------------------------
echo "==> [2/3] Training run: --bench $BENCH with 1 worker (OMP_NUM_THREADS=1)"
( cd "$GEN_BUILD_DIR" && OMP_NUM_THREADS=1 "./$EXE" --bench "$BENCH" )

if ! ls "$PGO_DATA"/*.gcda >/dev/null 2>&1; then
    echo "ERROR: no .gcda profile data produced in $PGO_DATA — aborting." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Phase 3: optimized rebuild using the profile
# ---------------------------------------------------------------------------
echo "==> [3/3] Configuring + building optimized binary ($BUILD_DIR)"
rm -rf "$BUILD_DIR"
cmake -S . -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release \
    "${CXX_ARG[@]}" \
    -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
    -DCMAKE_CXX_FLAGS="-march=$MARCH -funroll-loops -fprofile-use=$PGO_DATA -fprofile-correction -Wno-missing-profile" \
    -DCMAKE_EXE_LINKER_FLAGS="-fprofile-use=$PGO_DATA"
cmake --build "$BUILD_DIR" -j "$JOBS"

echo "==> Done. Optimized PGO binary: $BUILD_DIR/$EXE"
