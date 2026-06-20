"""
Gray-Scott Reaction-Diffusion (Turing Patterns)
Two virtual chemicals A and B interact and diffuse:
  ∂A/∂t = Da·∇²A  −  A·B²  +  f·(1−A)
  ∂B/∂t = Db·∇²B  +  A·B²  −  (f+k)·B

Depending on feed rate f and kill rate k, the system self-organizes into
remarkably different stable patterns — spots, stripes, mazes, and worms —
from a uniform initial state perturbed with a small random seed region.

Presets (f, k):
  1  coral   (0.0545, 0.062)  — branching coral / islands
  2  spots   (0.035,  0.065)  — leopard spots
  3  stripes (0.022,  0.051)  — parallel stripes / fingerprints
  4  maze    (0.029,  0.057)  — labyrinthine maze

Color maps A concentration:
  a  heat  — black→red→yellow→white
  b  algae — dark green→cyan→white
  c  mono  — dark blue→white

Controls:
  1-4     — preset
  a/b/c   — colormap
  r       — reset (new random seed)
  Space   — pause / resume
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 256  # simulation resolution (upscaled to display)
DT = 1.0
STEPS_PER_FRAME = 10

DA = 1.0
DB = 0.5

PRESETS = {
    "coral": (0.0545, 0.062),
    "spots": (0.035, 0.065),
    "stripes": (0.022, 0.051),
    "maze": (0.029, 0.057),
}
PRESET_NAMES = list(PRESETS.keys())
preset_idx = 0
colormap_idx = 0  # 0=heat 1=algae 2=mono
paused = False

_A: np.ndarray
_B: np.ndarray

# Laplacian stencil weights (5-point)
_LAP_CENTER = -1.0
_LAP_EDGE = 0.2
_LAP_CORNER = 0.05


def _laplacian(Z: np.ndarray) -> np.ndarray:
    """Compute discrete Laplacian using roll (periodic BCs)."""
    return (
        _LAP_CENTER * Z
        + _LAP_EDGE * (np.roll(Z, 1, 0) + np.roll(Z, -1, 0) + np.roll(Z, 1, 1) + np.roll(Z, -1, 1))
        + _LAP_CORNER
        * (
            np.roll(np.roll(Z, 1, 0), 1, 1)
            + np.roll(np.roll(Z, 1, 0), -1, 1)
            + np.roll(np.roll(Z, -1, 0), 1, 1)
            + np.roll(np.roll(Z, -1, 0), -1, 1)
        )
    )


def _reset() -> None:
    global _A, _B
    _A = np.ones((GRID, GRID), dtype=np.float32)
    _B = np.zeros((GRID, GRID), dtype=np.float32)
    # Small random seed patch at center
    r = GRID // 10
    cy, cx = GRID // 2, GRID // 2
    _A[cy - r : cy + r, cx - r : cx + r] = 0.50 + np.random.uniform(
        -0.05, 0.05, (2 * r, 2 * r)
    ).astype(np.float32)
    _B[cy - r : cy + r, cx - r : cx + r] = 0.25 + np.random.uniform(
        -0.05, 0.05, (2 * r, 2 * r)
    ).astype(np.float32)


def _step() -> None:
    global _A, _B
    f, k = PRESETS[PRESET_NAMES[preset_idx]]
    f, k = np.float32(f), np.float32(k)

    lapA = _laplacian(_A)
    lapB = _laplacian(_B)
    reaction = _A * _B * _B

    _A += DT * (DA * lapA - reaction + f * (1.0 - _A))
    _B += DT * (DB * lapB + reaction - (f + k) * _B)

    np.clip(_A, 0.0, 1.0, out=_A)
    np.clip(_B, 0.0, 1.0, out=_B)


def _colorize(t: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if colormap_idx == 0:  # heat
        r8 = np.clip(t * 3.0 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip((t - 0.33) * 2.0 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip((t - 0.66) * 3.0 * 255, 0, 255).astype(np.uint8)
    elif colormap_idx == 1:  # algae
        r8 = np.clip((t - 0.6) * 2.5 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 1.2 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip((t - 0.3) * 1.5 * 255, 0, 255).astype(np.uint8)
    else:  # mono (blue-white)
        r8 = np.clip((t - 0.5) * 2.0 * 255, 0, 255).astype(np.uint8)
        g8 = np.clip((t - 0.3) * 1.5 * 255, 0, 255).astype(np.uint8)
        b8 = np.clip(t * 255, 0, 255).astype(np.uint8)
    return r8, g8, b8


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        for _ in range(STEPS_PER_FRAME):
            _step()

    ph, pw = py5.pixel_height, py5.pixel_width
    gy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    a_d = _A[np.ix_(gy, gx)]

    r8, g8, b8 = _colorize(a_d)
    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    cmaps = ["heat", "algae", "mono"]
    py5.fill(220, 235, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Gray-Scott  preset:{PRESET_NAMES[preset_idx]}  cmap:{cmaps[colormap_idx]}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global preset_idx, colormap_idx, paused
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
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
    elif k == "a":
        colormap_idx = 0
    elif k == "b":
        colormap_idx = 1
    elif k == "c":
        colormap_idx = 2
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"rd_{PRESET_NAMES[preset_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
