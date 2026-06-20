"""
Iterated Function Systems — Chaos Game
An IFS is a finite set of affine contractions { fₙ } with probabilities { pₙ }.
The Hutchinson attractor is the unique set A such that A = ∪ fₙ(A).

Chaos game algorithm: start from any point, repeatedly apply a randomly
chosen transformation (weighted by pₙ), and plot the orbit. After enough
iterations the plot converges to the attractor regardless of starting point.

Vectorized: N_PARTICLES=80000 points evolved in parallel each frame.
A 2D histogram accumulates hit counts; the log-scaled count drives the
color so both dense cores and sparse filaments stay visible.

Presets:
  1  Barnsley Fern    — iconic botanical fractal
  2  Sierpinski       — classic triangle gasket
  3  Dragon Curve     — twin-dragon IFS
  4  Fractal Tree     — symmetric binary tree
  5  Crystal / Maple  — 6-fold symmetric crystal

Controls:
  1–5     — preset
  r       — reset particles
  c       — next colormap (ember / ice / spectrum / gold)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 600  # accumulation grid resolution
N_PARTICLES = 80_000
STEPS_PER_FRAME = 20

# Each IFS entry: list of (a,b,c,d,e,f, probability)
# Transformation: x' = a*x + b*y + e,  y' = c*x + d*y + f
PRESETS = {
    "barnsley_fern": [
        (0.00, 0.00, 0.00, 0.16, 0.00, 0.00, 0.01),
        (0.85, 0.04, -0.04, 0.85, 0.00, 1.60, 0.85),
        (0.20, -0.26, 0.23, 0.22, 0.00, 1.60, 0.07),
        (-0.15, 0.28, 0.26, 0.24, 0.00, 0.44, 0.07),
    ],
    "sierpinski": [
        (0.50, 0.00, 0.00, 0.50, 0.00, 0.00, 0.33),
        (0.50, 0.00, 0.00, 0.50, 0.50, 0.00, 0.33),
        (0.50, 0.00, 0.00, 0.50, 0.25, 0.43, 0.34),
    ],
    "dragon_curve": [
        (0.50, -0.50, 0.50, 0.50, 0.00, 0.00, 0.50),
        (-0.50, -0.50, 0.50, -0.50, 1.00, 0.00, 0.50),
    ],
    "fractal_tree": [
        (0.00, 0.00, 0.00, 0.50, 0.00, 0.00, 0.05),
        (0.42, -0.42, 0.42, 0.42, 0.00, 0.20, 0.40),
        (-0.42, 0.42, 0.42, 0.42, 0.00, 0.20, 0.40),
        (0.00, 0.00, 0.00, 0.50, 0.00, 0.50, 0.15),
    ],
    "crystal": [
        (0.382, 0.00, 0.00, 0.382, 0.00, 0.00, 0.20),
        (0.382, 0.00, 0.00, 0.382, 0.618, 0.00, 0.20),
        (0.191, -0.330, 0.330, 0.191, 0.309, 0.535, 0.20),
        (0.191, 0.330, -0.330, 0.191, 0.309, -0.535, 0.20),
        (-0.382, 0.00, 0.00, 0.382, 1.00, 0.00, 0.20),
    ],
}
PRESET_NAMES = list(PRESETS.keys())
CMAPS = ["ember", "ice", "spectrum", "gold"]

preset_idx = 0
cmap_idx = 0

_pts: np.ndarray  # (N, 2)
_hist: np.ndarray  # (GRID, GRID)  accumulated counts

# View bounds per preset (xmin, xmax, ymin, ymax)
_BOUNDS = {
    "barnsley_fern": (-2.5, 2.5, -0.2, 10.2),
    "sierpinski": (-0.1, 1.1, -0.1, 0.95),
    "dragon_curve": (-0.6, 1.6, -0.4, 1.2),
    "fractal_tree": (-0.6, 0.6, -0.1, 1.05),
    "crystal": (-0.2, 1.2, -0.6, 0.6),
}


def _reset() -> None:
    global _pts, _hist
    _pts = np.random.uniform(0, 1, (N_PARTICLES, 2)).astype(np.float64)
    _hist = np.zeros((GRID, GRID), dtype=np.float32)


def _step() -> None:
    transforms = PRESETS[PRESET_NAMES[preset_idx]]
    n_tf = len(transforms)
    probs = np.array([t[6] for t in transforms], dtype=np.float64)
    probs /= probs.sum()

    for _ in range(STEPS_PER_FRAME):
        # Choose a transform index for each particle
        idx = np.searchsorted(np.cumsum(probs), np.random.random(N_PARTICLES))
        idx = np.clip(idx, 0, n_tf - 1)

        new_pts = np.empty_like(_pts)
        for ti, (a, b, c, d, e, f, _p) in enumerate(transforms):
            m = idx == ti
            if not m.any():
                continue
            x, y = _pts[m, 0], _pts[m, 1]
            new_pts[m, 0] = a * x + b * y + e
            new_pts[m, 1] = c * x + d * y + f
        _pts[:] = new_pts

    # Accumulate to histogram
    xmin, xmax, ymin, ymax = _BOUNDS[PRESET_NAMES[preset_idx]]
    xi = (((_pts[:, 0] - xmin) / (xmax - xmin)) * GRID).astype(int)
    yi = (((_pts[:, 1] - ymin) / (ymax - ymin)) * GRID).astype(int)
    valid = (xi >= 0) & (xi < GRID) & (yi >= 0) & (yi < GRID)
    np.add.at(_hist, (GRID - 1 - yi[valid], xi[valid]), 1)


def _colorize(log_t: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.clip(log_t, 0, 1)
    if cmap_idx == 0:  # ember
        r8 = np.clip(t * 3.0 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip((t - 0.33) * 2.0 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip((t - 0.66) * 3.0 * 255, 0, 255).astype(np.uint8)
    elif cmap_idx == 1:  # ice
        r8 = np.clip((t - 0.5) * 2.0 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 1.5 * 200, 0, 255).astype(np.uint8)
        b8 = np.clip(t * 255, 0, 255).astype(np.uint8)
    elif cmap_idx == 2:  # spectrum
        h = (t * 280.0).astype(np.float32)
        h6 = h / 60.0
        i6 = h6.astype(np.int32) % 6
        f6 = h6 - i6
        q = 1.0 - f6
        r_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [1, q, 0, 0, f6], 1)
        g_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [f6, 1, 1, q, 0], 0)
        b_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [0, 0, f6, 1, 1], q)
        r8 = np.clip(r_f * t**0.4 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(g_f * t**0.4 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(b_f * t**0.4 * 255, 0, 255).astype(np.uint8)
    else:  # gold
        r8 = np.clip(t * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 0.75 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip((t - 0.7) * 2.0 * 255, 0, 255).astype(np.uint8)
    return r8, g8, b8


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    _step()

    ph, pw = py5.pixel_height, py5.pixel_width
    gy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    h_d = _hist[np.ix_(gy, gx)]

    max_h = h_d.max()
    if max_h > 0:
        log_t = np.log1p(h_d) / np.log1p(max_h)
    else:
        log_t = np.zeros_like(h_d)

    r8, g8, b8 = _colorize(log_t)
    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    py5.fill(220, 235, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"IFS  preset:{PRESET_NAMES[preset_idx]}  " f"pts:{N_PARTICLES}  cmap:{CMAPS[cmap_idx]}",
        8,
        18,
    )


def key_pressed() -> None:
    global preset_idx, cmap_idx
    k = py5.key
    if k == "r":
        _reset()
    elif k == "c":
        cmap_idx = (cmap_idx + 1) % len(CMAPS)
    elif k == "1":
        preset_idx = 0
        _reset()
    elif k == "2":
        preset_idx = 1
        _reset()
    elif k == "3":
        preset_idx = 2
        _reset()
    elif k == "4":
        preset_idx = 3
        _reset()
    elif k == "5":
        preset_idx = 4
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"ifs_{PRESET_NAMES[preset_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
