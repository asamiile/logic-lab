"""
Lenia: Continuous Cellular Automaton.

Lenia is a continuous generalization of Conway's Game of Life that produces
life-like creatures and complex emergent patterns. Introduced by Bert Wang-Chak Chan.

Update rule:
    A_next = clip(A + dt * (2*G(K*A) - 1), 0, 1)

Where:
    - A: activity grid (continuous 0.0-1.0)
    - K: kernel (annular bell-shaped in 2D)
    - G: growth mapping function (bell curve centered at mu with width sigma)
    - dt: time step (controls speed of evolution)

The kernel K is a normalized annular function (ring shape) in the frequency domain.
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

GRID_SIZE = 256
PIXEL_SCALE = 2

# Lenia parameters
R = 13  # Kernel radius
dt = 0.1  # Time step
mu = 0.15  # Growth center
sigma = 0.015  # Growth width

PRESETS = {
    "orbium": {"R": 13, "dt": 0.1, "mu": 0.15, "sigma": 0.015},
    "geminium": {"R": 13, "dt": 0.1, "mu": 0.26, "sigma": 0.036},
    "scutium": {"R": 13, "dt": 0.1, "mu": 0.17, "sigma": 0.015},
}

preset_name = "orbium"

A: np.ndarray
K_fft: np.ndarray
paused = False


def _build_kernel(r: int, size: int) -> np.ndarray:
    """Build normalized annular kernel in the frequency domain."""
    y, x = np.ogrid[-size // 2 : size // 2, -size // 2 : size // 2]
    dist = np.sqrt(x * x + y * y) / r
    # Bell-shaped kernel: peaks at dist=0.5 (mid-ring)
    kernel = np.exp(-((dist - 0.5) ** 2) / (2 * 0.15**2)) * (dist < 1.0)
    kernel = kernel / (kernel.sum() + 1e-10)
    return np.fft.fft2(np.fft.fftshift(kernel)).astype(np.complex64)


def _growth(u: np.ndarray, mu_: float, sigma_: float) -> np.ndarray:
    """Bell-shaped growth function."""
    return 2.0 * np.exp(-((u - mu_) ** 2) / (2 * sigma_**2)) - 1.0


def _initialize_grid() -> np.ndarray:
    """Seed a small random patch in the center."""
    a = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)
    rng = np.random.RandomState(42)
    c = GRID_SIZE // 2
    r = 20
    patch = rng.uniform(0, 1, (r * 2, r * 2)).astype(np.float32)
    a[c - r : c + r, c - r : c + r] = patch
    return a


def _update_step() -> None:
    global A

    A_fft = np.fft.fft2(A)
    potential = np.real(np.fft.ifft2(K_fft * A_fft)).astype(np.float32)
    growth = _growth(potential, mu, sigma)
    A = np.clip(A + dt * growth, 0.0, 1.0)


def _render_frame() -> None:
    py5.load_pixels()
    pixels = py5.pixels
    w = py5.width

    # Colormap: dark background → cyan/green life
    r_ch = (A * 50).astype(np.uint8)
    g_ch = (A * 220).astype(np.uint8)
    b_ch = (A * 180).astype(np.uint8)

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
    global A, K_fft
    py5.size(GRID_SIZE * PIXEL_SCALE, GRID_SIZE * PIXEL_SCALE)
    py5.background(0)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    K_fft = _build_kernel(R, GRID_SIZE)
    A = _initialize_grid()


def draw() -> None:
    if not paused:
        _update_step()
    _render_frame()

    py5.fill(220)
    py5.text_size(12)
    py5.text(f"Lenia | {preset_name} | R:{R} mu:{mu:.3f} sigma:{sigma:.3f}", 10, 20)
    if paused:
        py5.text("PAUSED", 10, 35)


def key_pressed() -> None:
    global R, dt, mu, sigma, A, K_fft, paused, preset_name

    if py5.key == "1":
        preset_name = "orbium"
    elif py5.key == "2":
        preset_name = "geminium"
    elif py5.key == "3":
        preset_name = "scutium"

    if py5.key in ("1", "2", "3"):
        p = PRESETS[preset_name]
        R, dt, mu, sigma = p["R"], p["dt"], p["mu"], p["sigma"]
        K_fft = _build_kernel(R, GRID_SIZE)
        A = _initialize_grid()
    elif py5.key == "r":
        A = _initialize_grid()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"lenia_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
