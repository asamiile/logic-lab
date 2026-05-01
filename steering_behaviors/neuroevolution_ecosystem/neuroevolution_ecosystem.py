from pathlib import Path
import random as rand_module
import math
import copy

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

creatures = []
food = []
time_multiplier = 1


class NeuralNetwork:
    def __init__(self, input_size: int = 15, hidden_size: int = 8, output_size: int = 2) -> None:
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


class Sensor:
    def __init__(self, v: py5.Py5Vector) -> None:
        self.v = py5.Py5Vector(v.x, v.y)
        self.value = 0

    def sense(self, position: py5.Py5Vector, food_item: "Food") -> None:
        end_x = position.x + self.v.x
        end_y = position.y + self.v.y

        d = math.sqrt((end_x - food_item.position.x) ** 2 +
                      (end_y - food_item.position.y) ** 2)

        if d < food_item.r:
            self.value = 1

    def reset(self) -> None:
        self.value = 0


class Creature:
    def __init__(self, x: float, y: float, brain: NeuralNetwork = None) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.full_size = 12
        self.r = self.full_size
        self.maxspeed = 2
        self.sensors = []
        self.health = 100

        # Create 15 sensors
        total_sensors = 15
        for i in range(total_sensors):
            angle = (i / total_sensors) * 2 * math.pi
            vx = math.cos(angle) * self.full_size * 1.5
            vy = math.sin(angle) * self.full_size * 1.5
            self.sensors.append(Sensor(py5.Py5Vector(vx, vy)))

        self.brain = brain.copy() if brain else NeuralNetwork(15, 8, 2)

    def think(self) -> None:
        # Reset all sensor values
        for sensor in self.sensors:
            sensor.reset()

        # Sense all food
        for food_item in food:
            for sensor in self.sensors:
                sensor.sense(self.position, food_item)

        # Prepare inputs for neural network
        inputs = [sensor.value for sensor in self.sensors]

        # Get outputs from neural network
        outputs = self.brain.feedforward(inputs)
        angle = outputs[0] * 2 * math.pi
        magnitude = outputs[1]

        force = py5.Py5Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)
        self.apply_force(force)

    def eat(self) -> None:
        for food_item in food:
            d = math.sqrt((self.position.x - food_item.position.x) ** 2 +
                         (self.position.y - food_item.position.y) ** 2)
            if d < self.r + food_item.r:
                self.health += 0.5
                food_item.r -= 0.05
                if food_item.r < 20:
                    food_item.position.x = rand_module.random() * py5.width
                    food_item.position.y = rand_module.random() * py5.height
                    food_item.r = 50

    def update(self) -> None:
        self.velocity.x += self.acceleration.x
        self.velocity.y += self.acceleration.y

        # Limit speed
        speed = math.sqrt(self.velocity.x ** 2 + self.velocity.y ** 2)
        if speed > self.maxspeed:
            self.velocity.x = (self.velocity.x / speed) * self.maxspeed
            self.velocity.y = (self.velocity.y / speed) * self.maxspeed

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        self.acceleration.x = 0
        self.acceleration.y = 0

        self.health -= 0.25

    def borders(self) -> None:
        if self.position.x < -self.r:
            self.position.x = py5.width + self.r
        if self.position.y < -self.r:
            self.position.y = py5.height + self.r
        if self.position.x > py5.width + self.r:
            self.position.x = -self.r
        if self.position.y > py5.height + self.r:
            self.position.y = -self.r

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration.x += force.x
        self.acceleration.y += force.y

    def reproduce(self) -> "Creature":
        child_brain = self.brain.copy()
        child_brain.mutate(0.1)
        return Creature(self.position.x, self.position.y, child_brain)

    def show(self) -> None:
        py5.push()
        py5.translate(self.position.x, self.position.y)

        # Draw sensors
        for sensor in self.sensors:
            py5.stroke(0, int(self.health * 2))
            py5.line(0, 0, sensor.v.x, sensor.v.y)

            if sensor.value > 0:
                py5.fill(255, int(sensor.value * 255))
                py5.stroke(0, 100)
                py5.circle(sensor.v.x, sensor.v.y, 4)

        # Draw body (size based on health)
        py5.no_stroke()
        py5.fill(0, int(self.health * 2))
        self.r = (self.health / 100) * self.full_size
        self.r = max(2, min(self.r, self.full_size))
        py5.circle(0, 0, self.r * 2)

        py5.pop()


class Food:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(rand_module.random() * py5.width,
                                      rand_module.random() * py5.height)
        self.r = 50

    def show(self) -> None:
        py5.no_stroke()
        py5.fill(0, 100)
        py5.circle(self.position.x, self.position.y, self.r * 2)


def setup() -> None:
    global creatures, food, time_multiplier

    py5.size(640, 240)

    creatures = [Creature(rand_module.random() * py5.width,
                          rand_module.random() * py5.height)
                 for _ in range(20)]

    food = [Food() for _ in range(8)]

    time_multiplier = 1

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global creatures, food, time_multiplier

    py5.background(255)

    # Run simulation multiple times per frame
    for _ in range(int(time_multiplier)):
        i = len(creatures) - 1
        while i >= 0:
            creatures[i].think()
            creatures[i].eat()
            creatures[i].update()
            creatures[i].borders()

            if creatures[i].health < 0:
                creatures.pop(i)
            elif rand_module.random() < 0.001:
                child = creatures[i].reproduce()
                creatures.append(child)

            i -= 1

    # Display food
    for food_item in food:
        food_item.show()

    # Display creatures
    for creature in creatures:
        creature.show()

    # Display info
    py5.fill(0)
    py5.text_size(12)
    py5.text(f"Creatures: {len(creatures)}", 10, py5.height - 20)
    py5.text(f"Food: {len(food)}", 10, py5.height - 5)
    py5.text(f"Speed: {int(time_multiplier)}x | UP/DOWN to adjust", 250, py5.height - 10)


def key_pressed() -> None:
    global time_multiplier

    if py5.key == py5.CODED:
        if py5.key_code == py5.UP:
            time_multiplier = min(20, time_multiplier + 1)
        elif py5.key_code == py5.DOWN:
            time_multiplier = max(1, time_multiplier - 1)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "neuroevolution_ecosystem_####.png"))


py5.run_sketch()
