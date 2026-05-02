from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

ctr: list[tuple[float, float]] = []
STEP = 10
itr = 0


def setup() -> None:
    global ctr
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ctr = [(0, 0), (py5.width, 0), (py5.width, py5.height)]
    py5.no_fill()


def draw() -> None:
    global itr
    mid_pts = ctr
    while len(mid_pts) > 1:
        mid_pts = get_mid_points(mid_pts, itr / STEP)
        py5.stroke(len(mid_pts) / len(ctr), 1, 1)
        draw_line(mid_pts)

    itr += 1
    if itr > STEP:
        py5.stroke(0, 0, 0)
        py5.stroke_weight(1)
        py5.begin_shape()
        py5.vertex(0, 0)
        py5.quadratic_vertex(py5.width, 0, py5.width, py5.height)
        py5.end_shape()
        py5.no_loop()


def get_mid_points(points: list[tuple[float, float]], t: float) -> list[tuple[float, float]]:
    return [
        (points[i][0] + (points[i + 1][0] - points[i][0]) * t, points[i][1] + (points[i + 1][1] - points[i][1]) * t)
        for i in range(len(points) - 1)
    ]


def draw_line(points: list[tuple[float, float]]) -> None:
    if len(points) > 1:
        py5.stroke_weight(1)
        for i in range(len(points) - 1):
            py5.line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
    else:
        py5.stroke(0, 0, 0)
        py5.stroke_weight(8)
        py5.point(points[0][0], points[0][1])


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "quadratic_bezier_####.png"))


py5.run_sketch()

