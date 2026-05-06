from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

Point = tuple[float, float]

points: list[Point] = []
previous_points: list[Point] = []
region_ids: np.ndarray | None = None
point_count = 42
sample_step = 5
iteration = 0
seed_value = 24
auto_relax = False
show_regions = True
show_motion = True


def setup() -> None:
    py5.size(680, 680)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_points()


def draw() -> None:
    global region_ids

    if auto_relax and py5.frame_count % 12 == 0:
        relax_once()

    region_ids = compute_regions(points)
    py5.background(214, 13, 96)
    if show_regions:
        draw_regions(region_ids)
    if show_motion:
        draw_motion_vectors()
    draw_points()
    draw_info()


def reset_points() -> None:
    global points, previous_points, iteration

    random.seed(seed_value)
    margin = 56
    points = [
        (
            random.uniform(margin, py5.width - margin),
            random.uniform(margin, py5.height - margin),
        )
        for _ in range(point_count)
    ]
    previous_points = points.copy()
    iteration = 0


def compute_regions(seeds: list[Point]) -> np.ndarray:
    cols = py5.width // sample_step
    rows = py5.height // sample_step
    ids = np.zeros((rows, cols), dtype=np.int32)
    seed_array = np.array(seeds, dtype=np.float32)

    for row in range(rows):
        y = row * sample_step + sample_step * 0.5
        for col in range(cols):
            x = col * sample_step + sample_step * 0.5
            dx = seed_array[:, 0] - x
            dy = seed_array[:, 1] - y
            ids[row, col] = int(np.argmin(dx * dx + dy * dy))

    return ids


def relax_once() -> None:
    global points, previous_points, iteration

    ids = compute_regions(points)
    sums = np.zeros((len(points), 2), dtype=np.float64)
    counts = np.zeros(len(points), dtype=np.int32)

    rows, cols = ids.shape
    for row in range(rows):
        y = row * sample_step + sample_step * 0.5
        for col in range(cols):
            x = col * sample_step + sample_step * 0.5
            idx = ids[row, col]
            sums[idx, 0] += x
            sums[idx, 1] += y
            counts[idx] += 1

    previous_points = points.copy()
    next_points = []
    for i, point in enumerate(points):
        if counts[i] == 0:
            next_points.append(point)
        else:
            next_points.append((float(sums[i, 0] / counts[i]), float(sums[i, 1] / counts[i])))
    points = next_points
    iteration += 1


def draw_regions(ids: np.ndarray) -> None:
    rows, cols = ids.shape
    py5.no_stroke()
    for row in range(rows):
        for col in range(cols):
            idx = int(ids[row, col])
            hue = (184 + idx * 31) % 360
            py5.fill(hue, 32, 91, 68)
            py5.rect(col * sample_step, row * sample_step, sample_step + 1, sample_step + 1)


def draw_motion_vectors() -> None:
    py5.stroke(24, 82, 42, 72)
    py5.stroke_weight(1.4)
    for before, after in zip(previous_points, points):
        if distance_sq(before, after) < 0.05:
            continue
        py5.line(before[0], before[1], after[0], after[1])


def draw_points() -> None:
    py5.no_stroke()
    for x, y in points:
        py5.fill(214, 70, 12, 86)
        py5.circle(x, y, 12)
        py5.fill(42, 94, 98, 100)
        py5.circle(x, y, 5)


def distance_sq(a: Point, b: Point) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


def draw_info() -> None:
    py5.no_stroke()
    py5.fill(214, 24, 12, 90)
    py5.rect(14, 14, 610, 54, 4)
    py5.fill(0, 0, 100, 100)
    state = "auto" if auto_relax else "manual"
    py5.text(
        f"Lloyd relaxation | {state} | points {len(points)} | iteration {iteration} | n: step | a: auto | r: reset | +/-: count | v: regions | m: motion | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global seed_value, point_count, auto_relax, show_regions, show_motion

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "lloyd_relaxation_####.png"))
    elif py5.key == "n":
        relax_once()
    elif py5.key == "a":
        auto_relax = not auto_relax
    elif py5.key == "r":
        seed_value = random.randint(0, 100000)
        reset_points()
    elif py5.key == "+":
        point_count = min(140, point_count + 6)
        reset_points()
    elif py5.key == "-":
        point_count = max(4, point_count - 6)
        reset_points()
    elif py5.key == "v":
        show_regions = not show_regions
    elif py5.key == "m":
        show_motion = not show_motion


py5.run_sketch()
