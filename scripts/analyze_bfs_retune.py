#!/usr/bin/env python3
"""Analyze the BFS-regime re-tuning suite (Part A 1D + Part B 2D).

Robust to the metric-saturation noise: instead of trusting the per-(circuit,d)
argmin (which jumps around when many weight values tie), we normalise each
(circuit,d) group to its own minimum and AVERAGE the excess non_routed across
groups per weight value. The weight minimising the mean excess is the robust
optimum, and the flatness of the curve tells whether the weight matters at all.

Part A: cnotdim -> cnot_high optimum & d-scaling; mappeddim -> mapped optimum.
Part B: 2d -> is the cnot_high optimum independent of mapped (separable)?
"""
import csv, glob, re, sys
from collections import defaultdict

def load(path):
    return [r for r in csv.DictReader(open(path)) if r["status"] == "success"
            and r["non_routed_layer_pct"] not in ("", None)]

def short(c):
    c = re.sub(r"_t030.*", "", c).replace("synth_", "s_")
    return c

def fam(c):
    if c.startswith(("synth_", "s_")): return "synth"
    if c.startswith("qft"): return "qft"
    return "rest"

# ---- Part A: 1D weight optimum, robust ----
def analyze_1d(path, weight_col):
    rows = load(path)
    # group[(circuit,d)][weight] = mean non_routed over safe_passage
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        acc[(r["circuit"], int(r["graph_x"]))][float(r[weight_col])].append(
            float(r["non_routed_layer_pct"]))
    groups = {k: {w: sum(v)/len(v) for w, v in d.items()} for k, d in acc.items()}

    # robust optimum: average (non_routed - group_min) per weight
    excess = defaultdict(list)
    for (c, d), wmap in groups.items():
        gmin = min(wmap.values())
        for w, nr in wmap.items():
            excess[w].append(nr - gmin)
    mean_excess = {w: sum(v)/len(v) for w, v in excess.items()}
    weights = sorted(mean_excess)
    best_w = min(mean_excess, key=mean_excess.get)

    # per-(circuit,d) argmin, for d-scaling test (noisy, used only for trend)
    best_per = {(c, d): min(wmap, key=wmap.get) for (c, d), wmap in groups.items()}
    return weights, mean_excess, best_w, best_per, groups

def fmt_curve(weights, mean_excess, best_w):
    out = []
    for w in weights:
        mark = "*" if w == best_w else " "
        out.append(f"{w:g}:{mean_excess[w]:.2f}{mark}")
    return "  ".join(out)

def dscaling(best_per, weight_label):
    # correlation of argmin-weight with d, per family
    import statistics as st
    byfam = defaultdict(list)
    for (c, d), w in best_per.items():
        byfam[fam(c)].append((d, w))
    print(f"    d-scaling of {weight_label}* (argmin, noisy):")
    for f in ("rest", "synth", "qft"):
        pts = byfam.get(f, [])
        if len(pts) < 3:
            continue
        ds = [p[0] for p in pts]; ws = [p[1] for p in pts]
        try:
            r = st.correlation(ds, ws) if len(set(ds)) > 1 and len(set(ws)) > 1 else 0.0
        except Exception:
            r = 0.0
        wmean = st.mean(ws); wmed = st.median(ws)
        print(f"      {f:<6} n={len(pts):<3} mean={wmean:.2f} median={wmed:.2f} corr(d,{weight_label}*)={r:+.2f}")

def part_a():
    for strat in ("coarse", "fine"):
        for geom in ("cube", "noncube"):
            print(f"\n========== PART A  {strat}/{geom} ==========")
            for axis, col in (("cnot_high", "cnot_high"), ("mapped", "mapped_gaussian_weight")):
                tag = "cnotdim" if axis == "cnot_high" else "mappeddim"
                path = f"benchmarks/results/bfs_retune_{tag}_{strat}_{geom}_runs.csv"
                weights, me, best, best_per, groups = analyze_1d(path, col)
                print(f"  [{axis}]  robust optimum = {best:g}   (mean-excess non_routed per value, *=best)")
                print(f"    {fmt_curve(weights, me, best)}")
                dscaling(best_per, axis)

# ---- Part B: 2D separability ----
def analyze_2d(strat, geom):
    path = f"benchmarks/results/bfs_retune_2d_{strat}_{geom}_runs.csv"
    rows = load(path)
    # per circuit: grid[(ch,mp)] = mean non_routed over (d, safe_passage)
    # To compare across d fairly, normalise per (circuit,d) then average.
    per_cd = defaultdict(lambda: defaultdict(list))
    for r in rows:
        key = (r["circuit"], int(r["graph_x"]))
        per_cd[key][(float(r["cnot_high"]), float(r["mapped_gaussian_weight"]))].append(
            float(r["non_routed_layer_pct"]))
    # normalised excess per circuit over (ch,mp)
    circ_grid = defaultdict(lambda: defaultdict(list))
    for (c, d), g in per_cd.items():
        gg = {k: sum(v)/len(v) for k, v in g.items()}
        gmin = min(gg.values())
        for k, nr in gg.items():
            circ_grid[c][k].append(nr - gmin)
    print(f"\n========== PART B (2D separability)  {strat}/{geom} ==========")
    print(f"  {'circuit':<20}{'joint(ch,mp)':>14}{'best ch | per mp column':>34}")
    sep_ok = 0; total = 0
    for c in sorted(circ_grid):
        grid = {k: sum(v)/len(v) for k, v in circ_grid[c].items()}
        chs = sorted(set(k[0] for k in grid))
        mps = sorted(set(k[1] for k in grid))
        joint = min(grid, key=grid.get)
        # best ch for each mp column
        bestch_per_mp = []
        for mp in mps:
            col = {ch: grid.get((ch, mp), 9e9) for ch in chs}
            bestch_per_mp.append(min(col, key=col.get))
        spread = max(bestch_per_mp) - min(bestch_per_mp)
        separable = spread <= 1.0  # best ch barely moves with mp
        sep_ok += separable; total += 1
        tag = "SEP" if separable else "INTERACT"
        print(f"  {short(c):<20}({joint[0]:g},{joint[1]:g})".ljust(36)
              + f"{tag}  bestch/mp={bestch_per_mp}")
    print(f"  -> separabili: {sep_ok}/{total}")

def part_b():
    for strat in ("coarse", "fine"):
        for geom in ("cube", "noncube"):
            analyze_2d(strat, geom)

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("a", "all"): part_a()
    if what in ("b", "all"): part_b()
