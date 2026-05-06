from pathlib import Path

import py5
import pymunk

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
movers: list["Mover"] = []
attractor: "Attractor"

G = 0.2
MATTER_DENSITY = 0.001
# Pymunk integrates force in SI-like units (seconds), while Matter.js examples
# are tuned for Matter's per-step scale. This bridges that scale gap.
FORCE_SCALE = 36000.0


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Mover:
    def __init__(self, x: float, y: float, radius: float) -> None:
        self.radius = radius
        # Approximate Matter.js default mass behavior: density * area
        mass = MATTER_DENSITY * py5.PI * radius * radius
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, py5.height - y)

        # Random velocity: 2 * (cos(angle), sin(angle))
        angle = py5.random(py5.TWO_PI)
        self.body.velocity = (2 * py5.cos(angle), 2 * py5.sin(angle))

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 1.0
        # Matter.js default surface friction is 0.1 unless overridden.
        self.shape.friction = 0.1

        space.add(self.body, self.shape)

    def apply_force(self, force: tuple[float, float]) -> None:
        scaled_force = (force[0] * FORCE_SCALE, force[1] * FORCE_SCALE)
        self.body.apply_force_at_world_point(scaled_force, self.body.position)

    def show(self) -> None:
        px = float(self.body.position.x)
        py_ = to_screen_y(float(self.body.position.y))

        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.push()
        py5.translate(px, py_)
        py5.rotate(-self.body.angle)
        py5.circle(0, 0, self.radius * 2)
        py5.line(0, 0, self.radius, 0)
        py5.pop()


class Attractor:
    def __init__(self, x: float, y: float) -> None:
        self.radius = 32
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x, py5.height - y)
        self.shape = pymunk.Circle(self.body, self.radius)
        space.add(self.body, self.shape)

    def attract(self, mover: Mover) -> tuple[float, float]:
        # Vector from mover to attractor (same as Vector.sub(attractor.pos, mover.pos))
        force_x = self.body.position.x - mover.body.position.x
        force_y = self.body.position.y - mover.body.position.y

        # Distance (unconstrained for normalization)
        distance = (force_x * force_x + force_y * force_y) ** 0.5

        # Constrain distance for strength calculation only
        distance_constrained = max(5, min(25, distance))

        # Calculate strength with constrained distance
        strength = (G * 1.0 * mover.body.mass) / (distance_constrained * distance_constrained)

        # Normalize using unconstrained distance, then scale by strength
        if distance > 0:
            force_x = (force_x / distance) * strength
            force_y = (force_y / distance) * strength
        else:
            force_x = 0
            force_y = 0

        return (force_x, force_y)

    def show(self) -> None:
        ax = float(self.body.position.x)
        ay = to_screen_y(float(self.body.position.y))

        py5.fill(0)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.push()
        py5.translate(ax, ay)
        py5.circle(0, 0, self.radius * 2)
        py5.pop()


def setup() -> None:
    global space, attractor
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, 0)
    # Match Matter.js feel a bit closer.
    space.damping = 1.0
    space.iterations = 6

    for _ in range(100):
        movers.append(Mover(py5.random(py5.width), py5.random(py5.height), py5.random(4, 8)))

    attractor = Attractor(py5.width / 2, py5.height / 2)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    # Match Matter.js flow: apply forces, then step engine, then render.
    for mover in movers:
        force = attractor.attract(mover)
        mover.apply_force(force)

    space.step(1 / 60)

    for mover in movers:
        mover.show()

    attractor.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "matter_js_attraction_####.png"))


py5.run_sketch()
