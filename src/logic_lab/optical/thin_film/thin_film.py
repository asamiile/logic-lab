"""
Thin Film Interference
When light reflects off both surfaces of a thin transparent film (soap bubble,
oil slick, anti-reflection coating), the two reflected beams interfere.
The optical path difference is 2·n·d·cos(θ), where d is the film thickness
and n is the refractive index. For each visible wavelength λ, the reflected
intensity varies as I ∝ cos²(π·OPD/λ).

Integrating over the visible spectrum (380–700 nm) and converting to CIE XYZ
then sRGB gives the characteristic rainbow banding seen in soap films.

Display modes:
  • flat    — uniform thickness gradient (horizontal bands)
  • bubble  — spherical soap bubble profile (d varies radially)
  • ripple  — animated wave disturbance on the bubble thickness

Controls:
  1 / 2 / 3  — mode (flat / bubble / ripple)
  n / N      — decrease / increase refractive index
  t          — toggle thickness scale
  s          — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800

MODES = ["flat", "bubble", "ripple"]
mode_idx = 0

N_IOR = 1.33  # refractive index of water (soap film)
D_MIN = 0.0  # minimum film thickness (nm)
D_MAX = 1200.0  # maximum film thickness (nm) -- covers several orders
thick_scale = 1.0  # multiplier on D_MAX

# Precomputed CIE color matching functions (sampled every 5 nm, 380-700 nm)
# Source: CIE 1931 2-degree observer approximation
_WL = np.arange(380, 705, 5, dtype=np.float64)


# Gaussian approximation to CIE CMFs
def _cie_gauss(wl: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Approximate CIE 1931 color matching functions."""
    # X has two lobes
    x = (
        1.056 * np.exp(-0.5 * ((wl - 599.8) / 37.9) ** 2)
        + 0.362 * np.exp(-0.5 * ((wl - 442.0) / 16.0) ** 2)
        - 0.065 * np.exp(-0.5 * ((wl - 501.1) / 20.4) ** 2)
    )
    y = 0.821 * np.exp(-0.5 * ((wl - 568.8) / 46.9) ** 2) + 0.286 * np.exp(
        -0.5 * ((wl - 530.9) / 16.3) ** 2
    )
    z = 1.217 * np.exp(-0.5 * ((wl - 437.0) / 11.8) ** 2) + 0.681 * np.exp(
        -0.5 * ((wl - 459.0) / 26.0) ** 2
    )
    return np.clip(x, 0, None), np.clip(y, 0, None), np.clip(z, 0, None)


_CMF_X, _CMF_Y, _CMF_Z = _cie_gauss(_WL)

# XYZ → linear sRGB matrix (D65 white point)
_XYZ_TO_RGB = np.array(
    [
        [3.2406, -1.5372, -0.4986],
        [-0.9689, 1.8758, 0.0415],
        [0.0557, -0.2040, 1.0570],
    ],
    dtype=np.float64,
)


def _spectrum_to_rgb(intensity: np.ndarray) -> np.ndarray:
    """
    intensity: (N_WL,) array of spectral reflectance.
    Returns (3,) sRGB values in [0, 1].
    """
    X = np.sum(intensity * _CMF_X)
    Y = np.sum(intensity * _CMF_Y)
    Z = np.sum(intensity * _CMF_Z)
    xyz = np.array([X, Y, Z])
    # Normalize by white
    white_X = _CMF_X.sum()
    white_Y = _CMF_Y.sum()
    white_Z = _CMF_Z.sum()
    xyz /= np.array([white_X, white_Y, white_Z]) + 1e-9
    rgb = _XYZ_TO_RGB @ xyz
    # Gamma correction (sRGB)
    rgb = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)
    return np.clip(rgb, 0, 1)


def _film_reflectance(d: np.ndarray) -> np.ndarray:
    """
    d: (H, W) thickness in nm.
    Returns (H, W, 3) sRGB image.
    """
    H, W = d.shape
    img = np.zeros((H, W, 3), dtype=np.float32)

    for ki, wl in enumerate(_WL):
        opd = 2.0 * N_IOR * d  # (H, W) optical path difference in nm
        # Phase difference (+ π for reflection off denser medium for first surface)
        phase = np.pi + 2.0 * np.pi * opd / wl
        intensity = np.cos(phase * 0.5) ** 2  # (H, W)

        img[:, :, 0] += intensity * _CMF_X[ki]
        img[:, :, 1] += intensity * _CMF_Y[ki]
        img[:, :, 2] += intensity * _CMF_Z[ki]

    # Normalize by white (sum of CMFs)
    img[:, :, 0] /= _CMF_X.sum()
    img[:, :, 1] /= _CMF_Y.sum()
    img[:, :, 2] /= _CMF_Z.sum()

    # XYZ → sRGB per pixel (batch)
    xyz = img.reshape(-1, 3)
    rgb = xyz @ _XYZ_TO_RGB.T
    rgb = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)
    rgb = np.clip(rgb, 0, 1)
    return rgb.reshape(H, W, 3)


# Precomputed pixel arrays
_pw: int = 0
_ph: int = 0
_frame = 0
_cache: np.ndarray | None = None
_dirty = True


def _thickness_flat(pw: int, ph: int) -> np.ndarray:
    """Linear gradient top → bottom."""
    y = np.linspace(0, 1, ph)[:, np.newaxis] * np.ones((1, pw))
    return (D_MIN + y * D_MAX * thick_scale).astype(np.float64)


def _thickness_bubble(pw: int, ph: int) -> np.ndarray:
    """Spherical bubble profile: thin at top (gravity drains), thick at equator."""
    fy = np.linspace(-1, 1, ph)[:, np.newaxis]
    fx = np.linspace(-1, 1, pw)[np.newaxis, :]
    r = np.sqrt(fx**2 + fy**2)
    # Thin on top half, thicker at equator
    d = D_MAX * thick_scale * (1.0 - np.abs(fy) * 0.5) * np.exp(-r * 0.3)
    return np.clip(d, 0, D_MAX).astype(np.float64)


def _thickness_ripple(pw: int, ph: int, frame: int) -> np.ndarray:
    """Bubble with animated standing wave disturbance."""
    fy = np.linspace(-1, 1, ph)[:, np.newaxis]
    fx = np.linspace(-1, 1, pw)[np.newaxis, :]
    r = np.sqrt(fx**2 + fy**2)
    ripple = 80.0 * np.cos(r * 12 - frame * 0.15) * np.exp(-r * 2)
    base = _thickness_bubble(pw, ph)
    return np.clip(base + ripple, 0, D_MAX)


def _render() -> None:
    global _cache, _dirty, _pw, _ph
    pw, ph = py5.pixel_width, py5.pixel_height
    _pw, _ph = pw, ph

    if mode_idx == 0:
        d = _thickness_flat(pw, ph)
    elif mode_idx == 1:
        d = _thickness_bubble(pw, ph)
    else:
        d = _thickness_ripple(pw, ph, _frame)

    rgb = _film_reflectance(d)

    r8 = (rgb[:, :, 0] * 255).astype(np.uint8)
    g8 = (rgb[:, :, 1] * 255).astype(np.uint8)
    b8 = (rgb[:, :, 2] * 255).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    _cache = argb
    _dirty = False


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.frame_rate(10)


def draw() -> None:
    global _frame, _dirty
    _frame += 1

    if mode_idx == 2:
        _dirty = True  # ripple animates every frame

    if _dirty:
        _render()

    if _cache is not None:
        py5.load_pixels()
        py5.pixels[:] = _cache.flatten()
        py5.update_pixels()

    py5.fill(240, 240, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"mode:{MODES[mode_idx]}  n={N_IOR:.2f}  d_max:{int(D_MAX * thick_scale)}nm",
        8,
        18,
    )


def key_pressed() -> None:
    global mode_idx, N_IOR, thick_scale, _dirty
    k = py5.key
    if k == "1":
        mode_idx = 0
        _dirty = True
    elif k == "2":
        mode_idx = 1
        _dirty = True
    elif k == "3":
        mode_idx = 2
    elif k == "n":
        N_IOR = max(1.0, round(N_IOR - 0.05, 2))
        _dirty = True
    elif k == "N":
        N_IOR = min(2.5, round(N_IOR + 0.05, 2))
        _dirty = True
    elif k == "t":
        thick_scale = 0.5 if thick_scale == 1.0 else (2.0 if thick_scale == 0.5 else 1.0)
        _dirty = True
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"thin_film_{MODES[mode_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
