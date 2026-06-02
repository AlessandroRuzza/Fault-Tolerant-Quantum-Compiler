# syntax=docker/dockerfile:1.7

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — System build tools
# Rarely changes → sits high in the cache chain.
# BuildKit cache-mounts keep apt archives out of the image layers entirely.
# ─────────────────────────────────────────────────────────────────────────────
FROM debian:bookworm-slim AS sys-deps

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        libeigen3-dev \
        libboost-dev

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — External / submodule deps
# Invalidated only when external/ (nlohmann_json submodule) changes.
# ─────────────────────────────────────────────────────────────────────────────
FROM sys-deps AS ext-deps

WORKDIR /app
COPY external/ ./external/

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3 — Compile
# Invalidated when CMakeLists.txt, include/, or src/ change.
# LTO (IPO) + symbol stripping minimize the binary shipped to the runtime.
# ─────────────────────────────────────────────────────────────────────────────
FROM ext-deps AS builder

COPY CMakeLists.txt ./
COPY include/        ./include/
COPY src/            ./src/
COPY visualization/  ./visualization/

RUN cmake -S . -B build \
        -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
        -DEIGEN3_INCLUDE_DIR=/usr/include/eigen3 \
        -DBOOST_INCLUDEDIR=/usr/include \
 && cmake --build build --target FaultTolerantQuantumCompiler --parallel "$(nproc)" \
 && strip --strip-all build/FaultTolerantQuantumCompiler

# ─────────────────────────────────────────────────────────────────────────────
# Stage 4 — Minimal runtime image
# Only the stripped binary + runtime data files land here.
# cmake/ninja/gcc/headers are NOT copied — saves ~500 MB.
# ─────────────────────────────────────────────────────────────────────────────
FROM debian:bookworm-slim AS runtime

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        make \
        libgomp1 \
        libstdc++6 \
        gnuplot \
        python3 \
        python3-pip \
        python3-venv

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir matplotlib

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Stripped binary from builder
COPY --from=builder /app/build/FaultTolerantQuantumCompiler ./build/FaultTolerantQuantumCompiler

# Runtime support files
COPY scripts/                ./scripts/
COPY config/                 ./config/
COPY graphs/                 ./graphs/
COPY qasms/                  ./qasms/
COPY universal_set_qasms/    ./universal_set_qasms/

# Writable benchmark output directories
RUN mkdir -p benchmarks/results benchmarks/logs

# Thin Makefile so "make run-bench [BENCH_PATH=<name>]" works without cmake.
# run-bench.sh reads BENCH_PATH from the environment when not set on the
# command line, so both "docker run -e BENCH_PATH=..." and
# "docker run ... make run-bench BENCH_PATH=..." work.
RUN printf '.PHONY: run-bench\nrun-bench:\n\tsh /app/scripts/run-bench.sh /app/build/FaultTolerantQuantumCompiler\n' \
    > /app/Makefile

# ─────────────────────────────────────────────────────────────────────────────
# Stage 5 — Entry-point layer
# Only ENV / CMD live here; editing them doesn't invalidate any layer above.
# ─────────────────────────────────────────────────────────────────────────────
FROM runtime AS final

# Default benchmark; override at run-time:
#   docker run --init -e BENCH_PATH=gaussian_coarse_vs_fine <image>
#   docker run --init <image> make run-bench BENCH_PATH=cache_vs_no_cache
ENV BENCH_PATH=naive_congestion_boost_normal_t_smart_t

# Default BENCH_JOBS = all cores

# IMPORTANT: launch with `docker run --init ...` so tini becomes PID 1 and
# forwards signals to the benchmark binary. run-bench.sh `exec`s the binary,
# so SIGINT/SIGTERM/SIGHUP land directly on it and trigger a clean "interrupted"
# write to the CSV before exiting.
CMD ["sh", "/app/scripts/run-bench.sh", "/app/build/FaultTolerantQuantumCompiler"]
