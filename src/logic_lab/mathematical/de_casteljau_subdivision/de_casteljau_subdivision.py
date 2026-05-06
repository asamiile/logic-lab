from __future__ import annotations

from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

Point = tuple[float, float]

PRESETS: list[list[Point]] = [
    [(80, 560), (210, 90), (510, 130), (640, 560)],
    [(90, 520), (150, 150), (330, 600), (500, 80), (640, 500)],
    [(80, 500), (130, 140), (260, 580), (390, 120), (540, 560), (650, 220)],
]

control_points: list[Point] = []
preset_index = 0
t_value = 0.0
animate_t = True
show_curve = True
selected_index: int | None = None


def setup() -> None:
    py5.size(720, 640)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    load_preset()


def draw() -> None:
    global t_value

    py5.background(216, 14, 96)
    if animate_t:
        t_value = (t_value + 0.004) % 1.0

    if show_curve:
        draw_bezier_curve()
    draw_casteljau_levels(t_value)
    draw_control_polygon()
    draw_info()


def load_preset() -> None:
    global control_points, t_value, selected_index

    control_points = PRESETS[preset_index].copy()
    t_value = 0.0
    selected_index = None


def de_casteljau_levels(points: list[Point], t: float) -> list[list[Point]]:
    levels = [points]
    current = points
    while len(current) > 1:
        next_level = []
        for i in range(len(current) - 1):
            x1, y1 = current[i]
            x2, y2 = current[i + 1]
            next_level.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
        levels.append(next_level)
        current = next_level
    return levels


def evaluate_curve(t: float) -> Point:
    return de_casteljau_levels(control_points, t)[-1][0]


def draw_bezier_curve() -> None:
    py5.no_fill()
    py5.stroke(202, 72, 42, 32)
    py5.stroke_weight(7)
    py5.begin_shape()
    for i in range(260):
        x, y = evaluate_curve(i / 259)
        py5.vertex(x, y)
    py5.end_shape()

    py5.stroke(34, 86, 94, 96)
    py5.stroke_weight(2.4)
    py5.begin_shape()
    for i in range(260):
        x, y = evaluate_curve(i / 259)
        py5.vertex(x, y)
    py5.end_shape()


def draw_control_polygon() -> None:
    py5.no_fill()
    py5.stroke(220, 26, 26, 52)
    py5.stroke_weight(1.4)
    py5.begin_shape()
    for x, y in control_points:
        py5.vertex(x, y)
    py5.end_shape()

    py5.no_stroke()
    for i, (x, y) in enumerate(control_points):
        py5.fill(212, 66, 18, 88)
        py5.circle(x, y, 15)
        py5.fill(42, 94, 98, 100)
        py5.circle(x, y, 7)
        py5.fill(220, 28, 18, 88)
        py5.text(str(i), x + 10, y - 10)


def draw_casteljau_levels(t: float) -> None:
    levels = de_casteljau_levels(control_points, t)

    for level_index, points in enumerate(levels[1:], start=1):
        hue = (190 + level_index * 34) % 360
        py5.stroke(hue, 70, 42, 72)
        py5.stroke_weight(max(1.0, 3.2 - level_index * 0.32))
        py5.no_fill()
        py5.begin_shape()
        for x, y in points:
            py5.vertex(x, y)
        py5.end_shape()

        py5.no_stroke()
        for x, y in points:
            py5.fill(hue, 80, 92, 92)
            py5.circle(x, y, max(5, 12 - level_index))

    curve_point = levels[-1][0]
    py5.no_stroke()
    py5.fill(0, 0, 100, 100)
    py5.circle(curve_point[0], curve_point[1], 18)
    py5.fill(34, 96, 98, 100)
    py5.circle(curve_point[0], curve_point[1], 10)


def draw_info() -> None:
    degree = len(control_points) - 1
    py5.no_stroke()
    py5.fill(216, 24, 12, 90)
    py5.rect(14, 14, 625, 54, 4)
    py5.fill(0, 0, 100, 100)
    py5.text(
        f"De Casteljau subdivision | degree {degree} | t {t_value:.2f} | drag points | n: preset | space: animate | c: curve | s: save",
        24,
        46,
    )


def mouse_pressed() -> None:
    global selected_index

    selected_index = None
    for i, (x, y) in enumerate(control_points):
        if py5.dist(py5.mouse_x, py5.mouse_y, x, y) < 18:
            selected_index = i
            break


def mouse_dragged() -> None:
    if selected_index is not None:
        control_points[selected_index] = (py5.mouse_x, py5.mouse_y)


def mouse_released() -> None:
    global selected_index
    selected_index = None


def key_pressed() -> None:
    global preset_index, animate_t, show_curve

    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "de_casteljau_subdivision_####.png"))
    elif py5.key == "n":
        preset_index = (preset_index + 1) % len(PRESETS)
        load_preset()
    elif py5.key == " ":
        animate_t = not animate_t
    elif py5.key == "c":
        show_curve = not show_curve


py5.run_sketch()
