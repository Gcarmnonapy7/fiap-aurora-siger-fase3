"""End-to-end simulator integration tests."""

import unittest

from colony.constants import TOTAL_STEPS
from colony.simulator import run_simulation


class TestSimulatorIntegration(unittest.TestCase):

    def test_history_has_168_points(self):
        _, _, history = run_simulation(seed=42)
        for key in ["wind_ms", "temperature_c", "total_generation_kw", "total_consumption_kw"]:
            self.assertEqual(len(history[key]), TOTAL_STEPS)

    def test_total_generation_never_negative(self):
        _, _, history = run_simulation(seed=42)
        for g in history["total_generation_kw"]:
            self.assertGreaterEqual(g, 0)

    def test_total_consumption_never_negative(self):
        _, _, history = run_simulation(seed=42)
        for c in history["total_consumption_kw"]:
            self.assertGreaterEqual(c, 0)

    def test_battery_within_limits(self):
        _, battery, history = run_simulation(seed=42)
        for charge in history["battery_charge_kwh"]:
            self.assertGreaterEqual(charge, 0)
            self.assertLessEqual(charge, battery["max_capacity_kwh"])

    def test_didactic_event_appears_in_history(self):
        _, _, history = run_simulation(seed=42)
        self.assertIn("moderate", history["storm"])

    def test_horizon_parameter_shortens_run(self):
        _, _, history = run_simulation(seed=42, horizon=10)
        self.assertEqual(len(history["wind_ms"]), 10)


class TestSimulatorDeterminism(unittest.TestCase):

    def test_seed_42_is_reproducible(self):
        _, _, h1 = run_simulation(seed=42)
        _, _, h2 = run_simulation(seed=42)
        self.assertEqual(h1["wind_ms"], h2["wind_ms"])
        self.assertEqual(h1["total_generation_kw"], h2["total_generation_kw"])

    def test_seed_none_produces_different_runs(self):
        """seed=None lets the system entropy vary the outputs.

        We can't assert *every* point differs (collisions are possible by
        chance), so we assert at least one differs across the 168 points.
        """
        _, _, h1 = run_simulation(seed=None)
        _, _, h2 = run_simulation(seed=None)
        self.assertTrue(
            any(a != b for a, b in zip(h1["wind_ms"], h2["wind_ms"])),
            "expected non-deterministic runs to differ somewhere",
        )

    def test_different_seeds_differ(self):
        _, _, h1 = run_simulation(seed=1)
        _, _, h2 = run_simulation(seed=2)
        self.assertNotEqual(h1["wind_ms"], h2["wind_ms"])


if __name__ == "__main__":
    unittest.main()
