# Fault-Tolerant-Quantum-Compiler

Fault-Tolerant-Quantum-Compiler is a C++20 project that parses OpenQASM circuits, maps them onto a target architecture with configurable strategies, and performs routing with several selectable strategies (congestion-aware, naive, naive-critical, packing, and an optional Boost-based router).

The repository also includes:
- Benchmark execution from JSON configs.
- Automatic benchmark CSV and log generation.
- Utilities to merge/plot benchmark results.
- Optional graph and Gaussian visualization tooling.

## Repository layout

Main directories you will use most often:

- `src/`, `include/`: core compiler implementation.
- `qasms/`: input OpenQASM circuits.
- `config/`: single-run config files and benchmark JSONs.
- `graphs/`: graph descriptions in JSON.
- `universal_set_qasms/`: generated translated QASM output.
- `benchmarks/results/`: benchmark CSV outputs.
- `benchmarks/logs/`: per-run benchmark logs.
- `scripts/`: helper scripts for benchmark execution and analysis.
- `visualization/`: generated visualization outputs (cleaned at each normal run).

## Prerequisites

Build/runtime requirements:

- CMake 3.15+
- C++20 compiler (g++ or clang++)
- Eigen3 (required by CMake)

Bundled dependency:

- nlohmann/json is vendored under `external/nlohmann_json/`.

Optional tools used by specific flows:

- OpenMP runtime/library for parallel benchmark execution.
- `timeout` (GNU coreutils) for benchmark timeout support.
- `gnuplot` for Gaussian frame plotting.
- `ffmpeg` for the `make-video` target.
- Python 3 for scripts in `scripts/`.

Python packages for analysis scripts:

```bash
pip install -r requirements.txt
```

## Build (build folder + cmake + make)

From repository root:

```bash
mkdir -p build
cd build
cmake ..
make -j
```

This produces at least:

- `build/FaultTolerantQuantumCompiler`
- `build/graph_viewer`

## Basic usage

Recommended: run the executable from `build/` so default relative paths resolve as intended.

Run help from `build/`:

```bash
cd build
./FaultTolerantQuantumCompiler --help
```

The executable supports:

- Single execution mode (default; QASM/config driven).
- Benchmark mode through `--bench_path`, `--bench-path`, or `--bench`.

Configuration precedence in single execution mode:

1. CLI flags
2. Config file (`--config`)
3. Hardcoded defaults

## Run a single QASM file

From `build/`:

```bash
./FaultTolerantQuantumCompiler --circuit example
```

Also valid:

```bash
./FaultTolerantQuantumCompiler --circuit example.qasm
./FaultTolerantQuantumCompiler --circuit /absolute/path/to/my_circuit.qasm
```

By default, bare names are resolved under `qasms/`.

You can add other strategy flags as needed, for example:

```bash
./FaultTolerantQuantumCompiler \
	--circuit qft_20 \
	--type magic_aware \
	--magic-aware-strategy distance \
	--routing-strategy congestion
```

## Run a single config JSON

Single-run config files are JSON objects (for example `config/0_compiler_config.json`).

Use benchmark-style configs with arrays (for example `config/ex1.json`) only in benchmark mode.

From `build/`:

```bash
./FaultTolerantQuantumCompiler --config ../config/0_compiler_config.json
```

You can still override config values from CLI:

```bash
./FaultTolerantQuantumCompiler \
	--config ../config/0_compiler_config.json \
	--circuit dnn_n16 \
	--routing-strategy naive
```

## Tuned Gaussian mapping parameters

Recommended parameter values for the Gaussian mapping, grouped by *regime* — the
combination of `gaussian_strategy` (`coarse` / `fine`) and `safe_passage_strategy`
(`cube` / `connectivity`). `cube` yields shorter routes but needs a larger
lattice; `connectivity` packs onto smaller lattices.

Common to all configurations:

| Parameter | Value | Note |
|---|---|---|
| `EXTERNAL_WEIGHT` | `0` | |
| `BASE_GAUSSIAN_WEIGHT` | `1` | |
| `CNOT_LOW` | `0` | |
| `number_of_magic_states` | `-1` | auto |
| `MagicStatePlacementStrategy` | `center_circle` | with `border_distance_percentage` |
| `routing_strategy` / `t-routing-mode` | `naive` / `smart_t_routing` | |

Border-independent weights:

| Regime (`gaussian_strategy` / `safe_passage_strategy`) | `GAUSSIAN_CONFIDENCE` | `CNOT_HIGH` | `MAPPED_GAUSSIAN_WEIGHT` | `MAGIC_LOW` |
|---|---|---|---|---|
| coarse / cube | 0.999999 | 1.5 | 0 | 0 |
| coarse / connectivity | 0.99999 | 1.5 | 2.0 | 0 |
| fine / cube | 0.999999 | 0.5 | 0 | 1 † |
| fine / connectivity | 0.99999 | 0.5 | 1.5 | 0 |

`MAGIC_HIGH` depends on `border_distance_percentage` (`b`, in %):

| Regime | `b=0` | `b=5` | `b=10` | `b=20` | `b=30` |
|---|---|---|---|---|---|
| coarse / cube | 0 | 0.2 | 0.2 | 0.2 | 1.6 |
| coarse / connectivity | 0 | 0.2 | 0.8 | 0.8 | 0.2 |
| fine / cube | 20 ‡ | 3 | 1.6 | 0 | 0 |
| fine / connectivity | 3 | 1.6 | 0.4 | 0.4 | 0.2 |

† `MAGIC_LOW` = 1 for `border_distance_percentage` ≤ 10, else 0 (fine / cube only).
‡ Robust argmin is 20, but the curve is flat above ~1.6.

### Example: `cube` vs `connectivity` on `ising_n420`

The "`cube` routes better, `connectivity` packs smaller" rule above is a
tendency, not a law. `ising_n420` is a counterexample where `connectivity` wins
on *both* axes — it routes optimally on a much smaller lattice (gaussian mapping,
`naive_critical` routing):

| Config | Grid | Routing steps | Avg parallelism | Non-routed | Exec. time |
|---			 |---	 |---	 |---				 |---	  |---	   |
| `cube`         | 42×42 | 5     | 167.6 / 209.5     | 2.51%  | 0.21 s |
| `connectivity` | 24×24 | **4** | **209.5 / 209.5** | **0%** | 0.28 s |
| WISQ           | 45x45 | 43    | —                 | —      | 93 s   |

`connectivity` reaches full parallelism (209.5 / 209.5) with zero non-routed
layers in 4 steps on a 24×24 grid, while `cube` needs 42×42 yet takes 5 steps and
leaves 2.5% of gates in layers unrouted. This is **circuit-specific**: for most circuits
`cube` still gives the shorter routes — `ising_n420` is an exception, not the rule.

Both configs also dwarf the external WISQ compiler on this circuit: ~4–5 routing
steps in ~0.2–0.3 s versus WISQ's **43 steps in 93 s** (≈10× fewer steps, ≈300×
faster).

## Routing strategies

Pick the corridor router with `--routing-strategy <name>` (aliases also accepted:
`--routing`, `--routing-method`) or the `routing_strategy` config field. The
default is `naive_critical` (simple, fast, and competitive across circuit classes).

**No router is universally best.** The strongest strategy is circuit-specific:
`packing` usually opens the most parallel corridors on *contended* circuits, but
on structured/regular circuits a simpler ordering can win — on `qft_n200`,
`naive_critical` beats `packing` by ~12% fewer steps while routing ~10× faster
(see the example below). Benchmark a couple of strategies per circuit class
rather than assuming one wins everywhere.

| Strategy (aliases) | What it does |
|---|---|
| `congestion` (`congestion_aware`) | Shortest-path corridors with a congestion penalty (scale `0.35`, static global) that steers paths away from already-busy nodes. Gates routed one-by-one, shortest operand-distance first. |
| `naive` | Plain shortest-path corridors, no congestion penalty. Gates routed one-by-one, shortest operand-distance first. |
| `naive_critical` (`critical`, `naivecritical`) | Same shortest-path routing as `naive`, but orders each layer's gates by **criticality** (dependency-chain tail length) first, operand distance second, so gates on the critical path claim corridors first. **Default.** |
| `packing` (`pack`, `disjoint`, `disjoint_paths`) | Maximises the set of **vertex-disjoint** corridors opened per layer instead of routing greedily one-by-one. Per layer: (1) generate up to `k` candidate paths per gate (penalised re-search for 2-qubit gates, nearest free magic states for T gates); (2) greedily select a conflict-free subset, prioritising **downstream criticality** (how many of the next `L` layers touch the gate's qubits), ties broken by shorter path; (3) a fill pass routes any still-unrouted gate on a fresh disjoint path, so each step is always maximal. Routes more gates per step → usually fewer routing steps on contended circuits (not universal; see below). |
| `boost` | Boost Graph Library-based router. Only available when the binary is built with Boost support; otherwise it errors out. |

> **Operand distance** is the length of a *trial* shortest path between a gate's two
> operand tiles on the free lattice, computed before the layer's corridors are committed.
> A compile-time flag (`ORDER_GATES_BY_MANHATTAN`, off by default) swaps it for plain
> Manhattan distance between the two tiles.

### Packing tunables

Defaults are the tuned values (`k=2`, `L=4`, tuned on a `qft`/`qaoa`/`randomcircuit`
n50–n100 sweep); override via environment only when re-deriving them in a sweep:

| Env var | Default | Meaning |
|---|---|---|
| `FTQC_PACKING_CANDIDATES` | `2` | `k`: candidate paths generated per gate |
| `FTQC_PACKING_LOOKAHEAD` | `4` | `L`: layers of downstream lookahead for the criticality weight |

### T-gate routing

Independently of the corridor strategy, magic-state delivery for T gates uses one
of two modes via `--t-routing-mode` (or the `t_routing_mode` config field):

- `smart_t_routing` — when no magic state is reachable, defers the T gate and
  retries it in a later step, up to `--patience-threshold <n>` (integer `≥ 0`)
  deferrals before giving up.
- `normal_t_routing` — routes to the nearest free magic state immediately, no deferral.

### Example: when packing loses (`qft_n200`)

`packing` usually opens more disjoint corridors per step on contended circuits,
so it is the strongest choice there — but it is not universally best. On
`qft_n200` (gaussian mapping, `cube`, same 31×31 grid for both), the simpler
`naive_critical` routes better on *every* axis:

| Router (cube) | Routing steps | Avg parallelism | Non-routed | Routing time |
|---|---|---|---|---|
| `naive_critical` | **1192** | **6.36 / 9.55** | **22.3%** | **0.16 s** |
| `packing`        | 1360     | 5.57 / 9.55     | 23.9%      | 1.62 s     |

`naive_critical` (and plain `naive`, which behaves similarly here) gets ~12% fewer
steps, higher parallelism, and fewer non-routed layers — while routing ~10×
faster, since packing's per-gate candidate search and criticality selection are
pure overhead when they don't improve the packing. **Rule of thumb:** packing for
contended circuits, but benchmark `naive_critical` on regular/structured ones like
QFT.

Note the safe-passage interaction too: under `connectivity` (26×26) both routers
collapse on `qft_n200` — `packing` balloons to 4769 steps with 64.6% non-routed
layers. So QFT strongly prefers `cube`, the exact opposite of `ising_n420` above.
Both safe-passage **and** router choice are circuit-specific.

## Run benchmarks through JSON in config/

Benchmark mode expands and runs combinations defined in a benchmark JSON (for example `config/ex1.json`).

### Direct binary usage

From `build/`:

```bash
./FaultTolerantQuantumCompiler --bench ex1
```

To limit or increase benchmark parallelism, set `OMP_NUM_THREADS`:

```bash
OMP_NUM_THREADS=8 ./FaultTolerantQuantumCompiler --bench ex1
```

Equivalent aliases:

```bash
./FaultTolerantQuantumCompiler --bench_path ex1
./FaultTolerantQuantumCompiler --bench-path ex1
```

You can also pass values like `config/ex1.json`; the runner extracts the benchmark name and resolves it in `config/`.

### Rerun only timed-out cases

```bash
./FaultTolerantQuantumCompiler --bench ex1 --rerun-timeouts
```

Or:

```bash
./FaultTolerantQuantumCompiler --bench ex1 --rerun-timeouts=true
```

### Make target usage

From `build/`:

```bash
make run-bench BENCH_PATH=ex1
```

To control benchmark parallelism from the make target:

```bash
make run-bench BENCH_PATH=ex1 BENCH_JOBS=8
```

To control the round-robin `process` field written into the expanded JSON, use a separate process count:

```bash
./FaultTolerantQuantumCompiler --bench ex1 --process-count 4
make run-bench BENCH_PATH=ex1 BENCH_PROCESS_COUNT=4
```

With timeout rerun enabled:

```bash
make run-bench BENCH_PATH=ex1 RERUN_TIMEOUTS=1
```

You can combine both:

```bash
make run-bench BENCH_PATH=ex1 RERUN_TIMEOUTS=1 BENCH_JOBS=8
```

## Where execution results are written

### 1) Single QASM run

- Console output: printed to terminal (routing steps, average parallelism, selected options).
- Generated universal-set circuit:
	- `universal_set_qasms/<circuit_name>_universal.qasm`
- Visualization artifacts (if produced by the selected flow):
	- `visualization/` and `visualization/gaussian_frames/`

Note: each single execution starts by cleaning previous generated files in `visualization/` (except `visualization/README.md` and `visualization/graph_viewer.cpp`).

### 2) Single config run

Same output locations as single QASM run:

- Terminal summary.
- `universal_set_qasms/<circuit_name>_universal.qasm`
- `visualization/` generated artifacts.

### 3) Benchmark run

Benchmark mode writes persistent artifacts in three places:

- Expanded benchmark definition with execution state:
	- `config/executed/<bench_name>_expanded.json`
	- Includes fields like `id`, `executed`, and `timeout_reached` per expanded case.

- Per-run logs:
	- `benchmarks/logs/run_<run_id>_<case_id>.log`

- Aggregated benchmark CSV:
	- `benchmarks/results/<bench_name>_runs.csv`

CSV rows include status fields such as `status`, `exit_code`, `duration_seconds`, `timeout_reached`, `routing_steps`, and log path.

Benchmark workers disable shared visualization/QASM artifact generation so parallel runs do not interfere with each other; logs and CSV outputs remain the persistent benchmark outputs.

## Benchmark JSON notes

Benchmark JSON files in `config/` can define parameter sweeps using arrays.

Example benchmark file:

- `config/ex1.json`

Expansion output:

- `config/executed/ex1_expanded.json`

Each expanded case is executed once unless already marked `executed=true`.

If `timeout` is set in a case, execution is wrapped with `timeout`; timed-out runs are recorded in CSV as `status=timeout` and can be selectively rerun with `--rerun-timeouts`.

## Analyze benchmark outputs

Merge multiple benchmark CSVs and generate plots:

```bash
python3 scripts/merge_and_plot_results.py
```

Defaults:

- input dir: `benchmarks/results/`
- merged CSV: `benchmarks/results/merged_runs.csv`
- plots dir: `benchmarks/results/plots/`

Generate plots from a single benchmark CSV:

```bash
python3 scripts/generate_benchmark_plots.py --csv benchmarks/results/ex1_runs.csv
```

Default output for single-CSV mode:

- `benchmarks/results/<csv_name_without_extension>_plots/`

Create a readable CSV view from one benchmark CSV:

```bash
python3 scripts/make_readable_csv.py benchmarks/results/ex1_runs.csv
```

Default output:

- `tmp/<input_name>_readable.csv`

## Other useful CMake targets

From `build/`:

- Run main executable:

```bash
make run-main
```

- Run graph viewer test mode:

```bash
make run-graph-viewer
```

This generates/opens a graph HTML view. In `--test` mode (used by this target), the file is `graph_view.html` in the repository root.

- Build Gaussian animation video and GIF (requires ffmpeg):

```bash
make make-video
```

Outputs:

- `visualization/gaussians_2fps.mp4`
- `visualization/gaussians_2fps.gif`

## Quick command recap

Build:

```bash
mkdir -p build && cd build && cmake .. && make -j
```

Single QASM:

```bash
cd build
./FaultTolerantQuantumCompiler --circuit example
```

Single config:

```bash
cd build
./FaultTolerantQuantumCompiler --config ../config/0_compiler_config.json
```

Benchmark from config JSON:

```bash
cd build
./FaultTolerantQuantumCompiler --bench ex1
```

Benchmark via make target:

```bash
cd build
make run-bench BENCH_PATH=ex1
```
