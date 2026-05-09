"""Layered Paint Mixing - Multiple reaction-diffusion layers with color blending."""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Canvas parameters
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Layer parameters (each channel gets different diffusion rates)
LAYER_COUNT = 3
DT = 0.1
FEED_RATE = 0.055
KILL_RATE = 0.062

# Blending modes
BLEND_MODE = "screen"  # "screen", "multiply", "overlay", "normal"


class ReactionDiffusionLayer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.U = np.ones((height, width), dtype=np.float32)
        self.V = np.random.rand(height, width).astype(np.float32) * 0.1
        self.Du = 0.16
        self.Dv = 0.08

    def laplacian(self, grid: np.ndarray) -> np.ndarray:
        """Compute Laplacian using simple finite differences."""
        lap = np.zeros_like(grid)
        lap[1:-1, 1:-1] = (
            grid[:-2, 1:-1]
            + grid[2:, 1:-1]
            + grid[1:-1, :-2]
            + grid[1:-1, 2:]
            - 4 * grid[1:-1, 1:-1]
        )
        return lap

    def step(self) -> None:
        """Reaction-diffusion step."""
        lap_u = self.laplacian(self.U)
        lap_v = self.laplacian(self.V)

        uv2 = self.U * self.V * self.V
        self.U += (self.Du * lap_u - uv2 + FEED_RATE * (1 - self.U)) * DT
        self.V += (self.Dv * lap_v + uv2 - (KILL_RATE + FEED_RATE) * self.V) * DT

        self.U = np.clip(self.U, 0, 1)
        self.V = np.clip(self.V, 0, 1)

    def add_stimulus(self, x: int, y: int, radius: int = 10) -> None:
        """Add V stimulus at position."""
        y = int(np.clip(y, 0, self.height - 1))
        x = int(np.clip(x, 0, self.width - 1))

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                ny = y + dy
                nx = x + dx
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= radius:
                        strength = 1.0 - dist / radius
                        self.V[ny, nx] = min(1.0, self.V[ny, nx] + strength * 0.5)

    def clear(self) -> None:
        """Reset layer."""
        self.U = np.ones_like(self.U)
        self.V = np.random.rand(*self.U.shape) * 0.1


class LayeredPaintMixing:
    def __init__(self, width: int, height: int, layer_count: int = 3):
        self.width = width
        self.height = height
        self.layers = [ReactionDiffusionLayer(width, height) for _ in range(layer_count)]
        self.layer_colors = [
            (255, 100, 100),  # Red layer
            (100, 150, 255),  # Blue layer
            (100, 255, 150),  # Green layer
        ]
        self.active_layer = 0

    def step(self) -> None:
        """Update all layers."""
        for layer in self.layers:
            layer.step()

    def add_stimulus(self, x: int, y: int) -> None:
        """Add stimulus to active layer."""
        self.layers[self.active_layer].add_stimulus(x, y)

    def blend_layers(self, mode: str = "screen") -> np.ndarray:
        """Blend layers using specified mode."""
        # Normalize V values to 0-255
        layer_images = [(1 - layer.V) * 255 for layer in self.layers]  # Invert: high V = dark

        result = np.ones((self.height, self.width, 3), dtype=np.float32) * 255

        for img, color in zip(layer_images, self.layer_colors):
            colored = img[:, :, np.newaxis] * np.array(color) / 255.0

            if mode == "screen":
                # Screen blend: result = 1 - (1-a)*(1-b)
                result = 255 * (1 - (1 - result / 255) * (1 - colored / 255))
            elif mode == "multiply":
                # Multiply blend
                result = result * colored / 255
            elif mode == "overlay":
                # Overlay blend
                result = np.where(
                    result < 128,
                    2 * result * colored / 255,
                    255 - 2 * (255 - result) * (255 - colored) / 255,
                )
            elif mode == "normal":
                # Normal blend (top layer only)
                result = colored

        return np.clip(result, 0, 255).astype(np.uint8)

    def get_display_image(self) -> np.ndarray:
        """Get blended image for display."""
        return self.blend_layers(BLEND_MODE)

    def clear(self) -> None:
        """Clear all layers."""
        for layer in self.layers:
            layer.clear()


painting = LayeredPaintMixing(CANVAS_WIDTH, CANVAS_HEIGHT, LAYER_COUNT)


def setup() -> None:
    py5.size(CANVAS_WIDTH, CANVAS_HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    # Simulation step
    painting.step()

    # Render
    img = painting.get_display_image()
    py5.image(py5.create_image_from_numpy(img), 0, 0)

    # Draw info
    py5.fill(255)
    py5.text_size(12)
    py5.text(
        "Layered Paint Mixing | Drag: paint | 1-3: layer | b: blend mode | s: save | c: clear",
        10,
        py5.height - 10,
    )

    # Layer indicator
    for i, color in enumerate(painting.layer_colors):
        if i == painting.active_layer:
            py5.fill(255, 255, 0)
            py5.rect(10 + i * 30, py5.height - 30, 25, 25)
        py5.fill(*color)
        py5.rect(12 + i * 30, py5.height - 28, 21, 21)


def mouse_dragged() -> None:
    painting.add_stimulus(py5.mouse_x, py5.mouse_y)


def key_pressed() -> None:
    global BLEND_MODE

    if py5.key == "1":
        painting.active_layer = 0
    elif py5.key == "2":
        painting.active_layer = 1
    elif py5.key == "3":
        painting.active_layer = 2
    elif py5.key == "b":
        modes = ["screen", "multiply", "overlay", "normal"]
        current_idx = modes.index(BLEND_MODE)
        BLEND_MODE = modes[(current_idx + 1) % len(modes)]
        print(f"Blend mode: {BLEND_MODE}")
    elif py5.key == "c":
        painting.clear()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "layered_paint_mixing_####.png"))


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
