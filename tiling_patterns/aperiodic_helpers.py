from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import py5

from tiling_patterns.pattern_helpers import Point, add, from_angle, mul, rotate, sub


PHI = (1 + sqrt(5)) / 2


def distance(a: Point, b: Point) -> float:
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def draw_polygon(points: list[Point], indices: list[int] | None = None, close: bool = True) -> None:
    py5.begin_shape()
    for index in indices if indices is not None else range(len(points)):
        py5.vertex(*points[index])
    if close:
        py5.end_shape(py5.CLOSE)
    else:
        py5.end_shape()


@dataclass
class Tri:
    vertices: list[Point]

    def update_thin_s(self) -> None:
        v0, v1, v2 = self.vertices
        v3 = add(mul(sub(v0, v2), 2 - PHI), v2)
        self.vertices = [v1, v2, v3]

    def div_thin_s(self, next_thin: list[Tri], next_fat: list[Tri]) -> None:
        v0, v1, v2 = self.vertices
        v3 = add(mul(sub(v0, v2), 2 - PHI), v2)
        next_thin.append(Tri([v1, v2, v3]))
        next_fat.append(Tri([v3, v0, v1]))

    def div_thin_l(self, next_thin: list[Tri], next_fat: list[Tri]) -> None:
        v0, v1, v2 = self.vertices
        v3 = add(mul(sub(v0, v2), 2 - PHI), v2)
        v4 = add(mul(sub(v1, v0), 1 / (PHI + 1)), v0)
        next_thin.append(Tri([v1, v4, v3]))
        next_thin.append(Tri([v1, v2, v3]))
        next_fat.append(Tri([v4, v3, v0]))

    def div_fat_l(self, next_thin: list[Tri], next_fat: list[Tri]) -> None:
        v0, v1, v2 = self.vertices
        v3 = add(mul(sub(v2, v1), 1 / (PHI + 1)), v1)
        v4 = add(mul(sub(v0, v2), 1 / PHI), v2)
        next_thin.append(Tri([v3, v0, v4]))
        next_fat.append(Tri([v3, v0, v1]))
        next_fat.append(Tri([v4, v2, v3]))

    def div_fat_s(self, next_thin: list[Tri], next_fat: list[Tri]) -> None:
        v0, v1, v2 = self.vertices
        v3 = add(mul(sub(v2, v1), 1 / (PHI + 1)), v1)
        next_thin.append(Tri([v2, v3, v0]))
        next_fat.append(Tri([v3, v0, v1]))

    def draw_triangle(self) -> None:
        draw_polygon(self.vertices)

    def draw_arc(self, rad_end: float) -> float:
        v0, _v1, v2 = self.vertices
        diam = 2 * distance(v0, v2)
        rad_start = rad_end - 3 * pi / 5
        py5.no_fill()
        py5.arc(v2[0], v2[1], diam, diam, rad_start, rad_end)
        return rad_start

    def draw_rhomb(self) -> None:
        draw_polygon(self.vertices, [1, 0, 2], close=False)

    def draw_kite_dart(self) -> None:
        draw_polygon(self.vertices, [0, 1, 2], close=False)

    def draw_pent_f(self, pent_color: int, star_color: int) -> None:
        v0, v1, v2 = self.vertices
        v3 = add(mul(sub(v1, v0), PHI - 1), v0)
        v4 = add(mul(sub(v2, v1), PHI / (PHI + 1)), v1)
        v5 = add(mul(sub(v0, v2), 0.5), v2)
        points = [v0, v1, v2, v3, v4, v5]
        py5.no_stroke()
        py5.fill(pent_color)
        draw_polygon(points, [0, 2, 4, 3], close=False)
        py5.fill(star_color)
        draw_polygon(points, [1, 3, 4], close=False)
        py5.no_fill()
        py5.stroke(0, 0, 0)
        draw_polygon(points, [3, 4, 5], close=False)

    def draw_pent_t(self, pent_color: int, star_color: int) -> None:
        v0, v1, v2 = self.vertices
        v3 = add(mul(sub(v1, v0), PHI - 1), v0)
        v4 = add(mul(sub(v2, v1), 1 - PHI / 2), v1)
        v5 = add(mul(sub(v0, v2), 0.5), v2)
        points = [v0, v1, v2, v3, v4, v5]
        py5.no_stroke()
        py5.fill(pent_color)
        draw_polygon(points, [0, 2, 4, 3], close=False)
        py5.fill(star_color)
        draw_polygon(points, [1, 3, 4], close=False)
        py5.no_fill()
        py5.stroke(0, 0, 0)
        draw_polygon(points, [4, 3, 5], close=False)


@dataclass
class Pent:
    vertices: list[Point]

    @classmethod
    def from_center_vertex(cls, center: Point, vertex: Point) -> Pent:
        direction = sub(vertex, center)
        vertices = [center]
        for i in range(1, 6):
            vertices.append(add(rotate(direction, 2 * i * pi / 5), center))
        return cls(vertices)

    def divide(self, next_pents: list[Pent]) -> None:
        center = self.vertices[0]
        w = add(rotate(mul(sub(self.vertices[1], center), PHI / (2 * PHI + 1)), pi / 5), center)
        next_pents.append(Pent.from_center_vertex(center, w))
        for i in range(1, 6):
            w = add(mul(sub(self.vertices[i], center), (PHI + 1) / (2 * PHI + 1)), center)
            next_pents.append(Pent.from_center_vertex(w, self.vertices[i]))

    def draw(self) -> None:
        draw_polygon(self.vertices, [1, 2, 3, 4, 5])


def initial_triangle(scalar: float) -> Tri:
    return Tri(
        [
            from_angle(3 * pi / 2, scalar),
            from_angle(7 * pi / 10, scalar),
            from_angle(3 * pi / 10, scalar),
        ]
    )


def initial_decagon(scalar: float) -> list[Tri]:
    result = []
    for i in range(10):
        v0 = (0.0, 0.0)
        v1 = from_angle(i * 2 * pi / 10, scalar)
        v2 = from_angle((i + 1) * 2 * pi / 10, scalar)
        result.append(Tri([v0, v1, v2] if i % 2 == 0 else [v0, v2, v1]))
    return result
