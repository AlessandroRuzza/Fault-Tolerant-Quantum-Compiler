#!/usr/bin/env python3
"""
Strip a QASM file down to only the gates the router actually cares about.

By default keeps the CNOT family (cx, cnot, cz, cphase) and the T family
(t, tdg) — these are exactly what src/circuit.cpp turns into routing
operations; every other gate (h, u, rz, sx, ...) is dropped. Use --only
to keep a stricter set (e.g. literally just cx and t).

Header lines (OPENQASM, include, qreg, creg) are always preserved.
Measure/barrier lines are dropped.

Usage:
  python3 scripts/filter_gates.py <input.qasm> [output.qasm]
  python3 scripts/filter_gates.py in.qasm out.qasm --only cx t

  # in-place
  python3 scripts/filter_gates.py circuit.qasm --in-place
"""

import argparse
import re
import sys
from pathlib import Path

# Gate names the compiler's parser treats as routing-relevant.
DEFAULT_KEEP = {"cx", "cnot", "cz", "cphase", "t", "tdg"}

HEADER_PREFIXES = ("OPENQASM", "include", "qreg", "creg")
DROP_PREFIXES = ("measure", "barrier")


def gate_name(line: str) -> str:
    """Extract the gate name from a QASM instruction line.
    e.g. 'cx q[3],q[2];' -> 'cx';  'u(pi/2,0,pi) q[1];' -> 'u'."""
    m = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)", line)
    return m.group(1).lower() if m else ""


def filter_qasm(text: str, keep: set) -> tuple[str, dict]:
    kept_lines = []
    stats = {"kept": 0, "dropped": 0}
    dropped_names = {}
    for line in text.splitlines():
        s = line.strip()
        if not s:
            kept_lines.append(line)
            continue
        if s.startswith(HEADER_PREFIXES):
            kept_lines.append(line)
            continue
        if s.startswith(DROP_PREFIXES):
            stats["dropped"] += 1
            continue
        name = gate_name(s)
        if name in keep:
            kept_lines.append(line)
            stats["kept"] += 1
        else:
            stats["dropped"] += 1
            dropped_names[name] = dropped_names.get(name, 0) + 1
    stats["dropped_by_name"] = dropped_names
    return "\n".join(kept_lines) + "\n", stats


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path, help="Input QASM file")
    p.add_argument("output", type=Path, nargs="?", default=None,
                   help="Output QASM file (default: stdout, or alongside input with --in-place)")
    p.add_argument("--only", nargs="*", default=None,
                   help="Keep only these gate names (default: cx/cnot/cz/cphase/t/tdg)")
    p.add_argument("--in-place", action="store_true",
                   help="Overwrite the input file")
    args = p.parse_args()

    if not args.input.exists():
        print(f"ERROR: input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    keep = set(g.lower() for g in args.only) if args.only else DEFAULT_KEEP

    text = args.input.read_text()
    filtered, stats = filter_qasm(text, keep)

    if args.in_place:
        args.input.write_text(filtered)
        dest = str(args.input)
    elif args.output:
        args.output.write_text(filtered)
        dest = str(args.output)
    else:
        sys.stdout.write(filtered)
        dest = "(stdout)"

    dropped_detail = ", ".join(f"{n}:{c}" for n, c in
                               sorted(stats["dropped_by_name"].items(),
                                      key=lambda x: -x[1]))
    print(f"\nKept {stats['kept']} gates, dropped {stats['dropped']} "
          f"-> {dest}", file=sys.stderr)
    if dropped_detail:
        print(f"Dropped by name: {dropped_detail}", file=sys.stderr)


if __name__ == "__main__":
    main()
