#!/usr/bin/env sh
set -eu

PROJECT="${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}"

ffmpeg -y \
  -framerate 2 \
  -i "$PROJECT/visualization/gaussian_frames/gaussians_%d.png" \
  -c:v libx264 \
  -pix_fmt yuv420p \
  "$PROJECT/visualization/gaussian_frames/gaussians_2fps.mp4"
