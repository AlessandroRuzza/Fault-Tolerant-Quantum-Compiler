"""Web interface for the fault-tolerant quantum compiler.

The compiler is a C++ binary that takes one JSON object describing a run and
writes the routed circuit back out as JSON. This package is the thin layer that
turns that into something you can click:

    browser ──POST /api/compile──▶ FastAPI ──config.json──▶ the compiler binary
       ▲                                                            │
       └──────── route.json + metrics.json ◀─────────────────────────┘

Each request gets a scratch directory that is deleted when it ends. Nothing is
written into the repository, and two runs never share state.

Modules
-------
``spec``
    The compiler's configuration surface as data: every accepted JSON key with
    its type, bounds and default. The frontend generates its whole form from
    this, so a new compiler option means one new entry here and nothing else.
``compiler``
    Runs the binary and collects its two output files. The routed dump and the
    metrics payload are gated on different conditions, which is why the runner
    sets ``FTQC_BENCH_RESULT_FILE`` while leaving ``FTQC_BENCH_WORKER`` unset —
    that combination yields both from a single invocation.
``main``
    The HTTP surface: the form spec, the circuit list, and the compile call.
``cli``
    Command line entry point, so starting the server is one command.

The interesting output is ``steps``: a list where each entry holds every gate
routed *in parallel* during one routing step, each with the node path lattice
surgery follows. The frontend draws one lattice per step and animates all of a
step's paths on a single clock, because that is what the schedule means.
"""
