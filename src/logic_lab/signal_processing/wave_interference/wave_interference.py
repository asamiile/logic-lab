"""
2D Wave Interference
Multiple point sources emit circular waves:
  amplitude(x,y,t) = Σᵢ  sin(k·rᵢ  −  ω·t  +  φᵢ)

where rᵢ = distance from source i to pixel (x,y).

Superposition creates standing patterns, nodal lines, and moving fringes
identical to water waves, light through slits, and acoustic resonance.

Sources can be added interactively by clicking.
The default layout matches a classic double-slit experiment.

Color:
  negative amplitude → deep blue
  zero              → black
  positive amplitude → warm orange / white

Modes:
  1  snapshot     — instantaneous wave field (animated t)
  2  intensity    — time-averaged  Σ amplitude² (builds up slowly)
  3  phase map    — color by phase at each point

Controls:
  1-3         — display mode
  click       — add source at cursor
  r           — reset to 2-source default
  Space       — pause / resume time
  +/-         — increase / decrease wavelength
  s           — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
LAMBDA = 60.0  # wavelength in pixels
OMEGA = 0.06  # angular velocity (radians per frame)

mode = 1
paused = False
_t = 0.0

_sources: list  # list of (x, y, phase)

# Precomputed pixel coordinate grids
_gx: np.ndarray
_gy: np.ndarray

# Intensity accumulator for mode 2
_intensity: np.ndarray
_intensity_frames = 0


def _reset() -> None:
    global _sources, _intensity, _intensity_frames, _t
    _sources = [
        (WIDTH // 2 - 80, HEIGHT // 2, 0.0),
        (WIDTH // 2 + 80, HEIGHT // 2, 0.0),
    ]
    _intensity = np.zeros((py5.pixel_height, py5.pixel_width), dtype=np.float32)
    _intensity_frames = 0
    _t = 0.0


def _wave_field() -> np.ndarray:
    k = 2.0 * np.pi / LAMBDA
    field = np.zeros((py5.pixel_height, py5.pixel_width), dtype=np.float32)
    for sx, sy, phi in _sources:
        r = np.sqrt((_gx - sx) ** 2 + (_gy - sy) ** 2) + 1e-9
        field += np.sin(k * r - OMEGA * _t + phi) / np.sqrt(r / 30.0 + 1.0)
    return field


def _render(field: np.ndarray) -> None:
    if mode == 1:
        t = np.clip(field / (len(_sources) * 0.8), -1.0, 1.0)
        pos = np.clip(t, 0, 1)
        neg = np.clip(-t, 0, 1)
        r8 = np.clip(pos * 255 + neg * 30, 0, 255).astype(np.uint8)
        g8 = np.clip(pos * 160, 0, 255).astype(np.uint8)
        b8 = np.clip(neg * 255 + pos * 20, 0, 255).astype(np.uint8)

    elif mode == 2:
        t = np.clip(_intensity / (_intensity_frames * len(_sources) * 0.5 + 1e-9), 0, 1)
        r8 = np.clip(t * 255, 0, 255).astype(np.uint8)
        g8 = np.clip(t * 200, 0, 255).astype(np.uint8)
        b8 = np.clip((1 - t) * 120 + t * 80, 0, 255).astype(np.uint8)

    else:  # phase map
        k = 2.0 * np.pi / LAMBDA
        phase = np.zeros_like(field)
        for sx, sy, phi in _sources:
            r = np.sqrt((_gx - sx) ** 2 + (_gy - sy) ** 2) + 1e-9
            phase += (k * r + phi) % (2 * np.pi)
        phase = (phase / len(_sources)) % (2 * np.pi) / (2 * np.pi)
        h6 = phase * 6.0
        i6 = h6.astype(np.int32) % 6
        f6 = h6 - i6
        q = 1.0 - f6
        r_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [1, q, 0, 0, f6], 1)
        g_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [f6, 1, 1, q, 0], 0)
        b_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [0, 0, f6, 1, 1], q)
        r8 = (r_f * 220).astype(np.uint8)
        g8 = (g_f * 220).astype(np.uint8)
        b8 = (b_f * 220).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()


def setup() -> None:
    global _gx, _gy
    py5.size(WIDTH, HEIGHT)
    ph, pw = py5.pixel_height, py5.pixel_width
    xs = np.arange(pw, dtype=np.float32)
    ys = np.arange(ph, dtype=np.float32)
    _gx = np.tile(xs, (ph, 1))
    _gy = np.tile(ys[:, None], (1, pw))
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global _t, _intensity, _intensity_frames

    if not paused:
        _t += 1.0

    field = _wave_field()

    if mode == 2 and not paused:
        _intensity += field * field
        _intensity_frames += 1

    _render(field)

    # Source markers
    py5.no_fill()
    py5.stroke(255, 200, 100, 180)
    py5.stroke_weight(1.5)
    for sx, sy, _ in _sources:
        py5.circle(sx, sy, 12)

    mode_names = ["", "snapshot", "intensity", "phase"]
    py5.fill(220, 235, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Wave interference  sources:{len(_sources)}  λ={LAMBDA:.0f}px  "
        f"mode:{mode_names[mode]}  click=add source  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def mouse_pressed() -> None:
    _sources.append((float(py5.mouse_x), float(py5.mouse_y), 0.0))
    # Reset intensity accumulator when topology changes
    global _intensity, _intensity_frames
    _intensity[:] = 0.0
    _intensity_frames = 0


def key_pressed() -> None:
    global mode, paused, LAMBDA, _intensity, _intensity_frames
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        mode = 1
    elif k == "2":
        mode = 2
        _intensity[:] = 0.0
        _intensity_frames = 0
    elif k == "3":
        mode = 3
    elif k == "+":
        LAMBDA = min(200.0, LAMBDA + 5.0)
    elif k == "-":
        LAMBDA = max(15.0, LAMBDA - 5.0)
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"wave_m{mode}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
