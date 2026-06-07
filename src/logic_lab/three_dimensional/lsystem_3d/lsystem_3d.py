"""
3D L-System (Lindenmayer System).

Generates 3D branching tree and plant structures via symbol-rewriting rules.
The turtle interprets symbols as 3D movement commands using a rotation stack,
creating fractal-like recursive botanical forms.

Standard turtle symbols:
    F  : Move forward (draw branch segment)
    +/-: Rotate around Z axis (yaw)
    ^/&: Rotate around X axis (pitch up/down)
    \\/: Rotate around Y axis (roll)
    [  : Push turtle state
    ]  : Pop turtle state

Built-in presets:
    - tree_3d: Classic recursive branching tree
    - coral: Coral-like growth with variable branching angles
    - fern_3d: 3D fern frond with side branches
"""

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800

PRESETS = {
    "tree_3d": {
        "axiom": "F",
        "rules": {"F": "F[+F]F[-F][^F]"},
        "angle": 25.7,
        "length": 80.0,
        "length_scale": 0.5,
        "iterations": 4,
    },
    "coral": {
        "axiom": "F",
        "rules": {"F": "FF+[+F-F-F]-[-F+F+F]"},
        "angle": 22.5,
        "length": 60.0,
        "length_scale": 0.45,
        "iterations": 4,
    },
    "fern_3d": {
        "axiom": "X",
        "rules": {"X": "F[^+X]F[-X]+X", "F": "FF"},
        "angle": 20.0,
        "length": 70.0,
        "length_scale": 0.5,
        "iterations": 5,
    },
}

preset_name = "tree_3d"


@dataclass
class TurtleState:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    # Direction vector
    dx: float = 0.0
    dy: float = -1.0
    dz: float = 0.0
    # Up vector
    ux: float = 0.0
    uy: float = 0.0
    uz: float = 1.0
    depth: int = 0


def _expand(axiom: str, rules: dict[str, str], n: int) -> str:
    s = axiom
    for _ in range(n):
        s = "".join(rules.get(c, c) for c in s)
    return s


def _rotate_around(
    vx: float, vy: float, vz: float, ax: float, ay: float, az: float, angle: float
) -> tuple[float, float, float]:
    """Rotate vector v around axis a by angle (radians)."""
    c = math.cos(angle)
    s = math.sin(angle)
    dot = vx * ax + vy * ay + vz * az
    cx = ax * dot * (1 - c)
    cy = ay * dot * (1 - c)
    cz = az * dot * (1 - c)
    rx = vx * c + (ay * vz - az * vy) * s + cx
    ry = vy * c + (az * vx - ax * vz) * s + cy
    rz = vz * c + (ax * vy - ay * vx) * s + cz
    return rx, ry, rz


def _project(x: float, y: float, z: float, cx: float, cy: float) -> tuple[float, float]:
    """Simple perspective projection."""
    fov = 500.0
    dist = z + 6.0
    if dist < 0.1:
        dist = 0.1
    sx = cx + x * fov / dist
    sy = cy + y * fov / dist
    return sx, sy


def _draw_lsystem(sentence: str, angle_deg: float, length: float) -> None:
    rad = math.radians(angle_deg)
    stack: list[TurtleState] = []
    t = TurtleState(x=0.0, y=0.0, z=0.0)

    cx = WIDTH / 2.0
    cy = HEIGHT * 0.85

    # Side vectors from direction and up
    def _side(t: TurtleState) -> tuple[float, float, float]:
        sx = t.dy * t.uz - t.dz * t.uy
        sy = t.dz * t.ux - t.dx * t.uz
        sz = t.dx * t.uy - t.dy * t.ux
        mag = math.sqrt(sx * sx + sy * sy + sz * sz) + 1e-9
        return sx / mag, sy / mag, sz / mag

    for sym in sentence:
        if sym == "F":
            x2 = t.x + t.dx * length
            y2 = t.y + t.dy * length
            z2 = t.z + t.dz * length

            px1, py1 = _project(t.x, t.y, t.z, cx, cy)
            px2, py2 = _project(x2, y2, z2, cx, cy)

            depth_alpha = int(max(30, min(220, 220 - t.depth * 30)))
            py5.stroke(80, 160, 80, depth_alpha)
            sw = max(1, 4 - t.depth)
            py5.stroke_weight(sw)
            py5.line(px1, py1, px2, py2)

            t.x, t.y, t.z = x2, y2, z2

        elif sym == "+":
            t.dx, t.dy, t.dz = _rotate_around(t.dx, t.dy, t.dz, t.ux, t.uy, t.uz, rad)
        elif sym == "-":
            t.dx, t.dy, t.dz = _rotate_around(t.dx, t.dy, t.dz, t.ux, t.uy, t.uz, -rad)
        elif sym == "^":
            sx, sy, sz = _side(t)
            t.dx, t.dy, t.dz = _rotate_around(t.dx, t.dy, t.dz, sx, sy, sz, rad)
            t.ux, t.uy, t.uz = _rotate_around(t.ux, t.uy, t.uz, sx, sy, sz, rad)
        elif sym == "&":
            sx, sy, sz = _side(t)
            t.dx, t.dy, t.dz = _rotate_around(t.dx, t.dy, t.dz, sx, sy, sz, -rad)
            t.ux, t.uy, t.uz = _rotate_around(t.ux, t.uy, t.uz, sx, sy, sz, -rad)
        elif sym == "\\":
            t.dx, t.dy, t.dz = _rotate_around(t.dx, t.dy, t.dz, t.dx, t.dy, t.dz, rad)
            t.ux, t.uy, t.uz = _rotate_around(t.ux, t.uy, t.uz, t.dx, t.dy, t.dz, rad)
        elif sym == "/":
            t.dx, t.dy, t.dz = _rotate_around(t.dx, t.dy, t.dz, t.dx, t.dy, t.dz, -rad)
            t.ux, t.uy, t.uz = _rotate_around(t.ux, t.uy, t.uz, t.dx, t.dy, t.dz, -rad)
        elif sym == "[":
            stack.append(
                TurtleState(t.x, t.y, t.z, t.dx, t.dy, t.dz, t.ux, t.uy, t.uz, t.depth + 1)
            )
        elif sym == "]":
            if stack:
                t = stack.pop()


sentence: str = ""
draw_length: float = 0.0
draw_angle: float = 0.0


def _load_preset(name: str) -> None:
    global sentence, draw_length, draw_angle
    p = PRESETS[name]
    sentence = _expand(p["axiom"], p["rules"], p["iterations"])
    draw_length = p["length"] * (p["length_scale"] ** p["iterations"])
    draw_angle = p["angle"]


def setup() -> None:
    global preset_name
    py5.size(WIDTH, HEIGHT)
    py5.background(15, 20, 10)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _load_preset(preset_name)


def draw() -> None:
    py5.background(15, 20, 10)
    _draw_lsystem(sentence, draw_angle, draw_length)

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"3D L-System | {preset_name} | 1/2/3=preset R=reload S=save", 10, 20)


def key_pressed() -> None:
    global preset_name
    if py5.key == "1":
        preset_name = "tree_3d"
        _load_preset(preset_name)
    elif py5.key == "2":
        preset_name = "coral"
        _load_preset(preset_name)
    elif py5.key == "3":
        preset_name = "fern_3d"
        _load_preset(preset_name)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"lsystem_3d_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
