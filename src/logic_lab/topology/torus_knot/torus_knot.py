"""
Torus Knot
A (p,q)-torus knot winds p times around a torus's central axis and
q times through its hole. (2,3) is the trefoil, (2,5) the cinquefoil,
(3,5) the classic 5-fold torus knot. Rendered with depth-sorted segments
and a traveling-hue colormap for a glowing ribbon illusion.

Controls:
  p / P   — decrease / increase p winding
  q / Q   — decrease / increase q winding
  Space   — pause / resume rotation
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
N_PTS = 600  # curve resolution (segments)
SCALE = 170.0  # world-to-pixel scale

# Torus geometry
R = 2.0  # major radius
r = 0.65  # minor radius

# Winding numbers
p_wind = 2
q_wind = 3

# Animation
rot_y = 0.0
rot_x = 0.30
hue_offset = 0.0
paused = False


# Rotation matrices (3×3 numpy)
def _rx(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def _ry(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def _compute_knot(p: int, q: int) -> np.ndarray:
    """Return (N_PTS, 3) array of torus-knot points."""
    t = np.linspace(0, 2 * np.pi, N_PTS, endpoint=False)
    x = (R + r * np.cos(q * t)) * np.cos(p * t)
    y = (R + r * np.cos(q * t)) * np.sin(p * t)
    z = r * np.sin(q * t)
    return np.column_stack([x, y, z])


knot_pts = _compute_knot(p_wind, q_wind)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.stroke_cap(py5.ROUND)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global rot_y, hue_offset

    py5.background(230, 18, 7)
    py5.no_fill()

    if not paused:
        rot_y += 0.010
        hue_offset = (hue_offset + 0.5) % 360.0

    # Apply rotation
    mat = _rx(rot_x) @ _ry(rot_y)
    rotated = knot_pts @ mat.T  # (N, 3)

    # Orthographic projection + center
    xs = rotated[:, 0] * SCALE + WIDTH * 0.5
    ys = rotated[:, 1] * SCALE + HEIGHT * 0.5
    zs = rotated[:, 2]

    z_min, z_max = zs.min(), zs.max()
    z_range = z_max - z_min + 1e-9

    # Painter's sort: draw back-to-front
    order = np.argsort(zs)
    n = N_PTS

    for k in order:
        j = (k + 1) % n
        depth = (zs[k] - z_min) / z_range  # 0 = far, 1 = near
        hue = (hue_offset + k / n * 300.0) % 360.0
        sat = 60.0 + depth * 25.0
        bri = 45.0 + depth * 50.0
        alpha = 65.0 + depth * 35.0
        sw = 1.5 + depth * 3.0
        py5.stroke_weight(sw)
        py5.stroke(hue, sat, bri, alpha)
        py5.line(xs[k], ys[k], xs[j], ys[j])

    # HUD
    py5.fill(0, 0, 80)
    py5.no_stroke()
    py5.text_size(13)
    py5.text(f"({p_wind},{q_wind})-torus knot  {'PAUSED' if paused else ''}", 10, 22)


def key_pressed() -> None:
    global p_wind, q_wind, knot_pts, paused
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "p":
        p_wind = max(2, p_wind - 1)
        knot_pts = _compute_knot(p_wind, q_wind)
    elif k == "P":
        p_wind = min(9, p_wind + 1)
        knot_pts = _compute_knot(p_wind, q_wind)
    elif k == "q":
        q_wind = max(2, q_wind - 1)
        knot_pts = _compute_knot(p_wind, q_wind)
    elif k == "Q":
        q_wind = min(11, q_wind + 1)
        knot_pts = _compute_knot(p_wind, q_wind)
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"torus_knot_{p_wind}_{q_wind}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
