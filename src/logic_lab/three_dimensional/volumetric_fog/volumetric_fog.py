"""
Volumetric Fog Rendering.

Simulates volumetric fog/cloud by ray-marching through a 3D Perlin-noise
density field. Each screen pixel casts a ray into the volume; the
accumulated opacity and color along the ray is blended to produce
soft, atmospheric depth.

Technique:
    - Ray marching: step along each view ray accumulating density
    - Density field: 3D FBM (layered Perlin noise) animated over time
    - Beer-Lambert: exp(-density * step) approximation for light scattering
    - Directional light: contribution from a fixed sun direction

This is a CPU-based reference implementation; it is deliberately slow
(low resolution) to remain runnable in Python without shaders.
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

RENDER_W = 120  # Internal render resolution (upscaled for display)
RENDER_H = 90
DISPLAY_SCALE = 6  # Each render pixel → 6x6 display pixels
STEPS = 24  # Ray marching steps
STEP_SIZE = 0.12

FOV = 60.0
FOG_COLOR = np.array([0.85, 0.92, 1.0], dtype=np.float32)  # Blue-white
SKY_COLOR = np.array([0.15, 0.22, 0.45], dtype=np.float32)
SUN_DIR = np.array([0.6, 0.8, 0.4], dtype=np.float32)
SUN_DIR /= np.linalg.norm(SUN_DIR)
SUN_COLOR = np.array([1.0, 0.95, 0.75], dtype=np.float32)

paused = False
frame_pixels: np.ndarray


# ---- Noise ---------------------------------------------------------------


def _fade(t: np.ndarray) -> np.ndarray:
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
    return a + t * (b - a)


def _grad3(h: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    h = h & 15
    u = np.where(h < 8, x, y)
    v = np.where(h < 4, y, np.where((h == 12) | (h == 14), x, z))
    return np.where(h & 1, -u, u) + np.where(h & 2, -v, v)


_PERM = np.array(np.random.RandomState(0).permutation(256).tolist() * 2, dtype=np.int32)


def _perlin3(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
    xi = np.floor(x).astype(np.int32) & 255
    yi = np.floor(y).astype(np.int32) & 255
    zi = np.floor(z).astype(np.int32) & 255
    xf = x - np.floor(x)
    yf = y - np.floor(y)
    zf = z - np.floor(z)
    u, v, w = _fade(xf), _fade(yf), _fade(zf)

    p = _PERM
    a = p[xi] + yi
    aa, ab = p[a] + zi, p[a + 1] + zi
    b = p[xi + 1] + yi
    ba, bb = p[b] + zi, p[b + 1] + zi

    return _lerp(
        _lerp(
            _lerp(_grad3(p[aa], xf, yf, zf), _grad3(p[ba], xf - 1, yf, zf), u),
            _lerp(_grad3(p[ab], xf, yf - 1, zf), _grad3(p[bb], xf - 1, yf - 1, zf), u),
            v,
        ),
        _lerp(
            _lerp(_grad3(p[aa + 1], xf, yf, zf - 1), _grad3(p[ba + 1], xf - 1, yf, zf - 1), u),
            _lerp(
                _grad3(p[ab + 1], xf, yf - 1, zf - 1), _grad3(p[bb + 1], xf - 1, yf - 1, zf - 1), u
            ),
            v,
        ),
        w,
    )


def _fbm3(x: np.ndarray, y: np.ndarray, z: np.ndarray, octaves: int = 4) -> np.ndarray:
    val = np.zeros_like(x)
    amp = 0.5
    freq = 1.0
    for _ in range(octaves):
        val += amp * _perlin3(x * freq, y * freq, z * freq)
        amp *= 0.5
        freq *= 2.0
    return val


# ---- Rendering -----------------------------------------------------------


def _render(t: float) -> np.ndarray:
    """Render one frame into an (H, W, 3) float32 array."""
    aspect = RENDER_W / RENDER_H
    half_fov = np.radians(FOV / 2)

    # Generate ray directions
    xs = (np.arange(RENDER_W) + 0.5) / RENDER_W * 2 - 1
    ys = -((np.arange(RENDER_H) + 0.5) / RENDER_H * 2 - 1)
    xs, ys = np.meshgrid(xs, ys)
    zs = np.full_like(xs, -1.0 / np.tan(half_fov))

    # Normalize
    lens = np.sqrt(xs**2 + ys**2 + zs**2)
    rd_x = xs / lens * aspect
    rd_y = ys / lens
    rd_z = zs / lens

    # Camera position (slow drift)
    ro_x = np.sin(t * 0.3) * 0.5
    ro_y = 0.2 + np.sin(t * 0.17) * 0.1
    ro_z = -2.0 + t * 0.1

    img = np.ones((RENDER_H, RENDER_W, 3), dtype=np.float32) * SKY_COLOR

    transmittance = np.ones((RENDER_H, RENDER_W), dtype=np.float32)
    accumulated_color = np.zeros((RENDER_H, RENDER_W, 3), dtype=np.float32)

    for s in range(STEPS):
        depth = s * STEP_SIZE + 0.1
        px = ro_x + rd_x * depth
        py = ro_y + rd_y * depth
        pz = ro_z + rd_z * depth

        density_raw = _fbm3(px * 0.8, py * 0.8 + t * 0.05, pz * 0.8, octaves=3)
        density = np.clip(density_raw * 0.8 + 0.1, 0.0, 1.0) * 0.4

        # Sun contribution
        light = np.clip(
            _perlin3(px + SUN_DIR[0] * 0.3, py + SUN_DIR[1] * 0.3, pz + SUN_DIR[2] * 0.3) * 0.5
            + 0.7,
            0.0,
            1.0,
        )
        step_color = (
            FOG_COLOR[np.newaxis, np.newaxis, :] * light[:, :, np.newaxis]
            + SUN_COLOR[np.newaxis, np.newaxis, :] * (1 - light[:, :, np.newaxis]) * 0.3
        )

        absorption = np.exp(-density * STEP_SIZE)
        scatter = transmittance * (1.0 - absorption)

        accumulated_color += scatter[:, :, np.newaxis] * step_color
        transmittance *= absorption

    img = accumulated_color + transmittance[:, :, np.newaxis] * SKY_COLOR
    return np.clip(img, 0.0, 1.0)


def setup() -> None:
    global frame_pixels
    py5.size(RENDER_W * DISPLAY_SCALE, RENDER_H * DISPLAY_SCALE)
    py5.no_stroke()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    frame_pixels = np.zeros((RENDER_H, RENDER_W, 3), dtype=np.float32)


def draw() -> None:
    global frame_pixels

    if not paused:
        t = py5.frame_count * 0.05
        frame_pixels = _render(t)

    py5.load_pixels()
    pixels = py5.pixels
    w = py5.width

    for ry in range(RENDER_H):
        for rx in range(RENDER_W):
            r = int(frame_pixels[ry, rx, 0] * 255)
            g = int(frame_pixels[ry, rx, 1] * 255)
            b = int(frame_pixels[ry, rx, 2] * 255)
            c = py5.color(r, g, b)
            for dy in range(DISPLAY_SCALE):
                for dx in range(DISPLAY_SCALE):
                    px = rx * DISPLAY_SCALE + dx
                    py_ = ry * DISPLAY_SCALE + dy
                    pixels[py_ * w + px] = c

    py5.update_pixels()

    py5.fill(220)
    py5.text_size(12)
    py5.text(f"Volumetric Fog | frame {py5.frame_count} | SPACE=pause S=save", 10, 18)


def key_pressed() -> None:
    global paused
    if py5.key == " ":
        paused = not paused
    elif py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "volumetric_fog_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
