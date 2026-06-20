"""
Van der Pol Oscillator — Limit Cycle Behavior
A nonlinear oscillator governed by:
  d²x/dt² − μ(1 − x²)·dx/dt + x = A·cos(ωt)

The term μ(1 − x²)·dx/dt is nonlinear damping:
  - When |x| < 1, damping is negative → energy is injected
  - When |x| > 1, damping is positive → energy is dissipated
  - A limit cycle emerges, oscillating with constant amplitude

Unforced (A=0): pure limit cycle
Forced (A>0): rich dynamics including period-doubling, chaos, entrainment

Visualized as multiple coupled oscillators with different (μ, A, ω):
  - Left: (x, y) phase portrait for one oscillator
  - Center: three-panel time series for multiple oscillators
  - Right: Poincaré section (z-plane stroboscopic sampling) showing periodicity

Controls:
  m/M       — decrease / increase μ (nonlinearity strength)
  a/A       — decrease / increase forcing amplitude
  f/F       — decrease / increase forcing frequency
  Space     — pause / resume
  s         — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 1200, 600
PANEL_W = WIDTH // 3

MU = 0.5
FORCE_AMP = 0.3
FORCE_FREQ = 0.5

DT = 0.01

paused = False

# State: x, dx/dt for N oscillators
N_OSC = 3
_x: np.ndarray  # (N_OSC,)
_v: np.ndarray  # (N_OSC,)
_t = 0.0
_history: list  # time series history per oscillator


def _reset() -> None:
    global _x, _v, _t, _history
    _x = np.random.uniform(-0.5, 0.5, N_OSC)
    _v = np.random.uniform(-0.5, 0.5, N_OSC)
    _t = 0.0
    _history = [[] for _ in range(N_OSC)]


def _step() -> None:
    global _x, _v, _t
    # Van der Pol: d²x/dt² = μ(1 − x²)·dx/dt − x + A·cos(ωt)
    for i in range(N_OSC):
        accel = MU * (1 - _x[i] ** 2) * _v[i] - _x[i] + FORCE_AMP * np.cos(FORCE_FREQ * _t)
        _v[i] = _v[i] + DT * accel
        _x[i] = _x[i] + DT * _v[i]

    for i in range(N_OSC):
        _history[i].append((_t, _x[i], _v[i]))
        if len(_history[i]) > 1000:
            _history[i].pop(0)

    _t += DT


def _draw_phase_portrait() -> None:
    py5.push_matrix()
    py5.translate(0, 0)

    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, PANEL_W, HEIGHT)

    # Phase portrait: (x, v) with x in [-3, 3], v in [-3, 3]
    margin = 40
    inner_w = PANEL_W - margin * 2
    inner_h = HEIGHT - margin * 2

    def to_screen(x_val: float, v_val: float) -> tuple[float, float]:
        px = margin + (x_val + 3) / 6 * inner_w
        py = HEIGHT - margin - (v_val + 3) / 6 * inner_h
        return px, py

    # Axes
    py5.stroke(60, 80, 100)
    py5.stroke_weight(1)
    x0, y0 = to_screen(-3, 0)
    x1, y1 = to_screen(3, 0)
    py5.line(x0, y0, x1, y1)
    x0, y0 = to_screen(0, -3)
    x1, y1 = to_screen(0, 3)
    py5.line(x0, y0, x1, y1)

    # Draw limit cycle for current parameters
    py5.stroke(80, 200, 180)
    py5.stroke_weight(1.2)
    py5.no_fill()
    px, py2 = to_screen(_x[0], _v[0])
    py5.circle(float(px), float(py2), 8.0)

    # Recent trail
    if len(_history[0]) > 1:
        py5.stroke(100, 200, 160, 80)
        py5.stroke_weight(1)
        for j in range(1, len(_history[0])):
            x_j0, v_j0 = _history[0][j - 1][1], _history[0][j - 1][2]
            x_j1, v_j1 = _history[0][j][1], _history[0][j][2]
            px0, py0 = to_screen(x_j0, v_j0)
            px1, py1 = to_screen(x_j1, v_j1)
            py5.line(px0, py0, px1, py1)

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("Phase space", margin, 18)

    py5.pop_matrix()


def _draw_timeseries() -> None:
    py5.push_matrix()
    py5.translate(PANEL_W, 0)

    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, PANEL_W, HEIGHT)

    margin = 20
    inner_w = PANEL_W - margin * 2
    inner_h = (HEIGHT - margin * 4) // 3

    for osc_idx in range(N_OSC):
        y_offset = margin + osc_idx * (inner_h + margin)

        py5.push_matrix()
        py5.translate(0, y_offset)

        # Axes
        py5.stroke(50, 70, 90)
        py5.stroke_weight(1)
        py5.line(margin, inner_h, PANEL_W - margin, inner_h)
        py5.line(margin, 0, margin, inner_h)

        # Time series
        hist = _history[osc_idx]
        if len(hist) > 1:
            py5.stroke(100 + osc_idx * 50, 180, 220)
            py5.stroke_weight(1.2)
            n = len(hist)
            for j in range(1, n):
                x_j0, v_j0 = hist[j - 1][1], hist[j - 1][2]
                x_j1, v_j1 = hist[j][1], hist[j][2]
                t_j0 = hist[j - 1][0]
                t_j1 = hist[j][0]
                t_min = hist[0][0]
                t_max = hist[-1][0]
                t_range = max(t_max - t_min, 1.0)

                px0 = margin + (t_j0 - t_min) / t_range * inner_w
                px1 = margin + (t_j1 - t_min) / t_range * inner_w
                py0 = inner_h - (v_j0 + 3) / 6 * inner_h
                py1 = inner_h - (v_j1 + 3) / 6 * inner_h
                py5.line(px0, py0, px1, py1)

        py5.pop_matrix()

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("Time series (v vs t)", PANEL_W + margin, 18)

    py5.pop_matrix()


def _draw_poincare() -> None:
    py5.push_matrix()
    py5.translate(PANEL_W * 2, 0)

    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, PANEL_W, HEIGHT)

    margin = 40
    inner_w = PANEL_W - margin * 2
    inner_h = HEIGHT - margin * 2

    # Poincaré section: collect (x, v) samples when phase = 0 mod 2π
    py5.stroke(50, 70, 90)
    py5.stroke_weight(1)
    # x-axis
    x0 = margin + inner_w * 0.5
    py5.line(x0, HEIGHT - margin, x0, margin)
    # v-axis
    py5.line(
        margin, HEIGHT - margin - inner_h * 0.5, PANEL_W - margin, HEIGHT - margin - inner_h * 0.5
    )

    # Plot points (x, v)
    py5.fill(200, 150, 255)
    py5.no_stroke()
    for osc_idx in range(N_OSC):
        for t_samp, x_samp, v_samp in _history[osc_idx][::5]:  # sample every 5
            px = margin + (x_samp + 3) / 6 * inner_w
            py2 = HEIGHT - margin - (v_samp + 3) / 6 * inner_h
            py5.circle(float(px), float(py2), 2.5)

    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("Poincaré section", margin + PANEL_W * 2, 18)

    py5.pop_matrix()


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        for _ in range(5):
            _step()

    _draw_phase_portrait()
    _draw_timeseries()
    _draw_poincare()

    py5.fill(180, 200, 240)
    py5.no_stroke()
    py5.text_size(11)
    py5.text(
        f"Van der Pol  μ={MU:.2f}  A={FORCE_AMP:.2f}  ω={FORCE_FREQ:.3f}  "
        f"{'PAUSED' if paused else ''}",
        WIDTH // 2 - 150,
        HEIGHT - 6,
    )


def key_pressed() -> None:
    global paused, MU, FORCE_AMP, FORCE_FREQ
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "m":
        MU = max(0.1, round(MU - 0.1, 2))
        _reset()
    elif k == "M":
        MU = min(3.0, round(MU + 0.1, 2))
        _reset()
    elif k == "a":
        FORCE_AMP = max(0.0, round(FORCE_AMP - 0.05, 2))
        _reset()
    elif k == "A":
        FORCE_AMP = min(2.0, round(FORCE_AMP + 0.05, 2))
        _reset()
    elif k == "f":
        FORCE_FREQ = max(0.0, round(FORCE_FREQ - 0.05, 3))
        _reset()
    elif k == "F":
        FORCE_FREQ = min(3.0, round(FORCE_FREQ + 0.05, 3))
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "vdp_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
