from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SOLVER_ITERATIONS = 8

show_physics = True
show_particles = True
clusters: list["Cluster"] = []
springs: list["Spring"] = []
min_distance_springs: list["MinDistanceSpring"] = []


class Particle:
    def __init__(self, x: float, y: float, r: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = r

    def update(self) -> None:
        velocity = self.position - self.previous
        current = self.position.copy
        self.position += velocity + self.acceleration
        self.previous = current
        self.acceleration *= 0

    def constrain_to_world(self) -> None:
        x = min(max(self.position.x, 0), py5.width)
        y = min(max(self.position.y, 0), py5.height)
        if x != self.position.x or y != self.position.y:
            self.position = py5.Py5Vector(x, y)
            self.previous = self.position.copy

    def show(self) -> None:
        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.circle(self.position.x, self.position.y, self.r * 2)


class Spring:
    def __init__(self, a: Particle, b: Particle, rest_length: float, strength: float) -> None:
        self.a = a
        self.b = b
        self.rest_length = rest_length
        self.strength = strength

    def update(self) -> None:
        delta = self.b.position - self.a.position
        distance = delta.mag
        if distance == 0:
            return
        diff = (distance - self.rest_length) / distance
        correction = delta * (0.5 * self.strength * diff)
        self.a.position += correction
        self.b.position -= correction


class MinDistanceSpring:
    def __init__(self, a: Particle, b: Particle, min_distance: float, strength: float) -> None:
        self.a = a
        self.b = b
        self.min_distance = min_distance
        self.strength = strength

    def update(self) -> None:
        delta = self.b.position - self.a.position
        distance = delta.mag
        if distance == 0 or distance >= self.min_distance:
            return
        diff = (distance - self.min_distance) / distance
        correction = delta * (0.5 * self.strength * diff)
        self.a.position += correction
        self.b.position -= correction


class Cluster:
    def __init__(self, n: int, length: float) -> None:
        self.particles: list[Particle] = []
        self.length = length

        for _ in range(n):
            x = py5.width / 2 + py5.random(-1, 1)
            y = py5.height / 2 + py5.random(-1, 1)
            self.particles.append(Particle(x, y, 4))

        for i in range(len(self.particles) - 1):
            pi = self.particles[i]
            for j in range(i + 1, len(self.particles)):
                pj = self.particles[j]
                springs.append(Spring(pi, pj, length, 0.01))

    def connect(self, other: "Cluster") -> None:
        for i in range(len(self.particles)):
            pi = self.particles[i]
            for j in range(len(other.particles)):
                pj = other.particles[j]
                min_distance_springs.append(
                    MinDistanceSpring(pi, pj, (self.length + other.length) * 0.5, 0.05)
                )

    def show(self) -> None:
        for p in self.particles:
            p.show()

    def show_connections(self, other: "Cluster | None" = None) -> None:
        if other is None:
            other = self
            py5.stroke(0, 50)
            py5.stroke_weight(2)
        else:
            py5.stroke(0, 50)
            py5.stroke_weight(0.25)

        for i in range(len(self.particles)):
            pi = self.particles[i]
            for j in range(len(other.particles)):
                pj = other.particles[j]
                py5.line(pi.position.x, pi.position.y, pj.position.x, pj.position.y)


def new_graph() -> None:
    global clusters, springs, min_distance_springs
    clusters = []
    springs = []
    min_distance_springs = []

    for _ in range(8):
        clusters.append(Cluster(int(py5.random(3, 8)), py5.random(20, 100)))

    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            clusters[i].connect(clusters[j])


def setup() -> None:
    py5.size(640, 240)
    new_graph()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    for cluster in clusters:
        for p in cluster.particles:
            p.update()

    for _ in range(SOLVER_ITERATIONS):
        for spring in springs:
            spring.update()
        for min_spring in min_distance_springs:
            min_spring.update()
        for cluster in clusters:
            for p in cluster.particles:
                p.constrain_to_world()

    py5.background(255)

    if show_particles:
        for cluster in clusters:
            cluster.show()

    if show_physics:
        for i in range(len(clusters)):
            clusters[i].show_connections()
            for j in range(i + 1, len(clusters)):
                clusters[i].show_connections(clusters[j])


def key_pressed() -> None:
    global show_physics, show_particles
    if py5.key == "c":
        show_physics = not show_physics
        if not show_physics:
            show_particles = True
    elif py5.key == "p":
        show_particles = not show_particles
        if not show_particles:
            show_physics = True
    elif py5.key == "n":
        new_graph()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "exercise_6_13_force_directed_graph_####.png"))


py5.run_sketch()
