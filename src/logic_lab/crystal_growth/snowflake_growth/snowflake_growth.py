"""
Snowflake Crystal Growth
Dendritic crystal growth on a hexagonal lattice (Reiter 1996 diffusion model).

A seed ice crystal at center accumulates water vapor from the background field.
Receptive boundary cells crystallize when their vapor reaches saturation,
producing intricate 6-fold symmetric dendrites characteristic of real snowflakes.

Controls:
  1 / 2 / 3  — switch preset (dendrite / plate / fern)
  r          — reset current preset
  Space      — pause / resume
  s          — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# ─── Reiter (1996) presets ───────────────────────────────────────────────────
# beta:      background vapor (lower → sparser, more branchy)
# gamma:     accretion rate per step for receptive boundary cells
# diffusion: α coefficient for vapor diffusion (0–1)
PRESETS: dict[str, dict[str, float]] = {
    "dendrite": {"beta": 0.35, "gamma": 0.001, "diffusion": 0.5},
    "plate": {"beta": 0.50, "gamma": 0.001, "diffusion": 0.5},
    "fern": {"beta": 0.28, "gamma": 0.0005, "diffusion": 0.4},
}

N = 150  # half-grid radius; full grid = (2N+1)²
PIXEL_SCALE = 3  # logical canvas pixels per grid cell
STEPS_PER_FRAME = 10

ROWS = 2 * N + 1
COLS = 2 * N + 1
MID = N

# ─── Precomputed grid arrays ─────────────────────────────────────────────────
_row_idx = np.arange(ROWS)[:, np.newaxis]
_col_idx = np.arange(COLS)[np.newaxis, :]
_row_even = _row_idx % 2 == 0  # True for even rows
_dist_norm = np.hypot(_row_idx - MID, _col_idx - MID) / N  # 0 at center, ~1 at edge

# ─── Display index arrays (filled in setup, support HiDPI) ──────────────────
_px_to_cx: np.ndarray
_py_to_cy: np.ndarray

# ─── Simulation state ───────────────────────────────────────────────────────
vapor: np.ndarray
ice: np.ndarray
paused = False
done = False
preset_name = "dendrite"
_beta = PRESETS["dendrite"]["beta"]
_gamma = PRESETS["dendrite"]["gamma"]
_diffusion = PRESETS["dendrite"]["diffusion"]


def _reset() -> None:
    global vapor, ice, done, _beta, _gamma, _diffusion
    p = PRESETS[preset_name]
    _beta, _gamma, _diffusion = p["beta"], p["gamma"], p["diffusion"]
    vapor = np.full((ROWS, COLS), _beta, dtype=np.float64)
    ice = np.zeros((ROWS, COLS), dtype=bool)
    vapor[MID, MID] = 0.0
    ice[MID, MID] = True
    done = False


def _hex_sum(arr: np.ndarray, pad_val: float) -> np.ndarray:
    """Vectorized sum of 6 hex neighbors on an offset-row grid.

    Even rows: neighbors at (-1,-1),(-1,0),(0,-1),(0,+1),(+1,-1),(+1,0)
    Odd rows:  neighbors at (-1,0),(-1,+1),(0,-1),(0,+1),(+1,0),(+1,+1)
    """
    p = np.pad(arr, 1, constant_values=pad_val)
    s_even = p[:-2, :-2] + p[:-2, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:] + p[2:, :-2] + p[2:, 1:-1]
    s_odd = p[:-2, 1:-1] + p[:-2, 2:] + p[1:-1, :-2] + p[1:-1, 2:] + p[2:, 1:-1] + p[2:, 2:]
    return np.where(_row_even, s_even, s_odd)


def _step() -> None:
    global vapor, ice, done

    nb_vapor = _hex_sum(vapor, _beta)
    ice_nb = _hex_sum(ice.astype(np.float64), 0.0)

    # Receptive: non-ice cells touching at least one ice neighbor
    receptive = (ice_nb > 0.0) & ~ice
    free = ~receptive & ~ice

    new_vapor = vapor.copy()

    # Diffuse free cells toward local average
    new_vapor[free] += _diffusion / 6.0 * (nb_vapor[free] - 6.0 * vapor[free])

    # Receptive cells accumulate vapor (accretion)
    new_vapor[receptive] += _gamma

    # Crystallize cells that reached saturation
    new_crystals = receptive & (new_vapor >= 1.0)
    new_vapor[new_crystals] = 0.0  # vapor converts to solid ice
    ice[new_crystals] = True

    # Hard boundary: infinite vapor reservoir at edges
    new_vapor[[0, -1], :] = _beta
    new_vapor[:, [0, -1]] = _beta
    vapor[:] = new_vapor

    # Stop when crystal reaches 12 % from any edge
    margin = max(N // 8, 6)
    if ice[MID, margin] or ice[MID, COLS - 1 - margin]:
        done = True


def _render() -> None:
    """Vectorized ARGB pixel fill mapped to display resolution."""
    r_g = np.full((ROWS, COLS), 5, dtype=np.int32)
    g_g = np.full((ROWS, COLS), 10, dtype=np.int32)
    b_g = np.full((ROWS, COLS), 30, dtype=np.int32)

    # Ice: white-blue, warmer toward edges
    ice_r = np.clip(180 + _dist_norm * 70, 0, 255).astype(np.int32)
    ice_g = np.clip(210 + _dist_norm * 40, 0, 255).astype(np.int32)
    r_g[ice] = ice_r[ice]
    g_g[ice] = ice_g[ice]
    b_g[ice] = 255

    # Vapor: faint blue glow proportional to local supersaturation
    v_norm = np.clip((vapor - _beta * 0.4) / (1.0 - _beta * 0.4 + 1e-9), 0, 1).astype(np.float32)
    r_g[~ice] = np.clip(5 + (v_norm[~ice] * 8).astype(np.int32), 0, 255)
    b_g[~ice] = np.clip(30 + (v_norm[~ice] * 70).astype(np.int32), 0, 255)

    # Map grid → display pixels (HiDPI-aware)
    r_d = r_g[np.ix_(_py_to_cy, _px_to_cx)]
    g_d = g_g[np.ix_(_py_to_cy, _px_to_cx)]
    b_d = b_g[np.ix_(_py_to_cy, _px_to_cx)]

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
    py5.size(COLS * PIXEL_SCALE, ROWS * PIXEL_SCALE)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, ph = py5.pixel_width, py5.pixel_height
    _px_to_cx = (np.arange(pw) * COLS / pw).astype(int).clip(0, COLS - 1)
    _py_to_cy = (np.arange(ph) * ROWS / ph).astype(int).clip(0, ROWS - 1)
    _reset()


def draw() -> None:
    if not paused and not done:
        for _ in range(STEPS_PER_FRAME):
            _step()

    _render()

    py5.fill(160, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    ice_pct = float(ice.sum()) / (ROWS * COLS) * 100.0
    status = "DONE" if done else ("PAUSED" if paused else "")
    py5.text(
        f"preset:{preset_name}  β:{_beta:.2f}  ice:{ice_pct:.1f}%  {status}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, preset_name
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "1":
        preset_name = "dendrite"
        _reset()
    elif k == "2":
        preset_name = "plate"
        _reset()
    elif k == "3":
        preset_name = "fern"
        _reset()
    elif k == "r":
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"snowflake_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
