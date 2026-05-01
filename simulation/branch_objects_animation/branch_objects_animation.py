from pathlib import Path
import math

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

tree: list["Branch"] = []
leaves: list["Leaf"] = []


class Branch:
    def __init__(self, start_pos: py5.Py5Vector, velocity: py5.Py5Vector, timer_start: float) -> None:
        self.start = py5.Py5Vector(start_pos.x, start_pos.y)
        self.end = py5.Py5Vector(start_pos.x, start_pos.y)
        self.vel = py5.Py5Vector(velocity.x, velocity.y)
        self.timer_start = timer_start
        self.timer = self.timer_start
        self.growing = True

    def update(self) -> None:
        if self.growing:
            self.end += self.vel

    def show(self) -> None:
        py5.stroke(0)
        py5.line(self.start.x, self.start.y, self.end.x, self.end.y)

    def time_to_branch(self) -> bool:
        self.timer -= 1
        if self.timer < 0 and self.growing:
            self.growing = False
            return True
        else:
            return False

    def branch(self, angle: float) -> "Branch":
        # Get heading and magnitude of current velocity
        theta = math.atan2(self.vel.y, self.vel.x)
        mag = (self.vel.x * self.vel.x + self.vel.y * self.vel.y) ** 0.5

        # Rotate by angle (convert degrees to radians)
        theta += math.radians(angle)

        # Create new velocity from angle
        new_vel_x = math.cos(theta) * mag
        new_vel_y = math.sin(theta) * mag
        new_vel = py5.Py5Vector(new_vel_x, new_vel_y)

        return Branch(self.end, new_vel, self.timer_start * 0.66)


class Leaf:
    def __init__(self, position: py5.Py5Vector) -> None:
        self.pos = py5.Py5Vector(position.x, position.y)

    def show(self) -> None:
        py5.no_stroke()
        py5.fill(50, 100)
        py5.circle(self.pos.x, self.pos.y, 4)


def setup() -> None:
    py5.size(640, 240)
    py5.background(255)

    # Setup initial branch
    start = py5.Py5Vector(py5.width / 2, py5.height)
    direction = py5.Py5Vector(0, -1)
    b = Branch(start, direction, 80)
    tree.append(b)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    # Update and draw all branches
    for i in range(len(tree) - 1, -1, -1):
        b = tree[i]
        b.update()
        b.show()

        # Check if branch should split
        if b.time_to_branch():
            if len(tree) < 1024:
                tree.append(b.branch(30))
                tree.append(b.branch(-25))
            else:
                leaves.append(Leaf(b.end))

    # Draw all leaves
    for leaf in leaves:
        leaf.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "branch_objects_animation_####.png"))


py5.run_sketch()
