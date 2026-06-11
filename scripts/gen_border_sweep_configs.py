#!/usr/bin/env python3
"""Quick BORDER sweep — which border_distance_percentage is best (BFS regime).

All other weights pinned at their tuned BFS optima (see pesi_tunati.md); the only
swept axis is border. Border only affects circuits WITH T gates (it positions the
magic states), so we use the same 14 T-bearing circuits as the magic re-tune.

magic_high is swept over {0.4, 1.6} (both low, the absolute-best regime) so the
border comparison is not biased by a single fixed magic value; magic_low=0
(its effect is <0.16pp, irrelevant for "which border"). cnot/mapped held at the
per-regime optimum. Run on the gated binary (default threshold density<0.40).

Writes a single config/border_sweep.json holding a JSON array of the 4 fully
pinned regime blocks (the runner expands each array entry independently, so
per-regime weights stay pinned; cf. expand_config_variants.hpp).
"""
import json, os
OUT = os.path.join(os.path.dirname(__file__), "..", "config")

def synth(n, d, s):
    return f"synth_n{n}_d{d}_mix050_t030_hf000_hm001_r2_s{s}"

# exact T-bearing set proven to run (from magic_retune results).
CIRCUITS = [
    synth(50,"020",0), synth(50,"020",1), synth(100,"020",0), synth(100,"020",1),
    synth(200,"020",0), synth(200,"020",1),
    synth(50,"040",0), synth(50,"040",1), synth(100,"040",0), synth(100,"040",1),
    synth(200,"040",0), synth(200,"040",1),
    synth(50,"030",0),
    "bwt_n37",
]

BORDER     = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0]   # the axis of interest
DIM_OFFSET = [-8, -6, -4, -2, 0, 2, 4, 6]                     # robustness over dim
MAGIC_HL   = [{"MAGIC_HIGH": 0.4, "MAGIC_LOW": 0.0},
              {"MAGIC_HIGH": 1.6, "MAGIC_LOW": 0.0}]          # guard vs fixed-magic bias

# per-regime tuned optima (pesi_tunati.md)
REG = {
    ("coarse", "cube"):    dict(cnot=1.5, mapped=0.0, sp=["cube"],         conf=0.999999),
    ("coarse", "noncube"): dict(cnot=1.5, mapped=2.0, sp=["connectivity"], conf=0.99999),
    ("fine",   "cube"):    dict(cnot=0.5, mapped=0.0, sp=["cube"],         conf=0.999999),
    ("fine",   "noncube"): dict(cnot=0.5, mapped=1.5, sp=["connectivity"], conf=0.99999),
}

def main():
    blocks, total = [], 0
    for strat in ("coarse", "fine"):
        for geom in ("cube", "noncube"):
            r = REG[(strat, geom)]
            cfg = {
                "_comment": (
                    f"BORDER sweep, {strat}/{geom}. Only border varies; cnot={r['cnot']}, "
                    f"mapped={r['mapped']}, cnot_low=0, external=0, magic_high in {{0.4,1.6}}, "
                    f"magic_low=0. T-bearing circuits only. Gated binary (density<0.40)."),
                "circuit": CIRCUITS,
                "type": "gaussian",
                "gaussian_strategy": [strat],
                "safe_passage_strategy": r["sp"],
                "MagicStatePlacementStrategy": ["center_circle"],
                "border_distance_percentage": BORDER,
                "magic_hl_configs": MAGIC_HL,
                "cnot_hl_configs": [{"CNOT_HIGH": r["cnot"], "CNOT_LOW": 0.0}],
                "MAPPED_GAUSSIAN_WEIGHT": [r["mapped"]],
                "EXTERNAL_WEIGHT": 0.0,
                "BASE_GAUSSIAN_WEIGHT": 1.0,
                "GAUSSIAN_CONFIDENCE": r["conf"],
                "number_of_magic_states": -1,
                "x": -1, "y": -1,
                "dimension_offset": DIM_OFFSET,
                "routing_strategy": "naive",
                "t-routing-mode": "smart_t_routing",
                "timeout": 600,
                "timeout_reached": False,
            }
            blocks.append(cfg)
            n = (len(CIRCUITS) * len(BORDER) * len(DIM_OFFSET) * len(MAGIC_HL)
                 * len(cfg["cnot_hl_configs"]) * len(cfg["MAPPED_GAUSSIAN_WEIGHT"])
                 * len(r["sp"]))
            print(f"  {strat}/{geom:<8} {n:>6} runs")
            total += n
    name = "border_sweep.json"
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(blocks, f, indent=2)
    print(f"\n-> {name} ({len(blocks)} regime blocks in one array)")
    print(f"TOTAL: {total} runs ({len(CIRCUITS)} T-circuits, "
          f"borders={[int(b) for b in BORDER]})")

if __name__ == "__main__":
    main()
