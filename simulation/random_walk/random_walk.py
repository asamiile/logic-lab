import py5


class Walker:
    def __init__(self) -> None:
        self.x = py5.width / 2
        self.y = py5.height / 2

    def show(self) -> None:
        py5.stroke(0)
        py5.point(self.x, self.y)

    def step(self) -> None:
        choice = int(py5.random(4))

        if choice == 0:
            self.x += 1
        elif choice == 1:
            self.x -= 1
        elif choice == 2:
            self.y += 1
        else:
            self.y -= 1


walker: Walker


def setup() -> None:
    global walker
    py5.size(640, 240)
    walker = Walker()
    py5.background(255)


def draw() -> None:
    walker.step()
    walker.show()


py5.run_sketch()
