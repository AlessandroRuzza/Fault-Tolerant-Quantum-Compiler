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

RUN useradd --create-home --uid 10001 ftqc

# The circuit library the UI offers.
#
# A handful of circuits dominate it: the ten largest are ~350 MB of the ~440 MB
# total, and they are exactly the ones a modest instance cannot compile inside
# the request timeout — so shipping them costs image size and buys the user a
# guaranteed timeout. Raise the cut with --build-arg MAX_CIRCUIT_MB=... .
#
# This selects and copies in a single layer rather than copying the directory
# and deleting afterwards. Layers are additive: a COPY of the whole tree
# followed by `find -delete` leaves the full 440 MB sitting in the earlier
# layer and merely adds a tombstone, so the image pays for the big circuits
# either way. Binding the directory as a mount means only kept files are ever
# committed.
#
# `! -size +N M` rather than `-size -N M`: find rounds sizes up to whole units,
# so an 11.3 MB file counts as 12 and `-12M` would drop it. Negating the
# original predicate keeps the boundary exactly where the comment says it is.
#
# Done here rather than in .dockerignore because the benchmark image at the
# repository root copies the same directory and does need the big circuits.
ARG MAX_CIRCUIT_MB=12
RUN --mount=type=bind,source=qasms,target=/ctx/qasms \
    mkdir -p qasms universal_set_qasms visualization \
 && find /ctx/qasms -name '*.qasm' ! -size +${MAX_CIRCUIT_MB}M \
        -exec cp -t qasms/ {} + \
 && echo "circuits kept: $(find qasms -name '*.qasm' | wc -l) of $(find /ctx/qasms -name '*.qasm' | wc -l)" \
 && chown ftqc:ftqc universal_set_qasms visualization /app

# `--chown` on the COPY itself, never a `chown -R` afterwards: a recursive
# chown rewrites every file's metadata, which commits a second full copy of
# everything it touches into a new layer.
COPY --chown=ftqc:ftqc webserver/app/    ./webserver/app/
COPY --chown=ftqc:ftqc webserver/static/ ./webserver/static/

# Not everything a run writes lands in its scratch directory. Several paths are
# anchored to the compiler's compile-time PROJECT_ROOT, which is this /app:
#
#   universal_set_qasms/  a transpiled copy of the circuit, cached per circuit
#   visualization/        recreated on every run (src/one_execution.hpp:98)
#   out/                  only for a relative output_path, which the server
#                         never uses — but cheap to keep possible
#
# Hence /app itself is owned by the runtime user: the compiler creates those
# directories itself, and a blanket `chown -R` would duplicate the whole
# circuit library into another layer just to change its metadata.
USER ftqc

EXPOSE 8000

# Render (and most PaaS hosts) inject the port to bind. Fall back to 8000 for
# a plain `docker run`.
CMD ["sh", "-c", "exec uvicorn webserver.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
