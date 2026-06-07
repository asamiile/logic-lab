"""
Point Cloud Morphing.

Animates smooth transitions between 3D point cloud shapes by linearly
interpolating positions. Shapes are sampled on geometric primitives
(sphere, torus, cube, spiral) and morphed with a time-parameterized
easing function.

The result is a rotating 3D point cloud that dissolves from one form
to another, colored by depth and original shape membership.

Shapes available:
    - sphere: uniform distribution on unit sphere
    - torus: parametric torus surface
    - cube: uniform samples on cube faces
    - helix: helical spring shape
"""

import math
import random
from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH = 800
HEIGHT = 800
NUM_POINTS = 1200
MORPH_DURATION = 120  # Frames to complete one morph
ROTATE_SPEED = 0.007

SHAPE_NAMES = ["sphere", "torus", "cube", "helix"]

current_shape_idx = 0
next_shape_idx = 1
morph_t = 0.0

src_pts: np.ndarray  # (N, 3)
dst_pts: np.ndarray  # (N, 3)
rot_y = 0.0
rot_x = 0.15


def _sample_sphere(n: int) -> np.ndarray:
    rng = np.random.RandomState(0)
    pts = rng.randn(n, 3).astype(np.float32)
    norms = np.linalg.norm(pts, axis=1, keepdims=True)
    return pts / (norms + 1e-9)


def _sample_torus(n: int, R: float = 0.7, r: float = 0.3) -> np.ndarray:
    rng = np.random.RandomState(1)
    u = rng.uniform(0, math.tau, n)
    v = rng.uniform(0, math.tau, n)
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return np.stack([x, y, z], axis=1).astype(np.float32)


def _sample_cube(n: int) -> np.ndarray:
    rng = np.random.RandomState(2)
    pts = []
    per_face = n // 6
    for face in range(6):
        u = rng.uniform(-1, 1, per_face)
        v = rng.uniform(-1, 1, per_face)
        if face == 0:
            pts.append(np.stack([u, v, np.ones(per_face)], axis=1))
        elif face == 1:
            pts.append(np.stack([u, v, -np.ones(per_face)], axis=1))
        elif face == 2:
            pts.append(np.stack([np.ones(per_face), u, v], axis=1))
        elif face == 3:
            pts.append(np.stack([-np.ones(per_face), u, v], axis=1))
        elif face == 4:
            pts.append(np.stack([u, np.ones(per_face), v], axis=1))
        else:
            pts.append(np.stack([u, -np.ones(per_face), v], axis=1))
    out = np.concatenate(pts, axis=0)[:n]
    return (out * 0.7).astype(np.float32)


def _sample_helix(n: int, turns: int = 5) -> np.ndarray:
    t = np.linspace(0, turns * math.tau, n)
    x = np.cos(t) * 0.8
    y = np.sin(t) * 0.8
    z = np.linspace(-0.9, 0.9, n)
    return np.stack([x, y, z], axis=1).astype(np.float32)


_SHAPE_SAMPLERS = {
    "sphere": _sample_sphere,
    "torus": _sample_torus,
    "cube": _sample_cube,
    "helix": _sample_helix,
}


def _get_shape(name: str) -> np.ndarray:
    return _SHAPE_SAMPLERS[name](NUM_POINTS)


def _ease_in_out(t: float) -> float:
    return t * t * (3 - 2 * t)


def _project(pts: np.ndarray, ry: float, rx: float) -> np.ndarray:
    """Rotate and project (N,3) to (N,2) screen coords."""
    cy, sy = math.cos(ry), math.sin(ry)
    cx, sx = math.cos(rx), math.sin(rx)

    # Rotate Y
    x = pts[:, 0] * cy + pts[:, 2] * sy
    y = pts[:, 1]
    z = -pts[:, 0] * sy + pts[:, 2] * cy

    # Rotate X
    y2 = y * cx - z * sx
    z2 = y * sx + z * cx

    # Perspective
    fov = 400.0
    w2 = WIDTH / 2.0
    h2 = HEIGHT / 2.0
    dist = z2 + 3.0
    dist = np.maximum(dist, 0.1)
    sx_ = w2 + x * fov / dist
    sy_ = h2 + y2 * fov / dist
    return np.stack([sx_, sy_, z2], axis=1)


def setup() -> None:
    global src_pts, dst_pts
    py5.size(WIDTH, HEIGHT)
    py5.background(8, 8, 20)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    src_pts = _get_shape(SHAPE_NAMES[current_shape_idx])
    dst_pts = _get_shape(SHAPE_NAMES[next_shape_idx])


def draw() -> None:
    global morph_t, current_shape_idx, next_shape_idx, src_pts, dst_pts, rot_y, rot_x

    py5.background(8, 8, 20)

    # Advance morph
    morph_t = min(morph_t + 1.0 / MORPH_DURATION, 1.0)
    if morph_t >= 1.0:
        morph_t = 0.0
        current_shape_idx = next_shape_idx
        next_shape_idx = (next_shape_idx + 1) % len(SHAPE_NAMES)
        src_pts = dst_pts
        dst_pts = _get_shape(SHAPE_NAMES[next_shape_idx])

    t_eased = _ease_in_out(morph_t)
    pts = src_pts * (1.0 - t_eased) + dst_pts * t_eased

    rot_y += ROTATE_SPEED
    projected = _project(pts, rot_y, rot_x)

    # Sort by depth for painter's algorithm
    order = np.argsort(projected[:, 2])

    py5.stroke_weight(2)
    py5.no_fill()

    for i in order:
        sx, sy, z = projected[i]
        # Depth-based color: far = dark blue, near = bright cyan
        depth_t = float(np.clip((z + 2.0) / 3.0, 0.0, 1.0))
        r = int(30 + depth_t * 80)
        g = int(120 + depth_t * 135)
        b = int(200 + depth_t * 55)
        alpha = int(80 + depth_t * 175)
        py5.stroke(r, g, b, alpha)
        py5.point(float(sx), float(sy))

    py5.fill(200)
    py5.no_stroke()
    py5.text_size(12)
    src_name = SHAPE_NAMES[current_shape_idx]
    dst_name = SHAPE_NAMES[next_shape_idx]
    py5.text(f"Point Cloud | {src_name} → {dst_name} | t={morph_t:.2f} | S=save", 10, 20)


def key_pressed() -> None:
    if py5.key == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "point_cloud_morph_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
