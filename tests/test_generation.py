"""Tests for the energy generation model."""

import math
import unittest

from colony.generation import generate_solar, generate_wind, generate_nuclear
from colony.modules import find_module


class TestSolar(unittest.TestCase):

    def setUp(self):
        self.solar = find_module(4)

    def test_solar_is_zero_at_night(self):
        climate = {"hour": 2, "tau": 0.5, "panel_factor": 1.0}
        self.assertEqual(generate_solar(self.solar, climate), 0.0)

    def test_solar_peak_at_noon_clear(self):
        climate = {"hour": 12, "tau": 0.5, "panel_factor": 1.0}
        # capacity 100 * 1.0 * exp(-0.5) * 1.0 ≈ 60.65
        self.assertAlmostEqual(generate_solar(self.solar, climate), 100 * math.exp(-0.5), places=2)

    def test_solar_severe_storm_near_zero(self):
        climate = {"hour": 12, "tau": 8.0, "panel_factor": 1.0}
        self.assertLess(generate_solar(self.solar, climate), 0.1)

    def test_solar_dirty_panels_reduce_output(self):
        clean = {"hour": 12, "tau": 0.5, "panel_factor": 1.0}
        dirty = {"hour": 12, "tau": 0.5, "panel_factor": 0.5}
        self.assertGreater(generate_solar(self.solar, clean), generate_solar(self.solar, dirty))


class TestWind(unittest.TestCase):

    def setUp(self):
        self.wind = find_module(13)

    def test_cut_in_at_3_ms(self):
        """Below v=3 m/s, no generation (cut-in)."""
        self.assertEqual(generate_wind(self.wind, {"wind_ms": 2.0}), 0.0)
        self.assertEqual(generate_wind(self.wind, {"wind_ms": 3.0}), 0.0)

    def test_generates_in_medium_wind(self):
        # P = 2.5*10 - 7.5 = 17.5 kW
        self.assertAlmostEqual(generate_wind(self.wind, {"wind_ms": 10.0}), 17.5)

    def test_saturates_at_capacity(self):
        # capacity 30 kW; high wind must saturate
        self.assertEqual(generate_wind(self.wind, {"wind_ms": 25.0}), 30.0)


class TestNuclear(unittest.TestCase):

    def test_nuclear_is_constant(self):
        nuclear = find_module(5)
        for hour in range(24):
            climate = {"hour": hour, "tau": 0.5}
            self.assertEqual(generate_nuclear(nuclear, climate), 80.0)


if __name__ == "__main__":
    unittest.main()
