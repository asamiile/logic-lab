"""
Kuramoto Model — Spontaneous Synchronization of Coupled Oscillators
N oscillators each have a natural frequency ωᵢ drawn from a Lorentzian
distribution. They are globally (all-to-all) coupled with strength K:

  dθᵢ/dt = ωᵢ + K/N · Σⱼ sin(θⱼ − θᵢ)

The order parameter  r = |1/N Σ exp(iθⱼ)|  measures synchrony:
  r ≈ 0  → incoherent (phases uniformly spread)
  r ≈ 1  → fully synchronized (all phases locked)

There is a sharp phase transition at a critical coupling:
  Kc = 2 / (π · g(0))
For a Lorentzian g(ω) = γ/π / (ω² + γ²) this gives Kc = 2γ.

Three panels:
  LEFT    — Phase circles: N oscillators shown as dots on a unit circle,
             colored by ωᵢ (blue=slow, red=fast). The order-parameter
             vector (r, ψ) is drawn as a thick arrow. Synchronized clusters
             visibly bunch together.

  CENTER  — r(t) history: order parameter over the last 600 frames.
             Sudden jump near Kc is the synchronization transition.

  RIGHT   — K-sweep snapshot: steady-state ⟨r⟩ vs K from 0 to 4Kc,
             pre-computed. Blue curve = theoretical Kc(K), red dot = current K.

Controls:
  ←/→     — decrease / increase coupling K
  n/N     — fewer / more oscillators
  r       — reshuffle natural frequencies and phases
  Space   — pause / resume
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 1200, 600
PANEL_W = WIDTH // 3

N = 200  # number of oscillators
GAMMA = 1.0  # Lorentzian half-width  → Kc = 2γ
K = 2.0  # coupling strength (start below Kc)
DT = 0.05
HISTORY_LEN = 600
paused = False

_theta: np.ndarray  # (N,) phases
_omega: np.ndarray  # (N,) natural frequencies
_r_hist: list  # order-param history

# Precomputed K-sweep
_K_SWEEP_N = 120
_ksweep_K: np.ndarray
_ksweep_r: np.ndarray


def _init_oscillators() -> None:
    global _theta, _omega, _r_hist
    _theta = np.random.uniform(0, 2 * np.pi, N)
    _omega = np.random.standard_cauchy(N) * GAMMA  # Lorentzian
    _omega = np.clip(_omega, -8, 8)
    _r_hist = []


def _order_param() -> tuple[float, float]:
    z = np.mean(np.exp(1j * _theta))
    return float(abs(z)), float(np.angle(z))


def _step() -> None:
    global _theta
    # Vectorised Kuramoto: (N, N) diff matrix
    diffs = _theta[:, None] - _theta[None, :]  # sin(θⱼ - θᵢ) = -sin(diffs)
    coupling = -K / N * np.sum(np.sin(diffs), axis=1)
    _theta = (_theta + DT * (_omega + coupling)) % (2 * np.pi)


def _precompute_ksweep() -> None:
    global _ksweep_K, _ksweep_r
    Kc = 2 * GAMMA
    _ksweep_K = np.linspace(0, 4 * Kc, _K_SWEEP_N)
    _ksweep_r = np.zeros(_K_SWEEP_N)
    rng = np.random.default_rng(42)
    n_sw = 150
    omega_sw = rng.standard_cauchy(n_sw) * GAMMA
    omega_sw = np.clip(omega_sw, -6, 6)
    for ki, k_val in enumerate(_ksweep_K):
        th = rng.uniform(0, 2 * np.pi, n_sw)
        for _ in range(400):  # warmup
            d = th[:, None] - th[None, :]
            th = (th + DT * (omega_sw - k_val / n_sw * np.sum(np.sin(d), axis=1))) % (2 * np.pi)
        # Average r over 100 steps
        rs = 0.0
        for _ in range(100):
            d = th[:, None] - th[None, :]
            th = (th + DT * (omega_sw - k_val / n_sw * np.sum(np.sin(d), axis=1))) % (2 * np.pi)
            rs += abs(np.mean(np.exp(1j * th)))
        _ksweep_r[ki] = rs / 100


def _hue_rgb(h: float) -> tuple[int, int, int]:
    h6 = (h % 360) / 60.0
    i = int(h6) % 6
    f = h6 - int(h6)
    q2 = 1.0 - f
    lut = [(1, f, 0), (q2, 1, 0), (0, 1, f), (0, q2, 1), (f, 0, 1), (1, 0, q2)]
    r, g, b = lut[i]
    return int(r * 220), int(g * 220), int(b * 220)


def _draw_circles(r_val: float, psi: float) -> None:
    py5.push_matrix()
    py5.translate(0, 0)
    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, PANEL_W, HEIGHT)

    cx, cy = PANEL_W * 0.5, HEIGHT * 0.5
    radius = min(PANEL_W, HEIGHT) * 0.38

    # Unit circle
    py5.stroke(40, 60, 80)
    py5.stroke_weight(1)
    py5.no_fill()
    py5.circle(cx, cy, radius * 2)

    # Spokes at π/6 intervals
    py5.stroke(25, 40, 55)
    for a in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        py5.line(cx + np.cos(a) * radius, cy + np.sin(a) * radius, cx, cy)

    # Oscillator dots
    omega_range = max(float(np.max(np.abs(_omega))), 1e-3)
    for i in range(N):
        ang = _theta[i]
        px = cx + np.cos(ang) * radius
        py2 = cy + np.sin(ang) * radius
        hue = ((_omega[i] / omega_range) * 0.5 + 0.5) * 240.0  # blue→red
        rc, gc, bc = _hue_rgb(hue)
        py5.fill(rc, gc, bc, 180)
        py5.no_stroke()
        py5.circle(float(px), float(py2), 5.0)

    # Order parameter arrow
    arrow_len = r_val * radius
    ax = cx + np.cos(psi) * arrow_len
    ay = cy + np.sin(psi) * arrow_len
    py5.stroke(255, 230, 60)
    py5.stroke_weight(3)
    py5.line(cx, cy, float(ax), float(ay))

    py5.fill(220, 240, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("Phase circles", 8, 18)
    py5.text(f"r = {r_val:.3f}", 8, 34)

    py5.pop_matrix()


def _draw_history() -> None:
    py5.push_matrix()
    py5.translate(PANEL_W, 0)
    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, PANEL_W, HEIGHT)

    margin = 30
    inner_w = PANEL_W - margin * 2
    inner_h = HEIGHT - margin * 2

    # Axes
    py5.stroke(50, 70, 90)
    py5.stroke_weight(1)
    py5.line(margin, HEIGHT - margin, PANEL_W - margin, HEIGHT - margin)
    py5.line(margin, margin, margin, HEIGHT - margin)

    # Kc reference line
    Kc = 2 * GAMMA
    py5.stroke(80, 80, 40)
    py5.stroke_weight(1)
    py5.line(
        margin,
        int(HEIGHT - margin - 0.5 * inner_h),
        PANEL_W - margin,
        int(HEIGHT - margin - 0.5 * inner_h),
    )
    py5.fill(120, 120, 60)
    py5.text_size(9)
    py5.text("r=0.5", margin + 2, int(HEIGHT - margin - 0.5 * inner_h) - 2)

    # History curve
    n_h = len(_r_hist)
    if n_h > 1:
        py5.stroke(100, 220, 160)
        py5.stroke_weight(1.5)
        for i in range(1, n_h):
            x0 = margin + (i - 1) / HISTORY_LEN * inner_w
            x1 = margin + i / HISTORY_LEN * inner_w
            y0 = HEIGHT - margin - _r_hist[i - 1] * inner_h
            y1 = HEIGHT - margin - _r_hist[i] * inner_h
            py5.line(x0, y0, x1, y1)

    py5.fill(220, 240, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("Order parameter r(t)", margin, 18)
    py5.text_size(9)
    py5.text("1.0", margin - 16, margin + 4)
    py5.text("0.0", margin - 16, HEIGHT - margin + 4)
    Kc_label = f"Kc={Kc:.1f}"
    py5.text(f"K={K:.2f}  {Kc_label}", margin, HEIGHT - 10)

    py5.pop_matrix()


def _draw_ksweep() -> None:
    py5.push_matrix()
    py5.translate(PANEL_W * 2, 0)
    py5.fill(6, 8, 18)
    py5.no_stroke()
    py5.rect(0, 0, PANEL_W, HEIGHT)

    margin = 30
    inner_w = PANEL_W - margin * 2
    inner_h = HEIGHT - margin * 2

    Kc = 2 * GAMMA
    K_max = 4 * Kc

    # Axes
    py5.stroke(50, 70, 90)
    py5.stroke_weight(1)
    py5.line(margin, HEIGHT - margin, PANEL_W - margin, HEIGHT - margin)
    py5.line(margin, margin, margin, HEIGHT - margin)

    # Kc line
    py5.stroke(60, 80, 40)
    kc_x = int(margin + Kc / K_max * inner_w)
    py5.line(kc_x, margin, kc_x, HEIGHT - margin)
    py5.fill(100, 140, 60)
    py5.text_size(9)
    py5.text("Kc", kc_x + 2, margin + 10)

    # Sweep curve
    if len(_ksweep_r) > 1:
        py5.stroke(80, 160, 255)
        py5.stroke_weight(1.5)
        for i in range(1, _K_SWEEP_N):
            x0 = margin + _ksweep_K[i - 1] / K_max * inner_w
            x1 = margin + _ksweep_K[i] / K_max * inner_w
            y0 = HEIGHT - margin - _ksweep_r[i - 1] * inner_h
            y1 = HEIGHT - margin - _ksweep_r[i] * inner_h
            py5.line(x0, y0, x1, y1)

    # Current K marker
    cur_kx = margin + min(K / K_max, 1.0) * inner_w
    cur_r = _r_hist[-1] if _r_hist else 0.0
    cur_ry = HEIGHT - margin - cur_r * inner_h
    py5.fill(255, 80, 80)
    py5.no_stroke()
    py5.circle(float(cur_kx), float(cur_ry), 8.0)

    py5.fill(220, 240, 255)
    py5.no_stroke()
    py5.text_size(11)
    py5.text("⟨r⟩ vs K (sweep)", margin, 18)
    py5.text_size(9)
    py5.text("K →", PANEL_W - 30, HEIGHT - 12)

    py5.pop_matrix()


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    py5.frame_rate(60)
    _init_oscillators()
    _precompute_ksweep()


def draw() -> None:
    if not paused:
        for _ in range(3):
            _step()
        r_val, psi = _order_param()
        _r_hist.append(r_val)
        if len(_r_hist) > HISTORY_LEN:
            _r_hist.pop(0)
    else:
        r_val, psi = _order_param()

    _draw_circles(r_val, psi)
    _draw_history()
    _draw_ksweep()


def key_pressed() -> None:
    global K, N, paused
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _init_oscillators()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "kuramoto_####.png"))
    elif k == "n":
        N = max(20, N - 20)
        _init_oscillators()
    elif k == "N":
        N = min(500, N + 20)
        _init_oscillators()

    kc = py5.key_code
    if kc == py5.LEFT:
        K = max(0.0, round(K - 0.2, 2))
        _r_hist.clear()
    elif kc == py5.RIGHT:
        K = min(12.0, round(K + 0.2, 2))
        _r_hist.clear()


if __name__ == "__main__":
    py5.run_sketch()
