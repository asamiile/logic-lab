from pathlib import Path
import random as rand_module

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

world: "World"


class DNA:
    def __init__(self, genes=None):
        if genes:
            self.genes = genes[:]
        else:
            self.genes = [rand_module.random() for _ in range(1)]

    def copy(self) -> "DNA":
        return DNA(self.genes)

    def mutate(self, mutation_rate: float) -> None:
        for i in range(len(self.genes)):
            if rand_module.random() < mutation_rate:
                self.genes[i] = rand_module.random()


class Bloop:
    def __init__(self, position: py5.Py5Vector, dna: DNA) -> None:
        self.position = py5.Py5Vector(position.x, position.y)
        self.health = 200.0
        self.xoff = rand_module.random() * 1000
        self.yoff = rand_module.random() * 1000
        self.dna = dna

        # DNA determines size and maxspeed
        # Bigger bloops are slower
        self.maxspeed = (1 - self.dna.genes[0]) * 15
        self.r = self.dna.genes[0] * 25

    def run(self) -> None:
        self.update()
        self.borders()
        self.show()

    def eat(self, food: "Food") -> None:
        positions = food.food_positions
        i = len(positions) - 1
        while i >= 0:
            dx = self.position.x - positions[i].x
            dy = self.position.y - positions[i].y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < self.r * 2:
                self.health += 100
                positions.pop(i)

            i -= 1

    def reproduce(self) -> "Bloop":
        if rand_module.random() < 0.0005:
            child_dna = self.dna.copy()
            child_dna.mutate(0.01)
            return Bloop(py5.Py5Vector(self.position.x, self.position.y), child_dna)
        else:
            return None

    def update(self) -> None:
        vx = (py5.noise(self.xoff) * 2 - 1) * self.maxspeed
        vy = (py5.noise(self.yoff) * 2 - 1) * self.maxspeed

        self.position.x += vx
        self.position.y += vy

        self.xoff += 0.01
        self.yoff += 0.01

        self.health -= 0.2

    def borders(self) -> None:
        if self.position.x < -self.r:
            self.position.x = py5.width + self.r
        if self.position.y < -self.r:
            self.position.y = py5.height + self.r
        if self.position.x > py5.width + self.r:
            self.position.x = -self.r
        if self.position.y > py5.height + self.r:
            self.position.y = -self.r

    def show(self) -> None:
        py5.stroke(0, self.health)
        py5.fill(0, self.health)
        py5.circle(self.position.x, self.position.y, self.r * 2)

    def dead(self) -> bool:
        return self.health < 0


class Food:
    def __init__(self, num: int) -> None:
        self.food_positions = [
            py5.Py5Vector(rand_module.random() * py5.width, rand_module.random() * py5.height)
            for _ in range(num)
        ]

    def add(self, position: py5.Py5Vector) -> None:
        self.food_positions.append(py5.Py5Vector(position.x, position.y))

    def run(self) -> None:
        for position in self.food_positions:
            py5.rect_mode(py5.CENTER)
            py5.stroke(0)
            py5.stroke_weight(1)
            py5.fill(200)
            py5.square(position.x, position.y, 8)

        if rand_module.random() < 0.001:
            self.food_positions.append(
                py5.Py5Vector(rand_module.random() * py5.width, rand_module.random() * py5.height)
            )


class World:
    def __init__(self, population_size: int) -> None:
        self.bloops = [
            Bloop(py5.Py5Vector(rand_module.random() * py5.width, rand_module.random() * py5.height), DNA())
            for _ in range(population_size)
        ]
        self.food = Food(population_size)

    def run(self) -> None:
        self.food.run()

        i = len(self.bloops) - 1
        while i >= 0:
            bloop = self.bloops[i]
            bloop.run()
            bloop.eat(self.food)

            if bloop.dead():
                self.bloops.pop(i)
                self.food.add(bloop.position)
            else:
                child = bloop.reproduce()
                if child:
                    self.bloops.append(child)

            i -= 1

    def born(self, x: float, y: float) -> None:
        position = py5.Py5Vector(x, y)
        dna = DNA()
        self.bloops.append(Bloop(position, dna))


def setup() -> None:
    global world
    py5.size(640, 240)
    world = World(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    world.run()


def mouse_pressed() -> None:
    world.born(py5.mouse_x, py5.mouse_y)


def mouse_dragged() -> None:
    world.born(py5.mouse_x, py5.mouse_y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "evolving_bloops_####.png"))


py5.run_sketch()
