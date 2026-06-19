#!/usr/bin/env sh
# NOTE: gaussian frames are OFF by default (slow gnuplot render). Enable them
# either by flipping SAVE_GAUSSIAN_FRAMES in src/defines.cpp (+rebuild) or, for
# a one-off, with the env var:
#   FTQC_SAVE_FRAMES=1 ./build/FaultTolerantQuantumCompiler --type gaussian ...
# (frames land in visualization/gaussian_frames/), then run this script.
# Benchmark workers (FTQC_BENCH_WORKER=1) never render frames.
set -eu

PROJECT="${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}"

# Build MP4
ffmpeg -y \
  -framerate 2 \
  -i "$PROJECT/visualization/gaussian_frames/gaussians_%d.png" \
  -framerate 2 \
  -i "$PROJECT/visualization/gaussian_frames/gaussians_sum_%d.png" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" \
  -map "[v]" \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  "$PROJECT/visualization/gaussians_2fps.mp4"

# Build GIF
ffmpeg -y \
  -framerate 2 \
  -i "$PROJECT/visualization/gaussian_frames/gaussians_%d.png" \
  -framerate 2 \
  -i "$PROJECT/visualization/gaussian_frames/gaussians_sum_%d.png" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  "$PROJECT/visualization/gaussians_2fps.gif"
