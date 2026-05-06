import random
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# State
heightmap = None
roughness = 0.7
seed_value = 42


def initialize_terrain(size: int, roughness_factor: float) -> np.ndarray:
    """Initialize terrain using diamond-square algorithm."""
    global roughness
    roughness = roughness_factor

    # Create power-of-2 grid
    grid_size = size + 1
    terrain = np.zeros((grid_size, grid_size), dtype=np.float32)

    # Initialize corners with random values
    terrain[0, 0] = random.uniform(0, 1)
    terrain[0, -1] = random.uniform(0, 1)
    terrain[-1, 0] = random.uniform(0, 1)
    terrain[-1, -1] = random.uniform(0, 1)

    # Run diamond-square algorithm
    step_size = size
    scale = 1.0

    while step_size > 1:
        half_step = step_size // 2

        # Diamond step
        for y in range(0, size, step_size):
            for x in range(0, size, step_size):
                avg = (
                    terrain[y, x]
                    + terrain[y, x + step_size]
                    + terrain[y + step_size, x]
                    + terrain[y + step_size, x + step_size]
                ) / 4.0
                offset = random.uniform(-1, 1) * scale
                terrain[y + half_step, x + half_step] = avg + offset

        # Square step
        for y in range(0, size, half_step):
            for x in range((y + half_step) % step_size, size, step_size):
                avg_sum = 0
                count = 0
                # Get adjacent diamond centers
                if y >= half_step:
                    avg_sum += terrain[y - half_step, x]
                    count += 1
                if y + half_step <= size:
                    avg_sum += terrain[y + half_step, x]
                    count += 1
                if x >= half_step:
                    avg_sum += terrain[y, x - half_step]
                    count += 1
                if x + half_step <= size:
                    avg_sum += terrain[y, x + half_step]
                    count += 1

                if count > 0:
                    avg = avg_sum / count
                    offset = random.uniform(-1, 1) * scale
                    terrain[y, x] = avg + offset

        step_size = half_step
        scale *= roughness

    return terrain


def setup() -> None:
    global heightmap
    py5.size(640, 640)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    random.seed(seed_value)
    np.random.seed(seed_value)
    heightmap = initialize_terrain(512, roughness)


def draw() -> None:
    global heightmap

    if heightmap is not None:
        w, h = py5.pixel_width, py5.pixel_height
        normalized = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min() + 1e-6)

        # Sample heightmap at screen resolution
        pixels = np.zeros((h, w, 3), dtype=np.uint8)
        for y in range(h):
            src_y = int((y / h) * (heightmap.shape[0] - 1))
            for x in range(w):
                src_x = int((x / w) * (heightmap.shape[1] - 1))
                val = int(normalized[src_y, src_x] * 255)

                # Gradient: dark blue -> cyan -> white
                if val < 85:
                    r, g, b = 0, val, 170
                elif val < 170:
                    r, g, b = 0, 255, 255 - (val - 85) // 2
                else:
                    r, g, b = val, 255, 255 - (val - 170) // 2
                pixels[y, x] = [r, g, b]

        py5.set_np_pixels(pixels, bands="RGB")

    # Info
    py5.fill(255, 0, 0)
    py5.text(f"Roughness: {roughness:.2f} | r/f: adjust | n: new seed | s: save", 10, 20)


def key_pressed() -> None:
    global heightmap, roughness, seed_value
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "diamond_square_####.png"))
    elif py5.key == "r":
        roughness = min(1.0, roughness + 0.05)
        random.seed(seed_value)
        np.random.seed(seed_value)
        heightmap = initialize_terrain(512, roughness)
    elif py5.key == "f":
        roughness = max(0.1, roughness - 0.05)
        random.seed(seed_value)
        np.random.seed(seed_value)
        heightmap = initialize_terrain(512, roughness)
    elif py5.key == "n":
        seed_value = random.randint(0, 10000)
        random.seed(seed_value)
        np.random.seed(seed_value)
        heightmap = initialize_terrain(512, roughness)


py5.run_sketch()
