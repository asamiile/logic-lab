from pathlib import Path

import pymunk
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

space: pymunk.Space
windmill: "Windmill"
particles: list["Particle"] = []


def to_screen_y(pymunk_y: float) -> float:
    return py5.height - pymunk_y


class Windmill:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.w = w
        self.h = h
        mass = 1.0
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, (w, h)))
        body.position = (x, py5.height - y)
        self.shape = pymunk.Poly.create_box(body, (w, h))
        self.shape.elasticity = 0.3
        self.shape.friction = 0.1
        space.add(body, self.shape)

        # PivotJoint: pins the blade center to a fixed world point, allowing free rotation
        self.joint = pymunk.constraints.PivotJoint(body, space.static_body, body.position)
        space.add(self.joint)

    def show(self) -> None:
        body = self.shape.body
        bx = float(body.position.x)
        by = to_screen_y(float(body.position.y))

        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)

        # Blade via world-space vertices
        py5.begin_shape()
        for v in self.shape.get_vertices():
            wv = body.local_to_world(v)
            py5.vertex(float(wv.x), to_screen_y(float(wv.y)))
        py5.end_shape(py5.CLOSE)

        # Pole from blade center to bottom of screen
        py5.line(bx, by, bx, py5.height)


class Particle:
    def __init__(self, x: float, y: float) -> None:
        self.r = 8
        body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, self.r))
        body.position = (x, py5.height - y)
        self.shape = pymunk.Circle(body, self.r)
        self.shape.elasticity = 0.6
        space.add(body, self.shape)

    def show(self) -> None:
        body = self.shape.body
        px = float(body.position.x)
        py_ = to_screen_y(float(body.position.y))

        py5.fill(127)
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.push()
        py5.translate(px, py_)
        py5.rotate(-body.angle)
        py5.circle(0, 0, self.r * 2)
        py5.line(0, 0, self.r, 0)
        py5.pop()

    def check_edge(self) -> bool:
        return self.shape.body.position.y < -self.r

    def remove_body(self) -> None:
        space.remove(self.shape.body, self.shape)


def setup() -> None:
    global space, windmill
    py5.size(640, 240)

    space = pymunk.Space()
    space.gravity = (0, -1000)

    windmill = Windmill(py5.width / 2, py5.height - 50, 120, 10)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    if py5.random(1) < 0.05:
        particles.append(Particle(py5.width / 2 + py5.random(-60, 60), 0))

    space.step(1 / 60)

    windmill.show()

    for i in range(len(particles) - 1, -1, -1):
        particles[i].show()
        if particles[i].check_edge():
            particles[i].remove_body()
            particles.pop(i)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "windmill_####.png"))


py5.run_sketch()
