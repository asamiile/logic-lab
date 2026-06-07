"""
Coupled Oscillators (Kuramoto Model).

N phase oscillators, each with a natural frequency omega_i, interact
through a mean-field coupling term. Above a critical coupling strength K,
the oscillators spontaneously synchronize — their phases converge to a
common rhythm despite individual frequency differences.

Update rule (Euler integration):
    d(theta_i)/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i)

Visualization:
    - Each oscillator is a point on a unit circle (its phase = angle).
    - Color encodes natural frequency.
    - Lines connect each oscillator to the mean-field vector (order parameter R).
    - The order parameter R (center dot size) measures synchrony: R=0 chaos, R=1 sync.
    - LFO slowly ramps K to demonstrate the phase transition in real time.
"""

import math
import random
from pathlib import Path

import py5

from logic_lab.shared.lfo import LFOBank

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800
N = 80  # Number of oscillators
RADIUS = 280.0  # Display circle radius
dt = 0.04

lfo = LFOBank(sample_rate=60)
lfo.add("coupling", shape="triangle", freq=0.004, low=0.0, high=4.0)
lfo.add("noise_amp", shape="sine", freq=0.02, low=0.0, high=0.5)

thetas: list[float]
omegas: list[float]
paused = False
manual_k: float | None = None


def _initialize(seed: int = 42) -> None:
    global thetas, omegas
    rng = random.Random(seed)
    thetas = [rng.uniform(0, math.tau) for _ in range(N)]
    omegas = [rng.gauss(0.0, 0.8) for _ in range(N)]


def _order_parameter() -> tuple[float, float]:
    """Return (R, Psi) — synchrony magnitude and mean phase."""
    sx = sum(math.cos(t) for t in thetas) / N
    sy = sum(math.sin(t) for t in thetas) / N
    return math.hypot(sx, sy), math.atan2(sy, sx)


def _update(K: float, noise: float) -> None:
    rng = random.Random()
    new_thetas = []
    for i in range(N):
        coupling_sum = sum(math.sin(thetas[j] - thetas[i]) for j in range(N))
        dtheta = omegas[i] + K / N * coupling_sum + rng.gauss(0, noise)
        new_thetas.append(thetas[i] + dtheta * dt)
    thetas[:] = new_thetas


def _freq_color(omega: float) -> tuple[int, int, int]:
    """Map natural frequency to a hue (blue=slow, red=fast)."""
    t = (omega + 2.5) / 5.0
    t = max(0.0, min(1.0, t))
    hue = t * 270.0  # blue → red through spectrum
    c = 1.0 - abs((hue / 60) % 2 - 1)
    x = c
    if hue < 60:
        r, g, b = 1.0, x, 0.0
    elif hue < 120:
        r, g, b = x, 1.0, 0.0
    elif hue < 180:
        r, g, b = 0.0, 1.0, x
    elif hue < 240:
        r, g, b = 0.0, x, 1.0
    elif hue < 300:
        r, g, b = x, 0.0, 1.0
    else:
        r, g, b = 1.0, 0.0, x
    return int(r * 220), int(g * 220), int(b * 220)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.smooth(8)
    py5.background(10, 10, 18)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _initialize()


def draw() -> None:
    cx, cy = WIDTH / 2.0, HEIGHT / 2.0

    if not paused:
        vals = lfo.tick_all()
        K = manual_k if manual_k is not None else vals["coupling"]
        noise = vals["noise_amp"]
        _update(K, noise)
    else:
        K = manual_k if manual_k is not None else lfo.peek("coupling")

    R, psi = _order_parameter()

    # Background fade
    py5.fill(10, 10, 18, 35)
    py5.no_stroke()
    py5.rect(0, 0, WIDTH, HEIGHT)

    # Draw unit circle
    py5.no_fill()
    py5.stroke(60, 60, 80, 100)
    py5.stroke_weight(1)
    py5.circle(cx, cy, RADIUS * 2)

    # Draw order parameter arrow
    mx = cx + R * RADIUS * math.cos(psi)
    my = cy + R * RADIUS * math.sin(psi)
    py5.stroke(255, 220, 80, 180)
    py5.stroke_weight(2)
    py5.line(cx, cy, mx, my)

    # Draw oscillators
    for i in range(N):
        ox = cx + RADIUS * math.cos(thetas[i])
        oy = cy + RADIUS * math.sin(thetas[i])
        r, g, b = _freq_color(omegas[i])

        # Line to mean field
        py5.stroke(r, g, b, 30)
        py5.stroke_weight(0.5)
        py5.line(ox, oy, mx, my)

        # Oscillator dot
        py5.no_stroke()
        py5.fill(r, g, b, 200)
        py5.circle(ox, oy, 7)

    # Order parameter dot
    py5.no_stroke()
    py5.fill(255, 220, 80, 230)
    py5.circle(mx, my, max(4, R * 18))

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(f"Kuramoto | N={N} K={K:.2f} R={R:.3f} | ↑/↓=K SPACE=pause R=reset S=save", 10, 20)


def key_pressed() -> None:
    global paused, manual_k
    if py5.key == " ":
        paused = not paused
    elif py5.key == "r":
        _initialize()
        manual_k = None
    elif py5.key == "n":
        _initialize(seed=py5.frame_count)
        manual_k = None
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "kuramoto_####.png"))
    elif py5.key_code == py5.UP:
        manual_k = min(4.0, (manual_k if manual_k is not None else 1.0) + 0.1)
    elif py5.key_code == py5.DOWN:
        manual_k = max(0.0, (manual_k if manual_k is not None else 1.0) - 0.1)


if __name__ == "__main__":
    py5.run_sketch()
