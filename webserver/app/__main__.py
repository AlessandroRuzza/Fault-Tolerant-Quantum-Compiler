"""Allows ``python3 -m webserver.app [--port 8000]`` from the repository root."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
