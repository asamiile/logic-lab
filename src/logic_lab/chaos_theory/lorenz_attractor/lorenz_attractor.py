"""
Lorenz Attractor
Continuous 3D chaotic system (Lorenz 1963):
  dx/dt = σ(y − x)
  dy/dt = x(ρ − z) − y
  dz/dt = xy − βz
Classical parameters (σ=10, ρ=28, β=8/3) produce the iconic "butterfly"
strange attractor with fractal dimension ≈ 2.06.

Multiple trajectories start in a tiny ball near the equilibrium; they diverge
exponentially (Lyapunov exponent ≈ 0.9), illustrating sensitive dependence.
Depth is encoded by brightness; the 3D object rotates continuously.

Controls:
  Space   — pause / resume
  r       — reset trajectories
  1 / 2   — colormap (multi-hue / heat)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

# Lorenz parameters
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0

DT = 0.008  # RK4 step size
STEPS_PER_FRAME = 6  # integration steps per draw call
N_TRAJ = 24  # simultaneous trajectories
TAIL_LEN = 1200  # history points kept per trajectory

# Rotation
ROT_Y_SPEED = 0.004
ROT_X_SPEED = 0.0015

# State
_pos: np.ndarray  # (N_TRAJ, 3) current positions
_tail: np.ndarray  # (N_TRAJ, TAIL_LEN, 3) history ring buffer
_tail_head: int  # ring-buffer write index
rot_y = 0.0
rot_x = 0.25
paused = False
colormap_idx = 0


def _reset() -> None:
    global _pos, _tail, _tail_head
    eps = 0.02
    _pos = np.array(
        [
            [
                0.01 + np.random.uniform(-eps, eps),
                0.0 + np.random.uniform(-eps, eps),
                25.0 + np.random.uniform(-eps, eps),
            ]
            for _ in range(N_TRAJ)
        ],
        dtype=np.float64,
    )
    _tail = np.zeros((N_TRAJ, TAIL_LEN, 3), dtype=np.float64)
    _tail_head = 0


def _lorenz_deriv(p: np.ndarray) -> np.ndarray:
    """Lorenz vector field for (N_TRAJ, 3) array."""
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    dx = SIGMA * (y - x)
    dy = x * (RHO - z) - y
    dz = x * y - BETA * z
    return np.column_stack([dx, dy, dz])


def _rk4_step() -> None:
    k1 = _lorenz_deriv(_pos)
    k2 = _lorenz_deriv(_pos + 0.5 * DT * k1)
    k3 = _lorenz_deriv(_pos + 0.5 * DT * k2)
    k4 = _lorenz_deriv(_pos + DT * k3)
    _pos[:] += (DT / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def _integrate() -> None:
    global _tail_head
    for _ in range(STEPS_PER_FRAME):
        _rk4_step()
        _tail[:, _tail_head, :] = _pos
        _tail_head = (_tail_head + 1) % TAIL_LEN


def _project(pts: np.ndarray) -> np.ndarray:
    """Rotate then orthographic-project (N, 3) → (N, 3) where z is depth."""
    cy, sy = np.cos(rot_y), np.sin(rot_y)
    cx, sx = np.cos(rot_x), np.sin(rot_x)

    # Y-axis rotation
    x2 = pts[:, 0] * cy + pts[:, 2] * sy
    z2 = -pts[:, 0] * sy + pts[:, 2] * cy
    y2 = pts[:, 1]

    # X-axis rotation
    y3 = y2 * cx - z2 * sx
    z3 = y2 * sx + z2 * cx

    return np.column_stack([x2, y3, z3])


def _traj_color(traj_idx: int, age_frac: float, depth_n: float) -> tuple[int, int, int]:
    """Return (r,g,b) for trajectory index, age fraction [0=new,1=old], depth [0=near,1=far]."""
    bri = (1.0 - age_frac * 0.85) * (0.4 + depth_n * 0.6)

    if colormap_idx == 0:
        # Multi-hue: each trajectory gets a distinct hue
        hue = (traj_idx / N_TRAJ) * 360.0
        # Simplified HSV→RGB
        h = hue / 60.0
        i = int(h) % 6
        f = h - int(h)
        p, q, t = 0.0, 1.0 - f, f
        rgb_map = [(1, t, p), (q, 1, p), (p, 1, t), (p, q, 1), (t, p, 1), (1, p, q)]
        rv, gv, bv = rgb_map[i]
        return (int(rv * bri * 255), int(gv * bri * 255), int(bv * bri * 255))
    else:
        # Heat: blue → red → white
        r = min(1.0, bri * 2.0)
        g = max(0.0, bri * 2.0 - 1.0)
        b = max(0.0, 1.0 - bri * 2.5)
        return (int(r * 255), int(g * 255), int(b * 255))


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global rot_y, rot_x

    if not paused:
        _integrate()
        rot_y += ROT_Y_SPEED
        rot_x += ROT_X_SPEED * 0.3

    py5.background(8, 8, 16)

    cx, cy_screen = WIDTH * 0.5, HEIGHT * 0.5
    scale = 9.0

    # Rebuild ordered tail indices (oldest first)
    order = [((_tail_head + i) % TAIL_LEN) for i in range(TAIL_LEN)]

    py5.stroke_weight(1.0)
    py5.no_fill()

    for ti in range(N_TRAJ):
        pts_raw = _tail[ti, order, :]
        pts_proj = _project(pts_raw)

        # Depth normalization (z-axis after rotation)
        z_vals = pts_proj[:, 2]
        z_min, z_max = z_vals.min(), z_vals.max()
        z_range = z_max - z_min + 1e-6

        sx = pts_proj[:, 0] * scale + cx
        sy = -pts_proj[:, 1] * scale + cy_screen  # flip y

        for i in range(1, TAIL_LEN):
            age_frac = 1.0 - i / TAIL_LEN
            depth_n = (z_vals[i] - z_min) / z_range
            r, g, b = _traj_color(ti, age_frac, depth_n)
            alpha = int((1.0 - age_frac * 0.9) * 180)
            py5.stroke(r, g, b, alpha)
            py5.line(sx[i - 1], sy[i - 1], sx[i], sy[i])

    # HUD
    py5.fill(180, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    cmap = "multi" if colormap_idx == 0 else "heat"
    py5.text(
        f"Lorenz  σ={SIGMA}  ρ={RHO}  β={BETA:.3f}  "
        f"traj:{N_TRAJ}  cmap:{cmap}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, colormap_idx
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        colormap_idx = 0
    elif k == "2":
        colormap_idx = 1
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "lorenz_attractor_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
