#!/usr/bin/env python3
"""Visualize a WISQ scmr output JSON step by step on the surface-code grid.

WISQ's output JSON (from --mode scmr) contains:
  - "map":   list of [logical_qubit, physical_node] pairs (flat node indices)
  - "arch":  {"width", "height", "alg_qubits", "magic_states"}
  - "steps": list of steps; each step is a list of gate-paths
             {"id", "op", "qubits", "path": [node, node, ...]}
  - "gates": the routed gate list

This renders one PNG per step showing:
  - the grid, data-qubit slots, magic states
  - the logical-qubit labels at their mapped positions
  - each gate-path of that step as a coloured polyline
  - cells used by MORE THAN ONE path in the same step highlighted in RED
    (a lattice-surgery violation: paths in one step must be node-disjoint)

A summary of any overlaps is printed at the end — this is the key check for
whether WISQ is packing spatially-conflicting routes into a single step.

Usage:
    python scripts/visualize_wisq_steps.py --input /tmp/qft20_wisq_out.json \
        --output data/wisq_plots/qft20_steps [--max-steps 30]
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
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D


def node_to_xy(node: int, width: int) -> tuple[int, int]:
    """Flat node index -> (col, row)."""
    return node % width, node // width


def load(path: Path) -> dict:
    data = json.loads(path.read_text())
    if isinstance(data.get("steps"), str):
        raise SystemExit(f"This output has steps='{data['steps']}' (timeout) — nothing to draw.")
    return data


def draw_step(step_idx: int, step: list, data: dict, qmap: dict,
              width: int, height: int, magic: set, slots: set,
              out_dir: Path) -> int:
    """Draw one step. Returns the number of overlapping cells found."""
    fig, ax = plt.subplots(figsize=(width * 0.5 + 2, height * 0.5 + 2))

    # base grid
    for r in range(height):
        for c in range(width):
            node = r * width + c
            if node in magic:
                face = "#FFD54F"  # magic state
            elif node in slots:
                face = "#E3F2FD"  # data-qubit slot
            else:
                face = "#FAFAFA"  # routing corridor / empty
            ax.add_patch(mpatches.Rectangle((c - 0.5, r - 0.5), 1, 1,
                         facecolor=face, edgecolor="#DDDDDD", linewidth=0.5))

    # count cell usage across paths in this step (for overlap detection)
    cell_use: dict[int, int] = {}
    for gate in step:
        for node in gate.get("path", []):
            cell_use[node] = cell_use.get(node, 0) + 1
    overlaps = {n for n, k in cell_use.items() if k > 1}

    # draw paths
    cmap = plt.get_cmap("tab10")
    for gi, gate in enumerate(step):
        path = gate.get("path", [])
        if not path:
            continue
        xs = [node_to_xy(n, width)[0] for n in path]
        ys = [node_to_xy(n, width)[1] for n in path]
        color = cmap(gi % 10)
        ax.plot(xs, ys, "-", color=color, linewidth=2.5, alpha=0.8, zorder=3)
        # endpoints
        ax.plot([xs[0], xs[-1]], [ys[0], ys[-1]], "o", color=color,
                markersize=7, zorder=4)

    # highlight overlapping cells in red
    for node in overlaps:
        c, r = node_to_xy(node, width)
        ax.add_patch(mpatches.Rectangle((c - 0.5, r - 0.5), 1, 1,
                     facecolor="none", edgecolor="red", linewidth=2.5, zorder=5))

    # logical-qubit labels at mapped positions
    for q, node in qmap.items():
        c, r = node_to_xy(node, width)
        ax.text(c, r, str(q), ha="center", va="center", fontsize=6,
                color="#0D47A1", zorder=6)

    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([]); ax.set_yticks([])
    n_gates = len(step)
    title = f"step {step_idx}  ·  {n_gates} gate(s)"
    if overlaps:
        title += f"  ·  ⚠ {len(overlaps)} OVERLAP CELL(S)"
    ax.set_title(title, fontsize=11,
                 color="red" if overlaps else "black",
                 fontweight="bold" if overlaps else "normal")

    legend = [
        mpatches.Patch(facecolor="#E3F2FD", edgecolor="#DDD", label="data slot"),
        mpatches.Patch(facecolor="#FFD54F", edgecolor="#DDD", label="magic state"),
        Line2D([0], [0], color="red", lw=2.5, label="overlap (violation)"),
    ]
    ax.legend(handles=legend, loc="upper left", bbox_to_anchor=(1.01, 1),
              fontsize=7, framealpha=0.9)

    plt.tight_layout()
    out_path = out_dir / f"step_{step_idx:04d}.png"
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return len(overlaps)


def main() -> int:
    parser = argparse.ArgumentParser(description="Visualize WISQ scmr steps on the grid.")
    parser.add_argument("--input", "-i", required=True, help="WISQ scmr output JSON")
    parser.add_argument("--output", "-o", required=True, help="Output directory for step PNGs")
    parser.add_argument("--max-steps", type=int, default=None,
                        help="Only render the first N steps (default: all)")
    args = parser.parse_args()

    data = load(Path(args.input))
    arch = data["arch"]
    width, height = int(arch["width"]), int(arch["height"])
    magic = set(int(m) for m in arch.get("magic_states", []))
    slots = set(int(s) for s in arch.get("alg_qubits", []))
    qmap = {int(q): int(n) for q, n in (data["map"].items()
            if isinstance(data["map"], dict) else data["map"])}

    steps = data["steps"]
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    n = len(steps) if args.max_steps is None else min(args.max_steps, len(steps))
    print(f"Grid {width}x{height}, {len(magic)} magic, {len(slots)} slots, "
          f"{len(steps)} steps total. Rendering {n}.")

    total_overlap_steps = 0
    total_overlap_cells = 0
    for i in range(n):
        ov = draw_step(i, steps[i], data, qmap, width, height, magic, slots, out_dir)
        if ov:
            total_overlap_steps += 1
            total_overlap_cells += ov
            print(f"  step {i}: ⚠ {ov} overlapping cell(s)")

    print(f"\nSaved {n} PNGs to {out_dir}")
    if total_overlap_steps:
        print(f"⚠ OVERLAPS FOUND: {total_overlap_steps} step(s), "
              f"{total_overlap_cells} cell-uses — WISQ packed conflicting paths.")
    else:
        print("No intra-step path overlaps detected (paths are node-disjoint per step).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
