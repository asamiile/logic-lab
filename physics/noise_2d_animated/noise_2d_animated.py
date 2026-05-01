from pathlib import Path

import numpy as np
import py5


SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

OCTAVES = 4
FALLOFF = 0.5
XOFF = 0.01
YOFF = 0.01

speed = 0.0


def _hsv_to_rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    i = (h * 6).astype(int) % 6
    f = h * 6 - (h * 6).astype(int)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    cases = [i == k for k in range(6)]
    r = np.select(cases, [v, q, p, p, t, v])
    g = np.select(cases, [t, v, v, q, p, p])
    b = np.select(cases, [p, p, t, v, v, q])
    return np.stack([r, g, b], axis=-1)


def setup() -> None:
    py5.size(640, 240)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global speed
    py5.noise_detail(OCTAVES, FALLOFF)

    pw, ph = py5.pixel_width, py5.pixel_height
    xx, yy = np.meshgrid(
        np.linspace(0, py5.width * XOFF, pw, endpoint=False),
        np.linspace(0, py5.height * YOFF, ph, endpoint=False),
    )
    noise_vals = py5.noise(xx, yy, speed)

    hue = noise_vals
    val = np.minimum(noise_vals * 2.55, 1.0)
    sat = np.ones_like(noise_vals)

    rgb = (_hsv_to_rgb(hue, sat, val) * 255).astype(np.uint8)
    py5.set_np_pixels(rgb, bands="RGB")

    speed += 0.01


def key_pressed() -> None:
    if py5.key == "r":
        py5.noise_seed(int(py5.random(1_000_000)))
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "noise_2d_animated_####.png"))


py5.run_sketch()
