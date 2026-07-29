"""Runs the compiler binary and collects its two output files.

One invocation produces:

* the routed circuit, written by ``write_routing_json`` to ``output_path`` in
  WISQ's ``--mode scmr`` schema — ``{map, arch, steps, gates}``;
* a metrics object, written whenever ``FTQC_BENCH_RESULT_FILE`` names a path.

The metrics file is normally the benchmark harness's channel, but the write is
gated on the environment variable alone, whereas the routed dump is gated on
*not* being a benchmark worker. Setting ``FTQC_BENCH_RESULT_FILE`` while
leaving ``FTQC_BENCH_WORKER`` unset therefore gets us both at once.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

# Repository root: this file is <root>/webserver/app/compiler.py. It doubles as
# the compiler's PROJECT_ROOT, which is baked into the binary at build time, so
# the two must agree for bare circuit names to resolve.
REPO_ROOT = Path(os.environ.get("FTQC_ROOT", Path(__file__).resolve().parents[2]))
BINARY = Path(
    os.environ.get("FTQC_BINARY", REPO_ROOT / "build" / "FaultTolerantQuantumCompiler")
)
# Only the hand-written circuit library is offered. `universal_set_qasms/` is
# deliberately excluded: the compiler transpiles each circuit to a universal
# gate set and caches the result there, so every entry duplicates a circuit
# already in `qasms/` — and a run of a pasted circuit deposits one too, which
# would otherwise show up in the picker as though it were a bundled circuit.
QASM_DIRS = ["qasms"]

# A run is CPU-bound and single-threaded, so a small host can only honestly
# serve a couple at a time; the rest queue. Both are overridable because the
# right numbers depend entirely on the instance size.
MAX_CONCURRENT_RUNS = int(os.environ.get("FTQC_MAX_CONCURRENT_RUNS", "2"))
RUN_TIMEOUT_SECONDS = float(os.environ.get("FTQC_RUN_TIMEOUT", "120"))

# Guards on what crosses the wire. A deep circuit on a large lattice can route
# into tens of thousands of steps, and shipping every one to a browser helps
# nobody: the response is truncated and the UI says so.
MAX_UPLOAD_BYTES = int(os.environ.get("FTQC_MAX_UPLOAD_BYTES", str(4 * 1024 * 1024)))
MAX_STEPS_RETURNED = int(os.environ.get("FTQC_MAX_STEPS_RETURNED", "1500"))


class CompileError(RuntimeError):
    """The compiler refused the input or failed while running it."""

    def __init__(self, message: str, *, stderr: str = "", exit_code: int | None = None):
        super().__init__(message)
        self.stderr = stderr
        self.exit_code = exit_code


@dataclass
class CompileResult:
    route: dict
    metrics: dict
    stdout: str
    elapsed_seconds: float
    total_steps: int
    truncated: bool = False
    warnings: list[str] = field(default_factory=list)


def available_circuits() -> list[dict]:
    """Every ``.qasm`` the compiler can resolve by bare name, newest listing first.

    The compiler resolves an extension-less, parent-less ``circuit`` value
    against ``PROJECT_ROOT/qasms``. Circuits under ``universal_set_qasms`` need
    the directory prefix, which is still parent-less relative to the config we
    write into that same tree, so both directories are offered.
    """
    circuits: list[dict] = []
    for directory in QASM_DIRS:
        root = REPO_ROOT / directory
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.qasm")):
            circuits.append(
                {
                    "name": path.stem,
                    "value": str(path),
                    "group": directory,
                    "size_bytes": path.stat().st_size,
                }
            )
    return circuits


def _read_json(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def _describe_failure(exit_code: int, stderr: str) -> str:
    head = stderr.strip().splitlines()
    detail = head[-1] if head else ""
    if exit_code == 2:
        # SafePassageException: the mapper could not place a qubit while
        # honouring the safe-passage rule. Almost always a too-small lattice.
        return detail or (
            "Safe passage failed: no placement leaves the qubit reachable. "
            "Try a larger grid or a different safe passage strategy."
        )
    return detail or f"The compiler exited with code {exit_code}."


def run_compile(
    config: dict,
    *,
    circuit: str | None = None,
    qasm_text: str | None = None,
    qasm_name: str = "uploaded",
    timeout: float | None = None,
) -> CompileResult:
    """Compile one circuit and return its routing plus metrics.

    Exactly one of ``circuit`` (a path already on disk) or ``qasm_text`` (source
    to stage in the scratch directory) must be given.
    """
    if (circuit is None) == (qasm_text is None):
        raise CompileError("Provide either a circuit selection or QASM source.")

    if not BINARY.is_file():
        raise CompileError(
            f"Compiler binary not found at {BINARY}. Build it first, or point "
            "FTQC_BINARY at it."
        )

    workdir = Path(tempfile.mkdtemp(prefix="ftqc-web-"))
    try:
        if qasm_text is not None:
            encoded = qasm_text.encode()
            if len(encoded) > MAX_UPLOAD_BYTES:
                raise CompileError(
                    f"QASM is {len(encoded) // 1024} kB; the limit is "
                    f"{MAX_UPLOAD_BYTES // 1024} kB."
                )
            if not encoded.strip():
                raise CompileError("The uploaded QASM is empty.")
            safe_stem = "".join(
                c for c in Path(qasm_name).stem if c.isalnum() or c in "-_"
            )
            circuit_path = workdir / f"{safe_stem or 'uploaded'}.qasm"
            circuit_path.write_bytes(encoded)
        else:
            circuit_path = Path(circuit)
            if not circuit_path.is_absolute():
                circuit_path = (REPO_ROOT / circuit_path).resolve()
            # Confine selections to the shipped circuit directories so a crafted
            # `circuit` value cannot read arbitrary files off the host.
            roots = [(REPO_ROOT / d).resolve() for d in QASM_DIRS]
            if not any(circuit_path.resolve().is_relative_to(r) for r in roots):
                raise CompileError("That circuit is not one of the available circuits.")
            if not circuit_path.is_file():
                raise CompileError(f"No such circuit: {circuit_path.name}")

        route_path = workdir / "route.json"
        metrics_path = workdir / "metrics.json"
        config_path = workdir / "config.json"

        run_config = dict(config)
        run_config["circuit"] = str(circuit_path)
        run_config["output_path"] = str(route_path)
        config_path.write_text(json.dumps(run_config, indent=2))

        env = dict(os.environ)
        env["FTQC_BENCH_RESULT_FILE"] = str(metrics_path)
        # Must stay unset: it is what suppresses the routed-circuit dump.
        env.pop("FTQC_BENCH_WORKER", None)
        env.pop("FTQC_MAPPING_ONLY", None)

        started = time.monotonic()
        try:
            completed = subprocess.run(
                [str(BINARY), "--config", str(config_path)],
                capture_output=True,
                text=True,
                timeout=timeout or RUN_TIMEOUT_SECONDS,
                env=env,
                cwd=workdir,
            )
        except subprocess.TimeoutExpired:
            raise CompileError(
                f"The compiler ran past {timeout or RUN_TIMEOUT_SECONDS:.0f}s and "
                "was stopped. Try a smaller circuit or a larger grid."
            ) from None
        elapsed = time.monotonic() - started

        if completed.returncode != 0:
            # The metrics file carries the compiler's own error text when it got
            # far enough to write one; it is more specific than stderr's tail.
            message = ""
            if metrics_path.is_file():
                try:
                    payload = _read_json(metrics_path)
                    if payload.get("status") != "success":
                        message = str(payload.get("error", "")).strip()
                except (OSError, json.JSONDecodeError):
                    pass
            raise CompileError(
                message or _describe_failure(completed.returncode, completed.stderr),
                stderr=completed.stderr,
                exit_code=completed.returncode,
            )

        if not route_path.is_file():
            # Two very different causes land here and the message has to tell
            # them apart. A circuit the parser could make nothing of routes zero
            # gates and exits 0, printing "no routable gates" — blaming a stale
            # binary for that sends the reader off debugging the wrong thing.
            if "no routable gates" in completed.stdout:
                raise CompileError(
                    "The circuit produced no routable gates. Check that the "
                    "source is valid OpenQASM 2.0 and contains gates the "
                    "compiler routes.",
                    stderr=completed.stderr,
                    exit_code=completed.returncode,
                )
            raise CompileError(
                "The run finished but wrote no routed circuit. The binary may "
                "predate write_routing_json — rebuild it.",
                stderr=completed.stderr,
            )

        route = _read_json(route_path)
        metrics = _read_json(metrics_path) if metrics_path.is_file() else {}

        warnings: list[str] = []
        total_steps = len(route.get("steps", []))
        truncated = total_steps > MAX_STEPS_RETURNED
        if truncated:
            route["steps"] = route["steps"][:MAX_STEPS_RETURNED]
            warnings.append(
                f"Showing the first {MAX_STEPS_RETURNED} of {total_steps} routing "
                "steps. The metrics above still describe the whole run."
            )

        non_routed = metrics.get("non_routed_layer_pct")
        if isinstance(non_routed, (int, float)) and non_routed > 0:
            warnings.append(
                f"{non_routed:.2f}% of layers could not be routed on this "
                "lattice. Enlarge the grid for a complete schedule."
            )

        return CompileResult(
            route=route,
            metrics=metrics,
            stdout=completed.stdout,
            elapsed_seconds=elapsed,
            total_steps=total_steps,
            truncated=truncated,
            warnings=warnings,
        )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
