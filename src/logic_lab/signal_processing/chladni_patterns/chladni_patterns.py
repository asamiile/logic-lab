"""
Chladni Figures — Resonance Patterns of a Vibrating Plate
In 1787 Ernst Chladni spread sand on a metal plate and drew a violin bow along
the edge. Sand scattered from vibrating regions and accumulated at nodal lines
(points of zero displacement) — forming beautiful symmetric patterns.

The displacement of a square plate's (m,n) resonance mode is:
  f(x,y) = cos(m·π·x)·cos(n·π·y)  ±  cos(n·π·x)·cos(m·π·y)

Nodal lines are where f = 0. We render the "sand density" as:
  brightness ∝ exp(−|f|² / σ²)

Higher modes (larger m,n) create finer, more intricate patterns.
The sign (+/−) switches between the two symmetry classes of a given mode.

Animation sweeps through mode pairs, with a cross-fade between consecutive
patterns so the topology change is visible as a smooth morph.

Mode list scrolls through: (1,2), (1,3), (2,3), (1,4), (2,4), (3,4),
(1,5), (2,5), (3,5), (4,5), ...

Controls:
  Space   — pause / resume auto-scroll
  ←/→     — previous / next mode pair
  +/-     — wider / narrower nodal line (σ)
  1       — sand on dark background
  2       — glowing lines on black
  3       — color-mapped phase
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
GRID = 600
MORPH_FRAMES = 90  # frames to cross-fade between modes
SIGMA = 0.12  # nodal band width

paused = False
color_mode = 1
_frame_in_mode = 0

# Precomputed pixel coordinate grids on [0,1]
_gx: np.ndarray
_gy: np.ndarray

# Mode list: pairs (m, n) with m < n
_MODES: list
_mode_idx = 0

# Cached field for current and next mode
_field_cur: np.ndarray
_field_nxt: np.ndarray


def _build_modes(max_n: int = 8) -> list:
    pairs = []
    for n in range(2, max_n + 1):
        for m in range(1, n):
            pairs.append((m, n))
    return pairs


def _chladni_field(m: int, n: int) -> np.ndarray:
    f = np.cos(m * np.pi * _gx) * np.cos(n * np.pi * _gy) - np.cos(n * np.pi * _gx) * np.cos(
        m * np.pi * _gy
    )
    return f


def _render_field(f: np.ndarray, blend: float = 1.0) -> np.ndarray:
    """Convert field to [0,1] sand density."""
    return np.exp(-(f * f) / (SIGMA * SIGMA))


def _colorize(density: np.ndarray, field: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.clip(density, 0, 1)
    if color_mode == 1:
        # Sand (warm tan) on dark slate background
        bg_r, bg_g, bg_b = 18, 22, 30
        sand_r, sand_g, sand_b = 230, 210, 160
        r8 = np.clip(bg_r + t * (sand_r - bg_r), 0, 255).astype(np.uint8)
        g8 = np.clip(bg_g + t * (sand_g - bg_g), 0, 255).astype(np.uint8)
        b8 = np.clip(bg_b + t * (sand_b - bg_b), 0, 255).astype(np.uint8)
    elif color_mode == 2:
        # Glowing cyan lines on black
        r8 = np.clip((t - 0.4) * 1.7 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 1.2 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(t * 255, 0, 255).astype(np.uint8)
    else:
        # Phase-colored: sign of field drives hue
        sign = np.where(field >= 0, 1.0, 0.0)
        hue = sign * 200.0 + (1 - sign) * 20.0  # blue vs orange
        h6 = hue / 60.0
        i6 = h6.astype(np.int32) % 6
        f6 = h6 - i6
        q = 1.0 - f6
        r_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [1, q, 0, 0, f6], 1)
        g_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [f6, 1, 1, q, 0], 0)
        b_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [0, 0, f6, 1, 1], q)
        bri = 0.1 + t * 0.9
        r8 = np.clip(r_f * bri * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(g_f * bri * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(b_f * bri * 255, 0, 255).astype(np.uint8)
    return r8, g8, b8


def setup() -> None:
    global _gx, _gy, _MODES, _field_cur, _field_nxt
    py5.size(WIDTH, HEIGHT)
    ph, pw = py5.pixel_height, py5.pixel_width
    xs = np.linspace(0, 1, pw, dtype=np.float32)
    ys = np.linspace(0, 1, ph, dtype=np.float32)
    _gx = np.tile(xs, (ph, 1))
    _gy = np.tile(ys[:, None], (1, pw))
    _MODES = _build_modes(8)
    _field_cur = _chladni_field(*_MODES[0])
    _field_nxt = _chladni_field(*_MODES[1])
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global _frame_in_mode, _mode_idx, _field_cur, _field_nxt

    if not paused:
        _frame_in_mode += 1
        if _frame_in_mode >= MORPH_FRAMES:
            _frame_in_mode = 0
            _mode_idx = (_mode_idx + 1) % len(_MODES)
            _field_cur = _field_nxt
            _field_nxt = _chladni_field(*_MODES[(_mode_idx + 1) % len(_MODES)])

    # Cross-fade between modes
    alpha = _frame_in_mode / MORPH_FRAMES
    blended = (1 - alpha) * _field_cur + alpha * _field_nxt
    density = _render_field(blended)
    r8, g8, b8 = _colorize(density, blended)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    m, n = _MODES[_mode_idx]
    cmodes = ["", "sand", "glow", "phase"]
    py5.fill(220, 235, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Chladni  mode:({m},{n})  σ={SIGMA:.3f}  "
        f"cmap:{cmodes[color_mode]}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, color_mode, _mode_idx, _frame_in_mode, SIGMA
    global _field_cur, _field_nxt
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "1":
        color_mode = 1
    elif k == "2":
        color_mode = 2
    elif k == "3":
        color_mode = 3
    elif k == "+":
        SIGMA = min(0.40, round(SIGMA + 0.02, 3))
    elif k == "-":
        SIGMA = max(0.02, round(SIGMA - 0.02, 3))
    elif k == "s":
        m, n = _MODES[_mode_idx]
        py5.save_frame(str(SCREENSHOT_DIR / f"chladni_{m}_{n}_####.png"))

    kc = py5.key_code
    if kc == py5.RIGHT:
        _mode_idx = (_mode_idx + 1) % len(_MODES)
        _field_cur = _chladni_field(*_MODES[_mode_idx])
        _field_nxt = _chladni_field(*_MODES[(_mode_idx + 1) % len(_MODES)])
        _frame_in_mode = 0
    elif kc == py5.LEFT:
        _mode_idx = (_mode_idx - 1) % len(_MODES)
        _field_cur = _chladni_field(*_MODES[_mode_idx])
        _field_nxt = _chladni_field(*_MODES[(_mode_idx + 1) % len(_MODES)])
        _frame_in_mode = 0


if __name__ == "__main__":
    py5.run_sketch()
