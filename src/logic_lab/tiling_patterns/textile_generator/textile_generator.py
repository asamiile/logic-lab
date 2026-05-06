from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

ROW_A = 20
COLUMN_A = 4
mtx_a: list[list[int]] = []
mtx_b: list[list[int]] = []
mtx_c: list[list[int]] = []
mtx_p: list[list[int]] = []
scalar = 0.0


def setup() -> None:
    global mtx_a, mtx_b, mtx_c, scalar
    py5.size(500, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    mtx_a = zero_mtx(ROW_A, COLUMN_A)
    mtx_b = zero_mtx(COLUMN_A, COLUMN_A)
    mtx_c = zero_mtx(COLUMN_A, ROW_A)
    scalar = py5.height / (ROW_A + COLUMN_A)


def draw() -> None:
    global mtx_p
    mtx_p = mult_mtx(mult_mtx(mtx_a, tr_mtx(mtx_b)), mtx_c)

    py5.background(255)
    py5.stroke_weight(1)
    draw_table(mtx_a, 0, COLUMN_A, py5.color(0), py5.color(255))
    draw_table(mtx_b, 0, 0, py5.color(0), py5.color(255))
    draw_table(mtx_c, COLUMN_A, 0, py5.color(0), py5.color(255))
    draw_table(mtx_p, COLUMN_A, COLUMN_A, py5.color(255, 0, 0), py5.color(255, 255, 0))

    py5.stroke(0)
    py5.stroke_weight(3)
    py5.line(0, scalar * COLUMN_A, py5.width, scalar * COLUMN_A)
    py5.line(scalar * COLUMN_A, 0, scalar * COLUMN_A, py5.height)


def zero_mtx(rows: int, cols: int) -> list[list[int]]:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def mult_mtx(mtx1: list[list[int]], mtx2: list[list[int]]) -> list[list[int]]:
    new_mtx = [[0 for _ in range(len(mtx2[0]))] for _ in range(len(mtx1))]
    for i in range(len(mtx1)):
        for j in range(len(mtx2[0])):
            total = 0
            for k in range(len(mtx2)):
                total += mtx1[i][k] * mtx2[k][j]
            new_mtx[i][j] = total
    return new_mtx


def tr_mtx(mtx: list[list[int]]) -> list[list[int]]:
    return [[mtx[i][j] for i in range(len(mtx))] for j in range(len(mtx[0]))]


def draw_table(mtx: list[list[int]], x_cell: float, y_cell: float, c1: int, c2: int) -> None:
    pos_y = y_cell * scalar
    for row in mtx:
        pos_x = x_cell * scalar
        for value in row:
            py5.fill(c2 if value == 0 else c1)
            py5.rect(pos_x, pos_y, scalar, scalar)
            pos_x += scalar
        pos_y += scalar


def mouse_clicked() -> None:
    x_cell = int(py5.mouse_x // scalar)
    y_cell = int(py5.mouse_y // scalar)

    if y_cell < COLUMN_A:
        if x_cell < COLUMN_A:
            mtx_b[y_cell][x_cell] = (mtx_b[y_cell][x_cell] + 1) % 2
        elif x_cell - COLUMN_A < ROW_A:
            mtx_c[y_cell][x_cell - COLUMN_A] = (mtx_c[y_cell][x_cell - COLUMN_A] + 1) % 2
    elif x_cell < COLUMN_A and y_cell - COLUMN_A < ROW_A:
        mtx_a[y_cell - COLUMN_A][x_cell] = (mtx_a[y_cell - COLUMN_A][x_cell] + 1) % 2


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "textile_generator_####.png"))


py5.run_sketch()
