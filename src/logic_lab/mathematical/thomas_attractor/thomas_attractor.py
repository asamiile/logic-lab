"""Thomas attractor - produces a knot-like structure with elegant symmetry."""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Thomas parameters
B = 0.208186  # Sweet spot for knot formation
DT = 0.01

# Initial conditions
x, y, z = 0.1, 0.0, 0.0
trail = []
max_trail_length = 10000

# Visualization
rotation_x = 0.4
rotation_y = 0.0
rotation_z = 0.0
zoom = 0.08


def setup() -> None:
    py5.size(800, 600, py5.P3D)
    py5.color_mode(py5.HSB, 360, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global x, y, z, trail, rotation_x, rotation_y, rotation_z

    # Thomas equations (dissipative)
    dx = py5.sin(y) - B * x
    dy = py5.sin(z) - B * y
    dz = py5.sin(x) - B * z

    # Euler integration
    x += dx * DT
    y += dy * DT
    z += dz * DT

    trail.append((x, y, z))
    if len(trail) > max_trail_length:
        trail.pop(0)

    # Background
    py5.background(0)

    # Lighting
    py5.lights()

    # Camera and rotation
    py5.translate(py5.width / 2, py5.height / 2, 0)
    py5.rotate_x(rotation_x)
    py5.rotate_y(rotation_y)
    py5.rotate_z(rotation_z)
    rotation_y += 0.003
    rotation_z += 0.001

    # Draw trail
    py5.no_fill()
    py5.stroke_weight(1.2)

    for i in range(len(trail) - 1):
        x1, y1, z1 = trail[i]
        x2, y2, z2 = trail[i + 1]

        # Color by arc length (progress along trail)
        hue = (i / len(trail) * 360) % 360
        py5.stroke(hue, 85, 95)

        py5.line(
            x1 * zoom,
            y1 * zoom,
            z1 * zoom,
            x2 * zoom,
            y2 * zoom,
            z2 * zoom,
        )

    # Draw current point
    py5.fill(120, 100, 100)
    py5.no_stroke()
    py5.push_matrix()
    py5.translate(x * zoom, y * zoom, z * zoom)
    py5.sphere(2)
    py5.pop_matrix()

    # Info
    py5.camera()
    py5.no_lights()
    py5.fill(255)
    py5.text_align(py5.LEFT)
    py5.text_size(12)
    py5.text(f"Thomas Attractor | Points: {len(trail)}", 10, 20)
    py5.text(f"b={B:.6f} (knot formation)", 10, 40)


def key_pressed() -> None:
    global trail, rotation_x, rotation_y, rotation_z, zoom

    if py5.key == " ":
        trail.clear()
    elif py5.key == "r":
        rotation_x = 0.4
        rotation_y = 0.0
        rotation_z = 0.0
    elif py5.key == "z":
        zoom *= 1.1
    elif py5.key == "x":
        zoom /= 1.1
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "thomas_attractor_####.png"))


py5.run_sketch()
