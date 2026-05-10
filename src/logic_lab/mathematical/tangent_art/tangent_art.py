from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
circle_count = 8


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.01

    center_radius = 150

    circles = []
    for i in range(circle_count):
        angle = (2 * math.pi * i / circle_count) + time_value * 0.3
        cx = center_radius * math.cos(angle)
        cy = center_radius * math.sin(angle)
        radius = 20 + 15 * math.sin(time_value + i * 0.5)
        circles.append((cx, cy, max(5, radius)))

    py5.no_fill()
    py5.stroke_weight(1.2)

    for i in range(circle_count):
        for j in range(i + 1, circle_count):
            x1, y1, r1 = circles[i]
            x2, y2, r2 = circles[j]

            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > r1 + r2 + 1:
                angle = math.atan2(dy, dx)
                alpha = math.asin((r2 - r1) / dist) if dist > abs(r2 - r1) else 0

                for offset in [-1, 1]:
                    tangent_angle = angle + alpha * offset
                    px1 = x1 + r1 * math.cos(tangent_angle + math.pi / 2)
                    py1 = y1 + r1 * math.sin(tangent_angle + math.pi / 2)
                    px2 = x2 + r2 * math.cos(tangent_angle + math.pi / 2)
                    py2 = y2 + r2 * math.sin(tangent_angle + math.pi / 2)

                    hue = (angle * 180 / math.pi + i * 45 + time_value * 60) % 360
                    py5.stroke(hue, 70, 100)
                    py5.line(px1, py1, px2, py2)

    py5.fill(200, 40, 90)
    py5.no_stroke()
    for cx, cy, r in circles:
        py5.circle(cx, cy, r)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "tangent_art_####.png"))


py5.run_sketch()
