from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Walker:
    def __init__(self) -> None:
        self.x = py5.width / 2
        self.y = py5.height / 2

    def show(self) -> None:
        py5.stroke(0)
        py5.point(self.x, self.y)

    def step(self) -> None:
        xstep = py5.random_gaussian(0, 3)
        ystep = py5.random_gaussian(0, 3)
        self.x += xstep
        self.y += ystep


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
        py5.save_frame(str(SCREENSHOT_DIR / "gaussian_random_walker_####.png"))


py5.run_sketch()
