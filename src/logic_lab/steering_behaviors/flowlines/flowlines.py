from pathlib import Path
import py5
import math

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Flow field parameters
resolution = 20
scale = 0.01
time_offset = 0

# Streamline parameters
num_streamlines = 100
streamline_length = 200
line_width = 2


def get_flow_direction(x: float, y: float, t: float) -> tuple:
    """Get flow direction at position (x, y) using Perlin noise."""
    angle = py5.noise(x * scale, y * scale, t * 0.1) * 2 * math.pi
    return (math.cos(angle), math.sin(angle))


def trace_streamline(start_x: float, start_y: float, t: float, max_steps: int = 300) -> list:
    """Trace a streamline starting from (start_x, start_y) using Euler integration."""
    points = [(start_x, start_y)]
    x, y = start_x, start_y
    step_size = 2

    for _ in range(max_steps):
        # Get flow direction
        vx, vy = get_flow_direction(x, y, t)

        # Euler step
        x += vx * step_size
        y += vy * step_size

        # Boundary check
        if x < 0 or x >= py5.width or y < 0 or y >= py5.height:
            break

        points.append((x, y))

        # Check if we've traced long enough
        if len(points) > streamline_length:
            break

    return points


def setup() -> None:
    py5.size(800, 600)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_offset
    py5.background(255)

    # Draw flow field visualization (optional grid)
    py5.stroke(240)
    py5.stroke_weight(0.5)
    for y in range(0, py5.height, resolution):
        for x in range(0, py5.width, resolution):
            vx, vy = get_flow_direction(x, y, time_offset)
            length = 15
            end_x = x + vx * length
            end_y = y + vy * length
            py5.line(x, y, end_x, end_y)

    # Draw streamlines
    py5.no_fill()
    py5.stroke(50, 100, 200)
    py5.stroke_weight(line_width)

    # Generate random starting points
    py5.random_seed(42)  # Deterministic for consistency
    for _ in range(num_streamlines):
        start_x = py5.random(0, py5.width)
        start_y = py5.random(0, py5.height)

        streamline = trace_streamline(start_x, start_y, time_offset)

        if len(streamline) > 1:
            py5.begin_shape()
            for x, y in streamline:
                py5.curve_vertex(x, y)
            py5.end_shape()

    # Animate
    time_offset += 0.01

    # Draw info
    py5.fill(0)
    py5.text(f"t: {time_offset:.1f} | s: save", 10, 20)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "flowlines_####.png"))


py5.run_sketch()
