"""
Boids — Emergent Flocking (Craig Reynolds, 1987)
Each agent applies three local rules based on its neighbors within radius R:
  Separation  — steer away from agents that are too close
  Alignment   — match velocity with nearby agents
  Cohesion    — steer toward the center of mass of neighbors

No global coordination: complex flocking emerges from purely local rules.

All distance checks are vectorized: pairwise (N×N) distance matrix computed
with broadcasting. Wraps toroidally (agents reappear on the opposite edge).

Color encodes heading direction (hue) and speed (brightness).

Controls:
  r       — reset with new random positions
  n / N   — fewer / more boids
  s / S   — slower / faster max speed
  Space   — pause / resume
  1       — show trail
  2       — show heading arrows
  3       — show neighbor circles (debug)
  q       — screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
N_BOIDS = 300

R_SEP = 28.0  # separation radius
R_ALIGN = 60.0  # alignment radius
R_COH = 80.0  # cohesion radius

W_SEP = 1.8  # weight: separation
W_ALIGN = 1.0  # weight: alignment
W_COH = 0.8  # weight: cohesion

MAX_SPEED = 4.0
MIN_SPEED = 1.2
MAX_STEER = 0.3  # max turning force per frame

TRAIL_LEN = 18
FADE = 0.82

display_mode = 1  # 1=trail, 2=arrows, 3=debug circles
paused = False

_pos: np.ndarray  # (N, 2)
_vel: np.ndarray  # (N, 2)
_trail: list  # ring buffer of (N, 2) positions


def _reset() -> None:
    global _pos, _vel, _trail
    _pos = np.random.uniform([20, 20], [WIDTH - 20, HEIGHT - 20], (N_BOIDS, 2)).astype(np.float32)
    angles = np.random.uniform(0, 2 * np.pi, N_BOIDS)
    speeds = np.random.uniform(MIN_SPEED, MAX_SPEED, N_BOIDS)
    _vel = np.column_stack([np.cos(angles) * speeds, np.sin(angles) * speeds]).astype(np.float32)
    _trail = [_pos.copy() for _ in range(TRAIL_LEN)]


def _limit(v: np.ndarray, max_mag: float) -> np.ndarray:
    mag = np.linalg.norm(v, axis=1, keepdims=True)
    scale = np.where(mag > max_mag, max_mag / (mag + 1e-9), 1.0)
    return v * scale


def _set_mag(v: np.ndarray, mag: float) -> np.ndarray:
    n = np.linalg.norm(v, axis=1, keepdims=True) + 1e-9
    return v / n * mag


def _step() -> None:
    global _pos, _vel

    # Toroidal difference vectors between all pairs: (N, N, 2)
    dp = _pos[:, np.newaxis, :] - _pos[np.newaxis, :, :]  # (N,N,2)
    # Toroidal wrap
    dp[:, :, 0] = (dp[:, :, 0] + WIDTH / 2) % WIDTH - WIDTH / 2
    dp[:, :, 1] = (dp[:, :, 1] + HEIGHT / 2) % HEIGHT - HEIGHT / 2
    dist = np.linalg.norm(dp, axis=2)  # (N, N)
    np.fill_diagonal(dist, np.inf)

    steer = np.zeros((N_BOIDS, 2), dtype=np.float32)

    # Separation
    mask_sep = dist < R_SEP
    n_sep = mask_sep.sum(axis=1, keepdims=True).clip(1, None)
    # weighted push-away: direction dp[i,j] = pos[i]-pos[j], weight = 1/dist
    weight = np.where(mask_sep, 1.0 / (dist + 1e-6), 0.0)[:, :, np.newaxis]
    sep_force = (dp * weight).sum(axis=1)  # (N, 2)
    sep_force = np.where(n_sep > 1, sep_force, 0.0)
    steer += W_SEP * _limit(sep_force, MAX_STEER)

    # Alignment
    mask_ali = (dist < R_ALIGN) & (dist > 0)
    n_ali = mask_ali.sum(axis=1, keepdims=True).clip(1, None)
    avg_vel = (np.where(mask_ali[:, :, np.newaxis], _vel[np.newaxis, :, :], 0.0)).sum(
        axis=1
    ) / n_ali
    ali_force = avg_vel - _vel
    steer += W_ALIGN * _limit(ali_force, MAX_STEER)

    # Cohesion
    mask_coh = dist < R_COH
    n_coh = mask_coh.sum(axis=1, keepdims=True).clip(1, None)
    center = (np.where(mask_coh[:, :, np.newaxis], _pos[np.newaxis, :, :], 0.0)).sum(axis=1) / n_coh
    desired = center - _pos
    coh_force = _set_mag(desired, MAX_SPEED) - _vel
    coh_force = np.where(n_coh > 1, coh_force, 0.0)
    steer += W_COH * _limit(coh_force, MAX_STEER)

    _vel = _vel + steer
    _vel = _limit(_vel, MAX_SPEED)
    # Enforce minimum speed
    speed = np.linalg.norm(_vel, axis=1, keepdims=True)
    _vel = np.where(speed < MIN_SPEED, _vel / (speed + 1e-9) * MIN_SPEED, _vel)

    _pos = (_pos + _vel) % np.array([WIDTH, HEIGHT], dtype=np.float32)
    _trail.pop(0)
    _trail.append(_pos.copy())


def _heading_color(vx: float, vy: float, brightness: float = 1.0) -> tuple[int, int, int]:
    h = (np.degrees(np.arctan2(vy, vx)) % 360) / 60.0
    i = int(h) % 6
    f = h - int(h)
    q = 1.0 - f
    lut = [(1, f, 0), (q, 1, 0), (0, 1, f), (0, q, 1), (f, 0, 1), (1, 0, q)]
    r, g, b = lut[i]
    sc = brightness * 220
    return int(r * sc), int(g * sc), int(b * sc)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        _step()

    py5.background(10, 12, 22)

    speed_arr = np.linalg.norm(_vel, axis=1)
    speed_n = (speed_arr - MIN_SPEED) / (MAX_SPEED - MIN_SPEED + 1e-6)

    if display_mode == 1:
        # Trail lines
        for t in range(1, TRAIL_LEN):
            age = t / TRAIL_LEN
            for i in range(N_BOIDS):
                r_c, g_c, b_c = _heading_color(_vel[i, 0], _vel[i, 1], age * speed_n[i])
                alpha = int(age * 180)
                py5.stroke(r_c, g_c, b_c, alpha)
                py5.stroke_weight(1.0)
                py5.line(
                    _trail[t - 1][i, 0],
                    _trail[t - 1][i, 1],
                    _trail[t][i, 0],
                    _trail[t][i, 1],
                )
    elif display_mode == 2:
        # Arrow per boid
        py5.stroke_weight(1.5)
        for i in range(N_BOIDS):
            r_c, g_c, b_c = _heading_color(_vel[i, 0], _vel[i, 1], 0.7 + speed_n[i] * 0.3)
            py5.stroke(r_c, g_c, b_c, 200)
            L = 8 + speed_n[i] * 6
            ex = _pos[i, 0] + _vel[i, 0] / (np.linalg.norm(_vel[i]) + 1e-9) * L
            ey = _pos[i, 1] + _vel[i, 1] / (np.linalg.norm(_vel[i]) + 1e-9) * L
            py5.line(_pos[i, 0], _pos[i, 1], ex, ey)
    else:
        # Debug circles + dot
        py5.no_fill()
        for i in range(N_BOIDS):
            r_c, g_c, b_c = _heading_color(_vel[i, 0], _vel[i, 1])
            py5.stroke(r_c, g_c, b_c, 30)
            py5.stroke_weight(0.5)
            py5.circle(_pos[i, 0], _pos[i, 1], R_COH * 2)
            py5.fill(r_c, g_c, b_c, 200)
            py5.no_stroke()
            py5.circle(_pos[i, 0], _pos[i, 1], 5)
            py5.no_fill()

    modes = ["", "trail", "arrows", "debug"]
    py5.fill(190, 210, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Boids  n={N_BOIDS}  maxspd={MAX_SPEED:.1f}  "
        f"mode:{modes[display_mode]}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, display_mode, N_BOIDS, MAX_SPEED
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        display_mode = 1
    elif k == "2":
        display_mode = 2
    elif k == "3":
        display_mode = 3
    elif k == "n":
        N_BOIDS = max(50, N_BOIDS - 50)
        _reset()
    elif k == "N":
        N_BOIDS = min(800, N_BOIDS + 50)
        _reset()
    elif k == "s":
        MAX_SPEED = max(1.5, round(MAX_SPEED - 0.5, 1))
    elif k == "S":
        MAX_SPEED = min(8.0, round(MAX_SPEED + 0.5, 1))
    elif k == "q":
        py5.save_frame(str(SCREENSHOT_DIR / "boids_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
