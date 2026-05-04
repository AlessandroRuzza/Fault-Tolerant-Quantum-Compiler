# run_wisq.py

Runs [wisq](https://github.com/atiyo/wisq) on one or more QASM files and writes results as a CSV compatible with the benchmark CSVs in `benchmarks/results/`.

## Requirements

wisq must be installed in the project virtual environment:

```
.env/bin/wisq
```

## Usage

```
python scripts/run_wisq.py --qasm <file> [<file> ...] [options]
```

### Arguments

| Argument | Description |
|---|---|
| `--qasm FILE [FILE ...]` | One or more input `.qasm` files (required) |
| `--output FILE` / `-o FILE` | Write CSV to this file (default: print to stdout) |
| `--append` | Append to `--output` instead of overwriting |
| `--mr_timeout SECS` | Mapping/routing timeout in seconds passed to wisq (default: 1800) |

Any additional arguments are forwarded directly to wisq (e.g. `--verbose`).

## Examples

Print results to stdout:

```bash
python scripts/run_wisq.py --qasm universal_set_qasms/qft_20_universal.qasm
```

Run multiple circuits and save to a CSV:

```bash
python scripts/run_wisq.py \
  --qasm universal_set_qasms/qft_20_universal.qasm \
         universal_set_qasms/parallel_universal.qasm \
  --output benchmarks/results/wisq_runs.csv
```

Append a new circuit to an existing CSV:

```bash
python scripts/run_wisq.py \
  --qasm universal_set_qasms/ghz_n255_universal.qasm \
  --output benchmarks/results/wisq_runs.csv \
  --append
```

## Output columns

| Column | Description |
|---|---|
| `tool` | Always `wisq` |
| `run_date` / `run_datetime` | Wall-clock time at invocation |
| `circuit` | QASM filename with `_universal` / `_transpiled` stripped |
| `graph_x` / `graph_y` | Grid dimensions from wisq output (`arch.width` / `arch.height`) |
| `circuit_graph_label` | `{circuit}-{X}x{Y}` |
| `routing_steps` | Number of routing steps (`len(steps)` in wisq output JSON) |
| `timeout_reached` | `true` if wisq timed out |
| `status` | `success`, `failed`, or `timeout` |
| `exit_code` | wisq process exit code |
| `duration_seconds` | Wall-clock execution time |

Tool-specific columns present in the benchmark CSVs (e.g. `routing_strategy`, `gaussian_strategy`) are omitted as they have no wisq equivalent. The columns above are sufficient to compare routing steps and runtime side-by-side.
