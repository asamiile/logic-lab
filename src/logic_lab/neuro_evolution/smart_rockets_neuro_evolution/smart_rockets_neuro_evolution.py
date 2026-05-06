import copy
import math
import random as rand_module
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

life_span = 300
population: "Population"
life_counter = 0
record_time = 300

target: "Obstacle"
obstacles = []


class NeuralNetwork:
    def __init__(self, input_size: int = 2, hidden_size: int = 8, output_size: int = 2) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.w1 = [
            [rand_module.gauss(0, 0.5) for _ in range(input_size)] for _ in range(hidden_size)
        ]
        self.b1 = [rand_module.gauss(0, 0.5) for _ in range(hidden_size)]
        self.w2 = [
            [rand_module.gauss(0, 0.5) for _ in range(hidden_size)] for _ in range(output_size)
        ]
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


class Rocket:
    def __init__(self, x: float, y: float, brain: NeuralNetwork = None) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = 4
        self.brain = brain.copy() if brain else NeuralNetwork(2, 8, 2)

        self.finish_counter = 0
        self.record_distance = float("inf")
        self.fitness = 0
        self.hit_obstacle = False
        self.hit_target = False
        self.maxspeed = 4
        self.maxforce = 1

    def run(self, obstacles: list) -> None:
        if not self.hit_obstacle and not self.hit_target:
            inputs = [self.position.x / py5.width, self.position.y / py5.height]
            outputs = self.brain.feedforward(inputs)
            angle = outputs[0] * 2 * math.pi
            magnitude = outputs[1] * self.maxforce
            force = py5.Py5Vector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)
            self.apply_force(force)
            self.update()
            self.check_obstacles(obstacles)

        self.show()

    def check_target(self) -> None:
        distance = math.sqrt(
            (self.position.x - target.position.x) ** 2 + (self.position.y - target.position.y) ** 2
        )
        if distance < self.record_distance:
            self.record_distance = distance

        if target.contains(self.position) and not self.hit_target:
            self.hit_target = True
        elif not self.hit_target:
            self.finish_counter += 1

    def check_obstacles(self, obstacles: list) -> None:
        for obstacle in obstacles:
            if obstacle.contains(self.position):
                self.hit_obstacle = True

    def calculate_fitness(self) -> None:
        self.fitness = 1.0 / (self.finish_counter * self.record_distance)
        self.fitness = self.fitness**4

        if self.hit_obstacle:
            self.fitness *= 0.1

        if self.hit_target:
            self.fitness *= 2

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration.x += force.x
        self.acceleration.y += force.y

    def update(self) -> None:
        # Limit velocity
        speed = math.sqrt(self.velocity.x**2 + self.velocity.y**2)
        if speed > self.maxspeed:
            self.velocity.x = (self.velocity.x / speed) * self.maxspeed
            self.velocity.y = (self.velocity.y / speed) * self.maxspeed

        self.velocity.x += self.acceleration.x
        self.velocity.y += self.acceleration.y
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        self.acceleration.x = 0
        self.acceleration.y = 0

    def show(self) -> None:
        theta = math.atan2(self.velocity.y, self.velocity.x) + math.pi / 2

        py5.fill(200, 100)
        py5.stroke(0)
        py5.stroke_weight(1)
        py5.push()
        py5.translate(self.position.x, self.position.y)
        py5.rotate(theta)

        # Thrusters
        py5.rect_mode(py5.CENTER)
        py5.fill(0)
        py5.rect(-self.r / 2, self.r * 2, self.r / 2, self.r)
        py5.rect(self.r / 2, self.r * 2, self.r / 2, self.r)

        # Rocket body
        py5.fill(200)
        py5.begin_shape(py5.TRIANGLES)
        py5.vertex(0, -self.r * 2)
        py5.vertex(-self.r, self.r * 2)
        py5.vertex(self.r, self.r * 2)
        py5.end_shape()

        py5.pop()


class Obstacle:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.w = w
        self.h = h

    def show(self) -> None:
        py5.stroke(0)
        py5.fill(175)
        py5.stroke_weight(2)
        py5.rect_mode(py5.CORNER)
        py5.rect(self.position.x, self.position.y, self.w, self.h)

    def contains(self, spot: py5.Py5Vector) -> bool:
        return (
            spot.x > self.position.x
            and spot.x < self.position.x + self.w
            and spot.y > self.position.y
            and spot.y < self.position.y + self.h
        )


class Population:
    def __init__(self, mutation_rate: float, size: int) -> None:
        self.mutation_rate = mutation_rate
        self.population = [Rocket(py5.width / 2, py5.height - 20) for _ in range(size)]
        self.generations = 0

    def live(self, obstacles: list) -> None:
        for rocket in self.population:
            rocket.check_target()
            rocket.run(obstacles)

    def target_reached(self) -> bool:
        for rocket in self.population:
            if rocket.hit_target:
                return True
        return False

    def calculate_fitness(self) -> None:
        for rocket in self.population:
            rocket.calculate_fitness()

    def selection(self) -> None:
        total_fitness = sum(rocket.fitness for rocket in self.population)
        for rocket in self.population:
            rocket.fitness /= total_fitness if total_fitness > 0 else 1

    def reproduction(self) -> None:
        next_population = []
        for _ in range(len(self.population)):
            parent_a = self.weighted_selection()
            parent_b = self.weighted_selection()
            child = parent_a.crossover(parent_b)
            child.mutate(self.mutation_rate)
            next_population.append(Rocket(py5.width / 2, py5.height - 20, child))

        self.population = next_population
        self.generations += 1

    def weighted_selection(self) -> NeuralNetwork:
        index = 0
        start = rand_module.random()
        while start > 0 and index < len(self.population):
            start -= self.population[index].fitness
            index += 1
        index = max(0, index - 1)
        return self.population[index].brain


def setup() -> None:
    global population, target, obstacles, life_counter, record_time

    py5.size(640, 240)
    record_time = life_span

    target = Obstacle(py5.width / 2 - 12, 24, 24, 24)
    population = Population(0.01, 150)

    obstacles = []
    obstacles.append(Obstacle(py5.width / 2 - 75, py5.height / 2, 150, 10))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global life_counter, record_time

    py5.background(255)

    target.show()

    if life_counter < life_span:
        population.live(obstacles)
        if population.target_reached() and life_counter < record_time:
            record_time = life_counter
        else:
            life_counter += 1
    else:
        life_counter = 0
        population.calculate_fitness()
        population.selection()
        population.reproduction()

    for obstacle in obstacles:
        obstacle.show()

    py5.fill(0)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"Generation #: {population.generations}", 10, 18)
    py5.text(f"Cycles left: {life_span - life_counter}", 10, 36)
    py5.text(f"Record cycles: {record_time}", 10, 54)


def mouse_pressed() -> None:
    global record_time
    target.position.x = py5.mouse_x
    target.position.y = py5.mouse_y
    record_time = life_span


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "smart_rockets_neuro_evolution_####.png"))


py5.run_sketch()
