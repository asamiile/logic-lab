from __future__ import annotations

import math
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

AIR_IOR = 1.0
GLASS_IOR = 1.52
beam_spread = 0.22
animate = True


def setup() -> None:
    py5.size(920, 620)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    py5.background(220, 28, 10)
    prism = prism_points()
    draw_prism(prism)
    origin = py5.Py5Vector(70, py5.height * 0.48)
    base_angle = (py5.mouse_y / max(1, py5.height) - 0.5) * 0.55 if py5.is_mouse_pressed else 0.02
    for i, hue in enumerate([0, 24, 48, 128, 205, 268]):
        wavelength_offset = (i - 2.5) * 0.006
        direction = py5.Py5Vector(math.cos(base_angle), math.sin(base_angle + wavelength_offset))
        trace_prism_ray(
            origin + py5.Py5Vector(0, (i - 2.5) * 5), direction, prism, hue, wavelength_offset
        )
    draw_beam_source(origin)


def prism_points() -> list[py5.Py5Vector]:
    return [
        py5.Py5Vector(py5.width * 0.47, py5.height * 0.19),
        py5.Py5Vector(py5.width * 0.31, py5.height * 0.74),
        py5.Py5Vector(py5.width * 0.67, py5.height * 0.7),
    ]


def trace_prism_ray(
    origin: py5.Py5Vector,
    direction: py5.Py5Vector,
    prism: list[py5.Py5Vector],
    hue: float,
    wavelength_offset: float,
) -> None:
    direction.normalize()
    first = nearest_polygon_hit(origin, direction, prism)
    if not first:
        draw_ray(origin, origin + direction * py5.width, hue, 38)
        return

    hit1, normal1 = first
    inside_ray = refract(direction, normal1, AIR_IOR, GLASS_IOR + wavelength_offset)
    if inside_ray is None:
        return
    second = nearest_polygon_hit(hit1 + inside_ray * 0.5, inside_ray, prism)
    if not second:
        return
    hit2, normal2 = second
    outside_ray = refract(inside_ray, normal2 * -1, GLASS_IOR + wavelength_offset, AIR_IOR)
    if outside_ray is None:
        outside_ray = reflect(inside_ray, normal2)

    draw_ray(origin, hit1, hue, 52)
    draw_ray(hit1, hit2, hue, 30)
    draw_ray(hit2, hit2 + outside_ray * 640, hue, 84)


def nearest_polygon_hit(
    origin: py5.Py5Vector, ray: py5.Py5Vector, points: list[py5.Py5Vector]
) -> tuple[py5.Py5Vector, py5.Py5Vector] | None:
    best = None
    best_distance = float("inf")
    center = sum(points, py5.Py5Vector(0, 0)) / len(points)
    for a, b in zip(points, points[1:] + points[:1]):
        hit = ray_segment_intersection(origin, ray, a, b)
        if hit and hit[1] < best_distance:
            edge = b - a
            normal = py5.Py5Vector(edge.y, -edge.x)
            normal.normalize()
            midpoint = (a + b) * 0.5
            if (center - midpoint).dot(normal) > 0:
                normal *= -1
            best = (hit[0], normal)
            best_distance = hit[1]
    return best


def ray_segment_intersection(
    origin: py5.Py5Vector, ray: py5.Py5Vector, a: py5.Py5Vector, b: py5.Py5Vector
) -> tuple[py5.Py5Vector, float] | None:
    vx, vy = b.x - a.x, b.y - a.y
    denom = ray.x * vy - ray.y * vx
    if abs(denom) < 1e-9:
        return None
    qx, qy = a.x - origin.x, a.y - origin.y
    t = (qx * vy - qy * vx) / denom
    u = (qx * ray.y - qy * ray.x) / denom
    if t > 0.001 and 0 <= u <= 1:
        return py5.Py5Vector(origin.x + ray.x * t, origin.y + ray.y * t), t
    return None


def refract(
    ray: py5.Py5Vector, normal: py5.Py5Vector, n1: float, n2: float
) -> py5.Py5Vector | None:
    cos_i = max(-1.0, min(1.0, -normal.dot(ray)))
    eta = n1 / n2
    k = 1.0 - eta * eta * (1.0 - cos_i * cos_i)
    if k < 0:
        return None
    result = ray * eta + normal * (eta * cos_i - math.sqrt(k))
    result.normalize()
    return result


def reflect(ray: py5.Py5Vector, normal: py5.Py5Vector) -> py5.Py5Vector:
    result = ray - normal * (2 * ray.dot(normal))
    result.normalize()
    return result


def draw_ray(a: py5.Py5Vector, b: py5.Py5Vector, hue: float, alpha: float) -> None:
    for weight, scale in ((10, 0.14), (4, 0.32), (1.4, 1.0)):
        py5.stroke(hue, 84, 100, alpha * scale)
        py5.stroke_weight(weight)
        py5.line(a.x, a.y, b.x, b.y)


def draw_prism(points: list[py5.Py5Vector]) -> None:
    py5.fill(190, 20, 96, 20)
    py5.stroke(190, 18, 100, 58)
    py5.stroke_weight(2)
    py5.begin_shape()
    for point in points:
        py5.vertex(point.x, point.y)
    py5.end_shape(py5.CLOSE)


def draw_beam_source(origin: py5.Py5Vector) -> None:
    py5.no_stroke()
    py5.fill(45, 86, 100, 82)
    py5.circle(origin.x, origin.y, 18)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "refraction_prism_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
