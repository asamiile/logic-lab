"""
Voronoi Landscape
Space is partitioned by N seed points into cells: each pixel belongs to the
cell of its nearest seed. Elevation is assigned to seeds and interpolated
toward cell boundaries to form a rugged landscape.

Height model:
  h(x,y) = h_seed  −  blend * (d2 − d1) / d1
where d1 = distance to nearest seed, d2 = distance to second-nearest seed.
The ratio (d2−d1)/d1 is 0 at the seed and grows toward boundaries,
creating smooth hill-tops with sharp ridges between cells.

Modes:
  1  cells     — flat-color Voronoi diagram with thin ridge lines
  2  elevation — smooth height field colored by altitude + hillshade
  3  flow      — gradient flow lines (water runoff paths)
  4  distance  — d2/d1 ratio showing ridge topology

Seeds drift slowly each frame creating an organic morphing landscape.

Controls:
  1–4     — display mode
  r       — randomize seeds
  n / N   — fewer / more seeds
  Space   — pause / resume drift
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
N_SEEDS = 40
DRIFT_SPEED = 0.25  # pixels per frame

mode = 2
paused = False

_seeds: np.ndarray  # (N, 2) positions
_heights: np.ndarray  # (N,)   elevation [0, 1]
_vel: np.ndarray  # (N, 2) drift velocity

# Precomputed pixel grids
_gx: np.ndarray
_gy: np.ndarray


def _reset() -> None:
    global _seeds, _heights, _vel
    _seeds = np.random.uniform([20, 20], [WIDTH - 20, HEIGHT - 20], (N_SEEDS, 2)).astype(np.float32)
    _heights = np.random.uniform(0.0, 1.0, N_SEEDS).astype(np.float32)
    angles = np.random.uniform(0, 2 * np.pi, N_SEEDS)
    _vel = np.column_stack([np.cos(angles) * DRIFT_SPEED, np.sin(angles) * DRIFT_SPEED]).astype(
        np.float32
    )


def _drift() -> None:
    global _seeds, _vel
    _seeds += _vel
    # Bounce at borders
    for dim, limit in enumerate([WIDTH, HEIGHT]):
        lo, hi = 20.0, float(limit) - 20.0
        hit_lo = _seeds[:, dim] < lo
        hit_hi = _seeds[:, dim] > hi
        _vel[hit_lo, dim] = np.abs(_vel[hit_lo, dim])
        _vel[hit_hi, dim] = -np.abs(_vel[hit_hi, dim])
        _seeds[:, dim] = np.clip(_seeds[:, dim], lo, hi)


def _voronoi_fields() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (nearest_idx, d1, d2) at every pixel."""
    ph, pw = _gx.shape
    # (N, H, W) distance from each seed to each pixel
    dx = _gx[np.newaxis, :, :] - _seeds[:, 0, np.newaxis, np.newaxis]
    dy = _gy[np.newaxis, :, :] - _seeds[:, 1, np.newaxis, np.newaxis]
    dists = np.sqrt(dx * dx + dy * dy)  # (N, H, W)

    order = np.argsort(dists, axis=0)
    d1 = dists[order[0], np.arange(ph)[:, None], np.arange(pw)[None, :]]
    d2 = dists[order[1], np.arange(ph)[:, None], np.arange(pw)[None, :]]
    nearest = order[0]
    return nearest, d1, d2


def _hillshade(h: np.ndarray) -> np.ndarray:
    dhdx = np.gradient(h, axis=1)
    dhdy = np.gradient(h, axis=0)
    lx, ly, lz = -0.7, -0.7, 1.5
    L = np.sqrt(lx**2 + ly**2 + lz**2)
    lx, ly, lz = lx / L, ly / L, lz / L
    nx = -dhdx * 4.0
    ny = -dhdy * 4.0
    nz = np.ones_like(h)
    nm = np.sqrt(nx**2 + ny**2 + nz**2) + 1e-9
    return np.clip(nx / nm * lx + ny / nm * ly + nz / nm * lz, 0, 1)


def _render() -> None:
    nearest, d1, d2 = _voronoi_fields()

    if mode == 1:
        # Flat Voronoi cells with thin ridge highlight
        seed_hues = np.linspace(0, 300, N_SEEDS, dtype=np.float32)
        hue = seed_hues[nearest]
        h6 = hue / 60.0
        i6 = h6.astype(np.int32) % 6
        f6 = h6 - i6
        q = 1.0 - f6
        r_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [1, q, 0, 0, f6], 1)
        g_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [f6, 1, 1, q, 0], 0)
        b_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [0, 0, f6, 1, 1], q)
        ridge = np.clip(1.0 - (d2 - d1) * 3.0, 0, 1)
        r8 = np.clip(r_f * (0.4 + ridge * 0.6) * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(g_f * (0.4 + ridge * 0.6) * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(b_f * (0.4 + ridge * 0.6) * 255, 0, 255).astype(np.uint8)

    elif mode == 2:
        # Elevation + hillshade
        seed_h = _heights[nearest]
        blend = np.clip((d2 - d1) / (d1 + 1e-6) * 0.5, 0, 1)
        height = seed_h * (1.0 - blend * 0.6)
        shade = _hillshade(height)
        h2 = height
        # Geo colormap
        r_f = np.select(
            [h2 < 0.25, h2 < 0.45, h2 < 0.65, h2 < 0.82],
            [h2 * 30, h2 * 70 + 10, h2 * 160 + 20, h2 * 210 + 15],
            default=h2 * 255,
        )
        g_f = np.select(
            [h2 < 0.25, h2 < 0.45, h2 < 0.65, h2 < 0.82],
            [h2 * 80 + 30, h2 * 130 + 30, h2 * 155 + 25, h2 * 200 + 10],
            default=h2 * 255,
        )
        b_f = np.select(
            [h2 < 0.25, h2 < 0.45, h2 < 0.65, h2 < 0.82],
            [h2 * 180 + 50, h2 * 60 + 15, h2 * 50 + 5, h2 * 130 + 5],
            default=h2 * 255,
        )
        s = 0.35 + shade * 0.75
        r8 = np.clip(r_f * s, 0, 255).astype(np.uint8)
        g8 = np.clip(g_f * s, 0, 255).astype(np.uint8)
        b8 = np.clip(b_f * s, 0, 255).astype(np.uint8)

    elif mode == 3:
        # Flow / gradient map: color by gradient direction
        seed_h = _heights[nearest]
        blend = np.clip((d2 - d1) / (d1 + 1e-6) * 0.5, 0, 1)
        height = seed_h * (1.0 - blend * 0.6)
        gx_h = np.gradient(height, axis=1)
        gy_h = np.gradient(height, axis=0)
        angle = (np.arctan2(gy_h, gx_h) / np.pi + 1.0) * 0.5  # [0,1]
        mag = np.sqrt(gx_h**2 + gy_h**2)
        mag_n = np.clip(mag / (mag.max() + 1e-9), 0, 1)
        h6 = angle * 5.9
        i6 = h6.astype(np.int32) % 6
        f6 = h6 - i6
        q = 1.0 - f6
        r_f2 = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [1, q, 0, 0, f6], 1)
        g_f2 = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [f6, 1, 1, q, 0], 0)
        b_f2 = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [0, 0, f6, 1, 1], q)
        bri = 0.2 + mag_n * 0.8
        r8 = np.clip(r_f2 * bri * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(g_f2 * bri * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(b_f2 * bri * 255, 0, 255).astype(np.uint8)

    else:  # mode 4: distance ratio
        ratio = np.clip((d2 - d1) / (d2 + 1e-6), 0, 1)
        r8 = np.clip(ratio * 255, 0, 255).astype(np.uint8)
        g8 = np.clip((ratio - 0.3) * 1.4 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip((1.0 - ratio) * 200 + ratio * 50, 0, 255).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()


def setup() -> None:
    global _gx, _gy
    py5.size(WIDTH, HEIGHT)
    ph, pw = py5.pixel_height, py5.pixel_width
    xs = np.arange(pw, dtype=np.float32)
    ys = np.arange(ph, dtype=np.float32)
    _gx = np.tile(xs, (ph, 1))
    _gy = np.tile(ys[:, None], (1, pw))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        _drift()
    _render()

    mode_names = ["", "cells", "elevation", "flow", "distance"]
    py5.fill(220, 235, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Voronoi  n={N_SEEDS}  mode:{mode_names[mode]}  " f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global mode, paused, N_SEEDS, _gx, _gy
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        mode = 1
    elif k == "2":
        mode = 2
    elif k == "3":
        mode = 3
    elif k == "4":
        mode = 4
    elif k == "n":
        N_SEEDS = max(8, N_SEEDS - 8)
        _reset()
    elif k == "N":
        N_SEEDS = min(120, N_SEEDS + 8)
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"voronoi_m{mode}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
