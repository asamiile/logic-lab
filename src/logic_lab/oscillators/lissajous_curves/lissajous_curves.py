"""
Lissajous Curves.

Two sinusoidal oscillators drive the X and Y axes of a point, tracing
closed (or open) curves determined by the frequency ratio a:b and
phase offset delta. The shapes range from straight lines (ratio 1:1,
delta=0) to complex knots (high integer ratios).

    x(t) = A * sin(a*t + delta)
    y(t) = B * sin(b*t)

The LFOBank from shared/lfo is used to slowly drift the frequency
ratio and phase over time, creating a continuously evolving figure.
"""

import math
from pathlib import Path

import py5

from logic_lab.shared.lfo import LFOBank

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800
TRAIL_LENGTH = 4000

PRESETS = {
    "classic": {"a": 3, "b": 2, "delta": math.pi / 4},
    "knot": {"a": 5, "b": 4, "delta": math.pi / 2},
    "figure8": {"a": 1, "b": 2, "delta": math.pi / 2},
    "drift": {"a": 3, "b": 2, "delta": 0.0},  # delta drifts via LFO
}

preset_name = "classic"

t = 0.0
trail: list[tuple[float, float]] = []
paused = False

lfo = LFOBank(sample_rate=60)
lfo.add("delta_mod", shape="sine", freq=0.01, low=0.0, high=math.tau)
lfo.add("a_ratio", shape="noise", freq=0.003, low=1.0, high=6.0)
lfo.add("zoom", shape="sine", freq=0.02, low=0.7, high=1.0)

a_freq: float
b_freq: float
delta: float
drift_delta: bool


def _load_preset(name: str) -> None:
    global a_freq, b_freq, delta, drift_delta, trail, t
    p = PRESETS[name]
    a_freq = float(p["a"])
    b_freq = float(p["b"])
    delta = float(p["delta"])
    drift_delta = name == "drift"
    trail = []
    t = 0.0


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.smooth(8)
    py5.background(10, 10, 18)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _load_preset(preset_name)


def draw() -> None:
    global t, delta

    if not paused:
        vals = lfo.tick_all()
        zoom = vals["zoom"]
        rx = WIDTH / 2 * 0.9 * zoom
        ry = HEIGHT / 2 * 0.9 * zoom

        if drift_delta:
            delta = vals["delta_mod"]

        steps = 4
        dt = 0.008
        for _ in range(steps):
            x = WIDTH / 2 + rx * math.sin(a_freq * t + delta)
            y = HEIGHT / 2 + ry * math.sin(b_freq * t)
            trail.append((x, y))
            t += dt

        if len(trail) > TRAIL_LENGTH:
            trail[:] = trail[-TRAIL_LENGTH:]

    # Fade background
    py5.fill(0, 0, 0, 8)
    py5.no_stroke()
    py5.rect(0, 0, WIDTH, HEIGHT)

    # Draw trail with hue cycling
    py5.no_fill()
    n = len(trail)
    for i in range(1, n):
        age = i / n
        hue = (t * 15 + i * 0.05) % 360
        alpha = int(age * 90)
        py5.stroke(hue, 80, 95, alpha)
        py5.stroke_weight(1.2)
        py5.line(trail[i - 1][0], trail[i - 1][1], trail[i][0], trail[i][1])

    py5.color_mode(py5.RGB, 255)
    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Lissajous | {preset_name} | a={a_freq:.1f} b={b_freq:.1f} | 1-4=preset R=reset S=save",
        10,
        20,
    )
    py5.color_mode(py5.HSB, 360, 100, 100, 100)


def key_pressed() -> None:
    global preset_name, paused
    if py5.key == "1":
        preset_name = "classic"
        _load_preset(preset_name)
    elif py5.key == "2":
        preset_name = "knot"
        _load_preset(preset_name)
    elif py5.key == "3":
        preset_name = "figure8"
        _load_preset(preset_name)
    elif py5.key == "4":
        preset_name = "drift"
        _load_preset(preset_name)
    elif py5.key == "r":
        _load_preset(preset_name)
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"lissajous_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
