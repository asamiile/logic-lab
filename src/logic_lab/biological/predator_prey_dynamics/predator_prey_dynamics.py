"""
Predator-Prey Dynamics — Lotka-Volterra on a Spatial Grid
Classic population dynamics model on a 2D domain:

  ∂P/∂t = r·P·(1 − P/K) − α·P·Q    (prey: logistic growth − predation)
  ∂Q/∂t = β·α·P·Q − m·Q            (predators: growth from prey − mortality)

Spatial extension adds diffusion (predators and prey can move):
  ∂P/∂t = Dp·∇²P + r·P·(1 − P/K) − α·P·Q
  ∂Q/∂t = Dq·∇²Q + β·α·P·Q − m·Q

The interplay creates classic oscillatory cycles:
  1. Prey abundant → predators increase
  2. Predators eat prey → prey crash
  3. Predators starve → prey recover
  4. Cycle repeats

Spatial diffusion generates spiral waves, traveling bands, and localized
oscillatory pockets. Prey (green) and predators (red) create intricate
predator-prey waves across the domain.

Controls:
  r/R       — lower / higher prey growth rate
  a/A       — lower / higher predation efficiency
  m/M       — lower / higher predator mortality
  1         — show prey (green)
  2         — show predators (red)
  3         — show both (mixed colors)
  Space     — pause / resume
  s         — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 600
GRID = 300

DT = 0.01
STEPS_PER_FRAME = 3

# Model parameters
R = 0.8  # prey growth rate
K = 1.0  # prey carrying capacity
ALPHA = 0.8  # predation efficiency
BETA = 0.5  # predator efficiency (fraction of prey biomass → predator)
M = 0.4  # predator mortality

DP = 0.05  # prey diffusion
DQ = 0.02  # predator diffusion

paused = False
display_mode = 3  # 1=prey, 2=pred, 3=both

_P: np.ndarray  # (GRID, GRID) prey population
_Q: np.ndarray  # (GRID, GRID) predator population


def _laplacian(f: np.ndarray) -> np.ndarray:
    return np.roll(f, 1, 0) + np.roll(f, -1, 0) + np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4 * f


def _step() -> None:
    global _P, _Q
    lap_p = _laplacian(_P)
    lap_q = _laplacian(_Q)
    dp_dt = DP * lap_p + R * _P * (1 - _P / K) - ALPHA * _P * _Q
    dq_dt = DQ * lap_q + BETA * ALPHA * _P * _Q - M * _Q
    _P = np.clip(_P + DT * dp_dt, 0, K)
    _Q = np.clip(_Q + DT * dq_dt, 0, 2)


def _reset() -> None:
    global _P, _Q
    _P = np.random.uniform(0.3, 0.7, (GRID, GRID))
    # Predators localized in center region
    _Q = np.zeros((GRID, GRID))
    cx, cy = GRID // 2, GRID // 2
    r_pred = GRID // 6
    yy, xx = np.ogrid[:GRID, :GRID]
    mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= r_pred**2
    _Q[mask] = np.random.uniform(0.2, 0.5, mask.sum())


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
    p_d = _P[np.ix_(gy, gx)].astype(np.float32) / K
    q_d = _Q[np.ix_(gy, gx)].astype(np.float32)

    if display_mode == 1:
        r8 = np.clip(p_d * 60, 0, 255).astype(np.uint8)
        g8 = np.clip(p_d * 200, 0, 255).astype(np.uint8)
        b8 = np.clip(p_d * 80, 0, 255).astype(np.uint8)
    elif display_mode == 2:
        r8 = np.clip(q_d * 220, 0, 255).astype(np.uint8)
        g8 = np.clip(q_d * 60, 0, 255).astype(np.uint8)
        b8 = np.clip(q_d * 60, 0, 255).astype(np.uint8)
    else:
        r8 = np.clip(p_d * 80 + q_d * 180, 0, 255).astype(np.uint8)
        g8 = np.clip(p_d * 200 + q_d * 40, 0, 255).astype(np.uint8)
        b8 = np.clip(p_d * 60, 0, 255).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    py5.fill(210, 235, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text(
        f"Predator-Prey  r={R:.2f}  α={ALPHA:.2f}  m={M:.2f}  " f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, R, ALPHA, M, display_mode
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "1":
        display_mode = 1
    elif k == "2":
        display_mode = 2
    elif k == "3":
        display_mode = 3
    elif k == "r":
        R = max(0.1, round(R - 0.1, 2))
        _reset()
    elif k == "R":
        R = min(2.0, round(R + 0.1, 2))
        _reset()
    elif k == "a":
        ALPHA = max(0.1, round(ALPHA - 0.1, 2))
        _reset()
    elif k == "A":
        ALPHA = min(2.0, round(ALPHA + 0.1, 2))
        _reset()
    elif k == "m":
        M = max(0.1, round(M - 0.05, 2))
        _reset()
    elif k == "M":
        M = min(1.0, round(M + 0.05, 2))
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "predator_prey_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
