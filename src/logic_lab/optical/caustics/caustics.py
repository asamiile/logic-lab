"""
Water Caustics
Light passes through a rippled water surface and focuses into bright caustic
patterns on the pool floor — the same shimmering web seen in swimming pools.

Algorithm (reverse ray mapping):
  1. Build a height field h(x,y) as a sum of sine/cosine waves.
  2. Compute the surface normal at each point from ∇h.
  3. Apply Snell's law to compute the refracted ray direction (air→water).
  4. Each surface point maps to a floor point: floor = surface + depth*refracted.
  5. The floor brightness is proportional to how many rays land per unit area
     (local density of the mapped grid = 1/Jacobian of the mapping).
  6. Accumulate over multiple frames with slowly evolving wave phases for a
     smooth, time-averaged caustic (rather than high-contrast flicker).

The Jacobian is approximated by comparing the mapping of neighbouring pixels.

Controls:
  1   — single-frame snapshot (raw caustic)
  2   — accumulated average (cleaner, builds up over time)
  3   — wave height field (shows the water surface)
  r   — reset accumulator
  Space — pause / resume wave animation
  +/- — increase / decrease water depth
  s   — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
GRID = 300  # simulation resolution
N_IOR = 1.33  # index of refraction (water)
DEPTH = 1.8  # virtual depth (in grid units) for ray travel

mode = 2
paused = False

_t = 0.0
_accum: np.ndarray  # (GRID, GRID) accumulated intensity
_accum_n = 0

# Precomputed pixel grids for display upscaling
_gx: np.ndarray
_gy: np.ndarray

# Wave parameters: (amplitude, freq_x, freq_y, phase_speed)
_WAVES = [
    (0.08, 2.1, 1.3, 0.9),
    (0.06, 1.4, 2.7, 1.1),
    (0.05, 3.2, 0.8, 0.7),
    (0.04, 0.9, 3.5, 1.3),
    (0.03, 2.5, 2.2, 0.6),
]


def _height_field(t: float) -> np.ndarray:
    xs = np.linspace(0, 2 * np.pi, GRID, dtype=np.float32)
    ys = np.linspace(0, 2 * np.pi, GRID, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    h = np.zeros((GRID, GRID), dtype=np.float32)
    for amp, fx, fy, ps in _WAVES:
        h += amp * np.sin(fx * X + fy * Y + ps * t)
    return h


def _caustic_frame(t: float) -> np.ndarray:
    h = _height_field(t)
    # Surface normals from gradient
    dhdx = np.gradient(h, axis=1)
    dhdy = np.gradient(h, axis=0)

    # Normal vector (un-normalized): N = (-dhdx, -dhdy, 1)
    nx = -dhdx
    ny = -dhdy
    nz = np.ones((GRID, GRID), dtype=np.float32)
    nm = np.sqrt(nx**2 + ny**2 + nz**2)
    nx /= nm
    ny /= nm
    nz /= nm

    # Incident ray: straight down (0,0,-1) in world coords
    # Refraction: Snell's law in 2D (tangential components)
    # sin(theta_t)/sin(theta_i) = 1/N_IOR
    # For near-normal incidence, deflection ≈ (n1-n2)/n2 * tangential_normal
    eta = 1.0 / N_IOR
    # cos(theta_i) = nz (dot with downward normal)
    cos_i = nz
    sin2_t = eta**2 * (1.0 - cos_i**2)
    cos_t = np.sqrt(np.clip(1.0 - sin2_t, 0, 1))

    # Refracted direction components (x,y offset per unit depth)
    rx = eta * nx * (cos_t - cos_i) / (nz + 1e-9)
    ry = eta * ny * (cos_t - cos_i) / (nz + 1e-9)

    # Map each surface pixel to floor pixel
    xs = np.arange(GRID, dtype=np.float32)
    ys = np.arange(GRID, dtype=np.float32)
    floor_x = xs[np.newaxis, :] + rx * DEPTH * GRID / (2 * np.pi)
    floor_y = ys[:, np.newaxis] + ry * DEPTH * GRID / (2 * np.pi)

    floor_xi = np.clip(floor_x.astype(int), 0, GRID - 1)
    floor_yi = np.clip(floor_y.astype(int), 0, GRID - 1)

    caustic = np.zeros((GRID, GRID), dtype=np.float32)
    np.add.at(caustic, (floor_yi.ravel(), floor_xi.ravel()), 1)
    return caustic


def _upscale(grid: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ph, pw = _gx.shape
    gy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    return grid[np.ix_(gy, gx)]


def _colorize_caustic(c: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    m = c.max()
    t = np.clip(c / (m + 1e-9), 0, 1)
    # Warm pool-water palette: dark blue-green → bright white-gold
    r8 = np.clip((t - 0.3) * 1.4 * 255, 0, 255).astype(np.uint8)
    g8 = np.clip((t - 0.1) * 1.2 * 255, 0, 255).astype(np.uint8)
    b8 = np.clip(t**0.6 * 200 + (1 - t) * 80, 0, 255).astype(np.uint8)
    return r8, g8, b8


def _colorize_wave(h: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.clip((h - h.min()) / (h.max() - h.min() + 1e-9), 0, 1)
    r8 = np.clip((t - 0.5) * 2.0 * 200, 0, 255).astype(np.uint8)
    g8 = np.clip(t * 1.5 * 200, 0, 255).astype(np.uint8)
    b8 = np.clip(t * 255, 0, 255).astype(np.uint8)
    return r8, g8, b8


def setup() -> None:
    global _gx, _gy, _accum
    py5.size(WIDTH, HEIGHT)
    ph, pw = py5.pixel_height, py5.pixel_width
    xs = np.arange(pw, dtype=np.float32)
    ys = np.arange(ph, dtype=np.float32)
    _gx = np.tile(xs, (ph, 1))
    _gy = np.tile(ys[:, None], (1, pw))
    _accum = np.zeros((GRID, GRID), dtype=np.float32)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global _t, _accum, _accum_n

    if not paused:
        _t += 0.04

    c = _caustic_frame(_t)

    if mode == 1:
        disp = c
        r8, g8, b8 = _colorize_caustic(_upscale(disp))
    elif mode == 2:
        if not paused:
            _accum += c
            _accum_n += 1
        disp = _accum / max(_accum_n, 1)
        r8, g8, b8 = _colorize_caustic(_upscale(disp))
    else:
        h = _height_field(_t)
        r8, g8, b8 = _colorize_wave(_upscale(h))

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    mode_names = ["", "snapshot", "accumulated", "wave field"]
    py5.fill(200, 230, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Caustics  depth={DEPTH:.1f}  IOR={N_IOR}  "
        f"mode:{mode_names[mode]}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global mode, paused, DEPTH, _accum, _accum_n
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _accum[:] = 0.0
        _accum_n = 0
    elif k == "1":
        mode = 1
    elif k == "2":
        mode = 2
        _accum[:] = 0.0
        _accum_n = 0
    elif k == "3":
        mode = 3
    elif k == "+":
        DEPTH = min(6.0, round(DEPTH + 0.2, 1))
    elif k == "-":
        DEPTH = max(0.4, round(DEPTH - 0.2, 1))
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"caustics_m{mode}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
