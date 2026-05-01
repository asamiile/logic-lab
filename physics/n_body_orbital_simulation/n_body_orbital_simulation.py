from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self, x: float, y: float, vx: float, vy: float, mass: float) -> None:
        self.pos = py5.Py5Vector(x, y)
        self.vel = py5.Py5Vector(vx, vy)
        self.acc = py5.Py5Vector(0, 0)
        self.mass = mass
        self.r = py5.sqrt(self.mass)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acc += force / self.mass

    def attract(self, other: "Mover") -> None:
        force = self.pos - other.pos
        dist_sq = py5.constrain(force.mag ** 2, 100, 1000)
        strength = (self.mass * other.mass) / dist_sq
        other.apply_force(force.norm * strength)

    def update(self) -> None:
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(0, 100)
        py5.circle(self.pos.x, self.pos.y, self.r * 2)


movers: list[Mover]
sun: Mover


def setup() -> None:
    global movers, sun
    py5.size(640, 240)
    movers = []
    for _ in range(100):
        direction = py5.Py5Vector.random(dim=2)
        pos = direction * py5.random(100, 150)
        vel = py5.Py5Vector(-direction.y, direction.x) * py5.random(10, 15)
        mass = py5.random(10, 15)
        movers.append(Mover(pos.x, pos.y, vel.x, vel.y, mass))
    sun = Mover(0, 0, 0, 0, 500)
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255, 50)
    py5.translate(py5.width / 2, py5.height / 2)

    for mover in movers:
        sun.attract(mover)
        for other in movers:
            if mover is not other:
                mover.attract(other)

    for mover in movers:
        mover.update()
        mover.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "n_body_orbital_simulation_####.png"))


py5.run_sketch()
