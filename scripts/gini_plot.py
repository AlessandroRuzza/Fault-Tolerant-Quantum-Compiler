#!/usr/bin/env python3
"""
Plot gaussian-vs-random advantage as a function of CNOT-pair-repetition Gini
and interaction density, from a synthetic-study runs CSV.

For every circuit it takes the best (lowest) routing_steps achieved by gaussian
(over all its tuning variants) and by random, computes

    advantage = (random_best - gaussian_best) / random_best        (>0 = gaussian better)

and joins each circuit with its cnot_pair_rep_gini / cnot_interaction_density
from the metrics CSV. Produces:

  - advantage_vs_gini.png    scatter + median trend of advantage vs gini,
                             one series per density level
  - advantage_heatmap.png    2D heatmap of median advantage over
                             (density x gini-bucket)

Usage:
  python3 scripts/gini_plot.py <runs_csv> \
      [--metrics <cache_metrics_csv>] [--out-dir <dir>]
"""

import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METRICS = PROJECT_ROOT / "benchmarks" / "results" / "cache_metrics" / "all_circuits_cache_metrics.csv"

GINI_KEY = "cnot_pair_rep_gini"
DENSITY_KEY = "cnot_interaction_density"


def load_advantage(runs_csv, metrics_csv):
    """Return list of dicts: circuit, advantage, gini, density, g_steps, r_steps."""
    best = defaultdict(lambda: {"gaussian": None, "random": None})
    with open(runs_csv) as f:
        for r in csv.DictReader(f):
            if r.get("status") != "success" or not r.get("routing_steps", "").strip():
                continue
            t = r["mapping_type"]
            if t not in ("gaussian", "random"):
                continue
            s = int(float(r["routing_steps"]))
            cur = best[r["circuit"]][t]
            if cur is None or s < cur:
                best[r["circuit"]][t] = s

    metrics = {}
    with open(metrics_csv) as f:
        for r in csv.DictReader(f):
            metrics[r["circuit"]] = r

    out = []
    missing = []
    for c, bt in best.items():
        g, rnd = bt["gaussian"], bt["random"]
        if g is None or rnd is None or rnd == 0:
            continue
        m = metrics.get(c)
        if m is None or not m.get(GINI_KEY, "").strip():
            missing.append(c)
            continue
        out.append({
            "circuit": c,
            "advantage": (rnd - g) / rnd,
            "gini": float(m[GINI_KEY]),
            "density": float(m[DENSITY_KEY]),
            "g_steps": g, "r_steps": rnd,
        })
    if missing:
        print(f"WARNING: {len(missing)} circuit(s) missing metrics (run update_metrics.py): "
              f"{missing[:5]}{'...' if len(missing) > 5 else ''}")
    return out


def regression_r2(data):
    """advantage ~ gini + density (standardized). Returns (b_gini, b_dens, r2)."""
    if len(data) < 4:
        return None
    adv = np.array([d["advantage"] for d in data])
    gini = np.array([d["gini"] for d in data])
    dens = np.array([d["density"] for d in data])

    def z(x):
        sd = x.std()
        return (x - x.mean()) / sd if sd > 0 else x * 0.0

    X = np.column_stack([np.ones(len(adv)), z(gini), z(dens)])
    beta, *_ = np.linalg.lstsq(X, adv, rcond=None)
    pred = X @ beta
    ss_tot = ((adv - adv.mean()) ** 2).sum()
    r2 = 1 - ((adv - pred) ** 2).sum() / ss_tot if ss_tot > 0 else 0.0
    return beta[1], beta[2], r2


def plot_advantage_vs_gini(data, out_path):
    densities = sorted(set(round(d["density"], 2) for d in data))
    cmap = plt.get_cmap("viridis")
    colors = {dv: cmap(i / max(1, len(densities) - 1)) for i, dv in enumerate(densities)}

    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor="white")
    ax.axhline(0, color="#888888", lw=1.2, ls="--", zorder=1, label="pareggio (random = gaussian)")

    for dv in densities:
        pts = [d for d in data if round(d["density"], 2) == dv]
        xs = np.array([d["gini"] for d in pts])
        ys = np.array([d["advantage"] for d in pts])
        col = colors[dv]
        ax.scatter(xs, ys, color=col, alpha=0.55, s=40, zorder=2)
        # median trend over gini buckets
        order = np.argsort(xs)
        ux = sorted(set(round(x, 2) for x in xs))
        med = [np.median([y for x, y in zip(xs, ys) if round(x, 2) == g]) for g in ux]
        ax.plot(ux, med, color=col, lw=2.4, marker="o", zorder=3,
                label=f"density = {dv:.2f}")

    ax.set_xlabel("CNOT pair-repetition Gini  (0 = pesi uniformi, 1 = pochi hotspot)", fontsize=11)
    ax.set_ylabel("gaussian advantage = (random − gaussian) / random", fontsize=11)
    ax.set_title("Vantaggio di gaussian vs eterogeneità delle interazioni (Gini)\n"
                 "sopra 0 = gaussian meglio di random", fontsize=12, fontweight="bold")
    reg = regression_r2(data)
    if reg:
        bg, bd, r2 = reg
        ax.text(0.02, 0.02,
                f"regressione adv ~ gini + densità:  β_gini={bg:+.3f}, β_dens={bd:+.3f},  R²={r2:.2f}",
                transform=ax.transAxes, fontsize=9, color="#333333",
                bbox=dict(boxstyle="round", fc="white", ec="#cccccc"))
    ax.grid(color="#eeeeee", zorder=0)
    ax.legend(fontsize=9, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_heatmap(data, out_path):
    densities = sorted(set(round(d["density"], 2) for d in data))
    gini_edges = [0.0, 0.05, 0.40, 0.60, 1.01]
    gini_labels = ["~0", "0.05–0.4", "0.4–0.6", ">0.6"]

    grid = np.full((len(densities), len(gini_labels)), np.nan)
    counts = np.zeros_like(grid)
    for i, dv in enumerate(densities):
        for j in range(len(gini_labels)):
            lo, hi = gini_edges[j], gini_edges[j + 1]
            vals = [d["advantage"] for d in data
                    if round(d["density"], 2) == dv and lo <= d["gini"] < hi]
            if vals:
                grid[i, j] = np.median(vals)
                counts[i, j] = len(vals)

    vmax = np.nanmax(np.abs(grid)) if np.isfinite(grid).any() else 1.0
    fig, ax = plt.subplots(figsize=(8.5, 1.6 + 1.1 * len(densities)), facecolor="white")
    im = ax.imshow(grid, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(gini_labels)))
    ax.set_xticklabels(gini_labels)
    ax.set_yticks(range(len(densities)))
    ax.set_yticklabels([f"{dv:.2f}" for dv in densities])
    ax.set_xlabel("CNOT pair-repetition Gini (bucket)", fontsize=11)
    ax.set_ylabel("interaction density", fontsize=11)
    ax.set_title("Mediana del vantaggio di gaussian\n(verde = gaussian meglio, rosso = random meglio)",
                 fontsize=12, fontweight="bold")
    for i in range(len(densities)):
        for j in range(len(gini_labels)):
            if np.isfinite(grid[i, j]):
                ax.text(j, i, f"{grid[i, j]:+.2f}\n(n={int(counts[i, j])})",
                        ha="center", va="center", fontsize=9,
                        color="black")
    fig.colorbar(im, ax=ax, label="advantage mediano")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs_csv", help="synthetic-study runs CSV")
    p.add_argument("--metrics", type=Path, default=DEFAULT_METRICS,
                   help=f"cache metrics CSV (default: {DEFAULT_METRICS})")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="output directory (default: <runs_csv_dir>/gini_plots)")
    args = p.parse_args()

    out_dir = args.out_dir or (Path(args.runs_csv).resolve().parent / "gini_plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_advantage(args.runs_csv, args.metrics)
    if not data:
        print("ERROR: no circuits with both gaussian and random results + metrics.")
        return
    print(f"Circuiti analizzati: {len(data)}")
    wins = sum(1 for d in data if d["advantage"] > 0.01)
    print(f"gaussian vince: {wins} | random vince: {sum(1 for d in data if d['advantage'] < -0.01)}")
    reg = regression_r2(data)
    if reg:
        print(f"regressione: β_gini={reg[0]:+.3f}  β_density={reg[1]:+.3f}  R²={reg[2]:.3f}")

    plot_advantage_vs_gini(data, out_dir / "advantage_vs_gini.png")
    plot_heatmap(data, out_dir / "advantage_heatmap.png")
    print(f"Plot scritti in {out_dir}/")


if __name__ == "__main__":
    main()
