"""
Hénon Map Attractor
Discrete 2D chaotic map: x_{n+1} = 1 − a·x_n² + y_n,  y_{n+1} = b·x_n
The classical attractor (a=1.4, b=0.3) is a fractal "banana" with box
dimension ≈ 1.26. Rendered via density accumulation: millions of orbit
points are binned into a grid and colorized by log-count.

Controls:
  1–4     — switch preset (classic / sparse / dense / inverted)
  a / A   — decrease / increase a parameter
  b / B   — decrease / increase b parameter
  r       — reset density (current parameters)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 700  # density grid resolution
N_TRAJ = 800  # parallel trajectories (vectorized over this dimension)
STEPS_PER_FRAME = 300  # map iterations per trajectory per frame

PRESETS: dict[str, dict[str, float]] = {
    "classic": {"a": 1.40, "b": 0.30},
    "sparse": {"a": 1.20, "b": 0.30},
    "dense": {"a": 1.56, "b": 0.30},
    "inverted": {"a": 1.40, "b": -0.30},
}

# Attractor bounding box for classic params; widens for others
X_MIN, X_MAX = -1.6, 1.6
Y_MIN, Y_MAX = -0.65, 0.65

# Parameters
a_param = PRESETS["classic"]["a"]
b_param = PRESETS["classic"]["b"]
preset_name = "classic"

# State
_state: np.ndarray  # (N_TRAJ, 2) current (x, y) per trajectory
_density: np.ndarray  # (GRID, GRID) accumulated hit counts
_px_to_cx: np.ndarray
_py_to_cy: np.ndarray
_total_pts = 0


def _reset() -> None:
    global _state, _density, _total_pts
    _state = np.random.uniform([-0.5, -0.2], [0.5, 0.2], (N_TRAJ, 2))
    # Warm up so trajectories settle on the attractor
    for _ in range(400):
        x, y = _state[:, 0], _state[:, 1]
        nx = 1.0 - a_param * x * x + y
        ny = b_param * x
        _state = np.column_stack([nx, ny])
        # Re-seed escaped trajectories
        esc = np.abs(_state[:, 0]) > 5
        if esc.any():
            _state[esc] = np.random.uniform([-0.1, -0.05], [0.1, 0.05], (esc.sum(), 2))
    _density = np.zeros((GRID, GRID), dtype=np.float64)
    _total_pts = 0


def _iterate_and_accumulate() -> None:
    global _state, _total_pts
    for _ in range(STEPS_PER_FRAME):
        x, y = _state[:, 0], _state[:, 1]
        nx = 1.0 - a_param * x * x + y
        ny = b_param * x
        _state = np.column_stack([nx, ny])

        # Re-seed escaped trajectories
        esc = np.abs(_state[:, 0]) > 6
        if esc.any():
            _state[esc] = np.random.uniform([-0.1, -0.05], [0.1, 0.05], (esc.sum(), 2))

        # Accumulate to density grid
        gx = np.floor((_state[:, 0] - X_MIN) / (X_MAX - X_MIN) * GRID).astype(np.int32)
        gy = np.floor((_state[:, 1] - Y_MIN) / (Y_MAX - Y_MIN) * GRID).astype(np.int32)
        valid = (gx >= 0) & (gx < GRID) & (gy >= 0) & (gy < GRID)
        np.add.at(_density, (gy[valid], gx[valid]), 1)
    _total_pts += N_TRAJ * STEPS_PER_FRAME


def _render() -> None:
    """Map log-density to a cold-hot colormap (dark → blue → cyan → white)."""
    log_d = np.log1p(_density)
    max_d = log_d.max()
    if max_d < 1e-9:
        py5.background(230, 20, 8)
        return

    norm = log_d / max_d  # (GRID, GRID), 0..1

    # Colormap: 0→black, 0.3→deep blue, 0.6→cyan, 1→white
    r = np.clip(norm * 2 - 0.5, 0, 1)
    g = np.clip(norm * 2 - 0.2, 0, 1)
    b = np.clip(norm * 1.5, 0, 1)

    r8 = (r * 255).astype(np.uint8)
    g8 = (g * 255).astype(np.uint8)
    b8 = (b * 255).astype(np.uint8)

    # Map density grid → display resolution
    r_d = r8[np.ix_(_py_to_cy, _px_to_cx)]
    g_d = g8[np.ix_(_py_to_cy, _px_to_cx)]
    b_d = b8[np.ix_(_py_to_cy, _px_to_cx)]

    argb = (
        np.int32(-16777216)
        | (r_d.astype(np.int32) << 16)
        | (g_d.astype(np.int32) << 8)
        | b_d.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()


def setup() -> None:
    global _px_to_cx, _py_to_cy
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, ph = py5.pixel_width, py5.pixel_height
    _px_to_cx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    _py_to_cy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    _reset()


def draw() -> None:
    _iterate_and_accumulate()
    _render()

    # HUD
    py5.fill(160, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    mp = _total_pts / 1_000_000
    py5.text(f"preset:{preset_name}  a:{a_param:.3f}  b:{b_param:.3f}  pts:{mp:.1f}M", 8, 18)


def key_pressed() -> None:
    global a_param, b_param, preset_name
    k = py5.key
    if k == "r":
        _reset()
    elif k == "a":
        a_param = max(0.1, round(a_param - 0.02, 3))
        _reset()
    elif k == "A":
        a_param = min(2.0, round(a_param + 0.02, 3))
        _reset()
    elif k == "b":
        b_param = round(b_param - 0.02, 3)
        _reset()
    elif k == "B":
        b_param = round(b_param + 0.02, 3)
        _reset()
    elif k == "1":
        preset_name = "classic"
        a_param, b_param = PRESETS[preset_name]["a"], PRESETS[preset_name]["b"]
        _reset()
    elif k == "2":
        preset_name = "sparse"
        a_param, b_param = PRESETS[preset_name]["a"], PRESETS[preset_name]["b"]
        _reset()
    elif k == "3":
        preset_name = "dense"
        a_param, b_param = PRESETS[preset_name]["a"], PRESETS[preset_name]["b"]
        _reset()
    elif k == "4":
        preset_name = "inverted"
        a_param, b_param = PRESETS[preset_name]["a"], PRESETS[preset_name]["b"]
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"henon_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
