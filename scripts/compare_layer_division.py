#!/usr/bin/env python3
"""Compare our compiler's layer division against WISQ's, side by side.

Inputs:
  --ours : text dump from our compiler with PRINT_ROUTING enabled. Format is
           blocks of:
               # Step <i> #############
               (cx <a>,<b>): n0-n1-...
               (t <q>): ...
  --wisq : WISQ scmr output JSON (with "steps" as a list).

Produces one figure with two stacked schedule diagrams (ours on top, WISQ below):
  y-axis = logical qubit, x-axis = step, each gate = vertical connector / marker.
This shows how each tool packs gates into parallel layers.

Usage:
    python scripts/compare_layer_division.py \
        --ours /tmp/qft20_ours_steps.txt \
        --wisq /tmp/qft20_wisq_out.json \
        --output data/wisq_plots/qft20_layer_compare.png --title qft_20
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt

_GATE_RE = re.compile(r"\((cx|t|tdg)\s+([\d,]+)\)")


def parse_ours(path: Path) -> list[list[dict]]:
    """Parse our PRINT_ROUTING dump into a list of steps (list of gate dicts)."""
    steps: list[list[dict]] = []
    current: list[dict] | None = None
    for line in path.read_text().splitlines():
        if line.startswith("# Step"):
            current = []
            steps.append(current)
            continue
        if current is None:
            continue
        m = _GATE_RE.search(line)
        if m:
            op = m.group(1)
            qs = [int(x) for x in m.group(2).split(",")]
            current.append({"op": op, "qubits": qs})
    return steps


def parse_wisq(path: Path) -> list[list[dict]]:
    data = json.loads(path.read_text())
    if isinstance(data.get("steps"), str):
        raise SystemExit(f"WISQ steps='{data['steps']}' (timeout) — nothing to draw.")
    out = []
    for step in data["steps"]:
        out.append([{"op": g.get("op", ""), "qubits": [int(q) for q in g.get("qubits", [])]}
                    for g in step])
    return out


def n_qubits_of(steps: list[list[dict]]) -> int:
    mx = 0
    for step in steps:
        for g in step:
            for q in g["qubits"]:
                mx = max(mx, q)
    return mx + 1


def draw_schedule(ax, steps: list[list[dict]], label: str, color: str) -> None:
    gps = [len(s) for s in steps]
    n_steps = len(steps)
    nq = n_qubits_of(steps)
    for q in range(nq):
        ax.axhline(q, color="#F0F0F0", linewidth=0.5, zorder=0)
    for s, step in enumerate(steps):
        for g in step:
            qs = g["qubits"]
            if len(qs) == 2:
                lo, hi = min(qs), max(qs)
                ax.plot([s, s], [lo, hi], "-", color=color, linewidth=1.1, alpha=0.7, zorder=2)
                ax.plot([s, s], [lo, hi], ".", color=color, markersize=2.5, zorder=3)
            elif len(qs) == 1:
                mc = "#E53935" if g["op"] in ("t", "tdg") else "#43A047"
                ax.plot(s, qs[0], "s", color=mc, markersize=2.5, zorder=3)
    avg = sum(gps) / max(1, n_steps)
    ax.set_title(f"{label}: {n_steps} steps · avg {avg:.2f} gates/step · max {max(gps) if gps else 0}",
                 fontsize=11, fontweight="bold")
    ax.set_ylabel("qubit")
    ax.set_xlim(-1, max(n_steps, 1))
    ax.set_ylim(-1, nq)
    ax.invert_yaxis()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare our vs WISQ layer division.")
    parser.add_argument("--ours", required=True, help="Our PRINT_ROUTING text dump")
    parser.add_argument("--wisq", required=True, help="WISQ scmr output JSON")
    parser.add_argument("--output", "-o", required=True, help="Output PNG path")
    parser.add_argument("--title", default="", help="Circuit name for the figure title")
    args = parser.parse_args()

    ours = parse_ours(Path(args.ours))
    wisq = parse_wisq(Path(args.wisq))

    n_steps_max = max(len(ours), len(wisq))
    nq = max(n_qubits_of(ours), n_qubits_of(wisq))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(9, n_steps_max * 0.14),
                                                   max(5, nq * 0.32)), sharex=True)
    draw_schedule(ax1, ours, "OURS", "#1976D2")
    draw_schedule(ax2, wisq, "WISQ", "#8E24AA")
    # shared x range for fair visual comparison
    for ax in (ax1, ax2):
        ax.set_xlim(-1, n_steps_max)
        ax.set_ylim(-1, nq)
        ax.invert_yaxis()
    ax2.set_xlabel("step (layer)")
    fig.suptitle(f"Layer division: OURS vs WISQ  ·  {args.title}",
                 fontsize=13, fontweight="bold")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved comparison to {out}")
    print(f"  OURS: {len(ours)} steps, avg {sum(len(s) for s in ours)/max(1,len(ours)):.2f} gates/step")
    print(f"  WISQ: {len(wisq)} steps, avg {sum(len(s) for s in wisq)/max(1,len(wisq)):.2f} gates/step")
    return 0


if __name__ == "__main__":
    sys.exit(main())
