#!/usr/bin/env python3
"""Throwaway: generate several WISQ-comparison figure candidates from the
connectivity + packing same-grid CSV, so we can pick a replacement for the
ugly log-log diagonal scatter (Fig. 4)."""
from __future__ import annotations
import csv, os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
CSV = ROOT / "data/results/single_config/wisqmin_connectivity_packing.csv"
OUT = ROOT / "results/all_circuits_8/_fig_candidates"
OUT.mkdir(parents=True, exist_ok=True)

WIN = "#2E7D32"   # green
TIE = "#9E9E9E"   # grey
LOSS = "#C62828"  # red

def family(name: str) -> str:
    base = name.split("_n")[0]
    for tok in ("_transpiled",):
        base = base.replace(tok, "")
    return base

rows = []
with CSV.open(newline="") as f:
    for r in csv.DictReader(f):
        r["my_status"] = r["my_status"].strip()
        r["wisq_status"] = r["wisq_status"].strip()
        rows.append(r)

# both-complete records with a valid ratio
both = []
wisq_timeouts = []
for r in rows:
    if r["my_status"] != "success":
        continue
    if r["wisq_status"] != "success":
        wisq_timeouts.append(r)
        continue
    w = float(r["wisq_routing_steps"]); m = float(r["my_routing_steps"])
    if w <= 0 or m <= 0:
        continue
    both.append((r["circuit"], m, w, w / m))  # ratio>1 => we win (fewer steps)

n = len(both)
win = sum(1 for _, m, w, _ in both if m < w)
tie = sum(1 for _, m, w, _ in both if m == w)
loss = sum(1 for _, m, w, _ in both if m > w)
print(f"both={n} win={win} tie={tie} loss={loss} wisq_timeouts={len(wisq_timeouts)}")

# ---------------------------------------------------------------- Fig 1: diverging sorted ratio bars
def fig_ratio_bars():
    data = sorted(both, key=lambda t: t[3])  # ascending ratio: losses first
    ratios = np.array([t[3] for t in data])
    logr = np.log10(ratios)
    colors = [WIN if r > 1 else (TIE if r == 1 else LOSS) for r in ratios]
    fig, ax = plt.subplots(figsize=(4.0, 3.4))
    ax.bar(np.arange(len(data)), logr, width=1.0, color=colors, linewidth=0)
    ax.axhline(0, color="#212121", linewidth=0.8)
    # y ticks as multiplicative factors
    ymax = np.ceil(logr.max()); ymin = np.floor(logr.min())
    ticks = np.arange(ymin, ymax + 1)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{10**t:g}×" if t >= 0 else f"{10**t:.2g}×" for t in ticks])
    ax.set_xlim(-1, len(data))
    ax.set_xlabel("circuits (sorted by ratio)")
    ax.set_ylabel("WISQ steps / our steps")
    ax.set_title("Per-circuit routing-step ratio vs WISQ", fontsize=10)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=WIN, label=f"we win  ({win})"),
                       Patch(color=TIE, label=f"tie  ({tie})"),
                       Patch(color=LOSS, label=f"we lose  ({loss})")],
              loc="upper left", fontsize=8, frameon=False)
    ax.grid(True, axis="y", linestyle=":", alpha=0.3)
    ax.text(0.98, 0.03, f"+{len(wisq_timeouts)} WISQ timeouts\n(extra wins, off-scale)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7,
            style="italic", color="#555")
    fig.tight_layout(); fig.savefig(OUT / "1_ratio_bars.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- Fig 2: win-rate vs wall-clock budget
def fig_winrate_budget():
    budgets = [12000, 3600, 1800, 900, 600, 300, 60]
    labels = ["12000", "3600", "1800", "900", "600", "300", "60"]
    total = len(rows)
    vic_rate = []
    for B in budgets:
        vic = 0
        for r in rows:
            my_fin = r["my_status"] == "success" and float(r["my_duration_s"]) <= B
            wisq_fin = r["wisq_status"] == "success" and float(r["wisq_duration_s"]) <= B
            if my_fin and not wisq_fin:
                vic += 1
            elif my_fin and wisq_fin:
                m = float(r["my_routing_steps"]); w = float(r["wisq_routing_steps"])
                if m < w:
                    vic += 1
                elif m == w and float(r["my_duration_s"]) < float(r["wisq_duration_s"]):
                    vic += 1
        vic_rate.append(100 * vic / total)
    fig, ax = plt.subplots(figsize=(4.0, 3.4))
    x = np.arange(len(budgets))
    ax.plot(x, vic_rate, "-o", color="#1565C0", linewidth=1.8, markersize=6)
    for xi, v in zip(x, vic_rate):
        ax.annotate(f"{v:.0f}%", (xi, v), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlabel("wall-clock budget per circuit (s)  → tighter")
    ax.set_ylabel("our win-rate (% of 256)")
    ax.set_ylim(min(vic_rate) - 8, 100)
    ax.set_title("Win-rate vs WISQ as the time budget tightens", fontsize=10)
    ax.grid(True, linestyle=":", alpha=0.35)
    fig.tight_layout(); fig.savefig(OUT / "2_winrate_budget.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- Fig 3: performance profile (ECDF of ratio)
def fig_perf_profile():
    ratios = np.sort(np.array([t[3] for t in both]))
    y = np.arange(1, len(ratios) + 1) / len(ratios)
    # among the step-ties (ratio == 1), how many are also faster on wall-clock time
    tie_n = tie_time_win = 0
    for name, m, w, _ratio in [(t[0], t[1], t[2], t[3]) for t in both]:
        if m == w:
            tie_n += 1
    for r in csv.DictReader(CSV.open(newline="")):
        if r["my_status"].strip() != "success" or r["wisq_status"].strip() != "success":
            continue
        w = float(r["wisq_routing_steps"]); m = float(r["my_routing_steps"])
        if w <= 0 or m <= 0 or m != w:
            continue
        if float(r["my_duration_s"]) < float(r["wisq_duration_s"]):
            tie_time_win += 1
    tie_time_pct = 100 * tie_time_win / tie_n if tie_n else 0.0

    fig, ax = plt.subplots(figsize=(4.0, 3.4))
    ax.step(ratios, y, where="post", color="#1565C0", linewidth=1.8)
    ax.axvline(1.0, color=TIE, linestyle="--", linewidth=1.0)
    frac_le = np.mean(ratios >= 1.0)  # ratio>=1 => we're at least as good
    ax.axhline(1 - frac_le, color="#C62828", linestyle=":", linewidth=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("routing-step ratio  (WISQ / ours)")
    ax.set_ylabel("fraction of circuits ≤ ratio")
    ax.set_title("Performance profile vs WISQ", fontsize=10)
    ax.grid(True, which="both", linestyle=":", alpha=0.3)
    tie_share = 100 * tie_n / len(ratios)
    ink = "#263238"
    # in the empty region to the right of the ratio=1 line, two parallel notes
    ax.text(1.15, 0.60,
            f"{tie_share:.0f}% of circuits tie on steps:\n"
            f"{tie_time_pct:.0f}% finish faster.",
            transform=ax.get_xaxis_transform(), fontsize=7.5, color=ink,
            va="center", ha="left", linespacing=1.4)
    ax.text(1.15, 0.38,
            f"We match or outperform\n"
            f"WISQ on {frac_le*100:.0f}% of circuits.",
            transform=ax.get_xaxis_transform(), fontsize=7.5, color=ink,
            va="center", ha="left", linespacing=1.4)
    fig.tight_layout(); fig.savefig(OUT / "3_perf_profile.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- Fig 3.2: same profile, axes swapped
def fig_perf_profile_swapped():
    ratios = np.sort(np.array([t[3] for t in both]))
    frac = np.arange(1, len(ratios) + 1) / len(ratios)

    tie_n = int(np.sum([1 for t in both if t[1] == t[2]]))
    tie_time_win = 0
    for r in csv.DictReader(CSV.open(newline="")):
        if r["my_status"].strip() != "success" or r["wisq_status"].strip() != "success":
            continue
        w = float(r["wisq_routing_steps"]); m = float(r["my_routing_steps"])
        if w <= 0 or m <= 0 or m != w:
            continue
        if float(r["my_duration_s"]) < float(r["wisq_duration_s"]):
            tie_time_win += 1
    tie_time_pct = 100 * tie_time_win / tie_n if tie_n else 0.0
    tie_share = 100 * tie_n / len(ratios)

    fig, ax = plt.subplots(figsize=(4.0, 3.4))
    ax.step(frac, ratios, where="pre", color="#1565C0", linewidth=1.8)
    ax.axhline(1.0, color=TIE, linestyle="--", linewidth=1.0)
    frac_ge = float(np.mean(ratios >= 1.0))
    ax.axvline(1 - frac_ge, color="#C62828", linestyle=":", linewidth=0.8)
    ax.set_yscale("log")
    ax.set_xlim(0, 1)
    ax.set_xlabel("fraction of circuits ≤ ratio")
    ax.set_ylabel("routing-step ratio  (WISQ / ours)")
    ax.set_title("Performance profile vs WISQ", fontsize=10)
    ax.grid(True, which="both", linestyle=":", alpha=0.3)
    ax.text(0.62, 0.55, f"{frac_ge*100:.0f}% of circuits:\nwe ≤ WISQ steps",
            transform=ax.get_yaxis_transform(), fontsize=8, color="#2E7D32",
            va="top", ha="center")
    # label above the ratio=1 plateau (the step-ties): time-win share
    ax.text(0.30, 1.15, f"step-ties ({tie_share:.0f}% of circuits):\n{tie_time_pct:.0f}% also faster\non wall-clock time",
            transform=ax.get_yaxis_transform(), fontsize=7.5, color="#00695C",
            va="bottom", ha="left")
    fig.tight_layout(); fig.savefig(OUT / "3.2_perf_profile_swapped.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- Fig 4: per-family win/tie/loss stacked bars
def fig_family_winloss():
    fam = {}
    for name, m, w, _ in both:
        f = family(name)
        d = fam.setdefault(f, [0, 0, 0])  # win, tie, loss
        if m < w: d[0] += 1
        elif m == w: d[1] += 1
        else: d[2] += 1
    # keep families with >=3 circuits, sort by win-share then n
    items = [(f, d) for f, d in fam.items() if sum(d) >= 3]
    items.sort(key=lambda kv: (kv[1][0] - kv[1][2]) / sum(kv[1]))
    names = [f for f, _ in items]
    wins = np.array([d[0] for _, d in items])
    ties = np.array([d[1] for _, d in items])
    loss = np.array([d[2] for _, d in items])
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(4.2, max(3.4, 0.32 * len(names))))
    ax.barh(y, wins, color=WIN, label="win")
    ax.barh(y, ties, left=wins, color=TIE, label="tie")
    ax.barh(y, loss, left=wins + ties, color=LOSS, label="lose")
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=7)
    ax.set_xlabel("circuits (both compilers complete)")
    ax.set_title("Routing-step outcome vs WISQ, by family", fontsize=10)
    ax.legend(loc="lower right", fontsize=8, frameon=False, ncol=3)
    ax.margins(y=0.01)
    fig.tight_layout(); fig.savefig(OUT / "4_family_winloss.png", dpi=170); plt.close(fig)

fig_winrate_budget()
fig_perf_profile()
fig_perf_profile_swapped()
print("saved to", OUT)
