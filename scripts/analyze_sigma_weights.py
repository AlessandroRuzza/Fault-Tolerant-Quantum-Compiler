#!/usr/bin/env python3
"""Analyse the sigma weight-fixing sweep (sigma pinned, weights+border swept).

Per regime (gaussian_strategy + safe_passage_strategy): best-per-circuit over
dimension_offset, mean over circuits, per weight combo
(sigma, cnot_high, mapped, magic_high, magic_low, border). Prints the best combo,
the per-axis marginal (best-of-rest), and the magic_high x border table at the
best (sigma, cnot, mapped, magic_low) — border is the lever for magic_high.

Usage: analyze_sigma_weights.py [path/to/sigma_weights_sweep_runs.csv]
"""
import csv, sys
from collections import defaultdict

DEFAULT = "data/results/sigma_weights_sweep_runs.csv"
csv.field_size_limit(10**7)


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    # regime -> combo -> circuit -> best nr (min over dims)
    agg = defaultdict(lambda: defaultdict(dict))
    circ = defaultdict(set)
    with open(path) as f:
        for r in csv.DictReader(f):
            nr = fnum(r.get("non_routed_layer_pct"))
            if nr is None:
                continue
            reg = (r.get("gaussian_strategy", "?"), r.get("safe_passage_strategy", "?"))
            combo = (fnum(r["gaussian_sigma"]), fnum(r["cnot_high"]),
                     fnum(r["mapped_gaussian_weight"]), fnum(r["magic_high"]),
                     fnum(r["magic_low"]), fnum(r["border_distance_percentage"]))
            d = agg[reg][combo]
            d[r["circuit"]] = min(nr, d.get(r["circuit"], nr))
            circ[reg].add(r["circuit"])

    names = ["sigma", "cnot", "mapped", "magic_high", "magic_low", "border"]
    for reg in sorted(agg):
        n = len(circ[reg])
        means = {c: sum(d.values()) / len(d) for c, d in agg[reg].items() if len(d) == n}
        if not means:
            t = 0.9 * n
            means = {c: sum(d.values()) / len(d) for c, d in agg[reg].items() if len(d) >= t}
        print(f"\n########## {reg[0]}/{reg[1]}  ({n} circuits, {len(means)} full combos) ##########")
        if not means:
            print("  (insufficient circuit coverage)"); continue
        best = min(means, key=means.get)
        print("  BEST: " + "  ".join(f"{k}={v:g}" for k, v in zip(names, best))
              + f"   mean non_routed={means[best]:.3f}")

        for i, label in enumerate(names):
            byv = defaultdict(lambda: 1e9)
            for c, m in means.items():
                byv[c[i]] = min(byv[c[i]], m)
            print(f"   {label:<10} (best-of-rest): "
                  + "  ".join(f"{v:g}:{byv[v]:.2f}" for v in sorted(byv)))

        # magic_high x border table at best (sigma, cnot, mapped, magic_low)
        s, cn, mp, _mh, ml, _b = best
        mags = sorted({c[3] for c in means})
        bords = sorted({c[5] for c in means})
        print(f"   magic_high × border  (at sigma={s:g}, cnot={cn:g}, mapped={mp:g}, magic_low={ml:g}):")
        print("     mh\\border " + "".join(f"{b:>8g}" for b in bords))
        for mh in mags:
            cells = []
            for b in bords:
                k = (s, cn, mp, mh, ml, b)
                cells.append(f"{means[k]:>8.2f}" if k in means else f"{'-':>8}")
            print(f"     {mh:>8g} " + "".join(cells))


if __name__ == "__main__":
    main()
