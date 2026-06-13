#!/usr/bin/env bash
# Sweep BFS-threshold 0.7-1.0 in DOCKER, codice POST-FIX (build da sorgente).
# NON tocca il Dockerfile ne' l'immagine alessandroruzza/ftqc (che e' pre-fix):
# builda un'immagine nuova con tag ftqc-retune:postfix.
#   scripts/run_bfs_threshold_hi_docker.sh
set -eu
cd "$(dirname "$0")/.."
IMAGE="ftqc-retune:postfix"
THREADS="${OMP_NUM_THREADS:-$(nproc)}"

echo "=== build immagine post-fix ($IMAGE) ==="
DOCKER_BUILDKIT=1 docker build -t "$IMAGE" .

echo "=== soglia 0.7 (bfs_hi_070) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.7 \
  -e BENCH_PATH=bfs_hi_070 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.8 (bfs_hi_080) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.8 \
  -e BENCH_PATH=bfs_hi_080 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.9 (bfs_hi_090) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.9 \
  -e BENCH_PATH=bfs_hi_090 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 0.95 (bfs_hi_095) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=0.95 \
  -e BENCH_PATH=bfs_hi_095 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "=== soglia 1.0 (bfs_hi_100) ==="
docker run --rm --init \
  -e FTQC_BFS_DENSITY_THRESHOLD=1.0 \
  -e BENCH_PATH=bfs_hi_100 \
  -e OMP_NUM_THREADS="$THREADS" \
  -v "$PWD/data/config:/app/config" \
  -v "$PWD/data/results:/app/benchmarks/results" \
  "$IMAGE"

echo "FATTO. CSV in data/results/bfs_hi_*_runs.csv"