from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Pendulum:
    def __init__(self, x: float, y: float, r: float) -> None:
        self.pivot = py5.Py5Vector(x, y)
        self.bob = py5.Py5Vector(dim=2)
        self.r = r
        self.angle = py5.PI / 4

        self.angle_velocity = 0.0
        self.angle_acceleration = 0.0
        self.damping = 0.995
        self.ball_radius = 24.0
        self.dragging = False

    def update(self) -> None:
        if not self.dragging:
            gravity = 0.4
            self.angle_acceleration = ((-1 * gravity) / self.r) * py5.sin(self.angle)

            self.angle_velocity += self.angle_acceleration
            self.angle += self.angle_velocity
            self.angle_velocity *= self.damping

    def show(self) -> None:
        self.bob = py5.Py5Vector(
            self.r * py5.sin(self.angle),
            self.r * py5.cos(self.angle),
        )
        self.bob += self.pivot

        py5.stroke(0)
        py5.stroke_weight(2)
        py5.line(self.pivot.x, self.pivot.y, self.bob.x, self.bob.y)
        py5.fill(127)
        py5.circle(self.bob.x, self.bob.y, self.ball_radius * 2)

    def clicked(self, mx: float, my: float) -> None:
        d = py5.dist(mx, my, self.bob.x, self.bob.y)
        if d < self.ball_radius:
            self.dragging = True

    def stop_dragging(self) -> None:
        self.angle_velocity = 0
        self.dragging = False

    def drag(self) -> None:
        if self.dragging:
            mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
            diff = self.pivot - mouse
            self.angle = py5.atan2(-1 * diff.y, diff.x) - py5.radians(90)


pendulum: Pendulum


def setup() -> None:
    global pendulum
    py5.size(640, 240)
    pendulum = Pendulum(py5.width / 2, 0, 175)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    pendulum.update()
    pendulum.show()
    pendulum.drag()


def mouse_pressed() -> None:
    pendulum.clicked(py5.mouse_x, py5.mouse_y)


def mouse_released() -> None:
    pendulum.stop_dragging()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "swinging_pendulum_####.png"))


py5.run_sketch()
