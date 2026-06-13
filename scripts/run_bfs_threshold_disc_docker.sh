#!/usr/bin/env bash
# Sweep BFS-threshold DISCRIMINANTE (griglie strette) in DOCKER, codice POST-FIX.
# Builda ftqc-retune:postfix dal sorgente (NON tocca Dockerfile ne' immagine pubblicata).
#   scripts/run_bfs_threshold_disc_docker.sh
set -eu
cd "$(dirname "$0")/.."
IMAGE="ftqc-retune:postfix"
THREADS="${OMP_NUM_THREADS:-$(nproc)}"

echo "=== build immagine post-fix ($IMAGE) ==="
DOCKER_BUILDKIT=1 docker build -t "$IMAGE" .

echo "=== soglia -1.0 (bfs_disc_heap) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=-1.0 \
  -e BENCH_PATH=bfs_disc_heap \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.4 (bfs_disc_040) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.4 \
  -e BENCH_PATH=bfs_disc_040 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.45 (bfs_disc_045) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.45 \
  -e BENCH_PATH=bfs_disc_045 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.5 (bfs_disc_050) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.5 \
  -e BENCH_PATH=bfs_disc_050 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.55 (bfs_disc_055) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.55 \
  -e BENCH_PATH=bfs_disc_055 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.65 (bfs_disc_065) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.65 \
  -e BENCH_PATH=bfs_disc_065 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.8 (bfs_disc_080) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.8 \
  -e BENCH_PATH=bfs_disc_080 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.9 (bfs_disc_090) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.9 \
  -e BENCH_PATH=bfs_disc_090 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 1.0 (bfs_disc_100) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=1.0 \
  -e BENCH_PATH=bfs_disc_100 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "FATTO. CSV in data/results/bfs_disc_*_runs.csv"