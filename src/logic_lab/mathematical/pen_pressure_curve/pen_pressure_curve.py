from dataclasses import dataclass
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Watercolor ink bleed parameters
BLEED_ENABLED = True
BLEED_RADIUS_SCALE = 3.5
BLEED_OPACITY_BASE = 0.08
BLEED_NOISE_SCALE = 0.018
BLEED_NOISE_OFFSET = 5000.0


def draw_bleed_halo(
    x1: float, y1: float, x2: float, y2: float, pressure: float, noise_t: float = 0.0
) -> None:
    """Draw a translucent Gaussian bleed halo along a line segment."""
    stroke_weight = 2 + pressure * 8
    base_radius = stroke_weight * BLEED_RADIUS_SCALE

    seg_len = max(1.0, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    steps = max(1, int(seg_len / 4))

    py5.no_stroke()
    BLEED_LAYERS = 5
    for layer in range(BLEED_LAYERS, 0, -1):
        t_layer = layer / BLEED_LAYERS
        layer_radius = base_radius * t_layer
        layer_alpha = BLEED_OPACITY_BASE * np.exp(-3.0 * (1.0 - t_layer) ** 2) * pressure

        for i in range(steps + 1):
            t = i / max(steps, 1)
            px = x1 + (x2 - x1) * t
            py_pos = y1 + (y2 - y1) * t

            noise_val = py5.noise(
                px * BLEED_NOISE_SCALE,
                py_pos * BLEED_NOISE_SCALE + BLEED_NOISE_OFFSET,
                noise_t,
            )
            perturb = 0.7 + 0.6 * noise_val
            r = layer_radius * perturb

            py5.fill(35, 30, 70, int(layer_alpha * 255))
            py5.ellipse(px, py_pos, r, r)


@dataclass
class PressurePoint:
    x: float
    y: float
    pressure: float = 0.5


class PressureCurveSimulation:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.points = []
        self.smoothed_points = []
        self.pressure_curve = []
        self.mouse_down = False

    def add_point(self, x, y, pressure):
        """Add a raw input point"""
        self.points.append(PressurePoint(x, y, pressure))

    def apply_kalman_filter(self):
        """Simple Kalman filter for pressure smoothing"""
        if len(self.points) < 2:
            return

        self.smoothed_points = []
        q = 0.01  # Process noise
        r = 1.0  # Measurement noise
        p = 1.0  # Estimate error
        x = self.points[0].pressure

        for point in self.points:
            p = p + q
            k = p / (p + r)
            x = x + k * (point.pressure - x)
            p = (1 - k) * p

            smoothed_point = PressurePoint(point.x, point.y, x)
            self.smoothed_points.append(smoothed_point)

    def apply_bezier_interpolation(self):
        """Smooth path using quadratic Bezier curves"""
        if len(self.smoothed_points) < 3:
            return self.smoothed_points

        interpolated = []
        for i in range(len(self.smoothed_points) - 2):
            p0 = self.smoothed_points[i]
            p1 = self.smoothed_points[i + 1]
            p2 = self.smoothed_points[i + 2]

            for t in np.linspace(0, 1, 5):
                x = (1 - t) ** 2 * p0.x + 2 * (1 - t) * t * p1.x + t**2 * p2.x
                y = (1 - t) ** 2 * p0.y + 2 * (1 - t) * t * p1.y + t**2 * p2.y
                pressure = (
                    (1 - t) ** 2 * p0.pressure + 2 * (1 - t) * t * p1.pressure + t**2 * p2.pressure
                )
                interpolated.append(PressurePoint(x, y, pressure))

        return interpolated

    def draw(self):
        py5.background(240)

        py5.stroke(150)
        py5.stroke_weight(1)
        py5.no_fill()
        for point in self.smoothed_points:
            py5.circle(point.x, point.y, 2)

        interpolated = self.apply_bezier_interpolation()
        if interpolated:
            self.smoothed_points = interpolated

        # --- Bleed pass (drawn first, underneath the main stroke) ---
        if BLEED_ENABLED and len(self.smoothed_points) > 1:
            noise_t = py5.frame_count * 0.003
            for i in range(len(self.smoothed_points) - 1):
                p1 = self.smoothed_points[i]
                p2 = self.smoothed_points[i + 1]
                draw_bleed_halo(p1.x, p1.y, p2.x, p2.y, p1.pressure, noise_t)

        py5.stroke_weight(1)
        for i in range(len(self.smoothed_points) - 1):
            p1 = self.smoothed_points[i]
            p2 = self.smoothed_points[i + 1]

            size = 2 + p1.pressure * 8
            py5.stroke_weight(size)
            py5.stroke(50)
            py5.line(p1.x, p1.y, p2.x, p2.y)

        py5.fill(0)
        py5.text_align(py5.LEFT)
        py5.text_size(12)
        py5.text("Draw with mouse - Pressure varies with Y-position", 10, 20)
        py5.text(f"Points: {len(self.points)}", 10, 40)
        py5.text("Press R to reset, S to save | b: toggle bleed", 10, 60)

    def reset(self):
        self.points = []
        self.smoothed_points = []

    def simulate_pressure(self, x, y):
        """Simulate pressure based on Y position"""
        normalized_y = y / self.height
        return max(0, min(1, 0.5 + np.sin(py5.frame_count * 0.02 + y * 0.01) * 0.3))


def setup():
    py5.size(800, 600)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    global simulation
    simulation = PressureCurveSimulation(py5.width, py5.height)


def draw():
    # Check if mouse button is pressed
    if py5.mouse_button == py5.LEFT:
        pressure = simulation.simulate_pressure(py5.mouse_x, py5.mouse_y)
        simulation.add_point(py5.mouse_x, py5.mouse_y, pressure)

    simulation.apply_kalman_filter()
    simulation.draw()


def key_pressed():
    global BLEED_ENABLED
    if py5.key == "r":
        simulation.reset()
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "pen_pressure_curve_####.png"))
    elif py5.key == "b":
        BLEED_ENABLED = not BLEED_ENABLED


if __name__ == "__main__":
    py5.run_sketch()
