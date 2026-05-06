from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

gon = 10
curve_color = 0
ctr: list[tuple[float, float]] = []


def setup() -> None:
    py5.size(500, 500, py5.P2D)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.background(0, 0, 1)
    make_curve()
    draw_shape()
    py5.no_loop()


def make_curve() -> None:
    global curve_color, ctr
    v0 = (py5.width / 2, 0)
    v1 = (py5.cos(py5.PI / gon) * py5.width / 2, py5.sin(py5.PI / gon) * py5.width / 2)
    bases = [v0, v0, v1, v1]
    ctr = [(base[0] * py5.random(1), base[1] * py5.random(1)) for base in bases]
    curve_color = py5.color(py5.random(1), 1, 1)


def draw_shape() -> None:
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    for j in range(2):
        for k in range(gon):
            py5.push_matrix()
            py5.scale(1, pow(-1, j))
            py5.rotate(k * py5.TWO_PI / gon)
            draw_curve()
            py5.pop_matrix()
    py5.pop_matrix()


def draw_curve() -> None:
    py5.fill(curve_color)
    py5.begin_shape()
    py5.vertex(0, 0)
    py5.vertex(ctr[0][0], ctr[0][1])
    py5.bezier_vertex(ctr[1][0], ctr[1][1], ctr[2][0], ctr[2][1], ctr[3][0], ctr[3][1])
    py5.end_shape(py5.CLOSE)


def mouse_clicked() -> None:
    make_curve()
    draw_shape()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "symmetric_shape_####.png"))


py5.run_sketch()
