from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def apply_wolfram_rule(row: list[int], rule: int) -> list[int]:
    new_row = [0] * len(row)
    for i in range(len(row)):
        left = row[(i - 1) % len(row)]
        center = row[i]
        right = row[(i + 1) % len(row)]

        pattern = left * 4 + center * 2 + right
        new_row[i] = (rule >> pattern) & 1

    return new_row


def setup() -> None:
    py5.size(1000, 800)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    draw_rules()


def draw_rules() -> None:
    py5.background(20)

    rules = [30, 90, 110, 184]
    cell_size = py5.height // len(rules)

    for rule_idx, rule in enumerate(rules):
        row = [0] * 100
        row[50] = 1

        for gen in range(cell_size):
            x_offset = rule_idx * (py5.width // len(rules))

            for i, cell in enumerate(row):
                if cell == 1:
                    py5.fill(100 + rule_idx * 40, 150, 255)
                    py5.stroke_weight(0)
                    py5.rect(x_offset + i * 2, gen, 2, 1)

            row = apply_wolfram_rule(row, rule)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "rule_variations_####.png"))


def draw() -> None:
    pass


py5.run_sketch()
