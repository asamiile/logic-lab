from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Bob:
    def __init__(self, x: float, y: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.mass = 24
        self.damping = 0.98
        self.drag_offset = py5.Py5Vector(0, 0)
        self.dragging = False

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity *= self.damping
        self.position += self.velocity
        self.acceleration *= 0

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force / self.mass

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(2)
        if self.dragging:
            py5.fill(200)
        else:
            py5.fill(127)
        py5.circle(self.position.x, self.position.y, self.mass * 2)

    def handle_click(self, mx: float, my: float) -> None:
        d = py5.dist(mx, my, self.position.x, self.position.y)
        if d < self.mass:
            self.dragging = True
            self.drag_offset = self.position - py5.Py5Vector(mx, my)

    def stop_dragging(self) -> None:
        self.dragging = False

    def handle_drag(self, mx: float, my: float) -> None:
        if self.dragging:
            self.position = py5.Py5Vector(mx, my) + self.drag_offset


class Spring:
    def __init__(self, x: float, y: float, length: float) -> None:
        self.anchor = py5.Py5Vector(x, y)
        self.rest_length = length
        self.k = 0.2

    def connect(self, bob: Bob) -> None:
        force = bob.position - self.anchor
        current_length = force.mag
        stretch = current_length - self.rest_length

        if current_length > 0:
            force = force.norm * (-1 * self.k * stretch)
            bob.apply_force(force)

    def constrain_length(self, bob: Bob, min_length: float, max_length: float) -> None:
        direction = bob.position - self.anchor
        length = direction.mag

        if length == 0:
            return

        if length < min_length:
            bob.position = self.anchor + direction.norm * min_length
            bob.velocity *= 0
        elif length > max_length:
            bob.position = self.anchor + direction.norm * max_length
            bob.velocity *= 0

    def show(self) -> None:
        py5.fill(127)
        py5.circle(self.anchor.x, self.anchor.y, 10)

    def show_line(self, bob: Bob) -> None:
        py5.stroke(0)
        py5.line(bob.position.x, bob.position.y, self.anchor.x, self.anchor.y)


bob: Bob
spring: Spring


def setup() -> None:
    global bob, spring
    py5.size(640, 240)
    spring = Spring(py5.width / 2, 10, 100)
    bob = Bob(py5.width / 2, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    gravity = py5.Py5Vector(0, 2)
    bob.apply_force(gravity)

    bob.update()
    bob.handle_drag(py5.mouse_x, py5.mouse_y)

    spring.connect(bob)
    spring.constrain_length(bob, 30, 200)

    spring.show_line(bob)
    bob.show()
    spring.show()


def mouse_pressed() -> None:
    bob.handle_click(py5.mouse_x, py5.mouse_y)


def mouse_released() -> None:
    bob.stop_dragging()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "spring_connection_####.png"))


py5.run_sketch()
