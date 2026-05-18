class LinearRegression:
    def __init__(self):
        self.slope = 0.0
        self.intercept = 0.0

    def fit(self, xs: list, ys: list):
        n = len(xs)
        if n < 2:
            self.slope = 0.0
            self.intercept = ys[0] if n == 1 else 0.0
            return

        x_mean = sum(xs) / n
        y_mean = sum(ys) / n

        numerator   = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        denominator = sum((x - x_mean) ** 2 for x in xs)

        self.slope     = numerator / denominator if denominator != 0 else 0.0
        self.intercept = y_mean - self.slope * x_mean

    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept
