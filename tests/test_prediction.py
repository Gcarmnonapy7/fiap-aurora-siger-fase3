"""Tests for the manual linear regression (assignment item 1.3)."""

import unittest

from colony.prediction import (
    linear_regression, predict, fit_wind_power_model, predict_next_wind_power,
)
from colony.simulator import run_simulation


class TestLinearRegression(unittest.TestCase):

    def test_assignment_example(self):
        """vento=[8,10,12], energia=[20,25,30] → reta y = 2.5x, prediz 11→27.5."""
        a, b = linear_regression([8, 10, 12], [20, 25, 30])
        self.assertAlmostEqual(a, 2.5, places=6)
        self.assertAlmostEqual(b, 0.0, places=6)
        self.assertAlmostEqual(predict(a, b, 11), 27.5, places=6)

    def test_perfect_line_recovers_coefficients(self):
        xs = [0, 1, 2, 3, 4, 5]
        ys = [3 + 2 * x for x in xs]
        a, b = linear_regression(xs, ys)
        self.assertAlmostEqual(a, 2.0, places=6)
        self.assertAlmostEqual(b, 3.0, places=6)

    def test_noisy_data_approximates_true_slope(self):
        xs = [1, 2, 3, 4, 5, 6, 7, 8]
        # y = 1.5x + 0.5 com pequeno ruído determinístico
        ys = [1.5 * x + 0.5 + (0.1 if i % 2 else -0.1) for i, x in enumerate(xs)]
        a, b = linear_regression(xs, ys)
        self.assertAlmostEqual(a, 1.5, places=1)
        self.assertAlmostEqual(b, 0.5, places=1)

    def test_empty_lists_raise(self):
        with self.assertRaises(ValueError):
            linear_regression([], [])

    def test_single_point_raises(self):
        with self.assertRaises(ValueError):
            linear_regression([5.0], [10.0])

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            linear_regression([1, 2, 3], [10, 20])

    def test_constant_xs_raise(self):
        """All xs equal: variance is 0, slope undefined."""
        with self.assertRaises(ValueError):
            linear_regression([5, 5, 5, 5], [1, 2, 3, 4])


class TestPredict(unittest.TestCase):

    def test_predict_is_linear(self):
        self.assertEqual(predict(2.0, 3.0, 5.0), 13.0)
        self.assertEqual(predict(-1.0, 10.0, 4.0), 6.0)


class TestWindPowerModel(unittest.TestCase):

    def test_fit_on_real_history_returns_positive_slope(self):
        """A reta vento→eólica deve ter a > 0 (mais vento, mais energia)."""
        _, _, history = run_simulation(seed=42)
        a, b = fit_wind_power_model(history)
        self.assertGreater(a, 0)

    def test_predict_next_wind_power_at_zero_wind_is_clamped_or_low(self):
        """A regressão é treinada apenas em pontos com geração > 0 (cut-in
        descartado), então extrapolar para vento=0 pode dar valor negativo —
        o predict puro não clampa, mas o helper deve. Validamos não-negativo."""
        _, _, history = run_simulation(seed=42)
        pred = predict_next_wind_power(history, wind_forecast_ms=0.0)
        self.assertGreaterEqual(pred, 0.0)

    def test_predict_next_wind_power_grows_with_wind(self):
        _, _, history = run_simulation(seed=42)
        low = predict_next_wind_power(history, wind_forecast_ms=5.0)
        high = predict_next_wind_power(history, wind_forecast_ms=12.0)
        self.assertGreater(high, low)

    def test_fit_raises_when_history_has_no_wind_generation(self):
        """If wind_generation_kw is all zeros, can't fit (no signal)."""
        empty_history = {
            "wind_ms": [0.0] * 10,
            "wind_generation_kw": [0.0] * 10,
        }
        with self.assertRaises(ValueError):
            fit_wind_power_model(empty_history)


if __name__ == "__main__":
    unittest.main()
