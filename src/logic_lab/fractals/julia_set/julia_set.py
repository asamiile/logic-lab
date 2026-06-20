"""
Julia Set Explorer
For each pixel z₀ = x + iy, iterate zₙ₊₁ = zₙ² + c until |z| > 2 or MAX_ITER.
The filled Julia set is the set of z₀ that never escape.

c is animated around the boundary of the Mandelbrot set so the fractal
continuously morphs between island-style sets, dendrites, and dust.

Smooth coloring: fractional escape count via log-magnitude interpolation
avoids the banding of integer iteration counts.

Colormaps:
  1  heatmap  — black → deep red → gold → white
  2  spectrum — full rainbow by escape speed
  3  ice      — dark navy → cyan → white

Controls:
  1-3     — colormap
  Space   — pause / resume c animation
  r       — reset view
  +/-     — zoom in / out
  arrows  — pan
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
MAX_ITER = 80
ESCAPE_R = 2.0

_cx = 0.0
_cy = 0.0
_scale = 2.5
colormap_idx = 0
paused = False

_c_angle = 0.0
C_SPEED = 0.008

_px_w = WIDTH
_px_h = HEIGHT


def _c_from_angle(a: float) -> complex:
    """Parametric path along the Mandelbrot cardioid + period-2 bulb."""
    if a < np.pi:
        t = a
        return 0.5 * np.exp(1j * t) - 0.25 * np.exp(2j * t)
    else:
        t = (a - np.pi) * 2
        return -1.0 + 0.25 * np.exp(1j * t)


def _julia(c: complex) -> np.ndarray:
    """Return (H, W) float array of smooth iteration counts [0..MAX_ITER]."""
    xs = np.linspace(_cx - _scale, _cx + _scale, _px_w, dtype=np.float32)
    ys = np.linspace(
        _cy - _scale * _px_h / _px_w,
        _cy + _scale * _px_h / _px_w,
        _px_h,
        dtype=np.float32,
    )
    zr = np.tile(xs, (_px_h, 1))
    zi = np.tile(ys[:, None], (1, _px_w))

    cr, ci = float(c.real), float(c.imag)
    escaped = np.zeros((_px_h, _px_w), dtype=np.float32)
    mask = np.ones((_px_h, _px_w), dtype=bool)

    for n in range(MAX_ITER):
        zr2 = zr * zr - zi * zi + cr
        zi = 2.0 * zr * zi + ci
        zr = zr2

        mag2 = zr * zr + zi * zi
        newly = mask & (mag2 > ESCAPE_R * ESCAPE_R)
        log_zn = np.log(np.maximum(mag2[newly], 1e-9)) * 0.5
        escaped[newly] = n + 1 - np.log(log_zn / np.log(ESCAPE_R)) / np.log(2.0)
        mask[newly] = False
        if not mask.any():
            break

    return escaped


def _colorize(iters: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.clip(iters / MAX_ITER, 0.0, 1.0)
    interior = iters == 0.0

    if colormap_idx == 0:
        r8 = np.clip(t * 3.5 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip((t - 0.33) * 2.0 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip((t - 0.66) * 3.0 * 255, 0, 255).astype(np.uint8)
    elif colormap_idx == 1:
        h = (t * 320.0).astype(np.float32)
        h6 = h / 60.0
        i6 = h6.astype(np.int32) % 6
        f6 = h6 - i6
        q = 1.0 - f6
        r_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [1, q, 0, 0, f6], 1)
        g_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [f6, 1, 1, q, 0], 0)
        b_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [0, 0, f6, 1, 1], q)
        bright = t**0.5
        r8 = np.clip(r_f * bright * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(g_f * bright * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(b_f * bright * 255, 0, 255).astype(np.uint8)
    else:
        r8 = np.clip((t - 0.5) * 2.0 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 1.5 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(t * 255, 0, 255).astype(np.uint8)

    r8[interior] = 0
    g8[interior] = 0
    b8[interior] = 0
    return r8, g8, b8


def setup() -> None:
    global _px_w, _px_h
    py5.size(WIDTH, HEIGHT)
    _px_w = py5.pixel_width
    _px_h = py5.pixel_height
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global _c_angle

    if not paused:
        _c_angle = (_c_angle + C_SPEED) % (2 * np.pi)

    c = _c_from_angle(_c_angle)
    iters = _julia(c)
    r8, g8, b8 = _colorize(iters)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    cmaps = ["heatmap", "spectrum", "ice"]
    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Julia  c={c.real:.4f}+{c.imag:.4f}i  cmap:{cmaps[colormap_idx]}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, colormap_idx, _cx, _cy, _scale, _c_angle
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _cx, _cy, _scale = 0.0, 0.0, 2.5
        _c_angle = 0.0
    elif k == "1":
        colormap_idx = 0
    elif k == "2":
        colormap_idx = 1
    elif k == "3":
        colormap_idx = 2
    elif k == "+":
        _scale *= 0.75
    elif k == "-":
        _scale /= 0.75
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "julia_set_####.png"))

    kc = py5.key_code
    if kc == py5.LEFT:
        _cx -= _scale * 0.2
    elif kc == py5.RIGHT:
        _cx += _scale * 0.2
    elif kc == py5.UP:
        _cy -= _scale * 0.2
    elif kc == py5.DOWN:
        _cy += _scale * 0.2


if __name__ == "__main__":
    py5.run_sketch()
