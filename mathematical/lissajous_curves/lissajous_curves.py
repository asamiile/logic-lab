from __future__ import annotations

from pathlib import Path
import math

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PRESETS = [
    ("classic", 3, 2, math.pi / 2),
    ("bow", 5, 4, math.pi / 3),
    ("orbit", 7, 3, math.pi / 5),
    ("weave", 9, 8, math.pi / 4),
    ("flower", 6, 5, math.pi / 2),
]

preset_index = 0
phase_offset = 0.0
animate_phase = True
show_trail = True
show_drivers = True
sample_count = 720


def setup() -> None:
    py5.size(760, 640)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global phase_offset

    py5.background(218, 14, 96)
    if animate_phase:
        phase_offset += 0.012

    name, freq_x, freq_y, base_phase = PRESETS[preset_index]
    phase = base_phase + phase_offset
    points = lissajous_points(freq_x, freq_y, phase)

    if show_drivers:
        draw_driver_waves(freq_x, freq_y, phase)
    draw_curve(points)
    if show_trail:
        draw_moving_point(freq_x, freq_y, phase)
    draw_info(name, freq_x, freq_y, phase)


def lissajous_points(freq_x: int, freq_y: int, phase: float) -> list[tuple[float, float]]:
    center_x = py5.width * 0.5
    center_y = py5.height * 0.55
    amp_x = py5.width * 0.32
    amp_y = py5.height * 0.34
    points = []
    for i in range(sample_count + 1):
        t = py5.TWO_PI * i / sample_count
        x = center_x + math.sin(freq_x * t + phase) * amp_x
        y = center_y + math.sin(freq_y * t) * amp_y
        points.append((x, y))
    return points


def draw_curve(points: list[tuple[float, float]]) -> None:
    py5.no_fill()
    py5.stroke_weight(2.4)
    py5.begin_shape()
    for i, (x, y) in enumerate(points):
        hue = (196 + i * 140 / max(1, len(points))) % 360
        py5.stroke(hue, 72, 48 + 42 * i / max(1, len(points)), 92)
        py5.vertex(x, y)
    py5.end_shape()


def draw_moving_point(freq_x: int, freq_y: int, phase: float) -> None:
    center_x = py5.width * 0.5
    center_y = py5.height * 0.55
    amp_x = py5.width * 0.32
    amp_y = py5.height * 0.34
    t = py5.frame_count * 0.025
    x = center_x + math.sin(freq_x * t + phase) * amp_x
    y = center_y + math.sin(freq_y * t) * amp_y

    py5.no_stroke()
    py5.fill(34, 94, 98, 100)
    py5.circle(x, y, 12)
    py5.fill(0, 0, 100, 100)
    py5.circle(x, y, 4)


def draw_driver_waves(freq_x: int, freq_y: int, phase: float) -> None:
    top = 74
    left = 74
    width = py5.width - 148
    wave_height = 34

    draw_wave(left, top, width, wave_height, freq_x, phase, 198, "x")
    draw_wave(left, top + 58, width, wave_height, freq_y, 0.0, 34, "y")


def draw_wave(
    left: float,
    baseline: float,
    width: float,
    amplitude: float,
    frequency: int,
    phase: float,
    hue: float,
    label: str,
) -> None:
    py5.no_fill()
    py5.stroke(hue, 58, 42, 30)
    py5.stroke_weight(1)
    py5.line(left, baseline, left + width, baseline)

    py5.stroke(hue, 74, 72, 86)
    py5.stroke_weight(1.6)
    py5.begin_shape()
    for i in range(220):
        amount = i / 219
        x = left + amount * width
        y = baseline + math.sin(py5.TWO_PI * frequency * amount + phase) * amplitude
        py5.vertex(x, y)
    py5.end_shape()

    py5.no_stroke()
    py5.fill(hue, 78, 36, 90)
    py5.text(f"{label}: {frequency}", left - 44, baseline + 5)


def draw_info(name: str, freq_x: int, freq_y: int, phase: float) -> None:
    py5.no_stroke()
    py5.fill(218, 24, 12, 90)
    py5.rect(14, 14, 610, 44, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Lissajous curves | {name} {freq_x}:{freq_y} phase {phase % py5.TWO_PI:.2f} | n: preset | space: animate | d: drivers | p: point | s: save",
        24,
        42,
    )


def key_pressed() -> None:
    global preset_index, phase_offset, animate_phase, show_trail, show_drivers

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "lissajous_curves_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
        phase_offset = 0.0
    elif py5.key == " ":
        animate_phase = not animate_phase
    elif py5.key == "p":
        show_trail = not show_trail
    elif py5.key == "d":
        show_drivers = not show_drivers


py5.run_sketch()
