from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

mode = 0
phase = 0.0


def setup() -> None:
    py5.size(760, 460)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def signal(t: float) -> float:
    if mode == 0:
        return math.sin(t) * 0.72 + math.sin(t * 2.01 + 0.8) * 0.18
    if mode == 1:
        return math.sin(t) * 0.55 + math.sin(t * 3.0) * 0.25 + math.sin(t * 5.0) * 0.14
    return math.sin(t + math.sin(t * 0.25 + phase) * 2.2) * 0.75


def draw_waveform() -> None:
    py5.no_fill()
    py5.stroke(178, 76, 96)
    py5.stroke_weight(2.4)
    py5.begin_shape()
    for x in range(34, py5.width - 33):
        t = (x - 34) / 28 + phase
        y = py5.height * 0.34 - signal(t) * 92
        py5.vertex(x, y)
    py5.end_shape()


def draw_lissajous() -> None:
    py5.no_fill()
    py5.stroke(42, 78, 96, 80)
    py5.stroke_weight(1.8)
    py5.begin_shape()
    for i in range(620):
        t = i * 0.035 + phase
        x = py5.width * 0.28 + signal(t) * 120
        y = py5.height * 0.72 + signal(t * 1.51 + 0.7) * 82
        py5.vertex(x, y)
    py5.end_shape()


def draw_spectrum() -> None:
    base_x = py5.width * 0.55
    py5.no_stroke()
    for i in range(32):
        amount = abs(math.sin(phase * (0.2 + i * 0.015) + i * 0.72))
        harmonic = 1 / (1 + i * (0.16 + mode * 0.08))
        h = (amount * 0.45 + harmonic) * 118
        py5.fill(200 + i * 2.5, 68, 90, 78)
        py5.rect(base_x + i * 6, py5.height * 0.82 - h, 4, h)


def draw() -> None:
    global phase
    phase += 0.075
    py5.background(244, 18, 8)
    py5.stroke(210, 8, 72, 24)
    py5.line(0, py5.height * 0.34, py5.width, py5.height * 0.34)
    py5.line(0, py5.height * 0.72, py5.width, py5.height * 0.72)
    draw_waveform()
    draw_lissajous()
    draw_spectrum()
    py5.no_stroke()
    py5.fill(42, 80, 96)
    py5.text_size(15)
    py5.text(["dual sine", "odd harmonics", "phase modulation"][mode], 24, 28)


def key_pressed() -> None:
    global mode
    if py5.key == " ":
        mode = (mode + 1) % 3
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "audio_wave_scope_####.png"))


py5.run_sketch()
