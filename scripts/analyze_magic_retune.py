#!/usr/bin/env python3
"""Analyze the BFS-regime MAGIC re-tune suite (magic_retune_{strat}_{geom}).

Goal: under the BFS mapping order (gated binary, density<0.40), find the optimal
MAGIC_HIGH per border, decide whether MAGIC_LOW now matters (historically inert
for coarse), and confirm the magic optimum is robust to cnot_high/mapped.

Robust to metric-saturation noise (cf. analyze_bfs_retune): normalise each
control group to its own minimum and AVERAGE the excess non_routed per value.
The value minimising mean-excess is the robust optimum; curve flatness says
whether the knob matters. Pairing controls confounds (circuit, d, cnot, mapped,
the other magic knob) so we isolate one axis at a time.
"""
import csv, sys
from collections import defaultdict

RESULTS = "data/results"

def load(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            if r.get("status") != "success":
                continue
            nr = r.get("non_routed_layer_pct")
            if nr in ("", None):
                continue
            try:
                r["_nr"] = float(nr)
                r["_d"]  = int(r["graph_x"])
                r["_mh"] = float(r["magic_high"])
                r["_ml"] = float(r["magic_low"])
                r["_b"]  = float(r["border_distance_percentage"])
                r["_ch"] = float(r["cnot_high"])
                r["_mp"] = float(r["mapped_gaussian_weight"])
            except (ValueError, KeyError):
                continue
            rows.append(r)
    return rows

def robust_opt(rows, axis, control_keys):
    """Mean-excess optimum of `axis` controlling for `control_keys`.
    Returns (sorted_values, mean_excess_dict, best_value, n_groups)."""
    grp = defaultdict(lambda: defaultdict(list))
    for r in rows:
        ck = tuple(r[k] for k in control_keys)
        grp[ck][r[axis]].append(r["_nr"])
    excess = defaultdict(list)
    n = 0
    for ck, vmap in grp.items():
        means = {v: sum(x)/len(x) for v, x in vmap.items()}
        if len(means) < 2:
            continue
        gmin = min(means.values())
        for v, m in means.items():
            excess[v].append(m - gmin)
        n += 1
    me = {v: sum(x)/len(x) for v, x in excess.items()}
    if not me:
        return [], {}, None, 0
    vals = sorted(me)
    return vals, me, min(me, key=me.get), n

def fmt(vals, me, best):
    return "  ".join(f"{v:g}:{me[v]:.2f}" + ("*" if v == best else "") for v in vals)

def paired_winrate(rows, axis, a, b, control_keys):
    """Fraction of control groups where axis=a beats axis=b (lower non_routed),
    plus mean delta (a-b). Pairs on identical control_keys."""
    grp = defaultdict(dict)
    for r in rows:
        if r[axis] in (a, b):
            ck = tuple(r[k] for k in control_keys)
            grp[ck].setdefault(r[axis], []).append(r["_nr"])
    wins = ties = losses = 0
    deltas = []
    for ck, vm in grp.items():
        if a not in vm or b not in vm:
            continue
        ma = sum(vm[a])/len(vm[a]); mb = sum(vm[b])/len(vm[b])
        deltas.append(ma - mb)
        if ma < mb - 1e-9: wins += 1
        elif ma > mb + 1e-9: losses += 1
        else: ties += 1
    tot = wins + ties + losses
    md = sum(deltas)/len(deltas) if deltas else 0.0
    return wins, ties, losses, tot, md

def analyze(strat, geom):
    path = f"{RESULTS}/magic_retune_{strat}_{geom}_runs.csv"
    rows = load(path)
    print(f"\n{'='*72}\n  {strat}/{geom}   (n_success={len(rows)})\n{'='*72}")

    borders = sorted(set(r["_b"] for r in rows))
    mls     = sorted(set(r["_ml"] for r in rows))
    mhs     = sorted(set(r["_mh"] for r in rows))

    # --- MAGIC_HIGH optimum per border (control: circuit,d,cnot,mapped,magic_low) ---
    print("\n  MAGIC_HIGH robust optimum per border")
    print("  (control = circuit,d,cnot_high,mapped,magic_low ; *=best, value=mean-excess pp)")
    ck_h = ("circuit", "_d", "_ch", "_mp", "_ml")
    best_by_b = {}
    for b in borders:
        sub = [r for r in rows if r["_b"] == b]
        vals, me, best, n = robust_opt(sub, "_mh", ck_h)
        best_by_b[b] = best
        print(f"    b={b:>4g} (groups={n:>4})  best={best:g}")
        print(f"               {fmt(vals, me, best)}")

    # --- MAGIC_LOW: does it matter? per border (control: circuit,d,cnot,mapped,magic_high) ---
    print("\n  MAGIC_LOW robust optimum per border")
    print("  (control = circuit,d,cnot_high,mapped,magic_high)")
    ck_l = ("circuit", "_d", "_ch", "_mp", "_mh")
    for b in borders:
        sub = [r for r in rows if r["_b"] == b]
        vals, me, best, n = robust_opt(sub, "_ml", ck_l)
        spread = (max(me.values()) - min(me.values())) if me else 0.0
        flag = "INERT" if spread < 0.10 else ("weak" if spread < 0.30 else "MATTERS")
        print(f"    b={b:>4g} best={best:g}  spread={spread:.2f}pp [{flag}]   {fmt(vals, me, best)}")

    # --- robustness of MAGIC_HIGH optimum to cnot/mapped: optimum within each (cnot,mapped) cell ---
    print("\n  MAGIC_HIGH optimum stability across cnot_high x mapped (at the best border)")
    bb = max(borders, key=lambda b: 1 if best_by_b[b] == max(best_by_b.values()) else 0) \
         if geom == "cube" else borders[0]
    # pick the border with the most decisive (largest) magic_high optimum for the stability probe
    bb = max(best_by_b, key=lambda b: best_by_b[b])
    sub = [r for r in rows if r["_b"] == bb]
    chs = sorted(set(r["_ch"] for r in sub)); mps = sorted(set(r["_mp"] for r in sub))
    print(f"    border={bb:g}: best magic_high per (cnot_high,mapped) cell")
    for ch in chs:
        line = []
        for mp in mps:
            cell = [r for r in sub if r["_ch"] == ch and r["_mp"] == mp]
            vals, me, best, n = robust_opt(cell, "_mh", ("circuit", "_d", "_ml"))
            line.append(f"mp{mp:g}:mh*={best:g}" if best is not None else f"mp{mp:g}:--")
        print(f"      cnot={ch:<4g} " + "  ".join(line))

    return best_by_b, mhs, borders

def main():
    summary = {}
    for strat in ("coarse", "fine"):
        for geom in ("cube", "noncube"):
            best_by_b, mhs, borders = analyze(strat, geom)
            summary[(strat, geom)] = best_by_b
    print(f"\n\n{'#'*72}\n  SUMMARY: best MAGIC_HIGH by border (BFS regime)\n{'#'*72}")
    hdr = "  {:<16}".format("regime") + "".join(f"b={b:<6g}" for b in sorted(
        next(iter(summary.values())).keys()))
    print(hdr)
    for (strat, geom), bb in summary.items():
        row = "  {:<16}".format(f"{strat}/{geom}")
        for b in sorted(bb):
            row += f"{bb[b]:<8g}"
        print(row)

if __name__ == "__main__":
    main()
