"""
Lissajous Figures
Parametric oscilloscope traces: x(t) = A·sin(a·t + δ),  y(t) = B·sin(b·t)
When the frequency ratio a:b is rational, the curve closes into a stable knot;
irrational ratios slowly fill the screen. Phase drift animates the transition.

Display modes:
  • single   — one large Lissajous with animated phase
  • grid     — 5×5 grid sweeping a and b ratios
  • drift    — ratio near-integer so the figure slowly precesses

Color encodes instantaneous speed (slow = dim/blue, fast = bright/white).
Trail fades using alpha accumulation — old points dim toward background.

Controls:
  1 / 2 / 3  — mode (single / grid / drift)
  a / A      — decrease / increase x-frequency ratio
  b / B      — decrease / increase y-frequency ratio
  d / D      — decrease / increase phase drift rate
  r          — reset
  s          — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
N_PTS = 4096  # curve samples per figure
TRAIL_FRAMES = 80  # frames before full fade

MODES = ["single", "grid", "drift"]
mode_idx = 0

# Single / drift mode parameters
freq_a = 3.0
freq_b = 2.0
phase = 0.0
drift_rate = 0.003  # radians per frame added to phase

# Pre-allocated ARGB pixel buffer
_px_to_cx: np.ndarray
_py_to_cy: np.ndarray

# For trail effect: accumulate float RGB then convert (resized in _reset after setup)
_buf_r: np.ndarray = np.zeros((1, 1), dtype=np.float32)
_buf_g: np.ndarray = np.zeros((1, 1), dtype=np.float32)
_buf_b: np.ndarray = np.zeros((1, 1), dtype=np.float32)
FADE = 0.88  # multiplicative fade per frame


def _reset() -> None:
    global phase, _buf_r, _buf_g, _buf_b
    phase = 0.0
    pw, ph = py5.pixel_width, py5.pixel_height
    _buf_r = np.zeros((ph, pw), dtype=np.float32)
    _buf_g = np.zeros((ph, pw), dtype=np.float32)
    _buf_b = np.zeros((ph, pw), dtype=np.float32)


def _lissajous_pts(
    a: float, b: float, delta: float, cx: float, cy: float, scale: float
) -> tuple[np.ndarray, np.ndarray]:
    """Return (xs, ys) pixel coordinates for one Lissajous curve."""
    t = np.linspace(0, 2 * np.pi, N_PTS, endpoint=False)
    x = np.sin(a * t + delta)
    y = np.sin(b * t)
    return cx + x * scale, cy + y * scale


def _speed_color(xs: np.ndarray, ys: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return R, G, B arrays [0,255] colored by normalized speed."""
    dx = np.diff(xs, append=xs[0])
    dy = np.diff(ys, append=ys[0])
    speed = np.sqrt(dx * dx + dy * dy)
    spd_n = speed / (speed.max() + 1e-9)  # 0=slow, 1=fast

    # slow = deep blue, mid = cyan, fast = white
    r = np.clip(spd_n * 2.0 - 0.5, 0, 1)
    g = np.clip(spd_n * 1.6 - 0.1, 0, 1)
    b = np.ones_like(spd_n) * 0.9

    return (r * 255).astype(np.uint8), (g * 255).astype(np.uint8), (b * 255).astype(np.uint8)


def _draw_curve_to_buf(
    xs: np.ndarray, ys: np.ndarray, r8: np.ndarray, g8: np.ndarray, b8: np.ndarray, pw: int, ph: int
) -> None:
    """Splat curve points into the float RGB accumulation buffers."""
    xi = xs.astype(np.int32)
    yi = ys.astype(np.int32)
    valid = (xi >= 0) & (xi < pw) & (yi >= 0) & (yi < ph)
    xi, yi = xi[valid], yi[valid]
    r_v, g_v, b_v = (
        r8[valid].astype(np.float32),
        g8[valid].astype(np.float32),
        b8[valid].astype(np.float32),
    )
    np.maximum.at(_buf_r, (yi, xi), r_v)
    np.maximum.at(_buf_g, (yi, xi), g_v)
    np.maximum.at(_buf_b, (yi, xi), b_v)


def _flush_to_pixels() -> None:
    """Write float accumulation buffers to py5.pixels as ARGB."""
    r_u = _buf_r.clip(0, 255).astype(np.uint8)
    g_u = _buf_g.clip(0, 255).astype(np.uint8)
    b_u = _buf_b.clip(0, 255).astype(np.uint8)
    argb = (
        np.int32(-16777216)
        | (r_u.astype(np.int32) << 16)
        | (g_u.astype(np.int32) << 8)
        | b_u.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()


def _render_single(pw: int, ph: int) -> None:
    global _buf_r, _buf_g, _buf_b
    _buf_r *= FADE
    _buf_g *= FADE
    _buf_b *= FADE

    cx, cy = pw * 0.5, ph * 0.5
    scale = min(pw, ph) * 0.44
    xs, ys = _lissajous_pts(freq_a, freq_b, phase, cx, cy, scale)
    r8, g8, b8 = _speed_color(xs, ys)
    _draw_curve_to_buf(xs, ys, r8, g8, b8, pw, ph)
    _flush_to_pixels()


def _render_grid(pw: int, ph: int) -> None:
    """Static 5×5 grid: rows=b ratio, cols=a ratio."""
    _buf_r[:] = 0
    _buf_g[:] = 0
    _buf_b[:] = 0

    ratios = [1, 2, 3, 4, 5]
    n = len(ratios)
    cell_w = pw / n
    cell_h = ph / n
    margin = 0.40

    for ri, b_val in enumerate(ratios):
        for ci, a_val in enumerate(ratios):
            cx = (ci + 0.5) * cell_w
            cy = (ri + 0.5) * cell_h
            scale = min(cell_w, cell_h) * margin
            xs, ys = _lissajous_pts(float(a_val), float(b_val), np.pi / 4, cx, cy, scale)
            r8, g8, b8 = _speed_color(xs, ys)
            _draw_curve_to_buf(xs, ys, r8, g8, b8, pw, ph)

    _flush_to_pixels()


def _render_drift(pw: int, ph: int) -> None:
    """Near-integer ratio slowly precessing figure."""
    global _buf_r, _buf_g, _buf_b
    _buf_r *= FADE
    _buf_g *= FADE
    _buf_b *= FADE

    cx, cy = pw * 0.5, ph * 0.5
    scale = min(pw, ph) * 0.44
    # Irrational offset makes the figure never quite close
    a = freq_a + 0.007
    xs, ys = _lissajous_pts(a, freq_b, phase, cx, cy, scale)
    r8, g8, b8 = _speed_color(xs, ys)
    _draw_curve_to_buf(xs, ys, r8, g8, b8, pw, ph)
    _flush_to_pixels()


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global phase
    pw, ph = py5.pixel_width, py5.pixel_height
    mode = MODES[mode_idx]
    phase += drift_rate

    if mode == "single":
        _render_single(pw, ph)
    elif mode == "grid":
        _render_grid(pw, ph)
    else:
        _render_drift(pw, ph)

    # HUD
    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"mode:{mode}  a:{freq_a:.2f}  b:{freq_b:.2f}  drift:{drift_rate:.4f}",
        8,
        18,
    )


def key_pressed() -> None:
    global mode_idx, freq_a, freq_b, drift_rate
    k = py5.key
    if k == "1":
        mode_idx = 0
        _reset()
    elif k == "2":
        mode_idx = 1
        _reset()
    elif k == "3":
        mode_idx = 2
        _reset()
    elif k == "r":
        _reset()
    elif k == "a":
        freq_a = max(1.0, freq_a - 1.0)
        _reset()
    elif k == "A":
        freq_a = min(10.0, freq_a + 1.0)
        _reset()
    elif k == "b":
        freq_b = max(1.0, freq_b - 1.0)
        _reset()
    elif k == "B":
        freq_b = min(10.0, freq_b + 1.0)
        _reset()
    elif k == "d":
        drift_rate = max(0.0005, drift_rate * 0.75)
    elif k == "D":
        drift_rate = min(0.05, drift_rate * 1.33)
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"lissajous_{MODES[mode_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
