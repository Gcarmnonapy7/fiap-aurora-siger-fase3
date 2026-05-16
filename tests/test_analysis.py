"""Tests for the analysis module (assignment item 1.4)."""

import os
import tempfile
import unittest

from colony.analysis import (
    analyze_balance, summarize_history, write_log,
    aggregate_by_sol, status_distribution,
    generation_breakdown, critical_moments,
)
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
            write_log(history, path, seed=42)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertIn("sol", content.lower())
            for line_number in range(5):
                self.assertIn(f"step={line_number}", content)

    def test_header_contains_seed_and_hour_count(self):
        _, _, history = run_simulation(seed=42, horizon=3)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "log.txt")
            write_log(history, path, seed=42)
            with open(path) as f:
                content = f.read()
            self.assertIn("seed=42", content)
            self.assertIn("3 hours", content)
            self.assertIn("Aurora Siger", content)

    def test_random_seed_renders_as_random(self):
        _, _, history = run_simulation(seed=1, horizon=2)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "log.txt")
            write_log(history, path, seed=None)
            with open(path) as f:
                self.assertIn("seed=random", f.read())

    def test_subsequent_calls_append_instead_of_overwrite(self):
        _, _, history_a = run_simulation(seed=1, horizon=2)
        _, _, history_b = run_simulation(seed=2, horizon=2)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "log.txt")
            write_log(history_a, path, seed=1)
            write_log(history_b, path, seed=2)
            with open(path) as f:
                content = f.read()
            self.assertIn("seed=1", content)
            self.assertIn("seed=2", content)
            # Two header lines (===) → two blocks preserved.
            self.assertEqual(content.count("=== Aurora Siger"), 2)

    def test_creates_parent_directory_when_missing(self):
        _, _, history = run_simulation(seed=42, horizon=2)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fresh_dir", "log.txt")
            self.assertFalse(os.path.isdir(os.path.dirname(path)))
            write_log(history, path, seed=42)
            self.assertTrue(os.path.exists(path))


class TestAggregateBySol(unittest.TestCase):

    def test_returns_one_row_per_sol(self):
        _, _, history = run_simulation(seed=42, horizon=72)  # 3 sols
        sols = aggregate_by_sol(history)
        self.assertEqual(len(sols), 3)
        for k, row in enumerate(sols):
            self.assertEqual(row["sol"], k)
            self.assertEqual(row["hours"], 24)

    def test_partial_sol_at_the_end(self):
        _, _, history = run_simulation(seed=42, horizon=30)  # 1 sol + 6h
        sols = aggregate_by_sol(history)
        self.assertEqual(len(sols), 2)
        self.assertEqual(sols[0]["hours"], 24)
        self.assertEqual(sols[1]["hours"], 6)

    def test_avg_delta_matches_avg_generation_minus_avg_consumption(self):
        _, _, history = run_simulation(seed=42, horizon=24)
        sols = aggregate_by_sol(history)
        row = sols[0]
        self.assertAlmostEqual(
            row["avg_delta_kw"],
            row["avg_generation_kw"] - row["avg_consumption_kw"],
            places=6,
        )

    def test_regime_orders_by_severity(self):
        history = {
            "total_generation_kw": [100.0] * 24,
            "total_consumption_kw": [80.0] * 24,
            "storm": ["light"] * 8 + ["clear"] * 8 + ["moderate"] * 8,
        }
        sols = aggregate_by_sol(history)
        self.assertEqual(sols[0]["regime"], "clear/light/moderate")

    def test_regime_collapses_when_uniform(self):
        history = {
            "total_generation_kw": [100.0] * 24,
            "total_consumption_kw": [80.0] * 24,
            "storm": ["moderate"] * 24,
        }
        sols = aggregate_by_sol(history)
        self.assertEqual(sols[0]["regime"], "moderate")


class TestStatusDistribution(unittest.TestCase):

    def test_sums_to_total_steps(self):
        _, _, history = run_simulation(seed=42, horizon=24)
        dist = status_distribution(history)
        self.assertEqual(sum(dist.values()), 24)

    def test_categories_present(self):
        _, _, history = run_simulation(seed=42, horizon=24)
        dist = status_distribution(history)
        self.assertEqual(set(dist.keys()), {"risk", "balanced", "surplus"})

    def test_handcrafted_distribution(self):
        history = {
            "total_generation_kw": [10.0, 100.0, 50.0],
            "total_consumption_kw": [20.0, 30.0, 49.5],
        }
        # row 0: gen<con → risk; row 1: 100 > 30*1.1 → surplus; row 2: balanced
        dist = status_distribution(history)
        self.assertEqual(dist, {"risk": 1, "balanced": 1, "surplus": 1})


class TestGenerationBreakdown(unittest.TestCase):

    def test_shares_sum_to_one(self):
        _, _, history = run_simulation(seed=42, horizon=48)
        bd = generation_breakdown(history)
        total_share = bd["solar"]["share"] + bd["wind"]["share"] + bd["nuclear"]["share"]
        self.assertAlmostEqual(total_share, 1.0, places=6)

    def test_nuclear_dominates_in_typical_run(self):
        """Nuclear é 80 kW constante; solar e eólica são intermitentes — nuclear domina."""
        _, _, history = run_simulation(seed=42, horizon=24)
        bd = generation_breakdown(history)
        self.assertGreater(bd["nuclear"]["share"], bd["solar"]["share"])
        self.assertGreater(bd["nuclear"]["share"], bd["wind"]["share"])

    def test_empty_history_returns_zero_shares(self):
        history = {
            "total_generation_kw": [],
            "solar_generation_kw": [],
            "wind_generation_kw": [],
            "nuclear_generation_kw": [],
        }
        bd = generation_breakdown(history)
        self.assertEqual(bd["solar"]["share"], 0.0)


class TestCriticalMoments(unittest.TestCase):

    def test_worst_deficit_minimizes_delta(self):
        history = {
            "total_generation_kw": [10.0, 100.0, 50.0],
            "total_consumption_kw": [60.0, 30.0, 50.0],
            "storm": ["clear", "light", "moderate"],
        }
        # deltas: -50, +70, 0
        cm = critical_moments(history)
        self.assertEqual(cm["worst_deficit"]["sol"], 0)
        self.assertEqual(cm["worst_deficit"]["hour"], 0)
        self.assertAlmostEqual(cm["worst_deficit"]["delta_kw"], -50.0)
        self.assertEqual(cm["worst_deficit"]["storm"], "clear")

    def test_biggest_surplus_maximizes_delta(self):
        history = {
            "total_generation_kw": [10.0, 100.0, 50.0],
            "total_consumption_kw": [60.0, 30.0, 50.0],
            "storm": ["clear", "light", "moderate"],
        }
        cm = critical_moments(history)
        self.assertEqual(cm["biggest_surplus"]["sol"], 0)
        self.assertEqual(cm["biggest_surplus"]["hour"], 1)
        self.assertAlmostEqual(cm["biggest_surplus"]["delta_kw"], 70.0)

    def test_sol_and_hour_decomposition(self):
        # idx 30 → sol 1, hour 6
        history = {
            "total_generation_kw": [50.0] * 30 + [0.0] + [50.0] * 5,
            "total_consumption_kw": [50.0] * 30 + [100.0] + [50.0] * 5,
            "storm": ["clear"] * 36,
        }
        cm = critical_moments(history)
        self.assertEqual(cm["worst_deficit"]["sol"], 1)
        self.assertEqual(cm["worst_deficit"]["hour"], 6)


if __name__ == "__main__":
    unittest.main()
