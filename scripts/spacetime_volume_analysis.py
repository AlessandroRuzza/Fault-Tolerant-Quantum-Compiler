#!/usr/bin/env python3
"""Space-time volume comparison: our Gaussian compiler vs WISQ.

V = grid_x * grid_y * routing_steps, per litinski2019game (1 routing step
~ one lattice-surgery duration). Uses existing benchmark CSVs only; runs
no benchmarks.

Exclusion is symmetric: a row where either side has an error/timeout or a
missing grid/steps value is dropped from the comparison (counted per side).
Rows with safe_passage_fallback set are reported separately, never mixed in.

Caveat (stated, not resolved here): magic-state budgets differ between our
config (number_of_magic_states=-1, auto center_circle placement) and WISQ's
built-in arch. Factory-tile counts are NOT derivable from these CSVs
(wisq_n_slots counts algorithm-qubit slots, not factory tiles), so volumes
compare total grid area including whatever magic-state area each tool used.
"""

import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "data" / "results"

MAIN_CSV = RESULTS / "connectivity_vs_wisq.csv"
MINUS3_CSV = RESULTS / "connectivity_vs_wisq_minus3.csv"
MINUS5_CSV = RESULTS / "connectivity_vs_wisq_minus5.csv"

INT_FIELDS = ("my_x", "my_y", "my_routing_steps", "wisq_x", "wisq_y", "wisq_routing_steps")


def family(circuit):
    m = re.match(r"(.*?)_n\d+", circuit)
    return m.group(1) if m else circuit


def to_int(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def load(path):
    """Return (usable_rows, exclusions, fallback_rows)."""
    usable, fallback = [], []
    exclusions = defaultdict(list)  # reason -> [circuit]
    with open(path) as f:
        for r in csv.DictReader(f):
            circ = r["circuit"]
            vals = {k: to_int(r.get(k)) for k in INT_FIELDS}

            my_missing = any(vals[k] is None for k in ("my_x", "my_y", "my_routing_steps"))
            wisq_missing = any(vals[k] is None for k in ("wisq_x", "wisq_y", "wisq_routing_steps"))
            status = (r.get("wisq_status") or "").strip().lower()

            if r.get("safe_passage_fallback", "").strip():
                fallback.append(r)
                continue
            if status != "success":
                reason = f"wisq: status={status or 'missing'}"
                if circ.startswith("factor247"):
                    reason += " (timeout, wisq_duration_s=%s)" % r.get("wisq_duration_s", "?")
                exclusions[reason].append(circ)
                continue
            if wisq_missing:
                exclusions["wisq: missing grid/steps despite success"].append(circ)
                continue
            if my_missing:
                exclusions["ours: missing grid/steps"].append(circ)
                continue

            r.update(vals)
            r["n_qubits_i"] = to_int(r.get("n_qubits"))
            r["my_V"] = vals["my_x"] * vals["my_y"] * vals["my_routing_steps"]
            r["wisq_V"] = vals["wisq_x"] * vals["wisq_y"] * vals["wisq_routing_steps"]
            r["ratio"] = r["wisq_V"] / r["my_V"] if r["my_V"] else float("inf")
            usable.append(r)
    return usable, exclusions, fallback


def geomean(xs):
    xs = [x for x in xs if x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else float("nan")


def wlt(rows):
    w = sum(1 for r in rows if r["ratio"] > 1)
    l = sum(1 for r in rows if r["ratio"] < 1)
    t = len(rows) - w - l
    return w, l, t


def summarize(rows, label):
    print(f"\n### {label}: volume win/loss/tie (win = our V smaller, ratio wisq/ours > 1)")
    w, l, t = wlt(rows)
    print(f"overall: n={len(rows)}  win={w}  loss={l}  tie={t}  "
          f"geomean(wisq_V/our_V)={geomean([r['ratio'] for r in rows]):.4f}")
    fams = defaultdict(list)
    for r in rows:
        fams[family(r["circuit"])].append(r)
    print(f"{'family':<22}{'n':>4}{'win':>5}{'loss':>6}{'tie':>5}{'geomean':>10}")
    for fam in sorted(fams):
        fr = fams[fam]
        fw, fl, ft = wlt(fr)
        print(f"{fam:<22}{len(fr):>4}{fw:>5}{fl:>6}{ft:>5}{geomean([r['ratio'] for r in fr]):>10.4f}")


def analyze(path, tag):
    print("=" * 78)
    print(f"DATASET: {path.name}")
    print("=" * 78)
    rows, exclusions, fallback = load(path)

    n_excl = sum(len(v) for v in exclusions.values())
    print(f"\nusable rows: {len(rows)}   excluded: {n_excl}   fallback (reported separately): {len(fallback)}")
    if rows and "dim_diff_side" in rows[0]:
        dd = defaultdict(list)
        for r in rows:
            dd[r.get("dim_diff_side", "")].append(r["circuit"])
        expected = max(dd, key=lambda k: len(dd[k]))
        print(f"dim_diff_side: expected={expected} on {len(dd[expected])} rows; anomalies:")
        for k, circs in sorted(dd.items()):
            if k != expected:
                print(f"  dim_diff_side={k!r}: {', '.join(sorted(circs))}")
    for reason, circs in sorted(exclusions.items()):
        print(f"  excluded [{reason}]: {len(circs)} -> {', '.join(sorted(circs))}")
    if fallback:
        print("  fallback rows:", ", ".join(sorted(r["circuit"] for r in fallback)))

    out = RESULTS / f"spacetime_volume_per_circuit{tag}.csv"
    with open(out, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["circuit", "n_qubits", "family",
                     "my_x", "my_y", "my_routing_steps", "my_V",
                     "wisq_x", "wisq_y", "wisq_routing_steps", "wisq_V",
                     "ratio_wisqV_over_myV", "wisq_wins_raw_steps"])
        for r in sorted(rows, key=lambda r: (family(r["circuit"]), r["n_qubits_i"] or 0)):
            wr.writerow([r["circuit"], r["n_qubits_i"], family(r["circuit"]),
                         r["my_x"], r["my_y"], r["my_routing_steps"], r["my_V"],
                         r["wisq_x"], r["wisq_y"], r["wisq_routing_steps"], r["wisq_V"],
                         f"{r['ratio']:.4f}",
                         int(r["wisq_routing_steps"] < r["my_routing_steps"])])
    print(f"\nper-circuit table written: {out}")

    summarize(rows, "ALL usable circuits")

    steps_wisq_wins = [r for r in rows if r["wisq_routing_steps"] < r["my_routing_steps"]]
    print(f"\n### circuits where WISQ wins RAW routing steps: {len(steps_wisq_wins)}")
    if steps_wisq_wins:
        flipped = [r for r in steps_wisq_wins if r["ratio"] > 1]
        still_lose = [r for r in steps_wisq_wins if r["ratio"] < 1]
        tie = [r for r in steps_wisq_wins if r["ratio"] == 1]
        print(f"volume outcome on that subset: we WIN {len(flipped)}, we LOSE {len(still_lose)}, tie {len(tie)}")
        print(f"geomean(wisq_V/our_V) on subset: {geomean([r['ratio'] for r in steps_wisq_wins]):.4f}")
        print(f"{'circuit':<26}{'nq':>5}{'mySteps':>9}{'wSteps':>8}{'myGrid':>9}{'wGrid':>8}{'my_V':>12}{'wisq_V':>12}{'ratio':>8}")
        for r in sorted(steps_wisq_wins, key=lambda r: r["ratio"]):
            print(f"{r['circuit']:<26}{r['n_qubits_i'] or 0:>5}{r['my_routing_steps']:>9}{r['wisq_routing_steps']:>8}"
                  f"{str(r['my_x'])+'x'+str(r['my_y']):>9}{str(r['wisq_x'])+'x'+str(r['wisq_y']):>8}"
                  f"{r['my_V']:>12}{r['wisq_V']:>12}{r['ratio']:>8.3f}")
        summarize(steps_wisq_wins, "subset (WISQ wins raw steps)")
    return rows


def verdict(r):
    return "win" if r["ratio"] > 1 else ("loss" if r["ratio"] < 1 else "tie")


def compare_flips(main_rows, other_rows, label):
    print("=" * 78)
    print(f"MAIN vs {label}: verdict flips (circuits usable in both datasets)")
    print("=" * 78)
    other = {r["circuit"]: r for r in other_rows}
    flips = []
    both = 0
    for r in main_rows:
        o = other.get(r["circuit"])
        if not o:
            continue
        both += 1
        v1, v2 = verdict(r), verdict(o)
        if v1 != v2:
            flips.append((r["circuit"], v1, r["ratio"], v2, o["ratio"]))
    dirs = defaultdict(int)
    for _, v1, _, v2, _ in flips:
        dirs[f"{v1}->{v2}"] += 1
    print(f"circuits in both: {both}   flips: {len(flips)}   directions: {dict(dirs)}")
    for c, v1, r1, v2, r2 in sorted(flips):
        print(f"  {c:<26} main={v1} ({r1:.3f})  {label.lower()}={v2} ({r2:.3f})")


def main():
    main_rows = analyze(MAIN_CSV, "")
    minus3_rows = analyze(MINUS3_CSV, "_minus3")
    minus5_rows = analyze(MINUS5_CSV, "_minus5")
    compare_flips(main_rows, minus3_rows, "MINUS-3")
    compare_flips(main_rows, minus5_rows, "MINUS-5")


if __name__ == "__main__":
    main()
