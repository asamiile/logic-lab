from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

time_value = 0.0
blobs: list[dict] = []


class Blob:
    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = py5.random(-1, 1)
        self.vy = py5.random(-1, 1)

    def update(self, w: float, h: float) -> None:
        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius < -w or self.x + self.radius > w:
            self.vx *= -1
        if self.y - self.radius < -h or self.y + self.radius > h:
            self.vy *= -1

        self.x = max(-w, min(w, self.x))
        self.y = max(-h, min(h, self.y))

    def field_strength(self, px: float, py: float) -> float:
        dist = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2) + 0.1
        return self.radius / dist


def setup() -> None:
    py5.size(1000, 800)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    global blobs
    blobs = [
        Blob(py5.random(-200, 200), py5.random(-150, 150), py5.random(30, 60)) for _ in range(5)
    ]


def draw() -> None:
    global time_value

    py5.background(20)
    py5.translate(py5.width / 2, py5.height / 2)

    time_value += 0.02

    w, h = 400, 300

    for blob in blobs:
        blob.update(w, h)

    threshold = 2.0 + 0.5 * math.sin(time_value)

    py5.no_fill()
    py5.stroke_weight(2)

    hue_base = (time_value * 100) % 360
    py5.stroke(hue_base, 70, 100)

    step = 5
    py5.begin_shape()
    for x in range(-w, w + 1, step):
        total_field = sum(blob.field_strength(x, -h) for blob in blobs)
        if total_field > threshold:
            py5.vertex(x, -h - 5)
        else:
            py5.vertex(x, -h + 10)

    for y in range(-h, h + 1, step):
        total_field = sum(blob.field_strength(w, y) for blob in blobs)
        if total_field > threshold:
            py5.vertex(w + 5, y)
        else:
            py5.vertex(w - 10, y)

    for x in range(w, -w - 1, -step):
        total_field = sum(blob.field_strength(x, h) for blob in blobs)
        if total_field > threshold:
            py5.vertex(x, h + 5)
        else:
            py5.vertex(x, h - 10)

    for y in range(h, -h - 1, -step):
        total_field = sum(blob.field_strength(-w, y) for blob in blobs)
        if total_field > threshold:
            py5.vertex(-w - 5, y)
        else:
            py5.vertex(-w + 10, y)

    py5.end_shape()

    py5.fill(hue_base, 60, 80, 100)
    py5.no_stroke()
    for blob in blobs:
        py5.circle(blob.x, blob.y, blob.radius * 0.5)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "blob_generator_####.png"))


py5.run_sketch()
