#!/usr/bin/env python3
"""Throwaway: scatter of the routing-step ratio (WISQ / ours) against the
minimum CNOT degree of each circuit. Both axes linear, red dashed line at ratio=1.

min CNOT degree = smallest number of distinct CNOT partners over the qubits that
take part in at least one CNOT (matches the paper's fig:optimality definition;
validated against data/results/cache_metrics/all_circuits_cache_metrics.csv).
"""
from __future__ import annotations
import csv, os, re
from pathlib import Path
from collections import defaultdict

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
CSV = ROOT / "data/results/single_config/wisqmin_connectivity_naive_critical.csv"
QDIR = ROOT / "qasms"
OUT = ROOT / "results/all_circuits_8/_fig_candidates"
OUT.mkdir(parents=True, exist_ok=True)

CX = re.compile(r"^\s*(cx|cnot)\s+q\[(\d+)\]\s*,\s*q\[(\d+)\]\s*;", re.I)


def min_cnot_degree(name: str) -> int | None:
    p = QDIR / f"{name}.qasm"
    if not p.exists():
        return None
    adj: dict[int, set[int]] = defaultdict(set)
    for line in p.read_text().splitlines():
        m = CX.match(line)
        if m:
            a, b = int(m.group(2)), int(m.group(3))
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
    if not adj:
        return None
    return min(len(v) for v in adj.values())


xs, ys, skipped = [], [], 0
for r in csv.DictReader(CSV.open(newline="")):
    if r["my_status"].strip() != "success" or r["wisq_status"].strip() != "success":
        continue
    w = float(r["wisq_routing_steps"]); m = float(r["my_routing_steps"])
    if w <= 0 or m <= 0:
        continue
    d = min_cnot_degree(r["circuit"])
    if d is None:
        skipped += 1
        continue
    xs.append(d); ys.append(w / m)

xs = np.array(xs, dtype=float); ys = np.array(ys)
print(f"n={len(xs)} skipped(no qasm / no cnot)={skipped}")
print(f"min_cnot_degree range: {xs.min():.0f}..{xs.max():.0f}   ratio range: {ys.min():.2f}..{ys.max():.2f}")
print(f"we win (ratio>1): {int(np.sum(ys > 1))}, tie: {int(np.sum(ys == 1))}, lose: {int(np.sum(ys < 1))}")

fig, ax = plt.subplots(figsize=(3.8, 3.2))
ax.scatter(xs, ys, s=14, alpha=0.5, color="#1565C0", linewidths=0, zorder=2)
ax.axhline(1.0, color="#E53935", linestyle="--", linewidth=1.2, zorder=1, label="ratio $=1$")
ax.set_xlabel("Min CNOT degree")
ax.set_ylabel("routing-step ratio  (WISQ / ours)")
ax.legend(loc="upper right", fontsize=8, frameon=False)
ax.grid(True, linestyle=":", alpha=0.3)
fig.tight_layout()
dst = OUT / "9_ratio_vs_min_cnot_degree.png"
fig.savefig(dst, dpi=170)
plt.close(fig)
print("saved", dst)
