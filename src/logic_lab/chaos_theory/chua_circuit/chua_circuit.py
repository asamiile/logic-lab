"""
Chua's Circuit — Double-Scroll Attractor
The simplest electronic circuit that exhibits chaotic behavior (Chua 1983).
Equations in normalized form:
  dx/dt = α · (y − x − f(x))
  dy/dt = x − y + z
  dz/dt = −β · y

where f(x) = m₁·x + (m₀−m₁)/2 · (|x+1| − |x−1|)
is a piecewise-linear "Chua's diode" characteristic.

Classical parameters (α=15.6, β=28, m₀=−1/7, m₁=2/7) produce the famous
double-scroll: two interlinked spirals that trajectories switch between
unpredictably — sensitive dependence on initial conditions.

View projections:
  1  x-y   2  y-z   3  x-z   4  3D (isometric)

Controls:
  1–4     — projection plane
  r       — reset trajectories
  Space   — pause / resume
  a / A   — decrease / increase α
  b / B   — decrease / increase β
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

# Chua parameters (classic double-scroll)
ALPHA = 15.6
BETA = 28.0
M0 = -1.0 / 7.0
M1 = 2.0 / 7.0

DT = 0.004
STEPS_PER_FRAME = 8
N_TRAJ = 30
TAIL_LEN = 1800

projection = 0  # 0=xy, 1=yz, 2=xz, 3=3D
alpha_val = ALPHA
beta_val = BETA

_pos: np.ndarray
_tail: np.ndarray
_tail_head: int
paused = False


def _reset() -> None:
    global _pos, _tail, _tail_head
    eps = 0.05
    _pos = np.zeros((N_TRAJ, 3), dtype=np.float64)
    for i in range(N_TRAJ):
        _pos[i] = [
            0.01 + np.random.uniform(-eps, eps),
            0.0 + np.random.uniform(-eps, eps),
            0.0 + np.random.uniform(-eps, eps),
        ]
    _tail = np.zeros((N_TRAJ, TAIL_LEN, 3), dtype=np.float64)
    _tail_head = 0


def _chua_f(x: np.ndarray) -> np.ndarray:
    """Piecewise-linear Chua diode."""
    return M1 * x + 0.5 * (M0 - M1) * (np.abs(x + 1) - np.abs(x - 1))


def _chua_deriv(p: np.ndarray) -> np.ndarray:
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    fx = _chua_f(x)
    dx = alpha_val * (y - x - fx)
    dy = x - y + z
    dz = -beta_val * y
    return np.column_stack([dx, dy, dz])


def _rk4_step() -> None:
    k1 = _chua_deriv(_pos)
    k2 = _chua_deriv(_pos + 0.5 * DT * k1)
    k3 = _chua_deriv(_pos + 0.5 * DT * k2)
    k4 = _chua_deriv(_pos + DT * k3)
    _pos[:] += (DT / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    # Prevent blow-up
    np.clip(_pos, -20, 20, out=_pos)


def _integrate() -> None:
    global _tail_head
    for _ in range(STEPS_PER_FRAME):
        _rk4_step()
        _tail[:, _tail_head, :] = _pos
        _tail_head = (_tail_head + 1) % TAIL_LEN


def _proj2d(pts: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (px, py, depth) for current projection."""
    if projection == 0:
        return pts[:, 0], pts[:, 1], pts[:, 2]
    elif projection == 1:
        return pts[:, 1], pts[:, 2], pts[:, 0]
    elif projection == 2:
        return pts[:, 0], pts[:, 2], pts[:, 1]
    else:
        # Simple isometric 3D: rotate 30° around Y then X
        cx, sx = np.cos(0.5), np.sin(0.5)
        cy, sy = np.cos(0.4), np.sin(0.4)
        x2 = pts[:, 0] * cy + pts[:, 2] * sy
        z2 = -pts[:, 0] * sy + pts[:, 2] * cy
        y3 = pts[:, 1] * cx - z2 * sx
        z3 = pts[:, 1] * sx + z2 * cx
        return x2, y3, z3


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        _integrate()

    py5.background(8, 8, 16)

    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    scale = 38.0

    order = [((_tail_head + i) % TAIL_LEN) for i in range(TAIL_LEN)]
    py5.stroke_weight(0.9)
    py5.no_fill()

    for ti in range(N_TRAJ):
        pts_raw = _tail[ti, order, :]
        px, py_coords, depth = _proj2d(pts_raw)

        d_min, d_max = depth.min(), depth.max()
        d_range = d_max - d_min + 1e-6

        sx = px * scale + cx
        sy = -py_coords * scale + cy

        for i in range(1, TAIL_LEN):
            age = 1.0 - i / TAIL_LEN
            d_n = (depth[i] - d_min) / d_range
            bri = max(0.05, (1.0 - age * 0.87) * (0.3 + d_n * 0.7))

            # Left scroll = warm (red/orange), right scroll = cool (blue/cyan)
            # Color by x position
            t_col = np.clip((pts_raw[i, 0] + 3) / 6, 0, 1)
            r_c = int((0.2 + t_col * 0.8) * bri * 255)
            g_c = int((0.3 * (1 - t_col) + 0.4 * t_col) * bri * 255)
            b_c = int((0.8 - t_col * 0.6) * bri * 255)

            alpha = int((1 - age * 0.9) * 200)
            py5.stroke(r_c, g_c, b_c, alpha)
            py5.line(sx[i - 1], sy[i - 1], sx[i], sy[i])

    proj_names = ["x-y", "y-z", "x-z", "3D"]
    py5.fill(180, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Chua's Circuit  α={alpha_val:.1f}  β={beta_val:.1f}  "
        f"proj:{proj_names[projection]}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, projection, alpha_val, beta_val
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        projection = 0
    elif k == "2":
        projection = 1
    elif k == "3":
        projection = 2
    elif k == "4":
        projection = 3
    elif k == "a":
        alpha_val = max(5.0, round(alpha_val - 0.5, 1))
        _reset()
    elif k == "A":
        alpha_val = min(25.0, round(alpha_val + 0.5, 1))
        _reset()
    elif k == "b":
        beta_val = max(10.0, round(beta_val - 1.0, 1))
        _reset()
    elif k == "B":
        beta_val = min(50.0, round(beta_val + 1.0, 1))
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"chua_proj{projection}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
