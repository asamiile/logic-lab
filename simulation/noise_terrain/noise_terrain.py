from pathlib import Path

import numpy as np
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


class Terrain:
    def __init__(self, scl: int, w: int, h: int) -> None:
        self.scl = scl
        self.w = w
        self.h = h
        self.cols = w // scl
        self.rows = h // scl
        self.z = np.zeros((self.cols, self.rows))
        self.zoff = 0.0

    def calculate(self) -> None:
        xx, yy = np.meshgrid(
            np.arange(self.cols) * 0.1,
            np.arange(self.rows) * 0.1,
            indexing="ij",
        )
        self.z = py5.noise(xx, yy, self.zoff) * 240 - 120
        self.zoff += 0.01

    def render(self) -> None:
        for x in range(self.cols - 1):
            py5.begin_shape(py5.QUAD_STRIP)
            for y in range(self.rows):
                elevation = self.z[x, y]
                shade = py5.remap(elevation, -120, 120, 0, 255)
                py5.stroke(0)
                py5.fill(shade, 255)
                x_coord = x * self.scl - self.w / 2
                y_coord = y * self.scl - self.h / 2
                py5.vertex(x_coord, y_coord, self.z[x, y])
                py5.vertex(x_coord + self.scl, y_coord, self.z[x + 1, y])
            py5.end_shape()


land: Terrain
theta = 0.0


def setup() -> None:
    global land
    py5.size(640, 240, py5.P3D)
    land = Terrain(20, 800, 400)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global theta
    land.calculate()
    py5.background(255)
    py5.push()
    py5.translate(0, 20, -200)
    py5.rotate_x(py5.PI / 3)
    py5.rotate_z(theta)
    land.render()
    py5.pop()
    theta += 0.0025


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "noise_terrain_####.png"))


py5.run_sketch()
