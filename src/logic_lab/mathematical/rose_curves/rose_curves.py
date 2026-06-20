"""
Rose Curves — Rhodonea and Maclaurin's Roses
A rose curve in polar coordinates:  r = cos(k·θ)

The number of petals depends on k:
  k odd integer    → k petals
  k even integer   → 2k petals
  k = p/q (reduced fraction, q odd)  → p petals if p odd, 2p if p even
  k irrational     → dense, space-filling after infinite revolutions

Displayed with multiple overlapping roses at rotational phase offsets to
create mandala-like symmetric compositions.

Five display modes:
  1  single rotating rose  — one k, animates continuously
  2  petal bloom           — k sweeps 1→7 showing petal bifurcations
  3  mandala               — N roses at 2π/N offsets, rotating k
  4  lissajous-rose        — x=cos(at+δ), y=cos(bt), generalized Lissajous
  5  maclaurin spiral      — r = a·θ^(1/n) polar spiral family

Color encodes the arc length traveled along the curve (speed-based hue),
with older segments fading out via alpha accumulation.

Controls:
  1–5     — mode
  r       — reset / restart trace
  k/K     — decrease / increase k ratio (modes 1, 3)
  Space   — pause / resume
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
SCALE = min(WIDTH, HEIGHT) * 0.42

TRAIL = 6000  # points kept in trail
STEPS = 8  # points added per frame
DT = 0.008

mode = 1
paused = False

_k = 3.0 / 5.0  # rose ratio
_t = 0.0
_trail_x: list
_trail_y: list
_trail_c: list  # hue per segment


def _reset() -> None:
    global _t, _trail_x, _trail_y, _trail_c
    _t = 0.0
    _trail_x = []
    _trail_y = []
    _trail_c = []


def _rose_point(t: float, k: float, phase: float = 0.0) -> tuple[float, float]:
    r = np.cos(k * t)
    return r * np.cos(t + phase), r * np.sin(t + phase)


def _lissajous_point(t: float, a: float, b: float, delta: float) -> tuple[float, float]:
    return np.cos(a * t + delta), np.cos(b * t)


def _maclaurin_point(t: float, a: float, n: float) -> tuple[float, float]:
    r = a * (t ** (1.0 / n))
    return r * np.cos(t), r * np.sin(t)


def _hue_for_t(t: float) -> float:
    return (t * 30.0) % 360.0


def _hsv_rgb(h: float, s: float = 0.8, v: float = 0.9) -> tuple[int, int, int]:
    h6 = (h % 360) / 60.0
    i = int(h6) % 6
    f = h6 - int(h6)
    p, q2, tv = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    lut = [(v, tv, p), (q2, v, p), (p, v, tv), (p, q2, v), (tv, p, v), (v, p, q2)]
    r, g, b = lut[i]
    return int(r * 230), int(g * 230), int(b * 230)


def _step_single() -> None:
    for _ in range(STEPS):
        x, y = _rose_point(_t, _k)
        _trail_x.append(x)
        _trail_y.append(y)
        _trail_c.append(_hue_for_t(_t))
        if len(_trail_x) > TRAIL:
            _trail_x.pop(0)
            _trail_y.pop(0)
            _trail_c.pop(0)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()
    py5.frame_rate(60)


def draw() -> None:
    global _t, _k

    if not paused:
        _t += DT * STEPS

        if mode == 1:
            _step_single()
        elif mode == 2:
            _k = 1.0 + (_t * 0.05 % 6.0)
            _step_single()
        elif mode == 3:
            for _ in range(STEPS):
                for ph in np.linspace(0, 2 * np.pi, 6, endpoint=False):
                    x, y = _rose_point(_t, _k, ph)
                    _trail_x.append(x)
                    _trail_y.append(y)
                    _trail_c.append((_hue_for_t(_t) + ph * 57.3) % 360.0)
                while len(_trail_x) > TRAIL * 6:
                    _trail_x.pop(0)
                    _trail_y.pop(0)
                    _trail_c.pop(0)
        elif mode == 4:
            a = 3.0
            b = 2.0
            delta = _t * 0.1
            for _ in range(STEPS):
                x, y = _lissajous_point(_t, a, b, delta)
                _trail_x.append(x)
                _trail_y.append(y)
                _trail_c.append(_hue_for_t(_t))
                if len(_trail_x) > TRAIL:
                    _trail_x.pop(0)
                    _trail_y.pop(0)
                    _trail_c.pop(0)
        else:
            a = 0.055
            n = 1.5 + (_t * 0.01 % 3.0)
            t_max = _t % (6 * np.pi)
            if t_max < 0.01:
                _reset()
            for _ in range(STEPS):
                x, y = _maclaurin_point(max(_t % (6 * np.pi), 0.001), a, n)
                _trail_x.append(x)
                _trail_y.append(y)
                _trail_c.append(_hue_for_t(_t))
                if len(_trail_x) > TRAIL:
                    _trail_x.pop(0)
                    _trail_y.pop(0)
                    _trail_c.pop(0)

    py5.background(10, 10, 22)
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    n_pts = len(_trail_x)

    py5.stroke_weight(1.2)
    py5.no_fill()
    for i in range(1, n_pts):
        age = i / n_pts
        alpha = int(age * 200)
        r_c, g_c, b_c = _hsv_rgb(_trail_c[i], 0.75, age * 0.9 + 0.1)
        py5.stroke(r_c, g_c, b_c, alpha)
        x0, y0 = _trail_x[i - 1], _trail_y[i - 1]
        x1, y1 = _trail_x[i], _trail_y[i]
        # Skip large jumps (phase discontinuities)
        if abs(x1 - x0) + abs(y1 - y0) > 0.5:
            continue
        py5.line(
            x0 * SCALE + cx,
            -y0 * SCALE + cy,
            x1 * SCALE + cx,
            -y1 * SCALE + cy,
        )

    mode_names = ["", "single", "bloom", "mandala", "lissajous", "spiral"]
    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Rose curves  mode:{mode_names[mode]}  k={_k:.4f}  " f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, mode, _k
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        mode = 1
        _reset()
    elif k == "2":
        mode = 2
        _reset()
    elif k == "3":
        mode = 3
        _reset()
    elif k == "4":
        mode = 4
        _reset()
    elif k == "5":
        mode = 5
        _reset()
    elif k == "k":
        _k = max(0.1, round(_k - 0.1, 4))
        _reset()
    elif k == "K":
        _k = min(8.0, round(_k + 0.1, 4))
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"rose_m{mode}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
