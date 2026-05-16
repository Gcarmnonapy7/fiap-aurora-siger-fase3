"""Tests for the analysis module (assignment item 1.4)."""

import os
import tempfile
import unittest

from colony.analysis import analyze_balance, summarize_history, write_log
from colony.simulator import run_simulation


class TestAnalyzeBalance(unittest.TestCase):

    def test_consumption_above_generation_is_risk(self):
        r = analyze_balance(generation_kw=40, consumption_kw=70)
        self.assertEqual(r["status"], "risk")
        self.assertIn("ALERTA", r["message"])
        self.assertEqual(r["delta_kw"], -30)

    def test_generation_clearly_above_consumption_is_surplus(self):
        r = analyze_balance(generation_kw=80, consumption_kw=30)
        self.assertEqual(r["status"], "surplus")
        self.assertIn("SUGESTÃO", r["message"])

    def test_close_to_balanced_is_balanced(self):
        r = analyze_balance(generation_kw=50, consumption_kw=49)
        self.assertEqual(r["status"], "balanced")

    def test_delta_is_difference(self):
        r = analyze_balance(generation_kw=100, consumption_kw=60)
        self.assertEqual(r["delta_kw"], 40)


class TestSummarizeHistory(unittest.TestCase):

    def test_summary_has_expected_keys(self):
        _, _, history = run_simulation(seed=42, horizon=24)
        s = summarize_history(history)
        for key in ("avg_generation_kw", "avg_consumption_kw",
                    "max_generation_kw", "min_generation_kw",
                    "storm_hours", "alert_hours", "total_steps"):
            self.assertIn(key, s)

    def test_total_steps_matches_horizon(self):
        _, _, history = run_simulation(seed=42, horizon=24)
        s = summarize_history(history)
        self.assertEqual(s["total_steps"], 24)

    def test_storm_hours_counts_non_clear(self):
        history = {
            "wind_ms": [0.0] * 4,
            "total_generation_kw": [10.0] * 4,
            "total_consumption_kw": [8.0] * 4,
            "storm": ["clear", "clear", "light", "moderate"],
            "alerts": [[], [], [], ["foo"]],
        }
        s = summarize_history(history)
        self.assertEqual(s["storm_hours"], 2)
        self.assertEqual(s["alert_hours"], 1)


class TestWriteLog(unittest.TestCase):

    def test_writes_a_readable_file(self):
        _, _, history = run_simulation(seed=42, horizon=5)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "colony_log.txt")
            write_log(history, path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertIn("sol", content.lower())
            for line_number in range(5):
                self.assertIn(f"step={line_number}", content)


if __name__ == "__main__":
    unittest.main()
