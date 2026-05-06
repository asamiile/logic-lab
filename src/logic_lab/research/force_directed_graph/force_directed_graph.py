from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SOLVER_ITERATIONS = 8

show_physics = True
show_particles = True
cluster: "Cluster"


def make_cluster() -> "Cluster":
    return Cluster(int(py5.random(2, 20)), py5.random(10, py5.height / 2))


class Particle:
    def __init__(self, x: float, y: float, r: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.previous = py5.Py5Vector(x, y)
        self.acceleration = py5.Py5Vector(0, 0)
        self.r = r

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def update(self) -> None:
        velocity = self.position - self.previous
        current = self.position.copy
        self.position += velocity + self.acceleration
        self.previous = current
        self.acceleration *= 0

    def show(self) -> None:
        py5.fill(127)
        py5.stroke(0)
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


class Cluster:
    def __init__(self, n: int, length: float) -> None:
        self.particles: list[Particle] = []
        self.springs: list[Spring] = []

        for _ in range(n):
            x = py5.width / 2 + py5.random(-1, 1)
            y = py5.height / 2 + py5.random(-1, 1)
            self.particles.append(Particle(x, y, 4))

        for i in range(len(self.particles) - 1):
            particle_i = self.particles[i]
            for j in range(i + 1, len(self.particles)):
                particle_j = self.particles[j]
                self.springs.append(Spring(particle_i, particle_j, length, 0.01))

    def update(self) -> None:
        for particle in self.particles:
            particle.update()

        for _ in range(SOLVER_ITERATIONS):
            for spring in self.springs:
                spring.update()

    def show(self) -> None:
        for particle in self.particles:
            particle.show()

    def show_connections(self) -> None:
        py5.stroke(0, 150)
        py5.stroke_weight(2)
        for i in range(len(self.particles) - 1):
            pi = self.particles[i]
            for j in range(i + 1, len(self.particles)):
                pj = self.particles[j]
                py5.line(pi.position.x, pi.position.y, pj.position.x, pj.position.y)


def setup() -> None:
    global cluster
    py5.size(640, 240)
    cluster = make_cluster()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global cluster
    cluster.update()

    py5.background(255)

    if py5.frame_count % 120 == 0:
        cluster = make_cluster()

    if show_particles:
        cluster.show()

    if show_physics:
        cluster.show_connections()


def key_pressed() -> None:
    global show_physics, show_particles, cluster

    if py5.key == "c":
        show_physics = not show_physics
        if not show_physics:
            show_particles = True
    elif py5.key == "p":
        show_particles = not show_particles
        if not show_particles:
            show_physics = True
    elif py5.key == "n":
        cluster = make_cluster()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "force_directed_graph_####.png"))


py5.run_sketch()
