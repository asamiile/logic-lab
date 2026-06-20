"""
Evolving Circles — Simple Genetic Algorithm
A population of 2D circles (genes: x, y, radius, color) evolves to
reconstruct a target image or shape via fitness-based selection and mutation.

Algorithm:
  1. Evaluate each individual (circle) against the target (fitness = overlap).
  2. Select parents (tournament or roulette).
  3. Mutate: randomly perturb (x, y, r, RGBA) of survivors.
  4. Replace worst individuals with mutants.
  5. Repeat.

Over many generations, random circles collectively form a rough approximation
of the target. Emergent order from unguided individual search.

Three target modes:
  1. Target: growing circular gradient (mathematical)
  2. Target: horizontal stripe band
  3. Target: Mandelbrot set outline

Color: each circle's RGBA is part of genome; fitness reward overlapping
the target. Circles gradually cluster + color-match to recreate the image.

Controls:
  1–3     — target image
  +/−     — larger / smaller population
  Space   — pause / resume evolution
  r       — reset (randomize population)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800

N = 100  # population size
TARGET_IDX = 0
MUTATION_RATE = 0.15
MUTATION_STD = 0.05

paused = False

_genes: np.ndarray  # (N, 6) [x, y, r, r_g, b, a]
_fitness: np.ndarray  # (N,)


def _target_image(mode: int, x_arr: np.ndarray, y_arr: np.ndarray) -> np.ndarray:
    """Return target image pixel values (0–1)."""
    nx, ny = x_arr.shape
    if mode == 0:
        # Circular gradient
        cx, cy = 0.5, 0.5
        r = np.sqrt((x_arr - cx) ** 2 + (y_arr - cy) ** 2)
        return np.clip(1.0 - r * 2, 0, 1)
    elif mode == 1:
        # Horizontal stripes
        return (np.sin(y_arr * 10 * np.pi) > 0).astype(float)
    else:
        # Mandelbrot-like (simple quadratic)
        return np.clip(1.0 - ((x_arr - 0.5) ** 2 + (y_arr - 0.5) ** 2) ** 0.5 * 2, 0, 1)


def _evaluate_fitness() -> None:
    """Compute fitness for each circle based on overlap with target."""
    # Build target image on a coarse grid for speed
    res = 50
    xs = np.linspace(0, 1, res)
    ys = np.linspace(0, 1, res)
    XX, YY = np.meshgrid(xs, ys)
    target = _target_image(TARGET_IDX, XX, YY)

    # For each circle, compute overlap
    global _fitness
    _fitness = np.zeros(N)
    for i in range(N):
        x, y, r = _genes[i, 0], _genes[i, 1], _genes[i, 2]
        # Distance from circle center to each pixel
        dist = np.sqrt((XX - x) ** 2 + (YY - y) ** 2)
        in_circle = (dist < r).astype(float)
        # Fitness: overlap with target
        overlap = np.sum(in_circle * target) / (np.pi * r**2 + 1e-6)
        _fitness[i] = overlap


def _reset() -> None:
    global _genes
    _genes = np.random.uniform(0, 1, (N, 6))
    _genes[:, 2] = np.random.uniform(0.05, 0.3, N)  # radius smaller
    _genes[:, 3:] = np.random.uniform(0, 1, (N, 3))  # RGB
    _evaluate_fitness()


def _evolve_step() -> None:
    """One generation: select, mutate, replace."""
    # Select fittest (top 50%)
    order = np.argsort(-_fitness)
    elite_n = N // 2
    elite_idx = order[:elite_n]

    # Mutate elite to create offspring
    offspring = _genes[elite_idx].copy()
    mask = np.random.random((elite_n, 6)) < MUTATION_RATE
    offspring[mask] += np.random.normal(0, MUTATION_STD, np.sum(mask))
    offspring = np.clip(offspring, 0, 1)
    offspring[:, 2] = np.clip(offspring[:, 2], 0.02, 0.4)  # radius bounds

    # Replace worst individuals with offspring
    _genes[order[elite_n:]] = offspring
    _evaluate_fitness()


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        for _ in range(3):
            _evolve_step()

    # Render target in background
    res_render = 200
    xs = np.linspace(0, 1, res_render)
    ys = np.linspace(0, 1, res_render)
    XX, YY = np.meshgrid(xs, ys)
    target = _target_image(TARGET_IDX, XX, YY)

    # Scale and render target as background
    target_img = (target * 50).astype(np.uint8)
    scale = WIDTH / res_render

    py5.background(10, 10, 20)

    # Draw target faintly
    py5.no_stroke()
    for i in range(res_render):
        for j in range(res_render):
            gray = target_img[j, i]
            py5.fill(gray, gray, gray + 20)
            py5.rect(i * scale, j * scale, scale, scale)

    # Draw evolved circles
    py5.no_stroke()
    for i in range(N):
        x, y, r, rc, gc, bc = _genes[i]
        px = x * WIDTH
        py2 = y * HEIGHT
        pr = r * min(WIDTH, HEIGHT)
        py5.fill(int(rc * 220), int(gc * 220), int(bc * 220), 200)
        py5.circle(float(px), float(py2), float(pr))

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    targets = ["circle", "stripe", "mandel"]
    py5.text(
        f"Evolving circles  target:{targets[TARGET_IDX]}  N:{N}  "
        f"gen:{py5.frame_count * 3}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, TARGET_IDX, N
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        TARGET_IDX = 0
        _reset()
    elif k == "2":
        TARGET_IDX = 1
        _reset()
    elif k == "3":
        TARGET_IDX = 2
        _reset()
    elif k == "+":
        N = min(300, N + 20)
        _reset()
    elif k == "-":
        N = max(20, N - 20)
        _reset()
    elif k == "s":
        targets = ["circle", "stripe", "mandel"]
        py5.save_frame(str(SCREENSHOT_DIR / f"evolve_{targets[TARGET_IDX]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
