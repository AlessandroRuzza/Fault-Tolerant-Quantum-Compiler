#!/usr/bin/env python3
"""Throwaway: Fig.5 (steps/gate scatter, ours vs WISQ) with a smooth fitted
trend curve through the cloud instead of a jagged connecting line.
Same axes. Tries several non-linear fits in log-log space and keeps the best."""
from __future__ import annotations
import csv, os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline

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

lx = np.log10(xs); ly = np.log10(ys)
o = np.argsort(lx)
lxs, lys = lx[o], ly[o]

def r2(yhat, y):
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot

fits = {}
for deg in (1, 2, 3):
    c = np.polyfit(lxs, lys, deg)
    fits[f"poly{deg}"] = (r2(np.polyval(c, lxs), lys), ("poly", c))
# smoothing spline (needs strictly increasing x -> average duplicate lx)
ux, inv = np.unique(lxs, return_inverse=True)
uy = np.array([lys[inv == i].mean() for i in range(len(ux))])
if len(ux) > 6:
    spl = UnivariateSpline(ux, uy, k=3, s=len(ux) * 0.35)
    fits["spline"] = (r2(spl(lxs), lys), ("spline", spl))

print(f"n={n} win={wins} tie={ties} loss={losses}")
for k, (rr, _) in sorted(fits.items(), key=lambda kv: -kv[1][0]):
    print(f"  {k:8s} R2(log)={rr:.4f}")

# choose the best NON-linear fit (exclude poly1 per request)
cand = {k: v for k, v in fits.items() if k != "poly1"}
best_name = max(cand, key=lambda k: cand[k][0])
best_r2, (kind, model) = cand[best_name]
print(f"chosen: {best_name} R2={best_r2:.4f}")

xx = np.linspace(lxs.min(), lxs.max(), 400)
yy = np.polyval(model, xx) if kind == "poly" else model(xx)

fig, ax = plt.subplots(figsize=(3.4, 3.2))
ax.scatter(xs, ys, s=10, alpha=0.4, color="#1565C0", linewidths=0, zorder=2)
ax.plot(10 ** xx, 10 ** yy, color="#00695C", linewidth=2.0, zorder=3,
        label=f"fit ({best_name}, $R^2$={best_r2:.2f})")
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
dst = OUT / "7_scatter_per_gate_fit.png"
fig.savefig(dst, dpi=170)
plt.close(fig)
# drop the old jagged version so "figure 7" is unambiguous
old = OUT / "7_scatter_per_gate_joined.png"
if old.exists():
    old.unlink()
print("saved", dst)
