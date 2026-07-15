#!/usr/bin/env python3
"""Throwaway: Fig.8 -- steps/gate scatter (ours vs WISQ), same axes as Fig.5,
with a logarithmic fit  Y = a + b*ln(X)  through the cloud."""
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

xs, ys = [], []
for r in csv.DictReader(CSV.open(newline="")):
    if r["my_status"].strip() != "success" or r["wisq_status"].strip() != "success":
        continue
    w = float(r["wisq_routing_steps"]); m = float(r["my_routing_steps"])
    if w <= 0 or m <= 0:
        continue
    g = count_gates(r["circuit"])
    if not g:
        continue
    xs.append(w / g); ys.append(m / g)

xs = np.array(xs); ys = np.array(ys)
n = len(xs)
wins = int(np.sum(ys < xs)); ties = int(np.sum(ys == xs)); losses = int(np.sum(ys > xs))

# logarithmic fit: Y = a + b*ln(X)   (least squares in raw Y space)
lnx = np.log(xs)
b, a = np.polyfit(lnx, ys, 1)  # slope b, intercept a


def r2(yhat, y):
    return 1 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2)

r2_raw = r2(a + b * lnx, ys)
print(f"n={n} win={wins} tie={ties} loss={losses}")
print(f"log fit: Y = {a:.4f} + {b:.4f}*ln(X)   R2(raw)={r2_raw:.4f}")

fig, ax = plt.subplots(figsize=(3.4, 3.2))
ax.scatter(xs, ys, s=10, alpha=0.4, color="#1565C0", linewidths=0, zorder=2)
xx = np.logspace(np.log10(xs.min()), np.log10(xs.max()), 400)
yy = a + b * np.log(xx)
mask = yy > 0  # log axis can't show non-positive values
ax.plot(xx[mask], yy[mask], color="#6A1B9A", linewidth=2.0, zorder=3,
        label=f"log fit ($R^2$={r2_raw:.2f})")
lo = min(xs.min(), ys.min()) * 0.7
hi = max(xs.max(), ys.max()) * 1.4
ax.plot([lo, hi], [lo, hi], color="#E53935", linestyle="--", linewidth=1.0, zorder=1, label="$y=x$")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("WISQ routing steps / gate")
ax.set_ylabel("Gaussian + packing steps / gate")
ax.set_aspect("equal")
ax.legend(loc="upper left", fontsize=7.5, frameon=False)
ax.grid(True, which="both", linestyle=":", alpha=0.3)
stats = f"below diagonal: {wins}\non diagonal: {ties}\nabove diagonal: {losses}\n(n={n})"
ax.text(0.98, 0.02, stats, transform=ax.transAxes, ha="right", va="bottom",
        fontsize=7, family="monospace",
        bbox=dict(boxstyle="round", facecolor="#FFF9C4", edgecolor="#BDBDBD", alpha=0.9))
fig.tight_layout()
dst = OUT / "8_scatter_per_gate_logfit.png"
fig.savefig(dst, dpi=170)
plt.close(fig)
print("saved", dst)
