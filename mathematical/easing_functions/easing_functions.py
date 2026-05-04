from pathlib import Path
import py5
import math

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Easing functions: t in [0, 1] -> result in [0, 1]


def ease_in_quad(t: float) -> float:
    return t * t


def ease_out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t


def ease_in_cubic(t: float) -> float:
    return t * t * t


def ease_out_cubic(t: float) -> float:
    return 1 + (t - 1) ** 3


def ease_in_out_cubic(t: float) -> float:
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_in_sine(t: float) -> float:
    return 1 - math.cos((t * math.pi) / 2)


def ease_out_sine(t: float) -> float:
    return math.sin((t * math.pi) / 2)


def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def ease_in_expo(t: float) -> float:
    return 0 if t == 0 else 2 ** (10 * t - 10)


def ease_out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - 2 ** (-10 * t)


def ease_out_bounce(t: float) -> float:
    n1 = 7.5625
    d1 = 2.75

    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        return n1 * (t - 1.5 / d1) * (t - 1.5 / d1) + 0.75
    elif t < 2.5 / d1:
        return n1 * (t - 2.25 / d1) * (t - 2.25 / d1) + 0.9375
    else:
        return n1 * (t - 2.625 / d1) * (t - 2.625 / d1) + 0.984375


# List of easing functions for visualization
EASING_FUNCTIONS = [
    ("In Quad", ease_in_quad),
    ("Out Quad", ease_out_quad),
    ("In-Out Quad", ease_in_out_quad),
    ("In Cubic", ease_in_cubic),
    ("Out Cubic", ease_out_cubic),
    ("In-Out Cubic", ease_in_out_cubic),
    ("In Sine", ease_in_sine),
    ("Out Sine", ease_out_sine),
    ("In-Out Sine", ease_in_out_sine),
    ("In Expo", ease_in_expo),
    ("Out Expo", ease_out_expo),
    ("Out Bounce", ease_out_bounce),
]

# State
time_offset = 0
selected_index = 0


def setup() -> None:
    py5.size(640, 480)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global time_offset, selected_index
    py5.background(240)

    # Canvas dimensions
    margin = 40
    graph_x = margin
    graph_y = margin
    graph_w = py5.width - 2 * margin
    graph_h = py5.height - 2 * margin - 60

    # Draw grid
    py5.stroke(200)
    py5.stroke_weight(1)
    for i in range(0, 11):
        x = graph_x + (graph_w * i) // 10
        y = graph_y + (graph_h * i) // 10
        py5.line(x, graph_y, x, graph_y + graph_h)
        py5.line(graph_x, y, graph_x + graph_w, y)

    # Draw axes
    py5.stroke(0)
    py5.stroke_weight(2)
    py5.line(graph_x, graph_y + graph_h, graph_x + graph_w, graph_y + graph_h)
    py5.line(graph_x, graph_y, graph_x, graph_y + graph_h)

    # Draw easing curve
    name, func = EASING_FUNCTIONS[selected_index]
    py5.stroke(100, 150, 255)
    py5.stroke_weight(3)
    py5.no_fill()
    py5.begin_shape()
    for i in range(0, graph_w):
        t = i / graph_w
        y_val = func(t)
        x_pixel = graph_x + i
        y_pixel = graph_y + graph_h - (y_val * graph_h)
        py5.curve_vertex(x_pixel, y_pixel)
    py5.end_shape()

    # Draw animated dot
    t_anim = (time_offset % 1.0)
    y_anim = func(t_anim)
    x_anim = graph_x + (t_anim * graph_w)
    y_anim_pixel = graph_y + graph_h - (y_anim * graph_h)

    py5.fill(255, 100, 100)
    py5.no_stroke()
    py5.ellipse(x_anim, y_anim_pixel, 8, 8)

    # Draw labels
    py5.fill(0)
    py5.text_size(12)
    py5.text("0", graph_x - 20, graph_y + graph_h + 5)
    py5.text("1", graph_x + graph_w - 5, graph_y + graph_h + 5)
    py5.text_size(14)
    py5.text(name, 10, py5.height - 20)
    py5.text("← / →: Change | s: Save", 10, py5.height - 5)

    time_offset += 0.005


def key_pressed() -> None:
    global selected_index
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "easing_functions_####.png"))
    elif py5.key_code == py5.LEFT:
        selected_index = (selected_index - 1) % len(EASING_FUNCTIONS)
    elif py5.key_code == py5.RIGHT:
        selected_index = (selected_index + 1) % len(EASING_FUNCTIONS)


py5.run_sketch()
