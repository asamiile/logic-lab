from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

COLUMN_A = 10
REP = 10
ROW_A = REP * COLUMN_A

mtx_a: list[list[int]] = []
mtx_b: list[list[int]] = []
mtx_c: list[list[int]] = []
mtx_p: list[list[int]] = []
scalar = 0.0
color_tate = 0
color_yoko = 0
sym = True


def setup() -> None:
    global mtx_a, mtx_b, mtx_c, scalar
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    mtx_a = zero_mtx(ROW_A, COLUMN_A)
    mtx_b = zero_mtx(COLUMN_A, COLUMN_A)
    repeat_mtx(mtx_a)
    randomize(mtx_b)
    mtx_c = tr_mtx(mtx_a)
    scalar = py5.height / (ROW_A + COLUMN_A)


def draw() -> None:
    global mtx_p
    mtx_p = mult_mtx(mult_mtx(mtx_a, tr_mtx(mtx_b)), mtx_c)

    py5.background(0, 0, 1)
    py5.stroke_weight(1)
    draw_table(mtx_a, 0, COLUMN_A, py5.color(0, 0, 0), py5.color(0, 0, 1))
    draw_table(mtx_b, 0, 0, py5.color(0, 0, 0), py5.color(0, 0, 1))
    draw_table(mtx_c, COLUMN_A, 0, py5.color(0, 0, 0), py5.color(0, 0, 1))
    draw_table(mtx_p, COLUMN_A, COLUMN_A, color_yoko, color_tate)

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
    py5.no_stroke()
    pos_y = y_cell * scalar
    for row in mtx:
        pos_x = x_cell * scalar
        for value in row:
            py5.fill(c2 if value == 0 else c1)
            py5.rect(pos_x, pos_y, scalar, scalar)
            pos_x += scalar
        pos_y += scalar


def repeat_mtx(mtx: list[list[int]]) -> None:
    for i in range(ROW_A):
        for j in range(COLUMN_A):
            mtx[i][j] = 0

    for i in range(ROW_A):
        if int(i / COLUMN_A) % 2 == 0:
            i_zigzag = i % COLUMN_A
        else:
            i_zigzag = COLUMN_A - (i % COLUMN_A) - 1
        mtx[i][i_zigzag] = 1


def randomize(mtx: list[list[int]]) -> None:
    global color_tate, color_yoko
    for i in range(len(mtx)):
        for j in range(len(mtx[0])):
            mtx[i][j] = int(py5.random(2))

    if sym:
        for i in range(len(mtx)):
            for j in range(i, len(mtx[0])):
                mtx[j][i] = mtx[i][j]

    color_tate = py5.color(py5.random(1), 1, 1)
    color_yoko = py5.color(py5.random(1), 1, 1)


def mouse_clicked() -> None:
    global sym
    sym = True
    randomize(mtx_b)


def key_pressed() -> None:
    global sym
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "textile_repeater_####.png"))
    else:
        sym = False
        randomize(mtx_b)


py5.run_sketch()

