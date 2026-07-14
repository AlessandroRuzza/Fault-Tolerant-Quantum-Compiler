#!/usr/bin/env python3
"""Generate Figure 4 of the paper: per-circuit routing steps, ours vs WISQ.

Reads the primary same-grid comparison (Gaussian placement with the lightweight
naive-critical router) and plots a log-log scatter of WISQ routing steps (x)
against our routing steps (y), one point per circuit completed by both compilers.
Points below the y=x diagonal are circuits where we use fewer routing steps than
WISQ.

Usage:
    python scripts/plots/plot_paper_scatter.py
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_CSV = (
    REPO_ROOT
    / "data"
    / "results"
    / "single_config"
    / "wisqmin_connectivity_naive_critical.csv"
)
OUTPUT_PDF = REPO_ROOT / "paper_overleaf" / "figures" / "gaussian_scatter.pdf"


def main() -> int:
    xs, ys = [], []
    with INPUT_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("my_status", "").strip() != "success":
                continue
            if row.get("wisq_status", "").strip() != "success":
                continue
            wisq = float(row["wisq_routing_steps"])
            mine = float(row["my_routing_steps"])
            if wisq <= 0 or mine <= 0:
                continue
            xs.append(wisq)
            ys.append(mine)

    xs = np.array(xs)
    ys = np.array(ys)
    n = len(xs)
    wins = int(np.sum(ys < xs))
    ties = int(np.sum(ys == xs))
    losses = int(np.sum(ys > xs))

    fig, ax = plt.subplots(figsize=(3.4, 3.2))
    ax.scatter(xs, ys, s=10, alpha=0.55, color="#1565C0", linewidths=0)

    lo = min(xs.min(), ys.min()) * 0.7
    hi = max(xs.max(), ys.max()) * 1.4
    ax.plot([lo, hi], [lo, hi], color="#E53935", linestyle="--", linewidth=1.0,
            zorder=1, label="$y=x$")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("WISQ routing steps")
    ax.set_ylabel("Gaussian + naive-critical steps")
    ax.set_aspect("equal")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    ax.grid(True, which="both", linestyle=":", alpha=0.3)

    stats_txt = f"below diagonal: {wins}\non diagonal: {ties}\nabove diagonal: {losses}\n(n={n})"
    ax.text(0.98, 0.02, stats_txt, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7, family="monospace",
            bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD", alpha=0.9))

    plt.tight_layout()
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_PDF)
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")
    print(f"n={n} below={wins} on={ties} above={losses}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
