"""Simulator orchestrator: 1 step + complete 168-step horizon."""

import random
from collections import deque

from colony.allocation import allocate_energy
from colony.climate import (
    sample_wind, sample_temperature, compute_tau,
    update_panel_factor, StormState,
)
from colony.consumption import current_consumption_kw
from colony.constants import (
    HOURS_PER_SOL, TOTAL_STEPS,
    CLEANING_PROB_PER_SOL, FORCE_DIDACTIC_EVENT,
)
from colony.state import initial_state
from colony.generation import generate_solar, generate_wind, generate_nuclear
from colony.hierarchies import build_criticality_tree
from colony.modules import MODULES


def _detail_generation(climate):
    """Returns {kind: kW} for history bookkeeping.

    Iterates MODULES directly — generation only depends on each module's
    type, not on its position in any hierarchy.
    """
    detail = {"solar": 0.0, "wind": 0.0, "nuclear": 0.0}
    for m in MODULES:
        if m["type"] == "solar_generator":
            detail["solar"] += generate_solar(m, climate)
        elif m["type"] == "wind_generator":
            detail["wind"] += generate_wind(m, climate)
        elif m["type"] == "nuclear_generator":
            detail["nuclear"] += generate_nuclear(m, climate)
    return detail


def step(state):
    """Advances the simulation by 1 hour. Mutates `state` in place.

    `state` keys: climate, battery, history, criticality_tree,
    storm_state, last_wind_24h.
    """
    climate = state["climate"]
    battery = state["battery"]
    history = state["history"]
    criticality = state["criticality_tree"]
    storm_state = state["storm_state"]
    last_wind_24h = state["last_wind_24h"]

    sol = climate["sol"]
    hour = climate["hour"]

    # 1. Sample climate
    wind = sample_wind(hour)
    temperature = sample_temperature(sol, hour)
    last_wind_24h.append(wind)
    wind_max_24h = max(last_wind_24h)

    storm_state.advance(wind_max_24h, sol, hour, force_event=FORCE_DIDACTIC_EVENT)
    tau = compute_tau(storm_state.state, wind)

    # Update panels (once per sol, at hour 0)
    if hour == 0:
        cleaning_drawn = random.random() < CLEANING_PROB_PER_SOL
        climate["panel_factor"] = update_panel_factor(climate["panel_factor"], cleaning_drawn)

    climate["wind_ms"] = wind
    climate["temperature_c"] = temperature
    climate["storm"] = storm_state.state
    climate["tau"] = tau

    # 2. Generation
    detail = _detail_generation(climate)
    total_generation = detail["solar"] + detail["wind"] + detail["nuclear"]

    # 3. Supply (generation + battery available above reserve)
    battery_available = max(0, battery["current_charge_kwh"] - battery["emergency_reserve_kwh"])
    supply = total_generation + battery_available

    # 4. Allocation
    allocate_energy(criticality, supply_kw=supply, climate=climate)

    # 5. Total consumption
    total_consumption = sum(current_consumption_kw(m, climate) for m in MODULES)

    # 6. Battery balance — clamped to [0, max]. The emergency reserve is
    # preserved by construction in stages 1–3 (supply ignores below-reserve
    # charge); only stage-4 emergencies can dip below it, and those hours
    # always carry an EMERGÊNCIA alert (see step 7).
    balance = total_generation - total_consumption
    battery["current_charge_kwh"] = max(0, min(
        battery["max_capacity_kwh"],
        battery["current_charge_kwh"] + balance,
    ))

    # 7. Emergency alert
    alerts = []
    if total_consumption > total_generation + battery_available:
        alerts.append(f"EMERGÊNCIA sol {sol} hora {hour}: oferta insuficiente")

    # 8. Record history
    history["wind_ms"].append(wind)
    history["temperature_c"].append(temperature)
    history["storm"].append(storm_state.state)
    history["tau"].append(tau)
    history["solar_generation_kw"].append(detail["solar"])
    history["wind_generation_kw"].append(detail["wind"])
    history["nuclear_generation_kw"].append(detail["nuclear"])
    history["total_generation_kw"].append(total_generation)
    history["total_consumption_kw"].append(total_consumption)
    history["battery_charge_kwh"].append(battery["current_charge_kwh"])
    history["modes_summary"].append({m["name"]: m["current_mode"] for m in MODULES})
    history["alerts"].append(alerts)

    # 9. Advance clock
    climate["hour"] += 1
    if climate["hour"] >= HOURS_PER_SOL:
        climate["hour"] = 0
        climate["sol"] += 1


def run_simulation(seed: int | None = 42, horizon: int = TOTAL_STEPS):
    """Runs the simulator for `horizon` steps. Returns (climate, battery, history).

    seed=42 (default): deterministic run (used by tests).
    seed=None: skip random.seed() — system entropy is used, results vary.
    """
    if seed is not None:
        random.seed(seed)

    climate, battery, history = initial_state()
    state = {
        "climate": climate,
        "battery": battery,
        "history": history,
        "criticality_tree": build_criticality_tree(),
        "storm_state": StormState(),
        "last_wind_24h": deque(maxlen=24),
    }

    for _ in range(horizon):
        step(state)

    return climate, battery, history
