import random as rand_module
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Population variables
population: "Population"

# Button simulation
button_rect = {"x": 10, "y": 10, "w": 180, "h": 25}


class DNA:
    def __init__(self, genes=None):
        if genes:
            self.genes = genes[:]
        else:
            self.genes = [rand_module.random() for _ in range(14)]

    def crossover(self, partner: "DNA") -> "DNA":
        child_genes = []
        midpoint = rand_module.randint(0, len(self.genes))

        for i in range(len(self.genes)):
            if i < midpoint:
                child_genes.append(self.genes[i])
            else:
                child_genes.append(partner.genes[i])

        return DNA(child_genes)

    def mutate(self, mutation_rate: float) -> None:
        for i in range(len(self.genes)):
            if rand_module.random() < mutation_rate:
                self.genes[i] = rand_module.random()


class Flower:
    def __init__(self, x: float, y: float, dna: DNA) -> None:
        self.x = x
        self.y = y
        self.dna = dna
        self.fitness = 1.0
        self.rollover_on = False
        self.w = 70
        self.h = 140

    def contains(self, mx: float, my: float) -> bool:
        return (
            mx > self.x - self.w / 2
            and mx < self.x + self.w / 2
            and my > self.y - self.h / 2
            and my < self.y + self.h / 2
        )

    def show(self) -> None:
        genes = self.dna.genes

        # Map genes to visual properties (matching p5.js map ranges)
        petal_r = int(genes[0] * 255)
        petal_g = int(genes[1] * 255)
        petal_b = int(genes[2] * 255)
        petal_a = int(genes[3] * 255)

        # petal size: map(genes[4], 0, 1, 4, 24)
        petal_size = genes[4] * 20 + 4
        # petal count: map(genes[5], 0, 1, 2, 16)
        petal_count = int(genes[5] * 14 + 2)

        # Center color
        center_r = int(genes[6] * 255)
        center_g = int(genes[7] * 255)
        center_b = int(genes[8] * 255)

        # Center size: map(genes[9], 0, 1, 24, 48)
        center_size = genes[9] * 24 + 24

        # Stem color
        stem_r = int(genes[10] * 255)
        stem_g = int(genes[11] * 255)
        stem_b = int(genes[12] * 255)

        # Stem length: map(genes[13], 0, 1, 50, 100)
        stem_length = genes[13] * 50 + 50

        py5.push()
        py5.translate(self.x, self.y)

        # Draw bounding box
        if self.rollover_on:
            py5.fill(0, 0, 0, 64)
        else:
            py5.no_fill()

        py5.stroke(0)
        py5.stroke_weight(1)
        py5.rect_mode(py5.CENTER)
        py5.rect(0, 0, self.w, self.h)

        # Translate for flower drawing
        py5.translate(0, self.h / 2 - stem_length)

        # Draw stem
        py5.stroke(stem_r, stem_g, stem_b)
        py5.stroke_weight(4)
        py5.line(0, 0, 0, stem_length)

        py5.no_stroke()

        # Draw petals
        py5.fill(petal_r, petal_g, petal_b, petal_a)
        for i in range(petal_count):
            angle = (i / petal_count) * 2 * 3.14159
            px = petal_size * py5.cos(angle)
            py = petal_size * py5.sin(angle)
            py5.ellipse(px, py, petal_size, petal_size)

        # Draw center
        py5.fill(center_r, center_g, center_b)
        py5.ellipse(0, 0, center_size, center_size)

        py5.pop()

        # Display fitness value
        py5.text_align(py5.CENTER)
        if self.rollover_on:
            py5.fill(0)
        else:
            py5.fill(64)

        py5.text_size(12)
        py5.text(str(int(self.fitness)), self.x, self.y + 90)

    def rollover(self, mx: float, my: float) -> None:
        if self.contains(mx, my):
            self.rollover_on = True
            self.fitness += 0.25
        else:
            self.rollover_on = False


class Population:
    def __init__(self, num: int) -> None:
        self.flowers = [Flower(40 + i * 80, 120, DNA()) for i in range(num)]
        self.mutation_rate = 0.05
        self.generations = 0

    def show(self) -> None:
        for flower in self.flowers:
            flower.show()

    def rollover(self, mx: float, my: float) -> None:
        for flower in self.flowers:
            flower.rollover(mx, my)

    def selection(self) -> None:
        # Normalize fitness
        total_fitness = sum(f.fitness for f in self.flowers)
        for flower in self.flowers:
            flower.fitness /= total_fitness if total_fitness > 0 else 1

    def weighted_selection(self) -> "Flower":
        index = 0
        start = rand_module.random()

        while start > 0 and index < len(self.flowers):
            start -= self.flowers[index].fitness
            index += 1

        index = max(0, index - 1)
        return self.flowers[index]

    def reproduction(self) -> None:
        # Create next generation
        new_flowers = []
        for i in range(len(self.flowers)):
            parent_a = self.weighted_selection()
            parent_b = self.weighted_selection()

            child_dna = parent_a.dna.crossover(parent_b.dna)
            child_dna.mutate(self.mutation_rate)

            x = 40 + i * 80
            new_flowers.append(Flower(x, 120, child_dna))

        self.flowers = new_flowers
        self.generations += 1


def setup() -> None:
    global population
    py5.size(640, 240)
    population = Population(8)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    # Check for mouse rollover
    population.rollover(py5.mouse_x, py5.mouse_y)

    # Display flowers
    population.show()

    # Draw button
    py5.fill(100)
    py5.stroke(0)
    py5.stroke_weight(1)
    py5.rect(button_rect["x"], button_rect["y"], button_rect["w"], button_rect["h"])

    py5.fill(255)
    py5.text_size(12)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text(
        "evolve new generation",
        button_rect["x"] + button_rect["w"] / 2,
        button_rect["y"] + button_rect["h"] / 2,
    )

    # Display generation
    py5.fill(0)
    py5.text_size(12)
    py5.text_align(py5.LEFT)
    py5.text(f"Generation {population.generations}", 12, py5.height - 10)


def mouse_pressed() -> None:
    # Check if button was clicked
    if (
        button_rect["x"] < py5.mouse_x < button_rect["x"] + button_rect["w"]
        and button_rect["y"] < py5.mouse_y < button_rect["y"] + button_rect["h"]
    ):
        population.selection()
        population.reproduction()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "interactive_selection_####.png"))


py5.run_sketch()
