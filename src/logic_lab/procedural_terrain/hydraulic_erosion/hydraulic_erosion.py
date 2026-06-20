"""
Hydraulic Erosion
Particle-based hydraulic erosion sculpts a Diamond-Square heightmap.
Virtual water droplets flow downhill, picking up and depositing sediment
according to their speed and carrying capacity. Repeated passes expose
ridgelines, valleys, and river channels like geological timescales in seconds.

Rendering: height as luminance; erosion deposit as warm tint; water as blue.

Controls:
  r       — regenerate terrain and re-erode
  e       — run one erosion pass (5 000 droplets)
  1 / 2   — colormap: grayscale / tinted geological
  Space   — toggle auto-erode
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 256  # heightmap resolution (power of 2 for Diamond-Square)

# Hydraulic erosion parameters
N_DROPS = 5_000  # droplets per pass
MAX_STEPS = 64  # max steps per droplet
INERTIA = 0.05  # how much droplet keeps previous direction
CAPACITY = 4.0  # sediment capacity per unit speed
DEPOSITION = 0.1  # fraction of excess sediment deposited per step
EROSION = 0.3  # fraction of deficit capacity eroded per step
EVAPORATION = 0.02  # water lost per step
MIN_SLOPE = 0.001  # minimum slope to erode

# State
_height: np.ndarray  # (GRID, GRID) height values [0, 1]
_deposit: np.ndarray  # (GRID, GRID) accumulated sediment trace
_passes = 0
auto_erode = False
colormap_idx = 0


def _diamond_square(n: int, roughness: float = 0.55) -> np.ndarray:
    """Generate (n+1)×(n+1) fractal heightmap via Diamond-Square algorithm."""
    size = n + 1
    h = np.zeros((size, size), dtype=np.float32)
    h[0, 0] = h[0, -1] = h[-1, 0] = h[-1, -1] = np.random.rand() * 0.5 + 0.25

    step = n
    scale = roughness
    while step > 1:
        half = step // 2

        # Diamond step
        for r in range(0, n, step):
            for c in range(0, n, step):
                avg = (h[r, c] + h[r + step, c] + h[r, c + step] + h[r + step, c + step]) / 4
                h[r + half, c + half] = avg + (np.random.rand() * 2 - 1) * scale

        # Square step
        for r in range(0, n + 1, half):
            for c in range((r + half) % step, n + 1, step):
                neighbors = []
                if r - half >= 0:
                    neighbors.append(h[r - half, c])
                if r + half <= n:
                    neighbors.append(h[r + half, c])
                if c - half >= 0:
                    neighbors.append(h[r, c - half])
                if c + half <= n:
                    neighbors.append(h[r, c + half])
                h[r, c] = np.mean(neighbors) + (np.random.rand() * 2 - 1) * scale

        step = half
        scale *= roughness

    h = (h - h.min()) / (h.max() - h.min() + 1e-9)
    return h[:n, :n]  # return GRID×GRID


def _gradient(h: np.ndarray, r: float, c: float) -> tuple[float, float]:
    """Bilinear interpolated gradient at (r, c)."""
    ri, ci = int(r), int(c)
    ri = np.clip(ri, 0, GRID - 2)
    ci = np.clip(ci, 0, GRID - 2)
    fr, fc = r - ri, c - ci

    h00 = float(h[ri, ci])
    h10 = float(h[ri + 1, ci])
    h01 = float(h[ri, ci + 1])
    h11 = float(h[ri + 1, ci + 1])

    gr = (h10 - h00) * (1 - fc) + (h11 - h01) * fc
    gc = (h01 - h00) * (1 - fr) + (h11 - h10) * fr
    return gr, gc


def _bilinear(h: np.ndarray, r: float, c: float) -> float:
    ri, ci = int(r), int(c)
    ri = np.clip(ri, 0, GRID - 2)
    ci = np.clip(ci, 0, GRID - 2)
    fr, fc = r - ri, c - ci
    return float(
        h[ri, ci] * (1 - fr) * (1 - fc)
        + h[ri + 1, ci] * fr * (1 - fc)
        + h[ri, ci + 1] * (1 - fr) * fc
        + h[ri + 1, ci + 1] * fr * fc
    )


def _erode_pass() -> None:
    global _passes
    h = _height

    for _ in range(N_DROPS):
        # Spawn droplet at random position
        pos_r = np.random.uniform(1, GRID - 2)
        pos_c = np.random.uniform(1, GRID - 2)
        vel_r, vel_c = 0.0, 0.0
        water = 1.0
        sediment = 0.0

        for _ in range(MAX_STEPS):
            if water < 0.01:
                break

            ri, ci = int(pos_r), int(pos_c)
            if not (0 < ri < GRID - 1 and 0 < ci < GRID - 1):
                break

            gr, gc = _gradient(h, pos_r, pos_c)

            # Update direction (downhill + inertia)
            vel_r = vel_r * INERTIA - gr * (1 - INERTIA)
            vel_c = vel_c * INERTIA - gc * (1 - INERTIA)
            speed = np.sqrt(vel_r * vel_r + vel_c * vel_c) + 1e-9
            vel_r /= speed
            vel_c /= speed

            new_r = pos_r + vel_r
            new_c = pos_c + vel_c
            if not (0 < new_r < GRID - 1 and 0 < new_c < GRID - 1):
                break

            # Height difference
            old_h = _bilinear(h, pos_r, pos_c)
            new_h = _bilinear(h, new_r, new_c)
            dh = new_h - old_h

            # Carrying capacity
            capacity = max(-dh, MIN_SLOPE) * speed * water * CAPACITY

            if sediment > capacity:
                # Over capacity: deposit excess
                deposit = (sediment - capacity) * DEPOSITION
                sediment -= deposit
                ri_c, ci_c = int(pos_r), int(pos_c)
                ri_c = np.clip(ri_c, 0, GRID - 1)
                ci_c = np.clip(ci_c, 0, GRID - 1)
                h[ri_c, ci_c] += deposit
                _deposit[ri_c, ci_c] += deposit * 3
            else:
                # Under capacity: erode
                erode = min((capacity - sediment) * EROSION, -dh + 0.01)
                erode = max(erode, 0.0)
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        er, ec = ri + dr, ci + dc
                        if 0 <= er < GRID and 0 <= ec < GRID:
                            w = max(0.0, 1.0 - abs(dr) - abs(dc) * 0.5)
                            h[er, ec] -= erode * w * 0.25
                            _deposit[er, ec] -= erode * w * 0.05
                sediment += erode

            pos_r, pos_c = new_r, new_c
            water *= 1 - EVAPORATION

        # Deposit remaining sediment
        ri, ci = int(pos_r), int(pos_c)
        if 0 <= ri < GRID and 0 <= ci < GRID:
            h[ri, ci] += sediment
            _deposit[ri, ci] += sediment * 2

    # Normalize height
    _height[:] = np.clip(h, 0, 1)
    _deposit[:] = np.clip(_deposit, 0, 1)
    _passes += 1


def _reset() -> None:
    global _height, _deposit, _passes
    _height = _diamond_square(GRID)
    _deposit = np.zeros((GRID, GRID), dtype=np.float32)
    _passes = 0


def _render() -> None:
    h_norm = _height
    dep = np.clip(_deposit, 0, 1)

    if colormap_idx == 0:
        # Grayscale with blue water in valleys
        val = h_norm
        r8 = (val * 220).clip(0, 255).astype(np.uint8)
        g8 = (val * 220).clip(0, 255).astype(np.uint8)
        b8 = np.clip(val * 200 + dep * 30, 0, 255).astype(np.uint8)
    else:
        # Geological tint: deep blue → green → tan → white
        r8 = np.clip(h_norm * 220 + dep * 60, 0, 255).astype(np.uint8)
        g8 = np.clip(h_norm * 180 + dep * 40 + (1 - h_norm) * 30, 0, 255).astype(np.uint8)
        b8 = np.clip((1 - h_norm) * 120 + h_norm * 80 + dep * 20, 0, 255).astype(np.uint8)

    # Map to display pixels
    ph, pw = py5.pixel_height, py5.pixel_width
    gy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    r_d = r8[np.ix_(gy, gx)]
    g_d = g8[np.ix_(gy, gx)]
    b_d = b8[np.ix_(gy, gx)]

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
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if auto_erode:
        _erode_pass()
    _render()

    py5.fill(220, 230, 255)
    py5.no_stroke()
    py5.text_size(12)
    cmap = "gray" if colormap_idx == 0 else "geo"
    py5.text(
        f"passes:{_passes}  cmap:{cmap}  {'AUTO' if auto_erode else 'manual (e=erode)'}",
        8,
        18,
    )


def key_pressed() -> None:
    global auto_erode, colormap_idx
    k = py5.key
    if k == "r":
        _reset()
    elif k == "e":
        _erode_pass()
    elif k == " ":
        auto_erode = not auto_erode
    elif k == "1":
        colormap_idx = 0
    elif k == "2":
        colormap_idx = 1
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"erosion_pass{_passes}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
