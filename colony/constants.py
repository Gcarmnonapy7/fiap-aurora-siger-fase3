"""Parâmetros físicos e operacionais do simulador.

Valores derivados de literatura científica — ver Seção 6 do spec
em docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md
"""

import math

# Simulation horizon
HORIZON_SOLS = 7
HOURS_PER_SOL = 24
TOTAL_STEPS = HORIZON_SOLS * HOURS_PER_SOL  # 168

# --- Wind ---
V_BASE = 2.5
V_AMPLITUDE = 7.0
SEASONAL_FACTOR = 1.2  # perihelion
V_NOISE_SIGMA = 1.5

# --- Dust storms ---
BASE_PROB_PER_SOL = {
    "light":    0.40,
    "moderate": 0.04,
    "severe":   0.002,
}

DURATION_HOURS = {
    "light":    (12, 72),
    "moderate": (72, 168),
    "severe":   (168, 720),
}

WIND_BONUS_THRESHOLD = 15.0  # m/s above this raises storm probability
PERIHELION_FACTOR = 1.5

FORCE_DIDACTIC_EVENT = True
DIDACTIC_EVENT_SOL = 3
DIDACTIC_EVENT_HOUR = 8

# --- Atmospheric opacity (tau) ---
TAU_BASE = {
    "clear":    0.5,
    "light":    1.5,
    "moderate": 3.0,
    "severe":   8.0,
}
TAU_WIND_FACTOR = 0.05  # extra tau per m/s above 5 m/s
TAU_WIND_THRESHOLD = 5.0

# --- Solar panels ---
PANEL_LOSS_PER_SOL = 0.002          # 0.2% per sol
CLEANING_PROB_PER_SOL = 0.005       # ~1 event every 200 sols
CLEANING_RECOVERY = (0.30, 0.70)    # recovery range per dust devil
PANEL_FACTOR_FLOOR = 0.30           # manual cleaning floor

# --- Temperature ---
T_MEAN = -60.0
A_DAILY = 35.0
A_SEASONAL = 18.0
PHI_DAILY = 9  # peak around 15h local
SOLS_PER_MARS_YEAR = 668
T_NOISE_SIGMA = 2.0

# --- Thermal consumption (Q = U·A·ΔT) ---
A_ENVELOPE = 250.0           # m²
U_INSULATION = 0.15          # W/m²·K
T_TARGET_INTERNAL = 20.0     # °C
INTERNAL_GAIN_W = 4000.0     # W
ETA_HEATER = 0.95

# --- Battery ---
BATTERY_CAPACITY_KWH = 500.0
BATTERY_INITIAL_CHARGE_KWH = 250.0
BATTERY_EMERGENCY_RESERVE_FRACTION = 0.20  # 20% untouchable


def solar_daytime_curve(hour):
    """Fraction of irradiance as a function of hour (0..1, bell shape between 06–18h)."""
    return max(0.0, math.sin(math.pi * (hour - 6) / 12))
