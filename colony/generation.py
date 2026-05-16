"""Generation functions for the colony's three energy sources."""

from colony.climate import solar_transmission
from colony.constants import solar_daytime_curve


def generate_solar(module, climate):
    """Solar power (kW): capacity × daytime_curve × transmission × panel_factor."""
    curve = solar_daytime_curve(climate["hour"])
    transm = solar_transmission(climate["tau"])
    return module["max_capacity_kw"] * curve * transm * climate["panel_factor"]


def generate_wind(module, climate):
    """Wind power (kW): linear model with cut-in (3 m/s) and saturation at capacity.

    Form: P = max(0, min(capacity, A*v - B))
    With A=2.5 and B=7.5: P(3)=0, P(10)=17.5, saturates around v ≈ 15 m/s.
    """
    A_LINEAR = 2.5
    B_LINEAR = 7.5
    v = climate["wind_ms"]
    power = A_LINEAR * v - B_LINEAR
    return max(0.0, min(module["max_capacity_kw"], power))


def generate_nuclear(module, climate):
    """Nuclear power (kW): constant baseload at nominal capacity."""
    return module["max_capacity_kw"]
