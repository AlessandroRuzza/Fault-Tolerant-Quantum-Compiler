#!/usr/bin/env python3
"""make_wisq_report.py — unified generator for the WISQ-comparison `.md` reports.

One code path builds every section that until now was hand-written per report
(cube_wisq_results.md, connectivity_minus3_wisq_results.md, ...), so all reports
share identical definitions of win/loss, wall-clock budgets, compile-time
speedup and the ε speed-buffer win-rate.

Input: a side-by-side CSV from compare_wisq_2.py / compare_wisq_conn.py with the
columns circuit, n_qubits, my_routing_steps, my_duration_s, wisq_routing_steps,
wisq_duration_s, wisq_status, my_x/my_y, wisq_x/wisq_y (footprint/trade-off need
the grid columns; dim_diff_side enables the "−k" footprint section).

Sections emitted (in this order):
  1. Header (title + config blurb + data provenance)
  2. Tabella riassuntiva delle performance
  3. Footprint + Trade-off  (only when dim_diff_side / grid columns are present)
  4. Routing steps in aggregato (nostro vs WISQ)
  5. Tabella riassuntiva per ogni budget wall-clock
  6. Andamento del win-rate al variare del budget wall-clock
  7. Tempo di compilazione (wall-clock)
  8. Buffer di steps dipendente dalla velocità (ε speed-buffer win-rate)
  9. Per famiglia di circuiti
 10. Per circuito (dettaglio)

Usage:
  python make_wisq_report.py \
      --csv data/results/connectivity_vs_wisq_minus3.csv \
      --out results/connectivity_minus3_wisq_results.md \
      --title "Risultati WISQ-native MENO 3 — connectivity" \
      --intro "connectivity con i pesi finali ..." \
      --exclude knn_n25 test \
      --shrink-baseline data/results/connectivity_vs_wisq.csv \
      --wisq-timeout 12000 \
      --budgets 3600 1800 900 600 300 60
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import statistics as st
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # scripts/wisq_compare/ -> repo root


# ── circuit density (CNOT interaction density, computed from the universal QASM) ──

_CX_RE = re.compile(r"\bcx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\]")
_density_cache: dict[str, float | None] = {}


def cnot_density(circuit: str) -> float | None:
    """cnot_interaction_density = |distinct CNOT qubit-pairs| / (Q·(Q−1)/2),
    Q = distinct qubits touched by a CNOT. Same definition as circuit_metrics.hpp;
    read from universal_set_qasms/<c>_universal.qasm (fallback qasms/<c>.qasm).
    Verified to reproduce the compiler's values (qft_n10=1.0, qft_n50=0.6449, ...)."""
    if circuit in _density_cache:
        return _density_cache[circuit]
    path = None
    for cand in (REPO_ROOT / "universal_set_qasms" / f"{circuit}_universal.qasm",
                 REPO_ROOT / "qasms" / f"{circuit}.qasm"):
        if cand.exists():
            path = cand
            break
    d: float | None = None
    if path is not None:
        pairs, qubits = set(), set()
        for m in _CX_RE.finditer(path.read_text()):
            a, b = int(m.group(1)), int(m.group(2))
            pairs.add((min(a, b), max(a, b)))
            qubits.add(a)
            qubits.add(b)
        if len(qubits) >= 2:
            d = len(pairs) / (len(qubits) * (len(qubits) - 1) / 2.0)
    _density_cache[circuit] = d
    return d


# ── row parsing ───────────────────────────────────────────────────────────────

def _int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def _float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


class Row:
    """One circuit's paired result, with the derived fields every section needs."""
    def __init__(self, d: dict):
        self.circuit = d.get("circuit", "").strip()
        self.n = _int(d.get("n_qubits"))
        self.my_steps = _int(d.get("my_routing_steps"))
        self.wisq_steps = _int(d.get("wisq_routing_steps"))
        self.my_dur = _float(d.get("my_duration_s"))
        self.wisq_dur = _float(d.get("wisq_duration_s"))
        self.wisq_status = d.get("wisq_status", "").strip().lower()
        self.my_x, self.my_y = _int(d.get("my_x")), _int(d.get("my_y"))
        self.wisq_x, self.wisq_y = _int(d.get("wisq_x")), _int(d.get("wisq_y"))
        self.dim_diff = _int(d.get("dim_diff_side"))
        self.fallback = str(d.get("safe_passage_fallback", "")).strip().lower()

    # Our side produced a routing → we mapped. Empty steps == mapping/routing fail.
    @property
    def mapped(self) -> bool:
        return self.my_steps is not None

    # WISQ produced a routing (success with a step count). Missing == timeout/fail.
    @property
    def wisq_done(self) -> bool:
        return self.wisq_steps is not None

    @property
    def both(self) -> bool:
        return self.mapped and self.wisq_done

    # Step verdict where both complete: WIN = we use fewer routing steps.
    @property
    def verdict(self):
        if not self.both:
            return None
        if self.my_steps < self.wisq_steps:
            return "WIN"
        if self.my_steps > self.wisq_steps:
            return "LOSS"
        return "TIE"

    @property
    def we_faster(self):
        if self.my_dur is None or self.wisq_dur is None:
            return None
        return self.my_dur < self.wisq_dur


def family(circuit: str) -> str:
    """Heuristic circuit-family grouping (size token stripped). Good for the big
    families (qft/qaoa/synth/ising/vqe_*/graphstate/wstate/ghz); a few tiny
    singletons may differ from the hand-made tables — the per-circuit table is
    the exact record."""
    m = re.match(r"^(\d+qubits)", circuit)
    if m:
        return m.group(1)
    if circuit.startswith("synth"):
        return "synth"
    c = circuit.replace("_transpiled", "")
    c = re.sub(r"_n\d+$", "", c)
    c = re.sub(r"_\d+$", "", c)
    return c


# ── generic helpers ───────────────────────────────────────────────────────────

def pct(a, b) -> str:
    return f"{100.0 * a / b:.1f}%" if b else "—"


def median(xs):
    return st.median(xs) if xs else 0.0


def load_rows(path: Path, exclude: set[str]) -> list[Row]:
    rows = []
    with path.open(newline="") as f:
        for d in csv.DictReader(f):
            r = Row(d)
            if r.circuit and r.circuit not in exclude:
                rows.append(r)
    return rows


# ── section 2: performance summary ────────────────────────────────────────────

def sec_performance(rows: list[Row]) -> tuple[str, dict]:
    total = len(rows)
    mapfail = [r for r in rows if not r.mapped]
    mapped = [r for r in rows if r.mapped]
    wisq_to = [r for r in mapped if not r.wisq_done]      # we complete, WISQ timeout
    both = [r for r in mapped if r.both]
    wins = [r for r in both if r.verdict == "WIN"]
    ties = [r for r in both if r.verdict == "TIE"]
    losses = [r for r in both if r.verdict == "LOSS"]

    def faster(sub):
        return sum(1 for r in sub if r.we_faster)

    win_ratios = [r.wisq_steps / r.my_steps for r in wins if r.my_steps]
    loss_ratios = [r.wisq_steps / r.my_steps for r in losses if r.my_steps]
    tie_faster = faster(ties)
    victories = len(wisq_to) + len(wins) + tie_faster

    L = []
    L.append("## Tabella riassuntiva delle performance\n")
    L.append("| Categoria | Circuiti | Di cui noi +veloci |")
    L.append("|-----------|----------|--------------------|")
    L.append(f"| **Totale circuiti analizzati** | {total} | — |")
    if mapfail:
        L.append(f"| **Nostro mapping FALLISCE** | {len(mapfail)} | — |")
        L.append(f"| **Mappiamo con successo** | {len(mapped)} | — |")
    L.append(f"| ↳ WISQ va in timeout (noi vinciamo) | {len(wisq_to)} | — |")
    L.append(f"| ↳ Entrambi completano | {len(both)} | — |")
    L.append(f"|   ↳ Noi vinciamo su steps | {len(wins)} (ratio mediana {median(win_ratios):.2f}×) | {faster(wins)} ({pct(faster(wins), len(wins))}) |")
    L.append(f"|   ↳ Pareggio su steps | {len(ties)} | {tie_faster} ({pct(tie_faster, len(ties))}) |")
    L.append(f"|   ↳ WISQ vince su steps | {len(losses)} (ratio mediana {median(loss_ratios):.2f}×) | {faster(losses)} ({pct(faster(losses), len(losses))}) |")
    L.append("| | | |")
    L.append(f"| **TOTALE VITTORIE NOSTRE** | **{victories} / {total} ({pct(victories, total)})** | — |")
    L.append(f"| ↳ Noi completiamo, WISQ va in timeout | {len(wisq_to)} / {total} ({pct(len(wisq_to), total)}) | — |")
    L.append(f"| ↳ Noi vinciamo su steps (WISQ completa) | {len(wins)} / {total} ({pct(len(wins), total)}) | — |")
    L.append(f"| ↳ Pareggio su steps, noi più veloci | {tie_faster} / {total} ({pct(tie_faster, total)}) | — |")
    if mapfail:
        L.append("| | | |")
        L.append(f"| **SCONFITTE (mapping fallito)** | **{len(mapfail)} / {total} ({pct(len(mapfail), total)})** | — |")
        names = ", ".join(f"`{r.circuit}`" for r in mapfail)
        L.append(f"\nCircuiti dove non mappiamo: {names}.")
    return "\n".join(L), {"victories": victories, "total": total}


# ── section 3: footprint + trade-off (needs grid / dim_diff columns) ───────────

def sec_footprint(rows: list[Row], shrink_baseline: Path | None) -> str:
    mapped = [r for r in rows if r.mapped and r.my_x and r.wisq_x]
    if not mapped or all(r.dim_diff is None for r in mapped):
        return ""

    L = []
    # Footprint distribution.
    from collections import Counter
    dist = Counter(r.dim_diff for r in mapped if r.dim_diff is not None)
    L.append("## Footprint: quanto scendiamo sotto WISQ\n")
    L.append("| Δ lati vs WISQ (`dim_diff_side`) | Circuiti |")
    L.append("|---|---|")
    for k in sorted(dist, reverse=True):
        L.append(f"| {k:+d} | {dist[k]} |")
    my_area = sum(r.my_x * r.my_y for r in mapped)
    w_area = sum(r.wisq_x * r.wisq_y for r in mapped)
    area_ratios = [(r.my_x * r.my_y) / (r.wisq_x * r.wisq_y) for r in mapped]
    med_sav = 100.0 * (1 - median(area_ratios))
    agg_sav = 100.0 * (1 - my_area / w_area)
    L.append(f"\n**Risparmio di qubit fisici** vs WISQ sui {len(mapped)} successi: "
             f"mediano **{med_sav:.1f}%**, aggregato **{agg_sav:.1f}%** "
             f"(area `my_x·my_y` vs `wisq_x·wisq_y`).\n")

    # Trade-off A: steps lost vs qubits saved, against WISQ.
    both = [r for r in rows if r.both]
    my_steps_sum = sum(r.my_steps for r in both)
    w_steps_sum = sum(r.wisq_steps for r in both)
    L.append("---\n")
    L.append("## Trade-off: routing steps persi vs qubit fisici risparmiati\n")
    L.append(f"Step su {len(both)} circuiti dove entrambi completano; "
             f"qubit fisici su tutti i {len(mapped)} che mappiamo.\n")
    L.append("**A) Contro WISQ** (noi shrink vs WISQ nativa):\n")
    L.append("| | noi | WISQ nativa | differenza |")
    L.append("|---|--------|-------------|------------|")
    L.append(f"| Routing steps (aggregato) | {my_steps_sum:,} | {w_steps_sum:,} | "
             f"**{100.0*(my_steps_sum/w_steps_sum-1):+.1f}%** |".replace(",", "."))
    L.append(f"| Qubit fisici (aggregato) | {my_area:,} | {w_area:,} | "
             f"**{-agg_sav:+.1f}%** ({w_area-my_area:,} in meno) |".replace(",", "."))
    wtl = [r.verdict for r in both]
    L.append(f"\nStep per-circuito: WIN {wtl.count('WIN')} / TIE {wtl.count('TIE')} / "
             f"LOSS {wtl.count('LOSS')}, mediana "
             f"{100.0*(median([r.my_steps/r.wisq_steps for r in both])-1):+.0f}%.\n")

    # Trade-off B: pure shrink cost (us native vs us shrunk, same config).
    if shrink_baseline and shrink_baseline.exists():
        base = {r.circuit: r.my_steps for r in load_rows(shrink_baseline, set())
                if r.my_steps is not None}
        pairs = [(base[r.circuit], r.my_steps) for r in mapped if r.circuit in base]
        if pairs:
            nat = sum(a for a, _ in pairs)
            shr = sum(b for _, b in pairs)
            identical = sum(1 for a, b in pairs if a == b)
            med = median([b / a for a, b in pairs if a])
            L.append(f"**B) Costo puro dello shrink** (noi nativa vs noi shrink, stessa "
                     f"config — `{shrink_baseline.name}`, {len(pairs)} circuiti):\n")
            L.append("| | noi nativa | noi shrink | differenza |")
            L.append("|---|-----------|------------|------------|")
            L.append(f"| Routing steps (aggregato) | {nat:,} | {shr:,} | "
                     f"**{100.0*(shr/nat-1):+.1f}%** |".replace(",", "."))
            L.append(f"\nMediana **{100.0*(med-1):+.0f}%**, "
                     f"**{identical}/{len(pairs)} circuiti identici**.")
    return "\n".join(L)


# ── section 4: aggregate routing steps ────────────────────────────────────────

def sec_aggregate(rows: list[Row]) -> str:
    both = [r for r in rows if r.both]
    my = sum(r.my_steps for r in both)
    wq = sum(r.wisq_steps for r in both)
    ratios = [r.wisq_steps / r.my_steps for r in both if r.my_steps]
    ratio = wq / my if my else 0
    sign = "in meno" if ratio < 1 else "in più"
    L = ["## Routing steps in aggregato (nostro vs WISQ)\n",
         f"Sui {len(both)} circuiti dove **entrambi completano**:\n",
         "| Metrica | Valore |", "|---------|--------|",
         f"| Somma `my_routing_steps` | {my:,} |".replace(",", "."),
         f"| Somma `wisq_routing_steps` | {wq:,} |".replace(",", "."),
         f"| **Rapporto dei totali (wisq / nostro)** | **{ratio:.2f} → WISQ usa "
         f"{abs(100*(ratio-1)):.1f}% di steps {sign}** |",
         f"| Mediana di `ratio_wisq_over_mine` | {median(ratios):.2f} |",
         f"| Media di `ratio_wisq_over_mine` | {st.mean(ratios) if ratios else 0:.3f} |"]
    return "\n".join(L)


# ── section 4b: win/loss vs circuit density ───────────────────────────────────

def sec_density(rows: list[Row]) -> str:
    both = [r for r in rows if r.both]
    for r in both:
        r.density = cnot_density(r.circuit)
    covered = [r for r in both if r.density is not None]
    if not covered:
        return ""

    def stats(sub):
        ds = [r.density for r in sub if r.density is not None]
        if not ds:
            return "0 | — | — | — | —"
        return (f"{len(ds)} | {st.mean(ds):.3f} | {median(ds):.3f} | "
                f"{min(ds):.3f} | {max(ds):.3f}")

    wins = [r for r in covered if r.verdict == "WIN"]
    ties = [r for r in covered if r.verdict == "TIE"]
    losses = [r for r in covered if r.verdict == "LOSS"]

    L = ["## Densità dei circuiti: dove vinciamo vs dove perdiamo\n",
         "`cnot_interaction_density` = coppie-qubit CNOT distinte / coppie possibili "
         "`Q·(Q−1)/2` (0 = sparso/locale, 1 = ogni coppia interagisce). "
         f"Calcolata dal QASM universale su {len(covered)}/{len(both)} circuiti "
         "both-complete con QASM disponibile.\n",
         "**Per esito sugli steps:**\n",
         "| Esito (steps) | N | densità media | mediana | min | max |",
         "|---|---|---|---|---|---|",
         f"| **Vinciamo** (WIN) | {stats(wins)} |",
         f"| Pareggio (TIE) | {stats(ties)} |",
         f"| **Perdiamo** (LOSS) | {stats(losses)} |"]

    # Bucketed win/loss by density band (echoes the cid<0.15 → never-lose finding).
    bands = [("< 0.15", lambda d: d < 0.15),
             ("0.15 – 0.40", lambda d: 0.15 <= d < 0.40),
             ("≥ 0.40", lambda d: d >= 0.40)]
    L += ["\n**Win/Loss per fascia di densità** (sugli steps, both-complete):\n",
          "| Densità `cid` | N | Win | Tie | Loss | Loss-rate (decisi) |",
          "|---|---|---|---|---|---|"]
    for label, pred in bands:
        sub = [r for r in covered if pred(r.density)]
        w = sum(1 for r in sub if r.verdict == "WIN")
        t = sum(1 for r in sub if r.verdict == "TIE")
        ls = sum(1 for r in sub if r.verdict == "LOSS")
        decided = w + ls
        lr = pct(ls, decided) if decided else "—"
        L.append(f"| {label} | {len(sub)} | {w} | {t} | {ls} | {lr} |")
    return "\n".join(L)


# ── section 5+6: wall-clock budgets ───────────────────────────────────────────

def budget_stats(rows: list[Row], budget: float) -> dict:
    """Symmetric timeout at `budget` seconds: only who finishes within it counts.
    WISQ timeouts carry their recorded (large) duration, so they never 'finish'."""
    mapped = [r for r in rows if r.mapped]
    def my_ok(r):
        return r.my_dur is not None and r.my_dur <= budget
    def wq_ok(r):
        return r.wisq_done and r.wisq_dur is not None and r.wisq_dur <= budget

    wisq_not = [r for r in mapped if not wq_ok(r)]
    no_winner = [r for r in wisq_not if not my_ok(r)]
    we_win_to = [r for r in wisq_not if my_ok(r)]           # WISQ misses, we finish
    our_loss = [r for r in mapped if wq_ok(r) and not my_ok(r)]
    both = [r for r in mapped if my_ok(r) and wq_ok(r)]
    wins = [r for r in both if r.verdict == "WIN"]
    ties = [r for r in both if r.verdict == "TIE"]
    losses = [r for r in both if r.verdict == "LOSS"]
    tie_faster = sum(1 for r in ties if r.we_faster)
    victories = len(we_win_to) + len(wins) + tie_faster
    return dict(mapped=len(mapped), wisq_not=len(wisq_not), no_winner=len(no_winner),
                we_win_to=len(we_win_to), our_loss=len(our_loss), both=len(both),
                wins=wins, ties=ties, losses=losses, tie_faster=tie_faster,
                victories=victories)


def fmt_budget(s: float) -> str:
    if s % 3600 == 0:
        return f"{int(s//3600)} ora" if s == 3600 else f"{int(s//3600)} ore"
    if s % 60 == 0:
        return f"{int(s//60)} minuti" if s != 60 else "1 minuto"
    return f"{int(s)} s"


def sec_budget_table(rows: list[Row], budget: float, total: int, mapfail: int) -> str:
    s = budget_stats(rows, budget)
    lbl = fmt_budget(budget)

    def faster(sub):
        return sum(1 for r in sub if r.we_faster)
    def med(sub):
        rr = [r.wisq_steps / r.my_steps for r in sub if r.my_steps]
        return median(rr)

    L = [f"## Tabella riassuntiva — budget wall-clock {lbl} ({int(budget)} s)\n",
         "Timeout imposto simmetricamente: conta solo chi finisce entro il budget.\n",
         "| Categoria | Circuiti | Di cui noi +veloci |",
         "|-----------|----------|--------------------|",
         f"| **Totale circuiti analizzati** | {total} | — |"]
    if mapfail:
        L.append(f"| Nostro mapping fallisce | {mapfail} | — |")
    L.append(f"| **WISQ non finisce in {lbl}** | {s['wisq_not']} | — |")
    L.append(f"| ↳ …ma anche noi sforiamo → nessun vincitore | {s['no_winner']} | — |")
    L.append(f"| ↳ …noi finiamo → **vittoria** | {s['we_win_to']} | — |")
    if s["our_loss"]:
        L.append(f"| **Noi non finiamo, WISQ sì → sconfitta** | {s['our_loss']} | — |")
    L.append(f"| **Entrambi finiscono in {lbl}** | {s['both']} | — |")
    L.append(f"| ↳ Noi vinciamo su steps | {len(s['wins'])} (ratio mediana {med(s['wins']):.2f}×) | {faster(s['wins'])} ({pct(faster(s['wins']), len(s['wins']))}) |")
    L.append(f"| ↳ Pareggio su steps | {len(s['ties'])} | {s['tie_faster']} ({pct(s['tie_faster'], len(s['ties']))}) |")
    L.append(f"| ↳ WISQ vince su steps | {len(s['losses'])} (ratio mediana {med(s['losses']):.2f}×) | {faster(s['losses'])} ({pct(faster(s['losses']), len(s['losses']))}) |")
    L.append("| | | |")
    L.append(f"| **TOTALE VITTORIE NOSTRE** | **{s['victories']} / {total} ({pct(s['victories'], total)})** | — |")
    return "\n".join(L)


def sec_winrate_trend(rows: list[Row], budgets: list[float], wisq_timeout: float,
                      base_victories: int, total: int) -> str:
    # First row = original asymmetric budget (only WISQ subject to mr_timeout).
    both0 = [r for r in rows if r.both]
    wisq_to0 = [r for r in rows if r.mapped and not r.wisq_done]
    L = ["## Andamento del win-rate al variare del budget wall-clock\n",
         "| Budget | Entrambi finiscono | WISQ timeout → ns vittoria | Noi timeout → sconfitta | Nessun vincitore | **Vittorie totali** |",
         "|--------|--------------------|----------------------------|-------------------------|------------------|---------------------|",
         f"| {int(wisq_timeout)} s (orig., asimm.) | {len(both0)} | {len(wisq_to0)} | 0 | 0 | **{base_victories} ({pct(base_victories, total)})** |"]
    peak = max(budgets, key=lambda b: budget_stats(rows, b)["victories"])
    for b in budgets:
        s = budget_stats(rows, b)
        mark = " ⟵ picco" if b == peak else ""
        L.append(f"| {fmt_budget(b)} | {s['both']} | {s['we_win_to']} | {s['our_loss']} | "
                 f"{s['no_winner']} | **{s['victories']} ({pct(s['victories'], total)})**{mark} |")
    return "\n".join(L)


# ── section 7: compile-time ───────────────────────────────────────────────────

def sec_compile_time(rows: list[Row]) -> str:
    mapped = [r for r in rows if r.mapped and r.my_dur and r.wisq_dur]

    def block(sub, label):
        if not sub:
            return f"| {label} | 0 | — | — | — | — | — |"
        sp = [r.wisq_dur / r.my_dur for r in sub]
        nf = sum(1 for x in sp if x > 1)
        return (f"| {label} | {len(sub)} | {nf} ({pct(nf, len(sub))}) | "
                f"{median(sp):.0f}× | {st.mean(sp):.0f}× | {min(sp):.2f}× | {max(sp):.0f}× |")

    both = [r for r in mapped if r.both]
    L = ["## Tempo di compilazione (wall-clock)\n",
         "Confronto `my_duration_s` vs `wisq_duration_s`. "
         "Speedup = `wisq_duration / my_duration` (>1 = siamo più veloci). "
         "I timeout WISQ sono inclusi con la durata registrata.\n",
         "| Categoria | N | Noi più veloci | Speedup mediano | Speedup medio | Min | Max |",
         "|-----------|---|----------------|-----------------|---------------|-----|-----|",
         block(mapped, "**Tutti (inclusi timeout WISQ)**"),
         block([r for r in both if r.verdict == "WIN"], "↳ Dove vinciamo su steps"),
         block([r for r in both if r.verdict == "TIE"], "↳ In pareggio su steps"),
         block([r for r in both if r.verdict == "LOSS"], "↳ Dove WISQ vince su steps"),
         block([r for r in mapped if not r.wisq_done], "↳ WISQ in timeout")]
    return "\n".join(L)


# ── section 8: ε speed-buffer win-rate ────────────────────────────────────────

def sec_epsilon(rows: list[Row], base_victories: int, total: int, csv_name: str) -> str:
    both = [r for r in rows if r.both]
    real_losses = [r for r in both if r.verdict == "LOSS"]
    anchors = [20, 50, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 2500,
               3000, 4000, 5000]
    L = ["## Buffer di steps dipendente dalla velocità — win-rate vs WISQ\n",
         f"Analisi su `{csv_name}`. La metrica primaria sono i **routing steps**, "
         "il tempo è secondario: concediamo un buffer ε sugli steps che cresce con "
         "l'ordine di grandezza del vantaggio di tempo.\n",
         "```",
         "vinco  se   my_steps <= wisq_steps · (1 + ε)",
         "ε(speedup) = α · log10(speedup)      speedup = wisq_time / my_time",
         "α = 0.05 / log10(N)      (ancora: 5% di sforo steps ⇄ N× di velocità)",
         "```\n",
         f"Baseline (steps primario, tempo solo spareggio) = "
         f"**{base_victories}/{total} = {pct(base_victories, total)}**.\n",
         "| ancora | α | loss recuperati | vittorie | % |",
         "|---|---:|---:|---:|---:|"]
    for N in anchors:
        alpha = 0.05 / math.log10(N)
        recovered = 0
        for r in real_losses:
            if r.my_dur and r.wisq_dur and r.wisq_dur > r.my_dur:
                eps = alpha * math.log10(r.wisq_dur / r.my_dur)
                if r.my_steps <= r.wisq_steps * (1 + eps):
                    recovered += 1
        vic = base_victories + recovered
        L.append(f"| 5% ⇄ {N}× | {alpha:.4f} | {recovered} | {vic} | {pct(vic, total)} |")
    return "\n".join(L)


# ── section 9: per family ─────────────────────────────────────────────────────

def sec_family(rows: list[Row]) -> str:
    fams: dict[str, list[Row]] = {}
    for r in rows:
        fams.setdefault(family(r.circuit), []).append(r)
    L = ["## Per famiglia di circuiti\n",
         "**WISQ timeout** = WISQ non ha completato. **MapFail** = il nostro mapping non riesce. "
         "Win/=/Loss sono sugli steps dove entrambi completano.\n",
         "| Family | N | Win | = (noi+veloci) | Loss | WISQ timeout | MapFail | Note |",
         "|--------|---|-----|----------------|------|--------------|---------|------|"]
    for fam in sorted(fams):
        sub = fams[fam]
        both = [r for r in sub if r.both]
        win = sum(1 for r in both if r.verdict == "WIN")
        tie = [r for r in both if r.verdict == "TIE"]
        tief = sum(1 for r in tie if r.we_faster)
        loss = sum(1 for r in both if r.verdict == "LOSS")
        wto = sum(1 for r in sub if r.mapped and not r.wisq_done)
        mf = sum(1 for r in sub if not r.mapped)
        ns = [r.n for r in sub if r.n is not None]
        note = f"n={min(ns)}–{max(ns)}" if ns and min(ns) != max(ns) else (f"n={ns[0]}" if ns else "")
        L.append(f"| {fam} | {len(sub)} | {win} | {len(tie)} ({tief} noi+veloci) | "
                 f"{loss} | {wto} | {mf} | {note} |")
    return "\n".join(L)


# ── section 10: per circuit ───────────────────────────────────────────────────

def sec_per_circuit(rows: list[Row], has_dim: bool) -> str:
    L = ["## Per circuito (dettaglio)\n",
         "**Steps**: WIN = noi meno routing steps, LOSS = WISQ meno, = pareggio. "
         "**Tempo** confronta le durate quando disponibili.\n"]
    if has_dim:
        L.append("| # | Circuit | Qubits | Grid (nostra) | Δlati | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |")
        L.append("|---|---------|--------|---------------|-------|----------|------------|-------|-------------|-------|-------|")
    else:
        L.append("| # | Circuit | Qubits | Grid | My steps | WISQ steps | Ratio | WISQ status | Steps | Tempo |")
        L.append("|---|---------|--------|------|----------|------------|-------|-------------|-------|-------|")
    for i, r in enumerate(sorted(rows, key=lambda r: r.circuit), 1):
        grid = f"{r.my_x}×{r.my_y}" if r.my_x else "—"
        my = r.my_steps if r.my_steps is not None else "—"
        wq = r.wisq_steps if r.wisq_steps is not None else "—"
        ratio = f"{r.wisq_steps / r.my_steps:.4f}" if r.both and r.my_steps else "—"
        if not r.mapped:
            steps_v = "**MapFail**"
        elif not r.wisq_done:
            steps_v = "timeout"
        else:
            steps_v = {"WIN": "**WIN**", "LOSS": "LOSS", "TIE": "="}[r.verdict]
        time_v = "—" if r.we_faster is None else ("noi +veloci" if r.we_faster else "WISQ +veloce")
        status = r.wisq_status or "—"
        if has_dim:
            dd = f"{r.dim_diff:+d}" if r.dim_diff is not None else "—"
            L.append(f"| {i} | {r.circuit} | {r.n if r.n else '—'} | {grid} | {dd} | {my} | {wq} | {ratio} | {status} | {steps_v} | {time_v} |")
        else:
            L.append(f"| {i} | {r.circuit} | {r.n if r.n else '—'} | {grid} | {my} | {wq} | {ratio} | {status} | {steps_v} | {time_v} |")
    return "\n".join(L)


# ── assembly ──────────────────────────────────────────────────────────────────

def build_report(csv_path: Path, title: str, intro: str, exclude: set[str],
                 shrink_baseline: Path | None, wisq_timeout: float,
                 budgets: list[float]) -> str:
    rows = load_rows(csv_path, exclude)
    has_dim = any(r.dim_diff is not None for r in rows)
    mapfail = sum(1 for r in rows if not r.mapped)

    perf, meta = sec_performance(rows)
    total, base_vic = meta["total"], meta["victories"]

    parts = [f"# {title}\n", intro.strip() + "\n",
             f"Dati da: `{csv_path.name}` — **{len(rows)} circuiti**"
             + (f" (esclusi: {', '.join('`'+c+'`' for c in sorted(exclude))})" if exclude else "")
             + ".\n", "---\n", perf, "---\n"]

    foot = sec_footprint(rows, shrink_baseline)
    if foot:
        parts += [foot, "---\n"]

    parts += [sec_aggregate(rows), "---\n"]

    dens = sec_density(rows)
    if dens:
        parts += [dens, "---\n"]

    for b in budgets:
        parts += [sec_budget_table(rows, b, total, mapfail), "---\n"]
    parts += [sec_winrate_trend(rows, budgets, wisq_timeout, base_vic, total), "---\n",
              sec_compile_time(rows), "---\n",
              sec_epsilon(rows, base_vic, total, csv_path.name), "---\n",
              sec_family(rows), "---\n",
              sec_per_circuit(rows, has_dim)]
    return "\n\n".join(parts) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", required=True, type=Path, help="Side-by-side CSV.")
    p.add_argument("--out", required=True, type=Path, help="Output .md path.")
    p.add_argument("--title", required=True)
    p.add_argument("--intro", default="", help="Config/regime blurb under the title.")
    p.add_argument("--exclude", nargs="*", default=[], help="Circuits to drop.")
    p.add_argument("--shrink-baseline", type=Path, default=None,
                   help="Native-grid ours CSV; enables the 'pure shrink cost' trade-off.")
    p.add_argument("--wisq-timeout", type=float, default=12000,
                   help="mr_timeout used for the asymmetric baseline row (s).")
    p.add_argument("--budgets", type=float, nargs="*",
                   default=[3600, 1800, 900, 600, 300, 60])
    args = p.parse_args()

    md = build_report(args.csv, args.title, args.intro, set(args.exclude),
                      args.shrink_baseline, args.wisq_timeout, sorted(args.budgets, reverse=True))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md)
    print(f"Wrote {args.out}  ({len(md.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
