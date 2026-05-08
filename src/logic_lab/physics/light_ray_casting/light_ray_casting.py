from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from random import Random

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


@dataclass(frozen=True)
class Segment:
    ax: float
    ay: float
    bx: float
    by: float


segments: list[Segment] = []
rng = Random(18)
show_rays = False


def setup() -> None:
    py5.size(900, 680)
    py5.smooth()
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()


def reset_scene() -> None:
    global segments
    margin = 50
    segments = [
        Segment(margin, margin, py5.width - margin, margin),
        Segment(py5.width - margin, margin, py5.width - margin, py5.height - margin),
        Segment(py5.width - margin, py5.height - margin, margin, py5.height - margin),
        Segment(margin, py5.height - margin, margin, margin),
    ]
    for _ in range(11):
        cx = rng.uniform(130, py5.width - 130)
        cy = rng.uniform(120, py5.height - 120)
        radius = rng.uniform(34, 82)
        sides = rng.randrange(3, 7)
        angle_offset = rng.uniform(0, py5.TWO_PI)
        points = []
        for i in range(sides):
            angle = angle_offset + py5.TWO_PI * i / sides
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        for a, b in zip(points, points[1:] + points[:1]):
            segments.append(Segment(a[0], a[1], b[0], b[1]))


def draw() -> None:
    py5.background(232, 42, 10)
    source = (float(py5.mouse_x or py5.width * 0.36), float(py5.mouse_y or py5.height * 0.42))
    hits = visibility_polygon(source)
    draw_shadow_field(hits, source)
    draw_segments()
    draw_source(source)


def visibility_polygon(source: tuple[float, float]) -> list[tuple[float, float, float]]:
    angles = set()
    sx, sy = source
    for segment in segments:
        for x, y in ((segment.ax, segment.ay), (segment.bx, segment.by)):
            angle = math.atan2(y - sy, x - sx)
            angles.update((angle - 0.0008, angle, angle + 0.0008))

    hits = []
    for angle in angles:
        dx = math.cos(angle)
        dy = math.sin(angle)
        nearest = None
        nearest_distance = float("inf")
        for segment in segments:
            hit = ray_segment_intersection(sx, sy, dx, dy, segment)
            if hit and hit[2] < nearest_distance:
                nearest = hit
                nearest_distance = hit[2]
        if nearest:
            hits.append((angle, nearest[0], nearest[1]))
    return sorted(hits, key=lambda item: item[0])


def ray_segment_intersection(
    sx: float, sy: float, dx: float, dy: float, segment: Segment
) -> tuple[float, float, float] | None:
    vx = segment.bx - segment.ax
    vy = segment.by - segment.ay
    denom = dx * vy - dy * vx
    if abs(denom) < 1e-9:
        return None
    qx = segment.ax - sx
    qy = segment.ay - sy
    t = (qx * vy - qy * vx) / denom
    u = (qx * dy - qy * dx) / denom
    if t >= 0 and 0 <= u <= 1:
        return sx + dx * t, sy + dy * t, t
    return None


def draw_shadow_field(hits: list[tuple[float, float, float]], source: tuple[float, float]) -> None:
    py5.no_stroke()
    py5.fill(232, 42, 4, 92)
    py5.rect(0, 0, py5.width, py5.height)

    if len(hits) < 3:
        return
    py5.fill(45, 88, 96, 42)
    py5.begin_shape()
    for _, x, y in hits:
        py5.vertex(x, y)
    py5.end_shape(py5.CLOSE)

    if show_rays:
        py5.stroke(48, 70, 100, 18)
        py5.stroke_weight(1)
        for _, x, y in hits:
            py5.line(source[0], source[1], x, y)


def draw_segments() -> None:
    py5.stroke(205, 18, 86, 76)
    py5.stroke_weight(4)
    for segment in segments:
        py5.line(segment.ax, segment.ay, segment.bx, segment.by)


def draw_source(source: tuple[float, float]) -> None:
    py5.no_stroke()
    for radius, alpha in ((72, 10), (36, 22), (14, 92)):
        py5.fill(47, 90, 100, alpha)
        py5.circle(source[0], source[1], radius)


def key_pressed() -> None:
    global show_rays
    if py5.key == "r":
        reset_scene()
    elif py5.key == "v":
        show_rays = not show_rays
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "light_ray_casting_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
