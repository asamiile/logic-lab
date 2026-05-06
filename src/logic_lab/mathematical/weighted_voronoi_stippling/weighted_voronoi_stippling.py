from pathlib import Path

import py5
import numpy as np
from scipy.spatial import Voronoi, cKDTree

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class WeightedVoronoiStippling:
    def __init__(self, width=800, height=800, num_points=500, iterations=5):
        self.width = width
        self.height = height
        self.num_points = num_points
        self.iterations = iterations
        self.source_image = None
        self.points = None
        self.weights = None
        self._generate_initial_points()

    def _generate_initial_points(self):
        """Initialize points randomly"""
        self.points = np.random.rand(self.num_points, 2)
        self.points[:, 0] *= self.width
        self.points[:, 1] *= self.height

    def _create_test_image(self):
        """Create a simple gradient image for testing"""
        image = np.zeros((self.height, self.width))
        cx, cy = self.width // 2, self.height // 2
        for y in range(self.height):
            for x in range(self.width):
                dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                image[y, x] = np.exp(-dist / 150)
        return image

    def _compute_weights(self):
        """Compute density weights from image"""
        if self.source_image is None:
            self.source_image = self._create_test_image()

        weights = np.zeros(self.num_points)
        for i, (x, y) in enumerate(self.points):
            ix = int(np.clip(x, 0, self.width - 1))
            iy = int(np.clip(y, 0, self.height - 1))
            weights[i] = self.source_image[iy, ix]

        return weights

    def relax(self):
        """Lloyd relaxation iteration"""
        self.weights = self._compute_weights()

        try:
            vor = Voronoi(self.points)
        except:
            return

        new_points = np.zeros_like(self.points)
        weighted_sum = np.zeros(self.num_points)

        for region_idx, region in enumerate(vor.point_region):
            indices = vor.regions[region]
            if len(indices) > 0 and -1 not in indices:
                centroid = vor.vertices[indices].mean(axis=0)
                new_points[region_idx] = centroid
                weighted_sum[region_idx] = 1

        mask = weighted_sum > 0
        self.points[mask] = new_points[mask]

        self.points = np.clip(self.points, 0, [self.width, self.height])

    def draw(self):
        py5.background(255)

        if self.source_image is not None:
            for y in range(0, self.height, 8):
                for x in range(0, self.width, 8):
                    intensity = self.source_image[y, x]
                    gray = int(intensity * 255)
                    py5.fill(gray)
                    py5.stroke(gray)
                    py5.rect(x, y, 8, 8)

        self.weights = self._compute_weights()

        py5.fill(0)
        py5.no_stroke()
        for i, (x, y) in enumerate(self.points):
            size = 1 + self.weights[i] * 8
            py5.circle(x, y, size)


def setup():
    py5.size(800, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    global stippling
    stippling = WeightedVoronoiStippling(py5.width, py5.height, num_points=400)


def draw():
    for _ in range(2):
        stippling.relax()

    stippling.draw()

    py5.fill(0)
    py5.text_align(py5.LEFT)
    py5.text("Weighted Voronoi Stippling - Lloyd Relaxation", 10, 20)


def key_pressed():
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "weighted_voronoi_stippling_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
