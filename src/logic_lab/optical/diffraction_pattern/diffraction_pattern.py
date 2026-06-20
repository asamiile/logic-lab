"""
Diffraction Pattern
Wave optics simulation of Fraunhofer diffraction through apertures.
The intensity at each screen point is computed from the Fourier transform
of the aperture function: I(x,y) = |FFT(aperture)|².

Aperture modes:
  • single slit    — 1D slit; fringes perpendicular to slit axis
  • double slit    — two slits; Young's experiment interference
  • circular       — Airy disk; defines optical resolution limits
  • grating        — N-slit diffraction grating; sharp principal maxima
  • random holes   — random aperture; speckle pattern

Colormap: dark→indigo→cyan→white (wavelength-inspired cool palette).

Controls:
  1–5     — switch aperture mode
  w / W   — narrow / widen aperture feature (slit width / radius)
  n / N   — fewer / more slits (grating mode)
  r       — randomize holes (random mode)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 512  # aperture / FFT resolution

MODES = ["single_slit", "double_slit", "circular", "grating", "random_holes"]
mode_idx = 0

# Aperture parameters
slit_width = 0.04  # fraction of GRID
slit_sep = 0.12  # double-slit separation (fraction)
circ_radius = 0.08  # circular aperture radius (fraction)
n_slits = 6  # grating lines

# Display index arrays (HiDPI)
_px_to_cx: np.ndarray
_py_to_cy: np.ndarray


def _make_aperture() -> np.ndarray:
    """Return (GRID, GRID) aperture mask [0, 1]."""
    mode = MODES[mode_idx]
    x = np.linspace(-0.5, 0.5, GRID)
    y = np.linspace(-0.5, 0.5, GRID)
    xx, yy = np.meshgrid(x, y)
    half_w = slit_width * 0.5

    if mode == "single_slit":
        return (np.abs(xx) < half_w).astype(np.float32)

    elif mode == "double_slit":
        left = np.abs(xx - slit_sep * 0.5) < half_w
        right = np.abs(xx + slit_sep * 0.5) < half_w
        return (left | right).astype(np.float32)

    elif mode == "circular":
        return (np.sqrt(xx**2 + yy**2) < circ_radius).astype(np.float32)

    elif mode == "grating":
        # N periodic slits
        period = 1.0 / n_slits
        rel = ((xx + 0.5) % period) / period
        return (rel < slit_width * n_slits).astype(np.float32)

    else:  # random_holes
        rng = np.random.default_rng()
        holes = rng.random((GRID, GRID)) < 0.04
        return holes.astype(np.float32)


def _compute_pattern(aperture: np.ndarray) -> np.ndarray:
    """Fraunhofer diffraction intensity via 2D FFT."""
    fft = np.fft.fftshift(np.fft.fft2(aperture))
    intensity = np.abs(fft) ** 2
    # Log scale for visibility
    log_i = np.log1p(intensity)
    norm = log_i / (log_i.max() + 1e-12)
    return norm.astype(np.float32)


def _render(pattern: np.ndarray) -> None:
    """Cool-wavelength colormap: black → indigo → cyan → white."""
    v = pattern
    r8 = np.clip(v * 1.6 - 0.4, 0, 1)
    g8 = np.clip(v * 2.0 - 0.6, 0, 1)
    b8 = np.clip(v * 1.2, 0, 1)

    r_u = (r8 * 255).astype(np.uint8)
    g_u = (g8 * 255).astype(np.uint8)
    b_u = (b8 * 255).astype(np.uint8)

    r_d = r_u[np.ix_(_py_to_cy, _px_to_cx)]
    g_d = g_u[np.ix_(_py_to_cy, _px_to_cx)]
    b_d = b_u[np.ix_(_py_to_cy, _px_to_cx)]

    argb = (
        np.int32(-16777216)
        | (r_d.astype(np.int32) << 16)
        | (g_d.astype(np.int32) << 8)
        | b_d.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()


# Cache current pattern
_pattern: np.ndarray
_dirty = True


def _refresh() -> None:
    global _pattern, _dirty
    aperture = _make_aperture()
    _pattern = _compute_pattern(aperture)
    _dirty = False


def setup() -> None:
    global _px_to_cx, _py_to_cy
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    pw, ph = py5.pixel_width, py5.pixel_height
    _px_to_cx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    _py_to_cy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    _refresh()


def draw() -> None:
    if _dirty:
        _refresh()
    _render(_pattern)

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(12)
    mode = MODES[mode_idx]
    extra = f"  n_slits:{n_slits}" if mode == "grating" else f"  w:{slit_width:.3f}"
    py5.text(f"mode:{mode}{extra}", 8, 18)


def key_pressed() -> None:
    global mode_idx, slit_width, circ_radius, n_slits, _dirty
    k = py5.key
    if k == "1":
        mode_idx = 0
        _dirty = True
    elif k == "2":
        mode_idx = 1
        _dirty = True
    elif k == "3":
        mode_idx = 2
        _dirty = True
    elif k == "4":
        mode_idx = 3
        _dirty = True
    elif k == "5":
        mode_idx = 4
        _dirty = True
    elif k == "w":
        slit_width = max(0.005, slit_width * 0.85)
        circ_radius = slit_width * 2
        _dirty = True
    elif k == "W":
        slit_width = min(0.3, slit_width * 1.15)
        circ_radius = slit_width * 2
        _dirty = True
    elif k == "n":
        n_slits = max(2, n_slits - 1)
        _dirty = True
    elif k == "N":
        n_slits = min(20, n_slits + 1)
        _dirty = True
    elif k == "r":
        _dirty = True  # randomize uses rng inside _make_aperture
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"diffraction_{MODES[mode_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
