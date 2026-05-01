# Gesture Classifier - Neural Network

```bash
uv run python simulation/gesture_classifier/gesture_classifier.py
```

- Neural network trained to classify directional gestures (up, down, left, right)
- Uses a simple feedforward network with one hidden layer (2 inputs → 16 hidden → 4 outputs)
- Trained on 8 labeled examples of directional vectors normalized to unit length
- Trained for 200 epochs using backpropagation
- Draw gestures on the canvas by dragging the mouse
- The network classifies your gesture and displays the result
- Press `s` to save a screenshot to `simulation/gesture_classifier/screenshots/`

## How it works

1. **Training data**: 8 labeled examples
   - "right": vectors pointing right (x > 0.7, y near 0)
   - "left": vectors pointing left (x < -0.8, y near 0)
   - "down": vectors pointing down (x near 0, y > 0.7)
   - "up": vectors pointing up (x near 0, y < -0.8)

2. **Network architecture**:
   - Input layer: 2 nodes (x, y normalized direction)
   - Hidden layer: 16 nodes with sigmoid activation
   - Output layer: 4 nodes with sigmoid activation (one per class)

3. **Training**:
   - 200 epochs of backpropagation
   - Learning rate: 0.5
   - Data is normalized (input vectors are unit length)
   - One-hot encoding for output labels

4. **Usage**:
   - Click and drag to draw a gesture
   - Release the mouse to classify the direction
   - The network computes the direction vector, normalizes it, and classifies it
   - Result is displayed on screen

This example demonstrates how neural networks can learn to classify patterns from limited training data using backpropagation.
