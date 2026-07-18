#!/usr/bin/env python3
"""Render publication figures of the Gaussian placement score field.

Reads the per-frame ``.dat`` grids dumped by the compiler into
``visualization/gaussian_frames/`` (see src/mapping/gaussian_images.hpp) and
produces two PDFs for paper/paper.tex:

  * gaussian_fields.pdf  -> fig:fields  (decomposition: the four field families
                            + their superposition S, for one qubit)
  * gaussian_frames.pdf  -> fig:frames  (formation strip: the real total score
                            surface S as the layout forms, with committed
                            patches and magic tiles marked)

The formation strip uses the genuine ``total_N.dat`` surfaces.  The
decomposition is a canonical illustration computed from the method's own
formula (gaussian.cpp / gaussians.hpp) on the real lattice geometry and real
magic-tile positions, with field signs chosen as Section "Influence Fields"
describes (T-heavy qubit -> magic attractive).  Because real benchmarks rarely
exercise the magic *and* CNOT-partner families in the same frame, rendering the
decomposition from the formula is what keeps all four panels populated.

Usage:

    env/bin/python3 scripts/plots/render_paper_gaussians.py

The gaussian_frames dump the paper figure is rendered from was produced by the
JUNE binary (commit 19bf732, e.g. `git worktree add tmp/oldbin 19bf732`) --
today's `fine` strategy amplifies the magic weight per qubit, which buries the
repulsion wells under giant magic peaks:

    FTQC_SAVE_FRAMES=1 build/FaultTolerantQuantumCompiler \
        --circuit factor247_n15 --type gaussian --safe-passage connectivity \
        --magic-high 1.5 --mapped-gaussian-weight 3.5 --cnot-high 1.5 \
        --gaussian-sigma 0.85 --repetition 1

Illustrative weights, not the tuned ones, chosen so wells and magic bumps read
at a comparable scale.  Magic-tile positions come from magic_tiles.dat when
present (dumped from the graph by gaussian_images.hpp even at magic weight 0);
for older dumps like this one they are recovered from the magic_component
layers.
"""

import argparse
import glob
import os
import re

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import cm  # noqa: E402
from mpl_toolkits.mplot3d import Axes3D  # noqa: E402,F401  (registers 3d proj)

# ---------------------------------------------------------------------------
# Exact replication of the C++ Gaussian (include/gaussian.hpp, src/gaussian.cpp,
# src/mapping/gaussians.hpp). Kept faithful so the decomposition matches what
# the compiler would score.
# ---------------------------------------------------------------------------
KCUTOFF_ABS = 1e-3


def compute_sigma(radius, confidence):
    """sigma = R / sqrt(-2 ln(1-kappa))  (eq:sigma)."""
    return radius / np.sqrt(-2.0 * np.log(1.0 - confidence))


def gaussian_field(XX, YY, mx, my, sigma, weight, inverse):
    """Evaluate one influence field on a mesh; mirrors Gaussian::gaussian_at."""
    if weight == 0.0:
        return np.zeros_like(XX)
    inv_two_sigma_sq = 1.0 / (2.0 * sigma * sigma)
    exponent = -((XX - mx) ** 2) * inv_two_sigma_sq - ((YY - my) ** 2) * inv_two_sigma_sq
    cutoff = np.log(KCUTOFF_ABS / abs(weight))
    below = exponent < cutoff
    g = np.exp(exponent) * weight
    if inverse:  # valley at centre, rises to |weight| far away
        return np.where(below, weight, np.maximum(weight - g, 0.0))
    return np.where(below, 0.0, g)


# ---------------------------------------------------------------------------
# .dat helpers
# ---------------------------------------------------------------------------
def load_grid(path):
    """Load an 'x y z' .dat into Z[h, w] (blank lines ignored by loadtxt)."""
    a = np.loadtxt(path)
    x = a[:, 0].astype(int)
    y = a[:, 1].astype(int)
    z = a[:, 2]
    w = int(x.max()) + 1
    h = int(y.max()) + 1
    Z = np.zeros((h, w))
    Z[y, x] = z
    return Z, w, h


def component_paths(frames_dir, prefix, frame):
    """All single-Gaussian layers for `frame` (first index in the filename)."""
    out = []
    pat = re.compile(rf"{re.escape(prefix)}_component_(\d+)_(\d+)\.dat$")
    for p in glob.glob(os.path.join(frames_dir, f"{prefix}_component_*.dat")):
        m = pat.match(os.path.basename(p))
        if m and int(m.group(1)) == frame:
            out.append(p)
    return sorted(out)


def component_center(path):
    """Centre of a single field = cell furthest from the layer's median value.

    Works whether the layer is attractive (peak above a ~0 bulk) or inverse
    (well below a ~weight bulk)."""
    Z, _, _ = load_grid(path)
    med = np.median(Z)
    idx = int(np.argmax(np.abs(Z - med)))
    yy, xx = np.unravel_index(idx, Z.shape)
    return int(xx), int(yy)


def load_magic_tiles(frames_dir):
    """Real magic-tile coordinates.

    Prefers the ``magic_tiles.dat`` dump (written from the graph, so present
    even when the magic weights are 0); falls back to locating the per-tile
    magic gaussian components of runs where the magic weight was > 0."""
    p = os.path.join(frames_dir, "magic_tiles.dat")
    if os.path.exists(p):
        a = np.loadtxt(p, ndmin=2)
        return [(int(x), int(y)) for x, y in a]
    mf = first_frame_with(frames_dir, "magic")
    if mf is None:
        return []
    return [component_center(q) for q in component_paths(frames_dir, "magic", mf)]


def first_frame_with(frames_dir, prefix):
    pat = re.compile(rf"{re.escape(prefix)}_component_(\d+)_\d+\.dat$")
    frames = sorted(
        {int(pat.match(os.path.basename(p)).group(1))
         for p in glob.glob(os.path.join(frames_dir, f"{prefix}_component_*.dat"))
         if pat.match(os.path.basename(p))}
    )
    return frames[0] if frames else None


def bilinear_upsample(Z, factor):
    """Smooth a coarse per-tile grid for display (numpy only, no scipy)."""
    h, w = Z.shape
    xi = np.linspace(0, w - 1, (w - 1) * factor + 1)
    yi = np.linspace(0, h - 1, (h - 1) * factor + 1)
    x0 = np.floor(xi).astype(int)
    x1 = np.minimum(x0 + 1, w - 1)
    fx = xi - x0
    y0 = np.floor(yi).astype(int)
    y1 = np.minimum(y0 + 1, h - 1)
    fy = yi - y0
    Za = Z[np.ix_(y0, x0)]
    Zb = Z[np.ix_(y0, x1)]
    Zc = Z[np.ix_(y1, x0)]
    Zd = Z[np.ix_(y1, x1)]
    top = Za * (1 - fx)[None, :] + Zb * fx[None, :]
    bot = Zc * (1 - fx)[None, :] + Zd * fx[None, :]
    Zu = top * (1 - fy)[:, None] + bot * fy[:, None]
    XI, YI = np.meshgrid(xi, yi)
    return Zu, XI, YI


# ---------------------------------------------------------------------------
# styling
# ---------------------------------------------------------------------------
def set_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": 8,
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


SURF_CMAP = cm.viridis
HEAT_CMAP = cm.viridis


def _style_3d(ax):
    ax.set_box_aspect((1, 1, 0.55))
    ax.view_init(elev=42, azim=-58)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((1, 1, 1, 0))
        axis.line.set_linewidth(0.4)
    ax.tick_params(labelsize=6, pad=-1, length=2)
    ax.set_zticks([])
    ax.grid(False)


# ---------------------------------------------------------------------------
# fig:fields  -- decomposition (4 heatmaps + 3D superposition)
# ---------------------------------------------------------------------------
def render_fields(args):
    frames_dir = args.frames_dir
    frame = args.fields_frame

    # geometry from a real total grid
    _, w, h = load_grid(os.path.join(frames_dir, f"total_{frame}.dat"))
    maxX, maxY = w - 1, h - 1
    radius = max(maxX // 2, 1)
    sigma = compute_sigma(radius, args.confidence)

    # real magic-tile positions (constant across frames)
    magic = load_magic_tiles(frames_dir)

    # real placed positions at this frame; pick a compact illustrative subset
    placed_all = [component_center(p) for p in component_paths(frames_dir, "mapped", frame)]
    placed = placed_all[: args.illus_placed]
    partners = placed[: args.illus_partners]  # current qubit's frequent partners

    # fine evaluation mesh
    n = args.mesh
    xs = np.linspace(-0.5, maxX+0.5, n+1)
    ys = np.linspace(-0.5, maxY+0.5, n+1)
    XX, YY = np.meshgrid(xs, ys)
    # imshow extent must match the mesh domain, else markers misalign / clip
    extent = [xs[0], xs[-1], ys[0], ys[-1]]

    def stack(centres, weight, inverse, XX=XX, YY=YY):
        F = np.zeros_like(XX, dtype=float)
        for (mx, my) in centres:
            F += gaussian_field(XX, YY, mx, my, sigma, weight, inverse)
        return F

    f_magic = stack(magic, args.magic_high, inverse=False)          # T-heavy -> pull
    f_cnot = stack(partners, args.cnot_high, inverse=False)         # cluster
    f_mapped = stack(placed, args.mapped_weight, inverse=True)      # spread out
    f_base = gaussian_field(XX, YY, maxX // 2, maxY // 2, sigma, args.base_weight, False)
    S = f_magic + f_cnot + f_mapped + f_base

    # final mapping spot: the current qubit lands on the *lattice cell* with the
    # highest total score. Evaluate S on integer coords (not the fine display
    # mesh) and mask out occupied cells -- magic tiles and already-placed qubits.
    GX, GY = np.meshgrid(np.arange(w), np.arange(h))
    Sg = (stack(magic, args.magic_high, inverse=False, XX=GX, YY=GY)
          + stack(partners, args.cnot_high, inverse=False, XX=GX, YY=GY)
          + stack(placed, args.mapped_weight, inverse=True, XX=GX, YY=GY)
          + gaussian_field(GX, GY, maxX // 2, maxY // 2, sigma, args.base_weight, False))
    occupied = set(magic) | set(placed)
    for (ox, oy) in occupied:
        Sg[oy, ox] = -np.inf
    peak_yy, peak_xx = np.unravel_index(int(np.argmax(Sg)), Sg.shape)
    map_x, map_y = int(GX[peak_yy, peak_xx]), int(GY[peak_yy, peak_xx])

    from matplotlib.lines import Line2D

    set_style()
    fig = plt.figure(figsize=(args.fields_w, args.fields_h), constrained_layout=True)
    # extra short bottom row holds the shared marker legend
    gs = fig.add_gridspec(3, 3, width_ratios=[1, 1, 1.45],
                          height_ratios=[1, 1, 0.30])

    # Each family is shown on its own colour scale (with its own colourbar): the
    # repulsion field sums many inverse Gaussians into a tall plateau, so a single
    # shared scale would crush the lower-magnitude magic/CNOT/baseline panels.
    panels = [
        (f_magic, "magic-state", gs[0, 0]),
        (f_cnot, "partner", gs[0, 1]),
        (f_mapped, "repulsion", gs[1, 0]),
        (f_base, "centering", gs[1, 1]),
    ]
    for F, title, cell in panels:
        ax = fig.add_subplot(cell)
        im = ax.imshow(F, origin="lower", extent=extent,
                       cmap=HEAT_CMAP, aspect="auto", interpolation="bilinear")
        ax.set_title(title, pad=2, fontsize=11)
        ax.set_xticks(range(0, maxX + 1, 2))
        ax.set_yticks(range(0, maxY + 1, 2))
        ax.tick_params(labelsize=5, length=2)
        if title == "magic-state":
            for (mx, my) in magic:
                ax.plot(mx, my, marker="*", color="white", ms=8, mew=0.7, mec="black")
        if title == "partner":
            for (mx, my) in partners:
                ax.plot(mx, my, marker="o", color="white", ms=5, mew=0.6, mec="black")
        if title == "repulsion":
            for (mx, my) in placed:
                ax.plot(mx, my, marker="s", color="white", ms=5, mew=0.6, mec="black")
        cbf = fig.colorbar(im, ax=ax, location="right", shrink=0.9,
                           aspect=12, pad=0.03)
        cbf.ax.tick_params(labelsize=6.5, length=1.5)
        cbf.set_ticks([float(F.min()), float(F.max())])
        cbf.ax.set_yticklabels([f"{F.min():.1f}", f"{F.max():.1f}"])

    # Superposition S as a top-down heatmap, matching the four family panels.
    axS = fig.add_subplot(gs[0:2, 2])
    imS = axS.imshow(S, origin="lower", extent=extent,
                     cmap=HEAT_CMAP, aspect="auto", interpolation="bilinear")
    axS.set_title(r"superposition $S$", pad=2, fontsize=11)
    axS.set_xlabel("x", labelpad=1, fontsize=10)
    axS.set_ylabel("y", labelpad=1, fontsize=10)
    axS.set_xticks(range(0, maxX + 1, 2))
    axS.set_yticks(range(0, maxY + 1, 2))
    axS.tick_params(labelsize=5, length=2)
    for (mx, my) in magic:
        axS.plot(mx, my, marker="*", color="white", ms=9, mew=0.8, mec="black")
    for (mx, my) in partners:
        axS.plot(mx, my, marker="o", color="white", ms=5, mew=0.7, mec="black")
    for (mx, my) in placed:
        axS.plot(mx, my, marker="s", color="white", ms=5, mew=0.7, mec="black")
    axS.plot(map_x, map_y, marker="X", color="red", ms=9, mew=0.8, mec="black")
    cbS = fig.colorbar(imS, ax=axS, location="right", shrink=0.9, aspect=22, pad=0.02)
    cbS.set_label(r"score $S$", fontsize=10)
    cbS.ax.tick_params(labelsize=7)

    # Shared marker legend in the dedicated bottom row.
    axL = fig.add_subplot(gs[2, :])
    axL.axis("off")
    legend_handles = [
        Line2D([0], [0], linestyle="none", marker="*", markerfacecolor="white",
               markeredgecolor="black", markersize=11, label="magic tile"),
        Line2D([0], [0], linestyle="none", marker="o", markerfacecolor="white",
               markeredgecolor="black", markersize=9, label="partner"),
        Line2D([0], [0], linestyle="none", marker="s", markerfacecolor="white",
               markeredgecolor="black", markersize=9, label="placed qubit"),
        Line2D([0], [0], linestyle="none", marker="X", markerfacecolor="red",
               markeredgecolor="black", markersize=10, label="final mapping"),
    ]
    axL.legend(handles=legend_handles, loc="center", ncol=4, fontsize=10,
               handletextpad=0.4, columnspacing=1.4, framealpha=0.9,
               facecolor="0.85", edgecolor="0.6")

    out = os.path.join(args.out_dir, "gaussian_fields.pdf")
    fig.savefig(out)
    plt.close(fig)
    print(f"[fields] frame={frame} magic={len(magic)} placed={len(placed)} "
          f"partners={len(partners)} -> {out}")


# ---------------------------------------------------------------------------
# fig:frames  -- formation strip (real total surfaces + overlays)
# ---------------------------------------------------------------------------
MAGIC_COLOR = "#FFE0E0"   # red!12: the magic-tile fill of fig:overview (fig_conflict)
MAGIC_EDGE = "#8C0000"    # red!55!black
MAPPED_COLOR = "#C7D3DE"  # ftblue!25: the data-tile azure of fig:overview
MAPPED_EDGE = "#1F4E79"   # ftblue


def render_frames(args):
    frames_dir = args.frames_dir
    frames = args.strip_frames

    magic = load_magic_tiles(frames_dir)

    from matplotlib.patches import Patch
    from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

    set_style()
    fig = plt.figure(figsize=(args.strip_w, args.strip_h))
    # Interleave a thin column between each pair of plots; the shared colourbar
    # lives in a dedicated column at the right end of the strip.
    n = len(frames)
    width_ratios = []
    for i in range(n):
        width_ratios.append(1.0)
        if i < n - 1:
            width_ratios.append(0.05)
    width_ratios.append(0.20)
    gs = fig.add_gridspec(1, len(width_ratios), width_ratios=width_ratios,
                          wspace=0.02)
    plot_cols = [2 * i for i in range(n)]
    cbar_col = len(width_ratios) - 1

    axes, ranges = [], []
    for i, f in enumerate(frames):
        Z, w, h = load_grid(os.path.join(frames_dir, f"total_{f}.dat"))
        Zu, XI, YI = bilinear_upsample(Z, args.upsample)
        placed = [component_center(p) for p in component_paths(frames_dir, "mapped", f)]
        # per-frame normalisation: the score is repulsion-dominated, so the
        # absolute plateau height grows with the placed count; normalising each
        # frame exposes the relief (wells where qubits commit, magic features).
        zlo, zhi = float(Zu.min()), float(Zu.max())
        ax = fig.add_subplot(gs[0, plot_cols[i]], projection="3d")

        # Lattice grid drawn on the floor of the same axes, slightly below the
        # surface: plain tile grid with the magic tiles and committed patches
        # over-painted (named by the colour legend at the bottom).
        floor_z = zlo - 0.08 * (zhi - zlo)
        segs = [[(gx, -0.5, floor_z), (gx, h - 0.5, floor_z)]
                for gx in np.arange(-0.5, w, 1.0)]
        segs += [[(-0.5, gy, floor_z), (w - 0.5, gy, floor_z)]
                 for gy in np.arange(-0.5, h, 1.0)]
        ax.add_collection3d(Line3DCollection(segs, colors="0.75", linewidths=0.35))

        def tile(cx, cy):
            return [(cx - 0.5, cy - 0.5, floor_z), (cx + 0.5, cy - 0.5, floor_z),
                    (cx + 0.5, cy + 0.5, floor_z), (cx - 0.5, cy + 0.5, floor_z)]

        if magic:
            ax.add_collection3d(Poly3DCollection(
                [tile(mx, my) for mx, my in magic],
                facecolors=MAGIC_COLOR, edgecolors=MAGIC_EDGE, linewidths=0.4))
        if placed:
            ax.add_collection3d(Poly3DCollection(
                [tile(px, py) for px, py in placed],
                facecolors=MAPPED_COLOR, edgecolors=MAPPED_EDGE, linewidths=0.4))

        # Slightly translucent surface: the mapped-qubit tiles sit in the grid
        # interior, right under the wells, and an opaque sheet would hide them.
        ax.plot_surface(XI, YI, Zu, cmap=SURF_CMAP, linewidth=0, alpha=0.82,
                        antialiased=True, vmin=zlo, vmax=zhi, rcount=80, ccount=80)
        ax.set_xlim(-0.5, w - 0.5)
        ax.set_ylim(-0.5, h - 0.5)
        ax.set_zlim(floor_z, zhi)
        ax.set_title(f"{len(placed)} qubits placed", pad=-2)
        _style_3d(ax)
        ax.set_xticks(range(0, w, 2))
        ax.set_yticks(range(0, h, 2))
        ax.set_xlabel("x", labelpad=-7)
        ax.set_ylabel("y", labelpad=-7)
        axes.append(ax)
        ranges.append((zlo, zhi))

    # Colour legend for the floor-grid overlays.
    legend_handles = [
        Patch(facecolor=MAGIC_COLOR, edgecolor=MAGIC_EDGE, linewidth=0.6,
              label="magic tile"),
        Patch(facecolor=MAPPED_COLOR, edgecolor=MAPPED_EDGE, linewidth=0.6,
              label="mapped qubit"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=2, fontsize=7,
               handlelength=1.2, handleheight=1.1, handletextpad=0.6,
               columnspacing=1.4, framealpha=0.9, facecolor="0.9",
               edgecolor="0.6", bbox_to_anchor=(0.5, 0.04))

    # Single shared colour scale. Every surface uses the same viridis ramp, but
    # each is normalised to its own [zlo, zhi], so the bar is qualitative:
    # unlabelled, its ends just read "lowest" / "highest" within each frame.
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize
    sm = ScalarMappable(norm=Normalize(0.0, 1.0), cmap=SURF_CMAP)
    # Dedicated axis in the right-hand column: a thin bar, vertically centred
    # (~half height) with empty side columns keeping it clear of the surfaces.
    gap = gs[0, cbar_col].subgridspec(3, 3, height_ratios=[1.0, 3.5, 1.0],
                                      width_ratios=[1.0, 0.5, 1.0])
    cax = fig.add_subplot(gap[1, 1])
    cb = fig.colorbar(sm, cax=cax)
    cax.set_title("score", fontsize=8, pad=9)
    cb.set_ticks([])

    out = os.path.join(args.out_dir, "gaussian_frames.pdf")
    fig.savefig(out)
    plt.close(fig)
    print(f"[frames] frames={frames} magic={len(magic)} -> {out}")


# ---------------------------------------------------------------------------
def main():
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # scripts/plots/ -> root
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frames-dir", default=os.path.join(here, "visualization", "gaussian_frames"))
    ap.add_argument("--out-dir", default=os.path.join(here, "paper_overleaf", "figures"))
    ap.add_argument("--confidence", type=float, default=0.99999)

    # decomposition
    ap.add_argument("--fields-frame", type=int, default=8)
    ap.add_argument("--illus-placed", type=int, default=6,
                    help="how many real placed tiles to show in the illustration")
    ap.add_argument("--illus-partners", type=int, default=2)
    ap.add_argument("--magic-high", type=float, default=0.8)
    ap.add_argument("--cnot-high", type=float, default=1.5)
    ap.add_argument("--mapped-weight", type=float, default=2.0)
    ap.add_argument("--base-weight", type=float, default=1.0)
    ap.add_argument("--mesh", type=int, default=160)
    ap.add_argument("--fields-w", type=float, default=7.0)
    ap.add_argument("--fields-h", type=float, default=3.5)

    # formation strip
    ap.add_argument("--strip-frames", type=lambda s: [int(x) for x in s.split(",")],
                    default=[2, 10])
    ap.add_argument("--upsample", type=int, default=10)
    ap.add_argument("--strip-w", type=float, default=6.5)
    ap.add_argument("--strip-h", type=float, default=3.6)

    ap.add_argument("--only", choices=["fields", "frames"], default=None)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    if args.only != "frames":
        render_fields(args)
    if args.only != "fields":
        render_frames(args)


if __name__ == "__main__":
    main()
