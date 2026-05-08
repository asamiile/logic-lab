from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Mirror:
    ax: float
    ay: float
    bx: float
    by: float


mirrors: list[Mirror] = []
beam_angle = -0.54
animate_angle = True


def setup() -> None:
    py5.size(880, 680)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    build_mirrors()


def build_mirrors() -> None:
    global mirrors
    cx, cy = py5.width * 0.5, py5.height * 0.5
    mirrors = []
    for i in range(7):
        angle = py5.TWO_PI * i / 7 + 0.18
        radius = 224 + 38 * math.sin(i * 1.7)
        length = 126
        mx = cx + math.cos(angle) * radius
        my = cy + math.sin(angle) * radius * 0.82
        tangent = angle + py5.HALF_PI + math.sin(i) * 0.42
        mirrors.append(
            Mirror(
                mx - math.cos(tangent) * length * 0.5,
                my - math.sin(tangent) * length * 0.5,
                mx + math.cos(tangent) * length * 0.5,
                my + math.sin(tangent) * length * 0.5,
            )
        )
    mirrors.extend(
        [
            Mirror(42, 42, py5.width - 42, 42),
            Mirror(py5.width - 42, 42, py5.width - 42, py5.height - 42),
            Mirror(py5.width - 42, py5.height - 42, 42, py5.height - 42),
            Mirror(42, py5.height - 42, 42, 42),
        ]
    )


def draw() -> None:
    global beam_angle
    if animate_angle:
        beam_angle += 0.003
    py5.background(232, 36, 8)
    draw_mirrors()
    start = py5.Py5Vector(py5.width * 0.2, py5.height * 0.62)
    direction = py5.Py5Vector(math.cos(beam_angle), math.sin(beam_angle))
    path = trace_reflections(start, direction, 18)
    draw_path(path)


def trace_reflections(
    start: py5.Py5Vector, direction: py5.Py5Vector, max_bounces: int
) -> list[py5.Py5Vector]:
    path = [start.copy]
    origin = start.copy
    ray = direction.copy
    ray.normalize()
    last_mirror: Mirror | None = None
    for _ in range(max_bounces):
        best = None
        best_distance = float("inf")
        for mirror in mirrors:
            if mirror == last_mirror:
                continue
            hit = ray_mirror_intersection(origin, ray, mirror)
            if hit and hit[1] < best_distance:
                best = (mirror, hit[0])
                best_distance = hit[1]
        if not best:
            path.append(origin + ray * 1200)
            break
        mirror, hit_point = best
        path.append(hit_point)
        ray = reflected_vector(ray, mirror)
        origin = hit_point + ray * 0.2
        last_mirror = mirror
    return path


def ray_mirror_intersection(
    origin: py5.Py5Vector, ray: py5.Py5Vector, mirror: Mirror
) -> tuple[py5.Py5Vector, float] | None:
    vx = mirror.bx - mirror.ax
    vy = mirror.by - mirror.ay
    denom = ray.x * vy - ray.y * vx
    if abs(denom) < 1e-9:
        return None
    qx = mirror.ax - origin.x
    qy = mirror.ay - origin.y
    t = (qx * vy - qy * vx) / denom
    u = (qx * ray.y - qy * ray.x) / denom
    if t > 0.001 and 0 <= u <= 1:
        return py5.Py5Vector(origin.x + ray.x * t, origin.y + ray.y * t), t
    return None


def reflected_vector(ray: py5.Py5Vector, mirror: Mirror) -> py5.Py5Vector:
    tangent = py5.Py5Vector(mirror.bx - mirror.ax, mirror.by - mirror.ay)
    tangent.normalize()
    normal = py5.Py5Vector(-tangent.y, tangent.x)
    reflected = ray - normal * (2 * ray.dot(normal))
    reflected.normalize()
    return reflected


def draw_mirrors() -> None:
    py5.stroke(204, 18, 78, 82)
    py5.stroke_weight(5)
    for mirror in mirrors:
        py5.line(mirror.ax, mirror.ay, mirror.bx, mirror.by)
    py5.stroke(190, 8, 100, 34)
    py5.stroke_weight(1)
    for mirror in mirrors:
        py5.line(mirror.ax, mirror.ay, mirror.bx, mirror.by)


def draw_path(path: list[py5.Py5Vector]) -> None:
    for weight, alpha in ((16, 8), (7, 24), (2.2, 96)):
        py5.stroke(8, 92, 100, alpha)
        py5.stroke_weight(weight)
        py5.no_fill()
        py5.begin_shape()
        for point in path:
            py5.vertex(point.x, point.y)
        py5.end_shape()
    py5.no_stroke()
    for index, point in enumerate(path[1:-1], start=1):
        py5.fill((28 + index * 18) % 360, 82, 100, 70)
        py5.circle(point.x, point.y, 8)


def key_pressed() -> None:
    global animate_angle, beam_angle
    if py5.key == " ":
        animate_angle = not animate_angle
    elif py5.key == "r":
        beam_angle = -0.54
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "reflection_billiards_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
