from __future__ import annotations

from math import ceil, cos, pi, sin, sqrt

import py5


Point = tuple[float, float]


def rotate(point: Point, angle: float) -> Point:
    x_val, y_val = point
    return (
        x_val * cos(angle) - y_val * sin(angle),
        x_val * sin(angle) + y_val * cos(angle),
    )


def add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def mul(point: Point, scalar: float) -> Point:
    return (point[0] * scalar, point[1] * scalar)


def hex_vertices(scalar: float) -> list[Point]:
    radius = scalar / sqrt(3)
    return [(cos(2 * pi * i / 6) * radius, sin(2 * pi * i / 6) * radius) for i in range(6)]


def square_vertices(scalar: float) -> list[Point]:
    radius = scalar / sqrt(2)
    return [(cos(2 * pi * (i + 0.5) / 4) * radius, sin(2 * pi * (i + 0.5) / 4) * radius) for i in range(4)]


def hex_lattice(rows: int, scalar: float, height: float, ih02: bool = False) -> list[list[Point]]:
    base0 = (cos(pi / 2), sin(pi / 2))
    base1 = (cos(pi / 6), sin(pi / 6))
    denom = base1[0] - (1 / sqrt(3) if ih02 else 0)
    cols = ceil(rows / denom)
    return [
        [
            ((base0[0] * i + base1[0] * j) * scalar, ((base0[1] * i + base1[1] * j) * scalar) % (height + scalar))
            for j in range(cols + 1)
        ]
        for i in range(rows + 1)
    ]


def deformed_hex_lattice(rows: int, scalar: float, height: float, hor: float) -> list[list[Point]]:
    base0 = (cos(pi / 2), sin(pi / 2))
    base1 = (cos(pi / 6), sin(pi / 6))
    cols = ceil(rows / (base1[0] - 1 / sqrt(3)))
    return [
        [
            (
                (base0[0] * i + base1[0] * j) * scalar + hor * scalar * j / sqrt(3),
                ((base0[1] * i + base1[1] * j) * scalar) % (height + scalar),
            )
            for j in range(cols + 1)
        ]
        for i in range(rows + 1)
    ]


def square_lattice(num: int, scalar: float) -> list[list[Point]]:
    return [[(j * scalar, i * scalar) for j in range(num + 1)] for i in range(num + 1)]


def koch_points(start: Point, end: Point, upper_limit: int, convex: bool = True, itr: int = 0) -> list[Point]:
    if itr == upper_limit or itr > 5:
        return [start, end]

    direction = mul(sub(end, start), 1 / 3)
    slope = rotate(direction, pi / 3 if convex else -pi / 3)
    points = [
        start,
        add(start, direction),
        add(add(start, direction), slope),
        sub(end, direction),
        end,
    ]

    result: list[Point] = []
    for i in range(4):
        segment = koch_points(points[i], points[i + 1], upper_limit, convex, itr + 1)
        if result:
            result.extend(segment[1:])
        else:
            result.extend(segment)
    return result


def draw_poly(points: list[Point], fill_color: int | None = None) -> None:
    if fill_color is not None:
        py5.fill(fill_color)
    py5.begin_shape()
    for x_val, y_val in points:
        py5.vertex(x_val, y_val)
    py5.end_shape(py5.CLOSE)


def draw_bezier_poly(vertices: list[Point], mode: str, fill_color: int) -> None:
    rand_rows = 3 if len(vertices) == 6 else 2
    rand = [[py5.random(-1, 1), py5.random(-1, 1)] for _ in range(rand_rows)]

    py5.fill(fill_color)
    py5.begin_shape()
    py5.vertex(vertices[0][0], vertices[0][1])
    for i in range(len(vertices)):
        controls = parameterize(vertices, i, rand, mode)
        end = vertices[(i + 1) % len(vertices)]
        py5.bezier_vertex(controls[0][0], controls[0][1], controls[1][0], controls[1][1], end[0], end[1])
    py5.end_shape(py5.CLOSE)


def parameterize(vertices: list[Point], i: int, rand: list[list[float]], mode: str) -> list[Point]:
    n = len(vertices)
    result = []
    for j in range(2):
        vec = sub(vertices[(i + 1) % n], vertices[i])
        vec = mul(vec, pow(-1, j))
        if mode == "ih02":
            if i < 3:
                angle = rand[i][j] * pi / 3
            elif i != 4:
                angle = -rand[5 - i][j] * pi / 3
            else:
                angle = rand[5 - i][(j + 1) % 2] * pi / 3
        elif mode == "ih41":
            angle = rand[i % 2][j % 2] * pi / 4 if i < 2 else rand[i % 2][(j + 1) % 2] * pi / 4
        else:
            angle = rand[i % 3][j % 2] * pi / 3 if i < 3 else rand[i % 3][(j + 1) % 2] * pi / 3
        result.append(add(rotate(vec, angle), vertices[(i + j) % n]))
    return result


def tv08_vertices(scalar: float, hor: float, ver: float) -> list[Point]:
    vertices = hex_vertices(scalar)
    result = []
    for i, point in enumerate(vertices):
        x_val, y_val = point
        if i % 3 == 0:
            x_val *= 1 + hor
            y_val *= 1 + hor
        y_val += (-0.5 if 1 < i < 5 else 0.5) * ver * scalar / sqrt(3)
        result.append((x_val, y_val))
    return result


def draw_tiling(lattice: list[list[Point]], draw_tile, mirror_by_column: bool = False) -> None:
    for i, row in enumerate(lattice):
        for j, point in enumerate(row):
            py5.push_matrix()
            py5.translate(point[0], point[1])
            if mirror_by_column:
                py5.scale(pow(-1, j), 1)
            draw_tile(i, j)
            py5.pop_matrix()

