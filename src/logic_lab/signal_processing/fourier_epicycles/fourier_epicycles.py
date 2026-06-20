"""
Fourier Epicycles
Any closed 2D path can be expressed as a sum of rotating circles (epicycles).
The radii and phases come from the Discrete Fourier Transform of the path's
complex representation z(t) = x(t) + i·y(t).

As the animation runs, the nested chain of circles traces the original shape.
Sorting by amplitude (largest circle first) gives the classic spirograph look.

Presets: star, heart, trefoil, square, lissajous-butterfly, triangle.
Watch how increasing the number of circles (N_CIRCLES) improves fidelity.

Controls:
  1–6       — switch preset shape
  n / N     — fewer / more epicycles
  Space     — pause / resume
  t         — toggle path trail on/off
  s         — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800

N_PTS = 512  # DFT resolution (sample points on path)
N_CIRCLES = 32  # number of epicycles to show (adjustable)
OMEGA = 0.015  # animation speed (radians per frame)

PRESETS = ["star", "heart", "trefoil", "square", "butterfly", "triangle"]
preset_idx = 0

show_trail = True
paused = False
_t = 0.0  # animation phase [0, 2π)

# DFT coefficients: sorted by amplitude
_freqs: np.ndarray  # integer frequencies (signed)
_amps: np.ndarray  # magnitudes
_phases: np.ndarray  # initial phases

# Trail buffer
_trail_x: list
_trail_y: list
MAX_TRAIL = N_PTS * 2


def _path_pts(name: str) -> np.ndarray:
    """Return (N_PTS,) complex array for the named preset."""
    t = np.linspace(0, 2 * np.pi, N_PTS, endpoint=False)
    if name == "star":
        k = 5
        r = 1.0 + 0.5 * np.cos(k * t)
        return r * np.exp(1j * t)
    elif name == "heart":
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        return (x + 1j * (-y)) / 16.0
    elif name == "trefoil":
        r = np.cos(3 * t)
        return r * np.exp(1j * t)
    elif name == "square":
        # Approximate square via Fourier series: sum of odd harmonics
        x = np.zeros(N_PTS)
        y = np.zeros(N_PTS)
        for k in range(1, 20, 2):
            x += (4 / (np.pi * k)) * np.sin(k * t)
        x_s = 0.85 * np.clip(x, -1, 1) * 0.8 + 0.0
        y_s = np.roll(x_s, N_PTS // 4)
        return x_s + 1j * y_s
    elif name == "butterfly":
        # Lissajous-like butterfly: x=sin(3t), y=sin(2t)
        return np.sin(3 * t) + 1j * np.sin(2 * t)
    else:  # triangle
        x = 2 / np.pi * np.arcsin(np.sin(t))
        y = 2 / np.pi * np.arcsin(np.cos(t))
        return x + 1j * y


def _compute_dft(name: str) -> None:
    global _freqs, _amps, _phases
    z = _path_pts(name)
    F = np.fft.fft(z)
    n = len(F)
    # Map to signed frequencies: 0, 1, 2, ..., n//2, -(n//2)+1, ..., -1
    freqs = np.fft.fftfreq(n, d=1.0 / n).astype(int)
    amps = np.abs(F) / n
    phases = np.angle(F)

    # Sort descending by amplitude
    order = np.argsort(-amps)
    _freqs = freqs[order]
    _amps = amps[order]
    _phases = phases[order]


def _reset() -> None:
    global _t, _trail_x, _trail_y
    _compute_dft(PRESETS[preset_idx])
    _t = 0.0
    _trail_x = []
    _trail_y = []


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global _t

    if not paused:
        _t += OMEGA

    py5.background(10, 12, 22)

    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    scale = min(WIDTH, HEIGHT) * 0.36

    # Draw epicycles and accumulate tip position
    x, y = cx, cy
    n_show = min(N_CIRCLES, len(_amps))

    for k in range(n_show):
        freq = int(_freqs[k])
        amp = float(_amps[k]) * scale
        phi = float(_phases[k]) + freq * _t

        nx = x + amp * np.cos(phi)
        ny = y + amp * np.sin(phi)

        # Draw arm
        alpha = max(20, int(180 * amp / (float(_amps[0]) * scale + 1e-6)))
        py5.stroke(80, 120, 180, alpha)
        py5.stroke_weight(0.8)
        py5.no_fill()
        py5.circle(x, y, amp * 2)
        py5.stroke(120, 160, 220, min(alpha + 40, 220))
        py5.stroke_weight(1.2)
        py5.line(x, y, nx, ny)

        x, y = nx, ny

    # Record tip
    if show_trail:
        _trail_x.append(x)
        _trail_y.append(y)
        if len(_trail_x) > MAX_TRAIL:
            _trail_x.pop(0)
            _trail_y.pop(0)

        # Draw trail
        n_trail = len(_trail_x)
        py5.stroke_weight(1.6)
        for i in range(1, n_trail):
            age = i / n_trail
            py5.stroke(255, int(180 * age), int(60 * age), int(200 * age + 40))
            py5.line(_trail_x[i - 1], _trail_y[i - 1], _trail_x[i], _trail_y[i])

    # Tip dot
    py5.fill(255, 220, 100)
    py5.no_stroke()
    py5.circle(x, y, 6)

    # HUD
    py5.fill(180, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"preset:{PRESETS[preset_idx]}  circles:{N_CIRCLES}  "
        f"trail:{'on' if show_trail else 'off'}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global preset_idx, N_CIRCLES, show_trail, paused
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "t":
        show_trail = not show_trail
    elif k == "n":
        N_CIRCLES = max(1, N_CIRCLES - 4)
    elif k == "N":
        N_CIRCLES = min(N_PTS // 2, N_CIRCLES + 4)
    elif k == "1":
        preset_idx = 0
        _reset()
    elif k == "2":
        preset_idx = 1
        _reset()
    elif k == "3":
        preset_idx = 2
        _reset()
    elif k == "4":
        preset_idx = 3
        _reset()
    elif k == "5":
        preset_idx = 4
        _reset()
    elif k == "6":
        preset_idx = 5
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"epicycles_{PRESETS[preset_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
