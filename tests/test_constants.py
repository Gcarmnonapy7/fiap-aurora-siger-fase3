"""Tests for colony.constants — sanity checks for physical parameters."""

import unittest

from colony.constants import (
    HORIZON_SOLS, HOURS_PER_SOL, TOTAL_STEPS,
    BASE_PROB_PER_SOL, DURATION_HOURS, TAU_BASE,
    BATTERY_CAPACITY_KWH, BATTERY_INITIAL_CHARGE_KWH,
    BATTERY_EMERGENCY_RESERVE_FRACTION,
    solar_daytime_curve,
)


class TestHorizon(unittest.TestCase):
    def test_total_steps_is_consistent(self):
        self.assertEqual(TOTAL_STEPS, HORIZON_SOLS * HOURS_PER_SOL)
        self.assertEqual(TOTAL_STEPS, 168)


class TestStormParams(unittest.TestCase):
    def test_storm_classes_are_aligned(self):
        self.assertEqual(set(BASE_PROB_PER_SOL.keys()), {"light", "moderate", "severe"})
        self.assertEqual(set(DURATION_HOURS.keys()), {"light", "moderate", "severe"})

    def test_severe_is_rarer_than_light(self):
        self.assertLess(BASE_PROB_PER_SOL["severe"], BASE_PROB_PER_SOL["moderate"])
        self.assertLess(BASE_PROB_PER_SOL["moderate"], BASE_PROB_PER_SOL["light"])

    def test_severe_lasts_longer_than_light(self):
        self.assertGreater(DURATION_HOURS["severe"][0], DURATION_HOURS["light"][1])


class TestTauBase(unittest.TestCase):
    def test_tau_covers_all_states(self):
        self.assertEqual(set(TAU_BASE.keys()), {"clear", "light", "moderate", "severe"})

    def test_tau_increases_with_severity(self):
        self.assertLess(TAU_BASE["clear"], TAU_BASE["light"])
        self.assertLess(TAU_BASE["light"], TAU_BASE["moderate"])
        self.assertLess(TAU_BASE["moderate"], TAU_BASE["severe"])


class TestBatteryParams(unittest.TestCase):
    def test_initial_is_below_capacity(self):
        self.assertLessEqual(BATTERY_INITIAL_CHARGE_KWH, BATTERY_CAPACITY_KWH)

    def test_reserve_fraction_in_range(self):
        self.assertGreater(BATTERY_EMERGENCY_RESERVE_FRACTION, 0.0)
        self.assertLess(BATTERY_EMERGENCY_RESERVE_FRACTION, 1.0)


class TestSolarDaytimeCurve(unittest.TestCase):
    def test_zero_at_night(self):
        self.assertEqual(solar_daytime_curve(0), 0.0)
        self.assertEqual(solar_daytime_curve(5), 0.0)
        self.assertEqual(solar_daytime_curve(19), 0.0)
        self.assertEqual(solar_daytime_curve(23), 0.0)

    def test_peak_at_noon(self):
        self.assertAlmostEqual(solar_daytime_curve(12), 1.0, places=6)

    def test_dawn_and_dusk_are_zero(self):
        self.assertAlmostEqual(solar_daytime_curve(6), 0.0, places=6)
        self.assertAlmostEqual(solar_daytime_curve(18), 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
