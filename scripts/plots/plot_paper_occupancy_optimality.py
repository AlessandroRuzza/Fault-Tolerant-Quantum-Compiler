#!/usr/bin/env python3
"""Generate the paper figure: routing optimality vs tile occupancy.

For one circuit per swept family (the dimension sweep from the minimum
routable grid, `dim_sweep_family_median_min_dims.csv`), plots

    x = occupancy %          = (data qubits + magic tiles) / total tiles
    y = optimality           = Rmin / routing steps   (1 is ideal)

Each curve starts (dot marker) at the circuit's minimum routable grid --
the highest occupancy -- and moves left as the grid grows.

Rmin (`min_routing_steps`, the layering-depth lower bound) and the resolved
magic-tile count (`resolved_n_magic`) are circuit-intrinsic, so they are
joined per circuit from bench runs that recorded them; values are verified
identical across all sources that contain the same circuit.

Usage:
    python scripts/plots/plot_paper_occupancy_optimality.py
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SWEEP_CSV = REPO_ROOT / "benchmarks" / "results" / "dim_sweep_family_median_min_dims.csv"
# Sources for the per-circuit constants (Rmin, resolved magic count); together
# they cover all 37 swept circuits.
AUX_CSVS = [
    REPO_ROOT / "data" / "old_results" / "old_results_2july" / "all_circuits_4_variants_runs.csv",
    REPO_ROOT / "data" / "old_results" / "old_results_25june" / "dim_opt_cube_runs.csv",
    REPO_ROOT / "data" / "old_results" / "old_results_21june" / "nontuned_correlation_sweep_runs.csv",
    REPO_ROOT / "data" / "old_results" / "old_results_21june" / "magic_low_tune_runs.csv",
]
OUTPUT_PDF = REPO_ROOT / "paper_overleaf" / "figures" / "occupancy_vs_optimality.pdf"

# One curve per behaviour class, non-colliding end points (legend order).
CIRCUITS = [
    ("ising_n80", "ising"),
    ("factor247_n15", "factor247"),
    ("qft_n80", "qft"),
    ("randomcircuit_n100", "randomcircuit"),
    ("vqe_two_local_n80", "vqe_two_local"),
]
COLORS = ["#1565C0", "#E53935", "#2E7D32", "#6A1B9A", "#00838F"]
INK = "#263238"


def load_constants() -> dict[str, tuple[int, int]]:
    """circuit -> (resolved_n_magic, min_routing_steps), cross-file verified."""
    seen: dict[str, set[tuple[int, int]]] = {}
    for path in AUX_CSVS:
        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                c = row.get("circuit")
                magic = (row.get("resolved_n_magic") or "").strip()
                rmin = (row.get("min_routing_steps") or "").strip()
                if c and magic and rmin:
                    seen.setdefault(c, set()).add((int(magic), int(rmin)))
    out = {}
    for c, vals in seen.items():
        if len(vals) > 1:
            raise SystemExit(f"inconsistent (magic, Rmin) for {c}: {sorted(vals)}")
        out[c] = next(iter(vals))
    return out


def main() -> int:
    const = load_constants()
    by_circuit: dict[str, list[dict]] = {}
    with SWEEP_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["status"] == "success":
                by_circuit.setdefault(row["circuit"], []).append(row)

    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    for (circuit, label), color in zip(CIRCUITS, COLORS):
        n_magic, rmin = const[circuit]
        rows = sorted(by_circuit[circuit], key=lambda r: int(r["dim_index"]))
        n = int(rows[0]["n_qubits"])
        occ = [100.0 * (n + n_magic) / (int(r["my_x"]) * int(r["my_y"])) for r in rows]
        opt = [rmin / int(r["my_routing_steps"]) for r in rows]
        ax.plot(occ, opt, color=color, linewidth=1.5, label=label, zorder=2)
        ax.plot(occ[0], opt[0], marker="o", ms=3.5, color=color, zorder=3)

    ax.set_xlabel("occupancy (%)")
    ax.set_ylabel(r"optimality  $R_{\min}/|R_{\mathrm{out}}|$")
    ax.set_xlim(0, 48)
    ax.set_ylim(0, 1.05)
    ax.grid(True, which="both", linestyle=":", alpha=0.3)
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.88), fontsize=6.5,
              frameon=False, handlelength=1.4, labelspacing=0.35)

    plt.tight_layout()
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_PDF)
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
