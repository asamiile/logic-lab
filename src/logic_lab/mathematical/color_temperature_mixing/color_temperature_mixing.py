from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PIXEL_STEP = 5
phase = 0.0


def setup() -> None:
    py5.size(860, 620)
    py5.color_mode(py5.RGB, 255, 255, 255, 255)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global phase
    phase += 0.018
    lights = moving_lights()
    draw_mixed_field(lights)
    draw_lights(lights)


def moving_lights() -> list[tuple[float, float, int, float]]:
    return [
        (py5.width * 0.24 + math.sin(phase) * 28, py5.height * 0.34, 2200, 1.05),
        (py5.width * 0.68, py5.height * 0.32 + math.cos(phase * 0.9) * 34, 6500, 0.92),
        (py5.width * 0.48 + math.sin(phase * 0.7) * 46, py5.height * 0.76, 10000, 0.82),
    ]


def draw_mixed_field(lights: list[tuple[float, float, int, float]]) -> None:
    py5.no_stroke()
    for y in range(0, py5.height, PIXEL_STEP):
        for x in range(0, py5.width, PIXEL_STEP):
            color = np.zeros(3, dtype=np.float32)
            exposure = 0.0
            for sx, sy, kelvin, power in lights:
                distance_sq = max(2400.0, (x - sx) ** 2 + (y - sy) ** 2)
                weight = power * 90000.0 / distance_sq
                color += np.array(kelvin_to_rgb(kelvin), dtype=np.float32) * weight
                exposure += weight
            color = color / max(1.0, exposure)
            brightness = min(1.0, exposure * 0.55)
            rgb = np.clip(color * (0.18 + brightness * 0.92), 0, 255)
            py5.fill(float(rgb[0]), float(rgb[1]), float(rgb[2]), 255)
            py5.rect(x, y, PIXEL_STEP + 1, PIXEL_STEP + 1)


def kelvin_to_rgb(kelvin: int) -> tuple[float, float, float]:
    temp = kelvin / 100.0
    if temp <= 66:
        red = 255
        green = 99.4708025861 * math.log(temp) - 161.1195681661
        blue = 0 if temp <= 19 else 138.5177312231 * math.log(temp - 10) - 305.0447927307
    else:
        red = 329.698727446 * ((temp - 60) ** -0.1332047592)
        green = 288.1221695283 * ((temp - 60) ** -0.0755148492)
        blue = 255
    return clamp(red), clamp(green), clamp(blue)


def clamp(value: float) -> float:
    return max(0.0, min(255.0, value))


def draw_lights(lights: list[tuple[float, float, int, float]]) -> None:
    for sx, sy, kelvin, _ in lights:
        r, g, b = kelvin_to_rgb(kelvin)
        py5.no_stroke()
        py5.fill(r, g, b, 230)
        py5.circle(sx, sy, 16)
        py5.fill(255, 255, 255, 120)
        py5.text(f"{kelvin}K", sx + 14, sy - 12)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "color_temperature_mixing_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
