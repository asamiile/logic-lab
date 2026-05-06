import math
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Metaballs
metaballs = []
selected_ball = None
threshold = 1.0


class Metaball:
    def __init__(self, x: float, y: float, radius: float = 50):
        self.x = x
        self.y = y
        self.radius = radius

    def influence(self, px: float, py: float) -> float:
        """Compute influence at point (px, py)."""
        dx = px - self.x
        dy = py - self.y
        dist_sq = dx * dx + dy * dy

        if dist_sq == 0:
            return float("inf")

        # f(r) = r² / d²
        return (self.radius * self.radius) / dist_sq

    def contains(self, px: float, py: float) -> bool:
        """Check if point is close to this ball."""
        dx = px - self.x
        dy = py - self.y
        return dx * dx + dy * dy < (self.radius + 10) ** 2


def compute_metaball_field() -> np.ndarray:
    """Compute metaball field for entire screen."""
    w, h = py5.pixel_width, py5.pixel_height
    field = np.zeros((h, w), dtype=np.float32)

    for y in range(h):
        for x in range(w):
            total = 0
            for ball in metaballs:
                total += ball.influence(x, y)
            field[y, x] = min(total, 3.0)  # Clamp for visualization

    return field


def setup() -> None:
    global metaballs
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize with 3 metaballs
    metaballs = [
        Metaball(200, 150, 60),
        Metaball(400, 200, 50),
        Metaball(300, 350, 70),
    ]


def draw() -> None:
    global metaballs, selected_ball

    # Compute field
    field = compute_metaball_field()

    # Normalize and colorize
    w, h = py5.pixel_width, py5.pixel_height
    max_val = field.max()
    if max_val > 0:
        field_norm = field / max_val
    else:
        field_norm = field

    pixels = np.zeros((h, w, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            val = field_norm[y, x]

            # Color: low = blue, medium = cyan, high = white
            if val < 0.5:
                r = 0
                g = int(val * 2 * 255)
                b = 255
            else:
                r = int((val - 0.5) * 2 * 255)
                g = 255
                b = 255

            pixels[y, x] = [r, g, b]

    py5.set_np_pixels(pixels, bands="RGB")

    # Draw metaballs as circles
    py5.no_fill()
    py5.stroke(0)
    py5.stroke_weight(2)
    for ball in metaballs:
        if ball == selected_ball:
            py5.stroke(255, 0, 0)
            py5.stroke_weight(3)
        else:
            py5.stroke(100)
            py5.stroke_weight(2)
        py5.circle(ball.x, ball.y, ball.radius * 2)

    # Draw info
    py5.fill(255)
    py5.text(f"Balls: {len(metaballs)} | Click: drag ball | +/-: add/remove | s: save", 10, 20)


def mouse_pressed() -> None:
    global selected_ball, metaballs

    mx, my = py5.mouse_x, py5.mouse_y

    # Find closest ball
    closest = None
    closest_dist = 50

    for ball in metaballs:
        dx = ball.x - mx
        dy = ball.y - my
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < closest_dist:
            closest = ball
            closest_dist = dist

    selected_ball = closest


def mouse_dragged() -> None:
    if selected_ball:
        selected_ball.x = py5.mouse_x
        selected_ball.y = py5.mouse_y


def mouse_released() -> None:
    global selected_ball
    selected_ball = None


def key_pressed() -> None:
    global metaballs

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "metaball_####.png"))
    elif py5.key == "+":
        # Add new ball
        metaballs.append(
            Metaball(py5.random(100, py5.width - 100), py5.random(100, py5.height - 100))
        )
    elif py5.key == "-":
        # Remove last ball
        if metaballs:
            metaballs.pop()


py5.run_sketch()
