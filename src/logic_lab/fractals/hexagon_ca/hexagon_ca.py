from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

w = 20.0
h = 0.0
rows = 0
columns = 0
board: list[list[int]] = []


def create_2d_array(row_count: int, column_count: int) -> list[list[int]]:
    arr = [[0 for _ in range(column_count)] for _ in range(row_count)]
    return arr


def setup() -> None:
    global w, h, columns, rows, board
    py5.size(640, 240)
    w = 20.0
    h = py5.sin(py5.PI / 3) * w
    columns = py5.floor((py5.width / w) * 3)
    rows = py5.floor(py5.height / h) + 2
    board = create_2d_array(columns, rows)
    for i in range(columns):
        for j in range(rows):
            board[i][j] = py5.floor(py5.random(2))

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(220)

    for i in range(columns):
        for j in range(rows):
            x = i * w * 3
            y = j * h
            if j % 2 == 0:
                x += 1.5 * w
            py5.fill(255 - board[i][j] * 255)
            draw_hexagon(x, y, w)


def draw_hexagon(x: float, y: float, r: float) -> None:
    py5.push_matrix()
    py5.translate(x, y)
    py5.stroke(0)
    py5.begin_shape()
    angle = 0.0
    while angle < py5.TWO_PI:
        xoff = py5.cos(angle) * r
        yoff = py5.sin(angle) * r
        py5.vertex(xoff, yoff)
        angle += py5.PI / 3
    py5.end_shape(py5.CLOSE)
    py5.pop_matrix()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "hexagon_ca_####.png"))


py5.run_sketch()
