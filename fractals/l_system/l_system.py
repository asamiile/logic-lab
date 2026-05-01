from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
lsystem: "LSystem"
turtle: "Turtle"


class LSystem:
    def __init__(self, axiom: str, rules: dict[str, str]) -> None:
        self.sentence = axiom
        self.ruleset = rules

    def generate(self) -> None:
        nextgen = ""
        for c in self.sentence:
            nextgen += self.ruleset[c] if c in self.ruleset else c
        self.sentence = nextgen


class Turtle:
    def __init__(self, length: float, angle: float) -> None:
        self.length = length
        self.angle = angle

    def render(self, sentence: str) -> None:
        py5.stroke(0)
        for c in sentence:
            if c == "F":
                py5.line(0, 0, 0, -self.length)
                py5.translate(0, -self.length)
            elif c == "G":
                py5.translate(0, -self.length)
            elif c == "+":
                py5.rotate(self.angle)
            elif c == "-":
                py5.rotate(-self.angle)
            elif c == "[":
                py5.push_matrix()
            elif c == "]":
                py5.pop_matrix()


def setup() -> None:
    global lsystem, turtle
    py5.size(640, 240)

    rules = {"F": "FF+[+F-F-F]-[-F+F+F]"}
    lsystem = LSystem("F", rules)
    turtle = Turtle(4, py5.radians(25))

    for _ in range(4):
        lsystem.generate()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    py5.translate(py5.width / 2, py5.height)
    turtle.render(lsystem.sentence)
    py5.no_loop()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "l_system_####.png"))


py5.run_sketch()
