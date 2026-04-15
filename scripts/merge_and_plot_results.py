#!/usr/bin/env python3
"""
Merge benchmark CSV files and generate requested routing_steps plots.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import OrderedDict, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Callable

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


Row = dict[str, str]
Predicate = Callable[[Row], bool]


def normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def parse_float(value: str | None) -> float | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: str | None) -> int | None:
    parsed = parse_float(value)
    if parsed is None:
        return None
    return int(parsed)


def map_type(row: Row) -> str:
    value = normalize(row.get("mapping_type"))
    if value in {"magic-aware", "magicaware"}:
        return "magic_aware"
    if value in {"homogenous"}:
        return "homogeneous"
    return value


def placement_value(row: Row) -> str:
    return normalize(row.get("magic_state_placement_strategy"))


def placement_is_right(row: Row) -> bool:
    value = placement_value(row)
    return value in {"right", "right_row", "rightrow"} or "right" in value


def placement_is_center_circle(row: Row) -> bool:
    return placement_value(row) == "center_circle"


def build_predicate(
    *,
    mapping_type: str,
    safe_passage_strategy: str | None = None,
    gaussian_strategy: str | None = None,
    magic_aware_strategy: str | None = None,
    placement_check: Predicate | None = None,
    border_distance_percentage: int | None = None,
) -> Predicate:
    def _predicate(row: Row) -> bool:
        if map_type(row) != mapping_type:
            return False
        if safe_passage_strategy is not None and normalize(row.get("safe_passage_strategy")) != safe_passage_strategy:
            return False
        if gaussian_strategy is not None and normalize(row.get("gaussian_strategy")) != gaussian_strategy:
            return False
        if magic_aware_strategy is not None and normalize(row.get("magic_aware_strategy")) != magic_aware_strategy:
            return False
        if placement_check is not None and not placement_check(row):
            return False
        if border_distance_percentage is not None and parse_int(row.get("border_distance_percentage")) != border_distance_percentage:
            return False
        return True

    return _predicate


def circuit_graph_label(row: Row) -> str:
    explicit = (row.get("circuit_graph_label") or "").strip()
    if explicit:
        return explicit

    circuit = (row.get("circuit") or "").strip()
    dimensions = (row.get("graph_dimensions") or "").strip()
    if not dimensions:
        x = (row.get("graph_x") or "").strip()
        y = (row.get("graph_y") or "").strip()
        if x and y:
            dimensions = f"{x}x{y}"
    if circuit and dimensions:
        return f"{circuit}-{dimensions}"
    return circuit or dimensions or "unknown"


def graph_dims(row: Row) -> tuple[int | None, int | None]:
    x = parse_int(row.get("graph_x"))
    y = parse_int(row.get("graph_y"))
    if x is not None and y is not None:
        return x, y

    dims = normalize(row.get("graph_dimensions"))
    if "x" not in dims:
        return None, None
    left, right = dims.split("x", maxsplit=1)
    try:
        return int(left), int(right)
    except ValueError:
        return None, None


def sorted_x_labels(rows: list[Row]) -> list[str]:
    meta: dict[str, tuple[str, float, float, str]] = {}
    for row in rows:
        label = circuit_graph_label(row)
        if label in meta:
            continue
        circuit = (row.get("circuit") or "").strip()
        gx, gy = graph_dims(row)
        gx_s = float(gx) if gx is not None else math.inf
        gy_s = float(gy) if gy is not None else math.inf
        meta[label] = (circuit, gx_s, gy_s, label)
    return sorted(meta, key=lambda x: meta[x])


def merge_csvs(results_dir: Path, merged_csv: Path) -> tuple[list[Row], list[Path]]:
    input_files = sorted(path for path in results_dir.rglob("*.csv") if path.resolve() != merged_csv.resolve())
    if not input_files:
        raise FileNotFoundError(
            "Nessun CSV trovato in "
            f"{results_dir}. Usa --results-dir <path> oppure genera prima i benchmark CSV."
        )

    fields: OrderedDict[str, None] = OrderedDict()
    rows: list[Row] = []
    for csv_file in input_files:
        with csv_file.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                continue
            for field in reader.fieldnames:
                fields.setdefault(field, None)
            fields.setdefault("source_file", None)

            for row in reader:
                out = {field: row.get(field, "") for field in fields if field != "source_file"}
                out["source_file"] = str(csv_file.relative_to(results_dir))
                rows.append(out)

    merged_csv.parent.mkdir(parents=True, exist_ok=True)
    with merged_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields.keys()))
        writer.writeheader()
        writer.writerows(rows)

    return rows, input_files


def aggregate(values: list[float], strategy: str) -> float:
    if strategy == "median":
        return median(values)
    return mean(values)


def series_values(
    rows: list[Row],
    x_labels: list[str],
    specs: list[tuple[str, Predicate]],
    aggregate_strategy: str,
) -> tuple[dict[str, list[float]], list[str]]:
    labels_set = set(x_labels)
    bucket: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for row in rows:
        x = circuit_graph_label(row)
        if x not in labels_set:
            continue
        val = parse_float(row.get("routing_steps"))
        if val is None:
            continue
        for label, pred in specs:
            if pred(row):
                bucket[label][x].append(val)

    plotted: dict[str, list[float]] = {}
    missing: list[str] = []
    for label, _ in specs:
        points = []
        has_data = False
        for x in x_labels:
            values = bucket[label][x]
            if values:
                points.append(aggregate(values, aggregate_strategy))
                has_data = True
            else:
                points.append(math.nan)
        if has_data:
            plotted[label] = points
        else:
            missing.append(label)
    return plotted, missing


def distinct_colors(count: int) -> list[tuple[float, float, float, float]]:
    if plt is None or count <= 0:
        return []

    # Combine three qualitative palettes (20 + 20 + 20) before any fallback.
    palette_names = ("tab20", "tab20b", "tab20c")
    colors: list[tuple[float, float, float, float]] = []
    for name in palette_names:
        cmap = plt.get_cmap(name)
        cmap_colors = getattr(cmap, "colors", None)
        if cmap_colors is None:
            cmap_colors = [cmap(i / 19) for i in range(20)]
        for color in cmap_colors:
            if len(color) == 3:
                colors.append((color[0], color[1], color[2], 1.0))
            else:
                colors.append((color[0], color[1], color[2], color[3]))

    if count <= len(colors):
        return colors[:count]

    # Fallback for very high series counts.
    hsv = plt.get_cmap("hsv")
    extra = count - len(colors)
    for i in range(extra):
        c = hsv(i / max(1, extra))
        colors.append((c[0], c[1], c[2], c[3]))
    return colors[:count]


def homogeneous_specs(rows: list[Row]) -> list[tuple[str, Predicate]]:
    available_safe = {
        normalize(r.get("safe_passage_strategy"))
        for r in rows
        if map_type(r) == "homogeneous"
    }
    safe_values = [x for x in ("passage", "cube") if x in available_safe]
    if not safe_values:
        safe_values = [None]

    specs: list[tuple[str, Predicate]] = []
    placements = [("right", placement_is_right), ("center_circle", placement_is_center_circle)]
    for safe in safe_values:
        for place_name, place_check in placements:
            for pct in (0, 5):
                safe_part = f"{safe}-" if safe else ""
                label = f"homogeneous-{safe_part}{place_name}-pct{pct}"
                specs.append(
                    (
                        label,
                        build_predicate(
                            mapping_type="homogeneous",
                            safe_passage_strategy=safe,
                            placement_check=place_check,
                            border_distance_percentage=pct,
                        ),
                    )
                )
    return specs


def graph1_specs(rows: list[Row]) -> list[tuple[str, Predicate]]:
    specs: list[tuple[str, Predicate]] = []
    placements = [("right", placement_is_right), ("center_circle", placement_is_center_circle)]
    for gs in ("coarse", "fine"):
        for safe in ("passage", "cube"):
            for place_name, place_check in placements:
                for pct in (0, 5):
                    label = f"gaussian-{gs}-{safe}-{place_name}-pct{pct}"
                    specs.append(
                        (
                            label,
                            build_predicate(
                                mapping_type="gaussian",
                                gaussian_strategy=gs,
                                safe_passage_strategy=safe,
                                placement_check=place_check,
                                border_distance_percentage=pct,
                            ),
                        )
                    )
    specs.extend(homogeneous_specs(rows))
    return specs


def graph2_specs(rows: list[Row]) -> list[tuple[str, Predicate]]:
    specs: list[tuple[str, Predicate]] = []
    placements = [("right", placement_is_right), ("center_circle", placement_is_center_circle)]
    for mas in ("center", "distance", "random"):
        for safe in ("passage", "cube"):
            for place_name, place_check in placements:
                for pct in (0, 5):
                    label = f"magic-aware-{mas}-{safe}-{place_name}-pct{pct}"
                    specs.append(
                        (
                            label,
                            build_predicate(
                                mapping_type="magic_aware",
                                magic_aware_strategy=mas,
                                safe_passage_strategy=safe,
                                placement_check=place_check,
                                border_distance_percentage=pct,
                            ),
                        )
                    )
    specs.extend(homogeneous_specs(rows))
    return specs


def save_plot(
    *,
    x_labels: list[str],
    data: dict[str, list[float]],
    title: str,
    output: Path,
) -> None:
    if plt is None:
        raise ModuleNotFoundError("matplotlib non trovato. Installa matplotlib per generare i grafici.")
    if not x_labels:
        raise ValueError("Nessuna etichetta sull'asse X.")

    output.parent.mkdir(parents=True, exist_ok=True)
    width = max(14, len(x_labels) * 0.85)
    fig, ax = plt.subplots(figsize=(width, 8))
    x = list(range(len(x_labels)))

    line_styles = ["-", "--", "-.", ":"]
    markers = ["o", "s", "^", "D", "v", "P", "X", "*", "<", ">", "h", "8"]
    colors = distinct_colors(len(data))

    for idx, (label, values) in enumerate(data.items()):
        ax.plot(
            x,
            values,
            label=label,
            color=colors[idx],
            linestyle=line_styles[(idx // len(markers)) % len(line_styles)],
            marker=markers[idx % len(markers)],
            linewidth=1.4,
        )

    ax.set_title(title)
    ax.set_xlabel("circuit x graph_dimensions")
    ax.set_ylabel("routing_steps")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=55, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    if data:
        ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=False)
    else:
        ax.text(
            0.5,
            0.5,
            "Nessuna serie con routing_steps disponibile",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            color="gray",
        )

    fig.tight_layout()
    fig.savefig(output, dpi=170)
    plt.close(fig)


def resolve_project_path(path: Path, project_root: Path) -> Path:
    if path.is_absolute():
        return path
    return (project_root / path).resolve()


def _csv_inputs_in_dir(directory: Path, merged_csv: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted(path for path in directory.rglob("*.csv") if path.resolve() != merged_csv.resolve())


def auto_resolve_results_dir(requested: Path, project_root: Path, merged_csv: Path) -> Path:
    candidates = [
        requested,
        project_root / "benchmarks" / "results",
        project_root / "results",
        (Path.cwd() / "benchmarks" / "results").resolve(),
        (Path.cwd() / "results").resolve(),
    ]

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if _csv_inputs_in_dir(candidate, merged_csv):
            return candidate
    return requested


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unisce i CSV benchmark e genera grafici di routing_steps.")
    parser.add_argument("--results-dir", type=Path, default=Path("benchmarks/results"))
    parser.add_argument("--merged-csv", type=Path, default=Path("benchmarks/results/merged_runs.csv"))
    parser.add_argument("--plots-dir", type=Path, default=Path("benchmarks/results/plots"))
    parser.add_argument("--aggregate", choices=("mean", "median"), default="mean")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    merged_csv = resolve_project_path(args.merged_csv, project_root)
    plots_dir = resolve_project_path(args.plots_dir, project_root)
    requested_results_dir = resolve_project_path(args.results_dir, project_root)
    results_dir = auto_resolve_results_dir(requested_results_dir, project_root, merged_csv)

    rows, files = merge_csvs(results_dir=results_dir, merged_csv=merged_csv)
    x_labels = sorted_x_labels(rows)

    g1_specs = graph1_specs(rows)
    g2_specs = graph2_specs(rows)
    g1_data, g1_missing = series_values(rows, x_labels, g1_specs, args.aggregate)
    g2_data, g2_missing = series_values(rows, x_labels, g2_specs, args.aggregate)

    g1_out = plots_dir / "routing_steps_gaussian_vs_homogeneous.png"
    g2_out = plots_dir / "routing_steps_magic_aware_vs_homogeneous.png"

    save_plot(
        x_labels=x_labels,
        data=g1_data,
        title=(
            "Routing Steps: Gaussian (coarse/fine, passage/cube) vs Homogeneous\n"
            "placement right/center_circle, percentage 0/5"
        ),
        output=g1_out,
    )
    save_plot(
        x_labels=x_labels,
        data=g2_data,
        title=(
            "Routing Steps: Magic-Aware (center/distance/random, passage/cube) vs Homogeneous\n"
            "placement right/center_circle, percentage 0/5"
        ),
        output=g2_out,
    )

    print(f"CSV input trovati: {len(files)}")
    if results_dir != requested_results_dir:
        print(f"Results dir richiesto: {requested_results_dir}")
        print(f"Results dir usato (auto-detected): {results_dir}")
    print(f"Righe totali unite: {len(rows)}")
    print(f"CSV unificato: {merged_csv}")
    print(f"Grafico 1: {g1_out}")
    print(f"Grafico 2: {g2_out}")
    print(f"Serie senza dati (grafico 1): {len(g1_missing)} / {len(g1_specs)}")
    print(f"Serie senza dati (grafico 2): {len(g2_missing)} / {len(g2_specs)}")


if __name__ == "__main__":
    main()
