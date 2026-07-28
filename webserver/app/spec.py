"""Declarative description of the compiler's single-run configuration.

The compiler reads one JSON object per run (``--config <file>``); every key it
accepts is enumerated here together with its type, bounds and default. The
frontend builds its whole form from :func:`form_spec`, so adding a knob to the
compiler means adding one entry below and nothing else.

Defaults mirror the hardcoded defaults in ``src/main.cpp``
(``run_one_execution_from_args``), i.e. the tuned optimum of the
``connectivity`` column of ``results/pesi_finali.md`` — not the checked-in
``config/0_compiler_config.json``, which is a scratch file. Because we always
pass an explicit ``--config``, that scratch file is never consulted.
"""

from __future__ import annotations

from typing import Any


# --- enumerations -----------------------------------------------------------
#
# Values are the canonical spellings validated by src/parsing.cpp. The parser
# also accepts a pile of aliases (case-insensitive, '-' folded to '_'); we only
# ever emit canonical ones so a round-trip of the form is stable.

MAPPING_TYPES = ["gaussian", "magic_aware", "random"]
GAUSSIAN_STRATEGIES = ["fine", "coarse"]
MAGIC_AWARE_STRATEGIES = ["distance", "center", "random"]
SAFE_PASSAGE_STRATEGIES = ["connectivity", "cube", "passage", "passage_no_subgraphs"]
MAGIC_PLACEMENT_STRATEGIES = ["center_circle", "right_row"]
T_ROUTING_MODES = ["smart_t_routing", "normal_t_routing"]
ROUTING_STRATEGIES = [
    "naive_critical",
    "naive",
    "congestion",
    "packing",
    "critical_packing",
    "greedy_lookahead",
    "dascot_sa",
    # Only linked when the binary is built with FTOQC_HAS_BOOST_ROUTER; the
    # compiler rejects it otherwise and the error surfaces in the UI.
    "boost",
]


# --- field table ------------------------------------------------------------
#
# Each entry: (json_key, kind, default, extras). `kind` drives both the widget
# the frontend renders and the coercion applied server-side in `build_config`.

_FIELDS: list[dict[str, Any]] = [
    # -- architecture --------------------------------------------------------
    {
        "key": "x",
        "group": "architecture",
        "label": "Grid width",
        "kind": "int",
        "default": -1,
        "min": -1,
        "max": 200,
        "help": "-1 auto-sizes from qubit count and interaction degree, "
        "0 uses the upper-bound heuristic, >0 is an explicit width.",
    },
    {
        "key": "y",
        "group": "architecture",
        "label": "Grid height",
        "kind": "int",
        "default": -1,
        "min": -1,
        "max": 200,
        "help": "Same sentinels as the width. Grid size is the dominant lever "
        "on unrouted layers — raise it when layers fail to route.",
    },
    {
        "key": "dimension_offset",
        "group": "architecture",
        "label": "Dimension offset",
        "kind": "int",
        "default": 0,
        "min": -20,
        "max": 20,
        "help": "Signed delta applied to the auto-computed grid side. Only "
        "consulted when the width is negative.",
    },
    {
        "key": "MagicStatePlacementStrategy",
        "group": "architecture",
        "label": "Magic state placement",
        "kind": "enum",
        "default": "center_circle",
        "choices": MAGIC_PLACEMENT_STRATEGIES,
    },
    {
        "key": "number_of_magic_states",
        "group": "architecture",
        "label": "Magic states",
        "kind": "float",
        "default": -1,
        "min": -1,
        "max": 512,
        "step": 0.05,
        "help": "-1 scales with the circuit's peak per-layer T demand. A value "
        "between 0 and 1 is read as a multiplier of the qubit count; anything "
        "larger is an absolute count.",
    },
    {
        "key": "border_distance_percentage",
        "group": "architecture",
        "label": "Border distance %",
        "kind": "float",
        "default": 15.0,
        "min": 0.0,
        "max": 100.0,
        "step": 0.5,
        "help": "How far magic states are inset from the lattice border.",
    },
    # -- mapping -------------------------------------------------------------
    {
        "key": "type",
        "group": "mapping",
        "label": "Mapping type",
        "kind": "enum",
        "default": "gaussian",
        "choices": MAPPING_TYPES,
        "help": "gaussian is the contribution of this compiler; random is the "
        "baseline it is measured against.",
    },
    {
        "key": "gaussian_strategy",
        "group": "mapping",
        "label": "Gaussian strategy",
        "kind": "enum",
        "default": "fine",
        "choices": GAUSSIAN_STRATEGIES,
        "help": "Only consulted for the gaussian mapping type.",
    },
    {
        "key": "magic_aware_strategy",
        "group": "mapping",
        "label": "Magic-aware strategy",
        "kind": "enum",
        "default": "distance",
        "choices": MAGIC_AWARE_STRATEGIES,
        "help": "Only consulted for the magic_aware mapping type.",
    },
    {
        "key": "safe_passage_strategy",
        "group": "mapping",
        "label": "Safe passage strategy",
        "kind": "enum",
        "default": "connectivity",
        "choices": SAFE_PASSAGE_STRATEGIES,
        "help": "Decides which free neighbours a placement must keep so later "
        "routes can still reach the qubit.",
    },
    {
        "key": "bfs_density_threshold",
        "group": "mapping",
        "label": "BFS density threshold",
        "kind": "float",
        "default": 0.70,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "help": "CNOT-graph density below which qubits are mapped in "
        "CNOT-BFS order rather than priority-heap order.",
    },
    # -- gaussian weights ----------------------------------------------------
    {
        "key": "GAUSSIAN_SIGMA",
        "group": "weights",
        "label": "Sigma",
        "kind": "float",
        "default": 0.7,
        "min": 0.01,
        "max": 20.0,
        "step": 0.05,
        "help": "Absolute standard deviation, identical on both axes and "
        "independent of the grid. Must be positive.",
    },
    {
        "key": "MAPPED_GAUSSIAN_WEIGHT",
        "group": "weights",
        "label": "Mapped weight",
        "kind": "float",
        "default": 20.0,
        "min": -1.0,
        "max": 50.0,
        "step": 0.5,
        "help": "Attraction toward already-mapped partners. Rides a ridge with "
        "the CNOT weight at roughly mapped / 2.5 — retune the pair, never one "
        "of them alone.",
    },
    {
        "key": "CNOT_HIGH",
        "group": "weights",
        "label": "CNOT high",
        "kind": "float",
        "default": 8.0,
        "min": -1.0,
        "max": 50.0,
        "step": 0.5,
    },
    {
        "key": "CNOT_LOW",
        "group": "weights",
        "label": "CNOT low",
        "kind": "float",
        "default": 0.0,
        "min": -1.0,
        "max": 50.0,
        "step": 0.5,
    },
    {
        "key": "MAGIC_HIGH",
        "group": "weights",
        "label": "Magic high",
        "kind": "float",
        "default": 0.0,
        "min": 0.0,
        "max": 50.0,
        "step": 0.1,
        "help": "Inert in the connectivity regime — the sweeps closed it at 0 "
        "everywhere.",
    },
    {
        "key": "MAGIC_LOW",
        "group": "weights",
        "label": "Magic low",
        "kind": "float",
        "default": 0.0,
        "min": 0.0,
        "max": 50.0,
        "step": 0.1,
    },
    {
        "key": "BASE_GAUSSIAN_WEIGHT",
        "group": "weights",
        "label": "Base weight",
        "kind": "float",
        "default": 1.0,
        "min": 0.0,
        "max": 50.0,
        "step": 0.1,
    },
    {
        "key": "EXTERNAL_WEIGHT",
        "group": "weights",
        "label": "External weight",
        "kind": "float",
        "default": -15.0,
        "min": -50.0,
        "max": 50.0,
        "step": 0.5,
        "help": "Saturates: any negative value is near-optimal, 0 costs about "
        "1.5 percentage points.",
    },
    {
        "key": "CNOT_FORMULA_SCALE",
        "group": "weights",
        "label": "CNOT formula scale",
        "kind": "float",
        "default": 1.0,
        "min": 0.0,
        "max": 20.0,
        "step": 0.1,
        "help": "Applied to auto-computed weights only; ignored once the "
        "corresponding weight is pinned to a fixed value.",
    },
    {
        "key": "MAPPED_FORMULA_SCALE",
        "group": "weights",
        "label": "Mapped formula scale",
        "kind": "float",
        "default": 1.0,
        "min": 0.0,
        "max": 20.0,
        "step": 0.1,
    },
    # -- routing -------------------------------------------------------------
    {
        "key": "routing_strategy",
        "group": "routing",
        "label": "Routing strategy",
        "kind": "enum",
        "default": "naive_critical",
        "choices": ROUTING_STRATEGIES,
        "help": "boost is only available when the binary was built with the "
        "Boost router enabled.",
    },
    {
        "key": "t-routing-mode",
        "group": "routing",
        "label": "T routing mode",
        "kind": "enum",
        "default": "smart_t_routing",
        "choices": T_ROUTING_MODES,
    },
    {
        "key": "patience_threshold",
        "group": "routing",
        "label": "Patience threshold",
        "kind": "int",
        "default": 3,
        "min": 0,
        "max": 100,
    },
    {
        "key": "use_layer_cache",
        "group": "routing",
        "label": "Use layer cache",
        "kind": "bool",
        "default": True,
    },
    {
        "key": "packing_commute",
        "group": "routing",
        "label": "Packing commutation",
        "kind": "bool",
        "default": False,
        "help": "Commutation-aware frontier. Only the packing and "
        "critical_packing routers read it.",
    },
    {
        "key": "layering_commute",
        "group": "routing",
        "label": "Layering commutation",
        "kind": "bool",
        "default": False,
        "help": "Commutation-aware layering; yields shallower layers for every "
        "router.",
    },
    {
        "key": "repetition",
        "group": "routing",
        "label": "Repetitions",
        "kind": "int",
        "default": 1,
        "min": 1,
        "max": 64,
        "help": "Runs the mapping this many times and keeps the best result. "
        "Only the random mapping type varies between repetitions.",
    },
]

GROUPS = [
    {
        "id": "architecture",
        "label": "Architecture",
        "blurb": "Lattice size and where the magic states sit.",
    },
    {
        "id": "mapping",
        "label": "Mapping",
        "blurb": "How logical qubits are assigned to lattice nodes.",
    },
    {
        "id": "routing",
        "label": "Routing",
        "blurb": "How lattice surgery paths are scheduled into steps.",
    },
    {
        "id": "weights",
        "label": "Gaussian weights",
        "blurb": "Field strengths of the placement heuristic. The defaults are "
        "a tuned optimum — change them one axis at a time.",
    },
]

FIELDS_BY_KEY = {field["key"]: field for field in _FIELDS}

DEFAULTS = {field["key"]: field["default"] for field in _FIELDS}


def form_spec() -> dict[str, Any]:
    """The payload the frontend turns into a form."""
    return {"groups": GROUPS, "fields": _FIELDS, "defaults": DEFAULTS}


class ConfigError(ValueError):
    """A submitted configuration value the compiler would reject."""


def _coerce(field: dict[str, Any], raw: Any) -> Any:
    key, kind = field["key"], field["kind"]

    if kind == "bool":
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, str):
            return raw.strip().lower() not in {"", "0", "false", "no", "off"}
        return bool(raw)

    if kind == "enum":
        value = str(raw).strip()
        if value not in field["choices"]:
            raise ConfigError(
                f"{key}: {value!r} is not one of {', '.join(field['choices'])}"
            )
        return value

    # Numeric. Reject NaN/inf up front: the compiler's own validation does the
    # same but only after spending time parsing the circuit.
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ConfigError(f"{key}: {raw!r} is not a number") from None
    if value != value or value in (float("inf"), float("-inf")):
        raise ConfigError(f"{key}: must be finite")

    if kind == "int":
        if value != int(value):
            raise ConfigError(f"{key}: must be a whole number")
        value = int(value)

    low, high = field.get("min"), field.get("max")
    if low is not None and value < low:
        raise ConfigError(f"{key}: must be at least {low}")
    if high is not None and value > high:
        raise ConfigError(f"{key}: must be at most {high}")
    return value


def build_config(submitted: dict[str, Any]) -> dict[str, Any]:
    """Validate a submitted form and return the compiler's config object.

    Every known key is emitted whether or not the client sent it, so the run is
    fully determined by this object and never falls through to the compiler's
    own defaults.
    """
    unknown = set(submitted) - set(FIELDS_BY_KEY)
    if unknown:
        raise ConfigError(f"unknown setting(s): {', '.join(sorted(unknown))}")

    config: dict[str, Any] = {}
    for key, field in FIELDS_BY_KEY.items():
        config[key] = (
            _coerce(field, submitted[key]) if key in submitted else field["default"]
        )

    # number_of_magic_states carries three meanings in one slot. Only -1 and
    # fractions in (0, 1) are non-integral; everything else is a count, and
    # sending 4.0 where the parser wants an int trips its type check.
    magic = config["number_of_magic_states"]
    if magic == -1 or (0.0 < magic < 1.0):
        config["number_of_magic_states"] = magic
    else:
        if magic != int(magic):
            raise ConfigError(
                "number_of_magic_states: must be -1, a fraction between 0 and "
                "1, or a whole count"
            )
        config["number_of_magic_states"] = int(magic)

    return config
