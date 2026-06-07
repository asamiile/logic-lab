"""
Belousov-Zhabotinsky (BZ) Reaction Simulation.

The BZ reaction is a chemical oscillator that produces self-organizing
spiral waves and target patterns. Modeled here using the Oregonator
approximation on a 2D grid.

Discretized Oregonator equations (Winfree/Barkley variant):
    u_next = u + dt * (1/eps * (u*(1-u) - f*v*(u-q)/(u+q)) + Du*laplacian(u))
    v_next = v + dt * (u - v)

Where:
    - u: activator concentration (autocatalytic species)
    - v: inhibitor concentration
    - eps: time scale separation (0.05-0.3)
    - f: stoichiometric coefficient (1.0-3.0)
    - q: dimensionless parameter (0.002-0.01)
    - Du: diffusion coefficient for u
"""

from pathlib import Path

import numpy as np
import py5
import scipy.ndimage

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

GRID_SIZE = 256
PIXEL_SCALE = 2

# Oregonator parameters
eps = 0.1
f = 1.4
q = 0.002
Du = 1.0
dt = 0.05

LAPLACIAN_KERNEL = np.array([[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]])

PRESETS = {
    "spiral": {"eps": 0.1, "f": 1.4, "q": 0.002},
    "target": {"eps": 0.2, "f": 2.0, "q": 0.005},
    "turbulent": {"eps": 0.05, "f": 1.0, "q": 0.002},
}

preset_name = "spiral"

u: np.ndarray
v: np.ndarray
paused = False


def _initialize_grids() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(42)
    u_init = rng.uniform(0.0, 1.0, (GRID_SIZE, GRID_SIZE)).astype(np.float32)
    v_init = rng.uniform(0.0, 1.0, (GRID_SIZE, GRID_SIZE)).astype(np.float32)
    return u_init, v_init


def _update_step() -> None:
    global u, v

    laplacian_u = scipy.ndimage.convolve(u, LAPLACIAN_KERNEL, mode="wrap")

    u_v = u * v
    denom = np.maximum(u + q, 1e-10)

    du = (1.0 / eps) * (u * (1.0 - u) - f * v * (u - q) / denom) + Du * laplacian_u
    dv = u - v

    u = np.clip(u + dt * du, 0.0, 1.0)
    v = np.clip(v + dt * dv, 0.0, 1.0)


def _render_frame() -> None:
    py5.load_pixels()
    pixels = py5.pixels
    w = py5.width

    # Map u to a cyan-orange colormap
    u_scaled = (u * 255).astype(np.uint8)
    r = u_scaled
    g = (u * 180).astype(np.uint8)
    b = 255 - u_scaled

    for gy in range(GRID_SIZE):
        for gx in range(GRID_SIZE):
            c = py5.color(int(r[gy, gx]), int(g[gy, gx]), int(b[gy, gx]))
            for dy in range(PIXEL_SCALE):
                for dx in range(PIXEL_SCALE):
                    px = gx * PIXEL_SCALE + dx
                    py_ = gy * PIXEL_SCALE + dy
                    if px < py5.width and py_ < py5.height:
                        pixels[py_ * w + px] = c

    py5.update_pixels()


def setup() -> None:
    global u, v
    py5.size(GRID_SIZE * PIXEL_SCALE, GRID_SIZE * PIXEL_SCALE)
    py5.background(0)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    u, v = _initialize_grids()


def draw() -> None:
    if not paused:
        _update_step()
    _render_frame()

    py5.fill(220)
    py5.text_size(12)
    py5.text(f"BZ | Preset: {preset_name} | eps:{eps:.2f} f:{f:.1f} q:{q:.3f}", 10, 20)
    if paused:
        py5.text("PAUSED", 10, 35)


def key_pressed() -> None:
    global eps, f, q, u, v, paused, preset_name

    if py5.key == "1":
        preset_name = "spiral"
    elif py5.key == "2":
        preset_name = "target"
    elif py5.key == "3":
        preset_name = "turbulent"

    if py5.key in ("1", "2", "3"):
        eps = PRESETS[preset_name]["eps"]
        f = PRESETS[preset_name]["f"]
        q = PRESETS[preset_name]["q"]
        u, v = _initialize_grids()
    elif py5.key == "r":
        u, v = _initialize_grids()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"bz_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
