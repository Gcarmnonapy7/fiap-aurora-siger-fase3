class LinearRegression:

    def __init__(self, learning_rate: float = 0.01, n_iterations: int = 1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = [0.0]
        self.bias = 0.0
        self.losses = []

    @property
    def slope(self) -> float:
        return self.weights[0] if self.weights else 0.0

    def fit(self, X, y):
        if not X or len(X) < 2:
            return self

        # Handle 1D input
        if not isinstance(X[0], list):
            X = [[x] for x in X]

        n_samples, n_features = len(X), len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0

        _GRAD_CLIP = 1.0

        for interaction in range(self.n_iterations):

            y_hat = []
            for i in range(n_samples):
                prediction = sum(self.weights[j] * X[i][j] for j in range(n_features)) + self.bias
                y_hat.append(prediction)

            dw = [0.0] * n_features
            db = 0.0

            for i in range(n_samples):
                error = y_hat[i] - y[i]
                for j in range(n_features):
                    dw[j] += error * X[i][j]
                db += error

            dw = [max(-_GRAD_CLIP, min(_GRAD_CLIP, d / n_samples)) for d in dw]
            db = max(-_GRAD_CLIP, min(_GRAD_CLIP, db / n_samples))

            self.weights = [self.weights[j] - self.learning_rate * dw[j] for j in range(n_features)]
            self.bias -= self.learning_rate * db

            # stop early if weights have diverged
            if any(w != w or abs(w) == float('inf') for w in self.weights):
                self.weights = [0.0] * n_features
                self.bias = 0.0
                break

            if interaction % 100 == 0:
                mse = Metrics.mean_squared_error(y, y_hat)
                self.losses.append(mse)

        return self

    def predict(self, X):
        # Handle scalar input — return a single float
        if isinstance(X, (int, float)):
            result = self.weights[0] * X + self.bias
            return result

        # Handle 1D list input
        if not isinstance(X[0], list):
            X = [[x] for x in X]

        n_samples, n_features = len(X), len(X[0])
        y_pred = []
        for i in range(n_samples):
            prediction = sum(self.weights[j] * X[i][j] for j in range(n_features)) + self.bias
            y_pred.append(prediction)

        return y_pred

    def get_params(self) -> dict:
        return {"weights": self.weights, "bias": self.bias, "losses": self.losses}


class Metrics:

    @staticmethod
    def mean_squared_error(y_true, y_pred):
        n_samples = len(y_true)
        mse = sum((y_true[i] - y_pred[i]) ** 2 for i in range(n_samples)) / n_samples
        return mse

    @staticmethod
    def r2_score(y_true, y_pred):
        n_samples = len(y_true)
        mean_y = sum(y_true) / n_samples
        ss_total = sum((y_true[i] - mean_y) ** 2 for i in range(n_samples))
        ss_residual = sum((y_true[i] - y_pred[i]) ** 2 for i in range(n_samples))
        return 1 - (ss_residual / ss_total) if ss_total != 0 else 0.0

    @staticmethod
    def mean_absolute_error(y_true, y_pred):
        n_samples = len(y_true)
        mae = sum(abs(y_true[i] - y_pred[i]) for i in range(n_samples)) / n_samples
        return mae
