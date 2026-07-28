#!/usr/bin/env python3
"""
Standalone launcher for the Fault-Tolerant Quantum Compiler web interface.

Run:
    python3 webserver/serve.py [--port 8000]

The implementation lives in the ``webserver.app`` package in this directory
(see ``webserver/app/__init__.py`` for the concept overview).
Equivalent invocation:  python3 -m webserver.app [--port 8000]
"""
import sys
from pathlib import Path

# Running this file directly puts webserver/ on sys.path rather than the
# repository root, so `webserver.app` would not resolve. Prepend the root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webserver.app.cli import main  # noqa: E402 — must follow the path fix

if __name__ == "__main__":
    raise SystemExit(main())
