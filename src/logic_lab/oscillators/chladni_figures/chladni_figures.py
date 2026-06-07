"""
Chladni Figures.

Visualize standing wave patterns on a 2D plate. At resonant frequencies,
sand on a vibrating plate migrates to the nodal lines — the points of zero
displacement. The displacement function for mode (m, n) is:

    z(x, y) = cos(m*pi*x) * cos(n*pi*y) - cos(n*pi*x) * cos(m*pi*y)

Points where |z| < threshold are nodal lines and rendered bright;
the rest is dark, producing the characteristic sand-pattern geometry.

The LFOBank modulates the threshold and a slow cross-fade between
adjacent modes. A NoiseField adds organic perturbation to break perfect
symmetry — the nodal lines develop a natural, irregular texture.

Pixel filling is fully vectorized via numpy for smooth performance.
"""

import math
from pathlib import Path

import numpy as np
import py5

from logic_lab.shared.lfo import LFOBank
from logic_lab.shared.noise_field import NoiseField

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
lfo.add("noise_amp", shape="triangle", freq=0.012, low=0.01, high=0.08)

# Organic symmetry-breaking noise
_noise = NoiseField(seed=13, octaves=3, persistence=0.6, lacunarity=2.0, scale=0.5)
_noise_t = 0.0

# Pre-compute normalised grid coordinates [0, 1]
_xs, _ys = np.meshgrid(
    np.linspace(0, 1, GRID, dtype=np.float32),
    np.linspace(0, 1, GRID, dtype=np.float32),
)

# Pixel-to-grid index maps (computed once)
_px_to_gx = (np.arange(WIDTH) * GRID / WIDTH).astype(int).clip(0, GRID - 1)
_py_to_gy = (np.arange(HEIGHT) * GRID / HEIGHT).astype(int).clip(0, GRID - 1)


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


def _hsb_to_rgb_vec(
    h: np.ndarray, s: float, b: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized HSB (h∈[0,360), s∈[0,1], b∈[0,1]) → uint8 RGB arrays."""
    h6 = (h % 360.0) / 60.0
    i = np.floor(h6).astype(np.int32) % 6
    f = (h6 - np.floor(h6)).astype(np.float32)
    p = b * (1.0 - s)
    q = b * (1.0 - s * f)
    tv = b * (1.0 - s * (1.0 - f))
    r = np.select([i == 0, i == 1, i == 2, i == 3, i == 4], [b, q, p, p, tv], default=b)
    g = np.select([i == 0, i == 1, i == 2, i == 3, i == 4], [tv, b, b, q, p], default=p)
    bl = np.select([i == 0, i == 1, i == 2, i == 3, i == 4], [p, p, tv, b, b], default=q)
    return (
        (r * 255).clip(0, 255).astype(np.uint8),
        (g * 255).clip(0, 255).astype(np.uint8),
        (bl * 255).clip(0, 255).astype(np.uint8),
    )


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.background(10, 10, 18)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _rebuild_cache()


def draw() -> None:
    global preset_idx, _noise_t

    if paused:
        return

    vals = lfo.tick_all()
    threshold = vals["threshold"]
    morph = vals["morph"]
    hue_shift = vals["hue_shift"]
    noise_amp = vals["noise_amp"]

    # Blend between current and next mode
    z = cached_z * np.float32(1.0 - morph) + cached_z_next * np.float32(morph)

    # Organic perturbation — breaks perfect bilateral symmetry
    perturbation = _noise.grid(GRID, GRID, t=_noise_t) * np.float32(2.0) - np.float32(1.0)
    _noise_t += 0.0004
    z_p = z + perturbation * np.float32(noise_amp)

    nodal = np.abs(z_p) < np.float32(threshold)

    # Advance preset when morph completes
    if morph > 0.98:
        preset_idx = (preset_idx + 1) % len(PRESETS)
        _rebuild_cache()

    # --- Vectorized pixel filling ---
    # Hue field: (GRID, GRID)
    gx_arr = np.arange(GRID, dtype=np.float32)[np.newaxis, :]
    gy_arr = np.arange(GRID, dtype=np.float32)[:, np.newaxis]
    hue_field = (
        np.float32(hue_shift) + gx_arr * np.float32(0.3) + gy_arr * np.float32(0.2)
    ) % np.float32(360.0)

    # Brightness from clamped intensity (0 outside nodal lines)
    intensity = (np.float32(1.0) - np.abs(z_p) / (np.float32(threshold) + np.float32(1e-6))).clip(
        0, 1
    )
    bright = np.where(nodal, intensity, np.float32(0.0))

    r_grid, g_grid, b_grid = _hsb_to_rgb_vec(hue_field, 0.6, bright)

    # Dark background for non-nodal regions
    dark = (np.abs(z_p) * np.float32(12.0)).clip(0, 255).astype(np.uint8)
    dark_b = np.clip(dark.astype(np.int32) + 5, 0, 255).astype(np.uint8)
    r_grid = np.where(nodal, r_grid, dark)
    g_grid = np.where(nodal, g_grid, dark)
    b_grid = np.where(nodal, b_grid, dark_b)

    # Map grid → display resolution via pre-computed index arrays
    r_disp = r_grid[np.ix_(_py_to_gy, _px_to_gx)]
    g_disp = g_grid[np.ix_(_py_to_gy, _px_to_gx)]
    b_disp = b_grid[np.ix_(_py_to_gy, _px_to_gx)]

    # Pack ARGB int32 (alpha=255 → 0xFF000000 = -16777216 as signed int32)
    argb = (
        np.int32(-16777216)
        | (r_disp.astype(np.int32) << 16)
        | (g_disp.astype(np.int32) << 8)
        | b_disp.astype(np.int32)
    )

    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    m, n = PRESETS[preset_idx]
    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Chladni | mode ({m},{n}) | threshold={threshold:.3f} | ←/→=mode N=new S=save",
        10,
        20,
    )


def key_pressed() -> None:
    global preset_idx, paused, _noise_t
    if py5.key_code == py5.RIGHT:
        preset_idx = (preset_idx + 1) % len(PRESETS)
        _rebuild_cache()
    elif py5.key_code == py5.LEFT:
        preset_idx = (preset_idx - 1) % len(PRESETS)
        _rebuild_cache()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "n":
        _noise_t += 50.0  # jump noise phase for instant variety
    elif py5.key == "s":
        m, n = PRESETS[preset_idx]
        py5.save_frame(str(SCREENSHOT_DIR / f"chladni_{m}_{n}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
