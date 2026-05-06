from pathlib import Path
import random as rand_module
import math
import copy

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

creatures = []
glow: "Glow"
time_multiplier = 1
life_span = 250
life_counter = 0
generations = 0


class NeuralNetwork:
    def __init__(self, input_size: int = 5, hidden_size: int = 8, output_size: int = 2) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.w1 = [[rand_module.gauss(0, 0.5) for _ in range(input_size)] for _ in range(hidden_size)]
        self.b1 = [rand_module.gauss(0, 0.5) for _ in range(hidden_size)]
        self.w2 = [[rand_module.gauss(0, 0.5) for _ in range(hidden_size)] for _ in range(output_size)]
        self.b2 = [rand_module.gauss(0, 0.5) for _ in range(output_size)]

    def sigmoid(self, x: float) -> float:
        try:
            return 1.0 / (1.0 + math.exp(-x))
        except:
            return 0 if x < 0 else 1

    def feedforward(self, inputs: list) -> list:
        hidden = []
        for i in range(self.hidden_size):
            sum_val = self.b1[i]
            for j in range(self.input_size):
                sum_val += inputs[j] * self.w1[i][j]
            hidden.append(self.sigmoid(sum_val))

        output = []
        for i in range(self.output_size):
            sum_val = self.b2[i]
            for j in range(self.hidden_size):
                sum_val += hidden[j] * self.w2[i][j]
            output.append(self.sigmoid(sum_val))

        return output

    def copy(self) -> "NeuralNetwork":
        nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        nn.w1 = copy.deepcopy(self.w1)
        nn.b1 = copy.deepcopy(self.b1)
        nn.w2 = copy.deepcopy(self.w2)
        nn.b2 = copy.deepcopy(self.b2)
        return nn

    def crossover(self, partner: "NeuralNetwork") -> "NeuralNetwork":
        child = self.copy()
        for i in range(self.hidden_size):
            if rand_module.random() < 0.5:
                child.b1[i] = partner.b1[i]
            for j in range(self.input_size):
                if rand_module.random() < 0.5:
                    child.w1[i][j] = partner.w1[i][j]

        for i in range(self.output_size):
            if rand_module.random() < 0.5:
                child.b2[i] = partner.b2[i]
            for j in range(self.hidden_size):
                if rand_module.random() < 0.5:
                    child.w2[i][j] = partner.w2[i][j]

        return child

    def mutate(self, mutation_rate: float) -> None:
        for i in range(self.hidden_size):
            if rand_module.random() < mutation_rate:
                self.b1[i] += rand_module.gauss(0, 0.1)
            for j in range(self.input_size):
                if rand_module.random() < mutation_rate:
                    self.w1[i][j] += rand_module.gauss(0, 0.1)

        for i in range(self.output_size):
            if rand_module.random() < mutation_rate:
                self.b2[i] += rand_module.gauss(0, 0.1)
            for j in range(self.hidden_size):
                if rand_module.random() < mutation_rate:
                    self.w2[i][j] += rand_module.gauss(0, 0.1)


class Creature:
    def __init__(self, x: float, y: float, brain: NeuralNetwork = None) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = 4
        self.maxspeed = 4
        self.fitness = 0

        self.brain = brain.copy() if brain else NeuralNetwork(5, 8, 2)

    def seek(self, target: "Glow") -> None:
        # Direction to target
        v = py5.Py5Vector(target.position.x - self.position.x,
                          target.position.y - self.position.y)
        distance = math.sqrt(v.x * v.x + v.y * v.y) / py5.width

        # Normalize direction
        length = math.sqrt(v.x * v.x + v.y * v.y)
        if length > 0:
            v.x /= length
            v.y /= length

        # Prepare inputs
        inputs = [
            v.x,
            v.y,
            distance,
            self.velocity.x / self.maxspeed,
            self.velocity.y / self.maxspeed,
        ]

        # Get outputs from neural network
        outputs = self.brain.feedforward(inputs)
        angle = outputs[0] * 2 * math.pi
        magnitude = outputs[1]

        force = py5.Py5Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)
        self.apply_force(force)

    def update(self, target: "Glow") -> None:
        self.velocity.x += self.acceleration.x
        self.velocity.y += self.acceleration.y

        # Limit speed
        speed = math.sqrt(self.velocity.x * self.velocity.x + self.velocity.y * self.velocity.y)
        if speed > self.maxspeed:
            self.velocity.x = (self.velocity.x / speed) * self.maxspeed
            self.velocity.y = (self.velocity.y / speed) * self.maxspeed

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        self.acceleration.x = 0
        self.acceleration.y = 0

        # Check distance to target
        d = math.sqrt((self.position.x - target.position.x) ** 2 +
                      (self.position.y - target.position.y) ** 2)
        if d < self.r + target.r:
            self.fitness += 1

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration.x += force.x
        self.acceleration.y += force.y

    def show(self) -> None:
        angle = math.atan2(self.velocity.y, self.velocity.x)
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(1)
        py5.push()
        py5.translate(self.position.x, self.position.y)
        py5.rotate(angle)
        py5.begin_shape()
        py5.vertex(self.r * 2, 0)
        py5.vertex(-self.r * 2, -self.r)
        py5.vertex(-self.r * 2, self.r)
        py5.end_shape(py5.CLOSE)
        py5.pop()


class Glow:
    def __init__(self) -> None:
        self.xoff = 0
        self.yoff = 1000
        self.position = py5.Py5Vector(0, 0)
        self.r = 24

    def update(self) -> None:
        self.position.x = py5.noise(self.xoff) * py5.width
        self.position.y = py5.noise(self.yoff) * py5.height
        self.xoff += 0.01
        self.yoff += 0.01

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(200)
        py5.circle(self.position.x, self.position.y, self.r * 2)


def normalize_fitness() -> None:
    total = sum(creature.fitness for creature in creatures)
    if total > 0:
        for creature in creatures:
            creature.fitness /= total


def weighted_selection() -> NeuralNetwork:
    index = 0
    start = rand_module.random()
    while start > 0 and index < len(creatures):
        start -= creatures[index].fitness
        index += 1
    index = max(0, index - 1)
    return creatures[index].brain


def reproduction() -> None:
    global creatures, generations
    next_creatures = []
    for _ in range(len(creatures)):
        parent_a = weighted_selection()
        parent_b = weighted_selection()
        child = parent_a.crossover(parent_b)
        child.mutate(0.1)
        next_creatures.append(Creature(rand_module.random() * py5.width,
                                       rand_module.random() * py5.height,
                                       child))
    creatures = next_creatures
    generations += 1


def setup() -> None:
    global creatures, glow, time_multiplier

    py5.size(640, 240)

    creatures = [Creature(rand_module.random() * py5.width,
                          rand_module.random() * py5.height)
                 for _ in range(50)]
    glow = Glow()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global creatures, glow, time_multiplier, life_counter, generations

    py5.background(255)

    glow.show()

    for creature in creatures:
        creature.show()

    # Run simulation multiple times per frame based on time_multiplier
    for _ in range(int(time_multiplier)):
        for creature in creatures:
            creature.seek(glow)
            creature.update(glow)
        glow.update()
        life_counter += 1

        if life_counter > life_span:
            normalize_fitness()
            reproduction()
            life_counter = 0

    # Display info
    py5.fill(0)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"Generation #: {generations}", 10, 18)
    py5.text(f"Cycles left: {max(0, life_span - life_counter)}", 10, 36)

    # Time multiplier display
    py5.text(f"Speed: {int(time_multiplier)}x", 10, 54)
    py5.text("Use UP/DOWN arrows or click to change speed", 10, 220)


def key_pressed() -> None:
    global time_multiplier

    if py5.key == py5.CODED:
        if py5.key_code == py5.UP:
            time_multiplier = min(20, time_multiplier + 1)
        elif py5.key_code == py5.DOWN:
            time_multiplier = max(1, time_multiplier - 1)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "neuro_evolution_steering_seek_####.png"))


def mouse_pressed() -> None:
    global time_multiplier
    # Clicking changes speed based on where you click
    fraction = py5.mouse_x / py5.width
    time_multiplier = 1 + fraction * 19


py5.run_sketch()
