#!/usr/bin/env python3
"""Generate Figure 4 of the paper: performance profile of routing steps, ours vs WISQ.

Reads the primary same-grid comparison (Gaussian placement with the default
naive-critical router) and plots the empirical CDF of the per-circuit routing-step
ratio (WISQ steps / our steps) over the circuits completed by both compilers.
The vertical line at ratio 1 separates losses (left) from ties and wins (right).

Usage:
    python scripts/plots/plot_paper_perf_profile.py
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib
matplotlib.use("Agg")
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
OUTPUT_PDF = REPO_ROOT / "paper_overleaf" / "figures" / "gaussian_perf_profile.pdf"
PREVIEW_PNG = REPO_ROOT / "results" / "all_circuits_8" / "_fig_candidates" / "paper_fig4_perf_profile.png"

TIE = "#9E9E9E"
INK = "#263238"


def main() -> int:
    ratios = []
    tie_n = tie_time_win = 0
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
            ratios.append(wisq / mine)
            if mine == wisq:
                tie_n += 1
                if float(row["my_duration_s"]) < float(row["wisq_duration_s"]):
                    tie_time_win += 1

    ratios = np.sort(np.array(ratios))
    n = len(ratios)
    y = np.arange(1, n + 1) / n
    frac_ge = float(np.mean(ratios >= 1.0))          # match or outperform, on steps
    frac_lt = float(np.mean(ratios < 1.0))           # losses
    tie_share = 100 * tie_n / n
    tie_time_pct = 100 * tie_time_win / tie_n if tie_n else 0.0

    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    ax.step(ratios, y, where="post", color="#1565C0", linewidth=1.8)
    ax.axvline(1.0, color=TIE, linestyle="--", linewidth=1.0)
    ax.axhline(frac_lt, color="#C62828", linestyle=":", linewidth=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("routing-step ratio  (WISQ / ours)")
    ax.set_ylabel("fraction of circuits $\\leq$ ratio")
    ax.grid(True, which="both", linestyle=":", alpha=0.3)

    ax.text(1.15, 0.60,
            f"{tie_share:.0f}% of circuits tie on steps:\n{tie_time_pct:.0f}% finish faster.",
            transform=ax.get_xaxis_transform(), fontsize=7.5, color=INK,
            va="center", ha="left", linespacing=1.4)
    ax.text(1.15, 0.45,
            f"We match or outperform\nWISQ on {frac_ge*100:.0f}% of circuits.",
            transform=ax.get_xaxis_transform(), fontsize=7.5, color=INK,
            va="center", ha="left", linespacing=1.4)

    fig.tight_layout()
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PDF)
    PREVIEW_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PREVIEW_PNG, dpi=170)
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")
    print(f"preview: {PREVIEW_PNG}")
    print(f"n={n} match_or_beat={frac_ge*100:.1f}% ties={tie_share:.1f}% "
          f"tie_time_win={tie_time_pct:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
