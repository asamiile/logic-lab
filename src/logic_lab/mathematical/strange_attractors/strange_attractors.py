"""
Strange Attractors.

Chaotic dynamical systems that produce fractal trajectories confined to
a bounded region — the attractor. A particle following the equations
never exactly repeats its path, yet traces a recognizable geometric form.

Systems included:
    lorenz    — Lorenz (1963): classic butterfly / double-scroll
    rossler   — Rössler (1976): spiral band attractor
    thomas    — Thomas (1999): linked torus, labyrinthine chaos
    aizawa    — Aizawa (1984): torus-knot-like
    dadras    — Dadras (2009): scroll with wings

All are rendered in 3D with a simple perspective projection and depth-
based color for perceived volume. An LFO slowly rotates the view.
"""

import math
import random as _random
from pathlib import Path

import py5

from logic_lab.shared.lfo import LFOBank
from logic_lab.shared.rk4 import rk4_step

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800
NUM_PARTICLES = 4000
DT = 0.005

SYSTEMS: dict[str, dict] = {
    "lorenz": {
        "init": lambda i: (0.1 * (i % 10 - 5), 0.1 * (i // 10 - 10), 25.0 + 0.01 * i),
        "deriv": lambda x, y, z: (
            10.0 * (y - x),
            x * (28.0 - z) - y,
            x * y - (8.0 / 3.0) * z,
        ),
        "scale": 0.018,
        "color_axis": "z",
        "z_range": (0, 50),
    },
    "rossler": {
        "init": lambda i: (0.1 * (i % 20 - 10), 0.1 * (i // 20 - 5), 0.01 * i),
        "deriv": lambda x, y, z: (
            -y - z,
            x + 0.2 * y,
            0.2 + z * (x - 5.7),
        ),
        "scale": 0.03,
        "color_axis": "x",
        "z_range": (-15, 15),
    },
    "thomas": {
        "init": lambda i: (0.1 * (i % 20 - 10), 0.1 * (i // 20 - 5), 0.01 * i),
        "deriv": lambda x, y, z: (
            math.sin(y) - 0.208186 * x,
            math.sin(z) - 0.208186 * y,
            math.sin(x) - 0.208186 * z,
        ),
        "scale": 0.12,
        "color_axis": "y",
        "z_range": (-4, 4),
    },
    "aizawa": {
        "init": lambda i: (0.1 * (i % 20 - 10), 0.01 * i, 0.5),
        "deriv": lambda x, y, z: (
            (z - 0.7) * x - 3.5 * y,
            3.5 * x + (z - 0.7) * y,
            0.6 + 0.95 * z - z * z * z / 3 - (x * x + y * y) * (1 + 0.25 * z) + 0.1 * z * x * x * x,
        ),
        "scale": 0.16,
        "color_axis": "z",
        "z_range": (-1.5, 1.5),
    },
    "dadras": {
        "init": lambda i: (0.1 * (i % 20 - 10), 0.1 * (i // 20 - 5), 0.01 * i),
        "deriv": lambda x, y, z: (
            y - 3.0 * x + 2.7 * y * z,
            2.7 * y - x * z + z,
            0.4 * x * y - 1.7 * z,
        ),
        "scale": 0.04,
        "color_axis": "z",
        "z_range": (-20, 20),
    },
}

preset_name = "lorenz"
pts: list[list[float]]
paused = False

lfo = LFOBank(sample_rate=60)
lfo.add("rot_y", shape="sawtooth", freq=0.008, low=0.0, high=math.tau)
lfo.add("rot_x", shape="sine", freq=0.005, low=-0.4, high=0.4)
lfo.add("speed", shape="sine", freq=0.015, low=0.5, high=2.0)


def _initialize(jitter: float = 0.0) -> None:
    global pts
    sys_ = SYSTEMS[preset_name]
    pts = []
    for i in range(NUM_PARTICLES):
        p = list(sys_["init"](i))
        if jitter > 0:
            p[0] += _random.uniform(-jitter, jitter)
            p[1] += _random.uniform(-jitter, jitter)
            p[2] += _random.uniform(-jitter, jitter)
        pts.append(p)


def _step(steps: int) -> None:
    sys_ = SYSTEMS[preset_name]
    deriv = sys_["deriv"]
    speed = lfo.peek("speed")
    dt = DT * speed

    def f(_t: float, state: list[float]) -> list[float]:
        return list(deriv(state[0], state[1], state[2]))

    for _ in range(steps):
        for i in range(len(pts)):
            pts[i] = rk4_step(f, 0.0, pts[i], dt)


def _project(
    x: float, y: float, z: float, ry: float, rx: float, scale: float
) -> tuple[float, float, float]:
    # Rotate Y
    cos_y, sin_y = math.cos(ry), math.sin(ry)
    x2 = x * cos_y + z * sin_y
    z2 = -x * sin_y + z * cos_y
    # Rotate X
    cos_x, sin_x = math.cos(rx), math.sin(rx)
    y2 = y * cos_x - z2 * sin_x
    z3 = y * sin_x + z2 * cos_x
    # Perspective
    fov = 500.0
    dist = max(z3 * scale + 4.0, 0.2)
    sx = WIDTH / 2 + x2 * scale * fov / dist
    sy = HEIGHT / 2 + y2 * scale * fov / dist
    return sx, sy, z3


def _depth_color(val: float, lo: float, hi: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, (val - lo) / (hi - lo + 1e-9)))
    r = int(30 + t * 200)
    g = int(80 + t * 130)
    b = int(200 - t * 120)
    return r, g, b


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.smooth(4)
    py5.background(8, 8, 18)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _initialize()


def draw() -> None:
    if not paused:
        vals = lfo.tick_all()
        _step(2)
    else:
        vals = {"rot_y": lfo.peek("rot_y"), "rot_x": lfo.peek("rot_x")}

    # Fade
    py5.fill(8, 8, 18, 18)
    py5.no_stroke()
    py5.rect(0, 0, WIDTH, HEIGHT)

    sys = SYSTEMS[preset_name]
    scale = sys["scale"]
    z_lo, z_hi = sys["z_range"]
    color_axis = sys["color_axis"]
    ry = vals["rot_y"]
    rx = vals["rot_x"]

    axis_idx = {"x": 0, "y": 1, "z": 2}[color_axis]

    # Sort by projected depth
    projected = []
    for p in pts:
        sx, sy, sz = _project(p[0], p[1], p[2], ry, rx, scale)
        projected.append((sz, sx, sy, p[axis_idx]))

    projected.sort(key=lambda v: v[0])

    py5.stroke_weight(1)
    for _, sx, sy, cv in projected:
        r, g, b = _depth_color(cv, z_lo, z_hi)
        py5.stroke(r, g, b, 100)
        py5.point(sx, sy)

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"Strange Attractor | {preset_name} | 1-5=system SPACE=pause S=save", 10, 20)


def key_pressed() -> None:
    global preset_name, paused
    names = list(SYSTEMS.keys())
    if py5.key == "1":
        preset_name = names[0]
        _initialize()
    elif py5.key == "2":
        preset_name = names[1]
        _initialize()
    elif py5.key == "3":
        preset_name = names[2]
        _initialize()
    elif py5.key == "4":
        preset_name = names[3]
        _initialize()
    elif py5.key == "5":
        preset_name = names[4]
        _initialize()
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "n":
        _initialize(jitter=0.5)
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"attractor_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
