from pathlib import Path

fractal: "FractalOrbits | None" = None

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class OrbitTrapFractal:
    def __init__(self, width=800, height=800):
        self.width = width
        self.height = height
        self.zoom = 1
        self.pan_x = -0.7
        self.pan_y = 0
        self.trap_type = "circle"
        self.max_iterations = 256

    def mandelbrot_orbit(self, cx, cy, max_iter):
        """Calculate orbit and minimum distances to trap shapes"""
        z = complex(0, 0)
        circle_trap = float("inf")
        cross_trap = float("inf")
        line_trap = float("inf")

        for i in range(max_iter):
            if abs(z) > 4:
                break

            # Circle trap (origin)
            circle_trap = min(circle_trap, abs(z))

            # Cross trap (axes)
            cross_trap = min(cross_trap, min(abs(z.real), abs(z.imag)))

            # Line trap (real axis)
            line_trap = min(line_trap, abs(z.imag))

            z = z * z + complex(cx, cy)

        return circle_trap, cross_trap, line_trap, i

    def pixel_to_complex(self, px, py):
        """Convert pixel coordinates to complex plane"""
        real = self.pan_x + (px / self.width - 0.5) * (3 / self.zoom)
        imag = self.pan_y + (py / self.height - 0.5) * (3 / self.zoom)
        return real, imag

    def get_color(self, px, py):
        """Calculate color based on orbit trap distance"""
        cx, cy = self.pixel_to_complex(px, py)
        circle, cross, line, iterations = self.mandelbrot_orbit(cx, cy, self.max_iterations)

        if self.trap_type == "circle":
            distance = circle
        elif self.trap_type == "cross":
            distance = cross
        else:  # line
            distance = line

        distance = np.sqrt(distance) * 50

        if distance > 255:
            distance = 255

        return int(distance), iterations

    def draw(self):
        """Render the orbit trap fractal"""
        py5.background(20)

        step = 4
        for y in range(0, self.height, step):
            for x in range(0, self.width, step):
                circle, cross, line, iterations = self.mandelbrot_orbit(
                    self.pixel_to_complex(x, y)[0],
                    self.pixel_to_complex(x, y)[1],
                    self.max_iterations,
                )

                if self.trap_type == "circle":
                    trap_dist = circle
                elif self.trap_type == "cross":
                    trap_dist = cross
                else:
                    trap_dist = line

                trap_dist = max(0.001, trap_dist)

                if self.trap_type == "circle":
                    hue = int(np.sqrt(trap_dist) * 80) % 256
                elif self.trap_type == "cross":
                    hue = int(trap_dist * 100) % 256
                else:
                    hue = int(np.log(trap_dist + 1) * 50) % 256

                py5.no_stroke()
                py5.fill(hue, 200, 240)
                py5.circle(x, y, 2)


def setup() -> None:
    py5.size(800, 800)
    py5.color_mode(py5.HSB, 256)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    global fractal
    fractal = OrbitTrapFractal(py5.width, py5.height)


def draw() -> None:
    fractal.draw()

    py5.fill(0)
    py5.text_align(py5.LEFT)
    py5.text_size(12)
    py5.text(f"Trap: {fractal.trap_type} | Zoom: {fractal.zoom:.2f}", 10, 20)
    py5.text("Keys: C=circle, X=cross, L=line", 10, 35)


def key_pressed() -> None:
    if py5.key == "c":
        fractal.trap_type = "circle"
    elif py5.key == "x":
        fractal.trap_type = "cross"
    elif py5.key == "l":
        fractal.trap_type = "line"
    elif py5.key == "+":
        fractal.zoom *= 1.5
    elif py5.key == "-":
        fractal.zoom /= 1.5
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "orbit_traps_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
