"""
Chladni Figures.

Visualize standing wave patterns on a 2D plate. At resonant frequencies,
sand on a vibrating plate migrates to the nodal lines — the points of zero
displacement. The displacement function for mode (m, n) is:

    z(x, y) = cos(m*pi*x) * cos(n*pi*y) - cos(n*pi*x) * cos(m*pi*y)

Points where |z| < threshold are nodal lines and rendered bright;
the rest is dark, producing the characteristic sand-pattern geometry.

The LFOBank modulates the threshold and a slow cross-fade between
adjacent modes to animate the transition between figures.
"""

import math
from pathlib import Path

import numpy as np
import py5

from logic_lab.shared.lfo import LFOBank

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 700
HEIGHT = 700
GRID = 400  # Computation grid resolution

PRESETS: list[tuple[int, int]] = [
    (2, 1),
    (2, 3),
    (3, 2),
    (3, 4),
    (4, 3),
    (4, 5),
    (5, 4),
    (1, 4),
]

preset_idx = 0
paused = False

lfo = LFOBank(sample_rate=60)
lfo.add("threshold", shape="sine", freq=0.04, low=0.02, high=0.18)
lfo.add("morph", shape="triangle", freq=0.008, low=0.0, high=1.0)
lfo.add("hue_shift", shape="sawtooth", freq=0.015, low=0.0, high=360.0)

# Pre-compute normalised grid coordinates [-1, 1]
_xs, _ys = np.meshgrid(
    np.linspace(0, 1, GRID, dtype=np.float32),
    np.linspace(0, 1, GRID, dtype=np.float32),
)


def _chladni(m: int, n: int) -> np.ndarray:
    return np.cos(m * math.pi * _xs) * np.cos(n * math.pi * _ys) - np.cos(
        n * math.pi * _xs
    ) * np.cos(m * math.pi * _ys)


cached_z: np.ndarray
cached_z_next: np.ndarray
cache_key: tuple[int, int]
cache_key_next: tuple[int, int]


def _rebuild_cache() -> None:
    global cached_z, cached_z_next, cache_key, cache_key_next
    m, n = PRESETS[preset_idx]
    m2, n2 = PRESETS[(preset_idx + 1) % len(PRESETS)]
    cache_key = (m, n)
    cache_key_next = (m2, n2)
    cached_z = _chladni(m, n)
    cached_z_next = _chladni(m2, n2)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.background(10, 10, 18)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _rebuild_cache()


def draw() -> None:
    global preset_idx

    if paused:
        return

    vals = lfo.tick_all()
    threshold = vals["threshold"]
    morph = vals["morph"]
    hue_shift = vals["hue_shift"]

    # Blend between current and next mode
    z = cached_z * (1.0 - morph) + cached_z_next * morph
    nodal = np.abs(z) < threshold

    # Advance preset when morph completes
    if morph > 0.98:
        preset_idx = (preset_idx + 1) % len(PRESETS)
        _rebuild_cache()

    py5.load_pixels()
    pixels = py5.pixels
    scale_x = WIDTH / GRID
    scale_y = HEIGHT / GRID

    # Map nodal mask to pixel buffer
    intensity = (1.0 - np.abs(z) / (threshold + 1e-6)).clip(0, 1)
    for gy in range(GRID):
        for gx in range(GRID):
            if nodal[gy, gx]:
                v = float(intensity[gy, gx])
                hue = (hue_shift + gx * 0.3 + gy * 0.2) % 360
                r, g, b = _hsb_to_rgb(hue, 60.0, v * 100.0)
                c = py5.color(r, g, b)
            else:
                dark = int(float(np.abs(z[gy, gx])) * 12)
                c = py5.color(dark, dark, dark + 5)
            px = int(gx * scale_x)
            py_ = int(gy * scale_y)
            if 0 <= px < WIDTH and 0 <= py_ < HEIGHT:
                pixels[py_ * WIDTH + px] = c

    py5.update_pixels()

    m, n = PRESETS[preset_idx]
    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"Chladni | mode ({m},{n}) | threshold={threshold:.3f} | ←/→=mode S=save", 10, 20)


def _hsb_to_rgb(h: float, s: float, b: float) -> tuple[int, int, int]:
    h = h % 360
    s /= 100.0
    b /= 100.0
    c = b * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = b - c
    if h < 60:
        r, g, bv = c, x, 0.0
    elif h < 120:
        r, g, bv = x, c, 0.0
    elif h < 180:
        r, g, bv = 0.0, c, x
    elif h < 240:
        r, g, bv = 0.0, x, c
    elif h < 300:
        r, g, bv = x, 0.0, c
    else:
        r, g, bv = c, 0.0, x
    return int((r + m) * 255), int((g + m) * 255), int((bv + m) * 255)


def key_pressed() -> None:
    global preset_idx, paused
    if py5.key_code == py5.RIGHT:
        preset_idx = (preset_idx + 1) % len(PRESETS)
        _rebuild_cache()
    elif py5.key_code == py5.LEFT:
        preset_idx = (preset_idx - 1) % len(PRESETS)
        _rebuild_cache()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        m, n = PRESETS[preset_idx]
        py5.save_frame(str(SCREENSHOT_DIR / f"chladni_{m}_{n}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
