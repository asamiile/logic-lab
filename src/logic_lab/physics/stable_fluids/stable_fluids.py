"""
Stable Fluids (Jos Stam, 1999).

Real-time incompressible fluid simulation using the unconditionally
stable semi-Lagrangian advection scheme. The algorithm:

    1. Add external forces (mouse drag, gravity, random impulses).
    2. Diffuse velocity field (viscosity).
    3. Project velocity to be divergence-free (incompressibility).
    4. Advect velocity and density fields along the flow.

Grid cells store velocity (vx, vy) and an ink/dye density.
Mouse dragging injects both velocity and colored dye.
"""

import math
import random
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

N = 128  # Grid resolution
SCALE = 5  # Display pixels per grid cell
WIDTH = N * SCALE
HEIGHT = N * SCALE
VISCOSITY = 0.00001
DIFFUSION = 0.00005
DT = 0.15
ITER = 8  # Gauss-Seidel iterations for projection

vx: np.ndarray
vy: np.ndarray
vx0: np.ndarray
vy0: np.ndarray
density: np.ndarray  # (N, N, 3) — RGB dye
density0: np.ndarray

prev_mx: float = 0.0
prev_my: float = 0.0
paused = False
hue_offset = 0.0


def _idx(x: int, y: int) -> tuple[int, int]:
    return max(0, min(N - 1, x)), max(0, min(N - 1, y))


def _set_bnd(b: int, x: np.ndarray) -> None:
    """Boundary conditions."""
    x[0, :] = -x[1, :] if b == 1 else x[1, :]
    x[-1, :] = -x[-2, :] if b == 1 else x[-2, :]
    x[:, 0] = -x[:, 1] if b == 2 else x[:, 1]
    x[:, -1] = -x[:, -2] if b == 2 else x[:, -2]
    x[0, 0] = 0.5 * (x[1, 0] + x[0, 1])
    x[-1, 0] = 0.5 * (x[-2, 0] + x[-1, 1])
    x[0, -1] = 0.5 * (x[1, -1] + x[0, -2])
    x[-1, -1] = 0.5 * (x[-2, -1] + x[-1, -2])


def _lin_solve(b: int, x: np.ndarray, x0: np.ndarray, a: float, c: float) -> None:
    c_inv = 1.0 / c
    for _ in range(ITER):
        x[1:-1, 1:-1] = (
            x0[1:-1, 1:-1] + a * (x[:-2, 1:-1] + x[2:, 1:-1] + x[1:-1, :-2] + x[1:-1, 2:])
        ) * c_inv
        _set_bnd(b, x)


def _diffuse(b: int, x: np.ndarray, x0: np.ndarray, diff: float) -> None:
    a = DT * diff * (N - 2) ** 2
    _lin_solve(b, x, x0, a, 1 + 4 * a)


def _project(vx_: np.ndarray, vy_: np.ndarray, p: np.ndarray, div: np.ndarray) -> None:
    h = 1.0 / N
    div[1:-1, 1:-1] = -0.5 * h * (vx_[2:, 1:-1] - vx_[:-2, 1:-1] + vy_[1:-1, 2:] - vy_[1:-1, :-2])
    p[:] = 0
    _set_bnd(0, div)
    _set_bnd(0, p)
    _lin_solve(0, p, div, 1, 4)
    vx_[1:-1, 1:-1] -= 0.5 * (p[2:, 1:-1] - p[:-2, 1:-1]) / h
    vy_[1:-1, 1:-1] -= 0.5 * (p[1:-1, 2:] - p[1:-1, :-2]) / h
    _set_bnd(1, vx_)
    _set_bnd(2, vy_)


def _advect(b: int, d: np.ndarray, d0: np.ndarray, vx_: np.ndarray, vy_: np.ndarray) -> None:
    dt0 = DT * (N - 2)
    i = np.arange(1, N - 1)
    j = np.arange(1, N - 1)
    ii, jj = np.meshgrid(i, j, indexing="ij")

    x = ii - dt0 * vx_[1:-1, 1:-1]
    y = jj - dt0 * vy_[1:-1, 1:-1]

    x = np.clip(x, 0.5, N - 1.5)
    y = np.clip(y, 0.5, N - 1.5)

    i0 = x.astype(int)
    j0 = y.astype(int)
    i1 = i0 + 1
    j1 = j0 + 1

    s1 = x - i0
    s0 = 1 - s1
    t1 = y - j0
    t0 = 1 - t1

    i0 = np.clip(i0, 0, N - 1)
    i1 = np.clip(i1, 0, N - 1)
    j0 = np.clip(j0, 0, N - 1)
    j1 = np.clip(j1, 0, N - 1)

    d[1:-1, 1:-1] = s0 * (t0 * d0[i0, j0] + t1 * d0[i0, j1]) + s1 * (
        t0 * d0[i1, j0] + t1 * d0[i1, j1]
    )
    _set_bnd(b, d)


def _step_fluid() -> None:
    global vx, vy, vx0, vy0, density, density0

    # Velocity step
    _diffuse(1, vx0, vx, VISCOSITY)
    _diffuse(2, vy0, vy, VISCOSITY)

    p = np.zeros((N, N), dtype=np.float32)
    div = np.zeros((N, N), dtype=np.float32)
    _project(vx0, vy0, p, div)

    _advect(1, vx, vx0, vx0, vy0)
    _advect(2, vy, vy0, vx0, vy0)
    _project(vx, vy, p, div)

    # Density step
    for c in range(3):
        _diffuse(0, density0[:, :, c], density[:, :, c], DIFFUSION)
        _advect(0, density[:, :, c], density0[:, :, c], vx, vy)

    # Slow decay
    density *= 0.995


def _add_force(gx: int, gy: int, fx: float, fy: float, r: int, g: float, b: float) -> None:
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            nx, ny = _idx(gx + dx, gy + dy)
            w = math.exp(-(dx * dx + dy * dy) / 4.0)
            vx[nx, ny] += fx * w * DT * 500
            vy[nx, ny] += fy * w * DT * 500
            density[nx, ny, 0] += r * w * 0.3
            density[nx, ny, 1] += g * w * 0.3
            density[nx, ny, 2] += b * w * 0.3


def _hue_to_rgb(h: float) -> tuple[float, float, float]:
    h = h % 360
    c = 1.0
    x = c * (1 - abs((h / 60) % 2 - 1))
    if h < 60:
        return c, x, 0.0
    elif h < 120:
        return x, c, 0.0
    elif h < 180:
        return 0.0, c, x
    elif h < 240:
        return 0.0, x, c
    elif h < 300:
        return x, 0.0, c
    else:
        return c, 0.0, x


def setup() -> None:
    global vx, vy, vx0, vy0, density, density0, prev_mx, prev_my
    py5.size(WIDTH, HEIGHT)
    py5.background(0)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    vx = np.zeros((N, N), dtype=np.float32)
    vy = np.zeros((N, N), dtype=np.float32)
    vx0 = np.zeros((N, N), dtype=np.float32)
    vy0 = np.zeros((N, N), dtype=np.float32)
    density = np.zeros((N, N, 3), dtype=np.float32)
    density0 = np.zeros((N, N, 3), dtype=np.float32)
    prev_mx = py5.mouse_x
    prev_my = py5.mouse_y


def draw() -> None:
    global prev_mx, prev_my, hue_offset

    hue_offset = (hue_offset + 0.4) % 360
    r, g, b = _hue_to_rgb(hue_offset)

    if py5.is_mouse_pressed:
        gx = int(py5.mouse_x / SCALE)
        gy = int(py5.mouse_y / SCALE)
        fx = (py5.mouse_x - prev_mx) * 0.3
        fy = (py5.mouse_y - prev_my) * 0.3
        _add_force(gx, gy, fx, fy, r, g, b)

    prev_mx = float(py5.mouse_x)
    prev_my = float(py5.mouse_y)

    # Random impulse
    if py5.frame_count % 90 == 0:
        rng = random.Random()
        gx = rng.randint(N // 4, 3 * N // 4)
        gy = rng.randint(N // 4, 3 * N // 4)
        angle = rng.uniform(0, math.tau)
        _add_force(gx, gy, math.cos(angle) * 2, math.sin(angle) * 2, r, g, b)

    if not paused:
        _step_fluid()

    # Render
    py5.load_pixels()
    pixels = py5.pixels
    w = py5.width

    d_clamped = np.clip(density, 0.0, 1.0)
    for gy_ in range(N):
        for gx_ in range(N):
            rc = int(d_clamped[gx_, gy_, 0] * 255)
            gc = int(d_clamped[gx_, gy_, 1] * 255)
            bc = int(d_clamped[gx_, gy_, 2] * 255)
            c = py5.color(rc, gc, bc)
            for dy in range(SCALE):
                for dx in range(SCALE):
                    px = gx_ * SCALE + dx
                    py_ = gy_ * SCALE + dy
                    pixels[py_ * w + px] = c

    py5.update_pixels()

    py5.fill(220)
    py5.no_stroke()
    py5.text_size(12)
    py5.text("Stable Fluids | drag mouse to paint | SPACE=pause S=save", 10, 20)


def key_pressed() -> None:
    global paused, vx, vy, density
    if py5.key == " ":
        paused = not paused
    elif py5.key == "r":
        vx[:] = 0
        vy[:] = 0
        density[:] = 0
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "stable_fluids_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
