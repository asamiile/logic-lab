from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

img = None
use_reflection = False


def setup() -> None:
    global img
    py5.size(300, 300)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    img = py5.load_shape(str(Path(__file__).parent / "yosegiC6Part.svg"))
    draw_domain()
    py5.no_loop()


def draw_domain() -> None:
    py5.background(255)
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2)
    for j in range(2):
        for k in range(6):
            py5.push_matrix()
            if use_reflection:
                py5.scale(1, pow(-1, j))
            py5.rotate(k * py5.TWO_PI / 6)
            py5.shape(img)
            py5.pop_matrix()
    py5.pop_matrix()


def key_pressed() -> None:
    global img, use_reflection
    key = str(py5.key).lower()
    if key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fundamental_domain_####.png"))
        return
    if key == "c":
        img = py5.load_shape(str(Path(__file__).parent / "yosegiC6Part.svg"))
        use_reflection = False
    elif key == "d":
        img = py5.load_shape(str(Path(__file__).parent / "yosegiD6Part.svg"))
        use_reflection = True
    elif key == "h":
        img = py5.load_shape(str(Path(__file__).parent / "HelloWorld.svg"))
        use_reflection = False
    draw_domain()


py5.run_sketch()
