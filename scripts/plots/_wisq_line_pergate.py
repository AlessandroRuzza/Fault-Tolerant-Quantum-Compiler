#!/usr/bin/env python3
"""Throwaway: line version of the steps/gate comparison. Circuits sorted by
WISQ steps/gate on x; two curves (ours vs WISQ); area shaded where we win/lose."""
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

rec = []  # (wisq_per_gate, my_per_gate)
for r in csv.DictReader(CSV.open(newline="")):
    if r["my_status"].strip() != "success" or r["wisq_status"].strip() != "success":
        continue
    w = float(r["wisq_routing_steps"]); m = float(r["my_routing_steps"])
    if w <= 0 or m <= 0:
        continue
    g = count_gates(r["circuit"])
    if not g:
        continue
    rec.append((w / g, m / g))

rec.sort(key=lambda t: t[0])          # sort by WISQ steps/gate -> smooth reference
wisq = np.array([t[0] for t in rec])
mine = np.array([t[1] for t in rec])
x = np.arange(len(rec))
wins = int(np.sum(mine < wisq)); ties = int(np.sum(mine == wisq)); loss = int(np.sum(mine > wisq))
print(f"n={len(rec)} win={wins} tie={ties} loss={loss}")

WIN = "#2E7D32"; LOSS = "#C62828"
fig, ax = plt.subplots(figsize=(4.4, 3.2))
# shaded win/lose regions between the two curves
ax.fill_between(x, mine, wisq, where=(mine <= wisq), interpolate=True,
                color=WIN, alpha=0.18, linewidth=0)
ax.fill_between(x, mine, wisq, where=(mine > wisq), interpolate=True,
                color=LOSS, alpha=0.18, linewidth=0)
ax.plot(x, wisq, color="#455A64", linewidth=1.6, label="WISQ")
ax.plot(x, mine, color="#1565C0", linewidth=1.4, label="Gaussian + packing")
ax.set_yscale("log")
ax.set_xlim(0, len(rec) - 1)
ax.set_xlabel("circuits (sorted by WISQ steps / gate)")
ax.set_ylabel("routing steps / gate")
ax.set_title("Routing cost per gate: ours vs WISQ", fontsize=10)
ax.legend(loc="upper left", fontsize=8, frameon=False)
ax.grid(True, which="both", linestyle=":", alpha=0.3)
from matplotlib.patches import Patch
leg2 = ax.legend(handles=[Patch(color=WIN, alpha=0.3, label=f"we win/tie ({wins+ties})"),
                          Patch(color=LOSS, alpha=0.3, label=f"we lose ({loss})")],
                 loc="lower right", fontsize=7.5, frameon=False)
ax.add_artist(leg2)
ax.legend(loc="upper left", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(OUT / "6_line_steps_per_gate.png", dpi=170)
plt.close(fig)
print("saved", OUT / "6_line_steps_per_gate.png")
