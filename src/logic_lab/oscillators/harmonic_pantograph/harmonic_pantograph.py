"""
Harmonic Pantograph (Spirograph / Epicycloid Drawer).

A chain of rotating arms — each driven by an independent oscillator —
draws the combined tip path. The number of arms, their radii, and their
angular speeds determine the complexity of the resulting curve.

This is equivalent to a Fourier epicycle approximation: given N arms
you can approximate any closed curve by choosing the right radii and
frequencies. The LFOBank modulates arm speeds over time for slowly
morphing patterns.

    tip(t) = sum_k [ r_k * exp(i * (omega_k * t + phi_k)) ]
"""

import math
from dataclasses import dataclass
from pathlib import Path

import py5

from logic_lab.shared.lfo import LFOBank

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800
TRAIL_LENGTH = 6000

PRESETS = {
    "trident": [(200, 1.0, 0.0), (80, -3.0, 0.0), (30, 7.0, 0.0)],
    "rose": [(180, 1.0, 0.0), (100, 3.0, 0.5), (40, 5.0, 1.0), (15, -9.0, 0.3)],
    "star": [(160, 1.0, 0.0), (80, -5.0, 0.0), (40, 7.0, 0.0), (20, 11.0, 0.0)],
    "wave": [(220, 1.0, 0.0), (60, 2.0, math.pi / 3), (20, 4.0, math.pi / 6)],
}
# Each arm tuple: (radius, freq_multiplier, phase_offset)

preset_name = "rose"
trail: list[tuple[float, float]] = []
t = 0.0
paused = False

lfo = LFOBank(sample_rate=60)
lfo.add("speed_mod", shape="sine", freq=0.008, low=0.6, high=1.4)
lfo.add("arm2_drift", shape="noise", freq=0.005, low=-0.3, high=0.3)
lfo.add("hue_base", shape="sawtooth", freq=0.012, low=0.0, high=360.0)

arms: list[tuple[float, float, float]]


def _load_preset(name: str) -> None:
    global arms, trail, t
    arms = list(PRESETS[name])
    trail = []
    t = 0.0


def _tip_position(time: float, speed: float, arm2_drift: float) -> tuple[float, float]:
    cx = WIDTH / 2.0
    cy = HEIGHT / 2.0
    x, y = cx, cy
    for i, (r, freq, phi) in enumerate(arms):
        f = freq * speed
        if i == 1:
            f += arm2_drift
        angle = f * time + phi
        x += r * math.cos(angle)
        y += r * math.sin(angle)
    return x, y


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.background(10, 10, 18)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _load_preset(preset_name)


def draw() -> None:
    global t

    if not paused:
        vals = lfo.tick_all()
        speed = vals["speed_mod"]
        arm2_drift = vals["arm2_drift"]
        hue_base = vals["hue_base"]

        steps = 6
        dt = 0.006
        for _ in range(steps):
            tx, ty = _tip_position(t, speed, arm2_drift)
            trail.append((tx, ty))
            t += dt

        if len(trail) > TRAIL_LENGTH:
            trail[:] = trail[-TRAIL_LENGTH:]

    # Fade
    py5.fill(0, 0, 0, 6)
    py5.no_stroke()
    py5.rect(0, 0, WIDTH, HEIGHT)

    # Draw trail
    n = len(trail)
    for i in range(1, n):
        age = i / n
        hue = (hue_base + i * 0.04) % 360
        alpha = int(age * 85)
        py5.stroke(hue, 75, 95, alpha)
        py5.stroke_weight(1.0)
        py5.line(trail[i - 1][0], trail[i - 1][1], trail[i][0], trail[i][1])

    # Draw arms at current tip
    if not paused and trail:
        vals2 = lfo.peek("speed_mod"), lfo.peek("arm2_drift")
        x, y = WIDTH / 2.0, HEIGHT / 2.0
        py5.stroke(0, 0, 60, 40)
        py5.stroke_weight(1)
        for i, (r, freq, phi) in enumerate(arms):
            f = freq * vals2[0]
            if i == 1:
                f += vals2[1]
            nx = x + r * math.cos(f * t + phi)
            ny = y + r * math.sin(f * t + phi)
            py5.line(x, y, nx, ny)
            x, y = nx, ny

    py5.color_mode(py5.RGB, 255)
    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"Pantograph | {preset_name} | 1-4=preset R=reset SPACE=pause S=save", 10, 20)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)


def key_pressed() -> None:
    global preset_name, paused
    if py5.key == "1":
        preset_name = "trident"
        _load_preset(preset_name)
    elif py5.key == "2":
        preset_name = "rose"
        _load_preset(preset_name)
    elif py5.key == "3":
        preset_name = "star"
        _load_preset(preset_name)
    elif py5.key == "4":
        preset_name = "wave"
        _load_preset(preset_name)
    elif py5.key == "r":
        _load_preset(preset_name)
    elif py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"pantograph_{preset_name}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
