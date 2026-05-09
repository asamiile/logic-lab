from __future__ import annotations

from pathlib import Path
from random import Random

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

GRID_STEP = 4
PALETTES = [
    np.array([[36, 34, 140], [48, 98, 164], [150, 93, 132]], dtype=np.float32),
    np.array([[32, 70, 118], [180, 66, 84], [220, 142, 68]], dtype=np.float32),
    np.array([[20, 96, 88], [64, 135, 114], [22, 48, 92]], dtype=np.float32),
]

rng = Random(120)
paper: np.ndarray
ink: np.ndarray
wetness: np.ndarray
palette_index = 0
show_paper = True
auto_drop = True
frame_count = 0


def setup() -> None:
    py5.size(880, 640)
    py5.color_mode(py5.RGB, 255, 255, 255, 255)
    py5.noise_seed(120)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_paper()


def reset_paper() -> None:
    global paper, ink, wetness, frame_count
    rows = py5.height // GRID_STEP
    cols = py5.width // GRID_STEP
    paper = build_paper(rows, cols)
    ink = np.zeros((rows, cols, 3), dtype=np.float32)
    wetness = np.zeros((rows, cols), dtype=np.float32)
    frame_count = 0
    for i in range(5):
        add_drop(
            int(cols * (0.22 + i * 0.13)),
            int(rows * (0.38 + rng.uniform(-0.09, 0.1))),
            rng.randrange(8, 15),
            i % 3,
        )


def build_paper(rows: int, cols: int) -> np.ndarray:
    texture = np.zeros((rows, cols), dtype=np.float32)
    for row in range(rows):
        for col in range(cols):
            fine = py5.noise(col * 0.11, row * 0.11)
            fiber = py5.noise(col * 0.025 + 40, row * 0.04)
            texture[row, col] = 0.78 + fine * 0.12 + fiber * 0.18
    return np.clip(texture, 0.72, 1.08)


def draw() -> None:
    global frame_count
    frame_count += 1
    if auto_drop and frame_count % 48 == 0:
        rows, cols = wetness.shape
        add_drop(
            rng.randrange(cols // 6, cols * 5 // 6),
            rng.randrange(rows // 5, rows * 4 // 5),
            rng.randrange(7, 13),
            rng.randrange(3),
        )
    if py5.is_mouse_pressed:
        add_drop(py5.mouse_x // GRID_STEP, py5.mouse_y // GRID_STEP, 9, frame_count % 3)
    for _ in range(3):
        step_diffusion()
    draw_field()


def add_drop(cx: int, cy: int, radius: int, color_index: int) -> None:
    rows, cols = wetness.shape
    color = PALETTES[palette_index][color_index]
    for row in range(max(0, cy - radius * 2), min(rows, cy + radius * 2 + 1)):
        for col in range(max(0, cx - radius * 2), min(cols, cx + radius * 2 + 1)):
            distance = ((col - cx) ** 2 + (row - cy) ** 2) ** 0.5
            if distance <= radius * 2:
                amount = max(0.0, 1.0 - distance / (radius * 2))
                grain = 0.65 + paper[row, col] * 0.45
                ink[row, col] += color * amount * grain * 0.022
                wetness[row, col] = min(1.0, wetness[row, col] + amount * 0.9)


def step_diffusion() -> None:
    global ink, wetness
    diffusion = 0.12 + (paper - 0.72) * 0.18
    neighbors = (
        np.roll(ink, 1, axis=0)
        + np.roll(ink, -1, axis=0)
        + np.roll(ink, 1, axis=1)
        + np.roll(ink, -1, axis=1)
    ) * 0.25
    delta = (neighbors - ink) * diffusion[:, :, None] * wetness[:, :, None]
    ink = np.clip(ink + delta, 0, 3.2)
    wetness = np.clip(
        wetness
        + (
            np.roll(wetness, 1, axis=0)
            + np.roll(wetness, -1, axis=0)
            + np.roll(wetness, 1, axis=1)
            + np.roll(wetness, -1, axis=1)
            - wetness * 4
        )
        * 0.035,
        0,
        1,
    )
    wetness *= 0.986


def draw_field() -> None:
    rows, cols = wetness.shape
    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            pigment = ink[row, col]
            density = min(1.0, float(pigment.sum()) * 0.09)
            base = 246 * paper[row, col] if show_paper else 248
            edge = wet_edge(row, col)
            rgb = np.array([base, base * 0.985, base * 0.94], dtype=np.float32)
            rgb = rgb * (1 - density * 0.72) + pigment * 255 * density * 0.42
            rgb *= 1 - edge * 0.28
            py5.fill(
                float(np.clip(rgb[0], 0, 255)),
                float(np.clip(rgb[1], 0, 255)),
                float(np.clip(rgb[2], 0, 255)),
            )
            py5.rect(col * GRID_STEP, row * GRID_STEP, GRID_STEP + 1, GRID_STEP + 1)


def wet_edge(row: int, col: int) -> float:
    center = wetness[row, col]
    up = wetness[(row - 1) % wetness.shape[0], col]
    down = wetness[(row + 1) % wetness.shape[0], col]
    left = wetness[row, (col - 1) % wetness.shape[1]]
    right = wetness[row, (col + 1) % wetness.shape[1]]
    return min(1.0, abs(center * 4 - up - down - left - right) * 2.4)


def key_pressed() -> None:
    global palette_index, show_paper, auto_drop
    if py5.key == "r":
        reset_paper()
    elif py5.key == "p":
        palette_index = (palette_index + 1) % len(PALETTES)
        reset_paper()
    elif py5.key == "t":
        show_paper = not show_paper
    elif py5.key == " ":
        auto_drop = not auto_drop
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "watercolor_ink_diffusion_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
