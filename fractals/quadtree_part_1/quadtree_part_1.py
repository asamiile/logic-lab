from pathlib import Path

import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

qtree: "QuadTree"


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x = x  # center x
        self.y = y  # center y
        self.w = w  # half-width
        self.h = h  # half-height

    def contains(self, point: Point) -> bool:
        return (self.x - self.w <= point.x < self.x + self.w and
                self.y - self.h <= point.y < self.y + self.h)

    def intersects(self, other: "Rectangle") -> bool:
        return not (other.x - other.w > self.x + self.w or
                    other.x + other.w < self.x - self.w or
                    other.y - other.h > self.y + self.h or
                    other.y + other.h < self.y - self.h)


class QuadTree:
    def __init__(self, boundary: Rectangle, capacity: int) -> None:
        self.boundary = boundary
        self.capacity = capacity
        self.points: list[Point] = []
        self.divided = False
        self.northeast: "QuadTree | None" = None
        self.northwest: "QuadTree | None" = None
        self.southeast: "QuadTree | None" = None
        self.southwest: "QuadTree | None" = None

    def subdivide(self) -> None:
        x, y = self.boundary.x, self.boundary.y
        w, h = self.boundary.w / 2, self.boundary.h / 2
        self.northeast = QuadTree(Rectangle(x + w, y - h, w, h), self.capacity)
        self.northwest = QuadTree(Rectangle(x - w, y - h, w, h), self.capacity)
        self.southeast = QuadTree(Rectangle(x + w, y + h, w, h), self.capacity)
        self.southwest = QuadTree(Rectangle(x - w, y + h, w, h), self.capacity)
        self.divided = True

    def insert(self, point: Point) -> bool:
        if not self.boundary.contains(point):
            return False
        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        if not self.divided:
            self.subdivide()
        return (self.northeast.insert(point) or  # type: ignore[union-attr]
                self.northwest.insert(point) or  # type: ignore[union-attr]
                self.southeast.insert(point) or  # type: ignore[union-attr]
                self.southwest.insert(point))    # type: ignore[union-attr]

    def query(self, query_range: Rectangle, found: list[Point] | None = None) -> list[Point]:
        if found is None:
            found = []
        if not self.boundary.intersects(query_range):
            return found
        for p in self.points:
            if query_range.contains(p):
                found.append(p)
        if self.divided:
            self.northwest.query(query_range, found)   # type: ignore[union-attr]
            self.northeast.query(query_range, found)   # type: ignore[union-attr]
            self.southwest.query(query_range, found)   # type: ignore[union-attr]
            self.southeast.query(query_range, found)   # type: ignore[union-attr]
        return found

    def show(self) -> None:
        py5.stroke(0)
        py5.no_fill()
        py5.stroke_weight(1)
        py5.rect_mode(py5.CENTER)
        b = self.boundary
        py5.rect(b.x, b.y, b.w * 2, b.h * 2)
        for p in self.points:
            py5.stroke_weight(1)
            py5.stroke(0)
            py5.point(p.x, p.y)
        if self.divided:
            self.northeast.show()  # type: ignore[union-attr]
            self.northwest.show()  # type: ignore[union-attr]
            self.southeast.show()  # type: ignore[union-attr]
            self.southwest.show()  # type: ignore[union-attr]


def setup() -> None:
    global qtree
    py5.size(640, 240)
    boundary = Rectangle(py5.width / 2, py5.height / 2, py5.width, py5.height)
    qtree = QuadTree(boundary, 8)
    for _ in range(2000):
        x = py5.random_gaussian(py5.width / 2, py5.width / 8)
        y = py5.random_gaussian(py5.height / 2, py5.height / 8)
        qtree.insert(Point(x, y))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(255)
    qtree.show()

    py5.rect_mode(py5.CENTER)
    query_rect = Rectangle(py5.mouse_x, py5.mouse_y, 50, 50)

    if py5.mouse_x < py5.width and py5.mouse_y < py5.height:
        py5.stroke_weight(2)
        py5.stroke(255, 50, 50)
        py5.fill(255, 50, 50, 50)
        py5.rect(query_rect.x, query_rect.y, query_rect.w * 2, query_rect.h * 2)

        points = qtree.query(query_rect)
        for p in points:
            py5.stroke_weight(3)
            py5.stroke(50, 50, 50)
            py5.point(p.x, p.y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "quadtree_part_1_####.png"))


py5.run_sketch()
