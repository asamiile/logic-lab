"""
Rössler Attractor
Continuous 3D chaotic system (Rössler 1976):
  dx/dt = -y - z
  dy/dt = x + a·y
  dz/dt = b + z·(x - c)

Unlike Lorenz's twin-scroll butterfly, the Rössler system has a single-scroll
topology: trajectories spiral outward in the x-y plane, then shoot up in z
and return to the inner spiral. The fractal cross-section resembles a folded
band — the "screw attractor."

Classical parameters: a=0.1, b=0.1, c=14.0.
Varying c produces period-doubling: c≈4 (period-1) → c≈6 (period-2) → chaos.

Controls:
  Space   — pause / resume
  r       — reset trajectories
  a / A   — decrease / increase parameter a
  c / C   — decrease / increase parameter c (main route to chaos)
  1 / 2   — colormap (spectrum / heat)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

# Rössler parameters
a_param = 0.10
b_param = 0.10
c_param = 14.0

DT = 0.012
STEPS_PER_FRAME = 5
N_TRAJ = 20
TAIL_LEN = 1400

ROT_Z_SPEED = 0.005
ROT_X_SPEED = 0.0012

_pos: np.ndarray
_tail: np.ndarray
_tail_head: int
rot_z = 0.0
rot_x = 0.25
paused = False
colormap_idx = 0


def _reset() -> None:
    global _pos, _tail, _tail_head, rot_z
    eps = 0.05
    _pos = np.zeros((N_TRAJ, 3), dtype=np.float64)
    for i in range(N_TRAJ):
        _pos[i] = [
            -5.0 + np.random.uniform(-eps, eps),
            0.0 + np.random.uniform(-eps, eps),
            0.02 + np.random.uniform(-eps, eps),
        ]
    _tail = np.zeros((N_TRAJ, TAIL_LEN, 3), dtype=np.float64)
    _tail_head = 0
    rot_z = 0.0


def _rossler_deriv(p: np.ndarray) -> np.ndarray:
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    dx = -y - z
    dy = x + a_param * y
    dz = b_param + z * (x - c_param)
    return np.column_stack([dx, dy, dz])


def _rk4_step() -> None:
    k1 = _rossler_deriv(_pos)
    k2 = _rossler_deriv(_pos + 0.5 * DT * k1)
    k3 = _rossler_deriv(_pos + 0.5 * DT * k2)
    k4 = _rossler_deriv(_pos + DT * k3)
    _pos[:] += (DT / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def _integrate() -> None:
    global _tail_head
    for _ in range(STEPS_PER_FRAME):
        _rk4_step()
        _tail[:, _tail_head, :] = _pos
        _tail_head = (_tail_head + 1) % TAIL_LEN


def _rz_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _rx_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _project(pts: np.ndarray) -> np.ndarray:
    Rz = _rz_mat(rot_z)
    Rx = _rx_mat(rot_x)
    return (Rx @ Rz @ pts.T).T


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global rot_z, rot_x

    if not paused:
        _integrate()
        rot_z += ROT_Z_SPEED
        rot_x += ROT_X_SPEED * 0.4

    py5.background(8, 8, 16)

    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    scale = 15.0

    order = [((_tail_head + i) % TAIL_LEN) for i in range(TAIL_LEN)]
    py5.stroke_weight(0.9)
    py5.no_fill()

    for ti in range(N_TRAJ):
        pts_raw = _tail[ti, order, :]
        pts = _project(pts_raw)

        z_vals = pts[:, 2]
        z_min, z_max = z_vals.min(), z_vals.max()
        z_range = z_max - z_min + 1e-6

        sx = pts[:, 0] * scale + cx
        sy = -pts[:, 1] * scale + cy

        for i in range(1, TAIL_LEN):
            age = 1.0 - i / TAIL_LEN
            depth_n = (z_vals[i] - z_min) / z_range
            bri = max(0.05, (1.0 - age * 0.88) * (0.35 + depth_n * 0.65))

            if colormap_idx == 0:
                # Spectrum: hue by trajectory index, brightness by age+depth
                hue = (ti / N_TRAJ) * 360.0
                h = hue / 60.0
                i6 = int(h) % 6
                f = h - int(h)
                p, q, t = 0.0, 1.0 - f, f
                rgb_map = [(1, t, p), (q, 1, p), (p, 1, t), (p, q, 1), (t, p, 1), (1, p, q)]
                rv, gv, bv = rgb_map[i6]
                r_c = int(rv * bri * 255)
                g_c = int(gv * bri * 255)
                b_c = int(bv * bri * 255)
            else:
                r_c = int(min(1.0, bri * 2.2) * 255)
                g_c = int(max(0.0, bri * 2.0 - 0.8) * 255)
                b_c = int(max(0.0, 1.0 - bri * 3.0) * 255)

            alpha = int((1.0 - age * 0.92) * 190)
            py5.stroke(r_c, g_c, b_c, alpha)
            py5.line(sx[i - 1], sy[i - 1], sx[i], sy[i])

    py5.fill(180, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    cmap = "spectrum" if colormap_idx == 0 else "heat"
    py5.text(
        f"Rössler  a={a_param:.2f}  b={b_param:.2f}  c={c_param:.1f}  "
        f"cmap:{cmap}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, colormap_idx, a_param, c_param
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "a":
        a_param = max(0.01, round(a_param - 0.02, 2))
        _reset()
    elif k == "A":
        a_param = min(0.5, round(a_param + 0.02, 2))
        _reset()
    elif k == "c":
        c_param = max(2.0, round(c_param - 0.5, 1))
        _reset()
    elif k == "C":
        c_param = min(20.0, round(c_param + 0.5, 1))
        _reset()
    elif k == "1":
        colormap_idx = 0
    elif k == "2":
        colormap_idx = 1
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"rossler_c{c_param:.1f}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
