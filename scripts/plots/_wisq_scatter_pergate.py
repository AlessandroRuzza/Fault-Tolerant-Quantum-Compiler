#!/usr/bin/env python3
"""Throwaway: Fig.4-style log-log scatter (ours vs WISQ) but each axis is
routing steps normalised by the circuit's gate count. connectivity+packing CSV."""
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
QDIR = ROOT / "qasms"
OUT = ROOT / "results/all_circuits_8/_fig_candidates"
OUT.mkdir(parents=True, exist_ok=True)

_SKIP = ("openqasm", "include", "qreg", "creg", "barrier", "measure",
         "gate ", "opaque", "//", "if(", "if (")

def count_gates(name: str) -> int | None:
    p = QDIR / f"{name}.qasm"
    if not p.exists():
        return None
    g = 0
    for raw in p.read_text().splitlines():
        s = raw.strip()
        if not s or s in ("{", "}"):
            continue
        low = s.lower()
        if any(low.startswith(k) for k in _SKIP):
            continue
        if ";" in s:
            g += 1
    return g or None

xs, ys, missing = [], [], 0
for r in csv.DictReader(CSV.open(newline="")):
    if r["my_status"].strip() != "success" or r["wisq_status"].strip() != "success":
        continue
    w = float(r["wisq_routing_steps"]); m = float(r["my_routing_steps"])
    if w <= 0 or m <= 0:
        continue
    g = count_gates(r["circuit"])
    if not g:
        missing += 1
        continue
    xs.append(w / g); ys.append(m / g)

xs = np.array(xs); ys = np.array(ys)
n = len(xs)
wins = int(np.sum(ys < xs)); ties = int(np.sum(ys == xs)); losses = int(np.sum(ys > xs))
print(f"n={n} below(win)={wins} on={ties} above(loss)={losses} missing_qasm={missing}")

fig, ax = plt.subplots(figsize=(3.4, 3.2))
ax.scatter(xs, ys, s=10, alpha=0.55, color="#1565C0", linewidths=0)
lo = min(xs.min(), ys.min()) * 0.7
hi = max(xs.max(), ys.max()) * 1.4
ax.plot([lo, hi], [lo, hi], color="#E53935", linestyle="--", linewidth=1.0, zorder=1, label="$y=x$")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("WISQ routing steps / gate")
ax.set_ylabel("Gaussian + packing steps / gate")
ax.set_aspect("equal")
ax.legend(loc="upper left", fontsize=8, frameon=False)
ax.grid(True, which="both", linestyle=":", alpha=0.3)
stats = f"below diagonal: {wins}\non diagonal: {ties}\nabove diagonal: {losses}\n(n={n})"
ax.text(0.98, 0.02, stats, transform=ax.transAxes, ha="right", va="bottom",
        fontsize=7, family="monospace",
        bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD", alpha=0.9))
fig.tight_layout()
fig.savefig(OUT / "5_scatter_steps_per_gate.png", dpi=170)
plt.close(fig)
print("saved", OUT / "5_scatter_steps_per_gate.png")
