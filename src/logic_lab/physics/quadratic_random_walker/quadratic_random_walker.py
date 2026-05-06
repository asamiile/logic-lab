from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def accept_reject() -> float:
    while True:
        r1 = py5.random(1)
        probability = r1 * r1
        r2 = py5.random(1)
        if r2 < probability:
            return r1


class Walker:
    def __init__(self) -> None:
        self.x = py5.width / 2
        self.y = py5.height / 2

    def show(self) -> None:
        py5.stroke(0)
        py5.point(self.x, self.y)

    def step(self) -> None:
        step = 5
        xstep = accept_reject() * step
        if py5.random(1) < 0.5:
            xstep *= -1
        ystep = accept_reject() * step
        if py5.random(1) < 0.5:
            ystep *= -1
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
        py5.save_frame(str(SCREENSHOT_DIR / "quadratic_random_walker_####.png"))


py5.run_sketch()
