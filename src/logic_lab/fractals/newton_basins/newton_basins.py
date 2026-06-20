"""
Newton Basins (Newton Fractal)
Applying Newton's root-finding method to f(z) = zⁿ − 1 on the complex plane:
  z_{k+1} = z_k − f(z_k) / f'(z_k)

Each pixel's starting complex value z₀ converges to one of the n roots.
Color encodes WHICH root it converges to (hue); brightness encodes HOW FAST
(fewer iterations → brighter). The fractal boundaries are the Julia sets of
the Newton map — intricate filaments where convergence is ambiguous.

Polynomials:
  1  zⁿ − 1           (roots on unit circle)
  2  z³ − 2z + 2      (roots off the real axis)
  3  z⁴ − 1           (4 roots, 4-fold symmetry)
  4  z⁵ − 1           (5 roots, petals)
  5  z⁶ − z³ − 1      (asymmetric; 6 irregular roots)

Controls:
  1–5     — switch polynomial
  r       — re-render (same polynomial, resets pan/zoom)
  scroll  — zoom (if py5 supports; fallback: +/- keys)
  + / -   — zoom in / out
  arrow keys — pan
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
MAX_ITER = 40
TOL = 1e-6

POLY_NAMES = ["z^n-1 (n=3)", "z^3-2z+2", "z^4-1", "z^5-1", "z^6-z^3-1"]
poly_idx = 0

# View parameters
_cx = 0.0  # center real
_cy = 0.0  # center imag
_zoom = 1.0  # scale (higher = more zoomed in)

_px_to_cx: np.ndarray
_py_to_cy: np.ndarray

_pixels_cache: np.ndarray | None = None
_dirty = True


def _poly_and_deriv(z: np.ndarray, idx: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (f(z), f'(z)) for selected polynomial."""
    if idx == 0:  # z³ - 1
        return z**3 - 1, 3 * z**2
    elif idx == 1:  # z³ - 2z + 2
        return z**3 - 2 * z + 2, 3 * z**2 - 2
    elif idx == 2:  # z⁴ - 1
        return z**4 - 1, 4 * z**3
    elif idx == 3:  # z⁵ - 1
        return z**5 - 1, 5 * z**4
    else:  # z⁶ - z³ - 1
        return z**6 - z**3 - 1, 6 * z**5 - 3 * z**2


def _roots(idx: int) -> np.ndarray:
    """Analytic roots for each polynomial."""
    if idx == 0:
        n = 3
        return np.exp(2j * np.pi * np.arange(n) / n)
    elif idx == 1:
        return np.roots([1, 0, -2, 2])
    elif idx == 2:
        n = 4
        return np.exp(2j * np.pi * np.arange(n) / n)
    elif idx == 3:
        n = 5
        return np.exp(2j * np.pi * np.arange(n) / n)
    else:
        return np.roots([1, 0, 0, -1, 0, 0, -1])


def _hue_to_rgb(h: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized HSV-like hue [0,1] → RGB uint8 at S=V=1."""
    h6 = h * 6.0
    i = h6.astype(np.int32) % 6
    f = h6 - np.floor(h6)
    p = np.zeros_like(h)
    q = 1.0 - f
    t = f
    r = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [np.ones_like(h), q, p, p, t, np.ones_like(h)],
    )
    g = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [t, np.ones_like(h), np.ones_like(h), q, p, p],
    )
    b = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [p, p, t, np.ones_like(h), np.ones_like(h), q],
    )
    return r, g, b


def _render() -> None:
    global _pixels_cache, _dirty
    pw, ph = py5.pixel_width, py5.pixel_height
    half_w = pw / (2 * _zoom * pw / WIDTH)
    half_h = ph / (2 * _zoom * ph / HEIGHT)

    re = np.linspace(_cx - half_w / 100, _cx + half_w / 100, pw)
    im = np.linspace(_cy - half_h / 100, _cy + half_h / 100, ph)
    Z = (re[np.newaxis, :] + 1j * im[:, np.newaxis]).astype(np.complex128)

    roots = _roots(poly_idx)
    n_roots = len(roots)
    iters = np.full(Z.shape, MAX_ITER, dtype=np.float32)
    root_map = np.full(Z.shape, -1, dtype=np.int32)

    converged = np.zeros(Z.shape, dtype=bool)
    z = Z.copy()

    for i in range(MAX_ITER):
        active = ~converged
        if not active.any():
            break
        f, fp = _poly_and_deriv(z[active], poly_idx)
        # Avoid division by zero
        safe = np.abs(fp) > 1e-12
        dz = np.where(safe, f / np.where(safe, fp, 1.0), 0.0)
        z[active] -= dz

        # Check convergence to each root
        for ri, root in enumerate(roots):
            close = active & (np.abs(z - root) < TOL) & (root_map == -1)
            root_map[close] = ri
            iters[close] = i
            converged[close] = True

        converged |= np.abs(z) > 1e6

    # Colorize
    hue = np.where(root_map >= 0, root_map / max(n_roots, 1), 0.0).astype(np.float32)
    bright = np.where(root_map >= 0, (1.0 - iters / MAX_ITER) ** 0.5, 0.0).astype(np.float32)

    rh, gh, bh = _hue_to_rgb(hue)
    r8 = (rh * bright * 255).clip(0, 255).astype(np.uint8)
    g8 = (gh * bright * 255).clip(0, 255).astype(np.uint8)
    b8 = (bh * bright * 255).clip(0, 255).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    _pixels_cache = argb
    _dirty = False


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.frame_rate(10)


def draw() -> None:
    global _dirty
    if _dirty:
        _render()

    if _pixels_cache is not None:
        py5.load_pixels()
        py5.pixels[:] = _pixels_cache.flatten()
        py5.update_pixels()

    # HUD
    py5.fill(240, 240, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"poly:{POLY_NAMES[poly_idx]}  zoom:{_zoom:.2f}  " f"center:({_cx:.3f},{_cy:.3f})",
        8,
        18,
    )


def key_pressed() -> None:
    global poly_idx, _zoom, _cx, _cy, _dirty
    k = py5.key
    step = 0.15 / _zoom
    if k in "12345":
        poly_idx = int(k) - 1
        _cx, _cy, _zoom = 0.0, 0.0, 1.0
        _dirty = True
    elif k == "r":
        _cx, _cy, _zoom = 0.0, 0.0, 1.0
        _dirty = True
    elif k == "+":
        _zoom *= 1.4
        _dirty = True
    elif k == "-":
        _zoom = max(0.1, _zoom / 1.4)
        _dirty = True
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"newton_{poly_idx + 1}_####.png"))

    coded = py5.key_code
    if coded == py5.UP:
        _cy -= step
        _dirty = True
    elif coded == py5.DOWN:
        _cy += step
        _dirty = True
    elif coded == py5.LEFT:
        _cx -= step
        _dirty = True
    elif coded == py5.RIGHT:
        _cx += step
        _dirty = True


if __name__ == "__main__":
    py5.run_sketch()
