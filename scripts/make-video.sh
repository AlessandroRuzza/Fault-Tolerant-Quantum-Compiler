#!/usr/bin/env sh
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
