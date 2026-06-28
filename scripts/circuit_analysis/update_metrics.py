#!/usr/bin/env python3
"""
Update benchmarks/results/cache_metrics/all_circuits_cache_metrics.csv
for every QASM file found in qasms/.

Calls the compiled binary with --metrics-only for each circuit:
  - parses QASM + builds layers
  - writes/updates one row in the CSV
  - exits immediately (no mapping, no routing)

Path-length metrics (avg/max/stddev) are 0 in the output because no mapping
is performed; all structural metrics (gate counts, layer structure, etc.) are
fully populated.

Usage:
  python3 scripts/update_metrics.py [--binary <path>] [--qasm-dir <path>] [--jobs <n>]
"""

import argparse
import subprocess
import sys
import os
import concurrent.futures
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BINARY = PROJECT_ROOT / "build" / "FaultTolerantQuantumCompiler"
DEFAULT_QASM_DIR = PROJECT_ROOT / "qasms"


def run_one(binary: Path, qasm_path: Path) -> tuple[str, bool, str]:
    """Run the binary in --metrics-only mode for one QASM file.

    Returns (circuit_name, success, error_message).
    """
    name = qasm_path.stem
    try:
        result = subprocess.run(
            [str(binary), "--circuit", str(qasm_path), "--metrics-only"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            snippet = (result.stderr or result.stdout or "").strip()[-300:]
            return name, False, snippet
        return name, True, ""
    except subprocess.TimeoutExpired:
        return name, False, "timeout (60s)"
    except Exception as e:
        return name, False, str(e)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY,
                        help="Path to compiled binary (default: build/FaultTolerantQuantumCompiler)")
    parser.add_argument("--qasm-dir", type=Path, default=DEFAULT_QASM_DIR,
                        help="Directory containing .qasm files (default: qasms/)")
    parser.add_argument("--jobs", type=int, default=1,
                        help="Parallel workers (default: 1; >1 may cause CSV write races)")
    args = parser.parse_args()

    if not args.binary.exists():
        print(f"ERROR: binary not found at {args.binary}", file=sys.stderr)
        print("Run: cmake --build build --parallel 4", file=sys.stderr)
        sys.exit(1)

    qasm_files = sorted(args.qasm_dir.glob("*.qasm"))
    if not qasm_files:
        print(f"ERROR: no .qasm files found in {args.qasm_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(qasm_files)} QASM files in {args.qasm_dir}")
    print(f"Binary: {args.binary}")
    if args.jobs > 1:
        print(f"WARNING: --jobs > 1 with shared CSV may cause write races; use with care.")
    print()

    ok = []
    failed = []

    if args.jobs == 1:
        for i, qasm in enumerate(qasm_files, 1):
            print(f"[{i:2d}/{len(qasm_files)}] {qasm.stem}...", end=" ", flush=True)
            name, success, err = run_one(args.binary, qasm)
            if success:
                print("ok")
                ok.append(name)
            else:
                print(f"FAILED: {err}")
                failed.append((name, err))
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(run_one, args.binary, q): q for q in qasm_files}
            done = 0
            for fut in concurrent.futures.as_completed(futures):
                name, success, err = fut.result()
                done += 1
                status = "ok" if success else f"FAILED: {err}"
                print(f"[{done:2d}/{len(qasm_files)}] {name}: {status}")
                if success:
                    ok.append(name)
                else:
                    failed.append((name, err))

    print()
    print(f"Done: {len(ok)} succeeded, {len(failed)} failed.")
    if failed:
        print("\nFailed circuits:")
        for name, err in failed:
            print(f"  {name}: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
