"""Energy-balance analysis — covers item 1.4 of the official assignment.

Three responsibilities:

1. `analyze_balance(generation, consumption)`: instantaneous comparison
   that emits "ALERTA: consumo maior que geração" or
   "SUGESTÃO: armazenar energia excedente" exactly as the syllabus
   prescribes.
2. `summarize_history(history)`: aggregate statistics over the entire
   simulation run (averages, extremes, alert counts).
3. `write_log(history, path)`: serializes the step-by-step history to a
   plaintext file (the artifact requested by the AURORA CORE proposal).
"""

SURPLUS_MARGIN = 1.10  # generation must exceed consumption by 10% to be "surplus"

STATUS_RISK = "risk"
STATUS_SURPLUS = "surplus"
STATUS_BALANCED = "balanced"

MSG_RISK = "ALERTA: consumo maior que geração"
MSG_SURPLUS = "SUGESTÃO: armazenar energia excedente"
MSG_BALANCED = "BALANCEADO"


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


def write_log(history, path):
    """Writes the per-step history to `path` as readable plaintext."""
    n = len(history["total_generation_kw"])
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Aurora Siger colony log\n")
        f.write(f"# {n} steps recorded\n\n")
        for k in range(n):
            balance = analyze_balance(
                history["total_generation_kw"][k],
                history["total_consumption_kw"][k],
            )
            sol = k // 24
            hour = k % 24
            f.write(
                f"step={k} sol={sol} hour={hour:02d} "
                f"storm={history['storm'][k]} "
                f"gen={history['total_generation_kw'][k]:.1f}kW "
                f"con={history['total_consumption_kw'][k]:.1f}kW "
                f"bat={history['battery_charge_kwh'][k]:.0f}kWh "
                f"status={balance['status']}\n"
            )
