from pathlib import Path
from random import Random

import py5
from logic_lab.shared.physics2d import AABB, Vec2

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

rng = Random(7)
boxes: list[dict[str, Vec2 | float]] = []


def add_box(x: float, y: float) -> None:
    boxes.append({"pos": Vec2(x, y), "vel": Vec2(rng.uniform(-12, 12), 0), "w": 34.0, "h": 24.0})


def setup() -> None:
    py5.size(640, 360)
    for i in range(12):
        add_box(295 + (i % 3) * 36, 55 - i * 27)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def box_aabb(box: dict[str, Vec2 | float]) -> AABB:
    return AABB(box["pos"], Vec2(box["w"] * 0.5, box["h"] * 0.5))  # type: ignore[arg-type, operator]


def solve_pair(a: dict[str, Vec2 | float], b: dict[str, Vec2 | float]) -> None:
    aa = box_aabb(a)
    bb = box_aabb(b)
    if not aa.overlaps(bb):
        return
    dx = min(aa.max_x - bb.min_x, bb.max_x - aa.min_x)
    dy = min(aa.max_y - bb.min_y, bb.max_y - aa.min_y)
    if dx < dy:
        push = dx * 0.5
        if aa.center.x < bb.center.x:
            a["pos"].x -= push  # type: ignore[union-attr]
            b["pos"].x += push  # type: ignore[union-attr]
        else:
            a["pos"].x += push  # type: ignore[union-attr]
            b["pos"].x -= push  # type: ignore[union-attr]
        a["vel"].x *= 0.2  # type: ignore[union-attr]
        b["vel"].x *= 0.2  # type: ignore[union-attr]
    else:
        push = dy * 0.5
        if aa.center.y < bb.center.y:
            a["pos"].y -= push  # type: ignore[union-attr]
            b["pos"].y += push  # type: ignore[union-attr]
        else:
            a["pos"].y += push  # type: ignore[union-attr]
            b["pos"].y -= push  # type: ignore[union-attr]
        a["vel"].y *= -0.08  # type: ignore[union-attr]
        b["vel"].y *= -0.08  # type: ignore[union-attr]


def draw() -> None:
    py5.background(248)
    for box in boxes:
        box["vel"].y += 10  # type: ignore[union-attr]
        box["pos"].x += box["vel"].x / 60  # type: ignore[union-attr]
        box["pos"].y += box["vel"].y / 60  # type: ignore[union-attr]
        floor = py5.height - box["h"] * 0.5  # type: ignore[operator]
        if box["pos"].y > floor:  # type: ignore[operator]
            box["pos"].y = floor  # type: ignore[union-attr]
            box["vel"].y = 0  # type: ignore[union-attr]
            box["vel"].x *= 0.9  # type: ignore[union-attr]
    for _ in range(8):
        for i, a in enumerate(boxes):
            for b in boxes[i + 1 :]:
                solve_pair(a, b)
    py5.rect_mode(py5.CENTER)
    for box in boxes:
        py5.fill(220, 170, 74, 170)
        py5.stroke(35)
        py5.rect(box["pos"].x, box["pos"].y, box["w"], box["h"])  # type: ignore[union-attr]


def mouse_pressed() -> None:
    add_box(py5.mouse_x, py5.mouse_y)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "contact_solver_####.png"))


py5.run_sketch()
