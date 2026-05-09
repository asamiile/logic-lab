"""Lorenz attractor - chaotic 3D system revealing fractal structure."""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Lorenz parameters (classic chaotic regime)
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0
DT = 0.01

# Initial conditions
x, y, z = 0.1, 0.0, 0.0
trail = []
max_trail_length = 5000

# Visualization
rotation_x = 0.5
rotation_z = 0.0
zoom = 0.015


def setup() -> None:
    py5.size(800, 600, py5.P3D)
    py5.color_mode(py5.HSB, 360, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global x, y, z, trail, rotation_x, rotation_z

    # Lorenz equations
    dx = SIGMA * (y - x)
    dy = x * (RHO - z) - y
    dz = x * y - BETA * z

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
    py5.rotate_z(rotation_z)
    rotation_z += 0.002

    # Draw trail
    py5.no_fill()
    py5.stroke_weight(1)

    for i in range(len(trail) - 1):
        x1, y1, z1 = trail[i]
        x2, y2, z2 = trail[i + 1]

        # Color by position along trail (hue from z-coordinate)
        hue = (z + 50) % 360
        py5.stroke(hue, 80, 100)

        py5.line(
            x1 * zoom,
            y1 * zoom,
            z1 * zoom,
            x2 * zoom,
            y2 * zoom,
            z2 * zoom,
        )

    # Draw current point
    py5.fill(0, 100, 100)
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
    py5.text(f"Lorenz Attractor | Points: {len(trail)}", 10, 20)
    py5.text("σ=10, ρ=28, β=8/3", 10, 40)


def key_pressed() -> None:
    global trail, rotation_x, rotation_z, zoom

    if py5.key == " ":
        trail.clear()
    elif py5.key == "r":
        rotation_x = 0.5
        rotation_z = 0.0
    elif py5.key == "z":
        zoom *= 1.1
    elif py5.key == "x":
        zoom /= 1.1
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "lorenz_attractor_####.png"))


py5.run_sketch()
