import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
pendulums: list[dict] = []


def setup() -> None:
    global pendulums
    py5.size(1000, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(5):
        pendulums.append(
            {
                "angle1": math.pi / 4 + i * 0.001,
                "angle2": 0,
                "vel1": 0,
                "vel2": 0,
                "trail": [],
                "color": (100 + i * 30, 150, 255 - i * 30),
            }
        )


def draw() -> None:
    py5.background(20)

    g, L1, L2 = 1, 200, 150

    for pend in pendulums:
        a1, a2 = pend["angle1"], pend["angle2"]
        v1, v2 = pend["vel1"], pend["vel2"]

        a1_accel = (
            -g / L1 * math.sin(a1)
            - 0.5 * math.sin(a1 - a2) * (L2 * v2 * v2 + g * math.cos(a1 - a2)) / L1
        )
        a2_accel = -g / L2 * math.sin(a2) + L1 * v1 * v1 * math.sin(a1 - a2) / L2

        v1 += a1_accel * 0.01
        v2 += a2_accel * 0.01
        a1 += v1 * 0.01
        a2 += v2 * 0.01

        pend["angle1"] = a1
        pend["angle2"] = a2
        pend["vel1"] = v1 * 0.99
        pend["vel2"] = v2 * 0.99

        x1 = py5.width / 2 + L1 * math.sin(a1)
        y1 = 100 + L1 * math.cos(a1)
        x2 = x1 + L2 * math.sin(a2)
        y2 = y1 + L2 * math.cos(a2)

        pend["trail"].append((x2, y2))
        if len(pend["trail"]) > 100:
            pend["trail"].pop(0)

        py5.stroke(*pend["color"])
        py5.stroke_weight(1)
        for i in range(len(pend["trail"]) - 1):
            py5.line(
                pend["trail"][i][0],
                pend["trail"][i][1],
                pend["trail"][i + 1][0],
                pend["trail"][i + 1][1],
            )

        py5.stroke_weight(3)
        py5.line(py5.width / 2, 100, x1, y1)
        py5.line(x1, y1, x2, y2)
        py5.fill(*pend["color"])
        py5.circle(x2, y2, 3)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "double_pendulum_####.png"))


py5.run_sketch()
