"""Command line entry point for the web interface.

Wraps the uvicorn invocation so starting the server is one obvious command
rather than a module path and a port flag to remember. See
``webserver/app/__init__.py`` for what the service actually does.
"""

from __future__ import annotations

import argparse
import sys

from . import compiler

APP_PATH = "webserver.app.main:app"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="webserver",
        description="Serve the fault-tolerant quantum compiler web interface.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="interface to bind (default: %(default)s; use 0.0.0.0 to expose it)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="port to bind (default: %(default)s)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="restart on source changes; for development only",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="uvicorn log level (default: %(default)s)",
    )
    return parser


def preflight() -> bool:
    """Report on the compiler binary before the first request needs it.

    Missing or stale binaries are far and away the most common way this fails,
    and finding out at startup beats a 422 on the first compile.
    """
    if not compiler.BINARY.is_file():
        print(
            f"warning: no compiler binary at {compiler.BINARY}\n"
            "         build it with:\n"
            "           cmake -S . -B build -DCMAKE_BUILD_TYPE=Release\n"
            "           cmake --build build --target FaultTolerantQuantumCompiler "
            "--parallel\n"
            "         or point FTQC_BINARY at an existing one. The interface "
            "will load, but every compile will fail.",
            file=sys.stderr,
        )
        return False

    # Flushed explicitly: stdout is block-buffered when it is a pipe or a log
    # file, which would otherwise strand the banner behind uvicorn's own
    # startup lines, or lose it entirely if the process is killed.
    circuits = len(compiler.available_circuits())
    print(f"compiler: {compiler.BINARY}", flush=True)
    print(f"circuits: {circuits} found under {compiler.REPO_ROOT}", flush=True)
    if circuits == 0:
        print(
            "warning: no .qasm files found — only pasted circuits will work.",
            file=sys.stderr,
        )
    return True


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Imported here rather than at module scope so `--help` and the preflight
    # check still work when uvicorn is not installed.
    try:
        import uvicorn
    except ImportError:
        print(
            "error: uvicorn is not installed. Install the server's "
            "dependencies with:\n"
            "  pip install -r webserver/requirements.txt",
            file=sys.stderr,
        )
        return 1

    preflight()
    print(f"serving on http://{args.host}:{args.port}", flush=True)

    uvicorn.run(
        APP_PATH,
        host=args.host,
        port=args.port,
        reload=args.reload,
        # Without this the reloader watches the whole repository, and the
        # thousands of circuit files make every restart crawl.
        reload_dirs=[str(compiler.REPO_ROOT / "webserver")] if args.reload else None,
        log_level=args.log_level,
    )
    return 0
