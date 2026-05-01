from pathlib import Path
import random as rand_module

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Mutation rate
MUTATION_RATE = 0.01
# Population size
POPULATION_SIZE = 150

# Population array
population: list["DNA"] = []

# Target phrase
TARGET = "to be or not to be"


def random_character() -> str:
    """Return a random printable character (ASCII 32-126)."""
    return chr(rand_module.randint(32, 126))


class DNA:
    def __init__(self, length: int) -> None:
        self.genes = [random_character() for _ in range(length)]
        self.fitness = 0.0

    def get_phrase(self) -> str:
        """Convert genes array to string."""
        return "".join(self.genes)

    def calculate_fitness(self, target: str) -> None:
        """Calculate fitness by comparing to target."""
        score = 0
        for i in range(len(self.genes)):
            if self.genes[i] == target[i]:
                score += 1
        self.fitness = score / len(target)

    def crossover(self, partner: "DNA") -> "DNA":
        """Create child DNA by crossover."""
        child = DNA(len(self.genes))

        # Random midpoint
        midpoint = rand_module.randint(0, len(self.genes))

        for i in range(len(self.genes)):
            if i < midpoint:
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = partner.genes[i]

        return child

    def mutate(self, mutation_rate: float) -> None:
        """Mutate genes randomly."""
        for i in range(len(self.genes)):
            if rand_module.random() < mutation_rate:
                self.genes[i] = random_character()


def setup() -> None:
    py5.size(640, 240)

    # Initialize population
    for _ in range(POPULATION_SIZE):
        population.append(DNA(len(TARGET)))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    # Step 1: Calculate fitness
    for phrase in population:
        phrase.calculate_fitness(TARGET)

    # Step 2: Build mating pool
    mating_pool = []
    for phrase in population:
        # Add each member n times based on fitness
        n = int(phrase.fitness * 100)
        for _ in range(n):
            mating_pool.append(phrase)

    # Step 3: Reproduction
    for i in range(len(population)):
        # Pick two random parents
        partner_a = rand_module.choice(mating_pool)
        partner_b = rand_module.choice(mating_pool)

        # Crossover
        child = partner_a.crossover(partner_b)

        # Mutation
        child.mutate(MUTATION_RATE)

        # Replace population with children
        population[i] = child

    # Display all phrases in population
    py5.background(255)
    py5.fill(0)
    py5.text_size(11)
    py5.text_align(py5.LEFT)

    # Create string of all phrases separated by spaces
    everything = "    ".join(phrase.get_phrase() for phrase in population)

    # Display with word wrapping
    py5.text(everything, 12, 12, py5.width - 24, py5.height - 24)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ga_shakespeare_####.png"))


py5.run_sketch()
