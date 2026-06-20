"""
Kohonen Self-Organizing Map (SOM)
An unsupervised neural network that learns a 2D topology-preserving map
of its input space. Each neuron holds a weight vector; winning neurons
(closest to input) and their neighbors update toward the input.
Over time, the map unfolds to reflect the structure of the data manifold.

Three visual modes show the map at different levels:
  • grid   — weight vectors as colored tiles (2D input → palette)
  • ribbon — 1D topology ring mapping to 3D color cube
  • flow   — 2D map over a flow field (x,y training data)

Controls:
  1 / 2 / 3  — switch mode (grid / ribbon / flow)
  r          — reset and retrain
  Space      — pause / resume training
  s          — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800

# SOM grid dimensions
ROWS, COLS = 40, 40
N_NEURONS = ROWS * COLS

# Training schedule
MAX_ITER = 20_000
LR_0 = 0.5  # initial learning rate
SIGMA_0 = max(ROWS, COLS) / 2.0  # initial neighbourhood radius
LAMBDA = MAX_ITER / np.log(SIGMA_0)  # decay constant

STEPS_PER_FRAME = 80  # training steps per draw call

MODES = ["grid", "ribbon", "flow"]

# State
_weights: np.ndarray  # (N_NEURONS, 3) or (N_NEURONS, 2) weights in [0,1]
_iter = 0
paused = False
mode_idx = 0
mode = MODES[0]

# Precomputed neuron indices for neighbourhood distance
_neuron_rc = np.array([[r, c] for r in range(ROWS) for c in range(COLS)], dtype=np.float32)


def _reset() -> None:
    global _weights, _iter
    _weights = np.random.rand(N_NEURONS, 3).astype(np.float32)
    _iter = 0


def _sample_input() -> np.ndarray:
    """Draw a random training sample in [0,1]^3 (RGB cube)."""
    if mode == "ribbon":
        # Samples on a circle in a 2D subspace → 3D
        t = np.random.uniform(0, 2 * np.pi)
        x = (np.cos(t) + 1) * 0.5
        y = (np.sin(t) + 1) * 0.5
        return np.array([x, y, 0.5], dtype=np.float32)
    elif mode == "flow":
        # 2D Gaussian blobs
        centers = np.array([[0.2, 0.2], [0.8, 0.2], [0.5, 0.8]], dtype=np.float32)
        c = centers[np.random.randint(len(centers))]
        pt = np.clip(c + np.random.randn(2).astype(np.float32) * 0.12, 0, 1)
        return np.array([pt[0], pt[1], 0.4], dtype=np.float32)
    else:
        return np.random.rand(3).astype(np.float32)


def _train_step() -> None:
    global _iter
    if _iter >= MAX_ITER:
        return

    t = _iter
    lr = LR_0 * np.exp(-t / MAX_ITER)
    sigma = SIGMA_0 * np.exp(-t / LAMBDA)

    sample = _sample_input()

    # Find best matching unit (BMU)
    diff = _weights - sample
    dists_sq = (diff * diff).sum(axis=1)
    bmu = int(dists_sq.argmin())

    # BMU position on grid
    bmu_r, bmu_c = bmu // COLS, bmu % COLS
    bmu_pos = np.array([bmu_r, bmu_c], dtype=np.float32)

    # Neighbourhood influence (Gaussian around BMU)
    d2 = ((_neuron_rc - bmu_pos) ** 2).sum(axis=1)
    h = np.exp(-d2 / (2 * sigma * sigma)).astype(np.float32)

    # Update weights
    _weights += lr * h[:, np.newaxis] * (sample - _weights)
    _weights = np.clip(_weights, 0, 1)

    _iter += 1


def _render_grid() -> None:
    """Render SOM weights as colored tiles."""
    cell_w = WIDTH / COLS
    cell_h = HEIGHT / ROWS
    py5.no_stroke()
    for r in range(ROWS):
        for c in range(COLS):
            idx = r * COLS + c
            w = _weights[idx]
            py5.fill(int(w[0] * 255), int(w[1] * 255), int(w[2] * 255))
            py5.rect(c * cell_w, r * cell_h, cell_w + 1, cell_h + 1)


def _render_ribbon() -> None:
    """Draw neurons as a connected ring in screen space, colored by weight."""
    py5.background(15, 15, 25)
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    ring_r = min(WIDTH, HEIGHT) * 0.38
    py5.stroke_weight(3)
    py5.no_fill()

    for i in range(N_NEURONS):
        j = (i + 1) % N_NEURONS
        ang_i = 2 * np.pi * i / N_NEURONS
        ang_j = 2 * np.pi * j / N_NEURONS
        xi, yi = cx + np.cos(ang_i) * ring_r, cy + np.sin(ang_i) * ring_r
        xj, yj = cx + np.cos(ang_j) * ring_r, cy + np.sin(ang_j) * ring_r
        w = _weights[i]
        py5.stroke(int(w[0] * 255), int(w[1] * 255), int(w[2] * 255))
        py5.line(xi, yi, xj, yj)

    # Draw weight positions in color cube projected to 2D
    py5.stroke_weight(2)
    for i in range(N_NEURONS):
        w = _weights[i]
        # Project R,G → x,y; B → brightness
        wx = w[0] * WIDTH * 0.4 + WIDTH * 0.3
        wy = w[1] * HEIGHT * 0.4 + HEIGHT * 0.3
        alpha = 80 + int(w[2] * 175)
        py5.stroke(int(w[0] * 255), int(w[1] * 255), int(w[2] * 255), alpha)
        py5.point(wx, wy)


def _render_flow() -> None:
    """SOM grid as a flow field overlay."""
    cell_w = WIDTH / COLS
    cell_h = HEIGHT / ROWS
    py5.background(10, 12, 22)
    py5.stroke_weight(1.2)

    for r in range(ROWS):
        for c in range(COLS):
            idx = r * COLS + c
            w = _weights[idx]
            # Position on screen
            x = (c + 0.5) * cell_w
            y = (r + 0.5) * cell_h
            # Weight as 2D direction vector
            dx = (w[0] - 0.5) * cell_w * 0.8
            dy = (w[1] - 0.5) * cell_h * 0.8
            mag = (dx * dx + dy * dy) ** 0.5 + 1e-4
            bri = min(int(mag / (cell_w * 0.5) * 180) + 40, 220)
            py5.stroke(int(w[0] * 255), int(w[1] * 255), bri)
            py5.line(x - dx * 0.5, y - dy * 0.5, x + dx * 0.5, y + dy * 0.5)
            # Arrowhead dot
            py5.fill(int(w[0] * 255), int(w[1] * 255), bri, 160)
            py5.no_stroke()
            py5.circle(x + dx * 0.5, y + dy * 0.5, 2.5)
            py5.stroke_weight(1.2)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.color_mode(py5.RGB)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused and _iter < MAX_ITER:
        for _ in range(STEPS_PER_FRAME):
            _train_step()

    if mode == "ribbon":
        _render_ribbon()
    elif mode == "flow":
        _render_flow()
    else:
        _render_grid()

    # HUD
    py5.fill(220, 220, 255)
    py5.no_stroke()
    py5.text_size(12)
    done = _iter >= MAX_ITER
    py5.text(
        f"mode:{mode}  iter:{_iter}/{MAX_ITER}  "
        f"{'DONE' if done else 'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, mode_idx, mode
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        mode_idx = 0
        mode = MODES[mode_idx]
        _reset()
    elif k == "2":
        mode_idx = 1
        mode = MODES[mode_idx]
        _reset()
    elif k == "3":
        mode_idx = 2
        mode = MODES[mode_idx]
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"kohonen_som_{mode}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
