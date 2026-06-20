"""
Spirograph — Hypotrochoid and Epitrochoid Curves
A small circle of radius r rolls inside (hypo) or outside (epi) a fixed circle
of radius R. A pen at distance d from the rolling circle's center traces:

  Hypotrochoid:
    x(t) = (R − r)·cos(t) + d·cos((R−r)/r · t)
    y(t) = (R − r)·sin(t) − d·sin((R−r)/r · t)

  Epitrochoid:
    x(t) = (R + r)·cos(t) − d·cos((R+r)/r · t)
    y(t) = (R + r)·sin(t) − d·sin((R+r)/r · t)

When r/R is rational (p/q in lowest terms) the curve closes after q
revolutions. Irrational ratios produce dense space-filling curves.

The ratio r/R animates slowly to morph continuously between patterns.
A trail buffer accumulates the locus; when a new period starts the buffer
clears and a fresh curve is traced.

Three pens at offsets 0°, 120°, 240° create symmetric tri-color designs.

Presets (R, r, d as fractions of canvas half-size):
  1  Classic rose      r/R = 3/7,  d = 0.7R
  2  Star / asterisk   r/R = 2/5,  d = 0.9R
  3  Marigold          r/R = 4/11, d = 0.8R
  4  Epitrochoid star  r/R = 1/3,  d = 1.2r (epi)
  5  Animated drift    r/R slowly sweeps from 0.2 → 0.5

Controls:
  1–5     — preset
  e       — toggle hypo / epi mode
  r       — reset trail
  Space   — pause / resume
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
SCALE = min(WIDTH, HEIGHT) * 0.40
N_PENS = 3  # symmetric pens
STEPS = 4  # curve points added per frame
TRAIL_MAX = 8000  # max points kept in trail (per pen)
FADE = 0.993  # alpha decay per frame of old points

epi_mode = False  # hypo by default
paused = False
drift_mode = False

# Curve parameters
R_big = 1.0
r_small = 3.0 / 7.0
d_pen = 0.7

_ratio_drift = 0.0  # used when drift_mode=True
_t = 0.0  # current angle parameter
# Trail: per-pen list of (x, y, alpha) points
_trails: list  # [[(x,y,a), ...], ...]

PRESETS = [
    # (r/R,      d/R,  epi)
    (3 / 7, 0.70, False),
    (2 / 5, 0.90, False),
    (4 / 11, 0.80, False),
    (1 / 3, 0.40, True),
    None,  # drift
]
PRESET_NAMES = ["rose", "star", "marigold", "epi-star", "drift"]
preset_idx = 0


def _reset() -> None:
    global _t, _trails, _ratio_drift
    _t = 0.0
    _ratio_drift = 0.2
    _trails = [[] for _ in range(N_PENS)]


def _curve_point(t: float, pen_offset: float) -> tuple[float, float]:
    if epi_mode:
        cx = (R_big + r_small) * np.cos(t + pen_offset) - d_pen * np.cos(
            (R_big + r_small) / r_small * (t + pen_offset)
        )
        cy = (R_big + r_small) * np.sin(t + pen_offset) - d_pen * np.sin(
            (R_big + r_small) / r_small * (t + pen_offset)
        )
    else:
        cx = (R_big - r_small) * np.cos(t + pen_offset) + d_pen * np.cos(
            (R_big - r_small) / r_small * (t + pen_offset)
        )
        cy = (R_big - r_small) * np.sin(t + pen_offset) - d_pen * np.sin(
            (R_big - r_small) / r_small * (t + pen_offset)
        )
    return float(cx), float(cy)


def _step() -> None:
    global _t, _ratio_drift, r_small
    dt = 0.02

    if drift_mode:
        _ratio_drift += 0.00015
        if _ratio_drift > 0.50:
            _ratio_drift = 0.20
            _reset()
        r_small = _ratio_drift

    for _ in range(STEPS):
        _t += dt
        pen_offsets = [i * 2 * np.pi / N_PENS for i in range(N_PENS)]
        for pi2, pen_off in enumerate(pen_offsets):
            x, y = _curve_point(_t, pen_off)
            _trails[pi2].append((x, y))
            if len(_trails[pi2]) > TRAIL_MAX:
                _trails[pi2].pop(0)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()
    py5.frame_rate(60)


def draw() -> None:
    if not paused:
        _step()

    py5.background(10, 10, 20)

    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    pen_hues = [0.0, 120.0, 240.0]

    py5.stroke_weight(1.1)
    py5.no_fill()

    for pi2 in range(N_PENS):
        trail = _trails[pi2]
        n = len(trail)
        if n < 2:
            continue
        hue = pen_hues[pi2]
        h6 = hue / 60.0
        i6 = int(h6) % 6
        f = h6 - int(h6)
        q2 = 1.0 - f
        lut = [
            (1, f, 0),
            (q2, 1, 0),
            (0, 1, f),
            (0, q2, 1),
            (f, 0, 1),
            (1, 0, q2),
        ]
        r_c, g_c, b_c = (int(v * 230) for v in lut[i6])

        for seg in range(1, n):
            age = seg / n
            alpha = int(age * 200)
            py5.stroke(r_c, g_c, b_c, alpha)
            x0, y0 = trail[seg - 1]
            x1, y1 = trail[seg]
            py5.line(
                x0 * SCALE + cx,
                -y0 * SCALE + cy,
                x1 * SCALE + cx,
                -y1 * SCALE + cy,
            )

    mode_str = "epi" if epi_mode else "hypo"
    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Spirograph  preset:{PRESET_NAMES[preset_idx]}  "
        f"r/R={r_small:.4f}  d={d_pen:.2f}  {mode_str}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, epi_mode, r_small, d_pen, preset_idx, drift_mode
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "e":
        epi_mode = not epi_mode
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"spirograph_{PRESET_NAMES[preset_idx]}_####.png"))
    elif k == "1":
        preset_idx = 0
        drift_mode = False
        r_small, d_pen, epi_mode = PRESETS[0][0], PRESETS[0][1], PRESETS[0][2]
        _reset()
    elif k == "2":
        preset_idx = 1
        drift_mode = False
        r_small, d_pen, epi_mode = PRESETS[1][0], PRESETS[1][1], PRESETS[1][2]
        _reset()
    elif k == "3":
        preset_idx = 2
        drift_mode = False
        r_small, d_pen, epi_mode = PRESETS[2][0], PRESETS[2][1], PRESETS[2][2]
        _reset()
    elif k == "4":
        preset_idx = 3
        drift_mode = False
        r_small, d_pen, epi_mode = PRESETS[3][0], PRESETS[3][1], PRESETS[3][2]
        _reset()
    elif k == "5":
        preset_idx = 4
        drift_mode = True
        epi_mode = False
        d_pen = 0.75
        _reset()


if __name__ == "__main__":
    py5.run_sketch()
