from pathlib import Path
import py5
import random
import math

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Parameters
min_distance = 20
max_samples = 30
cell_size = 0

# State
points = []
grid = {}


def generate_points(width: float, height: float, min_dist: float, k: int = 30) -> list[tuple]:
    """
    Fast Poisson disk sampling using Bridson (2007) algorithm.

    Returns list of (x, y) tuples with guaranteed minimum distance between points.
    """
    cell = min_dist / math.sqrt(2)

    # Initialize grid and active list
    grid_local = {}
    active = []
    points_local = []

    # Start with random first point
    first = (random.uniform(0, width), random.uniform(0, height))
    points_local.append(first)
    active.append(first)
    grid_local[_grid_coords(first, cell)] = first

    # Process active list
    while active:
        idx = random.randint(0, len(active) - 1)
        point = active[idx]
        found = False

        # Try k random samples around current point
        for _ in range(k):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(min_dist, 2 * min_dist)
            new_x = point[0] + distance * math.cos(angle)
            new_y = point[1] + distance * math.sin(angle)

            # Check bounds
            if not (0 <= new_x < width and 0 <= new_y < height):
                continue

            new_point = (new_x, new_y)

            # Check distance to existing points in neighboring cells
            if _is_valid(new_point, min_dist, grid_local, cell):
                points_local.append(new_point)
                active.append(new_point)
                grid_local[_grid_coords(new_point, cell)] = new_point
                found = True
                break

        if not found:
            active.pop(idx)

    return points_local


def _grid_coords(point: tuple, cell: float) -> tuple:
    """Convert point to grid coordinates."""
    return (int(point[0] / cell), int(point[1] / cell))


def _is_valid(point: tuple, min_dist: float, grid_dict: dict, cell: float) -> bool:
    """Check if point is valid (far enough from existing points)."""
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


def setup() -> None:
    global points, grid, cell_size
    py5.size(640, 640)
    py5.background(255)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate initial points
    cell_size = min_distance / math.sqrt(2)
    points = generate_points(py5.width, py5.height, min_distance, max_samples)


def draw() -> None:
    py5.background(255)

    # Draw points
    py5.fill(0)
    py5.no_stroke()
    for x, y in points:
        py5.ellipse(x, y, 4, 4)

    # Draw circles showing minimum distance
    py5.no_fill()
    py5.stroke(200)
    py5.stroke_weight(0.5)
    for x, y in points:
        py5.circle(x, y, min_distance * 2)

    # Draw info
    py5.fill(0)
    py5.text(f"Points: {len(points)} | Min dist: {min_distance} | Max samples: {max_samples}", 10, 20)
    py5.text("Arrow keys: adjust min distance | +/-: adjust max samples | r: regenerate | s: save", 10, 40)


def key_pressed() -> None:
    global points, min_distance, max_samples, cell_size

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "poisson_disk_####.png"))
    elif py5.key == "r":
        cell_size = min_distance / math.sqrt(2)
        points = generate_points(py5.width, py5.height, min_distance, max_samples)
    elif py5.key_code == py5.LEFT:
        min_distance = max(5, min_distance - 1)
        cell_size = min_distance / math.sqrt(2)
        points = generate_points(py5.width, py5.height, min_distance, max_samples)
    elif py5.key_code == py5.RIGHT:
        min_distance = min(100, min_distance + 1)
        cell_size = min_distance / math.sqrt(2)
        points = generate_points(py5.width, py5.height, min_distance, max_samples)
    elif py5.key == "+":
        max_samples = min(100, max_samples + 1)
        cell_size = min_distance / math.sqrt(2)
        points = generate_points(py5.width, py5.height, min_distance, max_samples)
    elif py5.key == "-":
        max_samples = max(1, max_samples - 1)
        cell_size = min_distance / math.sqrt(2)
        points = generate_points(py5.width, py5.height, min_distance, max_samples)


py5.run_sketch()
