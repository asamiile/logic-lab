"""
Double Pendulum — Sensitivity to Initial Conditions
Two pendulums hinged in series. The system is governed by four coupled ODEs
(θ₁, θ₂, ω₁, ω₂) with trigonometric coupling terms.

N_TRAJ trajectories start with slightly different θ₁ offsets (spacing DELTA).
They begin moving nearly identically, then diverge exponentially — the hallmark
of deterministic chaos. Color encodes initial condition offset.

Physics:
  m₁ = m₂ = 1,  L₁ = L₂ = 1,  g = 9.81
  Equations from Lagrangian mechanics (see e.g. Eric Neumann's derivation).

Modes:
  1  trails only     — fading path behind each pendulum tip
  2  pendulum + trail — draw current arm positions + trail
  3  Poincaré-style  — dots at each frame (no line, high density)

Controls:
  1–3     — display mode
  r       — reset (same initial angle)
  Space   — pause / resume
  a / A   — start angle −/+ 10°
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

G = 9.81
L1, L2 = 1.0, 1.0
M1, M2 = 1.0, 1.0

DT = 0.012
STEPS_PER_FRAME = 6
N_TRAJ = 20
DELTA = 1e-4  # initial angle spread between trajectories
TAIL_LEN = 600

SCALE = 160.0  # pixels per unit length
ORIGIN_X = WIDTH // 2
ORIGIN_Y = HEIGHT // 3

mode = 1
paused = False
start_angle = np.pi * 0.72

# State: (N_TRAJ, 4)  columns: θ1 θ2 ω1 ω2
_state: np.ndarray
_tail1: np.ndarray  # (N_TRAJ, TAIL_LEN, 2) tip1 xy in pixel space
_tail2: np.ndarray  # (N_TRAJ, TAIL_LEN, 2) tip2 xy
_tail_head = 0


def _hue_to_rgb(h: float) -> tuple[int, int, int]:
    h6 = (h % 360) / 60.0
    i = int(h6) % 6
    f = h6 - int(h6)
    q = 1.0 - f
    lut = [(1, f, 0), (q, 1, 0), (0, 1, f), (0, q, 1), (f, 0, 1), (1, 0, q)]
    r, g, b = lut[i]
    return int(r * 220), int(g * 220), int(b * 220)


def _derivs(s: np.ndarray) -> np.ndarray:
    """Vectorized RK4 step for N_TRAJ trajectories. s shape (N,4)."""
    t1, t2, w1, w2 = s[:, 0], s[:, 1], s[:, 2], s[:, 3]
    dt12 = t1 - t2
    cos12 = np.cos(dt12)
    sin12 = np.sin(dt12)
    denom = M1 + M2 - M2 * cos12 * cos12 + 1e-9

    alpha1 = (
        -G * (2 * M1 + M2) * np.sin(t1)
        - M2 * G * np.sin(t1 - 2 * t2)
        - 2 * sin12 * M2 * (w2 * w2 * L2 + w1 * w1 * L1 * cos12)
    ) / (L1 * denom)

    alpha2 = (
        2
        * sin12
        * (w1 * w1 * L1 * (M1 + M2) + G * (M1 + M2) * np.cos(t1) + w2 * w2 * L2 * M2 * cos12)
    ) / (L2 * denom)

    return np.column_stack([w1, w2, alpha1, alpha2])


def _rk4(s: np.ndarray) -> np.ndarray:
    k1 = _derivs(s)
    k2 = _derivs(s + 0.5 * DT * k1)
    k3 = _derivs(s + 0.5 * DT * k2)
    k4 = _derivs(s + DT * k3)
    return s + (DT / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def _to_screen(t1: np.ndarray, t2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return pixel coords of tip1 and tip2 for N trajectories."""
    x1 = ORIGIN_X + L1 * SCALE * np.sin(t1)
    y1 = ORIGIN_Y + L1 * SCALE * np.cos(t1)
    x2 = x1 + L2 * SCALE * np.sin(t2)
    y2 = y1 + L2 * SCALE * np.cos(t2)
    return np.column_stack([x1, y1]), np.column_stack([x2, y2])


def _reset() -> None:
    global _state, _tail1, _tail2, _tail_head
    _state = np.zeros((N_TRAJ, 4), dtype=np.float64)
    for i in range(N_TRAJ):
        _state[i, 0] = start_angle + i * DELTA
        _state[i, 1] = start_angle
    tip1, tip2 = _to_screen(_state[:, 0], _state[:, 1])
    _tail1 = np.tile(tip1[:, np.newaxis, :], (1, TAIL_LEN, 1))
    _tail2 = np.tile(tip2[:, np.newaxis, :], (1, TAIL_LEN, 1))
    _tail_head = 0


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global _state, _tail_head

    if not paused:
        for _ in range(STEPS_PER_FRAME):
            _state = _rk4(_state)
        tip1, tip2 = _to_screen(_state[:, 0], _state[:, 1])
        _tail1[:, _tail_head, :] = tip1
        _tail2[:, _tail_head, :] = tip2
        _tail_head = (_tail_head + 1) % TAIL_LEN

    py5.background(10, 10, 18)

    # Build ordered index into ring buffer (oldest → newest)
    order = [(_tail_head + i) % TAIL_LEN for i in range(TAIL_LEN)]
    py5.stroke_weight(1.0)

    for ti in range(N_TRAJ):
        hue = ti / N_TRAJ * 300.0
        r_c, g_c, b_c = _hue_to_rgb(hue)

        if mode == 3:
            # Poincaré: draw dots at tip2
            for idx in order[::4]:
                age = order.index(idx) / TAIL_LEN
                alpha = int(40 + age * 160)
                py5.stroke(r_c, g_c, b_c, alpha)
                py5.point(_tail2[ti, idx, 0], _tail2[ti, idx, 1])
        else:
            # Trail at tip2
            for seg in range(1, TAIL_LEN):
                i0, i1 = order[seg - 1], order[seg]
                age = seg / TAIL_LEN
                alpha = int(age * 200)
                py5.stroke(r_c, g_c, b_c, alpha)
                py5.line(
                    _tail2[ti, i0, 0],
                    _tail2[ti, i0, 1],
                    _tail2[ti, i1, 0],
                    _tail2[ti, i1, 1],
                )

        if mode == 2:
            # Draw current arm
            cur = _tail_head - 1 if _tail_head > 0 else TAIL_LEN - 1
            t1x, t1y = _tail1[ti, cur]
            t2x, t2y = _tail2[ti, cur]
            py5.stroke(r_c, g_c, b_c, 200)
            py5.stroke_weight(1.5)
            py5.line(ORIGIN_X, ORIGIN_Y, t1x, t1y)
            py5.line(t1x, t1y, t2x, t2y)
            py5.stroke_weight(1.0)

    mode_names = ["", "trails", "arms+trails", "dots"]
    py5.fill(190, 210, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Double pendulum  n={N_TRAJ}  Δθ={DELTA:.0e}  "
        f"mode:{mode_names[mode]}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, mode, start_angle
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        mode = 1
    elif k == "2":
        mode = 2
    elif k == "3":
        mode = 3
    elif k == "a":
        start_angle = (start_angle - np.radians(10)) % (2 * np.pi)
        _reset()
    elif k == "A":
        start_angle = (start_angle + np.radians(10)) % (2 * np.pi)
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"double_pendulum_m{mode}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
