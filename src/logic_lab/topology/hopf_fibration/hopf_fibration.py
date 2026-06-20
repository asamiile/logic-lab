"""
Hopf Fibration
The Hopf map h: S³ → S² decomposes the 3-sphere into a family of circles
(Hopf fibers). Each point on S² corresponds to exactly one great circle on S³,
and no two fibers intersect — yet together they fill all of S³.

Rendering:
  Each fiber is parametrized by ψ ∈ [0, 2π) and stereographically projected
  from S³ (⊂ ℝ⁴) into ℝ³ (omitting the north pole):
    (a, b, c, d) → (a/(1-d), b/(1-d), c/(1-d))

  Fibers are organized by their base point's latitude θ on S².
  Fibers at the same latitude lie on a common torus; varying θ nests the tori.

  Color encodes the base-point longitude φ (hue) and latitude θ (brightness).
  The 3D view rotates so all nesting levels are visible over time.

Controls:
  Space   — pause / resume rotation
  n / N   — fewer / more fibers (θ and φ resolution)
  r       — reset view
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800

N_THETA = 12  # latitude rings on S²
N_PHI = 16  # fibers per latitude ring
N_PTS = 120  # curve points per fiber

ROT_Y_SPEED = 0.006
ROT_X_SPEED = 0.003

rot_y = 0.0
rot_x = 0.40
paused = False

SCALE = 120.0


def _hopf_fiber(theta: float, phi: float) -> np.ndarray:
    """Return (N_PTS, 3) stereographic-projected fiber for base point (θ,φ)."""
    psi = np.linspace(0, 2 * np.pi, N_PTS, endpoint=False)

    # Hopf parametrization of the fiber
    a = np.cos(theta / 2) * np.cos(psi / 2)
    b = np.cos(theta / 2) * np.sin(psi / 2)
    c = np.sin(theta / 2) * np.cos(phi + psi / 2)
    d = np.sin(theta / 2) * np.sin(phi + psi / 2)

    # Stereographic projection from S³ north pole (0,0,0,1)
    denom = 1.0 - d + 1e-9
    X = a / denom
    Y = b / denom
    Z = c / denom
    return np.column_stack([X, Y, Z])


def _ry(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rx(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _precompute_fibers() -> list:
    """Return list of (pts3d, hue, bri) for all fibers."""
    fibers = []
    thetas = np.linspace(0.15, np.pi - 0.15, N_THETA)
    phis = np.linspace(0, 2 * np.pi, N_PHI, endpoint=False)
    for ti, theta in enumerate(thetas):
        bri = (ti + 1) / N_THETA
        for phi in phis:
            hue = phi / (2 * np.pi) * 360.0
            pts = _hopf_fiber(float(theta), float(phi))
            fibers.append((pts, hue, bri))
    return fibers


_fibers = _precompute_fibers()


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global rot_y, rot_x

    if not paused:
        rot_y += ROT_Y_SPEED
        rot_x += ROT_X_SPEED * 0.5

    R = _rx(rot_x) @ _ry(rot_y)
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5

    py5.background(8, 8, 18)
    py5.stroke_weight(1.1)
    py5.no_fill()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)

    for pts, hue, bri in _fibers:
        rotated = (R @ pts.T).T
        # Clip extremely large projected values (near south pole of S³)
        valid = np.all(np.abs(rotated) < 12, axis=1)

        sx = rotated[:, 0] * SCALE + cx
        sy = -rotated[:, 1] * SCALE + cy
        sz = rotated[:, 2]

        for i in range(N_PTS):
            if not valid[i] or not valid[(i + 1) % N_PTS]:
                continue
            j = (i + 1) % N_PTS
            depth_n = (sz[i] + 6) / 12.0
            alpha = int(60 + depth_n * 100)
            sat = 70 + depth_n * 20
            brightness = bri * 80 + depth_n * 15
            py5.stroke(hue % 360, sat, brightness, alpha)
            py5.line(sx[i], sy[i], sx[j], sy[j])

    py5.color_mode(py5.RGB)
    py5.fill(180, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Hopf fibration  θ-rings:{N_THETA}  φ-fibers/ring:{N_PHI}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, rot_y, rot_x, _fibers, N_THETA, N_PHI
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        rot_y, rot_x = 0.0, 0.40
    elif k == "n":
        N_THETA = max(4, N_THETA - 2)
        N_PHI = max(4, N_PHI - 4)
        _fibers = _precompute_fibers()
    elif k == "N":
        N_THETA = min(24, N_THETA + 2)
        N_PHI = min(32, N_PHI + 4)
        _fibers = _precompute_fibers()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "hopf_fibration_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
