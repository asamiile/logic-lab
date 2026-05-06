import math
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# State
seeds = []
use_poisson = False


def generate_poisson_seeds(width: int, height: int, min_dist: float = 40) -> list[tuple]:
    """Generate seed points using Poisson disk sampling."""
    import random

    points = []
    cell = min_dist / math.sqrt(2)
    grid = {}
    active = []

    # Start with random first point
    first = (random.uniform(0, width), random.uniform(0, height))
    points.append(first)
    active.append(first)
    grid[_grid_coords(first, cell)] = first

    # Process active list
    while active:
        idx = random.randint(0, len(active) - 1)
        point = active[idx]
        found = False

        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(min_dist, 2 * min_dist)
            new_x = point[0] + distance * math.cos(angle)
            new_y = point[1] + distance * math.sin(angle)

            if not (0 <= new_x < width and 0 <= new_y < height):
                continue

            new_point = (new_x, new_y)

            if _is_valid_seed(new_point, min_dist, grid, cell):
                points.append(new_point)
                active.append(new_point)
                grid[_grid_coords(new_point, cell)] = new_point
                found = True
                break

        if not found:
            active.pop(idx)

    return points


def _grid_coords(point: tuple, cell: float) -> tuple:
    return (int(point[0] / cell), int(point[1] / cell))


def _is_valid_seed(point: tuple, min_dist: float, grid_dict: dict, cell: float) -> bool:
    search_radius = 2
    grid_x, grid_y = _grid_coords(point, cell)

    for dx in range(-search_radius, search_radius + 1):
        for dy in range(-search_radius, search_radius + 1):
            neighbor_key = (grid_x + dx, grid_y + dy)
            if neighbor_key in grid_dict:
                neighbor = grid_dict[neighbor_key]
                dist = math.sqrt((point[0] - neighbor[0]) ** 2 + (point[1] - neighbor[1]) ** 2)
                if dist < min_dist:
                    return False

    return True


def compute_voronoi() -> np.ndarray:
    """Compute Voronoi diagram using brute-force nearest neighbor."""
    if not seeds:
        return np.zeros((py5.pixel_height, py5.pixel_width), dtype=np.uint8)

    w, h = py5.pixel_width, py5.pixel_height
    diagram = np.zeros((h, w), dtype=np.uint8)

    seeds_array = np.array(seeds, dtype=np.float32)

    for y in range(h):
        for x in range(w):
            # Compute distance to all seeds
            distances = np.sqrt((seeds_array[:, 0] - x) ** 2 + (seeds_array[:, 1] - y) ** 2)
            nearest_idx = np.argmin(distances)
            diagram[y, x] = nearest_idx % 256

    return diagram


def setup() -> None:
    global seeds
    py5.size(640, 480)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize with a few random seeds
    seeds = [(100, 100), (500, 100), (300, 400), (600, 400)]


def draw() -> None:
    global seeds

    if seeds:
        # Compute and display Voronoi diagram
        w, h = py5.pixel_width, py5.pixel_height
        diagram = compute_voronoi()

        # Colorize based on seed index
        pixels = np.zeros((h, w, 3), dtype=np.uint8)
        for i, (sx, sy) in enumerate(seeds):
            mask = diagram == (i % 256)
            hue = (i * 360 // len(seeds)) % 360
            sat = 80
            bright = 75
            # Manual HSB to RGB conversion (0-360 H, 0-100 S, 0-100 B)
            h_norm = hue / 60.0
            s_norm = sat / 100.0
            b_norm = bright / 100.0
            c = b_norm * s_norm
            x = c * (1 - abs((h_norm % 2) - 1))
            m = b_norm - c
            if h_norm < 1:
                r_temp, g_temp, b_temp = c, x, 0
            elif h_norm < 2:
                r_temp, g_temp, b_temp = x, c, 0
            elif h_norm < 3:
                r_temp, g_temp, b_temp = 0, c, x
            elif h_norm < 4:
                r_temp, g_temp, b_temp = 0, x, c
            elif h_norm < 5:
                r_temp, g_temp, b_temp = x, 0, c
            else:
                r_temp, g_temp, b_temp = c, 0, x
            r = int((r_temp + m) * 255)
            g = int((g_temp + m) * 255)
            b = int((b_temp + m) * 255)
            pixels[mask] = [r, g, b]

        py5.set_np_pixels(pixels, bands="RGB")

        # Draw seed points
        py5.stroke(0)
        py5.stroke_weight(2)
        py5.fill(255)
        for sx, sy in seeds:
            py5.ellipse(sx, sy, 8, 8)

    # Draw info
    py5.fill(0)
    py5.text(
        f"Seeds: {len(seeds)} | Click: add seed | p: Poisson seeds | c: clear | s: save", 10, 20
    )
    if use_poisson:
        py5.text("(Poisson mode)", 10, 40)


def mouse_pressed() -> None:
    global seeds
    if 0 <= py5.mouse_x < py5.width and 0 <= py5.mouse_y < py5.height:
        seeds.append((py5.mouse_x, py5.mouse_y))


def key_pressed() -> None:
    global seeds, use_poisson
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "voronoi_####.png"))
    elif py5.key == "c":
        seeds = [(100, 100), (500, 100), (300, 400), (600, 400)]
    elif py5.key == "p":
        use_poisson = True
        seeds = generate_poisson_seeds(py5.width, py5.height, 50)
        use_poisson = False


py5.run_sketch()
