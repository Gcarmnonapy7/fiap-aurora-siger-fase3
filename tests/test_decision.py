"""Tests for the simple decision rules (assignment item 1.2)."""

import unittest

from colony.decision import evaluate_rules, priority_order


class TestRules(unittest.TestCase):

    def test_low_energy_triggers_consumption_reduction(self):
        actions = evaluate_rules({"energy_kw": 40, "consumption_kw": 50, "storm": "clear"})
        self.assertIn("ALERTA: reduzir consumo", actions)

    def test_low_energy_high_consumption_triggers_economy_mode(self):
        actions = evaluate_rules({"energy_kw": 40, "consumption_kw": 80, "storm": "clear"})
        self.assertIn("ATIVAR MODO ECONOMIA", actions)

    def test_storm_moderate_triggers_climate_alert(self):
        actions = evaluate_rules({"energy_kw": 200, "consumption_kw": 100, "storm": "moderate"})
        self.assertIn("ALERTA CLIMÁTICO: priorizar Vital e Sustento", actions)

    def test_storm_severe_triggers_climate_alert(self):
        actions = evaluate_rules({"energy_kw": 200, "consumption_kw": 100, "storm": "severe"})
        self.assertIn("ALERTA CLIMÁTICO: priorizar Vital e Sustento", actions)

    def test_storm_light_does_not_trigger_climate_alert(self):
        actions = evaluate_rules({"energy_kw": 200, "consumption_kw": 100, "storm": "light"})
        self.assertNotIn("ALERTA CLIMÁTICO: priorizar Vital e Sustento", actions)

    def test_consumption_exceeds_energy_emergency(self):
        actions = evaluate_rules({"energy_kw": 30, "consumption_kw": 80, "storm": "clear"})
        self.assertIn("EMERGÊNCIA ENERGÉTICA", actions)

    def test_healthy_state_returns_no_alerts(self):
        actions = evaluate_rules({"energy_kw": 200, "consumption_kw": 100, "storm": "clear"})
        self.assertEqual(actions, [])

    def test_combined_low_energy_and_storm(self):
        actions = evaluate_rules({"energy_kw": 30, "consumption_kw": 80, "storm": "severe"})
        self.assertIn("ALERTA: reduzir consumo", actions)
        self.assertIn("ATIVAR MODO ECONOMIA", actions)
        self.assertIn("EMERGÊNCIA ENERGÉTICA", actions)
        self.assertIn("ALERTA CLIMÁTICO: priorizar Vital e Sustento", actions)


class TestPriorityOrder(unittest.TestCase):

    def test_priority_order_is_vital_first(self):
        order = priority_order()
        self.assertEqual(order[0], "Vital")
        self.assertEqual(order[1], "Sustenance")
        self.assertEqual(order[2], "Expansion")


if __name__ == "__main__":
    unittest.main()
