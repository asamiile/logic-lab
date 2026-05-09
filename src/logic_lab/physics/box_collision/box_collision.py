from pathlib import Path

import py5

from logic_lab.shared.physics2d import AABB, OrientedBox, Vec2, sat_collision

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

boxes = [
    OrientedBox(Vec2(205, 180), Vec2(70, 42), angle=0.35),
    OrientedBox(Vec2(430, 180), Vec2(72, 38), angle=-0.45),
]


def setup() -> None:
    py5.size(640, 360)
    py5.smooth()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw_box(box: OrientedBox, touching: bool) -> None:
    verts = box.vertices()
    py5.fill(230, 82, 76, 120) if touching else py5.fill(70, 135, 210, 110)
    py5.stroke(25)
    py5.begin_shape()
    for v in verts:
        py5.vertex(v.x, v.y)
    py5.end_shape(py5.CLOSE)
    aabb = box.aabb()
    py5.no_fill()
    py5.stroke(30, 150)
    py5.rect_mode(py5.CENTER)
    py5.rect(aabb.center.x, aabb.center.y, aabb.half.x * 2, aabb.half.y * 2)


def draw() -> None:
    py5.background(248)
    boxes[0].angle = py5.frame_count * 0.018
    boxes[1].center = Vec2(py5.mouse_x, py5.mouse_y)
    boxes[1].angle = -py5.frame_count * 0.012
    overlap = sat_collision(boxes[0].vertices(), boxes[1].vertices()).overlaps
    aabb_overlap = boxes[0].aabb().overlaps(boxes[1].aabb())
    draw_box(boxes[0], overlap)
    draw_box(boxes[1], overlap)
    py5.no_stroke()
    py5.fill(30)
    py5.text(f"AABB broad phase: {aabb_overlap}", 18, 28)
    py5.text(f"OBB/SAT narrow phase: {overlap}", 18, 48)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "box_collision_####.png"))


py5.run_sketch()
