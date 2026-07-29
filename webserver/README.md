# Web interface

A single-page frontend and a small Python service that drives the compiler.
You pick a circuit and a configuration, the server writes the config JSON, runs
the compiler binary, reads back the routed circuit, and the browser draws every
routing step as its own lattice with all of that step's paths animating together.

## How it hangs together

```
browser ──POST /api/compile──▶ FastAPI ──config.json──▶ FaultTolerantQuantumCompiler
   ▲                                                              │
   └──────── route.json + metrics.json ◀───────────────────────────┘
```

Every run gets a scratch directory that is deleted when the request ends. The
server writes three files into it and reads two back:

| File | Written by | Contents |
| --- | --- | --- |
| `config.json` | server | one object per run, passed as `--config` |
| `route.json` | compiler | the routed circuit, WISQ `scmr` schema |
| `metrics.json` | compiler | step count, parallelism, CNOT-graph statistics |

The routed dump comes from `write_routing_json` in
[`src/write_routing_json.hpp`](../src/write_routing_json.hpp), which the
compiler emits whenever `output_path` is set **and** it is not running as a
benchmark worker. The metrics file is the benchmark harness's channel and is
written whenever `FTQC_BENCH_RESULT_FILE` names a path. Those two conditions are
independent, so the server sets `FTQC_BENCH_RESULT_FILE` while making sure
`FTQC_BENCH_WORKER` stays unset, and gets both artifacts from one invocation.

### What `route.json` says

```jsonc
{
  "map":   [[logical_qubit, node], ...],
  "arch":  {"width": 7, "height": 7, "alg_qubits": [...], "magic_states": [...]},
  "steps": [ [{"id": 2, "op": "cx", "qubits": [0,2], "path": [31,32,25,18]}, ...], ... ],
  "gates": [{"id": 0, "op": "cx", "qubits": [0,1]}, ...]
}
```

Nodes are flat row-major grid indices — `node = y * width + x`. One entry of
`steps` is one routing step: every gate in it was scheduled to run *in
parallel*, each along the node path lattice surgery follows. That is what the
animation shows, and why all the paths in a panel grow on the same clock.

## Running it locally

The server shells out to the compiler binary, so build that first:

```sh
git submodule update --init --recursive     # nlohmann_json
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target FaultTolerantQuantumCompiler --parallel
```

Then, from the repository root:

```sh
python3 -m venv .venv && .venv/bin/pip install -r webserver/requirements.txt
.venv/bin/python webserver/serve.py --port 8000
```

Equivalent invocations, if you prefer them:

```sh
python3 -m webserver.app --port 8000                     # same launcher
uvicorn webserver.app.main:app --reload --port 8000      # uvicorn directly
```

`serve.py` accepts `--host`, `--port`, `--reload` and `--log-level`, and checks
on startup that the compiler binary is where it expects — the most common way
this fails is a missing or stale binary, and hearing about it at startup beats
hearing about it on the first compile.

Open <http://localhost:8000>. `GET /api/health` reports the same thing over HTTP.

> The binary must be new enough to contain `write_routing_json` (added
> 2026-07-17). An older one runs fine but writes no routed circuit, and the
> server says so rather than failing silently.

## Sharing a local run

[`tunnel.sh`](tunnel.sh) puts the local server behind a Cloudflare quick
tunnel — a random `https://<something>.trycloudflare.com` hostname that lasts as
long as the script runs. No Cloudflare account, no DNS, nothing to deploy, which
makes it the fast way to show someone a compilation.

```sh
./webserver/tunnel.sh --serve        # start the server and tunnel it
./webserver/tunnel.sh                # tunnel to a server already running
./webserver/tunnel.sh --install      # fetch cloudflared into webserver/.bin
```

It reuses a server already listening on the port, or starts one with `--serve`
and stops it again on exit. Ctrl-C closes both.

Be aware of what the tunnel is: while it runs, anyone holding the URL can reach
the compiler and spend your CPU on circuits of their choosing, with no
authentication in front of it. Keep it short-lived and use the Render
deployment for anything long-running.

## Docker

Build from the **repository root** — the image compiles the C++ sources, which
live above this directory:

```sh
docker build -f webserver/Dockerfile -t ftqc-web .
docker run --rm -p 8000:8000 ftqc-web
```

`PROJECT_ROOT` is baked into the binary at compile time as the CMake source
directory, which is `/app` in the image; `FTQC_ROOT` points the server at the
same `/app`, so a bare circuit name resolves identically on both sides.

The image keeps only circuits at or below `MAX_CIRCUIT_MB` (default 12) — 221
of 231 files. The ten it drops are ~350 MB of the ~440 MB library and are
exactly the ones a modest instance cannot compile inside the request timeout,
so shipping them buys nothing. That, plus avoiding a recursive `chown`, takes
the image from 1.46 GB to **355 MB**. Keep more circuits with:

```sh
docker build -f webserver/Dockerfile --build-arg MAX_CIRCUIT_MB=64 -t ftqc-web .
```

The cut is applied inside this Dockerfile rather than in `.dockerignore`
because the benchmark image at the repository root copies the same directory
and does need the big circuits.

## Deploying to Render

[`render.yaml`](render.yaml) is a ready blueprint. Point Render at the
repository root, keep the Docker context at `.` and the Dockerfile at
`./webserver/Dockerfile`. The health check path is `/api/health`, and the
container binds whatever `$PORT` Render injects.

Setting it up by hand instead of from the blueprint: leave **Root Directory
empty** — it sets the Docker build context, and the image compiles `src/`,
`include/` and `external/`, which all live above `webserver/`. Set the
**Dockerfile Path** to `./webserver/Dockerfile` under Advanced, and add the
environment variables below yourself, since the manual form does not read
`render.yaml`.

Submodules need no special handling. Two of the three are private, so a hosted
builder's recursive init aborts on them and leaves the public
`external/nlohmann_json` empty — which surfaces much later as a CMake error
about a missing `CMakeLists.txt`. The Dockerfile detects that and fetches the
pinned revision itself.

A compilation is CPU-bound and single-threaded for its whole duration, so size
`FTQC_MAX_CONCURRENT_RUNS` to the instance rather than leaving runs to fight
over a core.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `FTQC_ROOT` | repository root | where `qasms/` and the binary are looked up |
| `FTQC_BINARY` | `$FTQC_ROOT/build/FaultTolerantQuantumCompiler` | compiler binary |
| `FTQC_MAX_CONCURRENT_RUNS` | `2` | simultaneous compilations; the rest queue |
| `FTQC_RUN_TIMEOUT` | `120` | seconds before a run is killed |
| `FTQC_MAX_STEPS_RETURNED` | `1500` | steps sent to the browser before truncating |
| `FTQC_MAX_UPLOAD_BYTES` | `4194304` | size limit on pasted QASM |

Truncation only affects the picture. The metrics always describe the whole run,
so a circuit that routes into 116,400 steps still reports 116,400.

### One thing the compiler does outside its scratch directory

A run also transpiles the circuit to a universal gate set and caches the result
as `universal_set_qasms/<circuit>_universal.qasm`
([`src/one_execution.hpp:244`](../src/one_execution.hpp#L244)). That path is
anchored to `PROJECT_ROOT`, not to the scratch directory, so it is the one write
that outlives a request.

It is harmless — the directory is in `.gitignore`, and a cache hit makes the
next run of the same circuit faster — but it has two consequences worth knowing:

* The picker deliberately lists **only** `qasms/`. Every entry under
  `universal_set_qasms/` is derived output that duplicates a circuit already on
  offer, and compiling a pasted circuit deposits one there too, which would
  otherwise appear in the picker as though it were a bundled circuit.
* A long-lived container accumulates them, and they are not small — the cache
  entry for `factor247_n15` is 5.7 MB. If that matters, mount the directory on
  ephemeral storage or clear it periodically.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | the interface |
| `GET` | `/api/spec` | field table the form is generated from |
| `GET` | `/api/circuits` | bundled circuits, grouped by directory |
| `GET` | `/api/health` | binary present, circuit count, free run slots |
| `POST` | `/api/compile` | `{settings, circuit \| qasm_text}` → routing + metrics |
| `GET` | `/api/docs` | generated OpenAPI browser |

## Adding a compiler option to the form

The form is generated, not hand-written. Add one entry to `_FIELDS` in
[`app/spec.py`](app/spec.py) with the compiler's exact JSON key, its type,
bounds and default; the widget, the validation and the round-trip all follow.
Nothing in the frontend needs to change.

Defaults there mirror the hardcoded defaults in `run_one_execution_from_args`
(`src/main.cpp`) — the tuned optimum — rather than the scratch values checked
into `config/0_compiler_config.json`. Because the server always passes an
explicit `--config`, that scratch file is never read.

## The visualization

* One panel per routing step, laid out left-to-right then top-to-bottom. The
  column count is a slider; `auto` fills the available width.
* Within a panel, every path grows on one shared clock, because every gate in a
  step is scheduled to happen at once. Two-qubit routes, T routes to a magic
  state, and anything else each get their own colour.
* Panels mount lazily. A deep circuit routes into thousands of steps, and an
  `IntersectionObserver` keeps live canvases only for the ones near the
  viewport. One `requestAnimationFrame` loop drives them all, so the wall stays
  in lockstep no matter how much of it is on screen.
* Each panel caches its lattice — grid, idle nodes, qubits, magic states — in an
  offscreen bitmap and redraws only the paths per frame.
* Click any step to enlarge it, with the gate list and arrow-key navigation.
* "Follow qubit" dims every route that does not touch the chosen logical qubit,
  which is the quickest way to see where one qubit spends its time.
