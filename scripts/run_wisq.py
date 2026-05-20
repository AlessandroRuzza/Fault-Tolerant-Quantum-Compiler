#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

REPO_ROOT = Path(__file__).resolve().parent.parent
_local_wisq = REPO_ROOT / ".env" / "bin" / "wisq"
WISQ = _local_wisq if _local_wisq.exists() else Path("wisq")

# Columns that match the benchmark CSVs; tool-specific fields are left empty.
CSV_COLUMNS = [
    "tool",
    "run_date",
    "run_datetime",
    "circuit",
    "graph_x",
    "graph_y",
    "circuit_graph_label",
    "routing_steps",
    "timeout_reached",
    "status",
    "exit_code",
    "duration_seconds",
]


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run wisq on one or more QASM files and emit benchmark-compatible CSV."
    )
    parser.add_argument(
        "--qasm",
        required=True,
        nargs="+",
        metavar="FILE",
        help="Path(s) to input .qasm file(s)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="CSV output file (default: print to stdout)",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to --output instead of overwriting",
    )
    parser.add_argument(
        "--mr_timeout",
        type=int,
        default=30*60,
        metavar="SECS",
        help="Mapping/routing timeout passed to wisq (default: 1800)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        metavar="N",
        help="Number of parallel wisq workers (default: 4)",
    )
    # Extra unknown args are forwarded to wisq
    return parser.parse_known_args()


def circuit_name(qasm_path: Path) -> str:
    name = qasm_path.stem
    for suffix in ("_universal", "_transpiled"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name


def run_one(qasm_path: Path, mr_timeout: int, extra: list[str]) -> dict:
    now = datetime.now(timezone.utc)
    run_date = now.strftime("%Y-%m-%d")
    run_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out_path = Path(tmp.name)

    cmd = [
        str(WISQ),
        str(qasm_path),
        "--mode", "scmr",
        "--output_path", str(out_path),
        "--mr_timeout", str(mr_timeout),
        *extra,
    ]
    def _rel(p: str) -> str:
        try:
            return os.path.relpath(p)
        except ValueError:
            return p

    print(f"running: {' '.join(_rel(c) for c in cmd)}", file=sys.stderr)

    t0 = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.perf_counter() - t0

    exit_code = result.returncode
    status = "success" if exit_code == 0 else "failed"

    routing_steps = ""
    graph_x = ""
    graph_y = ""
    timeout_reached = "false"

    if exit_code == 0 and out_path.exists():
        try:
            data = json.loads(out_path.read_text())
            routing_steps = len(data.get("steps", []))
            arch = data.get("arch", {})
            graph_x = arch.get("width", "")
            graph_y = arch.get("height", "")
        except (json.JSONDecodeError, OSError):
            pass
    elif exit_code == 124:
        timeout_reached = "true"
        status = "timeout"

    out_path.unlink(missing_ok=True)

    circ = circuit_name(qasm_path)
    label = f"{circ}-{graph_x}x{graph_y}" if graph_x and graph_y else circ

    return {
        "tool": "wisq",
        "run_date": run_date,
        "run_datetime": run_datetime,
        "circuit": circ,
        "graph_x": graph_x,
        "graph_y": graph_y,
        "circuit_graph_label": label,
        "routing_steps": routing_steps,
        "timeout_reached": timeout_reached,
        "status": status,
        "exit_code": exit_code,
        "duration_seconds": f"{duration:.6f}",
    }


def write_row(row: dict, out_file: Path | None, first: bool, append: bool) -> None:
    if out_file:
        file_exists = out_file.exists()
        write_header = not file_exists if append else first
        mode = "a" if file_exists and (append or not first) else "w"

        with out_file.open(mode, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=CSV_COLUMNS)
        if first:
            writer.writeheader()
        writer.writerow(row)


def main() -> int:
    args, extra = parse_args()
    out_file = Path(args.output) if args.output else None
    if out_file is None:
        print("#### WARNING: writing only to stdout. ########################à")

    qasm_paths = []
    for qasm_str in args.qasm:
        qasm_path = Path(qasm_str).resolve()
        if not qasm_path.exists():
            print(f"error: QASM file not found: {qasm_path}", file=sys.stderr)
            return 1
        qasm_paths.append(qasm_path)

    lock = Lock()
    first_written = [True]

    def run_and_write(qasm_path: Path) -> None:
        row = run_one(qasm_path, args.mr_timeout, extra)
        with lock:
            write_row(row, out_file, first=first_written[0], append=args.append)
            first_written[0] = False
            if out_file:
                print(f"result appended to {out_file}", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_and_write, p): p for p in qasm_paths}
        for future in as_completed(futures):
            future.result()

    return 0


if __name__ == "__main__":
    sys.exit(main())
