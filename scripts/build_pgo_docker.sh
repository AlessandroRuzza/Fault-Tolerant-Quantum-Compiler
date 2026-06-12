#!/usr/bin/env bash
#
# build_pgo_docker.sh — portable Profile-Guided Optimization build, intended for
# use inside a Docker build (see Dockerfile_PGO). Same two-phase flow as
# build_pgo.sh, but:
#   * NO -march=native  -> binary stays portable across CPUs (safe to ship in an
#     image). Pass MARCH=x86-64-v3 (or similar) to opt into a baseline ISA.
#   * uses Ninja when available (the build image has it).
#   * builds only the FaultTolerantQuantumCompiler target.
#   * EXTRA_CMAKE_ARGS is forwarded to both cmake configure calls (e.g. Eigen /
#     Boost include hints supplied by the Dockerfile).
#
# Phases:
#   1. instrumented build (-fprofile-generate)
#   2. training run: --bench <BENCH> with a single worker (OMP_NUM_THREADS=1)
#   3. optimized rebuild (-fprofile-use + LTO)
#
# Usage:
#   scripts/build_pgo_docker.sh [BENCH] [MARCH]
#     BENCH  benchmark config name to train on   (default: profile)
#     MARCH  -march value, empty = generic        (default: empty)
#
# Env overrides:
#   EXTRA_CMAKE_ARGS  extra args appended to both configure calls (default: empty)
#   PGO_DATA          profile data dir            (default: /tmp/ftqc-pgo)
#   BUILD_DIR         final optimized build dir   (default: build)
#   GEN_BUILD_DIR     instrumented build dir      (default: build-pgo-gen)
#   JOBS              compile parallelism         (default: nproc)
#   TARGET            cmake target to build       (default: FaultTolerantQuantumCompiler)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BENCH="${1:-profile}"
MARCH="${2:-}"
PGO_DATA="${PGO_DATA:-/tmp/ftqc-pgo}"
BUILD_DIR="${BUILD_DIR:-build}"
GEN_BUILD_DIR="${GEN_BUILD_DIR:-build-pgo-gen}"
JOBS="${JOBS:-$(nproc)}"
TARGET="${TARGET:-FaultTolerantQuantumCompiler}"

# Optional -march; empty by default for a portable image.
MARCH_FLAG=""
if [[ -n "$MARCH" ]]; then
    MARCH_FLAG="-march=$MARCH"
fi

# Prefer Ninja when present (faster, and installed in the build image).
GEN_ARG=()
if command -v ninja >/dev/null 2>&1; then
    GEN_ARG=(-G Ninja)
fi

# Word-split EXTRA_CMAKE_ARGS into an array (Dockerfile passes a plain string).
read -r -a EXTRA_ARGS <<< "${EXTRA_CMAKE_ARGS:-}"

echo "==> PGO (docker) build for '$TARGET'"
echo "    bench=$BENCH  march='${MARCH:-generic}'  profile-data=$PGO_DATA  jobs=$JOBS"

# Start from clean profile data so stale counters can't leak in.
rm -rf "$PGO_DATA"
mkdir -p "$PGO_DATA"

# ---------------------------------------------------------------------------
# Phase 1: instrumented build
# ---------------------------------------------------------------------------
echo "==> [1/3] Configuring + building instrumented binary ($GEN_BUILD_DIR)"
rm -rf "$GEN_BUILD_DIR"
cmake -S . -B "$GEN_BUILD_DIR" "${GEN_ARG[@]}" -DCMAKE_BUILD_TYPE=Release \
    "${EXTRA_ARGS[@]}" \
    -DCMAKE_CXX_FLAGS="$MARCH_FLAG -fprofile-generate=$PGO_DATA" \
    -DCMAKE_EXE_LINKER_FLAGS="-fprofile-generate=$PGO_DATA"
cmake --build "$GEN_BUILD_DIR" --target "$TARGET" -j "$JOBS"

# ---------------------------------------------------------------------------
# Phase 2: training run (single worker)
# ---------------------------------------------------------------------------
echo "==> [2/3] Training run: --bench $BENCH with 1 worker (OMP_NUM_THREADS=1)"
( cd "$GEN_BUILD_DIR" && OMP_NUM_THREADS=1 "./$TARGET" --bench "$BENCH" )

if ! ls "$PGO_DATA"/*.gcda >/dev/null 2>&1; then
    echo "ERROR: no .gcda profile data produced in $PGO_DATA — aborting." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Phase 3: optimized rebuild using the profile
# ---------------------------------------------------------------------------
echo "==> [3/3] Configuring + building optimized binary ($BUILD_DIR)"
rm -rf "$BUILD_DIR"
cmake -S . -B "$BUILD_DIR" "${GEN_ARG[@]}" -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
    "${EXTRA_ARGS[@]}" \
    -DCMAKE_CXX_FLAGS="$MARCH_FLAG -funroll-loops -fprofile-use=$PGO_DATA -fprofile-correction -Wno-missing-profile" \
    -DCMAKE_EXE_LINKER_FLAGS="-fprofile-use=$PGO_DATA"
cmake --build "$BUILD_DIR" --target "$TARGET" -j "$JOBS"

echo "==> Done. Optimized PGO binary: $BUILD_DIR/$TARGET"
