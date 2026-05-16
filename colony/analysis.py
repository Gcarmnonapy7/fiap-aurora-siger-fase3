"""Energy-balance analysis — covers item 1.4 of the official assignment.

Three responsibilities:

1. `analyze_balance(generation, consumption)`: instantaneous comparison
   that emits "ALERTA: consumo maior que geração" or
   "SUGESTÃO: armazenar energia excedente" exactly as the syllabus
   prescribes.
2. `summarize_history(history)`: aggregate statistics over the entire
   simulation run (averages, extremes, alert counts).
3. `write_log(history, path, seed)`: appends the step-by-step history
   to a plaintext file with a header identifying the run.
"""

import os
from datetime import datetime

from colony.constants import HOURS_PER_SOL

SURPLUS_MARGIN = 1.10  # generation must exceed consumption by 10% to be "surplus"

STATUS_RISK = "risk"
STATUS_SURPLUS = "surplus"
STATUS_BALANCED = "balanced"

MSG_RISK = "ALERTA: consumo maior que geração"
MSG_SURPLUS = "SUGESTÃO: armazenar energia excedente"
MSG_BALANCED = "INFO: balanceado"

# Order used to render mixed climate regimes from least to worst severity.
STORM_SEVERITY = ["clear", "light", "moderate", "severe"]


def _safe_share(value, total):
    """Returns value/total, or 0.0 if total is zero. Avoids ZeroDivisionError."""
    return value / total if total > 0 else 0.0


def analyze_balance(generation_kw, consumption_kw):
    """Classifies the instantaneous balance into risk/surplus/balanced."""
    delta = generation_kw - consumption_kw
    if generation_kw < consumption_kw:
        status, message = STATUS_RISK, MSG_RISK
    elif generation_kw > consumption_kw * SURPLUS_MARGIN:
        status, message = STATUS_SURPLUS, MSG_SURPLUS
    else:
        status, message = STATUS_BALANCED, MSG_BALANCED
    return {"status": status, "message": message, "delta_kw": delta}


def summarize_history(history):
    """Aggregates metrics over the full history."""
    gen = history["total_generation_kw"]
    con = history["total_consumption_kw"]
    n = len(gen)
    return {
        "total_steps": n,
        "avg_generation_kw": sum(gen) / n if n else 0.0,
        "avg_consumption_kw": sum(con) / n if n else 0.0,
        "max_generation_kw": max(gen) if gen else 0.0,
        "min_generation_kw": min(gen) if gen else 0.0,
        "storm_hours": sum(1 for s in history["storm"] if s != "clear"),
        "alert_hours": sum(1 for a in history["alerts"] if a),
    }


def aggregate_by_sol(history):
    """Aggregates the history into one row per Martian sol (24 hours).

    A partial trailing sol shows up as the final row with `hours < 24`.
    Each row carries the per-sol averages plus a `regime` string listing
    the climate states observed that day in severity order.
    """
    gen = history["total_generation_kw"]
    con = history["total_consumption_kw"]
    storms = history["storm"]
    n = len(gen)

    rows = []
    for start in range(0, n, HOURS_PER_SOL):
        end = min(start + HOURS_PER_SOL, n)
        slice_gen = gen[start:end]
        slice_con = con[start:end]
        slice_storms = storms[start:end]
        hours = end - start
        avg_gen = sum(slice_gen) / hours
        avg_con = sum(slice_con) / hours
        unique_storms = sorted(set(slice_storms), key=STORM_SEVERITY.index)
        rows.append({
            "sol": start // HOURS_PER_SOL,
            "hours": hours,
            "avg_generation_kw": avg_gen,
            "avg_consumption_kw": avg_con,
            "avg_delta_kw": avg_gen - avg_con,
            "regime": "/".join(unique_storms),
        })
    return rows


def status_distribution(history):
    """Counts how many hours fell into each balance status."""
    counts = {STATUS_RISK: 0, STATUS_BALANCED: 0, STATUS_SURPLUS: 0}
    for g, c in zip(history["total_generation_kw"], history["total_consumption_kw"]):
        counts[analyze_balance(g, c)["status"]] += 1
    return counts


def generation_breakdown(history):
    """Average power and percentage share per energy source."""
    n = len(history["total_generation_kw"])
    if n == 0:
        empty = {"avg_kw": 0.0, "share": 0.0}
        return {"solar": dict(empty), "wind": dict(empty), "nuclear": dict(empty)}

    solar_avg = sum(history["solar_generation_kw"]) / n
    wind_avg = sum(history["wind_generation_kw"]) / n
    nuclear_avg = sum(history["nuclear_generation_kw"]) / n
    total = solar_avg + wind_avg + nuclear_avg
    return {
        "solar":   {"avg_kw": solar_avg,   "share": _safe_share(solar_avg, total)},
        "wind":    {"avg_kw": wind_avg,    "share": _safe_share(wind_avg, total)},
        "nuclear": {"avg_kw": nuclear_avg, "share": _safe_share(nuclear_avg, total)},
    }


def critical_moments(history):
    """Finds the hour of biggest deficit and biggest surplus."""
    n = len(history["total_generation_kw"])
    if n == 0:
        return {"worst_deficit": None, "biggest_surplus": None}

    deltas = [g - c for g, c in zip(history["total_generation_kw"], history["total_consumption_kw"])]
    worst = min(range(n), key=lambda i: deltas[i])
    best = max(range(n), key=lambda i: deltas[i])

    def snapshot(idx):
        return {
            "sol": idx // HOURS_PER_SOL,
            "hour": idx % HOURS_PER_SOL,
            "delta_kw": deltas[idx],
            "storm": history["storm"][idx],
        }

    return {"worst_deficit": snapshot(worst), "biggest_surplus": snapshot(best)}


def write_log(history, path, seed=None):
    """Appends the per-step history to `path` as readable plaintext.

    Each call adds a self-contained block prefixed by a header that
    identifies the simulation (seed, horizon, timestamp). Existing
    content is preserved — the file grows on every call.

    The parent directory is created on demand, so the first run on a
    fresh checkout does not fail with FileNotFoundError.
    """
    n = len(history["total_generation_kw"])
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    seed_label = "random" if seed is None else str(seed)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"=== Aurora Siger | seed={seed_label} | {n} hours | {timestamp} ===\n")
        for k in range(n):
            balance = analyze_balance(
                history["total_generation_kw"][k],
                history["total_consumption_kw"][k],
            )
            sol = k // HOURS_PER_SOL
            hour = k % HOURS_PER_SOL
            f.write(
                f"step={k} sol={sol} hour={hour:02d} "
                f"storm={history['storm'][k]} "
                f"gen={history['total_generation_kw'][k]:.1f}kW "
                f"con={history['total_consumption_kw'][k]:.1f}kW "
                f"bat={history['battery_charge_kwh'][k]:.0f}kWh "
                f"status={balance['status']}\n"
            )
        f.write("\n")
