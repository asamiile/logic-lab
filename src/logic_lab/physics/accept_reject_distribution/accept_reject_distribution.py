from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
TOTAL = 20

random_counts: list[int]


def accept_reject() -> float:
    while True:
        r1 = py5.random(1)
        probability = r1
        r2 = py5.random(1)

        if r2 < probability:
            return r1


def setup() -> None:
    global random_counts
    py5.size(640, 240)
    random_counts = [0] * TOTAL
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    index = int(accept_reject() * len(random_counts))
    random_counts[index] += 1

    py5.stroke(0)
    py5.stroke_weight(2)
    py5.fill(127)

    bar_width = py5.width / len(random_counts)
    for x, count in enumerate(random_counts):
        py5.rect(x * bar_width, py5.height - count, bar_width - 1, count)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "accept_reject_distribution_####.png"))


py5.run_sketch()
