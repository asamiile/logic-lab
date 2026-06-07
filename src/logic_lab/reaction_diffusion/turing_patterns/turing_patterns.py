"""
Turing Patterns: Gierer-Meinhardt Activator-Inhibitor Model.

Alan Turing's 1952 "The Chemical Basis of Morphogenesis" proposed that
reaction-diffusion systems can spontaneously generate spatial patterns.
The Gierer-Meinhardt model captures this with a short-range activator
and a long-range inhibitor.

Equations:
    da/dt = rho_a * (a^2 / h - mu_a * a) + Da * laplacian(a) + rho
    dh/dt = rho_h * a^2 - mu_h * h + Dh * laplacian(h)

Where:
    - a: activator concentration
    - h: inhibitor concentration
    - Da, Dh: diffusion coefficients (Dh >> Da for pattern formation)
    - rho_a, rho_h: production rates
    - mu_a, mu_h: decay rates
    - rho: basal activator production (prevents zero-state)
"""

from pathlib import Path

import numpy as np
import py5
import scipy.ndimage

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

GRID_SIZE = 256
PIXEL_SCALE = 2

# Gierer-Meinhardt parameters
Da = 0.005
Dh = 0.2
rho_a = 0.01
rho_h = 0.02
mu_a = 0.003
mu_h = 0.004
rho = 0.001
dt = 1.0

PRESETS = {
    "spots": {"Da": 0.005, "Dh": 0.2, "rho_a": 0.01, "rho_h": 0.02, "mu_a": 0.003, "mu_h": 0.004},
    "stripes": {"Da": 0.008, "Dh": 0.4, "rho_a": 0.01, "rho_h": 0.02, "mu_a": 0.005, "mu_h": 0.006},
    "labyrinth": {
        "Da": 0.003,
        "Dh": 0.15,
        "rho_a": 0.008,
        "rho_h": 0.016,
        "mu_a": 0.002,
        "mu_h": 0.003,
    },
}

preset_name = "spots"

a: np.ndarray
h: np.ndarray
paused = False

LAPLACIAN_KERNEL = np.array([[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]])


def _initialize_grids() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(0)
    a_init = rng.uniform(0.5, 1.5, (GRID_SIZE, GRID_SIZE)).astype(np.float32)
    h_init = rng.uniform(0.5, 1.5, (GRID_SIZE, GRID_SIZE)).astype(np.float32)
    return a_init, h_init


def _update_step() -> None:
    global a, h

    lap_a = scipy.ndimage.convolve(a, LAPLACIAN_KERNEL, mode="wrap")
    lap_h = scipy.ndimage.convolve(h, LAPLACIAN_KERNEL, mode="wrap")

    h_safe = np.maximum(h, 1e-6)
    a2 = a * a

    da = rho_a * (a2 / h_safe - mu_a * a) + Da * lap_a + rho
    dh = rho_h * a2 - mu_h * h + Dh * lap_h

    a[:] = np.maximum(a + dt * da, 0.0)
    h[:] = np.maximum(h + dt * dh, 0.0)


def _render_frame() -> None:
    py5.load_pixels()
    pixels = py5.pixels
    w = py5.width

    # Normalize a for display
    a_min, a_max = a.min(), a.max()
    if a_max > a_min:
        a_norm = (a - a_min) / (a_max - a_min)
    else:
        a_norm = np.zeros_like(a)

    # Warm colormap: black → deep red → orange → yellow
    r_ch = np.clip(a_norm * 255, 0, 255).astype(np.uint8)
    g_ch = np.clip((a_norm - 0.3) * 255 / 0.7, 0, 255).astype(np.uint8)
    b_ch = np.clip((a_norm - 0.7) * 255 / 0.3, 0, 255).astype(np.uint8)

    for gy in range(GRID_SIZE):
        for gx in range(GRID_SIZE):
            c = py5.color(int(r_ch[gy, gx]), int(g_ch[gy, gx]), int(b_ch[gy, gx]))
            for dy in range(PIXEL_SCALE):
                for dx in range(PIXEL_SCALE):
                    px = gx * PIXEL_SCALE + dx
                    py_ = gy * PIXEL_SCALE + dy
                    if px < py5.width and py_ < py5.height:
                        pixels[py_ * w + px] = c

    py5.update_pixels()


def setup() -> None:
    global a, h
    py5.size(GRID_SIZE * PIXEL_SCALE, GRID_SIZE * PIXEL_SCALE)
    py5.background(0)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    a, h = _initialize_grids()


def draw() -> None:
    if not paused:
        _update_step()
    _render_frame()

    py5.fill(220)
    py5.text_size(12)
    py5.text(f"Turing | {preset_name} | Da:{Da:.3f} Dh:{Dh:.2f}", 10, 20)
    if paused:
        py5.text("PAUSED", 10, 35)


def key_pressed() -> None:
    global Da, Dh, rho_a, rho_h, mu_a, mu_h, a, h, paused, preset_name

    if py5.key == "1":
        preset_name = "spots"
    elif py5.key == "2":
        preset_name = "stripes"
    elif py5.key == "3":
        preset_name = "labyrinth"

    if py5.key in ("1", "2", "3"):
        p = PRESETS[preset_name]
        Da, Dh = p["Da"], p["Dh"]
        rho_a, rho_h = p["rho_a"], p["rho_h"]
        mu_a, mu_h = p["mu_a"], p["mu_h"]
        a, h = _initialize_grids()
    elif py5.key == "r":
        a, h = _initialize_grids()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"turing_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
