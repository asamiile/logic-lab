from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Mover:
    def __init__(self, x: float, y: float, mass: float) -> None:
        self.mass = mass
        self.radius = mass * 8
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(1, 0)
        self.acceleration = py5.Py5Vector(0, 0)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force / self.mass

    def update(self) -> None:
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(127, 127)
        py5.circle(self.position.x, self.position.y, self.radius * 2)


class Attractor:
    def __init__(self) -> None:
        self.position = py5.Py5Vector(py5.width / 2, py5.height / 2)
        self.mass = 20
        self.g = 1.0
        self.drag_offset = py5.Py5Vector(0, 0)
        self.dragging = False
        self.rollover = False

    def attract(self, mover: Mover) -> py5.Py5Vector:
        force = self.position - mover.position
        distance = py5.constrain(force.mag, 5, 25)
        strength = (self.g * self.mass * mover.mass) / (distance * distance)
        return force.norm * strength

    def show(self) -> None:
        py5.stroke_weight(4)
        py5.stroke(0)
        if self.dragging:
            py5.fill(50)
        elif self.rollover:
            py5.fill(100)
        else:
            py5.fill(175, 200)
        py5.circle(self.position.x, self.position.y, self.mass * 2)

    def handle_press(self, mx: float, my: float) -> None:
        d = py5.dist(mx, my, self.position.x, self.position.y)
        if d < self.mass:
            self.dragging = True
            self.drag_offset = py5.Py5Vector(self.position.x - mx, self.position.y - my)

    def handle_hover(self, mx: float, my: float) -> None:
        d = py5.dist(mx, my, self.position.x, self.position.y)
        self.rollover = d < self.mass

    def stop_dragging(self) -> None:
        self.dragging = False

    def handle_drag(self, mx: float, my: float) -> None:
        if self.dragging:
            self.position = py5.Py5Vector(mx + self.drag_offset.x, my + self.drag_offset.y)


movers: list[Mover]
attractor: Attractor


def setup() -> None:
    global movers, attractor
    py5.size(640, 240)
    movers = [
        Mover(py5.random(py5.width), py5.random(py5.height), py5.random(0.5, 3)) for _ in range(10)
    ]
    attractor = Attractor()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    attractor.show()

    for mover in movers:
        force = attractor.attract(mover)
        mover.apply_force(force)
        mover.update()
        mover.show()


def mouse_moved() -> None:
    attractor.handle_hover(py5.mouse_x, py5.mouse_y)


def mouse_pressed() -> None:
    attractor.handle_press(py5.mouse_x, py5.mouse_y)


def mouse_dragged() -> None:
    attractor.handle_hover(py5.mouse_x, py5.mouse_y)
    attractor.handle_drag(py5.mouse_x, py5.mouse_y)


def mouse_released() -> None:
    attractor.stop_dragging()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "attraction_with_many_movers_####.png"))


py5.run_sketch()
