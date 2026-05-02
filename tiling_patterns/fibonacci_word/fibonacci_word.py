from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
word = "A"
generation = 0
history: list[tuple[int, str, int, int]] = []


def setup() -> None:
    py5.size(900, 500)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.text_font(py5.create_font("Monospaced", 16))
    transition()
    draw_state()
    py5.no_loop()


def transition() -> None:
    global word, generation
    num_a = word.split().count("A")
    num_b = word.split().count("B")
    print(f"{generation}: {word}")
    print(num_a, num_b)
    history.append((generation, word, num_a, num_b))

    next_symbols = ["A B" if symbol == "A" else "A" for symbol in word.split()]
    word = " ".join(next_symbols)
    generation += 1


def draw_state() -> None:
    py5.background(255)
    py5.fill(0)
    py5.text_size(16)
    y_pos = 28
    for gen, state, num_a, num_b in history[-14:]:
        visible = state
        if len(visible) > 84:
            visible = visible[:84] + " ..."
        py5.text(f"{gen:02d}  A:{num_a:3d}  B:{num_b:3d}  {visible}", 20, y_pos)
        y_pos += 32


def mouse_clicked() -> None:
    transition()
    draw_state()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "fibonacci_word_####.png"))


py5.run_sketch()
