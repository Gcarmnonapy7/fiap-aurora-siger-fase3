class LinearRegreession:
    
    def __init__(self,learning_rate: float = 0.01, n_iterations: int = 1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = 0.0
        self.bias = 0.0
        self.losses = [] # for tracking the model's losses (MSE for loss)     


    def fit(self, X,y):
        """
        Generating the fitting method with only built-in functions and no libraries, using the gradient descent algorithm.
        X is the list of features and y is the list of target values.
        The method will update the weights and bias of the model to minimize the mean squared error between the predicted values and the actual target values. 
        The losses will be stored in a list for tracking the model's performance over iterations.
        """
        
        n_samples, n_features = len(X), len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0
        
        for interaction in range(self.n_iterations):
            
            y_hat = []
            
            for i in range(n_samples):
                prediction = sum(self.weights[j] * X[i][j] for j in range(n_features) + self.bias)
                y_hat.append(prediction)
                
            # computing the gradients
            
            dw = [0.0] * n_features
            db = 0.0
            
            for i in range(n_samples):
                error = y_hat[i] - y[i]
                
                # Gradient for each weight
                for j in range(n_features):
                    dw[j] += error * X[i][j]
                    
                    db += error
                    
            # average for the gradients
            dw = [d / n_samples for d in dw]
            db = db / n_samples
            
            # update the weights and bias
            self.weights = [self.weights[j] - self.learning_rate * dw[j] for j in range(n_features)]
            self.bias -= self.learning_rate * db
            
            # calculate the loss and store it
            
            if interaction % 100 == 0: # calculate the loss every 100 iterations
                mse = Metrics.mean_squared_error(y, y_hat)
                self.losses.append(mse)
                print(f"Iteration {interaction}, MSE: {mse}")
        
        return self
            
    def predict(self,X) :
        """
        Make predictions on new data.
        
        Args:
            X: Features to predict on (list or list of lists) ==> please put the test data in the same format as the training data (list of lists)
            
        Returns:
            List of predictions
        """
        
        # Handle 1D input 
        
        if not isinstance(X[0], list):
            X = [[x] for x in X]
            
        n_samples, n_features = len(X), len(X[0])
        y_pred = []
        
        for i in range(n_samples):
            prediction = sum(self.weights[j] * X[i][j] for j in range(n_features)) + self.bias
            y_pred.append(prediction)
            
        return y_pred
            
            
    def get_params(self) -> dict:
        """
        Return the model's parameters (weights and bias)
        """
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
        
        r2 = 1 - (ss_residual / ss_total) if ss_total != 0 else 0.0
        return r2
    
    @staticmethod
    def mean_absolute_error(y_true, y_pred):
        n_samples = len(y_true)
        mae = sum(abs(y_true[i] - y_pred[i]) for i in range(n_samples)) / n_samples
        return mae
        