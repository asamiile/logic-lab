from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

num = 10
thr = 0
fibo: list[int] = []
SGN = [1, 1, -1, -1]


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.no_loop()
    py5.redraw()


def generate_fibo(ind: int) -> None:
    global fibo
    fibo = [0, 1]
    for i in range(1, ind):
        fibo.append(fibo[i - 1] + fibo[i])
    fibo.reverse()


def draw() -> None:
    generate_fibo(num)
    py5.background(0, 0, 1)
    div_square(0, 0, 0, 0, 1, 1)
    draw_status()


def draw_status() -> None:
    py5.no_stroke()
    py5.fill(0)
    py5.rect(0, 0, 190, 58)
    py5.fill(0, 0, 1)
    py5.text_size(12)
    py5.text(f"num {num}  thr {thr}", 10, 20)
    py5.text("A/Z num  S/X thr", 10, 40)
    py5.text("P save", 10, 55)
    py5.stroke(0)


def color_rect(x_pos: float, y_pos: float, wd: float, ht: float, ind: int) -> None:
    scalar = py5.width / fibo[0]
    py5.fill((ind / num) % 1, 1, 1)
    py5.rect(scalar * x_pos, scalar * y_pos, scalar * wd, scalar * ht)


def div_rect(x_pos: float, y_pos: float, ind: int, itr: int, sgn_x: int, sgn_y: int) -> None:
    for i in range(num - ind):
        lng = fibo[i + ind]
        new_sgn_x = sgn_x * SGN[(i + 1) % 4]
        new_sgn_y = sgn_y * SGN[i % 4]
        color_rect(x_pos, y_pos, new_sgn_x * lng, new_sgn_y * lng, ind + i)
        x_pos += new_sgn_x * lng
        y_pos += new_sgn_y * lng
        if itr < thr:
            div_square(x_pos, y_pos, ind + i, itr + 1, -new_sgn_x, -new_sgn_y)


def div_square(x_pos: float, y_pos: float, ind: int, itr: int, sgn_x: int, sgn_y: int) -> None:
    for i in range(num - ind):
        lng0 = fibo[i + ind + 1]
        lng1 = fibo[i + ind]
        new_sgn_x = sgn_x * SGN[i % 4]
        new_sgn_y = sgn_y * SGN[(i + 1) % 4]
        color_rect(x_pos, y_pos, new_sgn_x * lng0, new_sgn_y * lng1, ind + i + 1)
        x_pos += new_sgn_x * lng0
        y_pos += new_sgn_y * lng1
        if itr < thr:
            div_rect(x_pos, y_pos, ind + i + 1, itr + 1, -new_sgn_x, -new_sgn_y)


def key_pressed() -> None:
    global num, thr

    key = str(py5.key).lower()
    if key == "a":
        num = min(20, num + 1)
    elif key == "z":
        num = max(1, num - 1)
    elif key == "s":
        thr = min(9, thr + 1)
    elif key == "x":
        thr = max(0, thr - 1)
    elif key == "p":
        py5.save_frame(str(SCREENSHOT_DIR / f"{num}_{thr}_####.png"))
        return

    py5.redraw()


py5.run_sketch()
