#!/usr/bin/env python3
"""Throwaway: routing steps vs grid growth, one curve per circuit family. Three figures.

x = growth of the grid side relative to the MINIMUM grid, in %  ((side_k - side_0)/side_0).
    side = mean of the resolved width/height (both grow +1 per step, grids are near-square).
y = routing steps, LOG scale — the families span 2 .. 372724 steps.

  0_  two panels: half the families whose steps drop | half of the flat ones.
      Readable, but the two groups CROSS each other and sit far apart — see below.
  1_  one panel, 6 families picked by SEARCH: no pair ever crosses, every pair >= 1.3x
      apart, no vertical gap > 6.5x, >= 3 families that actually drop.
  2_  same search with the constraints relaxed (>= 1.10x apart, gap free): 23 families.

The data has a natural HOLE — nothing sits between 152 and 1320 steps — and the movers
descend THROUGH the flat families (synth 1320 -> 163 lands on bv_n280 = 152). That is what
produces the crossings in 0_ and the 11x gap that no selection can close.

Curves end at different x: each family starts from its own minimum grid, so +1 per side is
a different percentage for each (a 3x4 grid reaches +829%, a 19x19 only +153%). Labels
therefore sit at each curve's own tip, not at a shared right margin.

Source: benchmarks/results/dim_sweep_family_median_min_dims.csv (37 families x 30 dims).
"""
from __future__ import annotations
import csv, os, collections, itertools
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
CSV = ROOT / "benchmarks/results/dim_sweep_family_median_min_dims.csv"
OUTDIR = ROOT / "results/dim_sweep"
OUTDIR.mkdir(parents=True, exist_ok=True)
# Paper figure: vector PDF straight into the paper's figures/ dir, the same way
# plot_paper_perf_profile.py and render_paper_gaussians.py do it.
PAPER_FIG = ROOT / "paper_overleaf/figures/routing_steps_vs_grid_growth.pdf"

# dataviz reference palette, light mode.
SURFACE = "#fcfcfb"
INK, INK2, INK3 = "#0b0b0b", "#52514e", "#8b8a85"
CAT = ["#2a78d6", "#008300", "#e87ba4", "#eda100", "#1baf7a", "#eb6834", "#4a3aa7"]
FLATGREY = "#9a9993"  # neutral reference group; identity comes from the end label
# Sequential blue ramp (ordinal: no lighter than step 250 on a light surface).
BLUE = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf",
        "#1c5cab", "#184f95", "#104281", "#0d366b"]

SELECTED_1 = ["factor247_n15", "hhl_n10", "bwt_n37",
              "randomcircuit_n100", "vqe_two_local_n80", "qft_n80"]


def load():
    per = collections.defaultdict(list)
    for r in csv.DictReader(CSV.open()):
        if r["status"] != "success":
            continue
        side = (int(r["my_x"]) + int(r["my_y"])) / 2
        per[r["circuit"]].append((int(r["dim_index"]), side, int(r["my_routing_steps"])))
    out = {}
    for c, v in per.items():
        v.sort()
        s0 = v[0][1]
        out[c] = (np.array([(s - s0) / s0 * 100 for _, s, _ in v]),
                  np.array([st for _, _, st in v], float))
    return out


def short(c):
    return c.replace("_t030_hf000_hm001_r2_s0", "")


def ramp(n):
    idx = np.linspace(0, len(BLUE) - 1, n).round().astype(int)
    return [BLUE[i] for i in idx]


def separation(D, a, b):
    """Min vertical ratio over the common x range; None if the curves cross."""
    xa, ya = D[a]
    xb, yb = D[b]
    xs = np.linspace(0, min(xa[-1], xb[-1]), 300)
    A, B = np.interp(xs, xa, ya), np.interp(xs, xb, yb)
    r = A / B
    if r.min() < 1 < r.max():
        return None
    return (r if r.min() > 1 else 1 / r).min()


def greedy_set(D, minsep, xlo, xhi):
    """Largest non-crossing set (greedy, tallest first) with every pair >= minsep apart."""
    cand = sorted((c for c, v in D.items() if xlo <= v[0][-1] <= xhi),
                  key=lambda c: -D[c][1][0])
    chosen = []
    for c in cand:
        if all((s := separation(D, c, o)) and s > minsep for o in chosen):
            chosen.append(c)
    return chosen


def declutter(logys, gap):
    """Greedy vertical de-collision of the end labels, in log10 space."""
    order = sorted(range(len(logys)), key=lambda i: logys[i])
    out = list(logys)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    return out


def panel(ax, items, D, title=None, subtitle=None, fs=13, gapfrac=0.042,
          label_fs=13, tick_fs=12, lw=2.0, ms=8):
    ax.set_facecolor(SURFACE)
    xmax = max(D[c][0][-1] for c, _ in items)
    tips = []
    for c, col in items:
        x, y = D[c]
        ax.plot(x, y, color=col, lw=lw, solid_capstyle="round", zorder=3)
        # Dot marks the minimum grid (the anchor every curve starts from).
        ax.plot(x[0], y[0], "o", ms=ms, color=col, mec=SURFACE, mew=1.6, zorder=4)
        tips.append((x[-1], y[-1], short(c)))

    ax.set_yscale("log")
    lo = min(min(D[c][1]) for c, _ in items)
    hi = max(max(D[c][1]) for c, _ in items)
    span = np.log10(hi) - np.log10(lo)
    placed = declutter([np.log10(t[1]) for t in tips], gap=span * gapfrac)
    # Direct label at each curve's OWN tip: identity by position, never colour alone.
    for (xt, yt, name), ly in zip(tips, placed):
        ax.annotate(f" {name}", xy=(xt, yt), xytext=(xt + xmax * 0.012, 10 ** ly),
                    textcoords="data", va="center", ha="left", fontsize=fs,
                    color=INK2, zorder=5,
                    arrowprops=dict(arrowstyle="-", color=INK3, lw=0.7,
                                    shrinkA=0, shrinkB=3, alpha=0.5))
    ax.set_xlim(-xmax * 0.03, xmax * 1.30)
    if title:
        ax.set_title(f"{title}\n{subtitle}", fontsize=17, color=INK, pad=12, loc="left",
                     fontweight="bold")
    ax.set_xlabel("grid side growth over the minimum grid  (%)", fontsize=label_fs, color=INK2)
    ax.set_ylabel("routing steps  (log scale)", fontsize=label_fs, color=INK2)
    ax.grid(True, which="major", axis="both", color="#e6e5e1", lw=0.9, zorder=0)
    ax.grid(True, which="minor", axis="y", color="#f2f1ee", lw=0.6, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#d9d8d3")
    ax.tick_params(colors=INK2, labelsize=tick_fs)


def save(fig, name):
    p = OUTDIR / name
    fig.savefig(p, dpi=140, facecolor=SURFACE)
    plt.close(fig)
    print(f"  scritto {p.name}")


def fig0(D):
    """Two panels: half the movers | half the flat ones."""
    gain = {c: (y[0] - y.min()) / y[0] * 100 if y[0] else 0 for c, (_, y) in D.items()}
    var = {c: (y.max() - y.min()) / y.max() * 100 for c, (_, y) in D.items()}
    movers = sorted([c for c in D if gain[c] > 0], key=lambda c: -gain[c])
    flat = sorted([c for c in D if gain[c] == 0 and var[c] < 1], key=lambda c: -D[c][1][0])
    m_sel = movers[: (len(movers) + 1) // 2]
    f_sel = flat[::2][: len(flat) // 2]

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(SURFACE)
    panel(axes[0], list(zip(m_sel, CAT)), D,
          f"Si muovono — le {len(m_sel)} con il calo maggiore, di {len(movers)}",
          "salire di griglia riduce i routing step · il pallino è la griglia minima")
    panel(axes[1], list(zip(f_sel, ramp(len(f_sel)))), D,
          f"Piatte — {len(f_sel)} di {len(flat)}",
          "variazione < 1% su tutto il range: la griglia minima è già ottima")
    fig.tight_layout()
    save(fig, "0_muovono_vs_piatte.png")


def fig1(D):
    """The strict search: 6 families, no crossings, >=1.3x apart, gap <= 6.5x."""
    fig, ax = plt.subplots(figsize=(19, 10))
    fig.patch.set_facecolor(SURFACE)
    panel(ax, list(zip(SELECTED_1, CAT)), D)
    fig.tight_layout()
    save(fig, "1_sei_senza_incroci.png")


def fig1_paper(D):
    """fig1's curves, re-rendered for the paper (fig:scatter in figures/fig_scatter.tex).

    Rendered at final size rather than scaled down from the 19in screen figure:
    the paper is two-column IEEEtran, so a 3.5in column would shrink those 13pt
    labels to ~2pt. Font sizes follow the other paper scripts (serif, 8pt).
    """
    style = {
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": 8,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    }
    with plt.rc_context(style):
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        fig.patch.set_facecolor(SURFACE)
        panel(ax, list(zip(SELECTED_1, CAT)), D,
              fs=6, gapfrac=0.075, label_fs=7, tick_fs=6, lw=1.0, ms=3)
        fig.tight_layout()
        PAPER_FIG.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(PAPER_FIG, facecolor=SURFACE)
        plt.close(fig)
    print(f"  scritto {PAPER_FIG.relative_to(ROOT)}")


def fig2(D):
    """Relaxed search: as many families as fit without crossing, >=1.10x apart."""
    # x <= 660% keeps out simon_n6 / continuous_3_17_13, whose tiny 2x2 minimum grid
    # stretches to +1450% and would squash everything else into the left tenth.
    sel = greedy_set(D, minsep=1.10, xlo=150, xhi=660)
    gain = {c: (D[c][1][0] - D[c][1].min()) / D[c][1][0] * 100 for c in sel}
    # Composite colour: the families that actually drop take the categorical slots, the
    # rest are one neutral group — 23 categorical hues would be unreadable.
    mov = [c for c in sel if gain[c] > 50]
    items = [(c, CAT[mov.index(c)] if c in mov else FLATGREY)
             for c in sorted(sel, key=lambda c: -D[c][1][0])]
    fig, ax = plt.subplots(figsize=(20, 14))
    fig.patch.set_facecolor(SURFACE)
    panel(ax, items, D,
          f"Routing steps vs crescita della griglia — {len(sel)} famiglie, nessun incrocio",
          "vincoli rilassati (separazione ≥ 1.10×) · a colori le famiglie che calano, "
          "in grigio le piatte · il pallino è la griglia minima",
          fs=12, gapfrac=0.022)
    fig.tight_layout()
    save(fig, "2_rilassato_piu_curve.png")


def main():
    D = load()
    fig0(D)
    fig1(D)
    fig1_paper(D)
    fig2(D)


if __name__ == "__main__":
    main()
