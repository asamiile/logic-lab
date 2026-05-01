from pathlib import Path
import random as rand_module
import math

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

target: str
popmax: int
mutation_rate: float
population: "Population"


def new_char() -> str:
    """Generate a random character in the range for evolution."""
    c = int(rand_module.uniform(63, 123))
    if c == 63:
        c = 32
    if c == 64:
        c = 46
    return chr(c)


class DNA:
    def __init__(self, num: int) -> None:
        self.genes = [new_char() for _ in range(num)]
        self.fitness = 0.0

    def get_phrase(self) -> str:
        return "".join(self.genes)

    def calc_fitness(self, target: str) -> None:
        score = 0
        for i in range(len(self.genes)):
            if self.genes[i] == target[i]:
                score += 1
        self.fitness = score / len(target)

    def crossover(self, partner: "DNA") -> "DNA":
        child = DNA(len(self.genes))
        midpoint = int(rand_module.random() * len(self.genes))

        for i in range(len(self.genes)):
            if i > midpoint:
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = partner.genes[i]

        return child

    def mutate(self, mutation_rate: float) -> None:
        for i in range(len(self.genes)):
            if rand_module.random() < mutation_rate:
                self.genes[i] = new_char()


class Population:
    def __init__(self, target: str, mutation_rate: float, num: int) -> None:
        self.population = [DNA(len(target)) for _ in range(num)]
        self.mating_pool = []
        self.generations = 0
        self.finished = False
        self.target = target
        self.mutation_rate = mutation_rate
        self.perfect_score = 1.0
        self.best = ""
        self.calc_fitness()

    def calc_fitness(self) -> None:
        for dna in self.population:
            dna.calc_fitness(self.target)

    def natural_selection(self) -> None:
        self.mating_pool = []

        max_fitness = max(dna.fitness for dna in self.population)

        for dna in self.population:
            fitness = dna.fitness / max_fitness if max_fitness > 0 else 0
            n = int(fitness * 100)
            for _ in range(n):
                self.mating_pool.append(dna)

    def generate(self) -> None:
        new_population = []
        for _ in range(len(self.population)):
            a = int(rand_module.random() * len(self.mating_pool))
            b = int(rand_module.random() * len(self.mating_pool))
            partner_a = self.mating_pool[a]
            partner_b = self.mating_pool[b]
            child = partner_a.crossover(partner_b)
            child.mutate(self.mutation_rate)
            new_population.append(child)

        self.population = new_population
        self.generations += 1

    def evaluate(self) -> None:
        world_record = 0.0
        index = 0
        for i in range(len(self.population)):
            if self.population[i].fitness > world_record:
                index = i
                world_record = self.population[i].fitness

        self.best = self.population[index].get_phrase()
        if world_record == self.perfect_score:
            self.finished = True

    def is_finished(self) -> bool:
        return self.finished

    def get_generations(self) -> int:
        return self.generations

    def get_best(self) -> str:
        return self.best

    def get_average_fitness(self) -> float:
        total = sum(dna.fitness for dna in self.population)
        return total / len(self.population)

    def all_phrases(self) -> str:
        everything = ""
        display_limit = min(len(self.population), 51)

        for i in range(display_limit):
            everything += self.population[i].get_phrase()
            if (i + 1) % 3 == 0:
                everything += "\n"
            else:
                everything += " "

        return everything


def setup() -> None:
    global target, popmax, mutation_rate, population
    py5.size(640, 240)
    target = "To be or not to be."
    popmax = 200
    mutation_rate = 0.01

    population = Population(target, mutation_rate, popmax)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global population

    # Generate mating pool
    population.natural_selection()
    # Create next generation
    population.generate()
    # Calculate fitness
    population.calc_fitness()
    population.evaluate()

    # If we found the target phrase, stop
    if population.is_finished():
        py5.no_loop()

    py5.background(255)
    answer = population.get_best()

    py5.fill(0)
    py5.text_size(12)
    py5.text("Best phrase:", 10, 32)

    py5.text_size(24)
    py5.text(answer, 10, 64)

    stats_text = f"total generations:     {population.get_generations()}\n"
    stats_text += f"average fitness:       {population.get_average_fitness():.2f}\n"
    stats_text += f"total population:      {popmax}\n"
    stats_text += f"mutation rate:         {int(mutation_rate * 100)}%"

    py5.text_size(12)
    py5.text(stats_text, 10, 96)

    py5.text_size(8)
    py5.text(population.all_phrases(), py5.width / 2, 24)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ga_shakespeare_annotated_####.png"))


py5.run_sketch()
