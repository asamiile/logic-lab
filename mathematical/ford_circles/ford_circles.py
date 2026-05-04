from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class FractionCircle:
    numerator: int
    denominator: int
    x: float
    radius: float


max_denominator = 16
show_labels = False
show_baseline = True
show_fill = True
circles: list[FractionCircle] = []


def setup() -> None:
    py5.size(760, 520)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rebuild_circles()


def draw() -> None:
    py5.background(216, 14, 96)
    draw_scale_guides()
    draw_circles()
    draw_info()


def rebuild_circles() -> None:
    global circles

    values = []
    for denominator in range(1, max_denominator + 1):
        for numerator in range(0, denominator + 1):
            if gcd(numerator, denominator) == 1:
                x = numerator / denominator
                radius = 1 / (2 * denominator * denominator)
                values.append(FractionCircle(numerator, denominator, x, radius))

    circles = sorted(values, key=lambda item: (item.radius, item.x), reverse=True)


def draw_scale_guides() -> None:
    baseline = baseline_y()
    left = plot_left()
    width = plot_width()

    if show_baseline:
        py5.stroke(220, 22, 18, 52)
        py5.stroke_weight(2)
        py5.line(left, baseline, left + width, baseline)

        py5.stroke(220, 18, 42, 24)
        py5.stroke_weight(1)
        for i in range(11):
            x = left + width * i / 10
            py5.line(x, baseline - 6, x, baseline + 6)


def draw_circles() -> None:
    baseline = baseline_y()
    left = plot_left()
    width = plot_width()
    scale = plot_scale()

    for circle in circles:
        radius = circle.radius * scale
        x = left + circle.x * width
        y = baseline - radius
        hue = (196 + circle.denominator * 13 + circle.numerator * 9) % 360

        if show_fill:
            py5.fill(hue, 54, 92, 46 + min(34, radius * 0.5))
        else:
            py5.no_fill()
        py5.stroke((hue + 22) % 360, 74, 38, 86)
        py5.stroke_weight(max(0.7, min(2.2, radius * 0.045)))
        py5.circle(x, y, radius * 2)

        if show_labels and radius > 12:
            py5.no_stroke()
            py5.fill(220, 34, 12, 88)
            label = f"{circle.numerator}/{circle.denominator}"
            py5.text(label, x - py5.text_width(label) * 0.5, y + 4)


def plot_left() -> float:
    return 60


def plot_width() -> float:
    return py5.width - 120


def baseline_y() -> float:
    return py5.height - 78


def plot_scale() -> float:
    return min(py5.width - 120, py5.height * 0.92)


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 575, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Ford circles | denominator <= {max_denominator} | circles {len(circles)} | +/-: denominator | l: labels | b: baseline | f: fill | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global max_denominator, show_labels, show_baseline, show_fill

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "ford_circles_####.png"))
    elif py5.key == "+":
        max_denominator = min(42, max_denominator + 1)
        rebuild_circles()
    elif py5.key == "-":
        max_denominator = max(2, max_denominator - 1)
        rebuild_circles()
    elif py5.key == "l":
        show_labels = not show_labels
    elif py5.key == "b":
        show_baseline = not show_baseline
    elif py5.key == "f":
        show_fill = not show_fill


py5.run_sketch()
