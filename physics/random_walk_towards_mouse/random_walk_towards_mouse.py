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
        r = py5.random(1)
        if r < 0.5:
            if r < 0.25:
                if self.x < py5.mouse_x:
                    self.x += 1
                else:
                    self.x -= 1
            else:
                if self.y < py5.mouse_y:
                    self.y += 1
                else:
                    self.y -= 1
        else:
            choice = int(py5.random(4))
            if choice == 0:
                self.x += 1
            elif choice == 1:
                self.x -= 1
            elif choice == 2:
                self.y += 1
            else:
                self.y -= 1


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
        py5.save_frame(
            str(SCREENSHOT_DIR / "random_walk_towards_mouse_####.png")
        )


py5.run_sketch()
