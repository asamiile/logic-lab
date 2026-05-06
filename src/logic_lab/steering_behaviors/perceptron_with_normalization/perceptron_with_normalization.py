import random as rand_module
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

perceptron: "Perceptron"
training = []
count = 0


def f(x: float) -> float:
    """The formula for a line: y = 0.5x + 1"""
    return 0.5 * x + 1


class Perceptron:
    def __init__(self, total_inputs: int, learning_rate: float) -> None:
        self.weights = [rand_module.uniform(-1, 1) for _ in range(total_inputs)]
        self.learning_constant = learning_rate

    def feedforward(self, inputs: list) -> int:
        """Return an output based on inputs."""
        total = sum(inputs[i] * self.weights[i] for i in range(len(self.weights)))
        return self.activate(total)

    def activate(self, total: float) -> int:
        """Activation function: return +1 or -1."""
        return 1 if total > 0 else -1

    def train(self, inputs: list, desired: int) -> None:
        """Train the network against known data."""
        guess = self.feedforward(inputs)
        error = desired - guess
        for i in range(len(self.weights)):
            self.weights[i] += error * inputs[i] * self.learning_constant


def setup() -> None:
    global perceptron, training, count
    py5.size(640, 240)

    perceptron = Perceptron(3, 0.0001)

    # Make 2,000 training data points
    for _ in range(2000):
        x = rand_module.uniform(-py5.width / 2, py5.width / 2)
        y = rand_module.uniform(-py5.height / 2, py5.height / 2)
        training.append([x, y, 1])

    count = 0
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global count, perceptron, training

    py5.background(255)

    # Re-orient canvas to match traditional Cartesian plane
    py5.push()
    py5.translate(py5.width / 2, py5.height / 2)
    py5.scale(1, -1)

    # Draw the line
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.line(-py5.width / 2, f(-py5.width / 2), py5.width / 2, f(py5.width / 2))

    # Get the current (x,y) of the training data
    x = training[count][0]
    y = training[count][1]

    # What is the desired output?
    desired = 1 if y > f(x) else -1

    # Train the perceptron
    perceptron.train(training[count], desired)

    # For animation, training one point at a time
    count = (count + 1) % len(training)

    # Draw all the points and color according to the output of the perceptron
    for data_point in training:
        guess = perceptron.feedforward(data_point)

        if guess > 0:
            py5.fill(127)
        else:
            py5.fill(255)

        py5.stroke_weight(1)
        py5.stroke(0)
        py5.circle(data_point[0], data_point[1], 8)

    py5.pop()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "perceptron_with_normalization_####.png"))


py5.run_sketch()
