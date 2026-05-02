from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

num_a = 10
num_b = 6
thr = 100.0
ratio = num_b / num_a
rand: list[float] = []
count = 0


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.no_loop()
    redraw_current()


def redraw_current() -> None:
    py5.redraw()


def draw() -> None:
    global count, ratio
    py5.background(1, 0, 1)
    ratio = num_b / num_a
    count = 0
    if ratio != 1:
        div_square(0, 0, py5.width)
    draw_status()


def draw_status() -> None:
    py5.fill(0)
    py5.no_stroke()
    py5.rect(0, 0, 205, 72)
    py5.fill(0, 0, 1)
    py5.text_size(12)
    py5.text(f"numA {num_a}  numB {num_b}  thr {int(thr)}", 10, 20)
    py5.text("A/Z numA  S/X numB  D/C thr", 10, 40)
    py5.text("R colors  P save", 10, 60)
    py5.stroke(0)


def set_color() -> None:
    global count
    if len(rand) <= count:
        rand.append(py5.random(1))
    py5.fill(rand[count], 1, 1)
    count += 1


def change_color() -> None:
    for i in range(len(rand)):
        rand[i] = py5.random(1)


def div_square(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = wd + x_pos
    y_end_pos = wd + y_pos
    set_color()
    py5.rect(x_pos, y_pos, wd, wd)

    while wd > thr:
        itr += 1
        if itr % 2 == 1:
            while x_pos + wd * ratio < x_end_pos + 0.1:
                div_rect(x_pos, y_pos, wd * ratio)
                x_pos += wd * ratio
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd / ratio < y_end_pos + 0.1:
                div_rect(x_pos, y_pos, wd)
                y_pos += wd / ratio
            wd = y_end_pos - y_pos


def div_rect(x_pos: float, y_pos: float, wd: float) -> None:
    itr = 0
    x_end_pos = x_pos + wd
    y_end_pos = y_pos + wd / ratio
    set_color()
    py5.rect(x_pos, y_pos, wd, wd / ratio)

    while wd > thr:
        itr += 1
        if itr % 2 == 0:
            while x_pos + wd < x_end_pos + 0.1:
                div_square(x_pos, y_pos, wd)
                x_pos += wd
            wd = x_end_pos - x_pos
        else:
            while y_pos + wd < y_end_pos + 0.1:
                div_square(x_pos, y_pos, wd)
                y_pos += wd
            wd = y_end_pos - y_pos


def key_pressed() -> None:
    global num_a, num_b, thr

    key = str(py5.key).lower()
    if key == "a":
        num_a = min(40, num_a + 1)
    elif key == "z":
        num_a = max(1, num_a - 1)
    elif key == "s":
        num_b = min(40, num_b + 1)
    elif key == "x":
        num_b = max(1, num_b - 1)
    elif key == "d":
        thr = min(300, thr + 10)
    elif key == "c":
        thr = max(10, thr - 10)
    elif key == "r":
        change_color()
    elif key == "p":
        py5.save_frame(str(SCREENSHOT_DIR / f"{num_a}_{num_b}_{int(thr)}_####.png"))
        return

    redraw_current()


py5.run_sketch()

