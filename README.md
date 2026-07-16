# Fault-Tolerant Quantum Compiler - Gaussian Potential-Field mapping

Fault-Tolerant-Quantum-Compiler is a C++20 project that parses OpenQASM circuits, maps them onto a target architecture with configurable strategies, and performs routing with several selectable strategies (congestion-aware, naive, naive-critical, packing, critical-packing, and an optional Boost-based router).

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
- `out/`: routed circuits written by each run (gitignored).
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
2. Config file (`--config`, defaulting to `config/0_compiler_config.json`)
3. Hardcoded defaults (`src/main.cpp`)

Both layers 2 and 3 already hold the tuned optimal parameters, so passing nothing
is a valid, well-tuned run — see
[The default config file](#the-default-config-file) and
[Every configurable parameter](#every-configurable-parameter).

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

Use benchmark-style configs with arrays (for example `config/all_circuits.json`) only in benchmark mode.

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

### The default config file

`config/0_compiler_config.json` **is the default config**: it is loaded
automatically when you don't pass `--config`, and it is resolved from the
repository root (`PROJECT_ROOT`), not from the current directory — so it applies
no matter where you launch the binary from.

Its values are the **tuned optima** from
[`results/pesi_finali.md`](results/pesi_finali.md) (the `connectivity` column),
mirrored by the hardcoded defaults in `src/main.cpp`. **Running with no options
at all already compiles with the best-known configuration**, so in practice you
only need to specify the *circuit* and, optionally, the *grid dimension*:

```bash
./FaultTolerantQuantumCompiler --circuit qft_n100 --x 30 --y 30
```

The grid is in fact optional too. With the default `x = y = -1` the lattice is
**auto-sized** from the qubit count and the circuit's interaction degree. That
heuristic has a good chance of landing on a workable grid, but it is **not a
guarantee** — grid size is the single dominant lever on `non_routed` (see
[Tuned Gaussian mapping parameters](#tuned-gaussian-mapping-parameters)), so if
a run leaves layers unrouted, pin `--x`/`--y` explicitly or pad the auto grid
with `dimension_offset`.

### Routed-circuit output

Every single run writes the routed circuit — the compiler's actual product, as
opposed to the step counts and metrics it *reports* — as JSON:

```bash
./FaultTolerantQuantumCompiler --circuit adder_n4          # -> out/route.json
./FaultTolerantQuantumCompiler --circuit adder_n4 --output-path adder/run1
                                                            # -> out/adder/run1.json
```

Relative paths resolve under `<project_root>/out/`, **not** the working
directory: runs are normally launched from `build/`, and anchoring to the CWD
would bury the output there. Absolute paths are used verbatim, a missing `.json`
extension is appended, intermediate directories are created, and `out/` is
gitignored. Set `output_path` to `""` in a config to turn the dump off.

Benchmark workers never write it, the same way they skip the universal-QASM and
`.graph` artifacts: they run dozens-way parallel onto one shared path, so they
would clobber each other's dump. Benchmark outputs stay the logs and CSV — see
[Benchmark run](#3-benchmark-run).

The schema encodes positions as flat row-major indices and carries no edge list,
which matches the only topology the compiler accepts — see
[Supported graphs](#supported-graphs).

The file uses the same schema as WISQ's `--mode scmr` output, so the tools that
already read a WISQ result read ours unchanged — for example
`python scripts/plots/visualize_wisq_steps.py -i out/route.json -o frames/`,
which renders each step and checks the paths are node-disjoint:

| Field | Meaning |
|---|---|
| `map` | `[[logical_qubit, node], ...]` — where the mapper placed each qubit |
| `arch` | `{"width", "height", "alg_qubits", "magic_states"}` |
| `steps` | one entry per routing step; each is a list of `{"id", "op", "qubits", "path"}` routed in parallel on that step |
| `gates` | the routed gate list (post T-decomposition, as in `universal_set_qasms/`) |

Nodes are flat row-major grid indices (`node = y * width + x`). `arch.alg_qubits`
lists the nodes *holding* a logical qubit: WISQ picks its data qubits from a
fixed even/even sublattice, our mapper chooses them, so the field means
"occupied slots" rather than "available slots". With `repetition > 1` the dump is
the best repetition — the one the reported metrics describe. Gates are sorted by
`id`, so the same configuration always produces a byte-identical file.

Size scales with the step count (one path per gate per step), so it grows fast:
`bwt_n21` routes in 116400 steps and dumps 55 MB. Point `--output-path` somewhere
roomy — or disable it — before looping over large circuits by hand.

### Supported graphs

The target architecture is always a **generated rectangular grid**, sized from
`x`/`y` (or `dimension_offset`). External graphs cannot be passed: both `--graph`
and the `graph` config key are refused.

```
Error: --graph is not supported: the target architecture is always a generated
rectangular grid. Size it with --x/--y (or dimension_offset).
```

### Every configurable parameter

Each parameter can be set **either** as a key in the config JSON **or** as a CLI
flag — they are interchangeable, and CLI wins over the file (see
[precedence](#basic-usage)). Config keys are accepted in both `UPPER_CASE` and
`lower_case` spelling for the weights, and CLI flags accept `-` or `_` as
separator.

| Config key | CLI flag (aliases) | Values | Default |
|---|---|---|---|
| `circuit` | `--circuit` | name, `name.qasm`, or absolute path; bare names resolve under `qasms/` | `ising_n420` ‡ |
| `type` | `--type` | `magic_aware` \| `gaussian` \| `random` | `gaussian` |
| `gaussian_strategy` | `--gaussian-strategy` | `coarse` \| `fine` | `fine` |
| `magic_aware_strategy` | `--magic-aware-strategy` | `distance` \| `center` \| `random` (only for `type=magic_aware`) | `distance` |
| `safe_passage_strategy` | `--safe-passage` | `passage` \| `passage_no_subgraphs` \| `cube` \| `connectivity` | `connectivity` |
| `MagicStatePlacementStrategy` | `--magic-state-placement-strategy` (`--MagicStatePlacementStrategy`) | `right_row` \| `center_circle` | `center_circle` |
| `number_of_magic_states` | `--number-of-magic-states` (`--NumberOfMagicStates`) | `-1` = proportional to circuit \| integer = exact count \| `0<f<1` = multiplier | `-1` |
| `border_distance_percentage` | `--border-distance-percentage` (`--BorderDistancePercentage`) | float in `[0,100]` | `15` |
| `x` | `--x` | `>0` exact \| `0` heuristic upper bound \| `-1` auto-size (`< -1` rejected) | `-1` |
| `y` | `--y` | same sentinels as `x` | `-1` |
| `dimension_offset` | — (config only) | signed delta on the auto-sized grid (`<0` tighter, `>0` padded); applies only when `x`/`y` are `-1` | `0` |
| `MAGIC_HIGH` | `--magic-high` | float `>= 0`; must be `>= MAGIC_LOW` | `0` |
| `MAGIC_LOW` | `--magic-low` | float `>= 0` | `0` |
| `CNOT_HIGH` | `--cnot-high` | float `>= 0`, or `-1` = auto formula (per circuit family × grid size); must be `>= CNOT_LOW` | `8` |
| `CNOT_LOW` | `--cnot-low` | float `>= 0`, or `-1` = auto | `0` |
| `MAPPED_GAUSSIAN_WEIGHT` | `--mapped-gaussian-weight` | float `>= 0`, or `-1` = auto formula | `20` |
| `BASE_GAUSSIAN_WEIGHT` | `--base-gaussian-weight` | float `>= 0` | `1` |
| `EXTERNAL_WEIGHT` | `--external-weight` | any finite float (negative is the useful range) | `-15` |
| `GAUSSIAN_SIGMA` | `--gaussian-sigma` | float `> 0`; absolute stddev, same on both axes | `0.7` |
| `CNOT_FORMULA_SCALE` | — (config only) | float; scales the `CNOT_HIGH: -1` auto formula | `1.0` |
| `MAPPED_FORMULA_SCALE` | — (config only) | float; scales the `MAPPED_GAUSSIAN_WEIGHT: -1` auto formula | `1.0` |
| `bfs_density_threshold` | `--bfs-density-threshold` | float; CNOT-graph density below which CNOT-BFS mapping order is used, `<0` = always heap. Env `FTQC_BFS_DENSITY_THRESHOLD` overrides everything | `0.70` |
| `routing_strategy` | `--routing-strategy` (`--routing`, `--routing-method`) | `congestion` \| `naive` \| `naive_critical` \| `packing` \| `critical_packing` \| `greedy_lookahead` \| `dascot_sa` \| `boost` † | `naive_critical` |
| `t-routing-mode` | `--t-routing-mode` | `normal_t_routing` \| `smart_t_routing` | `smart_t_routing` |
| `patience_threshold` | `--patience-threshold` | integer `>= 0`; T-gate deferrals allowed under `smart_t_routing` | `3` |
| `packing_commute` | `--packing-commute` | `true` \| `false`; commutation-aware frontier, read only by `packing` / `critical_packing` | `false` |
| `layering_commute` | `--layering-commute` | `true` \| `false`; commutation-aware layering, affects every router | `false` |
| `use_layer_cache` | `--use-layer-cache` | `true` \| `false` | `true` |
| `repetition` | `--repetition` (`--repeat`, `--rep`) | integer `> 0`; repeats the run (useful for `random`) | `1` |
| — | `--metrics-only` | flag (CLI only); suppresses artifact generation, prints metrics only | off |
| `output_path` | `--output-path` (`--output_path`) | where to write the routed circuit as JSON (see [Routed-circuit output](#routed-circuit-output)); relative paths resolve under `out/`, `.json` is appended if missing, `""` disables the dump | `route.json` → `out/route.json` |
| `graph` | `--graph` | **not supported** — the grid is always generated, see [Supported graphs](#supported-graphs); passing either is an error | — |
| — | `--config` | path to a single-run config JSON | `config/0_compiler_config.json` |

† `boost` only exists when the binary is built with Boost support. See
[Routing strategies](#routing-strategies) for what each router does, and
[Packing tunables](#packing-tunables) for the two `packing` env vars
(`FTQC_PACKING_CANDIDATES`, `FTQC_PACKING_LOOKAHEAD`).

‡ The "Default" column is what you get from an argument-less run, i.e. the config
file's value. For `circuit` that is `ising_n420` (the config sets it); the
hardcoded fallback in `src/main.cpp`, used only if the config file is missing or
omits the key, is `qasms/example.qasm`. Every other default is identical in both
layers.

## Tuned Gaussian mapping parameters

Recommended Gaussian-mapping parameters, by *safe-passage regime*: `cube` yields
shorter routes but needs a larger lattice, `connectivity` packs onto smaller
lattices. These are the consolidated optima from the weight sweeps; the full
per-parameter reasoning, metric trade-offs, and correlation analysis live in
[`results/pesi_tunati.md`](results/pesi_tunati.md) (final summary in
[`results/pesi_finali.md`](results/pesi_finali.md)).

The **`connectivity` column is what the binary ships as its default** — both the
hardcoded defaults in `src/main.cpp` and `config/0_compiler_config.json` — so you
only need this table when switching to `cube` or re-tuning. See
[The default config file](#the-default-config-file).

| Parameter | `connectivity` | `cube` |
|---|---|---|
| `type` | `gaussian` | `gaussian` |
| `gaussian_strategy` | `fine` | `fine` |
| `safe_passage_strategy` | `connectivity` | `cube` |
| `EXTERNAL_WEIGHT` | −15 | −15 |
| `BASE_GAUSSIAN_WEIGHT` | 1 | 1 |
| `GAUSSIAN_SIGMA` | 0.7 | 0.7 |
| `MAPPED_GAUSSIAN_WEIGHT` | 20 | 15 |
| `CNOT_HIGH` | 8 | 6 |
| `CNOT_LOW` | 0 | 0 |
| `MAGIC_HIGH` | 0 | 0.7 |
| `MAGIC_LOW` | 0 | 0 |
| `border_distance_percentage` | 15 | 5 |
| `MagicStatePlacementStrategy` | `center_circle` | `center_circle` |
| `number_of_magic_states` | −1 (auto) | −1 (auto) |
| `bfs_density_threshold` | 0.70 | 0.70 |
| `routing_strategy` | `packing` † | `packing` † |
| `t-routing-mode` | `smart_t_routing` | `smart_t_routing` |
| `patience_threshold` | 3 | 3 |
| `use_layer_cache` | `true` | `true` |

Key points from the sweeps:

- **Grid size is the dominant lever** — `non_routed` moves ~8–9pp (connectivity) /
  ~2–3pp (cube) from a tight to a padded lattice, versus ≤1.4pp for *all* weights
  combined. Pad generously (`dimension_offset` 6–12) and don't re-tune the weights
  per size.
- **`MAPPED_GAUSSIAN_WEIGHT` and `CNOT_HIGH` ride a ridge** `cnot ≈ mapped / 2.5` —
  tune them together, never `mapped` alone. `GAUSSIAN_SIGMA ≈ 0.7` stays roughly
  constant along the ridge (widen it only on very tight lattices).
- **`EXTERNAL_WEIGHT` saturates** — any negative value is near-optimal; `0` costs
  ~1.5pp on connectivity.
- **`MAGIC_HIGH` / `MAGIC_LOW` / `CNOT_LOW` are inert** for `non_routed`, so keep
  them at 0 (cube's `MAGIC_HIGH = 0.7` only buys ~0.3–0.5% on `routing_steps`,
  nothing on `non_routed`). The old "wider border → higher magic" rule was an
  artifact, not a real effect.

† `routing_strategy`: the table lists `packing`, which minimises **routing steps**
on large circuits. For **non_routed** (the primary metric) and compile time,
`naive` / `naive_critical` is the more robust choice — it ties or beats packing on
non_routed and runs 12–18× faster with no timeouts. **`naive_critical` is
therefore the shipped default**, the one point where the defaults deviate from
this table; pass `--routing-strategy packing` when routing steps are what you
care about. See [Routing strategies](#routing-strategies) for the trade-off.

> `GAUSSIAN_CONFIDENCE` (a confidence value from which sigma was derived) was
> removed; the mapping now takes the absolute `GAUSSIAN_SIGMA` directly.

### Example: `cube` vs `connectivity` on `ising_n420`

The "`cube` routes better, `connectivity` packs smaller" rule above is a
tendency, not a law. `ising_n420` is a counterexample where `connectivity` wins
on *both* axes — it routes optimally on a much smaller lattice (gaussian mapping,
`naive_critical` routing):

| Config | Grid | Routing steps | Avg parallelism | Non-routed | Exec. time |
|---|---|---|---|---|---|
| `cube`         | 42×42 | 5     | 167.6 / 209.5     | 2.51%  | 0.21 s |
| `connectivity` | 24×24 | **4** | **209.5 / 209.5** | **0%** | 0.28 s |
| WISQ           | 45×45 | 43    | —                 | —      | 93 s   |

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
| `packing` (`pack`, `disjoint`, `disjoint_paths`) | Maximises the set of **vertex-disjoint** corridors opened per layer instead of routing greedily one-by-one. Per layer: (1) generate up to `k` candidate paths per gate (penalised re-search for 2-qubit gates, nearest free magic states for T gates); (2) greedily select a conflict-free subset, prioritising **downstream pressure** (how many of the next `L` layers touch the gate's qubits), ties broken by shorter path; (3) a fill pass routes any still-unrouted gate on a fresh disjoint path, so each step is always maximal. Routes more gates per step → usually fewer routing steps on contended circuits (not universal; see below). |
| `critical_packing` (`crit_packing`, `critpacking`) | Same per-layer disjoint-path packing as `packing`, but gates are prioritised by their true **critical-path length** (longest dependency-chain tail), keeping the downstream pressure only as the tiebreak. Recovers the step count on long serial cascades (e.g. QFT), where packing's short-lookahead pressure misses chain depth; on circuits with flat tails (e.g. QAOA) it reduces to plain `packing` behaviour. |
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
| `FTQC_PACKING_LOOKAHEAD` | `4` | `L`: layers of downstream lookahead for the pressure weight |

Both `packing` and `critical_packing` also accept `--packing-commute <true|false>`
(off by default), which makes the per-layer frontier commutation-aware so
commuting gates can be reordered when selecting disjoint paths.

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

Benchmark mode expands and runs combinations defined in a benchmark JSON. The
bundled `config/all_circuits.json` sweeps the full circuit set, so it is a long
run — the commands below use it only to show the syntax; point `--bench` at your
own (smaller) benchmark JSON for quick runs.

### Direct binary usage

From `build/`:

```bash
./FaultTolerantQuantumCompiler --bench all_circuits
```

To limit or increase benchmark parallelism, set `OMP_NUM_THREADS`:

```bash
OMP_NUM_THREADS=8 ./FaultTolerantQuantumCompiler --bench all_circuits
```

Equivalent aliases:

```bash
./FaultTolerantQuantumCompiler --bench_path all_circuits
./FaultTolerantQuantumCompiler --bench-path all_circuits
```

You can also pass values like `config/all_circuits.json`; the runner extracts the benchmark name and resolves it in `config/`.

### Rerun only timed-out cases

```bash
./FaultTolerantQuantumCompiler --bench all_circuits --rerun-timeouts
```

Or:

```bash
./FaultTolerantQuantumCompiler --bench all_circuits --rerun-timeouts=true
```

### Make target usage

From `build/`:

```bash
make run-bench BENCH_PATH=all_circuits
```

To control benchmark parallelism from the make target:

```bash
make run-bench BENCH_PATH=all_circuits BENCH_JOBS=8
```

To control the round-robin `process` field written into the expanded JSON, use a separate process count:

```bash
./FaultTolerantQuantumCompiler --bench all_circuits --process-count 4
make run-bench BENCH_PATH=all_circuits BENCH_PROCESS_COUNT=4
```

With timeout rerun enabled:

```bash
make run-bench BENCH_PATH=all_circuits RERUN_TIMEOUTS=1
```

You can combine both:

```bash
make run-bench BENCH_PATH=all_circuits RERUN_TIMEOUTS=1 BENCH_JOBS=8
```

## Where execution results are written

### 1) Single QASM run

- Console output: printed to terminal (routing steps, average parallelism, selected options).
- Routed circuit (see [Routed-circuit output](#routed-circuit-output)):
	- `out/route.json`, or wherever `--output-path` points
- Generated universal-set circuit:
	- `universal_set_qasms/<circuit_name>_universal.qasm`
- Visualization artifacts (if produced by the selected flow):
	- `visualization/` and `visualization/gaussian_frames/`

Note: each single execution starts by cleaning previous generated files in `visualization/` (except `visualization/README.md` and `visualization/graph_viewer.cpp`).

### 2) Single config run

Same output locations as single QASM run:

- Terminal summary.
- `out/route.json` (or the config's `output_path`).
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

CSV rows include status fields such as `status`, `exit_code`, `duration_seconds`, `timeout_reached`, `routing_steps`, `avg_parallelism`, and log path.

Benchmark workers disable shared visualization/QASM artifact generation so parallel runs do not interfere with each other; logs and CSV outputs remain the persistent benchmark outputs.

## Benchmark JSON notes

Benchmark JSON files in `config/` can define parameter sweeps using arrays.

Example benchmark file:

- `config/all_circuits.json`

Expansion output:

- `config/executed/all_circuits_expanded.json`

Each expanded case is executed once unless already marked `executed=true`.

If `timeout` is set in a case, execution is wrapped with `timeout`; timed-out runs are recorded in CSV as `status=timeout` and can be selectively rerun with `--rerun-timeouts`.

## Analyze benchmark outputs

Merge every benchmark CSV in `benchmarks/results/` and generate the full plot set:

```bash
python3 scripts/plots/generate_benchmark_plots.py --glob
```

`--glob` concatenates all CSVs in the results directory (writing a merged CSV to
the output directory). Use `--distinct` instead to de-duplicate repeated runs by
configuration, or `--output-dir <dir>` to change where plots are written.

Generate plots from a single benchmark CSV:

```bash
python3 scripts/plots/generate_benchmark_plots.py --csv benchmarks/results/all_circuits_runs.csv
```

Default output for single-CSV mode:

- `benchmarks/results/<csv_name_without_extension>_plots/`

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
./FaultTolerantQuantumCompiler --bench all_circuits
```

Benchmark via make target:

```bash
cd build
make run-bench BENCH_PATH=all_circuits
```
