"""Tests for the consumption model (base + thermal term)."""

import unittest

from colony.consumption import heating_consumption_kw, current_consumption_kw
from colony.modules import find_module


class TestHeating(unittest.TestCase):

    def test_module_without_thermal_factor_does_not_heat(self):
        # ISRU has thermal_factor = 0
        self.assertEqual(heating_consumption_kw(external_temperature=-70, thermal_factor=0.0), 0)

    def test_habitat_at_minus_70_within_gain_envelope(self):
        # thermal_factor = 1.0 (Habitat)
        # Q_loss = 0.15 * 250 * 90 = 3375 W; gain 4000*1.0 = 4000; clamp 0
        c = heating_consumption_kw(external_temperature=-70, thermal_factor=1.0)
        self.assertEqual(c, 0)

    def test_habitat_at_minus_90_consumes(self):
        # T_target=20, ΔT=110, Q_loss=0.15*250*110=4125 W; gain 4000; net 125 W; /0.95 ≈ 131 W ≈ 0.131 kW
        c = heating_consumption_kw(external_temperature=-90, thermal_factor=1.0)
        self.assertGreater(c, 0)
        self.assertAlmostEqual(c, 0.131, places=2)

    def test_temperature_above_target_does_not_heat(self):
        c = heating_consumption_kw(external_temperature=25, thermal_factor=1.0)
        self.assertEqual(c, 0)


class TestCurrentConsumption(unittest.TestCase):

    def test_adequate_mode_no_thermal(self):
        command = find_module(1)  # thermal_factor=0, consumption[adequate]=8
        command["current_mode"] = "adequate"
        climate = {"temperature_c": -70}
        self.assertEqual(current_consumption_kw(command, climate), 8)

    def test_off_mode_with_thermal_floor_clamps_zero(self):
        workshop = find_module(11)
        workshop["current_mode"] = "off"
        # thermal_factor = 0.2; even off it heats — at -50°C still clamps to 0
        climate = {"temperature_c": -50}
        self.assertEqual(current_consumption_kw(workshop, climate), 0)


if __name__ == "__main__":
    unittest.main()
