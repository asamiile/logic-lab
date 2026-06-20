"""
Fault-Line Terrain Generation
Randomly drawn fault lines divide the heightmap: one side raises, the other
lowers. After many faults the surface develops realistic ridges, valleys,
and plateaus. A Gaussian blur optionally smooths the sharp edges.

The result is then rendered with:
  • grayscale shading by height
  • normal-map hillshading (directional light from upper-left)
  • geological colormap (deep blue → green → tan → snow)

Controls:
  r          — new terrain (reset height, re-run faults)
  f          — add one fault pass (N_FAULTS faults)
  b          — toggle blur / sharp edges
  1 / 2 / 3  — colormap (gray / hillshade / geological)
  Space      — toggle auto-fault (add faults every frame)
  s          — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 256

N_FAULTS = 100  # faults per pass
DELTA = 0.012  # height change per fault

CMAPS = ["gray", "hillshade", "geo"]
colormap_idx = 2

_height: np.ndarray  # (GRID, GRID) float in [0, 1]
_passes = 0
blur_on = True
auto_fault = False


def _apply_faults(h: np.ndarray, n: int) -> np.ndarray:
    """Apply n random fault lines to height array."""
    gy, gx = np.mgrid[0:GRID, 0:GRID].astype(np.float32)
    gy = gy / GRID  # [0, 1]
    gx = gx / GRID

    for _ in range(n):
        # Random line through a random point with random angle
        px, py = np.random.rand(), np.random.rand()
        angle = np.random.uniform(0, np.pi)
        nx_n = np.sin(angle)
        ny_n = np.cos(angle)
        # Which side of the line?
        side = (gx - px) * nx_n + (gy - py) * ny_n > 0
        h[side] += DELTA
        h[~side] -= DELTA

    return h


def _smooth(h: np.ndarray, sigma: float = 1.5) -> np.ndarray:
    """Simple Gaussian blur via repeated box filter."""
    k = int(sigma * 3) | 1
    pad = k // 2
    padded = np.pad(h, pad, mode="edge")
    out = padded.copy()
    for _ in range(3):
        out = (
            out[:-2, 1:-1] + out[1:-1, :-2] + out[1:-1, 1:-1] * 4 + out[1:-1, 2:] + out[2:, 1:-1]
        ) / 8.0
        out = np.pad(out, 1, mode="edge")
    return out[pad:-pad, pad:-pad] if pad > 0 else out[:GRID, :GRID]


def _reset() -> None:
    global _height, _passes
    _height = np.zeros((GRID, GRID), dtype=np.float32)
    _passes = 0


def _fault_pass() -> None:
    global _passes
    _apply_faults(_height, N_FAULTS)
    _passes += 1


def _normalize(h: np.ndarray) -> np.ndarray:
    lo, hi = h.min(), h.max()
    return (h - lo) / (hi - lo + 1e-9)


def _hillshade(h_n: np.ndarray) -> np.ndarray:
    """Compute hillshade from normalized height."""
    dz = 4.0  # exaggeration
    dhdx = np.gradient(h_n, axis=1) * GRID
    dhdy = np.gradient(h_n, axis=0) * GRID
    # Light from upper-left, high elevation
    lx, ly, lz = -1.0, -1.0, 2.0
    L = np.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / L, ly / L, lz / L
    # Surface normal
    nx_n = -dhdx * dz
    ny_n = -dhdy * dz
    nz_n = np.ones_like(h_n)
    nm = np.sqrt(nx_n**2 + ny_n**2 + nz_n**2) + 1e-9
    shd = nx_n / nm * lx + ny_n / nm * ly + nz_n / nm * lz
    return np.clip(shd, 0, 1)


def _render() -> None:
    work = _smooth(_height.copy()) if blur_on else _height.copy()
    h_n = _normalize(work)

    ph, pw = py5.pixel_height, py5.pixel_width
    gy_idx = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx_idx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    h_d = h_n[np.ix_(gy_idx, gx_idx)]

    if colormap_idx == 0:
        v = (h_d * 230).astype(np.uint8)
        r8, g8, b8 = v, v, v

    elif colormap_idx == 1:
        shade = _hillshade(h_n)
        s_d = shade[np.ix_(gy_idx, gx_idx)]
        combined = h_d * 0.5 + s_d * 0.5
        v = (combined * 240).astype(np.uint8)
        r8, g8, b8 = v, v, v

    else:  # geological
        shade = _hillshade(h_n)
        s_d = shade[np.ix_(gy_idx, gx_idx)]
        h2 = h_d

        # Level bands: deep water, shallow, lowland, highland, alpine, snow
        r8 = np.select(
            [h2 < 0.3, h2 < 0.45, h2 < 0.6, h2 < 0.75, h2 < 0.88],
            [h2 * 30, h2 * 60, h2 * 140 + 20, h2 * 190 + 20, h2 * 220 + 10],
            default=(h2 * 255).astype(np.float32),
        )
        g8 = np.select(
            [h2 < 0.3, h2 < 0.45, h2 < 0.6, h2 < 0.75, h2 < 0.88],
            [h2 * 80 + 40, h2 * 120 + 40, h2 * 160 + 30, h2 * 140 + 20, h2 * 220 + 10],
            default=(h2 * 255).astype(np.float32),
        )
        b8 = np.select(
            [h2 < 0.3, h2 < 0.45, h2 < 0.6, h2 < 0.75, h2 < 0.88],
            [h2 * 200 + 55, h2 * 80 + 20, h2 * 60 + 10, h2 * 80 + 5, h2 * 220 + 10],
            default=(h2 * 255).astype(np.float32),
        )
        # Apply shading
        r8 = np.clip(r8 * (0.4 + s_d * 0.7), 0, 255).astype(np.uint8)
        g8 = np.clip(g8 * (0.4 + s_d * 0.7), 0, 255).astype(np.uint8)
        b8 = np.clip(b8 * (0.4 + s_d * 0.7), 0, 255).astype(np.uint8)

    r8 = np.asarray(r8, dtype=np.uint8)
    g8 = np.asarray(g8, dtype=np.uint8)
    b8 = np.asarray(b8, dtype=np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if auto_fault:
        _fault_pass()
    _render()

    py5.fill(220, 230, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"passes:{_passes}  cmap:{CMAPS[colormap_idx]}  "
        f"blur:{'on' if blur_on else 'off'}  "
        f"{'AUTO' if auto_fault else 'press f to add faults'}",
        8,
        18,
    )


def key_pressed() -> None:
    global auto_fault, blur_on, colormap_idx
    k = py5.key
    if k == "r":
        _reset()
    elif k == "f":
        _fault_pass()
    elif k == " ":
        auto_fault = not auto_fault
    elif k == "b":
        blur_on = not blur_on
    elif k == "1":
        colormap_idx = 0
    elif k == "2":
        colormap_idx = 1
    elif k == "3":
        colormap_idx = 2
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"fault_terrain_p{_passes}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
