#!/usr/bin/env bash
# Lancia lo sweep BFS-threshold: una run per soglia, env var diversa.
# Eseguire come l'utente che ha i permessi su data/config/executed/ (root).
#   scripts/run_bfs_threshold_sweep.sh <BINARIO> [OMP_NUM_THREADS]
set -eu
BIN="${1:?serve il path del binario, es. build/FaultTolerantQuantumCompiler}"
export OMP_NUM_THREADS="${2:-$(nproc)}"

echo "=== soglia -1.0 (bfs_thr_heap) ==="
FTQC_BFS_DENSITY_THRESHOLD=-1.0 "$BIN" --bench_path data/config/bfs_thr_heap.json

echo "=== soglia 0.4 (bfs_thr_040) ==="
FTQC_BFS_DENSITY_THRESHOLD=0.4 "$BIN" --bench_path data/config/bfs_thr_040.json

echo "=== soglia 0.45 (bfs_thr_045) ==="
FTQC_BFS_DENSITY_THRESHOLD=0.45 "$BIN" --bench_path data/config/bfs_thr_045.json

echo "=== soglia 0.5 (bfs_thr_050) ==="
FTQC_BFS_DENSITY_THRESHOLD=0.5 "$BIN" --bench_path data/config/bfs_thr_050.json

echo "=== soglia 0.55 (bfs_thr_055) ==="
FTQC_BFS_DENSITY_THRESHOLD=0.55 "$BIN" --bench_path data/config/bfs_thr_055.json

echo "=== soglia 0.65 (bfs_thr_065) ==="
FTQC_BFS_DENSITY_THRESHOLD=0.65 "$BIN" --bench_path data/config/bfs_thr_065.json

echo "=== soglia 1.0 (bfs_thr_bfs) ==="
FTQC_BFS_DENSITY_THRESHOLD=1.0 "$BIN" --bench_path data/config/bfs_thr_bfs.json
