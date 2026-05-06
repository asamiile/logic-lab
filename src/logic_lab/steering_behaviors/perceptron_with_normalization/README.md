# Perceptron with Normalization

```bash
uv run python steering_behaviors/perceptron_with_normalization/perceptron_with_normalization.py
```

- Simple perceptron neural network learning to classify points above or below a line
- The perceptron learns using the perceptron learning rule
- 2,000 training data points are generated and used to train the network one at a time
- The line is defined as y = 0.5x + 1
- Points are colored based on the perceptron's current classification:
  - **Gray** (127): Perceptron predicts above the line (+1)
  - **White** (255): Perceptron predicts below the line (-1)
- The black line shows the actual decision boundary the perceptron should learn
- Over time, the perceptron learns to better classify the points
- Press `s` to save a screenshot to `steering_behaviors/perceptron_with_normalization/screenshots/`

## How it works

1. **Perceptron architecture**:
   - 3 inputs: x, y, and bias (1)
   - Weights initialized randomly between -1 and 1
   - Learning rate: 0.0001

2. **Feedforward**:
   - Computes: sum = (x × w₀) + (y × w₁) + (1 × w₂)
   - Activation: returns +1 if sum > 0, else -1

3. **Training**:
   - Error = desired output - predicted output
   - Updates each weight: w = w + (error × input × learning_rate)
   - One training point per frame for smooth animation

4. **Learning dynamics**:
   - Initially, perceptron has no useful weights (random classification)
   - As training progresses, weights converge toward the decision boundary
   - Points gradually move to their correct colors
   - The perceptron learns a linear decision boundary using the Hebbian learning rule

This example demonstrates how simple neural networks can learn from data through iterative weight adjustment.
