from math import floor
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
RESOLUTION = 40

flock: "Flock"
grid: list[list[list["Boid"]]]
cols: int
rows: int


def limit_vector(v: py5.Py5Vector, max_val: float) -> py5.Py5Vector:
    mag_sq = v.x * v.x + v.y * v.y
    if mag_sq > max_val * max_val:
        scale = max_val / mag_sq**0.5
        return py5.Py5Vector(v.x * scale, v.y * scale)
    return v


def make_grid() -> list[list[list["Boid"]]]:
    return [[[] for _ in range(rows)] for _ in range(cols)]


class Boid:
    def __init__(self, x: float, y: float) -> None:
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(py5.random(-1, 1), py5.random(-1, 1))
        self.position = py5.Py5Vector(x, y)
        self.r = 3.0
        self.max_speed = 3.0
        self.max_force = 0.05

    def run(self) -> None:
        col = floor(self.position.x / RESOLUTION)
        row = floor(self.position.y / RESOLUTION)
        neighbors: list[Boid] = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                nc = col + i
                nr = row + j
                if 0 <= nc < cols and 0 <= nr < rows:
                    neighbors.extend(grid[nc][nr])
        self.flock(neighbors)
        self.update()
        self.borders()
        self.show()

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def flock(self, boids: list["Boid"]) -> None:
        sep = self.separate(boids)
        ali = self.align(boids)
        coh = self.cohesion(boids)
        sep *= 1.5
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)

    def update(self) -> None:
        self.velocity += self.acceleration
        self.velocity = limit_vector(self.velocity, self.max_speed)
        self.position += self.velocity
        self.acceleration *= 0

    def seek(self, target: py5.Py5Vector) -> py5.Py5Vector:
        desired = target - self.position
        if desired.mag > 0:
            desired = desired.norm * self.max_speed
        return limit_vector(desired - self.velocity, self.max_force)

    def show(self) -> None:
        py5.fill(127)
        py5.stroke(0)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.rotate(self.velocity.heading)
            py5.begin_shape()
            py5.vertex(self.r * 2, 0)
            py5.vertex(-self.r * 2, -self.r)
            py5.vertex(-self.r * 2, self.r)
            py5.end_shape(py5.CLOSE)

    def borders(self) -> None:
        r = self.r
        if self.position.x < -r:
            self.position.x = py5.width + r
        if self.position.y < -r:
            self.position.y = py5.height + r
        if self.position.x > py5.width + r:
            self.position.x = -r
        if self.position.y > py5.height + r:
            self.position.y = -r

    def separate(self, boids: list["Boid"]) -> py5.Py5Vector:
        desired_sq = 625.0  # 25.0 ** 2
        sx = sy = 0.0
        count = 0
        px, py_ = self.position.x, self.position.y
        for boid in boids:
            dx = px - boid.position.x
            dy = py_ - boid.position.y
            dist_sq = dx * dx + dy * dy
            if 0 < dist_sq < desired_sq:
                # normalize(diff) / distance == diff / dist_sq
                sx += dx / dist_sq
                sy += dy / dist_sq
                count += 1
        if count > 0:
            sx /= count
            sy /= count
        steer = py5.Py5Vector(sx, sy)
        if steer.mag > 0:
            steer = limit_vector(steer.norm * self.max_speed - self.velocity, self.max_force)
        return steer

    def align(self, boids: list["Boid"]) -> py5.Py5Vector:
        thresh_sq = 2500.0  # 50.0 ** 2
        sx = sy = 0.0
        count = 0
        px, py_ = self.position.x, self.position.y
        for boid in boids:
            dx = px - boid.position.x
            dy = py_ - boid.position.y
            if 0 < dx * dx + dy * dy < thresh_sq:
                sx += boid.velocity.x
                sy += boid.velocity.y
                count += 1
        if count > 0:
            avg = py5.Py5Vector(sx / count, sy / count)
            return limit_vector(avg.norm * self.max_speed - self.velocity, self.max_force)
        return py5.Py5Vector(0, 0)

    def cohesion(self, boids: list["Boid"]) -> py5.Py5Vector:
        thresh_sq = 2500.0  # 50.0 ** 2
        sx = sy = 0.0
        count = 0
        px, py_ = self.position.x, self.position.y
        for boid in boids:
            dx = px - boid.position.x
            dy = py_ - boid.position.y
            if 0 < dx * dx + dy * dy < thresh_sq:
                sx += boid.position.x
                sy += boid.position.y
                count += 1
        if count > 0:
            return self.seek(py5.Py5Vector(sx / count, sy / count))
        return py5.Py5Vector(0, 0)


class Flock:
    def __init__(self) -> None:
        self.boids: list[Boid] = []

    def run(self) -> None:
        for boid in self.boids:
            boid.run()

    def add_boid(self, boid: Boid) -> None:
        self.boids.append(boid)


def setup() -> None:
    global flock, grid, cols, rows
    py5.size(640, 240)
    cols = py5.width // RESOLUTION
    rows = py5.height // RESOLUTION
    grid = make_grid()
    flock = Flock()
    for _ in range(800):
        flock.add_boid(Boid(py5.random(py5.width), py5.random(py5.height)))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global grid
    py5.background(255)

    grid = make_grid()
    for boid in flock.boids:
        c = max(0, min(floor(boid.position.x / RESOLUTION), cols - 1))
        r = max(0, min(floor(boid.position.y / RESOLUTION), rows - 1))
        grid[c][r].append(boid)

    py5.stroke(200)
    py5.stroke_weight(1)
    for i in range(cols + 1):
        py5.line(i * RESOLUTION, 0, i * RESOLUTION, py5.height)
    for j in range(rows + 1):
        py5.line(0, j * RESOLUTION, py5.width, j * RESOLUTION)

    mc = floor(py5.mouse_x / RESOLUTION)
    mr = floor(py5.mouse_y / RESOLUTION)
    py5.no_stroke()
    py5.fill(255, 50, 50, 100)
    for i in range(-1, 2):
        for j in range(-1, 2):
            c = mc + i
            r = mr + j
            if 0 <= c < cols and 0 <= r < rows:
                py5.rect(c * RESOLUTION, r * RESOLUTION, RESOLUTION, RESOLUTION)

    flock.run()


def mouse_dragged() -> None:
    flock.add_boid(Boid(py5.mouse_x, py5.mouse_y))


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "flocking_with_binning_####.png"))


py5.run_sketch()
