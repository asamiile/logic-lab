from pathlib import Path
import random as rand_module
import math
import copy

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

birds = []
pipes = []
generation = 0


class NeuralNetwork:
    def __init__(self, input_size: int = 4, hidden_size: int = 8, output_size: int = 2) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Initialize weights
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
        # Hidden layer
        hidden = []
        for i in range(self.hidden_size):
            sum_val = self.b1[i]
            for j in range(self.input_size):
                sum_val += inputs[j] * self.w1[i][j]
            hidden.append(self.sigmoid(sum_val))

        # Output layer
        output = []
        for i in range(self.output_size):
            sum_val = self.b2[i]
            for j in range(self.hidden_size):
                sum_val += hidden[j] * self.w2[i][j]
            output.append(self.sigmoid(sum_val))

        return output

    def copy(self) -> "NeuralNetwork":
        """Create a copy of this network."""
        nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)
        nn.w1 = copy.deepcopy(self.w1)
        nn.b1 = copy.deepcopy(self.b1)
        nn.w2 = copy.deepcopy(self.w2)
        nn.b2 = copy.deepcopy(self.b2)
        return nn

    def crossover(self, partner: "NeuralNetwork") -> "NeuralNetwork":
        """Create a child network from two parents."""
        child = self.copy()

        # Crossover weights and biases randomly
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
        """Mutate the network weights."""
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


class Bird:
    def __init__(self, brain: NeuralNetwork = None) -> None:
        if brain:
            self.brain = brain.copy()
        else:
            self.brain = NeuralNetwork(4, 8, 2)

        self.x = 50
        self.y = 120
        self.velocity = 0
        self.gravity = 0.5
        self.flap_force = -10
        self.fitness = 0
        self.alive = True

    def think(self, pipes: list) -> None:
        """Use neural network to decide whether to flap."""
        next_pipe = None
        for pipe in pipes:
            if pipe.x + pipe.w > self.x:
                next_pipe = pipe
                break

        if next_pipe is None:
            return

        inputs = [
            self.y / py5.height,
            self.velocity / py5.height,
            next_pipe.top / py5.height,
            (next_pipe.x - self.x) / py5.width,
        ]

        output = self.brain.feedforward(inputs)
        if output[0] > output[1]:  # flap has higher activation
            self.flap()

    def flap(self) -> None:
        self.velocity += self.flap_force

    def update(self) -> None:
        self.velocity += self.gravity
        self.y += self.velocity
        self.velocity *= 0.95

        if self.y > py5.height or self.y < 0:
            self.alive = False

        self.fitness += 1

    def show(self) -> None:
        py5.stroke_weight(2)
        py5.stroke(0)
        py5.fill(127, 200)
        py5.circle(self.x, self.y, 16)


class Pipe:
    def __init__(self) -> None:
        self.spacing = 100
        self.top = rand_module.random() * (py5.height - self.spacing)
        self.bottom = self.top + self.spacing
        self.x = py5.width
        self.w = 20
        self.velocity = 2

    def collides(self, bird: Bird) -> bool:
        vertical_collision = bird.y < self.top or bird.y > self.bottom
        horizontal_collision = bird.x > self.x and bird.x < self.x + self.w
        return vertical_collision and horizontal_collision

    def show(self) -> None:
        py5.fill(0)
        py5.no_stroke()
        py5.rect(self.x, 0, self.w, self.top)
        py5.rect(self.x, self.bottom, self.w, py5.height - self.bottom)

    def update(self) -> None:
        self.x -= self.velocity

    def offscreen(self) -> bool:
        return self.x < -self.w


def all_birds_dead() -> bool:
    """Check if all birds are dead."""
    for bird in birds:
        if bird.alive:
            return False
    return True


def normalize_fitness() -> None:
    """Normalize fitness values."""
    total_fitness = sum(bird.fitness for bird in birds)
    if total_fitness > 0:
        for bird in birds:
            bird.fitness /= total_fitness


def weighted_selection() -> NeuralNetwork:
    """Select a bird based on fitness."""
    index = 0
    start = rand_module.random()
    while start > 0 and index < len(birds):
        start -= birds[index].fitness
        index += 1
    index = max(0, index - 1)
    return birds[index].brain


def reproduction() -> None:
    """Create next generation."""
    global birds, generation
    next_birds = []
    for _ in range(len(birds)):
        parent_a = weighted_selection()
        parent_b = weighted_selection()
        child = parent_a.crossover(parent_b)
        child.mutate(0.01)
        next_birds.append(Bird(child))
    birds = next_birds
    generation += 1


def reset_pipes() -> None:
    """Keep only the latest pipe."""
    global pipes
    if pipes:
        pipes = [pipes[-1]]
    else:
        pipes = [Pipe()]


def setup() -> None:
    global birds, pipes, generation
    py5.size(640, 240)
    birds = [Bird() for _ in range(200)]
    pipes = [Pipe()]
    generation = 0
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global birds, pipes, generation

    py5.background(255)

    # Update and display pipes
    i = len(pipes) - 1
    while i >= 0:
        pipes[i].update()
        pipes[i].show()
        if pipes[i].offscreen():
            pipes.pop(i)
        i -= 1

    # Update and display birds
    for bird in birds:
        if bird.alive:
            for pipe in pipes:
                if pipe.collides(bird):
                    bird.alive = False

            bird.think(pipes)
            bird.update()
            bird.show()

    # Add new pipe every 100 frames
    if py5.frame_count % 100 == 0:
        pipes.append(Pipe())

    # Check if all birds are dead
    if all_birds_dead():
        normalize_fitness()
        reproduction()
        reset_pipes()

    # Display generation
    py5.fill(0)
    py5.text_size(16)
    py5.text(f"Generation: {generation}", 10, 20)
    alive_count = sum(1 for bird in birds if bird.alive)
    py5.text(f"Alive: {alive_count}/{len(birds)}", 10, 40)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "flappy_bird_neuro_evolution_####.png"))


py5.run_sketch()
