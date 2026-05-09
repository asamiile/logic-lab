"""Acrylic Pour - Fluid dynamics with gravity and color mixing."""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Canvas parameters
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Fluid parameters
GRAVITY = 0.15  # Downward acceleration
VISCOSITY = 0.98  # Velocity damping
DIFFUSION = 0.95  # Color spread
DISSIPATION = 0.99  # Velocity dissipation
INJECT_RADIUS = 15


class AcrylicPourSimulation:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # Color field
        self.color = np.ones((height, width, 3), dtype=np.float32) * 240

        # Velocity field
        self.vel_x = np.zeros((height, width), dtype=np.float32)
        self.vel_y = np.zeros((height, width), dtype=np.float32)

        # Density for divergence-free constraint
        self.density = np.zeros((height, width), dtype=np.float32)

    def advect_color(self) -> None:
        """Move colors along velocity field using semi-Lagrangian advection."""
        new_color = np.copy(self.color)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Trace back along velocity
                src_x = x - self.vel_x[y, x] * 2
                src_y = y - self.vel_y[y, x] * 2

                # Clamp to bounds
                src_x = np.clip(src_x, 0, self.width - 1)
                src_y = np.clip(src_y, 0, self.height - 1)

                # Bilinear interpolation
                ix = int(src_x)
                iy = int(src_y)
                fx = src_x - ix
                fy = src_y - iy

                if ix + 1 < self.width and iy + 1 < self.height:
                    c00 = self.color[iy, ix]
                    c10 = self.color[iy, ix + 1]
                    c01 = self.color[iy + 1, ix]
                    c11 = self.color[iy + 1, ix + 1]

                    new_color[y, x] = (
                        (1 - fx) * (1 - fy) * c00
                        + fx * (1 - fy) * c10
                        + (1 - fx) * fy * c01
                        + fx * fy * c11
                    )

        self.color = new_color * DIFFUSION

    def apply_forces(self) -> None:
        """Apply gravity and update velocity."""
        # Add gravity (downward)
        self.vel_y[:-1] += GRAVITY

        # Apply diffusion to velocity
        self.vel_x *= VISCOSITY
        self.vel_y *= VISCOSITY

        # Dissipate at edges
        self.vel_x[0] *= 0
        self.vel_x[-1] *= 0
        self.vel_y[0] *= 0
        self.vel_y[-1] *= 0

    def diffuse_color_horizontally(self) -> None:
        """Spread color horizontally due to surface tension."""
        new_color = np.copy(self.color)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                neighbors = (
                    self.color[y - 1, x]
                    + self.color[y + 1, x]
                    + self.color[y, x - 1]
                    + self.color[y, x + 1]
                ) / 4.0
                new_color[y, x] = self.color[y, x] * 0.7 + neighbors * 0.3

        self.color = new_color

    def inject_fluid(self, x: int, y: int, color: tuple[float, float, float]) -> None:
        """Inject fluid at mouse position."""
        y = int(np.clip(y, 0, self.height - 1))
        x = int(np.clip(x, 0, self.width - 1))

        for dy in range(-INJECT_RADIUS, INJECT_RADIUS + 1):
            for dx in range(-INJECT_RADIUS, INJECT_RADIUS + 1):
                ny = y + dy
                nx = x + dx
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= INJECT_RADIUS:
                        strength = 1.0 - dist / INJECT_RADIUS

                        # Add color
                        self.color[ny, nx] = (
                            self.color[ny, nx] * (1 - strength * 0.7)
                            + np.array(color) * strength * 0.7
                        )

                        # Add downward velocity
                        self.vel_y[ny, nx] += GRAVITY * strength * 2

    def step(self) -> None:
        """Update simulation."""
        self.apply_forces()
        self.advect_color()
        self.diffuse_color_horizontally()

    def clear(self) -> None:
        """Reset simulation."""
        self.color[:] = 240
        self.vel_x[:] = 0
        self.vel_y[:] = 0

    def get_display_image(self) -> np.ndarray:
        """Return image for display."""
        return np.clip(self.color, 0, 255).astype(np.uint8)


sim = AcrylicPourSimulation(CANVAS_WIDTH, CANVAS_HEIGHT)
current_color = (255, 100, 100)


def setup() -> None:
    py5.size(CANVAS_WIDTH, CANVAS_HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    # Simulation step
    sim.step()

    # Render
    img = sim.get_display_image()
    py5.image(py5.create_image_from_numpy(img), 0, 0)

    # Draw info
    py5.fill(50)
    py5.text_size(12)
    py5.text(
        "Acrylic Pour | Drag: pour | 1-4: color | s: save | c: clear | space: reset",
        10,
        py5.height - 10,
    )

    # Color swatch
    py5.fill(*current_color)
    py5.rect(10, py5.height - 30, 20, 20)


def mouse_dragged() -> None:
    sim.inject_fluid(py5.mouse_x, py5.mouse_y, current_color)


def key_pressed() -> None:
    global current_color

    if py5.key == "1":
        current_color = (255, 100, 100)  # Red
    elif py5.key == "2":
        current_color = (100, 150, 255)  # Blue
    elif py5.key == "3":
        current_color = (100, 255, 150)  # Green
    elif py5.key == "4":
        current_color = (255, 200, 80)  # Orange
    elif py5.key == "c":
        sim.clear()
    elif py5.key == " ":
        sim.clear()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "acrylic_pour_####.png"))


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
