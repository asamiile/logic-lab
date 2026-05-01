from pathlib import Path
import random as rand_module
import math

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Training data
data = [
    {"x": 0.99, "y": 0.02, "label": "right"},
    {"x": 0.76, "y": -0.1, "label": "right"},
    {"x": -1.0, "y": 0.12, "label": "left"},
    {"x": -0.9, "y": -0.1, "label": "left"},
    {"x": 0.02, "y": 0.98, "label": "down"},
    {"x": -0.2, "y": 0.75, "label": "down"},
    {"x": 0.01, "y": -0.9, "label": "up"},
    {"x": -0.1, "y": -0.8, "label": "up"},
]

classifier: "NeuralNetwork"
status = "training"
start = None
end = None


class NeuralNetwork:
    def __init__(self, input_size: int, hidden_size: int, output_size: int, learning_rate: float = 0.1) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.learning_rate = learning_rate
        self.labels = ["up", "down", "left", "right"]

        # Initialize weights randomly
        self.w1 = [[rand_module.gauss(0, 0.5) for _ in range(input_size)] for _ in range(hidden_size)]
        self.b1 = [rand_module.gauss(0, 0.5) for _ in range(hidden_size)]
        self.w2 = [[rand_module.gauss(0, 0.5) for _ in range(hidden_size)] for _ in range(output_size)]
        self.b2 = [rand_module.gauss(0, 0.5) for _ in range(output_size)]

    def sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + math.exp(-x))

    def sigmoid_derivative(self, x: float) -> float:
        return x * (1.0 - x)

    def forward(self, inputs: list) -> tuple:
        # Hidden layer
        self.hidden = []
        for i in range(self.hidden_size):
            sum_val = self.b1[i]
            for j in range(self.input_size):
                sum_val += inputs[j] * self.w1[i][j]
            self.hidden.append(self.sigmoid(sum_val))

        # Output layer
        self.output = []
        for i in range(self.output_size):
            sum_val = self.b2[i]
            for j in range(self.hidden_size):
                sum_val += self.hidden[j] * self.w2[i][j]
            self.output.append(self.sigmoid(sum_val))

        return self.output

    def backward(self, inputs: list, targets: list) -> None:
        # Output layer error
        output_errors = [targets[i] - self.output[i] for i in range(self.output_size)]

        # Output layer gradients
        output_deltas = [output_errors[i] * self.sigmoid_derivative(self.output[i]) for i in range(self.output_size)]

        # Hidden layer error
        hidden_errors = [0] * self.hidden_size
        for i in range(self.hidden_size):
            for j in range(self.output_size):
                hidden_errors[i] += output_deltas[j] * self.w2[j][i]

        # Hidden layer gradients
        hidden_deltas = [hidden_errors[i] * self.sigmoid_derivative(self.hidden[i]) for i in range(self.hidden_size)]

        # Update output layer weights and biases
        for i in range(self.output_size):
            self.b2[i] += self.learning_rate * output_deltas[i]
            for j in range(self.hidden_size):
                self.w2[i][j] += self.learning_rate * output_deltas[i] * self.hidden[j]

        # Update hidden layer weights and biases
        for i in range(self.hidden_size):
            self.b1[i] += self.learning_rate * hidden_deltas[i]
            for j in range(self.input_size):
                self.w1[i][j] += self.learning_rate * hidden_deltas[i] * inputs[j]

    def train(self, inputs: list, targets: list) -> None:
        self.forward(inputs)
        self.backward(inputs, targets)

    def classify(self, inputs: list) -> str:
        output = self.forward(inputs)
        max_idx = output.index(max(output))
        return self.labels[max_idx]


def setup() -> None:
    global classifier, status

    py5.size(640, 240)

    # Create and train classifier
    classifier = NeuralNetwork(2, 16, 4, learning_rate=0.5)

    # Normalize data
    inputs_data = []
    outputs_data = []

    for item in data:
        inputs_data.append([item["x"], item["y"]])
        # One-hot encoding for output
        output = [0, 0, 0, 0]
        label_idx = classifier.labels.index(item["label"])
        output[label_idx] = 1
        outputs_data.append(output)

    # Train for 200 epochs
    for epoch in range(200):
        for i in range(len(inputs_data)):
            classifier.train(inputs_data[i], outputs_data[i])

    status = "ready"
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global start, end

    py5.background(255)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text_size(64)
    py5.fill(0)
    py5.text(status, py5.width / 2, py5.height / 2)

    if start and end:
        py5.stroke_weight(8)
        py5.stroke(0)
        py5.line(start.x, start.y, end.x, end.y)


def mouse_pressed() -> None:
    global start
    start = py5.Py5Vector(py5.mouse_x, py5.mouse_y)


def mouse_dragged() -> None:
    global end
    end = py5.Py5Vector(py5.mouse_x, py5.mouse_y)


def mouse_released() -> None:
    global status, start, end

    if start and end:
        # Calculate direction vector
        dir_x = end.x - start.x
        dir_y = end.y - start.y
        length = math.sqrt(dir_x * dir_x + dir_y * dir_y)

        if length > 0:
            dir_x /= length
            dir_y /= length
            inputs = [dir_x, dir_y]
            status = classifier.classify(inputs)

    start = None
    end = None


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "gesture_classifier_####.png"))


py5.run_sketch()
