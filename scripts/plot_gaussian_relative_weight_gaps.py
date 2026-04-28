#!/usr/bin/env python3

import argparse
import csv
import os
from statistics import median

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib-cache"
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm


DEFAULT_INPUT = os.path.join(
    "benchmarks",
    "results",
    "ex2_runs_plots",
    "best_gaussian_weight_profile_by_circuit_dimension.csv",
)
DEFAULT_OUTPUT_DIR = os.path.join("benchmarks", "results", "ex2_runs_plots")
DEFAULT_PLOT = "31_heatmap_best_gaussian_relative_weight_gaps.png"
DEFAULT_CSV = "best_gaussian_relative_weight_gaps.csv"

WEIGHT_COLUMNS = [
    ("magic high", "magic_high"),
    ("magic low", "magic_low"),
    ("CNOT high", "cnot_high"),
    ("CNOT low", "cnot_low"),
    ("gauss mapped", "mapped_gaussian_weight"),
    ("gauss base", "base_gaussian_weight"),
]


def format_number(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def read_profiles(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    profiles = []
    for row in rows:
        profile = {}
        for label, field in WEIGHT_COLUMNS:
            try:
                profile[label] = float(row[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid or missing numeric field {field!r}") from exc
        profiles.append(profile)
    return profiles


def relative_gap_entries(profiles):
    entries = []
    for row_label, _ in WEIGHT_COLUMNS:
        for col_label, _ in WEIGHT_COLUMNS:
            gaps = [profile[row_label] - profile[col_label] for profile in profiles]
            abs_gaps = [abs(gap) for gap in gaps]
            row_greater = sum(1 for gap in gaps if gap > 0)
            row_less = sum(1 for gap in gaps if gap < 0)
            equal = sum(1 for gap in gaps if gap == 0)
            total = len(gaps)
            entries.append(
                {
                    "row_weight_parameter": row_label,
                    "column_weight_parameter": col_label,
                    "mean_signed_gap": float(np.mean(gaps)) if gaps else 0.0,
                    "median_signed_gap": median(gaps) if gaps else 0.0,
                    "mean_abs_gap": float(np.mean(abs_gaps)) if abs_gaps else 0.0,
                    "median_abs_gap": median(abs_gaps) if abs_gaps else 0.0,
                    "row_greater_count": row_greater,
                    "row_less_count": row_less,
                    "equal_count": equal,
                    "row_greater_percentage": (100.0 * row_greater / total) if total else 0.0,
                }
            )
    return entries


def write_gap_csv(entries, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fieldnames = [
        "row_weight_parameter",
        "column_weight_parameter",
        "mean_signed_gap",
        "median_signed_gap",
        "mean_abs_gap",
        "median_abs_gap",
        "row_greater_count",
        "row_less_count",
        "equal_count",
        "row_greater_percentage",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    return path


def build_matrices(entries):
    labels = [label for label, _ in WEIGHT_COLUMNS]
    by_pair = {
        (entry["row_weight_parameter"], entry["column_weight_parameter"]): entry
        for entry in entries
    }
    signed = np.array(
        [
            [by_pair[(row_label, col_label)]["mean_signed_gap"] for col_label in labels]
            for row_label in labels
        ],
        dtype=float,
    )
    absolute = np.array(
        [
            [by_pair[(row_label, col_label)]["mean_abs_gap"] for col_label in labels]
            for row_label in labels
        ],
        dtype=float,
    )
    return labels, signed, absolute


def annotate_heatmap(ax, matrix, signed=False):
    max_abs = float(np.max(np.abs(matrix))) if matrix.size else 0.0
    for row_idx in range(matrix.shape[0]):
        for col_idx in range(matrix.shape[1]):
            value = matrix[row_idx, col_idx]
            if row_idx == col_idx:
                text = "-"
                color = "#64748B"
            else:
                text = f"{value:+.2f}" if signed else format_number(value)
                color = "white" if max_abs and abs(value) / max_abs > 0.55 else "#0F172A"
            ax.text(
                col_idx,
                row_idx,
                text,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold" if row_idx != col_idx else "normal",
                color=color,
            )


def plot_gap_heatmaps(entries, output_dir, filename, profile_count):
    labels, signed, absolute = build_matrices(entries)
    max_signed = float(np.max(np.abs(signed))) if signed.size else 1.0
    max_abs_gap = float(np.max(absolute)) if absolute.size else 1.0

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.8), constrained_layout=False)
    fig.subplots_adjust(left=0.13, right=0.94, top=0.78, bottom=0.16, wspace=0.34)
    fig.suptitle(
        f"Relative Distances Between Weights in Best Gaussian Configurations (n={profile_count})",
        fontsize=15,
        y=0.96,
    )
    fig.text(
        0.5,
        0.895,
        "Each cell compares the row weight with the column weight. The absolute values of the weights are not counted.",
        ha="center",
        va="center",
        fontsize=9,
        color="#475569",
    )

    signed_norm = TwoSlopeNorm(vmin=-max_signed, vcenter=0, vmax=max_signed)
    signed_image = axes[0].imshow(signed, cmap="RdBu_r", norm=signed_norm)
    abs_image = axes[1].imshow(absolute, cmap="YlGnBu", vmin=0, vmax=max_abs_gap)

    panel_specs = [
        (
            axes[0],
            signed_image,
            "Mean Signed Gap",
            "row - column",
            True,
        ),
        (
            axes[1],
            abs_image,
            "Mean Absolute Distance",
            "|row - column|",
            False,
        ),
    ]

    for ax, image, title, colorbar_label, signed_panel in panel_specs:
        ax.set_title(title, fontsize=12, pad=12)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8.5)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=8.5)
        ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=1.25)
        ax.tick_params(axis="both", length=0)
        ax.tick_params(which="minor", bottom=False, left=False)
        annotate_heatmap(ax, signed if signed_panel else absolute, signed=signed_panel)
        colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.035)
        colorbar.ax.tick_params(labelsize=8)
        colorbar.set_label(colorbar_label, fontsize=9)

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=170, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Plot pairwise relative gaps between gaussian weights."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--plot-name", default=DEFAULT_PLOT)
    parser.add_argument("--csv-name", default=DEFAULT_CSV)
    args = parser.parse_args()

    profiles = read_profiles(args.input)
    entries = relative_gap_entries(profiles)
    csv_path = write_gap_csv(entries, args.output_dir, args.csv_name)
    plot_path = plot_gap_heatmaps(entries, args.output_dir, args.plot_name, len(profiles))
    print(plot_path)
    print(csv_path)


if __name__ == "__main__":
    main()
