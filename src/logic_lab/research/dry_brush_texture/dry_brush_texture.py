"""Dry Brush Texture - Rough brush strokes with texture and paper interaction."""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Canvas parameters
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Brush parameters
STROKE_RADIUS = 20
ROUGHNESS = 0.6  # How much texture breaks up the stroke
PAPER_SCALE = 0.05  # Paper texture detail
PAPER_OCTAVES = 4


class PaperTexture:
    """Generate paper texture using Perlin-like noise."""

    def __init__(self, width: int, height: int, scale: float = 0.05, octaves: int = 4):
        self.width = width
        self.height = height
        self.scale = scale
        self.octaves = octaves
        self.texture = self._generate_texture()

    def _generate_texture(self) -> np.ndarray:
        """Generate procedural paper texture."""
        texture = np.zeros((self.height, self.width), dtype=np.float32)

        for octave in range(self.octaves):
            freq = 2**octave
            amplitude = 1.0 / (octave + 1)

            for y in range(self.height):
                for x in range(self.width):
                    # Simplified Perlin-like noise
                    nx = (x * self.scale * freq) % 256
                    ny = (y * self.scale * freq) % 256
                    noise_val = py5.sin(nx * 0.1) * py5.cos(ny * 0.1) * amplitude
                    texture[y, x] += noise_val

        # Normalize to 0-1
        texture = (texture - texture.min()) / (texture.max() - texture.min() + 1e-6)
        return texture

    def get_value(self, x: int, y: int) -> float:
        """Get texture value at position."""
        x = int(np.clip(x, 0, self.width - 1))
        y = int(np.clip(y, 0, self.height - 1))
        return self.texture[y, x]


class DryBrushCanvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.canvas = np.ones((height, width, 3), dtype=np.float32) * 240  # Off-white
        self.paper = PaperTexture(width, height, PAPER_SCALE, PAPER_OCTAVES)

    def add_stroke(
        self,
        x: int,
        y: int,
        color: tuple[float, float, float],
    ) -> None:
        """Add dry brush stroke with texture."""
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

                        # Get paper texture - high values = less paint
                        paper_tex = self.paper.get_value(nx, ny)

                        # Combine strength with paper texture and roughness
                        # High roughness = more texture breaks up the stroke
                        paint_coverage = strength * (1 - paper_tex * ROUGHNESS)

                        # Blend color
                        self.canvas[ny, nx] = (
                            self.canvas[ny, nx] * (1 - paint_coverage)
                            + np.array(color) * paint_coverage
                        )

    def clear(self) -> None:
        """Clear canvas."""
        self.canvas[:] = 240  # Reset to off-white

    def get_display_image(self) -> np.ndarray:
        """Return image for display."""
        return np.clip(self.canvas, 0, 255).astype(np.uint8)


canvas = DryBrushCanvas(CANVAS_WIDTH, CANVAS_HEIGHT)
current_color = (180, 100, 50)  # Warm brown by default
is_drawing = False


def setup() -> None:
    py5.size(CANVAS_WIDTH, CANVAS_HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    # Display canvas
    img = canvas.get_display_image()
    py5.image(py5.create_image_from_numpy(img), 0, 0)

    # Draw info
    py5.fill(100)
    py5.text_size(12)
    py5.text(
        "Dry Brush Texture | Drag: paint | 1-3: color | s: save | c: clear",
        10,
        py5.height - 10,
    )

    # Color swatch
    py5.fill(*current_color)
    py5.rect(10, py5.height - 30, 20, 20)


def mouse_dragged() -> None:
    canvas.add_stroke(py5.mouse_x, py5.mouse_y, current_color)


def key_pressed() -> None:
    global current_color

    if py5.key == "1":
        current_color = (180, 100, 50)  # Warm brown
    elif py5.key == "2":
        current_color = (50, 80, 120)  # Cool blue-gray
    elif py5.key == "3":
        current_color = (60, 120, 80)  # Muted green
    elif py5.key == "c":
        canvas.clear()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "dry_brush_texture_####.png"))


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
