"""Manual linear regression — covers item 1.3 of the official assignment.

Implements y = a*x + b with the closed-form OLS estimator, by hand:

    a = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)
    b = ȳ - a*x̄

No numpy / sklearn — only `sum()`, `len()` and a `for` loop, as required
by the assignment.

Specialized to the colony: trains over `history["wind_ms"]` vs
`history["wind_generation_kw"]` and predicts wind power for any future
wind forecast.
"""


def linear_regression(xs, ys):
    """Returns (a, b) such that y ≈ a*x + b minimizes the sum of squared errors.

    Raises ValueError on degenerate input: empty/single point, mismatched
    lengths, or constant xs (variance = 0).
    """
    n = len(xs)
    if n != len(ys):
        raise ValueError(f"xs and ys must have the same length ({n} vs {len(ys)})")
    if n < 2:
        raise ValueError("at least 2 points required to fit a line")

    x_mean = sum(xs) / n
    y_mean = sum(ys) / n

    numerator = 0.0
    denominator = 0.0
    for x, y in zip(xs, ys):
        dx = x - x_mean
        numerator += dx * (y - y_mean)
        denominator += dx * dx

    if denominator == 0:
        raise ValueError("xs must vary (variance is 0)")

    a = numerator / denominator
    b = y_mean - a * x_mean
    return a, b


def predict(a, b, x):
    """y = a*x + b."""
    return a * x + b


def fit_wind_power_model(history):
    """Trains the wind→power model from the simulator history.

    Filters out points where wind_generation_kw == 0 (below cut-in, no
    useful signal about the linear region), then runs linear_regression.
    """
    pairs = [
        (v, p) for v, p in zip(history["wind_ms"], history["wind_generation_kw"])
        if p > 0
    ]
    if len(pairs) < 2:
        raise ValueError("not enough non-zero wind generation points to fit a model")
    xs = [v for v, _ in pairs]
    ys = [p for _, p in pairs]
    return linear_regression(xs, ys)


def wind_power_forecast(a, b, wind_ms):
    """Predicts wind power for `wind_ms` using the fitted line, clamped to ≥ 0.

    The clamp encodes domain knowledge: physical wind power has a cut-in
    around 3 m/s, so values below the linear region produce negative
    predictions that must round to zero.
    """
    return max(0.0, predict(a, b, wind_ms))


def predict_next_wind_power(history, wind_forecast_ms):
    """Fits and forecasts in a single call. Convenience wrapper."""
    a, b = fit_wind_power_model(history)
    return wind_power_forecast(a, b, wind_forecast_ms)
