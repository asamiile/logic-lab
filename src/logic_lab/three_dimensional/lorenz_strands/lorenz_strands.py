"""
Lorenz Strands — Multiple Coupled Attractors in 3D
Multiple Lorenz systems (dx/dt=σ(y−x), dy/dt=x(ρ−z)−y, dz/dt=xy−βz)
are rendered simultaneously with different initial conditions, creating
an ensemble of orbits that collectively form the iconic "butterfly" shape.

Each trajectory is drawn as a continuous strand (tube-like trail).
Strands are colored by velocity or height, creating depth cues.
Back-to-front sorting (painter's algorithm) ensures correct 3D perception.

Three rendering modes:
  1. Velocity-colored strands (blue=slow, red=fast)
  2. Height-colored strands (blue=low, red=high)
  3. Time-faded strands (new=bright, old=dim)

Interactive 3D rotation via mouse/keyboard, allowing exploration of the
strange attractor geometry from all angles.

Controls:
  ←/→/↑/↓  — rotate around x and y axes
  +/−      — more / fewer trajectories
  1–3      — rendering mode
  Space    — pause / resume
  r        — reset view
  s        — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 1000, 900

# Lorenz parameters
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0

TRAIL_LEN = 400
DT = 0.002
STEPS_PER_FRAME = 5

N_STRANDS = 5
rot_x = 0.3
rot_y = 0.0
ROT_X_SPEED = 0.005
ROT_Y_SPEED = 0.007

paused = False
render_mode = 1  # 1=velocity, 2=height, 3=time-faded

_trails: list  # [(x,y,z), ...] per strand


def _init_trails() -> None:
    global _trails
    _trails = []
    for _ in range(N_STRANDS):
        # Initial conditions spread around a region
        x0 = np.random.uniform(-10, 10)
        y0 = np.random.uniform(-10, 10)
        z0 = np.random.uniform(0, 30)
        _trails.append([[x0, y0, z0]])


def _lorenz_step(x: float, y: float, z: float) -> tuple[float, float, float]:
    dx = SIGMA * (y - x)
    dy = x * (RHO - z) - y
    dz = x * y - BETA * z
    return x + DT * dx, y + DT * dy, z + DT * dz


def _step() -> None:
    for trail in _trails:
        x, y, z = trail[-1]
        x, y, z = _lorenz_step(x, y, z)
        trail.append([x, y, z])
        if len(trail) > TRAIL_LEN:
            trail.pop(0)


def _rx_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _ry_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    h6 = (h % 360) / 60.0
    i = int(h6) % 6
    f = h6 - int(h6)
    p, q2, t2 = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    lut = [(v, t2, p), (q2, v, p), (p, v, t2), (p, q2, v), (t2, p, v), (v, p, q2)]
    r, g, b = lut[i]
    return int(r * 255), int(g * 255), int(b * 255)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _init_trails()


def draw() -> None:
    global rot_x, rot_y

    if not paused:
        for _ in range(STEPS_PER_FRAME):
            _step()
        rot_x += ROT_X_SPEED
        rot_y += ROT_Y_SPEED

    py5.background(8, 10, 20)

    R_mat = _rx_mat(rot_x) @ _ry_mat(rot_y)
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    scale = 15.0

    # Collect all segments with depth
    segments = []
    for strand_idx, trail in enumerate(_trails):
        for i in range(1, len(trail)):
            p0 = np.array(trail[i - 1], dtype=np.float32)
            p1 = np.array(trail[i], dtype=np.float32)
            rp0 = R_mat @ p0
            rp1 = R_mat @ p1
            z_mid = (rp0[2] + rp1[2]) * 0.5
            vel = np.linalg.norm(p1 - p0)
            age = i / len(trail)
            segments.append((z_mid, strand_idx, i, p0, p1, rp0, rp1, vel, age))

    # Sort back-to-front
    segments.sort(key=lambda s: s[0])

    py5.stroke_weight(1.5)
    py5.no_fill()
    for z_mid, strand_idx, seg_idx, p0, p1, rp0, rp1, vel, age in segments:
        sx0 = rp0[0] * scale + cx
        sy0 = -rp0[1] * scale + cy
        sx1 = rp1[0] * scale + cx
        sy1 = -rp1[1] * scale + cy

        if render_mode == 1:
            # Velocity-colored
            hue = np.clip(vel * 100, 0, 300)
            rc, gc, bc = _hsv_to_rgb(hue, 0.8, 0.9)
        elif render_mode == 2:
            # Height-colored
            hue = np.clip((rp0[2] + 30) / 60 * 240, 0, 240)
            rc, gc, bc = _hsv_to_rgb(hue, 0.7, 0.9)
        else:
            # Time-faded
            alpha_t = int(age * 200)
            hue = (strand_idx / N_STRANDS) * 300
            rc, gc, bc = _hsv_to_rgb(hue, 0.7, age * 0.8 + 0.2)

        py5.stroke(rc, gc, bc, min(200, int(age * 250)))
        py5.line(float(sx0), float(sy0), float(sx1), float(sy1))

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    modes = ["velocity", "height", "time-fade"]
    py5.text(
        f"Lorenz strands  σ={SIGMA:.1f}  ρ={RHO:.1f}  "
        f"N={N_STRANDS}  mode:{modes[render_mode - 1]}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def mouse_moved() -> None:
    global rot_x, rot_y
    # Tie rotation to mouse position for interactive viewing
    rot_y = (py5.mouse_x / WIDTH) * 2 * np.pi
    rot_x = (py5.mouse_y / HEIGHT) * np.pi


def key_pressed() -> None:
    global paused, N_STRANDS, render_mode, rot_x, rot_y
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        rot_x, rot_y = 0.3, 0.0
    elif k == "1":
        render_mode = 1
    elif k == "2":
        render_mode = 2
    elif k == "3":
        render_mode = 3
    elif k == "+":
        N_STRANDS = min(20, N_STRANDS + 1)
        _init_trails()
    elif k == "-":
        N_STRANDS = max(1, N_STRANDS - 1)
        _init_trails()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "lorenz_strands_####.png"))

    kc = py5.key_code
    if kc == py5.LEFT:
        rot_y -= 0.1
    elif kc == py5.RIGHT:
        rot_y += 0.1
    elif kc == py5.UP:
        rot_x -= 0.1
    elif kc == py5.DOWN:
        rot_x += 0.1


if __name__ == "__main__":
    py5.run_sketch()
