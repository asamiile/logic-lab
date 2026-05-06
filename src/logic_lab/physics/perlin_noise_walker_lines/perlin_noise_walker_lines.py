from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Walker:
    def __init__(self) -> None:
        self.x = py5.width / 2
        self.y = py5.height / 2
        self.old_x = self.x
        self.old_y = self.y
        self.tx = 0.0
        self.ty = 10000.0

    def step(self) -> None:
        self.x += py5.remap(py5.noise(self.tx), 0, 1, -1, 1)
        self.y += py5.remap(py5.noise(self.ty), 0, 1, -1, 1)
        self.tx += 0.01
        self.ty += 0.01

    def show(self) -> None:
        py5.stroke(0)
        py5.line(self.old_x, self.old_y, self.x, self.y)
        self.old_x = self.x
        self.old_y = self.y


walker: Walker


def setup() -> None:
    global walker
    py5.size(640, 240)
    walker = Walker()
    py5.background(255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    walker.step()
    walker.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "perlin_noise_walker_lines_####.png"))


py5.run_sketch()
