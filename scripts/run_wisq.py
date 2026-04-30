#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WISQ = REPO_ROOT / ".env" / "bin" / "wisq"


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description="Run wisq on a QASM file.")
    parser.add_argument("--qasm", required=True, help="Path to the input .qasm file")
    # Extra unknown args (e.g. --mode, --verbose) are forwarded to wisq
    return parser.parse_known_args()


def main() -> int:
    args, extra = parse_args()

    qasm_path = Path(args.qasm).resolve()
    if not qasm_path.exists():
        print(f"error: QASM file not found: {qasm_path}", file=sys.stderr)
        return 1

    cmd = [str(WISQ), str(qasm_path), "--mode", "scmr", *extra]
    print(f"running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
