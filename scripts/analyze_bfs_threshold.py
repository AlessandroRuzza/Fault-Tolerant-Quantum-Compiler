#!/usr/bin/env python3
"""Post-hoc analysis of the density-gated CNOT-BFS sweep.

Inputs: two CSVs from config/cnot_retune_broad_density.json run at the two
extremes (always-BFS and always-heap, via FTQC_BFS_DENSITY_THRESHOLD), plus a
density map (circuit -> CNOT-graph density, from scripts/measure_cnot_density.sh).

For each candidate threshold T, the gated result of a circuit = its BFS best-non_routed
if density(circuit) < T else its heap best-non_routed. We sweep T and report the
threshold minimising aggregate non_routed, and the best CNOT_HIGH/LOW per regime.

Usage: analyze_bfs_threshold.py broad_BFS.csv broad_heap.csv
       (edit DENSITY below or pass a third arg pointing to a 'circuit density' file)
"""
import csv, sys
from collections import defaultdict

# Measured densities (scripts/measure_cnot_density.sh). Update if circuits change.
DENSITY = {
    "synth_n50_d020_mix000_t030_hf000_hm001_r2_s0": 0.20,
    "synth_n50_d020_mix100_t030_hf000_hm001_r2_s0": 0.20,
    "synth_n50_d030_mix050_t030_hf000_hm001_r2_s0": 0.30,
    "synth_n50_d040_mix000_t030_hf000_hm001_r2_s0": 0.40,
    "synth_n50_d040_mix100_t030_hf000_hm001_r2_s0": 0.40,
    "synth_n100_d020_mix050_t030_hf000_hm001_r2_s0": 0.20,
    "synth_n100_d040_mix050_t030_hf000_hm001_r2_s0": 0.40,
    "synth_n100_d040_mix100_t030_hf000_hm001_r2_s1": 0.40,
    "graphstate_n100": 0.020, "adder_n28": 0.103, "bwt_n21": 0.271, "bwt_n37": 0.066,
    "qft_n100": 0.362, "qaoa_n50": 0.479, "qaoa_n64": 0.486, "qaoa_n100": 0.492,
    "qft_n64": 0.531, "randomcircuit_n50": 0.979, "randomcircuit_n100": 0.966,
}

def load(path):
    # circuit -> list of (ch, cl, non_routed)
    d = defaultdict(list)
    with open(path) as f:
        for r in csv.DictReader(f):
            v = r["non_routed_layer_pct"]
            if v in ("", None):
                continue
            d[r["circuit"]].append((float(r["cnot_high"]), float(r["cnot_low"]), float(v)))
    return d

def best_nr(rows):
    return min(v for _, _, v in rows) if rows else None

def best_combo(rows):
    return min(rows, key=lambda t: t[2]) if rows else None

def main():
    bfs_csv, heap_csv = sys.argv[1], sys.argv[2]
    BFS, HEAP = load(bfs_csv), load(heap_csv)
    circuits = [c for c in DENSITY if c in BFS and c in HEAP and BFS[c] and HEAP[c]]
    missing = [c for c in DENSITY if c not in circuits]
    if missing:
        print("WARN: no/empty data for:", ", ".join(missing))

    bfs_best = {c: best_nr(BFS[c]) for c in circuits}
    heap_best = {c: best_nr(HEAP[c]) for c in circuits}

    print(f"\n{'circuit':<46}{'dens':>6}{'BFS':>8}{'heap':>8}{'Δ(B-h)':>8}")
    print("-" * 76)
    for c in sorted(circuits, key=lambda x: DENSITY[x]):
        d = BFS_b = bfs_best[c]; h = heap_best[c]
        print(f"{c:<46}{DENSITY[c]:>6.2f}{bfs_best[c]:>8.2f}{heap_best[c]:>8.2f}{bfs_best[c]-heap_best[c]:>+8.2f}")

    # Sweep threshold
    print("\n=== aggregate non_routed vs threshold (gated = BFS if dens<T else heap) ===")
    cand_T = [0.0, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.42, 0.45, 0.48, 0.50, 0.55, 0.60, 1.01]
    rows = []
    for T in cand_T:
        agg = sum(bfs_best[c] if DENSITY[c] < T else heap_best[c] for c in circuits)
        rows.append((T, agg))
    base_heap = sum(heap_best[c] for c in circuits)  # T=0 -> all heap (= main baseline)
    best = min(rows, key=lambda x: x[1])
    for T, agg in rows:
        mark = "  <== best" if (T, agg) == best else ""
        print(f"  T={T:<5}  aggregate non_routed = {agg:8.2f}  (Δ vs all-heap {agg-base_heap:+.2f}){mark}")
    print(f"\nOptimal threshold ~ {best[0]} (aggregate {best[1]:.2f}, improves all-heap by {best[1]-base_heap:+.2f} pp)")

    # Best CNOT combo per regime, using the optimal threshold
    Topt = best[0]
    print(f"\n=== best CNOT_HIGH/LOW per circuit (at chosen order, T={Topt}) ===")
    print(f"{'circuit':<46}{'order':>6}{'CH':>6}{'CL':>5}{'nr':>8}")
    print("-" * 71)
    for c in sorted(circuits, key=lambda x: DENSITY[x]):
        use_bfs = DENSITY[c] < Topt
        src = BFS if use_bfs else HEAP
        ch, cl, nr = best_combo(src[c])
        print(f"{c:<46}{'BFS' if use_bfs else 'heap':>6}{ch:>6.1f}{cl:>5.1f}{nr:>8.2f}")

if __name__ == "__main__":
    main()
