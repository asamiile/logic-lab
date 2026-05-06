from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

fibo = [0, 1]


def setup() -> None:
    py5.size(500, 500)
    py5.color_mode(py5.HSB, 1)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_squares()
    py5.no_loop()


def draw_squares() -> None:
    x_pos = 0.0
    y_pos = 0.0
    next_fibo = fibo[-2] + fibo[-1]
    scalar = py5.width / next_fibo

    py5.background(0, 0, 1)

    for i in range(1, len(fibo)):
        py5.fill((0.1 * i) % 1, 1, 1)
        py5.rect(scalar * x_pos, scalar * y_pos, scalar * fibo[i], scalar * fibo[i])
        if i % 2 == 1:
            x_pos += fibo[i]
            y_pos -= fibo[i - 1]
        else:
            x_pos -= fibo[i - 1]
            y_pos += fibo[i]


def mouse_clicked() -> None:
    next_fibo = fibo[-2] + fibo[-1]
    fibo.append(next_fibo)
    print(next_fibo)
    draw_squares()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fibonacci_square_####.png"))


py5.run_sketch()
