"""
Particle Swarm Optimization — Nature-Inspired Metaheuristic
Each particle represents a candidate solution in a D-dimensional search space.
Particles are guided by:
  1. Their own best-found position (cognitive/personal component)
  2. The swarm's global best position (social/collective component)
  3. Their current velocity (inertia)

Update rule (each dimension independently):
  v ← w·v + c1·r1·(pbest − x) + c2·r2·(gbest − x)
  x ← x + v

where r1, r2 ~ U(0,1) add stochasticity.

Visualizes the swarm optimizing a 2D function landscape in real-time.
The y-axis is fitness (objective value); x-z plane is parameter space.
Particles (colored spheres) converge toward the global minimum.

Three objective functions:
  1. Rosenbrock (bowl-like, slow convergence)
  2. Rastrigin (highly multimodal, challenging)
  3. Sphere (simple paraboloid, fast convergence)

Color: hue by fitness value (blue=good, red=bad); brightness by velocity.

Controls:
  1–3     — objective function
  Space   — pause / resume optimization
  r       — reinitialize swarm
  +/−     — more / fewer particles
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

N = 40  # particles
W = 0.7  # inertia weight
C1, C2 = 1.5, 1.5  # cognitive & social coefficients
DT = 0.1

func_idx = 0
paused = False

_x: np.ndarray  # (N, 2) positions
_v: np.ndarray  # (N, 2) velocities
_pbest: np.ndarray  # (N, 2) personal best positions
_pbest_f: np.ndarray  # (N,) personal best fitness
_gbest: np.ndarray  # (2,) global best position
_gbest_f: float


def _rosenbrock(x: np.ndarray) -> np.ndarray:
    """Rosenbrock function: 100(y-x²)² + (1-x)². Min at (1, 1)."""
    a, b = x[..., 0], x[..., 1]
    return 100 * (b - a * a) ** 2 + (1 - a) ** 2


def _rastrigin(x: np.ndarray) -> np.ndarray:
    """Rastrigin: 20 + Σ(xi² − 10·cos(2πxi)). Min at origin."""
    return 20 + np.sum(x**2 - 10 * np.cos(2 * np.pi * x), axis=-1)


def _sphere(x: np.ndarray) -> np.ndarray:
    """Sphere: Σ xi². Min at origin."""
    return np.sum(x**2, axis=-1)


def _get_objective(x: np.ndarray) -> np.ndarray:
    if func_idx == 0:
        return _rosenbrock(x)
    elif func_idx == 1:
        return _rastrigin(x)
    else:
        return _sphere(x)


def _reset() -> None:
    global _x, _v, _pbest, _pbest_f, _gbest, _gbest_f

    if func_idx == 0:
        _x = np.random.uniform(-2, 2, (N, 2))
    elif func_idx == 1:
        _x = np.random.uniform(-5.12, 5.12, (N, 2))
    else:
        _x = np.random.uniform(-5, 5, (N, 2))

    _v = np.random.uniform(-1, 1, (N, 2))
    _pbest = _x.copy()
    _pbest_f = _get_objective(_x)
    idx_best = np.argmin(_pbest_f)
    _gbest = _pbest[idx_best].copy()
    _gbest_f = float(_pbest_f[idx_best])


def _step() -> None:
    global _x, _v, _pbest, _pbest_f, _gbest, _gbest_f

    r1 = np.random.uniform(0, 1, (N, 2))
    r2 = np.random.uniform(0, 1, (N, 2))
    _v = W * _v + C1 * r1 * (_pbest - _x) + C2 * r2 * (_gbest - _x)
    _x = _x + DT * _v

    # Clip to bounds
    if func_idx == 0:
        _x = np.clip(_x, -2, 2)
    elif func_idx == 1:
        _x = np.clip(_x, -5.12, 5.12)
    else:
        _x = np.clip(_x, -5, 5)

    f_cur = _get_objective(_x)
    improved = f_cur < _pbest_f
    _pbest[improved] = _x[improved]
    _pbest_f[improved] = f_cur[improved]

    idx_best = np.argmin(_pbest_f)
    if _pbest_f[idx_best] < _gbest_f:
        _gbest = _pbest[idx_best].copy()
        _gbest_f = float(_pbest_f[idx_best])


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        _step()

    py5.background(10, 10, 20)

    # Draw 2D landscape in top-left quadrant with fitness as height
    # Particle x[i] maps to screen position
    # Fitness maps to brightness / color

    if func_idx == 0:
        lim = 2.0
        fname = "Rosenbrock"
    elif func_idx == 1:
        lim = 5.12
        fname = "Rastrigin"
    else:
        lim = 5.0
        fname = "Sphere"

    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    scale = min(WIDTH, HEIGHT) * 0.4 / lim

    # Draw particles
    py5.no_stroke()
    f_min = np.percentile(_pbest_f, 10)
    f_max = np.percentile(_pbest_f, 90)
    f_range = max(f_max - f_min, 1e-6)

    for i in range(N):
        x_pos = _x[i, 0]
        y_pos = _x[i, 1]
        f_val = _pbest_f[i]
        v_mag = np.linalg.norm(_v[i])

        # Skip if out of bounds for display
        if abs(x_pos) > lim or abs(y_pos) > lim:
            continue

        # Position on screen
        px = cx + x_pos * scale
        py = cy - y_pos * scale

        # Color by fitness (blue = good, red = bad)
        t = np.clip((f_val - f_min) / f_range, 0, 1)
        hue = (1 - t) * 240 + t * 0  # blue → red
        py5.color_mode(py5.HSB, 360, 100, 100)
        brightness = 50 + min(v_mag * 30, 50)  # faster = brighter
        py5.fill(hue, 70, brightness)
        py5.circle(float(px), float(py), 5.0)

    # Draw reference frame
    py5.color_mode(py5.RGB)
    py5.stroke(60, 80, 100)
    py5.stroke_weight(1)
    # x-axis
    py5.line(cx - lim * scale, cy, cx + lim * scale, cy)
    # y-axis
    py5.line(cx, cy - lim * scale, cx, cy + lim * scale)

    # Best-found marker
    gbest_px = cx + _gbest[0] * scale
    gbest_py = cy - _gbest[1] * scale
    py5.stroke(0, 255, 0)
    py5.stroke_weight(2)
    py5.no_fill()
    py5.circle(float(gbest_px), float(gbest_py), 12.0)

    # Stats
    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text(
        f"PSO  func:{fname}  N:{N}  " f"fbest:{_gbest_f:.3e}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, func_idx, N
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        func_idx = 0
        _reset()
    elif k == "2":
        func_idx = 1
        _reset()
    elif k == "3":
        func_idx = 2
        _reset()
    elif k == "+":
        N = min(200, N + 10)
        _reset()
    elif k == "-":
        N = max(10, N - 10)
        _reset()
    elif k == "s":
        fname = ["rosenbrock", "rastrigin", "sphere"][func_idx]
        py5.save_frame(str(SCREENSHOT_DIR / f"pso_{fname}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
