import numpy as np

class MLP:
    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.01):
        # Xavier initialization for better gradient flow
        self.weights1 = np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / input_size)
        self.weights2 = np.random.randn(hidden_size, output_size) * np.sqrt(2.0 / hidden_size)
        self.bias1 = np.zeros((1, hidden_size))
        self.bias2 = np.zeros((1, output_size))
        self.learning_rate = learning_rate
        
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def sigmoid_derivative(self, sigmoid_output):
        return sigmoid_output * (1 - sigmoid_output)
    
    def forward(self, X):
        """Forward pass through the network"""
        self.layer1 = X.dot(self.weights1) + self.bias1
        self.activation1 = self.sigmoid(self.layer1)
        self.layer2 = self.activation1.dot(self.weights2) + self.bias2
        self.activation2 = self.sigmoid(self.layer2)
        return self.activation2
    
    def backward(self, X, y, output):
        """Backward pass to update weights"""
        # Calculate gradients
        self.output_error = y - output
        self.output_delta = self.output_error * self.sigmoid_derivative(self.activation2)
        
        # Hidden layer gradients
        self.hidden_error = self.output_delta.dot(self.weights2.T)
        self.hidden_delta = self.hidden_error * self.sigmoid_derivative(self.activation1)
        
        # Update weights and biases
        self.weights2 += self.activation1.T.dot(self.output_delta) * self.learning_rate
        self.bias2 += np.sum(self.output_delta, axis=0, keepdims=True) * self.learning_rate
        self.weights1 += X.T.dot(self.hidden_delta) * self.learning_rate
        self.bias1 += np.sum(self.hidden_delta, axis=0, keepdims=True) * self.learning_rate
            
    def train(self, X, y, epochs=10000, verbose=True):
        """Train the network"""
        best_accuracy = 0
        for epoch in range(epochs):
            # Forward pass
            output = self.forward(X)
            
            # Backward pass
            self.backward(X, y, output)
            
            # Dynamic learning rate adjustment
            if epoch % 1000 == 0:
                self.learning_rate = max(self.learning_rate * 0.95, 1e-6) # Reduce learning rate over time
            
            # Calculate and print metrics
            if verbose:
                metrics = self.evaluate(X, y)
                loss = np.mean(np.square(y - output))
                print(f"Epoch {epoch}, Loss: {loss:.4f}, Accuracy: {metrics['accuracy']:.4f}")
                
                # Early stopping if accuracy is not improving
                if metrics['accuracy'] > best_accuracy:
                    best_accuracy = metrics['accuracy']
    
    def predict(self, X):
        """Make predictions"""
        output = self.forward(X)
        return (output > 0.5).astype(int)
    
    def evaluate(self, X, y):
        """
        Evaluate the model's performance using accuracy, precision, recall, and F1-score.
        
        Parameters:
            X (numpy.ndarray): Input features.
            y (numpy.ndarray): True labels.
        """
        # Make predictions
        predictions = self.predict(X)
        
        # Flatten predictions and true labels
        predictions = predictions.flatten()
        y = y.flatten()
        
        # Calculate True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN)
        TP = np.sum((predictions == 1) & (y == 1))
        FP = np.sum((predictions == 1) & (y == 0))
        TN = np.sum((predictions == 0) & (y == 0))
        FN = np.sum((predictions == 0) & (y == 1))
        
        accuracy = (TP + TN) / (TP + FP + TN + FN)
        
        # Handle division by zero for precision, recall, and F1-score
        precision = TP / (TP + FP) if (TP + FP) != 0 else 0
        recall = TP / (TP + FN) if (TP + FN) != 0 else 0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }


def preprocess_data(data, train_ratio=0.8):
    """Preprocess mushroom data and split into train/test sets"""
    encoding_dicts = {
        'class': {'e': 0, 'p': 1},
        'cap-shape': {'b': 0, 'c': 1, 'x': 2, 'f': 3, 'k': 4, 's': 5},
        'cap-surface': {'f': 0, 'g': 1, 'y': 2, 's': 3},
        'cap-color': {'n': 0, 'b': 1, 'c': 2, 'g': 3, 'r': 4, 'p': 5, 'u': 6, 'e': 7, 'w': 8, 'y': 9},
        'bruises': {'t': 0, 'f': 1},
        'odor': {'a': 0, 'l': 1, 'c': 2, 'y': 3, 'f': 4, 'm': 5, 'n': 6, 'p': 7, 's': 8},
        'gill-attachment': {'a': 0, 'd': 1, 'f': 2, 'n': 3},
        'gill-spacing': {'c': 0, 'w': 1, 'd': 2},
        'gill-size': {'b': 0, 'n': 1},
        'gill-color': {'k': 0, 'n': 1, 'b': 2, 'h': 3, 'g': 4, 'r': 5, 'o': 6, 'p': 7, 'u': 8, 'e': 9, 'w': 10, 'y': 11},
        'stalk-shape': {'e': 0, 't': 1},
        'stalk-surface-above-ring': {'f': 0, 'y': 1, 'k': 2, 's': 3},
        'stalk-surface-below-ring': {'f': 0, 'y': 1, 'k': 2, 's': 3},
        'stalk-color-above-ring': {'n': 0, 'b': 1, 'c': 2, 'g': 3, 'o': 4, 'p': 5, 'e': 6, 'w': 7, 'y': 8},
        'stalk-color-below-ring': {'n': 0, 'b': 1, 'c': 2, 'g': 3, 'o': 4, 'p': 5, 'e': 6, 'w': 7, 'y': 8},
        'veil-type': {'p': 0, 'u': 1},
        'veil-color': {'n': 0, 'o': 1, 'w': 2, 'y': 3},
        'ring-number': {'n': 0, 'o': 1, 't': 2},
        'ring-type': {'c': 0, 'e': 1, 'f': 2, 'l': 3, 'n': 4, 'p': 5, 's': 6, 'z': 7},
        'spore-print-color': {'k': 0, 'n': 1, 'b': 2, 'h': 3, 'r': 4, 'o': 5, 'u': 6, 'w': 7, 'y': 8},
        'population': {'a': 0, 'c': 1, 'n': 2, 's': 3, 'v': 4, 'y': 5},
        'habitat': {'g': 0, 'l': 1, 'm': 2, 'p': 3, 'u': 4, 'w': 5, 'd': 6}
    }
    
    # Parse data lines
    X_data = []
    y_data = []
    
    for line in data.strip().split('\n'):
        features = line.strip().split(',')

        # Extract class (target)
        target_class = encoding_dicts['class'][features[0]]
        
        # Extract features and convert to one-hot encoding
        feature_vector = []
        for i, feature in enumerate(features[1:], 1):
            feature_key = list(encoding_dicts.keys())[i]
            try:
                # Get the encoded value for the feature
                encoded_value = encoding_dicts[feature_key][feature]
                
                # one-hot coding maybe!!!!!!!!!!
                feature_vector.append(encoded_value)
            except KeyError:
                # Handle unknown feature values
                print(f"Warning: Unknown value '{feature}' for feature '{feature_key}'")
                feature_vector.append(0)  # Default to 0 for unknown values
                
        X_data.append(feature_vector)
        y_data.append(target_class)
    
    # Convert to numpy arrays
    X = np.array(X_data, dtype=float)
    y = np.array(y_data, dtype=float).reshape(-1, 1)
    
    # Normalize data (important for neural networks)
    X = (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-8)
    
    # Split data into training and testing sets
    n_samples = len(X)
    indices = np.random.permutation(n_samples)
    train_size = int(n_samples * train_ratio)
    np.random.shuffle(indices)

    train_indices = indices[:train_size]
    test_indices = indices[train_size:]
    
    X_train, y_train = X[train_indices], y[train_indices]
    X_test, y_test = X[test_indices], y[test_indices]
    
    return X_train, y_train, X_test, y_test, X, y

def run_mushroom_classification(data, hidden_size=8, learning_rate=0.01, epochs=10):
    """Run the mushroom classification model"""
    # Preprocess data
    X_train, y_train, X_test, y_test, _, _ = preprocess_data(data)
    
    # Get input size from data
    input_size = X_train.shape[1]
    output_size = 1  # Binary classification
    
    # Initialize and train the model
    model = MLP(input_size, hidden_size, output_size, learning_rate)
    print("Training model...")
    model.train(X_train, y_train, epochs=epochs)
    
    # Evaluate on test set
    metrics = model.evaluate(X_test, y_test)
    print("\nTest Set Results:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1-Score: {metrics['f1_score']:.4f}")
    
    return model


if __name__ == "__main__":
    with open('processed.data', 'r') as f:
        mushroom_data = f.read()

    model = run_mushroom_classification(mushroom_data)