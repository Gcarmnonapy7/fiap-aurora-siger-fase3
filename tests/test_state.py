"""Tests for the initial colony state factory."""

import unittest

from colony.state import initial_state
from colony.constants import (
    BATTERY_CAPACITY_KWH, BATTERY_INITIAL_CHARGE_KWH, BATTERY_EMERGENCY_RESERVE_FRACTION,
)


class TestInitialState(unittest.TestCase):

    def test_climate_starts_clear(self):
        climate, _, _ = initial_state()
        self.assertEqual(climate["storm"], "clear")
        self.assertEqual(climate["sol"], 0)
        self.assertEqual(climate["hour"], 0)
        self.assertEqual(climate["panel_factor"], 1.0)

    def test_battery_at_initial_charge(self):
        _, battery, _ = initial_state()
        self.assertEqual(battery["current_charge_kwh"], BATTERY_INITIAL_CHARGE_KWH)
        self.assertEqual(battery["max_capacity_kwh"], BATTERY_CAPACITY_KWH)
        expected_reserve = BATTERY_CAPACITY_KWH * BATTERY_EMERGENCY_RESERVE_FRACTION
        self.assertAlmostEqual(battery["emergency_reserve_kwh"], expected_reserve)

    def test_history_has_all_expected_keys(self):
        _, _, history = initial_state()
        expected_keys = {
            "wind_ms", "temperature_c", "storm", "tau",
            "solar_generation_kw", "wind_generation_kw", "nuclear_generation_kw",
            "total_generation_kw", "total_consumption_kw",
            "battery_charge_kwh", "modes_summary", "alerts",
        }
        self.assertEqual(set(history.keys()), expected_keys)

    def test_history_lists_start_empty(self):
        _, _, history = initial_state()
        for key, value in history.items():
            self.assertEqual(value, [], f"history[{key!r}] should be empty")

    def test_returns_fresh_objects_each_call(self):
        c1, b1, h1 = initial_state()
        c2, b2, h2 = initial_state()
        c1["sol"] = 999
        b1["current_charge_kwh"] = 0
        h1["wind_ms"].append(42)
        self.assertEqual(c2["sol"], 0)
        self.assertEqual(b2["current_charge_kwh"], BATTERY_INITIAL_CHARGE_KWH)
        self.assertEqual(h2["wind_ms"], [])


if __name__ == "__main__":
    unittest.main()
