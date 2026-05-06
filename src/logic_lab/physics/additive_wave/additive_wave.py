from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

X_SPACING = 8
MAX_WAVES = 5

w = 0
theta = 0.0
amplitudes: list[float] = []
dx: list[float] = []
yvalues: list[float] = []


def setup() -> None:
    global w, amplitudes, dx, yvalues
    py5.size(640, 240)
    w = py5.width + 16

    amplitudes = []
    dx = []
    for _ in range(MAX_WAVES):
        amplitudes.append(py5.random(10, 30))
        period = py5.random(100, 300)
        dx.append((py5.TWO_PI / period) * X_SPACING)

    yvalues = [0.0] * int(w / X_SPACING)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def calc_wave() -> None:
    global theta
    theta += 0.02

    for i in range(len(yvalues)):
        yvalues[i] = 0

    for j in range(MAX_WAVES):
        x = theta
        for i in range(len(yvalues)):
            if j % 2 == 0:
                yvalues[i] += py5.sin(x) * amplitudes[j]
            else:
                yvalues[i] += py5.cos(x) * amplitudes[j]
            x += dx[j]


def render_wave() -> None:
    py5.stroke(0)
    py5.fill(0, 100)
    py5.ellipse_mode(py5.CENTER)

    for x, y in enumerate(yvalues):
        py5.circle(x * X_SPACING, py5.height / 2 + y, 32)


def draw() -> None:
    py5.background(255)
    calc_wave()
    render_wave()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "additive_wave_####.png"))


py5.run_sketch()
