#!/usr/bin/env python3
"""Visualize WISQ's gate-to-step (layer) division as a schedule diagram.

Reads a WISQ scmr output JSON and draws a single overview:
  - y-axis: logical qubits
  - x-axis: routing step (= WISQ's parallel "layer")
  - each gate is drawn at its step: a CX is a vertical connector between its two
    qubit rows; a T/Tdg is a single marker.

This shows directly how WISQ packs gates into parallel layers — how many gates
share each step and which qubits they touch.

Usage:
    python scripts/plots/visualize_wisq_schedule.py --input /tmp/qft20_wisq_out.json \
        --output data/wisq_plots/qft20_schedule.png [--max-steps N]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot WISQ step/layer division.")
    parser.add_argument("--input", "-i", required=True, help="WISQ scmr output JSON")
    parser.add_argument("--output", "-o", required=True, help="Output PNG path")
    parser.add_argument("--max-steps", type=int, default=None,
                        help="Only show the first N steps (default: all)")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text())
    if isinstance(data.get("steps"), str):
        raise SystemExit(f"steps='{data['steps']}' (timeout) — nothing to draw.")

    steps = data["steps"]
    if args.max_steps is not None:
        steps = steps[: args.max_steps]

    # collect all qubits appearing in gates
    all_qubits = set()
    for step in steps:
        for g in step:
            for q in g.get("qubits", []):
                all_qubits.add(int(q))
    n_qubits = (max(all_qubits) + 1) if all_qubits else 1

    n_steps = len(steps)
    fig_w = max(8, n_steps * 0.16)
    fig_h = max(4, n_qubits * 0.22)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # faint horizontal qubit "wires"
    for q in range(n_qubits):
        ax.axhline(q, color="#EEEEEE", linewidth=0.6, zorder=0)

    gates_per_step = []
    for s, step in enumerate(steps):
        gates_per_step.append(len(step))
        for g in step:
            qs = [int(q) for q in g.get("qubits", [])]
            op = g.get("op", "")
            if len(qs) == 2:
                lo, hi = min(qs), max(qs)
                ax.plot([s, s], [lo, hi], "-", color="#1976D2", linewidth=1.2,
                        alpha=0.7, zorder=2)
                ax.plot([s, s], [lo, hi], ".", color="#1976D2", markersize=3, zorder=3)
            elif len(qs) == 1:
                color = "#E53935" if op in ("t", "tdg") else "#43A047"
                ax.plot(s, qs[0], "s", color=color, markersize=3, zorder=3)

    ax.set_xlabel(f"WISQ step (layer)   —   {n_steps} steps, "
                  f"avg {sum(gates_per_step)/max(1,n_steps):.1f} gates/step, "
                  f"max {max(gates_per_step) if gates_per_step else 0}")
    ax.set_ylabel("logical qubit")
    ax.set_title(f"WISQ layer division  ·  {Path(args.input).stem}", fontweight="bold")
    ax.set_xlim(-1, n_steps)
    ax.set_ylim(-1, n_qubits)
    ax.invert_yaxis()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved schedule to {out}")
    print(f"{n_steps} steps, {sum(gates_per_step)} gates, "
          f"avg {sum(gates_per_step)/max(1,n_steps):.2f} gates/step, "
          f"max {max(gates_per_step) if gates_per_step else 0}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
