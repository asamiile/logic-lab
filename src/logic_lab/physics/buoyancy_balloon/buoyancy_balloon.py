from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Balloon:
    def __init__(self, width: float, height: float) -> None:
        self.position = py5.Py5Vector(width / 2, height / 2)
        self.velocity = py5.Py5Vector(0, 0)
        self.acceleration = py5.Py5Vector(0, 0)
        self.helium = py5.Py5Vector(0, -0.02)
        self.noise_x = 1000.0
        self.top_speed = 5.0
        self.diameter = height / 5
        self.stroke_weight = 1
        self.triangle_size = 5

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def should_bounce(self) -> bool:
        return self.position.y - self.diameter / 2 - self.stroke_weight < 0

    def update(self) -> None:
        if self.should_bounce():
            self.position.y = self.diameter / 2 - self.stroke_weight + 2
            self.velocity.y *= -0.75

        self.apply_force(self.helium)

        wind_x = py5.remap(py5.noise(self.noise_x), 0, 1, -0.01, 0.01)
        self.apply_force(py5.Py5Vector(wind_x, 0))

        self.velocity += self.acceleration
        if self.velocity.mag > self.top_speed:
            self.velocity = self.velocity.norm * self.top_speed

        self.position += self.velocity
        self.check_sides()
        self.acceleration *= 0
        self.noise_x += 0.01

    def check_sides(self) -> None:
        if self.position.x > py5.width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = py5.width

    def show(self) -> None:
        py5.stroke(0)
        py5.stroke_weight(self.stroke_weight)

        py5.fill(255, 182, 193)
        py5.circle(self.position.x, self.position.y, self.diameter)

        balloon_bottom = self.position.y + self.diameter / 2
        ts = self.triangle_size
        py5.triangle(
            self.position.x,
            balloon_bottom,
            self.position.x + ts,
            balloon_bottom + ts,
            self.position.x - ts,
            balloon_bottom + ts,
        )

        py5.line(
            self.position.x,
            balloon_bottom + ts,
            self.position.x,
            balloon_bottom + ts * 20,
        )


balloon: Balloon


def setup() -> None:
    global balloon
    py5.size(640, 240)
    balloon = Balloon(py5.width, py5.height)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    balloon.update()
    balloon.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "buoyancy_balloon_####.png"))


py5.run_sketch()
