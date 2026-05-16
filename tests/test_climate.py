"""Tests for the climate model."""

import math
import random
import unittest

from colony.climate import (
    sample_wind, sample_temperature, compute_tau, solar_transmission,
    update_panel_factor, StormState,
)
from colony.constants import PANEL_FACTOR_FLOOR


class TestWind(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_wind_is_non_negative(self):
        for hour in range(24):
            self.assertGreaterEqual(sample_wind(hour), 0)

    def test_daytime_peak_higher_than_night(self):
        random.seed(42)
        day = [sample_wind(h) for h in [13, 14, 15] for _ in range(50)]
        random.seed(42)
        night = [sample_wind(h) for h in [2, 3, 4] for _ in range(50)]
        self.assertGreater(sum(day) / len(day), sum(night) / len(night))


class TestTemperature(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_noon_warmer_than_dawn(self):
        random.seed(42)
        warm = [sample_temperature(0, 14) for _ in range(50)]
        random.seed(42)
        cold = [sample_temperature(0, 4) for _ in range(50)]
        self.assertGreater(sum(warm) / len(warm), sum(cold) / len(cold))

    def test_temperature_in_martian_range(self):
        for sol in range(7):
            for hour in range(24):
                t = sample_temperature(sol, hour)
                self.assertGreater(t, -100)
                self.assertLess(t, 20)


class TestStormState(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_starts_clear(self):
        s = StormState()
        self.assertEqual(s.state, "clear")
        self.assertEqual(s.hours_remaining, 0)

    def test_advance_without_storm_stays_in_known_states(self):
        s = StormState()
        for _ in range(100):
            s.advance(wind_max_24h=5.0, sol=0, hour=12)
            self.assertIn(s.state, ("clear", "light", "moderate", "severe"))

    def test_force_didactic_event_at_sol_3(self):
        s = StormState()
        s.advance(wind_max_24h=5.0, sol=3, hour=8, force_event=True)
        self.assertEqual(s.state, "moderate")
        self.assertGreater(s.hours_remaining, 0)

    def test_light_storm_duration_decrements(self):
        s = StormState()
        s.state = "light"
        s.hours_remaining = 5
        s.advance(wind_max_24h=5.0, sol=0, hour=12)
        self.assertEqual(s.hours_remaining, 4)

    def test_storm_ends_when_hours_reach_zero(self):
        s = StormState()
        s.state = "light"
        s.hours_remaining = 1
        s.advance(wind_max_24h=5.0, sol=0, hour=12)
        self.assertEqual(s.state, "clear")
        self.assertEqual(s.hours_remaining, 0)


class TestTauAndTransmission(unittest.TestCase):

    def test_tau_clear_is_low(self):
        self.assertAlmostEqual(compute_tau("clear", wind=2.0), 0.5)

    def test_tau_severe_is_high(self):
        self.assertAlmostEqual(compute_tau("severe", wind=2.0), 8.0)

    def test_tau_grows_with_wind(self):
        low = compute_tau("clear", wind=5.0)
        high = compute_tau("clear", wind=15.0)
        self.assertGreater(high, low)

    def test_transmission_clear_is_about_60_percent(self):
        # exp(-0.5) ≈ 0.6065
        self.assertAlmostEqual(solar_transmission(0.5), math.exp(-0.5), places=3)

    def test_transmission_severe_near_zero(self):
        self.assertLess(solar_transmission(8.0), 0.001)


class TestPanelFactor(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_deposition_reduces_factor(self):
        new = update_panel_factor(current_factor=1.0, cleaning_drawn=False)
        self.assertLess(new, 1.0)
        self.assertAlmostEqual(new, 1.0 - 0.002, places=4)

    def test_cleaning_recovers_factor(self):
        new = update_panel_factor(current_factor=0.5, cleaning_drawn=True)
        self.assertGreater(new, 0.5)

    def test_factor_does_not_go_below_floor(self):
        new = update_panel_factor(current_factor=PANEL_FACTOR_FLOOR, cleaning_drawn=False)
        self.assertGreaterEqual(new, PANEL_FACTOR_FLOOR)


if __name__ == "__main__":
    unittest.main()
