"""Realistic climate model for the Aurora Siger colony.

Based on NASA/ESA literature (see spec, section 6).
Wind: diurnal cycle + Gaussian noise + seasonal modulation.
Temperature: sinusoidal diurnal cycle + seasonal variation + noise.
Storms: state machine (clear → light/moderate/severe).
Panels: continuous deposition + stochastic cleaning (dust devils).
"""

import math
import random

from colony.constants import (
    V_BASE, V_AMPLITUDE, SEASONAL_FACTOR, V_NOISE_SIGMA,
    T_MEAN, A_DAILY, A_SEASONAL, PHI_DAILY, T_NOISE_SIGMA,
    SOLS_PER_MARS_YEAR,
    BASE_PROB_PER_SOL, DURATION_HOURS, WIND_BONUS_THRESHOLD, PERIHELION_FACTOR,
    DIDACTIC_EVENT_SOL, DIDACTIC_EVENT_HOUR,
    TAU_BASE, TAU_WIND_FACTOR, TAU_WIND_THRESHOLD,
    PANEL_LOSS_PER_SOL, CLEANING_RECOVERY, PANEL_FACTOR_FLOOR,
)


def compute_tau(storm, wind):
    """Atmospheric opacity = base per class + wind bonus."""
    extra = TAU_WIND_FACTOR * max(0.0, wind - TAU_WIND_THRESHOLD)
    return TAU_BASE[storm] + extra


def solar_transmission(tau):
    """Beer-Lambert: transmission = exp(-tau) (zenith simplification)."""
    return math.exp(-tau)


def update_panel_factor(current_factor, cleaning_drawn):
    """Applies continuous deposition and (if cleaning_drawn) dust-devil recovery."""
    new = max(PANEL_FACTOR_FLOOR, current_factor - PANEL_LOSS_PER_SOL)
    if cleaning_drawn:
        recovery = random.uniform(*CLEANING_RECOVERY)
        new = min(1.0, new + recovery)
    return new


def sample_wind(hour):
    """Returns wind speed in m/s for the given local hour (0..23)."""
    daily_component = V_AMPLITUDE * max(0.0, math.sin(math.pi * (hour - 6) / 12))
    noise = random.gauss(0, V_NOISE_SIGMA)
    return max(0.0, (V_BASE + daily_component) * SEASONAL_FACTOR + noise)


def sample_temperature(sol, hour):
    """Returns temperature in °C for the given sol and hour."""
    daily = A_DAILY * math.sin(2 * math.pi * (hour - PHI_DAILY) / 24)
    seasonal = A_SEASONAL * math.sin(2 * math.pi * sol / SOLS_PER_MARS_YEAR)
    noise = random.gauss(0, T_NOISE_SIGMA)
    return T_MEAN + daily + seasonal + noise


class StormState:
    """State machine for Martian dust storms.

    States: 'clear' → 'light' / 'moderate' / 'severe'.
    Temporal persistence: once started, lasts `hours_remaining` hours.
    """

    def __init__(self):
        self.state = "clear"
        self.hours_remaining = 0

    def _start_probability(self, klass, wind_max_24h, sol):
        prob = BASE_PROB_PER_SOL[klass]
        wind_bonus = max(0.0, (wind_max_24h - WIND_BONUS_THRESHOLD) / 10.0)
        # perihelion: simple approximation — sols 0..6 are "perihelion" by construction
        return prob * (1 + wind_bonus) * PERIHELION_FACTOR

    def advance(self, wind_max_24h, sol, hour, force_event=False):
        """Advances one step (1 hour) of the state machine."""
        if force_event and sol == DIDACTIC_EVENT_SOL and hour == DIDACTIC_EVENT_HOUR and self.state == "clear":
            self.state = "moderate"
            min_h, max_h = DURATION_HOURS["moderate"]
            self.hours_remaining = random.randint(min_h, max_h)
            return

        if self.state != "clear":
            self.hours_remaining -= 1
            if self.hours_remaining <= 0:
                self.state = "clear"
                self.hours_remaining = 0
            return

        # current state = clear: roll to see if a new storm starts.
        # one roll per hour; per-sol probability divided by 24 → per-hour probability.
        for klass in ("severe", "moderate", "light"):  # rarest first
            hour_prob = self._start_probability(klass, wind_max_24h, sol) / 24.0
            if random.random() < hour_prob:
                self.state = klass
                min_h, max_h = DURATION_HOURS[klass]
                self.hours_remaining = random.randint(min_h, max_h)
                return
