import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def setup() -> None:
    py5.size(1000, 1000)
    py5.background(20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_ulam_spiral()


def draw_ulam_spiral() -> None:
    py5.stroke_weight(4)
    py5.no_fill()

    center_x, center_y = py5.width / 2, py5.height / 2
    spacing = 10
    n = 1
    x, y = 0, 0
    step = 1

    for _ in range(3000):
        if is_prime(n):
            py5.stroke(255, 150, 150)
            py5.point(center_x + x * spacing, center_y + y * spacing)

        n += 1

        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
            step += 1

        if x <= 0 and y < 0:
            x += 1
        elif x > 0 and y < 0:
            y += 1
        elif x > 0 and y >= 0:
            x -= 1
        else:
            y -= 1


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "prime_spiral_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
