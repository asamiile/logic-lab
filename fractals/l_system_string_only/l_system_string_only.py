from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
current = "A"


def setup() -> None:
    global current
    py5.size(640, 160)
    py5.background(255)
    py5.no_loop()

    for i in range(9):
        py5.text_size(16)
        py5.text_font(py5.create_font("courier", 16))
        py5.fill(0)
        py5.text(f"{i}: {current}", 4, 20 + i * 16)
        generate()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    pass


def generate() -> None:
    global current
    next_sentence = ""
    for c in current:
        if c == "A":
            next_sentence += "AB"
        elif c == "B":
            next_sentence += "A"
    current = next_sentence


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "l_system_string_only_####.png"))


py5.run_sketch()
