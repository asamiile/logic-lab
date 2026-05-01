from pathlib import Path
import math
import random as rand_module

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

LIFE_SPAN = 250
life_counter = 0

population: "Population"
target: py5.Py5Vector


class DNA:
    def __init__(self, life_span: int = LIFE_SPAN) -> None:
        self.genes = []
        self.max_force = 0.1

        for _ in range(life_span):
            angle = rand_module.uniform(0, 2 * math.pi)
            force_x = math.cos(angle) * rand_module.uniform(0, self.max_force)
            force_y = math.sin(angle) * rand_module.uniform(0, self.max_force)
            self.genes.append(py5.Py5Vector(force_x, force_y))

    def crossover(self, partner: "DNA") -> "DNA":
        child = DNA(len(self.genes))
        midpoint = rand_module.randint(0, len(self.genes))

        for i in range(len(self.genes)):
            if i < midpoint:
                child.genes[i] = py5.Py5Vector(self.genes[i].x, self.genes[i].y)
            else:
                child.genes[i] = py5.Py5Vector(partner.genes[i].x, partner.genes[i].y)

        return child

    def mutate(self, mutation_rate: float) -> None:
        for i in range(len(self.genes)):
            if rand_module.random() < mutation_rate:
                angle = rand_module.uniform(0, 2 * math.pi)
                force_x = math.cos(angle) * rand_module.uniform(0, self.max_force)
                force_y = math.sin(angle) * rand_module.uniform(0, self.max_force)
                self.genes[i] = py5.Py5Vector(force_x, force_y)


class Rocket:
    def __init__(self, x: float, y: float, dna: DNA) -> None:
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(0, 0)
        self.position = py5.Py5Vector(x, y)
        self.r = 4
        self.fitness = 0.0
        self.dna = dna
        self.gene_counter = 0

    def calculate_fitness(self) -> None:
        distance = (
            (self.position.x - target.x) ** 2 + (self.position.y - target.y) ** 2
        ) ** 0.5
        self.fitness = 1.0 / (distance * distance) if distance > 0 else 0

    def run(self) -> None:
        self.apply_force(self.dna.genes[self.gene_counter])
        self.gene_counter = (self.gene_counter + 1) % len(self.dna.genes)
        self.update()
        self.show()

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration = py5.Py5Vector(0, 0)

    def show(self) -> None:
        angle = math.atan2(self.velocity.y, self.velocity.x) + math.pi / 2
        r = self.r

        py5.stroke(0)
        py5.stroke_weight(1)
        py5.push()
        py5.translate(self.position.x, self.position.y)
        py5.rotate(angle)

        # Thrusters
        py5.rect_mode(py5.CENTER)
        py5.fill(0)
        py5.rect(-r / 2, r * 2, r / 2, r)
        py5.rect(r / 2, r * 2, r / 2, r)

        # Rocket body
        py5.fill(200)
        py5.begin_shape(py5.TRIANGLES)
        py5.vertex(0, -r * 2)
        py5.vertex(-r, r * 2)
        py5.vertex(r, r * 2)
        py5.end_shape()

        py5.pop()


class Population:
    def __init__(self, mutation_rate: float, pop_size: int) -> None:
        self.mutation_rate = mutation_rate
        self.population = []
        self.generations = 0

        for _ in range(pop_size):
            x = py5.width / 2
            y = py5.height + 20
            self.population.append(Rocket(x, y, DNA()))

    def live(self) -> None:
        for rocket in self.population:
            rocket.run()

    def fitness(self) -> None:
        for rocket in self.population:
            rocket.calculate_fitness()

    def selection(self) -> None:
        # Normalize fitness
        total_fitness = sum(rocket.fitness for rocket in self.population)
        for rocket in self.population:
            rocket.fitness /= total_fitness if total_fitness > 0 else 1

    def reproduction(self) -> None:
        next_population = []
        for _ in range(len(self.population)):
            parent_a = self.weighted_selection()
            parent_b = self.weighted_selection()
            child_dna = parent_a.crossover(parent_b)
            child_dna.mutate(self.mutation_rate)

            x = py5.width / 2
            y = py5.height + 20
            next_population.append(Rocket(x, y, child_dna))

        self.population = next_population
        self.generations += 1

    def weighted_selection(self) -> DNA:
        index = 0
        start = rand_module.random()

        while start > 0:
            start -= self.population[index].fitness
            index += 1

        index = max(0, index - 1)
        return self.population[index].dna


def setup() -> None:
    global population, target
    py5.size(640, 240)

    target = py5.Py5Vector(py5.width / 2, 24)
    mutation_rate = 0.01
    population = Population(mutation_rate, 50)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global life_counter

    py5.background(255)

    # Draw target
    py5.fill(127)
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.circle(target.x, target.y, 24)

    if life_counter < LIFE_SPAN:
        population.live()
        life_counter += 1
    else:
        life_counter = 0
        population.fitness()
        population.selection()
        population.reproduction()

    # Display info
    py5.fill(0)
    py5.no_stroke()
    py5.text_size(12)
    info_text = f"Generation #: {population.generations}\nCycles left: {LIFE_SPAN - life_counter}"
    py5.text(info_text, 10, 20)


def mouse_pressed() -> None:
    target.x = py5.mouse_x
    target.y = py5.mouse_y


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "smart_rockets_basic_####.png"))


py5.run_sketch()
