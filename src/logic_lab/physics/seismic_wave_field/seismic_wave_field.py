from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

events: list[Event] = []


@dataclass
class Event:
    x: float
    y: float
    age: float

    def update(self) -> None:
        self.age += 1.0


def setup() -> None:
    py5.size(720, 480)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    events.append(Event(py5.width * 0.34, py5.height * 0.58, 0))


def terrain_y(x: float, layer: int) -> float:
    return (
        py5.height * (0.32 + layer * 0.13)
        + math.sin(x * 0.012 + layer * 1.8) * 22
        + math.sin(x * 0.034 - layer) * 8
    )


def draw_terrain() -> None:
    for layer in range(4):
        py5.no_fill()
        py5.stroke(38 + layer * 24, 35, 44 + layer * 9, 62)
        py5.stroke_weight(2)
        py5.begin_shape()
        for x in range(-20, py5.width + 21, 10):
            py5.vertex(x, terrain_y(x, layer))
        py5.end_shape()


def draw_event(event: Event) -> None:
    for speed, hue, label_alpha in ((3.9, 28, 76), (2.35, 194, 58)):
        radius = event.age * speed
        alpha = max(0, label_alpha - event.age * 0.34)
        py5.no_fill()
        py5.stroke(hue, 78, 96, alpha)
        py5.stroke_weight(2.1)
        py5.circle(event.x, event.y, radius * 2)
        py5.stroke_weight(0.9)
        py5.circle(event.x, event.y, max(0, radius * 2 - 22))

    py5.no_stroke()
    py5.fill(4, 80, 100, max(0, 80 - event.age * 0.45))
    py5.circle(event.x, event.y, 9)


def draw() -> None:
    py5.background(226, 24, 10)
    draw_terrain()
    for event in list(events):
        draw_event(event)
        event.update()
        if event.age > 210:
            events.remove(event)

    if py5.frame_count % 150 == 0:
        events.append(Event(py5.random(80, py5.width - 80), py5.random(100, py5.height - 90), 0))
        if len(events) > 4:
            events.pop(0)


def mouse_pressed() -> None:
    events.append(Event(py5.mouse_x, py5.mouse_y, 0))


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "seismic_wave_field_####.png"))


py5.run_sketch()
