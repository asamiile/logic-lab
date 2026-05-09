from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

N = 72
DT = 0.16
DIFFUSION = 0.0002
DISSIPATION = 0.992
density = np.zeros((N, N), dtype=float)
vx = np.zeros((N, N), dtype=float)
vy = np.zeros((N, N), dtype=float)


def setup() -> None:
    py5.size(640, 360)
    py5.no_stroke()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def diffuse(field: np.ndarray) -> np.ndarray:
    return field + DIFFUSION * (
        np.roll(field, 1, 0)
        + np.roll(field, -1, 0)
        + np.roll(field, 1, 1)
        + np.roll(field, -1, 1)
        - 4 * field
    )


def advect(field: np.ndarray) -> np.ndarray:
    yy, xx = np.mgrid[0:N, 0:N]
    src_x = np.clip((xx - vx * DT).round().astype(int), 0, N - 1)
    src_y = np.clip((yy - vy * DT).round().astype(int), 0, N - 1)
    return field[src_y, src_x] * DISSIPATION


def inject(x: float, y: float, amount: float = 7.0) -> None:
    gx = int(np.clip(x / py5.width * N, 2, N - 3))
    gy = int(np.clip(y / py5.height * N, 2, N - 3))
    density[gy - 2 : gy + 3, gx - 2 : gx + 3] += amount
    vx[gy - 2 : gy + 3, gx - 2 : gx + 3] += (py5.mouse_x - py5.pmouse_x) * 0.8
    vy[gy - 2 : gy + 3, gx - 2 : gx + 3] += (py5.mouse_y - py5.pmouse_y) * 0.8


def draw() -> None:
    global density, vx, vy
    py5.background(12, 14, 18)
    inject(
        py5.mouse_x if py5.is_mouse_pressed else py5.width * 0.5,
        py5.mouse_y if py5.is_mouse_pressed else py5.height * 0.48,
        5.2 if py5.is_mouse_pressed else 1.2,
    )
    density = diffuse(advect(density))
    vx = diffuse(advect(vx)) * 0.985
    vy = diffuse(advect(vy)) * 0.985
    cw = py5.width / N
    ch = py5.height / N
    for y in range(N):
        for x in range(N):
            value = min(255, density[y, x] * 28)
            if value > 2:
                py5.fill(60 + value * 0.4, 145, 210, value)
                py5.rect(x * cw, y * ch, cw + 1, ch + 1)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "stable_fluids_2d_####.png"))


py5.run_sketch()
