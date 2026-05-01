from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Wave:
    def __init__(self, x: float, y: float, w: float, amplitude: float, period: float) -> None:
        self.xspacing = 8
        self.w = w
        self.origin = py5.Py5Vector(x, y)
        self.theta = 0.0
        self.amplitude = amplitude
        self.period = period
        self.dx = (py5.TWO_PI / self.period) * self.xspacing
        self.yvalues = [0.0] * int(py5.floor(self.w / self.xspacing))

    def update(self) -> None:
        self.theta += 0.02

        x = self.theta
        for i in range(len(self.yvalues)):
            self.yvalues[i] = py5.sin(x) * self.amplitude
            x += self.dx

    def show(self) -> None:
        for x, y in enumerate(self.yvalues):
            py5.stroke(0)
            py5.fill(0, 50)
            py5.circle(
                self.origin.x + x * self.xspacing,
                self.origin.y + y,
                48,
            )


wave0: Wave
wave1: Wave


def setup() -> None:
    global wave0, wave1
    py5.size(640, 240)
    wave0 = Wave(50, 75, 100, 20, 600)
    wave1 = Wave(300, 120, 300, 40, 180)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)

    wave0.update()
    wave0.show()

    wave1.update()
    wave1.show()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "oop_wave_####.png"))


py5.run_sketch()
