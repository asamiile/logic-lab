from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rot_x = py5.PI / 1.5
rot_y = py5.PI / 3


class Ball:
    def __init__(self, box_size: int) -> None:
        self.box_size = box_size
        self.position = py5.Py5Vector(0, 0, 0)
        self.velocity = py5.Py5Vector(2, 6, 5)
        self.radius = 10

    def update(self) -> None:
        self.position += self.velocity

    def check_edges(self) -> None:
        half = self.box_size / 2 - self.radius
        if self.position.x > half or self.position.x < -half:
            self.velocity.x *= -1
        if self.position.y > half or self.position.y < -half:
            self.velocity.y *= -1
        if self.position.z > half or self.position.z < -half:
            self.velocity.z *= -1

    def show(self) -> None:
        py5.push()
        py5.translate(self.position.x, self.position.y, self.position.z)
        # Approximate normalMaterial(): ambient base + RGB directional lights per axis
        py5.ambient_light(128, 128, 128)
        py5.directional_light(127, 0, 0, -1, 0, 0)  # red for +X normals
        py5.directional_light(0, 127, 0, 0, -1, 0)  # green for +Y normals
        py5.directional_light(0, 0, 127, 0, 0, -1)  # blue for +Z normals (front)
        py5.fill(255)
        py5.no_stroke()
        py5.sphere(self.radius)
        py5.pop()


ball: Ball
box_size: int


def setup() -> None:
    global ball, box_size
    py5.size(640, 240, py5.P3D)
    box_size = py5.width // 4
    ball = Ball(box_size)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    # P3D origin is top-left; translate to center to match WEBGL behaviour
    py5.translate(py5.width / 2, py5.height / 2, 0)
    py5.no_fill()
    py5.rotate_y(rot_y)
    py5.rotate_x(rot_x)
    py5.box(box_size)
    ball.update()
    ball.check_edges()
    ball.show()


def mouse_dragged() -> None:
    global rot_x, rot_y
    rot_y += (py5.mouse_x - py5.pmouse_x) * 0.01
    rot_x += (py5.mouse_y - py5.pmouse_y) * 0.01


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "bouncing_ball_3d_####.png"))


py5.run_sketch()
