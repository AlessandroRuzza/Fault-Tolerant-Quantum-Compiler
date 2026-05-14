#!/usr/bin/env python3
"""Dimension analysis per circuit.

For each circuit in mapping_only_benchmark.json:
  1. Run every expanded configuration at x=y=-1 (auto). If any fails,
     emit '<circuit>,0,0,0,0' and move on.
  2. Compute the starting dim using compute_upper_dimensions (via a single
     --x -2 call to the binary so we don't have to replicate the formula here).
  3. Decrement current_dim by 1 and rerun every configuration at (current,current):
       - all pass     -> keep going.
       - some pass    -> if max_dim not set yet, max_dim = current + 1; keep going.
       - none pass    -> if max_dim not set yet, max_dim = current + 1;
                         min_dim = current + 1; stop.
  4. Write '<circuit>,<max>,<max>,<min>,<min>' to dimensions.csv.

Results are flushed after each circuit so the run is resumable-safe (interrupting
loses only the in-progress circuit).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
BINARY = ROOT / "build" / "FaultTolerantQuantumCompiler"
CONFIG_PATH = ROOT / "config" / "mapping_only_benchmark.json"
OUTPUT_CSV = ROOT / "benchmarks" / "results" / "dimensions.csv"

CLI_MAP = {
    "circuit": "--circuit",
    "type": "--type",
    "gaussian_strategy": "--gaussian-strategy",
    "magic_aware_strategy": "--magic-aware-strategy",
    "safe_passage_strategy": "--safe-passage",
    "MagicStatePlacementStrategy": "--magic-state-placement-strategy",
    "number_of_magic_states": "--number-of-magic-states",
    "border_distance_percentage": "--border-distance-percentage",
    "MAGIC_HIGH": "--magic-high",
    "MAGIC_LOW": "--magic-low",
    "CNOT_HIGH": "--cnot-high",
    "CNOT_LOW": "--cnot-low",
    "MAPPED_GAUSSIAN_WEIGHT": "--mapped-gaussian-weight",
    "BASE_GAUSSIAN_WEIGHT": "--base-gaussian-weight",
    "SIZE_MOLTIPLIER": "--size-moltiplier",
    "GAUSSIAN_CONFIDENCE": "--gaussian-confidence",
    "routing_strategy": "--routing-strategy",
    "t-routing-mode": "--t-routing-mode",
}

RESOLVED_RE = re.compile(r"resolved graph dimensions:\s*(\d+)x(\d+)")


def expand_configs(config: dict) -> dict[str, list[dict]]:
    circuits = config["circuit"]
    axes: dict[str, list] = {}
    fixed: dict = {}
    for key, value in config.items():
        if key == "circuit":
            continue
        if isinstance(value, list):
            axes[key] = value
        else:
            fixed[key] = value

    keys = list(axes.keys())
    values = [axes[k] for k in keys]

    by_circuit: dict[str, list[dict]] = {}
    for circuit in circuits:
        configs = []
        for combo in product(*values):
            cfg = dict(fixed)
            for k, v in zip(keys, combo):
                cfg[k] = v
            cfg["circuit"] = circuit
            configs.append(cfg)
        by_circuit[circuit] = configs
    return by_circuit


def build_cmd(cfg: dict, x: int, y: int) -> list[str]:
    cmd = [str(BINARY)]
    for k, v in cfg.items():
        flag = CLI_MAP.get(k)
        if flag is None:
            continue
        cmd.extend([flag, str(v)])
    cmd.extend(["--x", str(x), "--y", str(y)])
    return cmd


def run_one(cfg: dict, x: int, y: int, timeout: int) -> tuple[int, str]:
    """Return (exit_code, stdout). exit_code 0 = success.

    FTQC_BENCH_WORKER=1 disables shared-file artifacts (universal qasm,
    visualization dir wipe) so parallel runs don't race.
    """
    cmd = build_cmd(cfg, x, y)
    env = dict(os.environ)
    env["FTQC_BENCH_WORKER"] = "1"
    env["OMP_NUM_THREADS"] = "1"
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        return 124, ""
    except Exception as exc:
        return 1, f"PYTHON_ERROR: {exc}"


def _worker(args):
    cfg, x, y, timeout = args
    return run_one(cfg, x, y, timeout)


def run_all_parallel(configs: list[dict], x: int, y: int, timeout: int, jobs: int) -> list[tuple[int, str]]:
    if jobs <= 1 or len(configs) == 1:
        return [run_one(c, x, y, timeout) for c in configs]

    payload = [(c, x, y, timeout) for c in configs]
    results: list[Optional[tuple[int, str]]] = [None] * len(payload)
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        future_to_idx = {pool.submit(_worker, item): idx for idx, item in enumerate(payload)}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            results[idx] = future.result()
    return [r for r in results if r is not None]


def parse_resolved_dim(stdout: str) -> Optional[int]:
    matches = list(RESOLVED_RE.finditer(stdout))
    if not matches:
        return None
    return int(matches[-1].group(1))


def is_no_routable_gates(stdout: str) -> bool:
    return "no routable gates" in stdout


def get_upper_dim(cfg: dict, timeout: int) -> tuple[Optional[int], bool]:
    """Single binary call with x=-2. Returns (upper_dim, no_routable_gates_flag)."""
    exit_code, stdout = run_one(cfg, -2, -2, timeout)
    if exit_code != 0:
        return None, False
    if is_no_routable_gates(stdout):
        return None, True
    return parse_resolved_dim(stdout), False


def write_row(csv_path: Path, circuit: str, max_dim: int, min_dim: int, note: str = "") -> None:
    with csv_path.open("a") as f:
        f.write(f"{circuit},{max_dim},{max_dim},{min_dim},{min_dim},{note}\n")


def already_done_circuits(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    done = set()
    with csv_path.open() as f:
        header = f.readline()
        if not header:
            return done
        for line in f:
            parts = line.strip().split(",")
            if parts:
                done.add(parts[0])
    return done


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(CONFIG_PATH), help="path to mapping_only_benchmark.json")
    parser.add_argument("--output", default=str(OUTPUT_CSV), help="output CSV path")
    parser.add_argument("--jobs", type=int, default=8, help="parallel workers per dim level")
    parser.add_argument("--timeout", type=int, default=60, help="per-run timeout in seconds")
    parser.add_argument("--min-dim", type=int, default=2, help="lower bound for current_dim (safety floor)")
    parser.add_argument("--fresh", action="store_true", help="overwrite output CSV instead of resuming")
    parser.add_argument("--only", nargs="*", default=None, help="restrict to these circuits")
    args = parser.parse_args()

    if not BINARY.exists():
        print(f"Binary not found at {BINARY}", file=sys.stderr)
        return 1

    with open(args.config) as f:
        config = json.load(f)
    by_circuit = expand_configs(config)
    timeout = int(config.get("timeout", args.timeout))

    csv_path = Path(args.output)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if args.fresh or not csv_path.exists():
        with csv_path.open("w") as f:
            f.write("circuit,max_x,max_y,min_x,min_y,note\n")
        done = set()
    else:
        done = already_done_circuits(csv_path)

    only_set = set(args.only) if args.only else None

    for circuit, configs in by_circuit.items():
        if circuit in done:
            print(f"[skip] {circuit} (already in CSV)")
            continue
        if only_set is not None and circuit not in only_set:
            continue

        print(f"\n=== {circuit} : {len(configs)} configs ===", flush=True)

        # Step 1: probe with one config at x=-2 to get upper_dim and detect
        # 'no routable gates' circuits (only single-qubit Cliffords).
        upper_dim, no_routable = get_upper_dim(configs[0], timeout)
        if no_routable:
            print(f"  no routable gates -> 1,1,1,1 (no_routable_gates)")
            write_row(csv_path, circuit, 1, 1, "no_routable_gates")
            continue
        if upper_dim is None or upper_dim < 2:
            print(f"  could not determine upper_dim -> 0,0,0,0 (upper_dim_unknown)")
            write_row(csv_path, circuit, 0, 0, "upper_dim_unknown")
            continue
        print(f"  upper_dim={upper_dim}", flush=True)

        # Step 2: validate at upper_dim. If anything fails here, the circuit
        # is truly unmappable for this config set.
        print(f"  [dim={upper_dim}] initial validation ({args.jobs} workers)...", flush=True)
        results = run_all_parallel(configs, upper_dim, upper_dim, timeout, args.jobs)
        n_ok = sum(1 for code, _ in results if code == 0)
        n_total = len(results)
        if n_ok != n_total:
            print(f"  [dim={upper_dim}] {n_total - n_ok}/{n_total} configs failed -> 0,0,0,0 (failed_at_upper_dim)")
            write_row(csv_path, circuit, 0, 0, "failed_at_upper_dim")
            continue

        # Step 3: decrement loop
        current_dim = upper_dim
        max_dim: Optional[int] = None
        min_dim: Optional[int] = None

        while current_dim > args.min_dim:
            current_dim -= 1
            results = run_all_parallel(configs, current_dim, current_dim, timeout, args.jobs)
            n_ok = sum(1 for code, _ in results if code == 0)
            n_total = len(results)
            if n_ok == n_total:
                print(f"  [dim={current_dim}] {n_ok}/{n_total} pass", flush=True)
                continue
            elif n_ok > 0:
                print(f"  [dim={current_dim}] {n_ok}/{n_total} pass (partial)", flush=True)
                if max_dim is None:
                    max_dim = current_dim + 1
            else:
                print(f"  [dim={current_dim}] 0/{n_total} pass (stop)", flush=True)
                if max_dim is None:
                    max_dim = current_dim + 1
                min_dim = current_dim + 1
                break

        if max_dim is None:
            # all configs still pass at the safety floor
            max_dim = current_dim
        if min_dim is None:
            min_dim = current_dim

        print(f"  -> max={max_dim}, min={min_dim}", flush=True)
        write_row(csv_path, circuit, max_dim, min_dim)

    print(f"\nDone. Results in {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
