#!/usr/bin/env python3
"""
Generate synthetic OpenQASM 2.0 circuits with *controlled* interaction-graph
properties, to study which circuit characteristics make the gaussian mapping
outperform random.

We build the CNOT interaction graph with a Stochastic-Block-Model so that the
two axes that actually correlated with gaussian's advantage in the real data
can be swept independently:

  - cnot_interaction_density   <-  --density   (fraction of qubit pairs used)
  - cnot_graph_modularity      <-  --mixing    (0 = clustered/high modularity,
                                                1 = random/low modularity)

Plus a controlled magic-state load:

  - t_count_ratio              <-  --t-ratio   (fraction of routable gates = T)

Each chosen edge (i,j) emits `--reps` cx gates; T gates are sprinkled on random
qubits to hit --t-ratio; the whole gate multiset is shuffled (seeded) and
written out. A manifest CSV records the intended parameters of every file.

Usage examples:
  # single circuit
  python3 scripts/generate_synthetic_circuits.py \
      --n 100 --density 0.3 --mixing 0.2 --t-ratio 0.3 --seed 0

  # a grid (cartesian product of the list-valued options)
  python3 scripts/generate_synthetic_circuits.py \
      --n 100 200 --density 0.1 0.5 --mixing 0.0 1.0 --t-ratio 0.0 0.3 --seeds 3
"""

import argparse
import itertools
import math
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = PROJECT_ROOT / "qasms"
DEFAULT_MANIFEST = PROJECT_ROOT / "benchmarks" / "results" / "synthetic_manifest.csv"


def communities_for(n: int, num_communities: int) -> list:
    """Assign each qubit to one of `num_communities` contiguous blocks."""
    k = max(1, num_communities)
    csize = math.ceil(n / k)
    return [min(q // csize, k - 1) for q in range(n)]


def build_edges(n, density, mixing, num_communities, rng):
    """Pick CNOT edges via an SBM: `density` sets how many of the n(n-1)/2 pairs
    become edges; `mixing` sets the fraction that cross community boundaries
    (low mixing => strong communities => high modularity)."""
    comm = communities_for(n, num_communities)
    all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    intra = [(i, j) for (i, j) in all_pairs if comm[i] == comm[j]]
    inter = [(i, j) for (i, j) in all_pairs if comm[i] != comm[j]]

    target_E = int(round(density * len(all_pairs)))
    target_E = max(1, min(target_E, len(all_pairs)))

    n_inter = min(len(inter), int(round(mixing * target_E)))
    n_intra = min(len(intra), target_E - n_inter)
    # If one bucket is short, top up from the other to still hit target_E.
    deficit = target_E - (n_intra + n_inter)
    if deficit > 0:
        if n_intra < len(intra):
            n_intra = min(len(intra), n_intra + deficit)
        elif n_inter < len(inter):
            n_inter = min(len(inter), n_inter + deficit)

    rng.shuffle(intra)
    rng.shuffle(inter)
    edges = intra[:n_intra] + inter[:n_inter]
    rng.shuffle(edges)
    return edges


def generate_one(n, density, mixing, t_ratio, reps, num_communities, seed,
                 out_dir, prefix, hotspot_frac=0.0, hotspot_mult=1):
    rng = random.Random(seed)
    edges = build_edges(n, density, mixing, num_communities, rng)

    # Heterogeneous edge weights => controls cnot_pair_rep_gini.
    # A `hotspot_frac` of the edges are repeated `reps*hotspot_mult` times, the
    # rest `reps` times. hotspot_frac=0 (or mult=1) => uniform => gini ~ 0.
    n_hot = int(round(hotspot_frac * len(edges)))
    ops = []
    for k, (i, j) in enumerate(edges):
        edge_reps = reps * hotspot_mult if k < n_hot else reps
        for _ in range(edge_reps):
            ops.append(("cx", i, j))
    n_cnot = len(ops)

    n_t = 0
    if 0.0 < t_ratio < 1.0 and n_cnot > 0:
        n_t = int(round(n_cnot * t_ratio / (1.0 - t_ratio)))
    for _ in range(n_t):
        ops.append(("t", rng.randrange(n)))

    rng.shuffle(ops)

    name = (f"{prefix}_n{n}_d{int(round(density*100)):03d}"
            f"_mix{int(round(mixing*100)):03d}_t{int(round(t_ratio*100)):03d}"
            f"_hf{int(round(hotspot_frac*100)):03d}_hm{hotspot_mult:03d}"
            f"_r{reps}_s{seed}")
    lines = ["OPENQASM 2.0;", 'include "qelib1.inc";', "",
             f"qreg q[{n}];", f"creg c[{n}];", ""]
    for op in ops:
        if op[0] == "cx":
            lines.append(f"cx q[{op[1]}],q[{op[2]}];")
        else:
            lines.append(f"t q[{op[1]}];")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{name}.qasm").write_text("\n".join(lines) + "\n")

    return {
        "circuit": name, "n": n, "density": density, "mixing": mixing,
        "t_ratio": t_ratio, "reps": reps, "num_communities": num_communities,
        "hotspot_frac": hotspot_frac, "hotspot_mult": hotspot_mult,
        "seed": seed, "num_edges": len(edges), "num_cnot": n_cnot, "num_t": n_t,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, nargs="+", required=True, help="qubit count(s)")
    p.add_argument("--density", type=float, nargs="+", default=[0.3],
                   help="edge density / cnot_interaction_density target(s)")
    p.add_argument("--mixing", type=float, nargs="+", default=[0.5],
                   help="inter-community edge fraction(s); 0=clustered, 1=random")
    p.add_argument("--t-ratio", type=float, nargs="+", default=[0.0],
                   help="target t_count_ratio (0 = pure CNOT)")
    p.add_argument("--reps", type=int, nargs="+", default=[2],
                   help="base cx repetitions per edge")
    p.add_argument("--hotspot-frac", type=float, nargs="+", default=[0.0],
                   help="fraction of edges that are 'hotspots' repeated hotspot-mult x more "
                        "(controls cnot_pair_rep_gini; 0 = uniform = gini~0)")
    p.add_argument("--hotspot-mult", type=int, nargs="+", default=[1],
                   help="repetition multiplier for hotspot edges (higher = higher gini)")
    p.add_argument("--num-communities", type=int, default=4,
                   help="number of community blocks for the SBM (default 4). "
                        "Note: max achievable modularity needs density <= ~1/num_communities.")
    p.add_argument("--max-cnot", type=int, default=30000,
                   help="skip any (n,density,reps) combo whose CNOT count exceeds "
                        "this cap, to keep routing feasible at large n (default 30000)")
    p.add_argument("--seeds", type=int, default=1,
                   help="number of seeds per parameter combination (0..seeds-1)")
    p.add_argument("--seed", type=int, nargs="+", default=None,
                   help="explicit seed list (overrides --seeds)")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--prefix", default="synth")
    args = p.parse_args()

    seeds = args.seed if args.seed is not None else list(range(args.seeds))

    rows = []
    skipped = 0
    for n, d, mix, tr, reps, hf, hm, s in itertools.product(
            args.n, args.density, args.mixing, args.t_ratio, args.reps,
            args.hotspot_frac, args.hotspot_mult, seeds):
        # CNOT count: non-hotspot edges * reps + hotspot edges * reps*hm.
        n_edges = int(round(d * n * (n - 1) / 2))
        n_hot = int(round(hf * n_edges))
        est_cnot = (n_edges - n_hot) * reps + n_hot * reps * hm
        if est_cnot > args.max_cnot:
            skipped += 1
            continue
        rows.append(generate_one(n, d, mix, tr, reps, args.num_communities, s,
                                 args.out_dir, args.prefix,
                                 hotspot_frac=hf, hotspot_mult=hm))

    if not rows:
        print(f"No circuits generated (all {skipped} combos exceeded --max-cnot={args.max_cnot}).")
        return

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    import csv
    existing = {}
    if args.manifest.exists():
        with open(args.manifest) as f:
            for r in csv.DictReader(f):
                existing[r["circuit"]] = r
    for r in rows:
        existing[r["circuit"]] = {k: str(v) for k, v in r.items()}
    with open(args.manifest, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in existing.values():
            w.writerow(r)

    print(f"Generated {len(rows)} circuit(s) into {args.out_dir} "
          f"({skipped} skipped over --max-cnot={args.max_cnot})")
    print(f"Manifest: {args.manifest}")


if __name__ == "__main__":
    main()
