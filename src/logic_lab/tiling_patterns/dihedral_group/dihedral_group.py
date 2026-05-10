from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

img = None
gon = 6
scalar = 0.0
j_reflect = 1
k_rotate = 0


def setup() -> None:
    global img, scalar
    py5.size(300, 300)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    scalar = py5.height * 0.4
    img = py5.load_shape(str(Path(__file__).parent / "F.svg"))
    draw_shape()
    py5.no_loop()


def draw_shape() -> None:
    py5.background(200)
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)

    py5.push_matrix()
    py5.scale(1, j_reflect)
    py5.rotate(k_rotate * py5.TWO_PI / gon)
    py5.shape(img)
    py5.pop_matrix()

    py5.no_fill()
    py5.stroke(0)
    py5.begin_shape()
    for i in range(gon):
        angle = py5.TWO_PI * i / gon
        py5.vertex(py5.cos(angle) * scalar, py5.sin(angle) * scalar)
    py5.end_shape(py5.CLOSE)

    py5.fill(0)
    py5.text_size(20)
    for i in range(gon):
        ind = (j_reflect * i - k_rotate + 2 * gon) % gon
        angle = py5.TWO_PI * i / gon
        py5.text(str(ind), py5.cos(angle) * scalar, py5.sin(angle) * scalar)

    py5.pop_matrix()


def key_pressed() -> None:
    global j_reflect, k_rotate
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "dihedral_group_####.png"))
        return
    if py5.key == "f":
        j_reflect *= -1
    elif py5.key == "r":
        k_rotate = (k_rotate + j_reflect + gon) % gon
    elif py5.key == "e":
        k_rotate = 0
        j_reflect = 1
    draw_shape()


py5.run_sketch()
