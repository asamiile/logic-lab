from math import cos, radians, sin
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

SC_PRECISION = 0.5
SC_INV_PREC = 1 / SC_PRECISION
SC_PERIOD = int(360 * SC_INV_PREC)

sin_lut: list[float] = []
cos_lut: list[float] = []


def init_sin_cos() -> None:
    for i in range(SC_PERIOD):
        sin_lut.append(sin(radians(i * SC_PRECISION)))
        cos_lut.append(cos(radians(i * SC_PRECISION)))


def setup() -> None:
    py5.size(640, 240)
    init_sin_cos()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    radius = 50 + 50 * sin_lut[py5.frame_count % SC_PERIOD]

    for i in range(0, 360, 5):
        theta = int((i * SC_INV_PREC) % SC_PERIOD)
        py5.stroke_weight(4)
        py5.point(
            py5.width / 2 + radius * cos_lut[theta],
            py5.height / 2 + radius * sin_lut[theta],
        )


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "sine_cosine_lookup_table_####.png"))


py5.run_sketch()
