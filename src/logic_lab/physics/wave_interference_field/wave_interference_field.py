from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

STEP = 5
show_sources = True
phase = 0.0


@dataclass(frozen=True)
class Source:
    x: float
    y: float
    wavelength: float
    offset: float


sources: list[Source] = []


def setup() -> None:
    py5.size(720, 440)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_sources()


def reset_sources() -> None:
    global sources
    sources = [
        Source(py5.width * 0.25, py5.height * 0.34, 42, 0.0),
        Source(py5.width * 0.74, py5.height * 0.39, 42, 1.6),
        Source(py5.width * 0.50, py5.height * 0.72, 58, 3.1),
    ]


def draw() -> None:
    global phase
    phase += 0.045
    py5.background(235, 26, 8)
    py5.no_stroke()

    for y in range(0, py5.height, STEP):
        for x in range(0, py5.width, STEP):
            total = 0.0
            for source in sources:
                distance = math.hypot(x - source.x, y - source.y)
                total += math.cos(py5.TWO_PI * distance / source.wavelength - phase - source.offset)
            normalized = total / len(sources)
            brightness = py5.constrain(48 + normalized * 48, 3, 96)
            saturation = 48 + abs(normalized) * 42
            py5.fill(205 + normalized * 38, saturation, brightness, 96)
            py5.rect(x, y, STEP + 1, STEP + 1)

    if show_sources:
        py5.stroke(48, 80, 100)
        py5.stroke_weight(2)
        py5.fill(48, 70, 98, 92)
        for source in sources:
            py5.circle(source.x, source.y, 12)


def mouse_pressed() -> None:
    sources.append(Source(py5.mouse_x, py5.mouse_y, py5.random(34, 68), py5.random(py5.TWO_PI)))
    if len(sources) > 5:
        sources.pop(0)


def key_pressed() -> None:
    global show_sources
    if py5.key == "v":
        show_sources = not show_sources
    elif py5.key == "r":
        reset_sources()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "wave_interference_field_####.png"))


py5.run_sketch()
