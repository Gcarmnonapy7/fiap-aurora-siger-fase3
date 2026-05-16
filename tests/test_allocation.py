"""Tests for the 4-stage allocation policy."""

import unittest

from colony.allocation import allocate_energy
from colony.constants import GENERATOR_TYPES
from colony.modules import MODULES, find_module
from colony.hierarchies import build_criticality_tree


def _reset_modes():
    """Puts every module back in 'adequate' before each test."""
    for m in MODULES:
        m["current_mode"] = "adequate"


class TestAllocation(unittest.TestCase):

    def setUp(self):
        _reset_modes()
        self.tree = build_criticality_tree()

    def test_abundant_supply_keeps_everyone_at_adequate_or_surplus(self):
        climate = {"temperature_c": 0}
        allocate_energy(self.tree, supply_kw=500.0, climate=climate)
        for m in MODULES:
            if m["type"] in GENERATOR_TYPES:
                self.assertEqual(m["current_mode"], "adequate")
                continue
            self.assertIn(m["current_mode"], ("adequate", "surplus"))

    def test_minimum_supply_preserves_vital(self):
        climate = {"temperature_c": -20}
        allocate_energy(self.tree, supply_kw=20.0, climate=climate)
        for vital_id in [1, 2, 3, 7]:
            self.assertNotEqual(find_module(vital_id)["current_mode"], "off")

    def test_low_supply_shuts_expansion_off(self):
        climate = {"temperature_c": -20}
        allocate_energy(self.tree, supply_kw=15.0, climate=climate)
        for exp_id in [9, 11, 12]:
            self.assertEqual(find_module(exp_id)["current_mode"], "off")

    def test_generators_never_downgraded(self):
        climate = {"temperature_c": 0}
        allocate_energy(self.tree, supply_kw=10.0, climate=climate)
        for gen_id in [4, 5, 13]:
            self.assertEqual(find_module(gen_id)["current_mode"], "adequate")

    def test_cost_includes_generators_own_consumption(self):
        """Policy must count generators' own consumption (4.5 kW total in
        'adequate': solar 1 + nuclear 3 + wind 0.5) when deciding fit.

        Scenario: consumers in 'adequate' sum exactly to supply, but the
        generators' own consumption tips over. At least one Expansion
        module must be downgraded.
        """
        climate = {"temperature_c": 0}
        # sum of consumers in "adequate" at 0°C (no thermal term):
        # 8+12+15+5+6+10+4+8+3+5 = 76 kW
        # with generators: +4.5 = 80.5 kW
        allocate_energy(self.tree, supply_kw=76.0, climate=climate)
        expansion_modes = [find_module(i)["current_mode"] for i in (9, 11, 12)]
        self.assertTrue(
            any(m in ("minimum", "off") for m in expansion_modes),
            f"Expected downgrade in Expansion, saw {expansion_modes}",
        )


if __name__ == "__main__":
    unittest.main()
