from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

debug = False
path: "PathObj"
vehicles: list["Vehicle"] = []


def limit_vector(v: py5.Py5Vector, max_val: float) -> py5.Py5Vector:
    mag_sq = v.x * v.x + v.y * v.y
    if mag_sq > max_val * max_val:
        scale = max_val / mag_sq**0.5
        return py5.Py5Vector(v.x * scale, v.y * scale)
    return v


def get_normal_point(p: py5.Py5Vector, a: py5.Py5Vector, b: py5.Py5Vector) -> py5.Py5Vector:
    ap = p - a
    ab = b - a
    if ab.mag > 0:
        ab_norm = ab.norm
        scalar = ap.x * ab_norm.x + ap.y * ab_norm.y
        return a + ab_norm * scalar
    return py5.Py5Vector(a.x, a.y)


class PathObj:
    def __init__(self) -> None:
        self.radius = 20
        self.points: list[py5.Py5Vector] = []

    def add_point(self, x: float, y: float) -> None:
        self.points.append(py5.Py5Vector(x, y))

    def display(self) -> None:
        py5.stroke_join(py5.ROUND)
        py5.stroke(175)
        py5.stroke_weight(self.radius * 2)
        py5.no_fill()
        py5.begin_shape()
        for v in self.points:
            py5.vertex(v.x, v.y)
        py5.end_shape(py5.CLOSE)

        py5.stroke(0)
        py5.stroke_weight(1)
        py5.no_fill()
        py5.begin_shape()
        for v in self.points:
            py5.vertex(v.x, v.y)
        py5.end_shape(py5.CLOSE)


class Vehicle:
    def __init__(self, x: float, y: float, max_speed: float, max_force: float) -> None:
        self.position = py5.Py5Vector(x, y)
        self.r = 12.0
        self.max_speed = max_speed
        self.max_force = max_force
        self.acceleration = py5.Py5Vector(0, 0)
        self.velocity = py5.Py5Vector(max_speed, 0)

    def apply_behaviors(self, boids: list["Vehicle"], p: PathObj) -> None:
        f = self.follow(p)
        s = self.separate(boids)
        f *= 3
        s *= 1
        self.apply_force(f)
        self.apply_force(s)

    def apply_force(self, force: py5.Py5Vector) -> None:
        self.acceleration += force

    def run(self) -> None:
        self.update()
        self.render()

    def follow(self, p: PathObj) -> py5.Py5Vector:
        predict = self.velocity.norm * 25
        predict_pos = self.position + predict

        normal = None
        target = None
        world_record = 1_000_000.0
        n = len(p.points)

        for i in range(n):
            a = p.points[i]
            b = p.points[(i + 1) % n]

            normal_point = get_normal_point(predict_pos, a, b)

            if (
                normal_point.x < min(a.x, b.x)
                or normal_point.x > max(a.x, b.x)
                or normal_point.y < min(a.y, b.y)
                or normal_point.y > max(a.y, b.y)
            ):
                normal_point = py5.Py5Vector(b.x, b.y)
                a = p.points[(i + 1) % n]
                b = p.points[(i + 2) % n]

            ab = b - a
            d = (predict_pos - normal_point).mag
            if d < world_record:
                world_record = d
                normal = normal_point
                dir_vec = ab.norm * 25
                target = normal + dir_vec

        if debug and normal is not None and target is not None:
            py5.stroke(0)
            py5.fill(0)
            py5.line(self.position.x, self.position.y, predict_pos.x, predict_pos.y)
            py5.ellipse(predict_pos.x, predict_pos.y, 4, 4)
            py5.ellipse(normal.x, normal.y, 4, 4)
            py5.line(predict_pos.x, predict_pos.y, target.x, target.y)
            if world_record > p.radius:
                py5.fill(255, 0, 0)
            py5.no_stroke()
            py5.ellipse(target.x, target.y, 8, 8)

        if world_record > p.radius and target is not None:
            return self.seek(target)
        return py5.Py5Vector(0, 0)

    def separate(self, boids: list["Vehicle"]) -> py5.Py5Vector:
        desired_sq = (self.r * 2) ** 2
        sx = sy = 0.0
        count = 0
        px, py_ = self.position.x, self.position.y
        for other in boids:
            dx = px - other.position.x
            dy = py_ - other.position.y
            dist_sq = dx * dx + dy * dy
            if 0 < dist_sq < desired_sq:
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

    def render(self) -> None:
        py5.fill(75)
        py5.stroke(0)
        with py5.push_matrix():
            py5.translate(self.position.x, self.position.y)
            py5.ellipse(0, 0, self.r, self.r)


def new_path() -> PathObj:
    p = PathObj()
    offset = 30
    p.add_point(offset, offset)
    p.add_point(py5.width - offset, offset)
    p.add_point(py5.width - offset, py5.height - offset)
    p.add_point(py5.width / 2, py5.height - offset * 3)
    p.add_point(offset, py5.height - offset)
    return p


def new_vehicle(x: float, y: float) -> Vehicle:
    return Vehicle(x, y, py5.random(2, 4), 0.3)


def setup() -> None:
    global path
    py5.size(640, 240)
    path = new_path()
    for _ in range(120):
        vehicles.append(new_vehicle(py5.random(py5.width), py5.random(py5.height)))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(240)
    path.display()
    for v in vehicles:
        v.apply_behaviors(vehicles, path)
        v.run()


def key_pressed() -> None:
    global debug
    if py5.key == "d":
        debug = not debug
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "crowd_path_following_####.png"))


def mouse_pressed() -> None:
    vehicles.append(new_vehicle(py5.mouse_x, py5.mouse_y))


py5.run_sketch()
