#!/usr/bin/env python3
"""Compare our compiler's benchmark results against WISQ on shared circuits.

Loads all our tool CSVs (glob) + a WISQ CSV, finds circuits that both ran
successfully, then generates comparison plots separated by metric:
  - routing steps (heatmap, ratio heatmap, grouped bars, scatter)
  - execution time  (heatmap, ratio heatmap, grouped bars, scatter)
"""

import argparse
import csv
import glob
import math
import os
import sys
import warnings
from collections import defaultdict

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

SUCCESS_STATUSES = {"ok", "ok_no_routing_metric", "success"}
DEFAULT_RESULTS_DIR = os.path.join("benchmarks", "results")
DEFAULT_OUR_GLOB = os.path.join(DEFAULT_RESULTS_DIR, "**", "*.csv")
DEFAULT_WISQ_CSV = os.path.join(DEFAULT_RESULTS_DIR, "wisq_run2.csv")
DEFAULT_OUTPUT_DIR = os.path.join(DEFAULT_RESULTS_DIR, "wisq_comparison_plots")

CONFIG_KEY_FIELDS = [
    "mapping_type",
    "gaussian_strategy",
    "magic_aware_strategy",
    "safe_passage_strategy",
    "routing_strategy",
    "t_routing_mode",
    "magic_state_placement_strategy",
]

FIELD_ABBREV = {
    "mapping_type": {"gaussian": "gauss", "magic_aware": "magic", "homogeneous": "homo"},
    "gaussian_strategy": {"coarse": "coarse", "fine": "fine"},
    "magic_aware_strategy": {"center": "ctr", "distance": "dist", "random": "rnd"},
    "safe_passage_strategy": {
        "cube": "cube",
        "connectivity": "conn",
        "passage_no_subgraphs": "pass",
    },
    "routing_strategy": {"naive": "naive", "congestion": "cong"},
    "t_routing_mode": {"normal_t_routing": "nT", "smart_t_routing": "sT"},
    "magic_state_placement_strategy": {
        "center_circle": "ccircle",
        "right_row": "rrow",
    },
}


# ── helpers ───────────────────────────────────────────────────────────────────

def to_float(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def to_int(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        try:
            return int(float(s))
        except ValueError:
            return None


def norm(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def is_success(row):
    return norm(row.get("status")) in SUCCESS_STATUSES


def save_fig(fig, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"  saved: {path}")


def cg_label_for(row, circuit_key="circuit", gx_keys=("graph_x", "x"), gy_keys=("graph_y", "y")):
    explicit = (row.get("circuit_graph_label") or "").strip()
    if explicit:
        return explicit
    circuit = (row.get(circuit_key) or "").strip()
    gx = next((to_int(row.get(k)) for k in gx_keys if row.get(k)), None)
    gy = next((to_int(row.get(k)) for k in gy_keys if row.get(k)), None)
    if circuit and gx is not None and gy is not None:
        return f"{circuit}-{gx}x{gy}"
    return circuit


# ── loading ───────────────────────────────────────────────────────────────────

def load_our_csvs(glob_pattern):
    """Load all our-tool CSVs matched by glob. Automatically skips WISQ CSVs."""
    files = sorted(glob.glob(glob_pattern, recursive=True))
    rows = []
    for path in files:
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    continue
                fnames = [fn.strip() for fn in reader.fieldnames]
                if "tool" in fnames:
                    continue
                if "status" not in fnames:
                    continue
                if "run_id" not in fnames and "id" not in fnames:
                    continue
                for raw in reader:
                    row = {fn.strip(): v for fn, v in raw.items()}
                    row["_source"] = os.path.basename(path)
                    rows.append(row)
        except OSError:
            continue
    return rows


def load_wisq_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{k.strip(): v for k, v in raw.items()} for raw in reader]


def prepare_our_rows(raw_rows):
    rows = []
    for raw in raw_rows:
        row = dict(raw)
        row["routing_steps_f"] = to_float(
            raw.get("routing_steps") or raw.get("total_routing_steps")
        )
        dur = to_float(raw.get("duration_seconds"))
        if dur is None:
            elapsed = to_float(raw.get("elapsed_ms"))
            dur = elapsed / 1000.0 if elapsed is not None else None
        row["duration_s_f"] = dur
        row["success"] = is_success(row)
        row["cg_label"] = cg_label_for(row)
        rows.append(row)
    return rows


def prepare_wisq_rows(raw_rows):
    rows = []
    for raw in raw_rows:
        row = dict(raw)
        row["routing_steps_f"] = to_float(raw.get("routing_steps"))
        row["duration_s_f"] = to_float(raw.get("duration_seconds"))
        row["success"] = is_success(row)
        row["cg_label"] = cg_label_for(row)
        rows.append(row)
    return rows


# ── config labeling ───────────────────────────────────────────────────────────

def find_varying_fields(rows):
    value_sets = defaultdict(set)
    for row in rows:
        for field in CONFIG_KEY_FIELDS:
            value_sets[field].add(norm(row.get(field)))
    return [f for f in CONFIG_KEY_FIELDS if len(value_sets[f]) > 1]


def config_label(row, varying_fields):
    parts = []
    for field in varying_fields:
        val = norm(row.get(field))
        if not val:
            continue
        abbrevs = FIELD_ABBREV.get(field, {})
        parts.append(abbrevs.get(val, val))
    return "+".join(parts) if parts else "default"


# ── aggregation ───────────────────────────────────────────────────────────────

def aggregate_our(rows, varying_fields):
    """dict[cg_label][config_label] -> stats dict. Only successful rows."""
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["cg_label"]][config_label(row, varying_fields)].append(row)

    result = {}
    for cg, cfg_map in grouped.items():
        result[cg] = {}
        for label, cfg_rows in cfg_map.items():
            r_vals = [r["routing_steps_f"] for r in cfg_rows if r["routing_steps_f"] is not None]
            d_vals = [r["duration_s_f"] for r in cfg_rows
                      if r["duration_s_f"] is not None and r["duration_s_f"] > 0]
            result[cg][label] = {
                "routing_min": min(r_vals) if r_vals else None,
                "routing_median": float(np.median(r_vals)) if r_vals else None,
                "routing_mean": float(np.mean(r_vals)) if r_vals else None,
                "duration_min": min(d_vals) if d_vals else None,
                "duration_median": float(np.median(d_vals)) if d_vals else None,
                "duration_mean": float(np.mean(d_vals)) if d_vals else None,
                "n": len(cfg_rows),
            }
    return result


def aggregate_wisq(rows):
    """dict[cg_label] -> {routing, duration, n}. Only successful rows."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["cg_label"]].append(row)

    agg = {}
    for cg, cg_rows in grouped.items():
        r_vals = [r["routing_steps_f"] for r in cg_rows if r["routing_steps_f"] is not None]
        d_vals = [r["duration_s_f"] for r in cg_rows if r["duration_s_f"] is not None]
        agg[cg] = {
            "routing": float(np.median(r_vals)) if r_vals else None,
            "duration": float(np.median(d_vals)) if d_vals else None,
            "n": len(cg_rows),
        }
    return agg


# ── matrix builder ────────────────────────────────────────────────────────────

def build_matrix(circuits, our_agg, wisq_agg, config_labels, our_key, wisq_key):
    """Returns (matrix, col_labels) where last col is wisq."""
    cols = config_labels + ["wisq"]
    mat = np.full((len(circuits), len(cols)), np.nan)
    for ci, cg in enumerate(circuits):
        for li, label in enumerate(config_labels):
            entry = our_agg.get(cg, {}).get(label)
            if entry:
                val = entry.get(our_key)
                if val is not None:
                    mat[ci, li] = val
        w = wisq_agg.get(cg, {}).get(wisq_key)
        if w is not None:
            mat[ci, -1] = w
    return mat, cols


# ── plot: per-circuit value bars ──────────────────────────────────────────────

def plot_circuit_bars(cg, cfg_map, wisq_val, our_key, ylabel, title, filename, circuit_dir, generated):
    """Bar chart for one circuit: all our configs + wisq bar highlighted in red."""
    labels = sorted(cfg_map.keys())
    our_vals = [cfg_map[lbl].get(our_key) for lbl in labels]
    cols = labels + ["wisq"]
    plot_vals = [(v if v is not None else 0) for v in our_vals] + \
                ([wisq_val] if wisq_val is not None else [0])
    colors = ["#1d4ed8"] * len(labels) + ["#e11d48"]
    alphas_mark = [0.87 if v is not None else 0.3 for v in our_vals] + [0.9]

    fig_w = max(10, 1.8 + len(cols) * 0.38)
    fig, ax = plt.subplots(figsize=(fig_w, 6))

    bars = ax.bar(range(len(cols)), plot_vals, color=colors, alpha=0.87,
                  edgecolor="white", linewidth=0.5)
    for bar, a in zip(bars, alphas_mark):
        bar.set_alpha(a)

    if wisq_val is not None:
        lbl_txt = str(int(round(wisq_val))) if abs(wisq_val - round(wisq_val)) < 1e-9 else f"{wisq_val:.3g}"
        ax.axhline(wisq_val, color="#e11d48", linewidth=1.4, linestyle="--",
                   alpha=0.65, label=f"wisq = {lbl_txt}")
        ax.legend(fontsize=9)

    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=50, ha="right", fontsize=7.5)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(f"{title}\n{cg}", fontsize=12, pad=10)
    ax.grid(True, axis="y", alpha=0.3)

    path = os.path.join(circuit_dir, filename)
    save_fig(fig, path)
    generated.append(path)


# ── plot: per-circuit ratio bars ──────────────────────────────────────────────

def plot_circuit_ratio_bars(cg, cfg_map, wisq_val, our_key, ylabel, title, filename, circuit_dir, generated):
    """Ratio bars (our/wisq) for one circuit. Green < 1 = ours better."""
    if wisq_val is None or wisq_val == 0:
        return

    labels = sorted(cfg_map.keys())
    ratios = []
    for lbl in labels:
        v = cfg_map[lbl].get(our_key)
        ratios.append(v / wisq_val if v is not None else None)

    if not any(r is not None for r in ratios):
        return

    colors = ["#16a34a" if (r is not None and r < 1.0)
              else "#dc2626" if r is not None
              else "#94a3b8"
              for r in ratios]
    plot_ratios = [(r if r is not None else 0) for r in ratios]

    fig_w = max(10, 1.8 + len(labels) * 0.38)
    fig, ax = plt.subplots(figsize=(fig_w, 6))

    bars = ax.bar(range(len(labels)), plot_ratios, color=colors, alpha=0.87,
                  edgecolor="white", linewidth=0.5)
    for bar, r in zip(bars, ratios):
        if r is None:
            bar.set_alpha(0.3)

    ax.axhline(1.0, color="#334155", linewidth=1.4, linestyle="--", label="parity (= wisq)")

    better = sum(1 for r in ratios if r is not None and r < 1.0)
    worse = sum(1 for r in ratios if r is not None and r >= 1.0)
    ax.text(0.01, 0.98,
            f"our < wisq (better): {better}   our ≥ wisq: {worse}",
            transform=ax.transAxes, va="top", ha="left", fontsize=8.5,
            bbox={"facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.85})

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=50, ha="right", fontsize=7.5)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(f"{title}\n{cg}\n(green < 1 = ours better, red ≥ 1 = wisq better)", fontsize=11, pad=10)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    path = os.path.join(circuit_dir, filename)
    save_fig(fig, path)
    generated.append(path)


# ── plot: cross-circuit summary heatmap ───────────────────────────────────────

def plot_summary_heatmap(mat, row_labels, col_labels, title, cbar_label, filename, output_dir, generated):
    """One-row-per-circuit heatmap for cross-circuit overview."""
    n_rows, n_cols = mat.shape
    fig_w = max(10, 1.5 + n_cols * 1.2)
    fig_h = max(5, 1.5 + n_rows * 0.52)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.subplots_adjust(left=0.34, right=0.91, top=0.91, bottom=0.22)

    masked = np.ma.array(mat, mask=np.isnan(mat))
    im = ax.imshow(masked, aspect="auto", cmap="YlOrRd")

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels, rotation=44, ha="right", fontsize=7.5)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=7.5)
    ax.set_title(title, fontsize=12, pad=14)
    ax.set_xlabel("configuration", fontsize=9)
    ax.set_ylabel("circuit × graph", fontsize=9)

    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.9)
    ax.tick_params(which="minor", bottom=False, left=False)

    vmin = float(np.nanmin(mat)) if not np.all(np.isnan(mat)) else 0.0
    vmax = float(np.nanmax(mat)) if not np.all(np.isnan(mat)) else 1.0
    span = (vmax - vmin) or 1.0

    for ri in range(n_rows):
        for ci in range(n_cols):
            val = mat[ri, ci]
            if np.isnan(val):
                ax.text(ci, ri, "—", ha="center", va="center", fontsize=7, color="#94a3b8")
            else:
                bright = (val - vmin) / span
                color = "white" if bright > 0.62 else "#0f172a"
                txt = str(int(round(val))) if abs(val - round(val)) < 1e-9 else f"{val:.3g}"
                ax.text(ci, ri, txt, ha="center", va="center", fontsize=7,
                        color=color, fontweight="bold")

    ax.axvline(n_cols - 1 - 0.5, color="#1e3a5f", linewidth=1.8, alpha=0.65)

    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label(cbar_label, fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    save_fig(fig, os.path.join(output_dir, filename))
    generated.append(os.path.join(output_dir, filename))


# ── plot: scatter our-best vs wisq ───────────────────────────────────────────

def plot_scatter(circuits, our_agg, wisq_agg, our_agg_key, wisq_key,
                 xlabel, ylabel, title, filename, output_dir, generated,
                 log_scale=False):
    our_vals, wisq_vals, labels = [], [], []

    for cg in circuits:
        w = wisq_agg.get(cg, {}).get(wisq_key)
        if w is None:
            continue
        entries = our_agg.get(cg, {}).values()
        vals = [e[our_agg_key] for e in entries if e.get(our_agg_key) is not None]
        if not vals:
            continue
        our_vals.append(min(vals))
        wisq_vals.append(w)
        labels.append(cg)

    if not our_vals:
        return

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(wisq_vals, our_vals, s=65, alpha=0.82, color="#1d4ed8", zorder=3)

    for x, y, lbl in zip(wisq_vals, our_vals, labels):
        ax.annotate(lbl, (x, y), textcoords="offset points", xytext=(5, 4),
                    fontsize=7, color="#475569")

    all_v = wisq_vals + our_vals
    lo = min(all_v) * (0.5 if log_scale else 0.9)
    hi = max(all_v) * (2.0 if log_scale else 1.1)
    ax.plot([lo, hi], [lo, hi], "--", color="#94a3b8", linewidth=1.2, label="parity (equal)")

    below = sum(1 for o, w in zip(our_vals, wisq_vals) if o < w)
    above = len(our_vals) - below
    ax.text(0.03, 0.97,
            f"our < wisq (better): {below}/{len(our_vals)}\n"
            f"our > wisq (worse):  {above}/{len(our_vals)}",
            transform=ax.transAxes, va="top", ha="left", fontsize=9,
            bbox={"facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.88})

    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(f"{title}\n({len(our_vals)} common circuits)", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, which="both" if log_scale else "major")
    if log_scale:
        ax.set_xscale("log")
        ax.set_yscale("log")

    save_fig(fig, os.path.join(output_dir, filename))
    generated.append(os.path.join(output_dir, filename))


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compare our compiler vs WISQ on shared circuits."
    )
    parser.add_argument("--our-csv", default=DEFAULT_OUR_GLOB,
                        help=f"Glob/file for our tool CSVs (default: {DEFAULT_OUR_GLOB})")
    parser.add_argument("--wisq-csv", default=DEFAULT_WISQ_CSV,
                        help=f"WISQ results CSV (default: {DEFAULT_WISQ_CSV})")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help=f"Plot output dir (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--metric", choices=["routing", "duration", "both"], default="both")
    args = parser.parse_args()

    print(f"Loading our CSVs: {args.our_csv}")
    our_raw = load_our_csvs(args.our_csv)
    if not our_raw:
        print(f"ERROR: no rows found matching {args.our_csv}", file=sys.stderr)
        sys.exit(1)
    our_rows = prepare_our_rows(our_raw)
    our_ok = [r for r in our_rows if r["success"]]
    print(f"  {len(our_rows)} rows loaded, {len(our_ok)} successful")

    print(f"Loading WISQ CSV: {args.wisq_csv}")
    wisq_raw = load_wisq_csv(args.wisq_csv)
    wisq_rows = prepare_wisq_rows(wisq_raw)
    wisq_ok = [r for r in wisq_rows if r["success"]]
    print(f"  {len(wisq_rows)} rows loaded, {len(wisq_ok)} successful")

    our_circuits = {r["cg_label"] for r in our_ok}
    wisq_circuits = {r["cg_label"] for r in wisq_ok}
    common = sorted(our_circuits & wisq_circuits)
    print(f"\nCommon circuits ({len(common)}):")
    for c in common:
        print(f"  {c}")

    if not common:
        print("ERROR: no common circuits.", file=sys.stderr)
        sys.exit(1)

    our_filtered = [r for r in our_ok if r["cg_label"] in common]
    wisq_filtered = [r for r in wisq_ok if r["cg_label"] in common]

    varying = find_varying_fields(our_filtered)
    print(f"\nVarying config fields: {varying}")

    our_agg = aggregate_our(our_filtered, varying)
    wisq_agg = aggregate_wisq(wisq_filtered)

    all_cfg_labels = sorted({
        lbl
        for cg in common
        for lbl in our_agg.get(cg, {})
    })
    print(f"Config labels ({len(all_cfg_labels)}): {all_cfg_labels}")

    os.makedirs(args.output_dir, exist_ok=True)
    generated = []

    do_routing = args.metric in ("routing", "both")
    do_duration = args.metric in ("duration", "both")

    # ── per-circuit subfolders ────────────────────────────────────────────────
    for cg in common:
        circuit_dir = os.path.join(args.output_dir, cg)
        os.makedirs(circuit_dir, exist_ok=True)
        cfg_map = our_agg.get(cg, {})
        wisq_entry = wisq_agg.get(cg, {})

        if do_routing:
            print(f"\n── {cg}: routing ──")
            plot_circuit_bars(
                cg, cfg_map, wisq_entry.get("routing"),
                "routing_min", "routing steps",
                "Routing Steps: Our Configs vs WISQ  (ours = min over runs)",
                "bars_routing_steps.png", circuit_dir, generated,
            )
            plot_circuit_ratio_bars(
                cg, cfg_map, wisq_entry.get("routing"),
                "routing_min", "routing steps ratio (our ÷ wisq)",
                "Routing Steps Ratio: Our ÷ WISQ",
                "ratio_routing.png", circuit_dir, generated,
            )

        if do_duration:
            print(f"\n── {cg}: duration ──")
            plot_circuit_bars(
                cg, cfg_map, wisq_entry.get("duration"),
                "duration_median", "duration (s)",
                "Execution Time: Our Configs vs WISQ  (ours = median over runs)",
                "bars_duration.png", circuit_dir, generated,
            )
            plot_circuit_ratio_bars(
                cg, cfg_map, wisq_entry.get("duration"),
                "duration_median", "duration ratio (our ÷ wisq)",
                "Duration Ratio: Our ÷ WISQ",
                "ratio_duration.png", circuit_dir, generated,
            )

    # ── cross-circuit summary: scatter + heatmaps in root ────────────────────
    print("\n── Cross-circuit summary plots ──")
    if do_routing:
        r_mat, r_cols = build_matrix(common, our_agg, wisq_agg, all_cfg_labels,
                                     "routing_min", "routing")
        plot_summary_heatmap(
            r_mat, common, r_cols,
            "Routing Steps: Our Configs vs WISQ  (ours = min per config)",
            "routing steps",
            "summary_heatmap_routing.png", args.output_dir, generated,
        )
        plot_scatter(
            common, our_agg, wisq_agg,
            "routing_min", "routing",
            "wisq routing steps",
            "our best routing steps (min over all configs)",
            "Our Best Routing Steps vs WISQ",
            "scatter_routing_vs_wisq.png", args.output_dir, generated,
        )

    if do_duration:
        d_mat, d_cols = build_matrix(common, our_agg, wisq_agg, all_cfg_labels,
                                     "duration_median", "duration")
        plot_summary_heatmap(
            d_mat, common, d_cols,
            "Execution Time (s): Our Configs vs WISQ  (ours = median per config)",
            "duration (s)",
            "summary_heatmap_duration.png", args.output_dir, generated,
        )
        plot_scatter(
            common, our_agg, wisq_agg,
            "duration_min", "duration",
            "wisq duration (s)",
            "our best duration (s, min over all configs)",
            "Our Best Duration vs WISQ",
            "scatter_duration_vs_wisq.png", args.output_dir, generated,
            log_scale=True,
        )

    print(f"\n{len(generated)} plots → {args.output_dir}/")
    for p in generated:
        print(f"  {p}")


if __name__ == "__main__":
    main()
