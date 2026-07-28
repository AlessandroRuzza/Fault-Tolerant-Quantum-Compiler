# syntax=docker/dockerfile:1.7
#
# Web interface image: the compiler binary plus the Python server that drives it.
#
# Build from the REPOSITORY ROOT, not from webserver/ — the compiler sources and
# the circuit library both live above this file:
#
#   docker build -f webserver/Dockerfile -t ftqc-web .
#   docker run --rm -p 8000:8000 ftqc-web
#
# PROJECT_ROOT is baked into the binary at compile time as the CMake source
# directory, which is /app here. The server's own FTQC_ROOT resolves to the same
# /app, so a bare circuit name means the same file to both halves.

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Compile the compiler
# Mirrors the root Dockerfile's builder: Release + LTO, then stripped.
# ─────────────────────────────────────────────────────────────────────────────
FROM debian:bookworm-slim AS builder

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        libeigen3-dev \
        libboost-dev

WORKDIR /app

# external/ holds the nlohmann_json submodule. Run
# `git submodule update --init --recursive` before building, or the CMake
# configure step will fail on the missing headers.
COPY external/        ./external/
COPY CMakeLists.txt   ./
COPY include/         ./include/
COPY src/             ./src/
COPY visualization/   ./visualization/

RUN cmake -S . -B build \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
        -DEIGEN3_INCLUDE_DIR=/usr/include/eigen3 \
        -DBOOST_INCLUDEDIR=/usr/include \
 && cmake --build build --target FaultTolerantQuantumCompiler --parallel "$(nproc)" \
 && strip --strip-all build/FaultTolerantQuantumCompiler

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Python dependencies
# Kept separate so a change to the server code does not reinstall the wheels.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS python-deps

COPY webserver/requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
 && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3 — Runtime
# No toolchain, no headers: the stripped binary only needs libgomp and libstdc++.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        libstdc++6

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FTQC_ROOT=/app \
    FTQC_BINARY=/app/build/FaultTolerantQuantumCompiler

WORKDIR /app

COPY --from=python-deps /opt/venv /opt/venv
COPY --from=builder /app/build/FaultTolerantQuantumCompiler ./build/FaultTolerantQuantumCompiler

# The circuit library the UI offers, and the server itself.
COPY qasms/              ./qasms/
COPY universal_set_qasms/ ./universal_set_qasms/
COPY webserver/app/     ./webserver/app/
COPY webserver/static/  ./webserver/static/

# Runs are written into a scratch directory and deleted afterwards, so nothing
# needs to be writable outside /tmp.
RUN useradd --create-home --uid 10001 ftqc && chown -R ftqc:ftqc /app
USER ftqc

EXPOSE 8000

# Render (and most PaaS hosts) inject the port to bind. Fall back to 8000 for
# a plain `docker run`.
CMD ["sh", "-c", "exec uvicorn webserver.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
