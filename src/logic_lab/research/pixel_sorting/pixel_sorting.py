"""Pixel Sorting - Glitch art by sorting pixels along scan lines."""

from pathlib import Path

import numpy as np

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required for pixel_sorting")
    print("Install with: pip install pillow")
    exit(1)

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class PixelSorter:
    def __init__(self, image_path: str | None = None):
        """Initialize with optional image path. If None, uses a gradient."""
        self.original = None
        self.sorted_img = None
        self.mode = "horizontal"  # horizontal or vertical
        self.threshold = 50  # Brightness threshold for sorting

        if image_path and Path(image_path).exists():
            self.load_image(image_path)
        else:
            self.create_test_gradient()

    def create_test_gradient(self):
        """Create a simple test gradient image."""
        width, height = 640, 480
        img = np.zeros((height, width, 3), dtype=np.uint8)

        for y in range(height):
            for x in range(width):
                # Rainbow gradient
                hue = (x / width) * 360
                saturation = 100
                brightness = 100
                # Simple HSV to RGB (approximate)
                rgb = self._hsv_to_rgb(hue, saturation, brightness)
                img[y, x] = rgb

        self.original = img
        self.sort_pixels()

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB (0-360, 0-100, 0-100 -> 0-255)."""
        h = h / 60.0
        s = s / 100.0
        v = v / 100.0

        c = v * s
        x = c * (1 - abs(h % 2 - 1))
        m = v - c

        if h < 1:
            r, g, b = c, x, 0
        elif h < 2:
            r, g, b = x, c, 0
        elif h < 3:
            r, g, b = 0, c, x
        elif h < 4:
            r, g, b = 0, x, c
        elif h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return np.array([int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)])

    def load_image(self, path: str):
        """Load image from file."""
        img = Image.open(path)
        img = img.convert("RGB")
        self.original = np.array(img)
        self.sort_pixels()

    def sort_pixels(self):
        """Sort pixels by brightness along scan lines."""
        if self.original is None:
            return

        self.sorted_img = self.original.copy()
        height, width, _ = self.original.shape

        if self.mode == "horizontal":
            # Sort each row
            for y in range(height):
                row = self.sorted_img[y]
                brightness = np.mean(row, axis=1)

                # Find sorting regions (above threshold)
                regions = []
                in_region = False
                start = 0
                for x in range(width):
                    is_bright = brightness[x] > self.threshold
                    if is_bright and not in_region:
                        start = x
                        in_region = True
                    elif not is_bright and in_region:
                        regions.append((start, x))
                        in_region = False
                if in_region:
                    regions.append((start, width))

                # Sort each region by brightness
                for start, end in regions:
                    region = row[start:end]
                    region_brightness = np.mean(region, axis=1)
                    sorted_indices = np.argsort(region_brightness)
                    row[start:end] = region[sorted_indices]

        elif self.mode == "vertical":
            # Sort each column
            for x in range(width):
                column = self.sorted_img[:, x]
                brightness = np.mean(column, axis=1)

                regions = []
                in_region = False
                start = 0
                for y in range(height):
                    is_bright = brightness[y] > self.threshold
                    if is_bright and not in_region:
                        start = y
                        in_region = True
                    elif not is_bright and in_region:
                        regions.append((start, y))
                        in_region = False
                if in_region:
                    regions.append((start, height))

                for start, end in regions:
                    region = column[start:end]
                    region_brightness = np.mean(region, axis=1)
                    sorted_indices = np.argsort(region_brightness)
                    column[start:end] = region[sorted_indices]

    def get_display_image(self) -> np.ndarray:
        """Return current display image."""
        return self.sorted_img if self.sorted_img is not None else self.original


sorter = PixelSorter()
paused = False


def setup() -> None:
    img = sorter.get_display_image()
    py5.size(img.shape[1], img.shape[0])
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    img = sorter.get_display_image()
    if img is not None:
        py5.image(py5.create_image(img.shape[1], img.shape[0], py5.RGB), 0, 0)
        img_resized = py5.create_image(img.shape[1], img.shape[0], py5.RGB)
        img_resized.load_pixels()
        for i, pixel in enumerate(img.flatten().reshape(-1, 3)):
            img_resized.pixels[i] = py5.color(*pixel)
        img_resized.update_pixels()
        py5.image(img_resized, 0, 0)

    # Info
    py5.fill(255)
    py5.text_align(py5.LEFT)
    py5.text_size(12)
    py5.text(
        f"Pixel Sorting | Mode: {sorter.mode} | Threshold: {sorter.threshold}",
        10,
        py5.height - 10,
    )
    py5.text("h: horizontal | v: vertical | +/-: threshold | s: save", 10, py5.height - 25)


def key_pressed() -> None:
    if py5.key == "h":
        sorter.mode = "horizontal"
        sorter.sort_pixels()
    elif py5.key == "v":
        sorter.mode = "vertical"
        sorter.sort_pixels()
    elif py5.key == "+":
        sorter.threshold = min(255, sorter.threshold + 10)
        sorter.sort_pixels()
    elif py5.key == "-":
        sorter.threshold = max(0, sorter.threshold - 10)
        sorter.sort_pixels()
    elif py5.key == "s":
        if sorter.sorted_img is not None:
            img = Image.fromarray(sorter.sorted_img)
            img.save(SCREENSHOT_DIR / "pixel_sorting_sorted.png")
            print(f"Saved to {SCREENSHOT_DIR / 'pixel_sorting_sorted.png'}")


py5.run_sketch()
