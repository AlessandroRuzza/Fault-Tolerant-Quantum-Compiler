#!/usr/bin/env sh
set -eu

PROJECT="${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}"

ffmpeg -y \
  -framerate 2 \
  -i "$PROJECT/visualization/gaussian_frames/gaussians_%d.png" \
  -framerate 2 \
  -i "$PROJECT/visualization/gaussian_frames/gaussians_sum_%d.png" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  "$PROJECT/visualization/gaussian_frames/gaussians_2fps.gif"
