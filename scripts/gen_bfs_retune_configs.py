#!/usr/bin/env python3
"""Generate the BFS-regime re-tuning suite (cluster-scale).

The density-gated CNOT-BFS order (gaussian_mapping, default threshold 0.40)
changed the mapping order ONLY for circuits with CNOT-graph density < 0.40.
Dense circuits keep the old heap order bit-for-bit (tuning still valid); the
sparse/structured "rest" circuits (and large qft, which is sparse) now use BFS,
so their cnot_high(d)/mapped(d) formulas must be re-fit.

Two parts:
  PART A (1D, comparable to the historical cnotdim/mappeddim methodology):
    sweep one weight x dimension with the other fixed. Produces directly
    comparable per-axis formula data, on a large BFS-regime circuit set with
    the full dimension range and 2 synth seeds.
  PART B (2D joint, rigor check): sweep cnot_high x mapped jointly on a
    responsive subset, to VERIFY the two optima are still separable under BFS
    (the historical methodology assumes they are).

Run every config on the gated binary at the DEFAULT threshold (no env override):
all listed circuits have density < 0.40 so the gate routes them to BFS.

Writes to config/:  bfs_retune_{cnotdim,mappeddim}_{coarse,fine}_{cube,noncube}.json  (Part A)
                    bfs_retune_2d_{coarse,fine}_{cube,noncube}.json                  (Part B)
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "config")

def synth(n, d, s):
    return f"synth_n{n}_d{d}_mix050_t030_hf000_hm001_r2_s{s}"

# PART A circuit set: synth backbone (2 seeds, clean d-scaling) + real BFS
# families + 2 saturated anchors. All measured density < 0.40.
CIRCUITS_1D = [
    synth(50,"020",0), synth(50,"020",1), synth(100,"020",0), synth(100,"020",1),
    synth(200,"020",0), synth(200,"020",1),
    synth(50,"040",0), synth(50,"040",1), synth(100,"040",0), synth(100,"040",1),
    synth(200,"040",0), synth(200,"040",1),
    synth(50,"030",0),
    "qft_n100", "qft_n128", "qft_n200",
    "bwt_n21", "bwt_n37",
    "square_root_n18", "square_root_n45",
    "ising_n26", "seca_n11", "dnn_n16", "multiplier_n45",
    "adder_n28", "graphstate_n100",          # saturated anchors (sanity)
]

# PART B (2D): responsive subset only — the joint sweep is expensive.
CIRCUITS_2D = [
    synth(50,"020",0), synth(100,"020",0), synth(50,"040",0), synth(100,"040",0),
    synth(50,"030",0), "qft_n100", "qft_n128", "bwt_n21", "ising_n26", "square_root_n45",
]

DIM_1D = [-8, -6, -4, -2, 0, 2, 4, 6]   # full range; tight grids may fail (skipped in fit)
DIM_2D = [-4, -2, 0, 2, 4]

# 1D grids (extended to 0 for the BFS regime).
CNOT_GRID_1D   = [0.0, 0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
MAPPED_GRID_1D = [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0]
# 2D grids (coarser per axis; the cross product is the cost).
CNOT_GRID_2D   = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
MAPPED_GRID_2D = [0.0, 0.4, 0.8, 1.2, 2.0, 3.0, 4.0, 6.0]

GEOM = {
    # noncube keeps BOTH non-cube safe_passage strategies, as in the historical
    # *_noncube configs (the formula is fit over both).
    "noncube": dict(safe_passage=["connectivity", "passage_no_subgraphs"],
                    confidence=0.99999, mapped_fixed=1.2, cnot_fixed=1.5),
    "cube":    dict(safe_passage=["cube"], confidence=0.999999,
                    mapped_fixed=0.8, cnot_fixed=4.5),
}

def base(strategy, geom, circuits, dims):
    g = GEOM[geom]
    return {
        "circuit": circuits,
        "type": "gaussian",
        "gaussian_strategy": [strategy],
        "safe_passage_strategy": g["safe_passage"],
        "MagicStatePlacementStrategy": ["center_circle"],
        "border_distance_percentage": 5.0,
        "MAGIC_HIGH": 1.6,
        "MAGIC_LOW": 0.0,
        "EXTERNAL_WEIGHT": 0.0,
        "BASE_GAUSSIAN_WEIGHT": 1.0,
        "GAUSSIAN_CONFIDENCE": g["confidence"],
        "number_of_magic_states": -1,
        "x": -1, "y": -1,
        "dimension_offset": dims,
        "routing_strategy": "naive",
        "t-routing-mode": "smart_t_routing",
        "timeout": 600,
        "timeout_reached": False,
    }

def write(name, cfg, comment):
    cfg = {"_comment": comment, **cfg}
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(cfg, f, indent=2)
    ncnot = len(cfg["cnot_hl_configs"])
    nmap = len(cfg["MAPPED_GAUSSIAN_WEIGHT"]) if isinstance(cfg["MAPPED_GAUSSIAN_WEIGHT"], list) else 1
    n = len(cfg["circuit"]) * len(cfg["dimension_offset"]) * ncnot * nmap * len(cfg["safe_passage_strategy"])
    print(f"  {name:<42} {n:>6} cases")
    return n

def main():
    total = 0
    for strat in ("coarse", "fine"):
        for geom in ("cube", "noncube"):
            g = GEOM[geom]
            # --- PART A: cnotdim (sweep cnot, mapped fixed) ---
            c = base(strat, geom, CIRCUITS_1D, DIM_1D)
            c["cnot_hl_configs"] = [{"CNOT_HIGH": v, "CNOT_LOW": 0.0} for v in CNOT_GRID_1D]
            c["MAPPED_GAUSSIAN_WEIGHT"] = g["mapped_fixed"]
            total += write(f"bfs_retune_cnotdim_{strat}_{geom}.json", c,
                f"PART A. BFS-regime cnot_high(d) re-tune, {strat}/{geom}. Sweeps CNOT_HIGH "
                f"(grid extended to 0) x dimension_offset, MAPPED fixed {g['mapped_fixed']}. "
                f"Mirrors gaussian_weight_tuning_cnotdim_{strat}_{geom} on the density<0.40 set.")
            # --- PART A: mappeddim (sweep mapped, cnot fixed) ---
            m = base(strat, geom, CIRCUITS_1D, DIM_1D)
            m["cnot_hl_configs"] = [{"CNOT_HIGH": g["cnot_fixed"], "CNOT_LOW": 0.0}]
            m["MAPPED_GAUSSIAN_WEIGHT"] = MAPPED_GRID_1D
            total += write(f"bfs_retune_mappeddim_{strat}_{geom}.json", m,
                f"PART A. BFS-regime mapped(d) re-tune, {strat}/{geom}. Sweeps "
                f"MAPPED_GAUSSIAN_WEIGHT x dimension_offset, CNOT_HIGH fixed {g['cnot_fixed']}. "
                f"Mirrors gaussian_weight_tuning_mappeddim_{strat}_{geom} on the density<0.40 set.")
            # --- PART B: 2D joint cnot x mapped ---
            j = base(strat, geom, CIRCUITS_2D, DIM_2D)
            j["cnot_hl_configs"] = [{"CNOT_HIGH": v, "CNOT_LOW": 0.0} for v in CNOT_GRID_2D]
            j["MAPPED_GAUSSIAN_WEIGHT"] = MAPPED_GRID_2D
            total += write(f"bfs_retune_2d_{strat}_{geom}.json", j,
                f"PART B. BFS-regime 2D joint cnot_high x mapped sweep, {strat}/{geom}, on a "
                f"responsive subset. Verifies whether the two weight optima are still separable "
                f"under BFS (the 1D methodology assumes they are). CNOT_HIGH x MAPPED cross product.")
    print(f"\nTOTAL: {total} cases across 12 configs")

if __name__ == "__main__":
    main()
