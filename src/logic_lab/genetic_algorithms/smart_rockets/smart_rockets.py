import math
import random as rand_module
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

population: "Population"
obstacle: "Obstacle"
target: py5.Py5Vector

MUTATION_RATE = 0.01
LIFE_SPAN = 250
life_counter = 0
record_cycles = float("inf")


class DNA:
    def __init__(self, newgenes=None, life_span: int = LIFE_SPAN):
        if newgenes:
            self.genes = [py5.Py5Vector(g.x, g.y) for g in newgenes]
        else:
            self.genes = []
            for _ in range(life_span):
                angle = rand_module.uniform(0, 2 * math.pi)
                force_x = math.cos(angle) * 0.1
                force_y = math.sin(angle) * 0.1
                self.genes.append(py5.Py5Vector(force_x, force_y))

    def mutate(self, m: float) -> None:
        for i in range(len(self.genes)):
            if rand_module.random() < m:
                angle = rand_module.uniform(0, 2 * math.pi)
                force_x = math.cos(angle) * 0.1
                force_y = math.sin(angle) * 0.1
                self.genes[i] = py5.Py5Vector(force_x, force_y)

    def crossover(self, partner: "DNA") -> "DNA":
        child = []
        midpoint = rand_module.randint(0, len(self.genes))

        for i in range(len(self.genes)):
            if i > midpoint:
                child.append(py5.Py5Vector(self.genes[i].x, self.genes[i].y))
            else:
                child.append(py5.Py5Vector(partner.genes[i].x, partner.genes[i].y))

        return DNA(child, len(self.genes))

    def copy(self) -> "DNA":
        return DNA(self.genes)


class Obstacle:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.w = w
        self.h = h

    def contains(self, spot: py5.Py5Vector) -> bool:
        return (
            spot.x > self.position.x
            and spot.x < self.position.x + self.w
            and spot.y > self.position.y
            and spot.y < self.position.y + self.h
        )

    def show(self) -> None:
        py5.fill(100)
        py5.stroke(0)
        py5.rect(self.position.x, self.position.y, self.w, self.h)


class Rocket:
    def __init__(self, dna: DNA) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.dna = dna
        self.hit_obstacle = False
        self.reached_target = False
        self.fitness = 0.0
        self.trail = [py5.Py5Vector(self.position.x, self.position.y)]

    def calc_fitness(self, target: py5.Py5Vector) -> None:
        distance = ((self.position.x - target.x) ** 2 + (self.position.y - target.y) ** 2) ** 0.5
        self.fitness = (py5.width - distance) if distance < py5.width else 0

        if self.reached_target:
            self.fitness *= 2

        if self.hit_obstacle:
            self.fitness *= 0.1

    def run(self, target: py5.Py5Vector, obstacle: Obstacle) -> None:
        # Execute one step of the DNA
        if not hasattr(self, "step_counter"):
            self.step_counter = 0

        if self.step_counter < len(self.dna.genes):
            self.apply_force(self.dna.genes[self.step_counter])
            self.update()
            self.check_obstacles(obstacle)
            self.check_target(target)
            self.boundaries()

            # Track cycles to target
            if self.reached_target and not hasattr(self, "cycles_to_target"):
                self.cycles_to_target = self.step_counter

            self.step_counter += 1

    def check_target(self, target: py5.Py5Vector) -> None:
        distance = ((self.position.x - target.x) ** 2 + (self.position.y - target.y) ** 2) ** 0.5
        if distance < 12:
            self.reached_target = True

    def check_obstacles(self, obstacle: Obstacle) -> None:
        if obstacle.contains(self.position):
            self.hit_obstacle = True

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration = py5.Py5Vector(0, 0)
        # Record trail
        self.trail.append(py5.Py5Vector(self.position.x, self.position.y))

    def boundaries(self) -> None:
        if self.position.x > py5.width:
            self.position.x = 0
        if self.position.y > py5.height:
            self.position.y = 0
        if self.position.x < 0:
            self.position.x = py5.width
        if self.position.y < 0:
            self.position.y = py5.height

    def show(self) -> None:
        # Draw trail
        py5.stroke(0)
        py5.stroke_weight(1)
        py5.no_fill()
        py5.begin_shape()
        for pos in self.trail:
            py5.vertex(float(pos.x), float(pos.y))
        py5.end_shape()

        # Draw rocket
        angle = math.atan2(self.velocity.y, self.velocity.x)
        py5.push()
        py5.translate(self.position.x, self.position.y)
        py5.rotate(angle)

        # Rocket body
        py5.fill(200)
        py5.rect(0, -5, 10, 10)

        # Rocket tip
        py5.fill(255, 0, 0)
        py5.begin_shape(py5.TRIANGLES)
        py5.vertex(10, -5)
        py5.vertex(10, 5)
        py5.vertex(15, 0)
        py5.end_shape()

        py5.pop()

    def copy(self) -> "Rocket":
        if rand_module.random() < 0.001:
            return Rocket(self.dna.copy())
        else:
            parent_a = rand_module.choice(self.dna.genes)
            parent_b = rand_module.choice(self.dna.genes)
            child_dna = DNA([parent_a, parent_b])
            child_dna.mutate(MUTATION_RATE)
            return Rocket(child_dna)


class Population:
    def __init__(self, num: int, mutation_rate: float) -> None:
        self.rockets = [Rocket(DNA()) for _ in range(num)]
        self.mutation_rate = mutation_rate
        self.generation = 0

    def live(self, obstacle: Obstacle, target: py5.Py5Vector) -> None:
        for rocket in self.rockets:
            rocket.run(target, obstacle)
            rocket.show()

    def target_reached(self) -> bool:
        return any(rocket.reached_target for rocket in self.rockets)

    def calculate_fitness(self, target: py5.Py5Vector) -> None:
        for rocket in self.rockets:
            rocket.calc_fitness(target)

    def selection(self) -> None:
        total = sum(rocket.fitness for rocket in self.rockets)
        for rocket in self.rockets:
            rocket.fitness /= total if total > 0 else 1

    def reproduction(self) -> None:
        new_rockets = []
        for _ in range(len(self.rockets)):
            parent_a = self.weighted_selection()
            parent_b = self.weighted_selection()
            child_dna = parent_a.dna.crossover(parent_b.dna)
            child_dna.mutate(self.mutation_rate)
            new_rockets.append(Rocket(child_dna, LIFE_SPAN))

        self.rockets = new_rockets
        self.generation += 1

    def weighted_selection(self) -> Rocket:
        index = 0
        start = rand_module.random()
        distance = 0

        while distance < start and index < len(self.rockets):
            distance += self.rockets[index].fitness
            index += 1

        index = max(0, min(index - 1, len(self.rockets) - 1))
        return self.rockets[index]


def setup() -> None:
    global population, obstacle, target
    py5.size(640, 360)

    population = Population(150, MUTATION_RATE)
    target = py5.Py5Vector(py5.width / 2, 50)
    obstacle = Obstacle(py5.width / 2 - 25, py5.height / 2 - 25, 50, 50)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global life_counter, record_cycles
    py5.background(255)

    if life_counter < LIFE_SPAN:
        population.live(obstacle, target)
        life_counter += 1
    else:
        # Check if any rocket reached target
        for rocket in population.rockets:
            if hasattr(rocket, "cycles_to_target"):
                record_cycles = min(record_cycles, rocket.cycles_to_target)

        # Next generation
        life_counter = 0
        population.calculate_fitness(target)
        population.selection()
        population.reproduction()

    obstacle.show()

    py5.fill(255, 0, 0)
    py5.circle(target.x, target.y, 16)

    # Display info
    py5.fill(0)
    py5.text_size(12)
    cycles_left = LIFE_SPAN - life_counter
    record_display = int(record_cycles) if record_cycles != float("inf") else "N/A"
    info_text = f"Generation #: {population.generation}\nCycles left: {cycles_left}\nRecord cycles: {record_display}"
    py5.text(info_text, 10, 20)


def mouse_pressed() -> None:
    target.x = py5.mouse_x
    target.y = py5.mouse_y


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "smart_rockets_####.png"))


py5.run_sketch()
