from pathlib import Path
import random as rand_module

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

bird: "Bird"
pipes = []


class Bird:
    def __init__(self) -> None:
        self.x = 50
        self.y = 120
        self.velocity = 0
        self.gravity = 0.5
        self.flap_force = -10

    def flap(self) -> None:
        self.velocity += self.flap_force

    def update(self) -> None:
        # Add gravity
        self.velocity += self.gravity
        self.y += self.velocity
        # Dampen velocity
        self.velocity *= 0.95

        # Handle the "floor"
        if self.y > py5.height:
            self.y = py5.height
            self.velocity = 0

    def show(self) -> None:
        py5.stroke_weight(2)
        py5.stroke(0)
        py5.fill(127)
        py5.circle(self.x, self.y, 16)


class Pipe:
    def __init__(self) -> None:
        self.spacing = 100
        self.top = rand_module.random() * (py5.height - self.spacing)
        self.bottom = self.top + self.spacing
        self.x = py5.width
        self.w = 20
        self.velocity = 2

    def collides(self, bird: Bird) -> bool:
        # Is the bird within the vertical range of the top or bottom pipe?
        vertical_collision = bird.y < self.top or bird.y > self.bottom
        # Is the bird within the horizontal range of the pipes?
        horizontal_collision = bird.x > self.x and bird.x < self.x + self.w
        # If it's both a vertical and horizontal hit, it's a hit!
        return vertical_collision and horizontal_collision

    def show(self) -> None:
        py5.fill(0)
        py5.no_stroke()
        py5.rect(self.x, 0, self.w, self.top)
        py5.rect(self.x, self.bottom, self.w, py5.height - self.bottom)

    def update(self) -> None:
        self.x -= self.velocity

    def offscreen(self) -> bool:
        return self.x < -self.w


def setup() -> None:
    global bird, pipes
    py5.size(640, 240)
    bird = Bird()
    pipes.append(Pipe())
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global bird, pipes

    py5.background(255)

    # Update and display pipes
    i = len(pipes) - 1
    while i >= 0:
        pipes[i].show()
        pipes[i].update()

        if pipes[i].collides(bird):
            py5.text("OOPS!", pipes[i].x, pipes[i].top + 20)

        if pipes[i].offscreen():
            pipes.pop(i)

        i -= 1

    # Update and display bird
    bird.update()
    bird.show()

    # Add new pipe every 100 frames
    if py5.frame_count % 100 == 0:
        pipes.append(Pipe())


def mouse_pressed() -> None:
    bird.flap()


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "flappy_bird_####.png"))


py5.run_sketch()
