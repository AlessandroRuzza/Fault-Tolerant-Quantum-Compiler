#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
RESULTS_DIR="$PROJECT_ROOT/benchmarks/results"
PLOT_SCRIPT="$SCRIPT_DIR/generate_benchmark_plots.py"

if [ -x "$PROJECT_ROOT/env/bin/python3" ]; then
  PYTHON=${PYTHON:-"$PROJECT_ROOT/env/bin/python3"}
else
  PYTHON=${PYTHON:-python3}
fi

found_csv=0
for csv in "$RESULTS_DIR"/*.csv; do
  [ -f "$csv" ] || continue
  found_csv=1

  header=$(sed -n '1p' "$csv")
  case ",$header," in
    *,status,*) ;;
    *)
      printf 'Skipping incompatible CSV without status column: %s\n' "$csv" >&2
      continue
      ;;
  esac
  case ",$header," in
    *,run_id,*|*,id,*) ;;
    *)
      printf 'Skipping incompatible CSV without run_id/id column: %s\n' "$csv" >&2
      continue
      ;;
  esac

  "$PYTHON" "$PLOT_SCRIPT" --csv "$csv"
done

if [ "$found_csv" -eq 0 ]; then
  printf 'No CSV files found in %s\n' "$RESULTS_DIR" >&2
  exit 1
fi

"$PYTHON" "$PLOT_SCRIPT" --distinct
