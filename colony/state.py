"""Global simulator state: current climate, battery, history."""

from colony.constants import (
    BATTERY_CAPACITY_KWH, BATTERY_INITIAL_CHARGE_KWH, BATTERY_EMERGENCY_RESERVE_FRACTION,
    HISTORY_KEYS,
)


def initial_state():
    """Builds a fresh colony state (empty climate/battery/history)."""
    climate = {
        "sol": 0, "hour": 0,
        "wind_ms": 0.0,
        "storm": "clear",
        "tau": 0.5,
        "temperature_c": -60.0,
        "panel_factor": 1.0,
    }
    battery = {
        "current_charge_kwh": BATTERY_INITIAL_CHARGE_KWH,
        "max_capacity_kwh": BATTERY_CAPACITY_KWH,
        "emergency_reserve_kwh": BATTERY_CAPACITY_KWH * BATTERY_EMERGENCY_RESERVE_FRACTION,
    }
    history = {key: [] for key in HISTORY_KEYS}
    return climate, battery, history
