#!/usr/bin/env python3
"""Build `test_set/`: every QASMBench circuit converted to the universal
(Clifford+T) gate set with **WISQ's own converter**.

The conversion is one `wisq --mode opt --target_gateset CLIFFORDT` call per
circuit: GUOQ optimises the circuit and resynthesises it into Clifford+T,
arbitrary rotations included (those need `--approx_epsilon > 0`; with the WISQ
default of 0 the rotation synthesiser divides by zero).

WISQ is not a dependency of this repo, so the runner is resolved at startup, in
order: `--wisq PATH`, `$WISQ`, `.env/bin/wisq`, `wisq` on PATH, then Docker
(`--docker-image`, default the image that already ships WISQ at
/opt/venv/bin/wisq). `--backend` forces one of them.

Every circuit is independent: failures and timeouts are recorded in the log CSV
and the sweep continues. Re-running skips circuits already converted, so an
interrupted build resumes where it stopped.

    scripts/build_test_set.py --list
    scripts/build_test_set.py --workers 8 --opt-timeout 300
    scripts/build_test_set.py --only 'small/*' --force
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> root

DEFAULT_SOURCE = REPO_ROOT / "QASMBench-master"
DEFAULT_OUT = REPO_ROOT / "test_set"
DEFAULT_IMAGE = "alessandroruzza/ftqc:latest"
DOCKER_WISQ = "/opt/venv/bin/wisq"
DOCKER_PYTHON = "/opt/venv/bin/python3"
SHIM = Path(__file__).resolve().parent / "wisq_zero_rz_shim.py"

# QASMBench keeps its circuits in these three size buckets; everything else in
# the tree (img/, verify/, interface/) is documentation or tooling.
CATEGORIES = ("small", "medium", "large")

CSV_COLUMNS = [
    "circuit",
    "category",
    "source_path",
    "output_path",
    "status",
    "epsilon",
    "exit_code",
    "duration_seconds",
    "input_bytes",
    "output_bytes",
    "rotations",
    "input_gates",
    "output_gates",
    "error",
]

_GATE_RE = re.compile(r"^\s*([a-zA-Z][a-zA-Z0-9_]*)")
_NON_GATE = {
    "OPENQASM", "include", "qreg", "creg", "gate", "opaque",
    "barrier", "measure", "reset", "if",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Convert every QASMBench circuit to the universal gate set with WISQ.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                   help="QASMBench root directory")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT,
                   help="output directory for the converted circuits")
    p.add_argument("--log", type=Path, default=None,
                   help="log CSV (default: <out>/_build_log.csv)")

    p.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1),
                   help="circuits converted in parallel")
    p.add_argument("--opt-timeout", type=int, default=0, metavar="SECONDS",
                   help="WISQ --opt_timeout: GUOQ optimisation budget. 0 makes WISQ "
                        "skip GUOQ and emit the converted circuit as-is — plain gate-set "
                        "conversion, which is what a test set wants. > 0 also optimises")
    p.add_argument("--timeout", type=int, default=3600, metavar="SECONDS",
                   help="hard wall-clock kill per circuit")
    p.add_argument("--epsilon", default="1e-10", metavar="EPS",
                   help="WISQ --approx_epsilon for rotation synthesis; must be > 0 "
                        "or circuits with arbitrary rotations crash. Larger = "
                        "faster and shallower, less accurate")
    p.add_argument("--gateset", default="CLIFFORDT",
                   choices=["CLIFFORDT", "NAM", "IBMO", "IBMN", "ION"],
                   help="WISQ --target_gateset")
    p.add_argument("--objective", default=None,
                   choices=["TWO_Q", "FIDELITY", "FT", "TOTAL", "T"],
                   help="WISQ --optimization_objective (default: WISQ's own)")

    p.add_argument("--backend", choices=["auto", "native", "docker", "apptainer"],
                   default="auto", help="how to run WISQ")
    p.add_argument("--sif", type=Path, default=None,
                   help="apptainer/singularity image carrying wisq (for --backend "
                        "apptainer; this is the way to run on the PBS cluster)")
    p.add_argument("--wisq", type=Path, default=None,
                   help="path to a native wisq executable")
    p.add_argument("--docker-image", default=DEFAULT_IMAGE,
                   help="image carrying wisq at " + DOCKER_WISQ)
    p.add_argument("--docker-python", default=DOCKER_PYTHON,
                   help="interpreter inside the image (used to run the shim)")
    p.add_argument("--no-shim", action="store_true",
                   help="call wisq directly instead of through "
                        "scripts/wisq_zero_rz_shim.py; rotation-free circuits then "
                        "die on WISQ's ZeroDivisionError")

    p.add_argument("--prefix", default="",
                   help="prepended to each circuit name, e.g. 'full_'. Two suites "
                        "can hold different circuits under the same stem "
                        "(FTCircuitBench's hamiltonians/ and hamiltonians_5trotter/ "
                        "both have ising_1d_9q); output names are stems, so without "
                        "a prefix one would overwrite the other. The prefix is part "
                        "of the circuit's identity: it shows up in the log and in "
                        "the rotation cache, so resume and skip stay consistent")
    p.add_argument("--suffix", default="",
                   help="appended to each output stem, e.g. '_universal'")
    p.add_argument("--only", action="append", default=None, metavar="PATTERN",
                   help="glob on '<category>/<name>' (repeatable), e.g. 'small/*'")
    p.add_argument("--skip-transpiled", action="store_true",
                   help="drop '*_transpiled.qasm' when the plain circuit exists too")
    p.add_argument("--max-rotations", type=int, default=0, metavar="N",
                   help="skip circuits with more than N *costly* rotations, i.e. "
                        "angles that are not multiples of pi/4 (0 = no limit). "
                        "This is the knob that decides whether a build finishes")
    p.add_argument("--seconds-per-rotation", type=float, default=6.7, metavar="S",
                   help="cost model used by --estimate: seconds per *costly* "
                        "rotation. 6.7 s is what this machine measured at "
                        "--epsilon 1e-8 over 104 circuits")
    p.add_argument("--max-input-mb", type=float, default=0.0, metavar="MB",
                   help="skip inputs larger than this (0 = no limit). QASMBench "
                        "tops out at ~90 MB and those blow up under synthesis")

    p.add_argument("--force", action="store_true",
                   help="reconvert circuits that already have an output file")
    p.add_argument("--list", action="store_true",
                   help="print the selected circuits and exit")
    p.add_argument("--estimate", action="store_true",
                   help="count each circuit's rotations and print the projected "
                        "conversion cost, then exit")
    p.add_argument("--dry-run", action="store_true",
                   help="print the wisq command for each circuit and exit")
    return p.parse_args()


# ── circuit discovery ────────────────────────────────────────────────────────

def discover(source: Path, only: list[str] | None, skip_transpiled: bool,
             max_input_mb: float, prefix: str = "") -> list[dict]:
    """Every .qasm under `source`, tagged with a category.

    QASMBench splits its circuits into small/medium/large and those become the
    categories; any other suite is walked whole, with the first path component
    under `source` as the category (or 'root' for files sitting directly in it).
    """
    buckets = [source / c for c in CATEGORIES if (source / c).is_dir()]
    roots = buckets or [source]

    circuits: list[dict] = []
    for root in roots:
        for qasm in sorted(root.rglob("*.qasm")):
            relative = qasm.relative_to(source)
            category = relative.parts[0] if len(relative.parts) > 1 else "root"
            # A couple of QASMBench circuits are named after their qubit count
            # alone (QV_n100/100.qasm); the directory carries the real name.
            name = qasm.parent.name if qasm.stem.isdigit() else qasm.stem
            circuits.append({
                "circuit": prefix + name,
                "category": category,
                "path": qasm,
                "bytes": qasm.stat().st_size,
            })

    if skip_transpiled:
        stems = {c["circuit"] for c in circuits}
        circuits = [c for c in circuits
                    if not (c["circuit"].endswith("_transpiled")
                            and c["circuit"][: -len("_transpiled")] in stems)]

    if only:
        circuits = [c for c in circuits
                    if any(fnmatch.fnmatch(f"{c['category']}/{c['circuit']}", pat)
                           or fnmatch.fnmatch(c["circuit"], pat) for pat in only)]

    if max_input_mb > 0:
        limit = int(max_input_mb * 1e6)
        circuits = [c for c in circuits if c["bytes"] <= limit]

    # Output names are the circuit stems, so a collision would silently
    # overwrite another circuit's conversion.
    seen: dict[str, Path] = {}
    for c in circuits:
        if c["circuit"] in seen:
            raise SystemExit(
                f"duplicate circuit name '{c['circuit']}': "
                f"{seen[c['circuit']]} and {c['path']}"
            )
        seen[c["circuit"]] = c["path"]
    return circuits


def count_gates(path: Path) -> int:
    """Rough gate count: statement lines that are neither declarations nor
    classical control. Only used for the log."""
    total = 0
    try:
        with path.open(errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                m = _GATE_RE.match(line)
                if m and m.group(1) not in _NON_GATE:
                    total += 1
    except OSError:
        return 0
    return total


# ── rotation cost model ──────────────────────────────────────────────────────
#
# WISQ synthesises one Clifford+T sequence per `rz` gate of the NAM-translated
# circuit, with no caching across repeated angles, and each one costs seconds.
# The rz count is therefore the whole cost model, and it is worth knowing before
# starting a build. Counting replays WISQ's own first pass (BasisTranslator into
# {rz, h, x, cx}), so the number matches what WISQ will see.

ROTATION_CACHE = "_rotations.csv"
# Docker start-up plus the wisq/qiskit imports, paid once per circuit.
CONTAINER_OVERHEAD = 25.0


def _count_rotations(path: Path) -> tuple[str, str, str]:
    """(rotations, hard_rotations, error) — replays WISQ's BasisTranslator pass.

    `hard_rotations` are the ones that actually cost anything: an angle that is a
    multiple of pi/4 is already a Clifford or a T, and Qualtran returns it
    immediately. Measured: `gf2^8_mult` has 448 rotations, all pi/4 multiples,
    and converts in 21 s — the container startup, nothing more.
    """
    import math

    from qiskit import QuantumCircuit
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import BasisTranslator
    from qiskit.circuit.equivalence_library import StandardEquivalenceLibrary as sel

    try:
        circuit = QuantumCircuit.from_qasm_file(str(path))
        nam = PassManager([
            BasisTranslator(equivalence_library=sel, target_basis=["rz", "h", "x", "cx"])
        ]).run(circuit)

        total = 0
        hard = 0
        for instruction in nam.data:
            if instruction.operation.name != "rz":
                continue
            total += 1
            try:
                angle = float(instruction.operation.params[0])
            except (TypeError, ValueError):
                hard += 1  # parameterised: assume it costs
                continue
            eighth = angle / (math.pi / 4)
            if abs(eighth - round(eighth)) > 1e-9:
                hard += 1
        return str(total), str(hard), ""
    except Exception as exc:  # WISQ hits the same qiskit front-end, so it fails too
        return "", "", f"{type(exc).__name__}: {exc}"[:200]


def rotation_counts(circuits: list[dict], cache_path: Path) -> dict[str, dict]:
    """Rotation count per circuit, cached in <out>/_rotations.csv — the count is
    a full qiskit transpile, minutes of work over the whole benchmark."""
    cache: dict[str, dict] = {}
    if cache_path.exists():
        with cache_path.open(newline="") as fh:
            for row in csv.DictReader(fh):
                cache[row["circuit"]] = row

    # A cache written before hard_rotations existed cannot drive the cost model.
    missing = [c for c in circuits
               if c["circuit"] not in cache
               or (cache[c["circuit"]].get("hard_rotations") is None
                   and not cache[c["circuit"]].get("error"))]
    for i, circuit in enumerate(missing, 1):
        print(f"  counting rotations [{i}/{len(missing)}] {circuit['circuit']}",
              file=sys.stderr, flush=True)
        rotations, hard, error = _count_rotations(circuit["path"])
        cache[circuit["circuit"]] = {
            "circuit": circuit["circuit"],
            "rotations": rotations,
            "hard_rotations": hard,
            "error": error,
        }

    if missing:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", newline="") as fh:
            writer = csv.DictWriter(
                fh, fieldnames=["circuit", "rotations", "hard_rotations", "error"])
            writer.writeheader()
            writer.writerows(sorted(cache.values(), key=lambda r: r["circuit"]))
    return cache


def fmt_duration(seconds: float) -> str:
    if seconds < 90:
        return f"{seconds:.0f}s"
    if seconds < 5400:
        return f"{seconds / 60:.1f}m"
    if seconds < 86400 * 2:
        return f"{seconds / 3600:.1f}h"
    return f"{seconds / 86400:.1f}d"


# ── backend ──────────────────────────────────────────────────────────────────

def resolve_backend(args: argparse.Namespace) -> tuple[str, Path | None]:
    """Return (backend, runner): ('native', wisq path), ('docker', None) or
    ('apptainer', path to the apptainer/singularity binary)."""
    if args.backend == "apptainer":
        if args.sif is None or not args.sif.exists():
            raise SystemExit("--backend apptainer needs --sif <image.sif>")
        for exe in ("apptainer", "singularity"):
            found = shutil.which(exe)
            if found:
                return "apptainer", Path(found)
        raise SystemExit("neither apptainer nor singularity is on PATH")

    if args.backend not in ("docker",):
        candidates = [args.wisq, Path(os.environ["WISQ"]) if os.environ.get("WISQ") else None,
                      REPO_ROOT / ".env" / "bin" / "wisq"]
        for cand in candidates:
            if cand and Path(cand).exists():
                return "native", Path(cand).resolve()
        found = shutil.which("wisq")
        if found:
            return "native", Path(found)
        if args.backend == "native":
            raise SystemExit(
                "no native wisq found (looked at --wisq, $WISQ, .env/bin/wisq, PATH).\n"
                "Install it with `pip install wisq`, or use --backend docker."
            )

    if args.backend != "native":
        if not shutil.which("docker"):
            raise SystemExit("docker not found and no native wisq available.")
        probe = subprocess.run(
            ["docker", "image", "inspect", args.docker_image],
            capture_output=True, text=True,
        )
        if probe.returncode != 0:
            raise SystemExit(
                f"docker image '{args.docker_image}' is not available locally.\n"
                f"Pull it (`docker pull {args.docker_image}`) or point --docker-image "
                f"at an image that carries wisq at {DOCKER_WISQ}."
            )
        return "docker", None

    raise SystemExit("no WISQ backend available")


def wisq_flags(args: argparse.Namespace) -> list[str]:
    flags = [
        "--mode", "opt",
        "--target_gateset", args.gateset,
        "--approx_epsilon", str(args.epsilon),
        "--opt_timeout", str(args.opt_timeout),
    ]
    if args.objective:
        flags += ["--optimization_objective", args.objective]
    return flags


def native_python(wisq: Path) -> str:
    """The interpreter the wisq launcher was installed against, read from its
    shebang — the shim has to import wisq from that very environment."""
    try:
        with wisq.open("rb") as fh:
            first = fh.readline(512).decode(errors="replace").strip()
        if first.startswith("#!"):
            return first[2:].split()[0]
    except OSError:
        pass
    return sys.executable


def build_command(args: argparse.Namespace, backend: str, wisq: Path | None,
                  source: Path, out_dir: Path, circuit: dict,
                  out_file: Path, tag: str) -> list[str]:
    if backend == "native":
        assert wisq is not None
        launcher = ([str(wisq)] if args.no_shim
                    else [native_python(wisq), str(SHIM)])
        return [*launcher, str(circuit["path"]), *wisq_flags(args),
                "--output_path", str(out_file)]

    rel_in = circuit["path"].relative_to(source)

    if backend == "apptainer":
        assert wisq is not None  # the apptainer/singularity binary
        binds = ["--bind", f"{source}:/in:ro", "--bind", f"{out_dir}:/out"]
        if args.no_shim:
            launcher = [DOCKER_WISQ]
        else:
            binds += ["--bind", f"{SHIM}:/shim/{SHIM.name}:ro"]
            launcher = [args.docker_python, f"/shim/{SHIM.name}"]
        return [
            # --cleanenv, not --containall: --contain would hand the job a small
            # tmpfs /tmp, and a large transpile writes more than that holds.
            str(wisq), "exec", "--cleanenv", "--env", "HOME=/tmp",
            *binds, str(args.sif), *launcher,
            f"/in/{rel_in}", *wisq_flags(args),
            "--output_path", f"/out/{out_file.name}",
        ]

    mounts = [
        "-v", f"{source}:/in:ro",
        "-v", f"{out_dir}:/out",
    ]
    if args.no_shim:
        launcher = ["--entrypoint", DOCKER_WISQ, args.docker_image]
    else:
        mounts += ["-v", f"{SHIM}:/shim/{SHIM.name}:ro"]
        launcher = ["--entrypoint", args.docker_python, args.docker_image,
                    f"/shim/{SHIM.name}"]

    return [
        "docker", "run", "--rm", "--name", tag,
        # Without --user the container writes its output (and the wisq_tmp_*
        # scratch dirs it drops next to it) as root into the host tree.
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-e", "HOME=/tmp",
        *mounts,
        *launcher,
        f"/in/{rel_in}", *wisq_flags(args),
        "--output_path", f"/out/{out_file.name}",
    ]


def relative_to_repo(path: Path) -> Path:
    """Path relative to the repo when it is inside it, absolute otherwise.
    Written the long way: Path.is_relative_to() is Python 3.9+, and this script
    also runs on cluster login nodes with an older interpreter."""
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def run_one(args: argparse.Namespace, backend: str, wisq: Path | None,
            source: Path, out_dir: Path, circuit: dict, index: int) -> dict:
    out_file = out_dir / f"{circuit['circuit']}{args.suffix}.qasm"
    row = {
        "circuit": circuit["circuit"],
        "category": circuit["category"],
        "source_path": str(relative_to_repo(circuit["path"])),
        "output_path": str(relative_to_repo(out_file)),
        "status": "",
        "epsilon": str(args.epsilon),
        "exit_code": "",
        "duration_seconds": "",
        "input_bytes": circuit["bytes"],
        "output_bytes": "",
        "rotations": circuit.get("rotations", ""),
        "input_gates": "",
        "output_gates": "",
        "error": "",
    }

    if out_file.exists() and out_file.stat().st_size > 0 and not args.force:
        row["status"] = "skipped"
        row["output_bytes"] = out_file.stat().st_size
        return row

    tag = f"wisq-testset-{os.getpid()}-{index}"
    cmd = build_command(args, backend, wisq, source, out_dir, circuit, out_file, tag)
    wall = args.timeout

    t0 = time.perf_counter()
    for attempt in range(BACKEND_RETRIES + 1):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=wall)
            exit_code, stderr = proc.returncode, proc.stderr
        except subprocess.TimeoutExpired:
            exit_code, stderr = 124, f"wall-clock timeout after {wall}s"
            if backend == "docker":
                subprocess.run(["docker", "kill", tag], capture_output=True, text=True)
            break

        # A container runtime that is momentarily unreachable is not a verdict on
        # the circuit: it fails in a fraction of a second and would otherwise be
        # logged next to real, permanent failures like a QASM parse error.
        if exit_code == 0 or not transient_backend_error(stderr):
            break
        if attempt < BACKEND_RETRIES:
            print(f"  {circuit['circuit']}: backend unreachable, retry "
                  f"{attempt + 1}/{BACKEND_RETRIES}", file=sys.stderr, flush=True)
            time.sleep(BACKEND_RETRY_WAIT)
    row["duration_seconds"] = f"{time.perf_counter() - t0:.2f}"
    row["exit_code"] = exit_code

    produced = out_file.exists() and out_file.stat().st_size > 0
    if exit_code == 0 and produced:
        row["status"] = "success"
        row["output_bytes"] = out_file.stat().st_size
        row["input_gates"] = count_gates(circuit["path"])
        row["output_gates"] = count_gates(out_file)
    else:
        row["status"] = "timeout" if exit_code == 124 else "failed"
        row["error"] = last_error_line(stderr)
        # A half-written file would be picked up as a valid result on resume.
        if out_file.exists():
            out_file.unlink()
    return row


# Container runtimes drop out for a moment — a daemon restart, a busy node. The
# circuit is fine; only the launch failed.
BACKEND_RETRIES = 2
BACKEND_RETRY_WAIT = 15.0

_TRANSIENT = (
    "cannot connect to the docker daemon",
    "error response from daemon",
    "connection refused",
    "is the docker daemon running",
    "failed to create container",
    "resource temporarily unavailable",
)


def transient_backend_error(stderr: str) -> bool:
    """True when the failure is the container runtime, not the circuit."""
    low = (stderr or "").lower()
    return any(marker in low for marker in _TRANSIENT)


def last_error_line(stderr: str) -> str:
    lines = [ln.strip() for ln in (stderr or "").splitlines() if ln.strip()]
    if not lines:
        return ""
    for line in reversed(lines):
        if not line.startswith(("File \"", "  ", "^")):
            return line[:300]
    return lines[-1][:300]


def cleanup_scratch(out_dir: Path) -> None:
    """WISQ drops wisq_tmp_* scratch dirs beside its output file."""
    for leftover in out_dir.glob("wisq_tmp_*"):
        shutil.rmtree(leftover, ignore_errors=True)


def drop_stale_epsilon(log_path: Path, out_dir: Path, suffix: str,
                       epsilon: str) -> int:
    """Delete outputs the log says were converted at a different --epsilon.

    Same gate set, different depth and fidelity: resuming a 1e-8 build on top of
    a 1e-10 one would leave a set that cannot be compared circuit to circuit.
    Returns how many files were dropped."""
    if not log_path.exists():
        return 0

    with log_path.open(newline="") as fh:
        stale = [row for row in csv.DictReader(fh)
                 if row.get("status") == "success"
                 and row.get("epsilon", "") != epsilon]

    dropped = 0
    for row in stale:
        path = out_dir / f"{row['circuit']}{suffix}.qasm"
        if path.exists():
            path.unlink()
            dropped += 1

    if dropped:
        was = stale[0].get("epsilon") or "unrecorded"
        print(f"dropped {dropped} circuits converted at epsilon {was}, now "
              f"{epsilon} — they will be reconverted\n", flush=True)
    return dropped


def write_log(log_path: Path, state: dict[str, dict]) -> None:
    """Rewrite the log from the current state. Called after every circuit: a
    build that gets killed (or runs out of wall clock) must not lose the record
    of what is already on disk, above all the epsilon each file was made at."""
    tmp = log_path.with_suffix(log_path.suffix + ".tmp")
    rows = sorted(state.values(), key=lambda r: (r["category"], r["circuit"]))
    with tmp.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(log_path)


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    out_dir = args.out.resolve()
    log_path = (args.log or (out_dir / "_build_log.csv")).resolve()

    if not source.is_dir():
        raise SystemExit(f"source directory not found: {source}")

    circuits = discover(source, args.only, args.skip_transpiled, args.max_input_mb,
                        args.prefix)
    if not circuits:
        raise SystemExit("no circuits selected")

    if args.list:
        for c in circuits:
            print(f"{c['category']:6} {c['circuit']:40} {c['bytes'] / 1e6:8.2f} MB")
        print(f"\n{len(circuits)} circuits, "
              f"{sum(c['bytes'] for c in circuits) / 1e6:.1f} MB of input")
        return 0

    backend, wisq = resolve_backend(args)

    # Cheapest first, always. Without it a handful of giants can seize every
    # worker while the quick circuits queue behind them, and an interrupted build
    # leaves far fewer circuits done. Input size is the free proxy; the rotation
    # count below is the real one, when we have it.
    circuits.sort(key=lambda c: (c["bytes"], c["circuit"]))

    if args.estimate or args.max_rotations > 0:
        counts = rotation_counts(circuits, out_dir / ROTATION_CACHE)
        for c in circuits:
            row = counts.get(c["circuit"], {})
            c["rotations"] = row.get("rotations", "")
            c["hard_rotations"] = row.get("hard_rotations", "")
            c["count_error"] = row.get("error", "")
        # Cheapest first: an interrupted build then leaves the most circuits done,
        # and the circuits that never finish are the ones already known to be huge.
        circuits.sort(key=lambda c: (int(c["hard_rotations"]) if c["hard_rotations"]
                                     else 1 << 62, c["circuit"]))

    if args.estimate:
        total = 0.0
        print(f"{'':6} {'circuit':40} {'rot':>9} {'costly':>9}  projected")
        for c in circuits:
            if c["hard_rotations"]:
                cost = (int(c["hard_rotations"]) * args.seconds_per_rotation
                        + CONTAINER_OVERHEAD)
                total += cost
                note = fmt_duration(cost)
            else:
                note = f"UNCONVERTIBLE — {c['count_error']}"
            print(f"{c['category']:6} {c['circuit']:40} "
                  f"{c['rotations'] or '-':>9} {c['hard_rotations'] or '-':>9}  {note}")
        convertible = [c for c in circuits if c["hard_rotations"]]
        print(f"\n{len(convertible)}/{len(circuits)} circuits convertible, "
              f"{sum(int(c['rotations']) for c in convertible)} rotations of which "
              f"{sum(int(c['hard_rotations']) for c in convertible)} costly, "
              f"{fmt_duration(total)} of single-core work "
              f"({fmt_duration(total / max(1, args.workers))} on {args.workers} workers)")
        return 0

    if args.max_rotations > 0:
        kept = []
        for c in circuits:
            if c["hard_rotations"] and int(c["hard_rotations"]) <= args.max_rotations:
                kept.append(c)
        dropped = len(circuits) - len(kept)
        circuits = kept
        print(f"--max-rotations {args.max_rotations}: {len(circuits)} circuits kept, "
              f"{dropped} dropped (too many rotations, or qiskit cannot load them)")
        if not circuits:
            raise SystemExit("no circuits left after --max-rotations")

    out_dir.mkdir(parents=True, exist_ok=True)


    if args.dry_run:
        for i, c in enumerate(circuits):
            out_file = out_dir / f"{c['circuit']}{args.suffix}.qasm"
            cmd = build_command(args, backend, wisq, source, out_dir, c, out_file,
                                f"wisq-testset-dry-{i}")
            print(" ".join(cmd))
        return 0

    print(f"backend      : {backend}" + (f" ({wisq})" if wisq else f" ({args.docker_image})"))
    print(f"source       : {source}")
    print(f"out          : {out_dir}")
    print(f"log          : {log_path}")
    print(f"circuits     : {len(circuits)}")
    print(f"wisq flags   : {' '.join(wisq_flags(args))}")
    print(f"workers      : {args.workers}, wall timeout {args.timeout}s\n", flush=True)

    if not args.force:
        drop_stale_epsilon(log_path, out_dir, args.suffix, str(args.epsilon))

    # The log describes the *directory*, not this run: rows for circuits this
    # build never looks at (Feynman on top of QASMBench) are kept, as long as
    # their file is still there.
    state: dict[str, dict] = {}
    if log_path.exists():
        with log_path.open(newline="") as fh:
            for row in csv.DictReader(fh):
                output = out_dir / f"{row['circuit']}{args.suffix}.qasm"
                if row.get("status") in ("success", "skipped") and output.exists():
                    state[row["circuit"]] = {k: row.get(k, "") for k in CSV_COLUMNS}

    lock = Lock()
    done = 0

    def submit(item: tuple[int, dict]) -> dict:
        return run_one(args, backend, wisq, source, out_dir, item[1], item[0])

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(submit, (i, c)): c for i, c in enumerate(circuits)}
        try:
            for future in as_completed(futures):
                row = future.result()
                with lock:
                    # A skip means the file is already there from an earlier run;
                    # keep that run's measurements rather than a blank row.
                    if row["status"] != "skipped" or row["circuit"] not in state:
                        state[row["circuit"]] = row
                    write_log(log_path, state)
                    done += 1
                    detail = ""
                    if row["status"] == "success":
                        detail = (f" {row['duration_seconds']}s, "
                                  f"{row['output_gates']} gates, "
                                  f"{int(row['output_bytes']) / 1e6:.1f} MB")
                    elif row["status"] in ("failed", "timeout"):
                        detail = f" {row['duration_seconds']}s — {row['error']}"
                    print(f"[{done}/{len(circuits)}] {row['status']:8} "
                          f"{row['circuit']}{detail}", flush=True)
        except KeyboardInterrupt:
            print("\ninterrupted — writing the log for what finished", file=sys.stderr)
            try:
                pool.shutdown(wait=False, cancel_futures=True)
            except TypeError:  # cancel_futures is 3.9+
                pool.shutdown(wait=False)

    cleanup_scratch(out_dir)

    write_log(log_path, state)

    rows = list(state.values())
    tally: dict[str, int] = {}
    for row in rows:
        tally[row["status"]] = tally.get(row["status"], 0) + 1
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(tally.items())))
    print(f"log: {log_path}")
    return 0 if tally.get("failed", 0) + tally.get("timeout", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
