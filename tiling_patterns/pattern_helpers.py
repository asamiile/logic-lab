from __future__ import annotations

from math import ceil, cos, pi, sin


Point = tuple[float, float]


def from_angle(angle: float, length: float = 1.0) -> Point:
    return (cos(angle) * length, sin(angle) * length)


def add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def mul(point: Point, scalar: float) -> Point:
    return (point[0] * scalar, point[1] * scalar)


def rotate(point: Point, angle: float) -> Point:
    x_val, y_val = point
    return (
        x_val * cos(angle) - y_val * sin(angle),
        x_val * sin(angle) + y_val * cos(angle),
    )


def hex_lattice(num: int, scalar: float, height: float) -> list[list[Point]]:
    base0 = from_angle(pi / 2)
    base1 = from_angle(pi / 6)
    cols = ceil(num / base1[0])
    return [
        [
            (
                (base0[0] * i + base1[0] * j) * scalar,
                ((base0[1] * i + base1[1] * j) * scalar) % (height + scalar),
            )
            for j in range(cols + 1)
        ]
        for i in range(num + 1)
    ]
