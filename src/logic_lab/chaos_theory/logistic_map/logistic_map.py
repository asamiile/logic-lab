"""
Logistic Map — Period-Doubling Route to Chaos
The logistic map  x_{n+1} = r·x_n·(1 − x_n)  is perhaps the simplest
equation that exhibits chaos. It was studied by May (1976) to model
population dynamics.

Three views run simultaneously:
  LEFT   — Bifurcation diagram: for each r in [2.5, 4.0], iterate 500 times
            (transient), then plot the next 200 attracting values.
            Period-1 → Period-2 → Period-4 → ... → Chaos at r ≈ 3.57.
            The Feigenbaum constant δ ≈ 4.669 governs the doubling rate.

  CENTER — Cobweb plot: for the currently selected r, trace the orbit as a
            staircase between the parabola y=rx(1-x) and the diagonal y=x.
            Shows how orbits converge to attractors or wander chaotically.

  RIGHT  — Time series: x_n vs n for the current r, up to 200 steps.
            Shows fixed point / period-2 / period-4 / chaotic bands clearly.

Mouse:
  Hover left panel  — move vertical r-cursor (updates center & right panels)
  Click left panel  — lock r at that position

Controls:
  Space   — pause / resume orbit animation
  r       — reset / randomize starting x₀
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 1200, 600

R_MIN, R_MAX = 2.5, 4.0
BIFURC_WARMUP = 500
BIFURC_SAMPLES = 200
BIF_W = WIDTH // 2  # bifurcation panel width
BIF_H = HEIGHT

COBWEB_W = WIDTH // 4
COBWEB_H = HEIGHT

TIME_W = WIDTH // 4
TIME_H = HEIGHT

COB_X = BIF_W
TIME_X = BIF_W + COBWEB_W

selected_r = 3.5
r_locked = False
paused = False
_cob_orbit: list  # cobweb (x0,y0,x1,y1) segments
_cob_x = 0.4  # current iterate for animation
_cob_step = 0  # step counter for cobweb animation
COB_STEPS = 300  # max steps shown in cobweb

# Precomputed bifurcation data
_bif_r: np.ndarray  # (N_R,)
_bif_xs: np.ndarray  # (N_R, BIFURC_SAMPLES)
N_R = 1000


def _compute_bifurcation() -> None:
    global _bif_r, _bif_xs
    _bif_r = np.linspace(R_MIN, R_MAX, N_R)
    x = np.full(N_R, 0.5)
    for _ in range(BIFURC_WARMUP):
        x = _bif_r * x * (1 - x)
    xs = np.zeros((N_R, BIFURC_SAMPLES))
    for i in range(BIFURC_SAMPLES):
        x = _bif_r * x * (1 - x)
        xs[:, i] = x
    _bif_xs = xs


def _reset_cobweb() -> None:
    global _cob_x, _cob_orbit, _cob_step
    _cob_x = np.random.uniform(0.1, 0.9)
    _cob_orbit = []
    _cob_step = 0


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.frame_rate(60)
    _compute_bifurcation()
    _reset_cobweb()


def _draw_bifurcation() -> None:
    py5.push_matrix()
    py5.translate(0, 0)
    py5.background(8, 10, 20)

    # Axes
    py5.stroke(60, 80, 100)
    py5.stroke_weight(1)
    # x-axis (r values) at bottom
    py5.line(30, BIF_H - 30, BIF_W - 10, BIF_H - 30)
    # y-axis (x values) at left
    py5.line(30, 10, 30, BIF_H - 30)

    # Labels
    py5.fill(150, 180, 210)
    py5.text_size(10)
    for rv in [2.5, 3.0, 3.5, 4.0]:
        px = int(30 + (rv - R_MIN) / (R_MAX - R_MIN) * (BIF_W - 40))
        py5.text(f"{rv:.1f}", px - 8, BIF_H - 14)
        py5.stroke(40, 60, 80)
        py5.line(px, BIF_H - 30, px, BIF_H - 25)
    for xv in [0.0, 0.25, 0.5, 0.75, 1.0]:
        py2 = int(BIF_H - 30 - xv * (BIF_H - 40))
        py5.text(f"{xv:.2f}", 1, py2 + 4)

    # Title
    py5.fill(200, 220, 255)
    py5.text_size(11)
    py5.text("Bifurcation Diagram", 35, 18)
    py5.text("r →", BIF_W - 30, BIF_H - 14)
    py5.text("x", 12, 22)

    # Plot attractor values
    py5.stroke_weight(1)
    py5.no_fill()
    for ri in range(N_R):
        px = int(30 + ri / N_R * (BIF_W - 40))
        r_val = _bif_r[ri]
        # Color: blue in ordered region, cyan→red near chaos
        chaos_t = max(0.0, (r_val - 3.5) / 0.5)
        rc = int(30 + chaos_t * 220)
        gc = int(160 - chaos_t * 120)
        bc = int(220 - chaos_t * 180)
        py5.stroke(rc, gc, bc, 140)
        for s in range(BIFURC_SAMPLES):
            xv = _bif_xs[ri, s]
            py2 = int(BIF_H - 30 - xv * (BIF_H - 40))
            py5.point(px, py2)

    # r cursor line
    cursor_px = int(30 + (selected_r - R_MIN) / (R_MAX - R_MIN) * (BIF_W - 40))
    py5.stroke(255, 220, 60, 200)
    py5.stroke_weight(1.5)
    py5.line(cursor_px, 10, cursor_px, BIF_H - 30)
    py5.fill(255, 220, 60)
    py5.text_size(10)
    py5.text(f"r={selected_r:.4f}", cursor_px + 3, 22)

    py5.pop_matrix()


def _draw_cobweb() -> None:
    py5.push_matrix()
    py5.translate(COB_X, 0)

    # Dark background for cobweb panel
    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, COBWEB_W, COBWEB_H)

    margin = 30
    inner_w = COBWEB_W - margin * 2
    inner_h = COBWEB_H - margin * 2

    def to_screen(x: float, y: float) -> tuple[float, float]:
        return margin + x * inner_w, COBWEB_H - margin - y * inner_h

    # Axes
    py5.stroke(50, 70, 90)
    py5.stroke_weight(1)
    ax0, ay0 = to_screen(0, 0)
    ax1, ay1 = to_screen(1, 0)
    py5.line(ax0, ay0, ax1, ay1)
    ax0, ay0 = to_screen(0, 0)
    ax1, ay1 = to_screen(0, 1)
    py5.line(ax0, ay0, ax1, ay1)

    # Parabola  y = r·x·(1-x)
    n_pts = 200
    xs_p = np.linspace(0, 1, n_pts)
    ys_p = selected_r * xs_p * (1 - xs_p)
    py5.stroke(80, 200, 255)
    py5.stroke_weight(1.5)
    for i in range(n_pts - 1):
        x0s, y0s = to_screen(xs_p[i], ys_p[i])
        x1s, y1s = to_screen(xs_p[i + 1], ys_p[i + 1])
        if 0 <= ys_p[i] <= 1 and 0 <= ys_p[i + 1] <= 1:
            py5.line(x0s, y0s, x1s, y1s)

    # Diagonal y = x
    py5.stroke(80, 100, 80)
    py5.stroke_weight(1)
    x0s, y0s = to_screen(0, 0)
    x1s, y1s = to_screen(1, 1)
    py5.line(x0s, y0s, x1s, y1s)

    # Cobweb path
    n_seg = len(_cob_orbit)
    py5.stroke_weight(1.2)
    for i, (sx0, sy0, sx1, sy1) in enumerate(_cob_orbit):
        age = i / max(n_seg, 1)
        alpha = int(60 + age * 180)
        hue_t = age
        r_c = int((1 - hue_t) * 60 + hue_t * 255)
        g_c = int((1 - hue_t) * 220 + hue_t * 60)
        b_c = int((1 - hue_t) * 100 + hue_t * 60)
        py5.stroke(r_c, g_c, b_c, alpha)
        px0, py0 = to_screen(sx0, sy0)
        px1, py1 = to_screen(sx1, sy1)
        py5.line(px0, py0, px1, py1)

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("Cobweb", margin, 18)

    py5.pop_matrix()


def _draw_timeseries() -> None:
    py5.push_matrix()
    py5.translate(TIME_X, 0)

    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, TIME_W, TIME_H)

    N_TS = 150
    x = _cob_x
    # Warm up then record
    for _ in range(50):
        x = selected_r * x * (1 - x)
    ts = []
    for _ in range(N_TS):
        x = selected_r * x * (1 - x)
        ts.append(x)
    ts = np.array(ts)

    margin_l = 20
    margin_b = 30
    margin_t = 30
    inner_w = TIME_W - margin_l - 10
    inner_h = TIME_H - margin_b - margin_t

    # Axes
    py5.stroke(50, 70, 90)
    py5.stroke_weight(1)
    py5.line(margin_l, margin_t, margin_l, TIME_H - margin_b)
    py5.line(margin_l, TIME_H - margin_b, TIME_W - 10, TIME_H - margin_b)

    # Series
    py5.stroke(80, 220, 160)
    py5.stroke_weight(1.3)
    for i in range(1, N_TS):
        x0s = margin_l + (i - 1) / N_TS * inner_w
        x1s = margin_l + i / N_TS * inner_w
        y0s = TIME_H - margin_b - ts[i - 1] * inner_h
        y1s = TIME_H - margin_b - ts[i] * inner_h
        py5.line(x0s, y0s, x1s, y1s)

    # Dots
    py5.fill(80, 220, 160)
    py5.no_stroke()
    for i, v in enumerate(ts):
        xp = margin_l + i / N_TS * inner_w
        yp = TIME_H - margin_b - v * inner_h
        py5.circle(xp, yp, 2.5)

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("Time series", margin_l, 18)
    py5.text("n →", TIME_W - 25, TIME_H - 14)

    py5.pop_matrix()


def draw() -> None:
    global _cob_x, _cob_step, _cob_orbit

    if not paused:
        # Advance cobweb one step per frame
        xn = selected_r * _cob_x * (1 - _cob_x)
        # Vertical: from (_cob_x, _cob_x) → (_cob_x, xn)
        _cob_orbit.append((_cob_x, _cob_x, _cob_x, xn))
        # Horizontal: from (_cob_x, xn) → (xn, xn)
        _cob_orbit.append((_cob_x, xn, xn, xn))
        _cob_x = xn
        _cob_step += 1
        if _cob_step > COB_STEPS:
            _reset_cobweb()
        # Trim to last 120 segments
        if len(_cob_orbit) > 120:
            _cob_orbit = _cob_orbit[-120:]

    _draw_bifurcation()
    _draw_cobweb()
    _draw_timeseries()

    py5.fill(180, 200, 240)
    py5.no_stroke()
    py5.text_size(11)
    py5.text(
        f"Logistic map  r={selected_r:.4f}  {'PAUSED' if paused else ''}",
        BIF_W // 2 - 80,
        HEIGHT - 6,
    )


def mouse_moved() -> None:
    global selected_r
    if not r_locked and py5.mouse_x < BIF_W:
        frac = (py5.mouse_x - 30) / (BIF_W - 40)
        new_r = R_MIN + frac * (R_MAX - R_MIN)
        if R_MIN <= new_r <= R_MAX:
            selected_r = new_r
            _reset_cobweb()


def mouse_pressed() -> None:
    global selected_r, r_locked
    if py5.mouse_x < BIF_W:
        frac = (py5.mouse_x - 30) / (BIF_W - 40)
        new_r = R_MIN + frac * (R_MAX - R_MIN)
        if R_MIN <= new_r <= R_MAX:
            selected_r = new_r
            r_locked = not r_locked
            _reset_cobweb()


def key_pressed() -> None:
    global paused
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset_cobweb()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "logistic_map_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
