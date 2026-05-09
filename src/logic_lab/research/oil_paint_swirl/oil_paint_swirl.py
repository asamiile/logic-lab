"""Oil Paint Swirl - Color flowing and mixing with swirling motion."""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Canvas parameters
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Simulation parameters
FLOW_SPEED = 0.02
DIFFUSION_RATE = 0.98  # How fast colors blend
ADVECTION_DAMPING = 0.99  # Velocity damping
STROKE_RADIUS = 20


class OilPaintSwirl:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.float32)
        self.flow_field = np.zeros((height, width, 2), dtype=np.float32)
        self.flow_time = 0.0
        self.velocity_x = np.zeros((height, width), dtype=np.float32)
        self.velocity_y = np.zeros((height, width), dtype=np.float32)

    def update_flow_field(self) -> None:
        """Update Perlin noise-based flow field."""
        self.flow_time += 0.01
        for y in range(self.height):
            for x in range(self.width):
                # Perlin-like noise for flow direction
                nx = x / self.width
                ny = y / self.height
                # Simplified flow using sin/cos
                angle = (
                    py5.sin(nx * 5 + self.flow_time) * 0.5
                    + py5.sin(ny * 5 + self.flow_time * 0.7) * 0.5
                )
                speed = (
                    py5.sin(nx * 3 + self.flow_time * 0.3) * 0.3
                    + py5.sin(ny * 3 + self.flow_time * 0.5) * 0.3
                )
                self.flow_field[y, x, 0] = py5.cos(angle) * (0.5 + speed)
                self.flow_field[y, x, 1] = py5.sin(angle) * (0.5 + speed)

    def advect_colors(self) -> None:
        """Move colors along flow field."""
        new_canvas = np.copy(self.canvas)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Advect from source position
                src_x = x - self.flow_field[y, x, 0] * FLOW_SPEED * self.width
                src_y = y - self.flow_field[y, x, 1] * FLOW_SPEED * self.height

                # Bilinear interpolation
                src_x = np.clip(src_x, 0, self.width - 1)
                src_y = np.clip(src_y, 0, self.height - 1)

                ix = int(src_x)
                iy = int(src_y)
                fx = src_x - ix
                fy = src_y - iy

                if ix + 1 < self.width and iy + 1 < self.height:
                    new_canvas[y, x] = (
                        (1 - fx) * (1 - fy) * self.canvas[iy, ix]
                        + fx * (1 - fy) * self.canvas[iy, ix + 1]
                        + (1 - fx) * fy * self.canvas[iy + 1, ix]
                        + fx * fy * self.canvas[iy + 1, ix + 1]
                    )

        self.canvas = new_canvas * ADVECTION_DAMPING

    def diffuse_colors(self) -> None:
        """Blend colors with neighbors."""
        new_canvas = np.copy(self.canvas)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Average with neighbors
                neighbor_sum = (
                    self.canvas[y - 1, x]
                    + self.canvas[y + 1, x]
                    + self.canvas[y, x - 1]
                    + self.canvas[y, x + 1]
                ) / 4.0
                new_canvas[y, x] = (
                    self.canvas[y, x] * (1 - DIFFUSION_RATE) + neighbor_sum * DIFFUSION_RATE
                )

        self.canvas = np.clip(new_canvas, 0, 255)

    def add_stroke(self, x: int, y: int, color: tuple[float, float, float]) -> None:
        """Add paint stroke at position."""
        y = int(np.clip(y, 0, self.height - 1))
        x = int(np.clip(x, 0, self.width - 1))

        for dy in range(-STROKE_RADIUS, STROKE_RADIUS + 1):
            for dx in range(-STROKE_RADIUS, STROKE_RADIUS + 1):
                ny = y + dy
                nx = x + dx
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= STROKE_RADIUS:
                        # Gaussian falloff
                        strength = np.exp(-(dist**2) / (STROKE_RADIUS**2 * 0.5))
                        self.canvas[ny, nx] = (
                            self.canvas[ny, nx] * (1 - strength) + np.array(color) * strength
                        )

    def step(self) -> None:
        """Update simulation."""
        self.update_flow_field()
        self.advect_colors()
        self.diffuse_colors()

    def get_display_image(self) -> np.ndarray:
        """Return image for display."""
        return np.clip(self.canvas, 0, 255).astype(np.uint8)


swirl = OilPaintSwirl(CANVAS_WIDTH, CANVAS_HEIGHT)
painting_mode = True
current_color = (255, 100, 100)  # Red by default


def setup() -> None:
    py5.size(CANVAS_WIDTH, CANVAS_HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global current_color

    # Simulation step
    swirl.step()

    # Draw canvas
    img = swirl.get_display_image()
    py5.image(py5.create_image_from_numpy(img), 0, 0)

    # Draw info
    py5.fill(255)
    py5.text_size(12)
    py5.text(
        "Oil Paint Swirl | Drag: paint | 1-3: color | s: save | c: clear",
        10,
        py5.height - 10,
    )
    py5.fill(*current_color)
    py5.rect(10, py5.height - 30, 20, 20)


def mouse_dragged() -> None:
    if painting_mode:
        swirl.add_stroke(py5.mouse_x, py5.mouse_y, current_color)


def key_pressed() -> None:
    global current_color

    if py5.key == "1":
        current_color = (255, 100, 100)  # Red
    elif py5.key == "2":
        current_color = (100, 150, 255)  # Blue
    elif py5.key == "3":
        current_color = (100, 255, 150)  # Green
    elif py5.key == "c":
        swirl.canvas[:] = 0
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "oil_paint_swirl_####.png"))


def create_image_from_numpy(arr: np.ndarray):
    """Helper to create py5 image from numpy array."""
    height, width = arr.shape[:2]
    img = py5.create_image(width, height, py5.RGB)
    img.load_pixels()
    for i, pixel in enumerate(arr.reshape(-1, 3)):
        img.pixels[i] = py5.color(*pixel)
    img.update_pixels()
    return img


py5.create_image_from_numpy = create_image_from_numpy

py5.run_sketch()
