# `test_set/` — QASMBench converted to the universal gate set by WISQ

Every circuit here is a QASMBench circuit put through **WISQ's own converter**,
so the gate set is the one WISQ produces rather than the one our parser derives.

    scripts/build_test_set.py

Conversion is one call per circuit:

    wisq <circuit>.qasm --mode opt --target_gateset CLIFFORDT \
         --approx_epsilon 1e-10 --opt_timeout 0 --output_path test_set/<circuit>.qasm

`--opt_timeout 0` is the "convert, don't optimise" switch: WISQ then skips GUOQ
and writes the circuit straight after the gate-set translation. `--approx_epsilon`
**must** be > 0 — WISQ divides the error budget by the rotation count, and the
default of 0 makes it crash before writing anything.

WISQ is not installed on this machine. The script runs it out of the Docker image
`alessandroruzza/ftqc:latest`, which carries it at `/opt/venv/bin/wisq`; on the
cluster use `--backend apptainer --sif ftqc.sif`.

## What is generated here

| file | what it is |
|---|---|
| `<circuit>.qasm` | the converted circuit |
| `_build_log.csv` | one row per circuit: status, exit code, seconds, gate counts, error |
| `_rotations.csv` | cached rotation count per circuit — the cost model, see below |

## The cost: one synthesis per rotation

WISQ decomposes **every `rz` gate individually** through Qualtran's rotation
synthesis, with no caching across repeated angles, so the rotation count is the
whole cost model — `scripts/build_test_set.py --estimate` prints it, and
`_rotations.csv` caches it.

Measured over the 87 converted circuits that actually carry rotations (10 928
rotations, 128 286 s of container time): **11.7 s per rotation on average**. The
spread is what matters, though — it is the *angle*, not the count, that decides:

| circuit | rotations | seconds | s/rotation |
|---|---|---|---|
| `wstate_n27` | 364 | 5 351 | 14.6 |
| `dnn_n2_transpiled` | 364 | 8 234 | 22.6 |
| `qf21_n15` | 163 | 9 931 | 60.8 |
| `ising_n34_transpiled` | 201 | 12 312 | 61.1 |
| `quantumwalks_n2` | 56 | timed out at 14 400 | > 257 |

Angles that are Clifford multiples cost nothing; the `ising_*` and `qf21_*`
families sit around 60 s, and `quantumwalks_n2` never finished within 4 h. Budget
with the average, but expect a long tail — and note that the per-angle epsilon is
`--epsilon / (2 * rotations)`, so a circuit with more rotations is also asking for
a *tighter* approximation on each one.

Projected over the 197 convertible QASMBench circuits (8.58 M rotations) at the
measured 11.7 s:

| cap (`--max-rotations`) | circuits | rotations | 1 core | 8 cores | 28 cores |
|---|---|---|---|---|---|
| 100 | 75 | 1 492 | 5.3 h | 0.7 h | 0.2 h |
| 500 | 118 | 12 912 | 42.8 h | 5.3 h | 1.5 h |
| 1 000 | 133 | 23 698 | 3 d | 9.7 h | 2.8 h |
| 5 000 | 169 | 103 312 | 14 d | 42.1 h | 12.0 h |
| 20 000 | 179 | 185 273 | 25 d | 3 d | 21.5 h |
| none | 197 | 8 576 722 | **1161 d** | 145 d | **41 d** |

The tail is `bwt_n97` (2.6 M rotations), `bwt_n57`, `bwt_n37` and the
`multiplier_n350/400` family. Converting all of QASMBench is a cluster campaign,
not a local build. Circuits are converted cheapest-first and the build resumes,
so raising `--max-rotations` on a later run only does the work still missing.

## `--epsilon` is the real knob, not `--max-rotations`

The per-angle budget WISQ hands to Qualtran is `--epsilon / (2 * rotations)`, and
below roughly 1e-12 per angle the synthesis search falls off a cliff.
`quantumwalks_n2` (56 rotations) makes it visible:

| `--epsilon` | per angle | time | gates |
|---|---|---|---|
| 1e-6 | 8.9e-9 | **302 s** | 4 177 |
| 1e-8 | 8.9e-11 | **503 s** | 5 131 |
| 1e-10 | 8.9e-13 | **> 14 400 s (timeout)** | — |

Two orders of magnitude of accuracy cost 1.7x the time and 23% more gates; the
third costs at least 48x and did not finish. **1e-8 is the sweet spot** — tight
enough to be honest, on the safe side of the cliff. The set currently in this
directory was built at 1e-10, which is why the `ising_*` family and
`quantumwalks_n2` never finished.

## What is in here now

**169 circuits at epsilon 1e-8**, 74 MB, gate set `{h, t, s, sdg, x, cx}` with
`measure`/`barrier`/`creg` carried through untouched. Two sources:

| source | in here | notes |
|---|---|---|
| QASMBench (`QASMBench-master/`) | 128 | the `--max-rotations 1000` tier |
| Feynman (`Feynman-benchmarks/`) | 41 | of 44; the whole suite is free to convert |

The whole set is at one epsilon — the log records it per circuit and the build
refuses to mix accuracies.

Missing, and why:

- **5 QASMBench circuits** hit the 4 h wall clock: `ising_n10`, `ising_n66`,
  `ising_n98`, `ising_n98_transpiled`, `qft_n18_transpiled`. It is the angles,
  not the size — `ising_n10` has 280 rotations and did not finish, while
  `ising_n10_transpiled` has 415 and converted in 2.9 h. `ising_n66_transpiled`
  (393) needed 3.25 h, so these are just over the line. A longer `--timeout`
  picks up only them.
- **3 Feynman circuits**: `gf2^256_mult` (458 k rotations, a ~2 h transpile, cut
  short by hand), and `cycle_17_3` / `mod_adder_1048576`, which qiskit refuses to
  parse — the same `duplicate qubits in gate application` defect as QASMBench's
  `random_QAOA_*`.

### The Feynman suite converts for free

Its 913 353 rotations contain **zero costly ones**: every angle is a multiple of
pi/4, so Qualtran returns immediately. `gf2^8_mult` has 448 rotations and
converts in 21 s — the container start-up, nothing more. This is why
`_rotations.csv` carries `hard_rotations` separately, and why that column, not
the raw rotation count, drives `--estimate` and `--max-rotations`.

## Adding more circuits

Every suite goes through the same driver; `--source` takes any directory tree.

    # a suite already on disk
    python3 scripts/build_test_set.py --source MQTBench \
        --epsilon 1e-8 --max-rotations 5000 --max-input-mb 2 --workers 8

    # MQT Bench is a generator: regenerate or extend the sizes first
    pip install mqt.bench
    scripts/gen_mqt_bench.py --out MQTBench --sizes 5,10,20,40,60,80,100,125

    # FTCircuitBench, widened or narrowed a directory at a time
    git -C FTCircuitBench sparse-checkout set qasm/adder qasm/qft qasm/hhl \
        qasm/hamiltonians_5trotter qasm/qsvt qasm/qpe qasm/hamiltonians

`--max-rotations` counts only the *costly* rotations and is the knob that decides
whether a build finishes; `--max-input-mb` keeps out the few giant sources whose
converted form dwarfs everything else.

> `FTCircuitBench/qasm/hamiltonians/` and `qasm/hamiltonians_5trotter/` hold
> different circuits under identical stems (`ising_1d_9q` and friends). Output
> names are stems, so converting both needs `--prefix` on one of them, otherwise
> the build stops on the name clash.

On the cluster the same thing runs as a PBS job — see `pbs/build_test_set.pbs`,
which is the one job here whose python runs on the host rather than inside
`ftqc.sif`, because the driver launches an `apptainer exec` per circuit.

## How to rebuild

    python3 scripts/build_test_set.py \
        --epsilon 1e-8 --max-rotations 1000 --max-input-mb 20 \
        --workers 8 --timeout 14400

The build resumes: interrupt with Ctrl-C, re-run the same command, and only the
missing circuits are converted. Change `--epsilon` and every output made at the
other value is deleted and reconverted, so the set can never end up half at one
accuracy and half at another.

On the cluster, same script with the image instead of Docker:

    python3 scripts/build_test_set.py --backend apptainer --sif ftqc.sif \
        --epsilon 1e-8 --max-rotations 5000 --workers 28 --timeout 14400

Useful before committing to a run:

    scripts/build_test_set.py --list       # what would be converted
    scripts/build_test_set.py --estimate   # rotations and projected cost
    scripts/build_test_set.py --dry-run    # the exact wisq command per circuit

## The 39 circuits WISQ cannot convert

They fail in WISQ's qiskit front-end, before any synthesis:

- **`if_else` (14)** — mid-circuit classical control (`cc_*`, `qec_sm_*`,
  `shor_n5`, `teleportation`-style circuits). `BasisTranslator` has no
  translation for it.
- **custom / non-standard gates (~11)** — `qugan_*` (`ryy_<id>` opaque gates),
  `wstate_n3` (`cH`), and similar.
- **malformed for qiskit 2.x (~14)** — `vqe_uccsd_*` (`'q' is not defined in
  this scope`), `random_QAOA_angles_*` (`duplicate qubits in gate application`).

`_rotations.csv` and `_build_log.csv` record the exact reason per circuit.
