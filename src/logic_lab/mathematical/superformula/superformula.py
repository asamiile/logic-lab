import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

PRESETS = [
    {"name": "petal", "m": 6.0, "n1": 1.0, "n2": 7.0, "n3": 8.0},
    {"name": "starfish", "m": 5.0, "n1": 0.32, "n2": 1.7, "n3": 1.7},
    {"name": "shell", "m": 7.0, "n1": 0.52, "n2": 0.92, "n3": 3.2},
    {"name": "crystal", "m": 8.0, "n1": 0.18, "n2": 1.7, "n3": 1.7},
    {"name": "leaf", "m": 3.0, "n1": 0.75, "n2": 4.5, "n3": 1.1},
]

preset_index = 0
layer_count = 12
animate_shape = True
show_points = False


def setup() -> None:
    py5.size(700, 700)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(218, 15, 97)
    py5.translate(py5.width / 2, py5.height / 2)

    t = py5.frame_count * 0.018 if animate_shape else 0.0
    draw_superformula_layers(t)

    py5.reset_matrix()
    draw_info()


def draw_superformula_layers(t: float) -> None:
    base = PRESETS[preset_index]
    max_radius = min(py5.width, py5.height) * 0.41

    for layer in range(layer_count, 0, -1):
        progress = layer / layer_count
        phase = t + layer * 0.23
        params = animated_params(base, progress, phase)
        scale = max_radius * (0.22 + 0.78 * progress)

        hue = (190 + preset_index * 34 + layer * 9 + t * 24) % 360
        py5.fill(hue, 58, 96 - progress * 28, 16)
        py5.stroke((hue + 24) % 360, 74, 48, 72)
        py5.stroke_weight(1.1 + progress * 1.4)

        points = superformula_points(params, scale)
        py5.begin_shape()
        for x, y in points:
            py5.vertex(x, y)
        py5.end_shape(py5.CLOSE)

        if show_points and layer == layer_count:
            py5.no_stroke()
            py5.fill(34, 92, 98, 92)
            for x, y in points[::12]:
                py5.circle(x, y, 4)


def animated_params(
    base: dict[str, float | str], progress: float, phase: float
) -> dict[str, float]:
    wobble = 0.0
    if animate_shape:
        wobble = math.sin(phase) * 0.12

    return {
        "m": float(base["m"]) + math.sin(phase * 0.7) * 0.16,
        "n1": max(0.08, float(base["n1"]) * (0.8 + progress * 0.4) + wobble),
        "n2": max(0.08, float(base["n2"]) * (0.9 + math.cos(phase) * 0.05)),
        "n3": max(0.08, float(base["n3"]) * (0.9 + math.sin(phase * 1.3) * 0.05)),
    }


def superformula_points(params: dict[str, float], scale: float) -> list[tuple[float, float]]:
    points = []
    steps = 420
    for i in range(steps):
        theta = py5.TWO_PI * i / steps
        radius = superformula_radius(
            theta,
            params["m"],
            params["n1"],
            params["n2"],
            params["n3"],
        )
        x = math.cos(theta) * radius * scale
        y = math.sin(theta) * radius * scale
        points.append((x, y))
    return points


def superformula_radius(theta: float, m: float, n1: float, n2: float, n3: float) -> float:
    a = 1.0
    b = 1.0
    part1 = abs(math.cos(m * theta / 4.0) / a) ** n2
    part2 = abs(math.sin(m * theta / 4.0) / b) ** n3
    value = (part1 + part2) ** (-1.0 / n1)
    return min(value, 8.0)


def draw_info() -> None:
    preset = PRESETS[preset_index]
    py5.no_stroke()
    py5.fill(218, 24, 12, 90)
    py5.rect(14, 14, 540, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"Superformula | {preset['name']} | layers {layer_count} | p: preset | +/-: layers | space: animate | d: points | s: save",
        24,
        46,
    )


def key_pressed() -> None:
    global preset_index, layer_count, animate_shape, show_points

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "superformula_####.png"))
    elif py5.key == "p":
        preset_index = (preset_index + 1) % len(PRESETS)
    elif py5.key == "+":
        layer_count = min(28, layer_count + 1)
    elif py5.key == "-":
        layer_count = max(1, layer_count - 1)
    elif py5.key == " ":
        animate_shape = not animate_shape
    elif py5.key == "d":
        show_points = not show_points


py5.run_sketch()
