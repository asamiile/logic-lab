import math
import random
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# State
feature_points = []
cell_size = 50
grid = {}
time_offset = 0
display_mode = 0  # 0: F1, 1: F2, 2: F2-F1, 3: Combined


def _grid_key(x: float, y: float) -> tuple:
    """Get grid cell key for a point."""
    return (int(x // cell_size), int(y // cell_size))


def generate_feature_points(width: int, height: int, spacing: float = 60) -> list:
    """Generate grid-aligned feature points."""
    points = []
    x = 0
    while x < width:
        y = 0
        while y < height:
            px = x + random.uniform(-spacing * 0.3, spacing * 0.3)
            py = y + random.uniform(-spacing * 0.3, spacing * 0.3)
            if 0 <= px < width and 0 <= py < height:
                points.append((px, py))
            y += spacing
        x += spacing
    return points


def setup() -> None:
    global feature_points
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    feature_points = generate_feature_points(py5.width, py5.height, 70)


def compute_worley_field() -> np.ndarray:
    """Compute Worley noise using grid acceleration."""
    w, h = py5.pixel_width, py5.pixel_height
    f1_field = np.full((h, w), float("inf"), dtype=np.float32)
    f2_field = np.full((h, w), float("inf"), dtype=np.float32)

    # Build spatial grid
    grid_dict = {}
    for px, py in feature_points:
        key = _grid_key(px, py)
        if key not in grid_dict:
            grid_dict[key] = []
        grid_dict[key].append((px, py))

    # For each pixel, check nearby grid cells
    for y in range(h):
        for x in range(w):
            grid_key = _grid_key(x, y)
            gx, gy = grid_key

            # Check 3x3 grid neighborhood
            min_dist1 = float("inf")
            min_dist2 = float("inf")

            for dgx in [-1, 0, 1]:
                for dgy in [-1, 0, 1]:
                    neighbor_key = (gx + dgx, gy + dgy)
                    if neighbor_key in grid_dict:
                        for px, py in grid_dict[neighbor_key]:
                            dx = x - px
                            dy = y - py
                            dist = math.sqrt(dx * dx + dy * dy)

                            if dist < min_dist1:
                                min_dist2 = min_dist1
                                min_dist1 = dist
                            elif dist < min_dist2:
                                min_dist2 = dist

            f1_field[y, x] = min_dist1
            f2_field[y, x] = min_dist2 if min_dist2 != float("inf") else min_dist1

    return f1_field, f2_field


def draw() -> None:
    global time_offset, display_mode

    w, h = py5.pixel_width, py5.pixel_height
    f1_field, f2_field = compute_worley_field()

    # Replace infinity with max finite value
    f1_finite = f1_field[np.isfinite(f1_field)]
    f2_finite = f2_field[np.isfinite(f2_field)]

    f1_max = f1_finite.max() if len(f1_finite) > 0 else 1.0
    f2_max = f2_finite.max() if len(f2_finite) > 0 else 1.0

    # Normalize fields, handling inf and nan
    f1_norm = np.nan_to_num(np.clip(f1_field / max(f1_max, 1.0), 0, 1), nan=0.0)
    f2_norm = np.nan_to_num(np.clip(f2_field / max(f2_max, 1.0), 0, 1), nan=0.0)

    # Visualize based on mode
    if display_mode == 0:  # F1
        field = f1_norm
    elif display_mode == 1:  # F2
        field = f2_norm
    elif display_mode == 2:  # F2 - F1 (edges)
        field = np.clip((f2_norm - f1_norm) * 2, 0, 1)
    else:  # Combined
        field = f1_norm * 0.7 + f2_norm * 0.3

    # Convert to pixels (handle any remaining NaN)
    field = np.nan_to_num(field, nan=0.0)
    pixels = (field * 255).astype(np.uint8)
    pixels_rgb = np.stack([pixels, pixels, pixels], axis=2)
    py5.set_np_pixels(pixels_rgb, bands="RGB")

    # Draw mode indicator
    py5.fill(255, 0, 0)
    modes = ["F1 (Distance)", "F2 (2nd nearest)", "F2-F1 (Edge)", "Combined"]
    py5.text(modes[display_mode], 10, 20)
    py5.text("1/2/3/4: mode | s: save", 10, py5.height - 10)


def key_pressed() -> None:
    global display_mode
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "worley_noise_####.png"))
    elif py5.key == "1":
        display_mode = 0
    elif py5.key == "2":
        display_mode = 1
    elif py5.key == "3":
        display_mode = 2
    elif py5.key == "4":
        display_mode = 3


py5.run_sketch()
