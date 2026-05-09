"""Impasto Rendering - Thick paint with visible brush strokes and relief."""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Canvas parameters
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Simulation parameters
STROKE_RADIUS = 25
HEIGHT_SCALE = 2.0  # How pronounced the relief is
AMBIENT_LIGHT = 0.3
LIGHT_DIRECTION = np.array([0.5, 0.5, 1.0])
LIGHT_DIRECTION = LIGHT_DIRECTION / np.linalg.norm(LIGHT_DIRECTION)


class ImpastoCanvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.color = np.zeros((height, width, 3), dtype=np.float32)
        self.height_map = np.zeros((height, width), dtype=np.float32)

    def add_stroke(
        self,
        x: int,
        y: int,
        color: tuple[float, float, float],
        paint_height: float = 30.0,
    ) -> None:
        """Add paint stroke with height information."""
        y = int(np.clip(y, 0, self.height - 1))
        x = int(np.clip(x, 0, self.width - 1))

        for dy in range(-STROKE_RADIUS, STROKE_RADIUS + 1):
            for dx in range(-STROKE_RADIUS, STROKE_RADIUS + 1):
                ny = y + dy
                nx = x + dx
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= STROKE_RADIUS:
                        # Gaussian falloff for both color and height
                        strength = np.exp(-(dist**2) / (STROKE_RADIUS**2 * 0.5))

                        # Blend color
                        self.color[ny, nx] = (
                            self.color[ny, nx] * (1 - strength) + np.array(color) * strength
                        )

                        # Add height with falloff
                        self.height_map[ny, nx] += paint_height * strength * 0.1

    def compute_normals(self) -> np.ndarray:
        """Compute surface normals from height map using Sobel operator."""
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)

        # Pad height map
        h_padded = np.pad(self.height_map * HEIGHT_SCALE, 1, mode="edge")

        # Compute gradients
        gx = np.zeros_like(self.height_map)
        gy = np.zeros_like(self.height_map)

        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                region = h_padded[y - 1 : y + 2, x - 1 : x + 2]
                gx[y - 1, x - 1] = np.sum(region * sobel_x)
                gy[y - 1, x - 1] = np.sum(region * sobel_y)

        # Normal: (-gx, -gy, 1)
        normals = np.zeros((self.height, self.width, 3), dtype=np.float32)
        normals[:, :, 0] = -gx * 0.01
        normals[:, :, 1] = -gy * 0.01
        normals[:, :, 2] = 1.0

        # Normalize
        norms = np.linalg.norm(normals, axis=2, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normals = normals / norms

        return normals

    def render_with_lighting(self) -> np.ndarray:
        """Render with directional lighting based on surface normals."""
        normals = self.compute_normals()

        # Compute diffuse light
        light_dir = LIGHT_DIRECTION.reshape(1, 1, 3)
        diffuse = np.clip(np.sum(normals * light_dir, axis=2, keepdims=True), 0, 1)

        # Ambient + diffuse
        lighting = AMBIENT_LIGHT + (1 - AMBIENT_LIGHT) * diffuse

        # Apply lighting to color
        shaded = self.color * lighting

        # Add specular highlight for glossy effect
        view_dir = np.array([0, 0, 1]).reshape(1, 1, 3)
        reflect_dir = 2 * np.sum(normals * light_dir, axis=2, keepdims=True) * normals - light_dir
        specular = np.clip(np.sum(reflect_dir * view_dir, axis=2, keepdims=True), 0, 1) ** 8
        specular = specular * (np.sum(self.color, axis=2, keepdims=True) > 0).astype(np.float32)

        shaded = shaded + specular * 50

        return np.clip(shaded, 0, 255).astype(np.uint8)

    def clear(self) -> None:
        """Clear canvas."""
        self.color[:] = 0
        self.height_map[:] = 0


canvas = ImpastoCanvas(CANVAS_WIDTH, CANVAS_HEIGHT)
current_color = (255, 100, 100)


def setup() -> None:
    py5.size(CANVAS_WIDTH, CANVAS_HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    # Render with lighting
    img = canvas.render_with_lighting()
    py5.image(py5.create_image_from_numpy(img), 0, 0)

    # Draw info
    py5.fill(255)
    py5.text_size(12)
    py5.text(
        "Impasto Rendering | Drag: paint | 1-3: color | s: save | c: clear",
        10,
        py5.height - 10,
    )
    py5.fill(*current_color)
    py5.rect(10, py5.height - 30, 20, 20)


def mouse_dragged() -> None:
    canvas.add_stroke(py5.mouse_x, py5.mouse_y, current_color)


def key_pressed() -> None:
    global current_color

    if py5.key == "1":
        current_color = (255, 100, 100)  # Red
    elif py5.key == "2":
        current_color = (100, 150, 255)  # Blue
    elif py5.key == "3":
        current_color = (100, 255, 150)  # Green
    elif py5.key == "c":
        canvas.clear()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "impasto_rendering_####.png"))


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
