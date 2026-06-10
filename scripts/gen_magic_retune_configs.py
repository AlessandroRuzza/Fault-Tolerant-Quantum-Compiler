#!/usr/bin/env python3
"""Generate the BFS-regime MAGIC re-tuning configs.

Tunes MAGIC_HIGH and MAGIC_LOW vs border_distance_percentage for the BFS regime,
holding cnot_high/mapped at their just-found BFS optima (varied slightly up/down
to confirm the magic optimum is robust to them). cnot_low=0, external=0.

Only circuits with T/Tdg gates are included (no T -> no magic states -> magic
weights do nothing). In the bfs_retune set that is the synth_* circuits (t030)
plus bwt_n37; everything else (qft, square_root, ising, adder, ...) parses to
zero T and is excluded.

Mirrors the historical gaussian_magictune methodology (magic_hl_configs x border
x dimension) but uses ABSOLUTE BFS-optimal cnot/mapped instead of the obsolete
formula scales. Same dimension_offset as the bfs_retune suite.

Writes config/magic_retune_{coarse,fine}_{cube,noncube}.json. Run on the gated
binary at the default threshold (all circuits density<0.40 -> BFS).
"""
import json, os
OUT = os.path.join(os.path.dirname(__file__), "..", "config")

def synth(n, d, s):
    return f"synth_n{n}_d{d}_mix050_t030_hf000_hm001_r2_s{s}"

# T-bearing circuits from the bfs_retune set (verified via grep t/tdg).
CIRCUITS = [
    synth(50,"020",0), synth(50,"020",1), synth(100,"020",0), synth(100,"020",1),
    synth(200,"020",0), synth(200,"020",1),
    synth(50,"040",0), synth(50,"040",1), synth(100,"040",0), synth(100,"040",1),
    synth(200,"040",0), synth(200,"040",1),
    synth(50,"030",0),
    "bwt_n37",          # t=tdg=5600
]

DIM_OFFSET = [-8, -6, -4, -2, 0, 2, 4, 6]            # same as bfs_retune suite
MAGIC_HIGH = [0.0, 0.2, 0.4, 0.8, 1.6, 3.0, 6.0, 12.0, 20.0, 30.0]  # wide: noncube~0.2, cube~30
MAGIC_LOW  = [0.0, 0.5, 1.0, 1.5]                    # historically 0; confirm/tune under BFS
BORDER     = [0.0, 5.0, 10.0, 20.0, 30.0]

# BFS-optimal cnot_high / mapped per regime (from analyze_bfs_retune), varied slightly.
REG = {
    ("coarse", "cube"):    dict(cnot=[1.0, 1.5, 2.0], mapped=[0.0, 0.4],
                                sp=["cube"], conf=0.999999),
    ("coarse", "noncube"): dict(cnot=[1.0, 1.5, 2.0], mapped=[1.5, 2.5],
                                sp=["connectivity"], conf=0.99999),
    ("fine", "cube"):      dict(cnot=[0.3, 0.5, 1.0], mapped=[0.0, 0.4],
                                sp=["cube"], conf=0.999999),
    ("fine", "noncube"):   dict(cnot=[0.3, 0.5, 1.0], mapped=[1.0, 2.0],
                                sp=["connectivity"], conf=0.99999),
}

def magic_pairs():
    pairs = []
    for h in MAGIC_HIGH:
        for l in MAGIC_LOW:
            if l <= h:                # magic_low never above magic_high
                pairs.append({"MAGIC_HIGH": h, "MAGIC_LOW": l})
    return pairs

def main():
    total = 0
    for strat in ("coarse", "fine"):
        for geom in ("cube", "noncube"):
            r = REG[(strat, geom)]
            cfg = {
                "_comment": (
                    f"BFS-regime MAGIC re-tune, {strat}/{geom}. Sweeps MAGIC_HIGH x MAGIC_LOW x "
                    f"border, with cnot_high/mapped held at BFS optima {r['cnot']}/{r['mapped']} "
                    f"(varied slightly), cnot_low=0, external=0. Only T-bearing circuits. Same "
                    f"dimension_offset as bfs_retune. Run on the gated binary (default threshold)."),
                "circuit": CIRCUITS,
                "type": "gaussian",
                "gaussian_strategy": [strat],
                "safe_passage_strategy": r["sp"],
                "MagicStatePlacementStrategy": ["center_circle"],
                "border_distance_percentage": BORDER,
                "magic_hl_configs": magic_pairs(),
                "cnot_hl_configs": [{"CNOT_HIGH": v, "CNOT_LOW": 0.0} for v in r["cnot"]],
                "MAPPED_GAUSSIAN_WEIGHT": r["mapped"],
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
            name = f"magic_retune_{strat}_{geom}.json"
            with open(os.path.join(OUT, name), "w") as f:
                json.dump(cfg, f, indent=2)
            n = (len(CIRCUITS) * len(DIM_OFFSET) * len(cfg["magic_hl_configs"])
                 * len(BORDER) * len(cfg["cnot_hl_configs"]) * len(cfg["MAPPED_GAUSSIAN_WEIGHT"])
                 * len(r["sp"]))
            print(f"  {name:<36} {n:>7} cases  (magic_pairs={len(cfg['magic_hl_configs'])})")
            total += n
    print(f"\nTOTAL: {total} cases across 4 configs ({len(CIRCUITS)} T-circuits)")

if __name__ == "__main__":
    main()
