"""
Klein Bottle — Figure-8 Immersion
A Klein bottle is a closed, non-orientable surface with no distinct "inside"
or "outside" — like a Möbius strip but without a boundary edge.

In 4D it embeds without self-intersection, but any rendering into 3D requires
the surface to pass through itself (an immersion, not an embedding).

Figure-8 parametrization (u ∈ [0, 2π], v ∈ [0, 2π]):
  x = (R + cos(u/2)·sin(v) − sin(u/2)·sin(2v)) · cos(u)
  y = (R + cos(u/2)·sin(v) − sin(u/2)·sin(2v)) · sin(u)
  z =      sin(u/2)·sin(v) + cos(u/2)·sin(2v)

The topology means one can continuously slide along the surface from "outside"
to "inside" — color is mapped to this journey (hue by v, brightness by u).

Rendering:
  Painter's algorithm: quads sorted back-to-front by mean z after rotation.
  Two rotation axes (Y and X) animate to show all aspects of the surface.

Controls:
  Space   — pause / resume rotation
  r       — reset view
  n / N   — lower / higher mesh resolution
  1       — hue by v (longitude)
  2       — hue by u (meridian)
  3       — normal-map shading
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900
NU = 80
NV = 40
R = 2.5

rot_y = 0.0
rot_x = 0.35
ROT_Y_SPEED = 0.007
ROT_X_SPEED = 0.003

paused = False
color_mode = 1  # 1=hue-by-v, 2=hue-by-u, 3=normals

_quads: np.ndarray  # (Q, 4, 3)  world-space quad vertices
_c_v: np.ndarray  # (Q,)       mean v parameter
_c_u: np.ndarray  # (Q,)       mean u parameter
_normals: np.ndarray  # (Q, 3)     face normals


def _build_mesh() -> None:
    global _quads, _c_v, _c_u, _normals
    us = np.linspace(0, 2 * np.pi, NU + 1)
    vs = np.linspace(0, 2 * np.pi, NV + 1)
    U, V = np.meshgrid(us, vs, indexing="ij")  # (NU+1, NV+1)

    # Figure-8 immersion
    rim = R + np.cos(U / 2) * np.sin(V) - np.sin(U / 2) * np.sin(2 * V)
    X = rim * np.cos(U)
    Y = rim * np.sin(U)
    Z = np.sin(U / 2) * np.sin(V) + np.cos(U / 2) * np.sin(2 * V)

    pts = np.stack([X, Y, Z], axis=-1)  # (NU+1, NV+1, 3)

    # Build quads from grid
    i0, j0 = np.meshgrid(np.arange(NU), np.arange(NV), indexing="ij")
    i1, j1 = i0 + 1, j0 + 1

    p00 = pts[i0, j0]  # (NU, NV, 3)
    p10 = pts[i1, j0]
    p11 = pts[i1, j1]
    p01 = pts[i0, j1]

    _quads = np.stack([p00, p10, p11, p01], axis=2)  # (NU, NV, 4, 3)
    _quads = _quads.reshape(-1, 4, 3)

    # Mean parameters per quad for coloring
    _c_u = (us[i0] + us[i1]).flatten() * 0.5
    _c_v = (vs[j0] + vs[j1]).flatten() * 0.5

    # Face normals: cross product of diagonals
    d1 = p11 - p00
    d2 = p01 - p10
    n = np.cross(d1.reshape(-1, 3), d2.reshape(-1, 3))
    nm = np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    _normals = n / nm


def _ry_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rx_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    h6 = (h % 360) / 60.0
    i = int(h6) % 6
    f = h6 - int(h6)
    p, q2, t2 = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    lut = [(v, t2, p), (q2, v, p), (p, v, t2), (p, q2, v), (t2, p, v), (v, p, q2)]
    r, g, b = lut[i]
    return int(r * 255), int(g * 255), int(b * 255)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _build_mesh()


def draw() -> None:
    global rot_y, rot_x

    if not paused:
        rot_y += ROT_Y_SPEED
        rot_x += ROT_X_SPEED * 0.4

    R_mat = _rx_mat(rot_x) @ _ry_mat(rot_y)
    rotated = (_quads.reshape(-1, 3) @ R_mat.T).reshape(-1, 4, 3)
    rot_normals = _normals @ R_mat.T

    # Painter's algorithm: sort by mean z of each quad
    mean_z = rotated[:, :, 2].mean(axis=1)
    order = np.argsort(mean_z)

    # Light direction
    light = np.array([0.4, 0.6, 1.0])
    light = light / np.linalg.norm(light)

    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    scale = 90.0

    py5.background(8, 10, 20)
    py5.no_stroke()

    for qi in order:
        verts = rotated[qi]  # (4, 3)
        sx = verts[:, 0] * scale + cx
        sy = -verts[:, 1] * scale + cy

        diff = float(np.clip(np.dot(rot_normals[qi], light), 0, 1))
        amb = 0.25
        shade = amb + (1 - amb) * diff

        if color_mode == 1:
            hue = _c_v[qi] / (2 * np.pi) * 360.0
            r_c, g_c, b_c = _hsv_to_rgb(hue, 0.75, shade)
        elif color_mode == 2:
            hue = _c_u[qi] / (2 * np.pi) * 360.0
            r_c, g_c, b_c = _hsv_to_rgb(hue, 0.65, shade)
        else:
            n = rot_normals[qi]
            r_c = int(np.clip((n[0] + 1) * 0.5 * shade * 255, 0, 255))
            g_c = int(np.clip((n[1] + 1) * 0.5 * shade * 255, 0, 255))
            b_c = int(np.clip((n[2] + 1) * 0.5 * 255 * (0.5 + shade * 0.5), 0, 255))

        py5.fill(r_c, g_c, b_c)
        py5.begin_shape()
        for j in range(4):
            py5.vertex(float(sx[j]), float(sy[j]))
        py5.end_shape(py5.CLOSE)

    cmode_names = ["", "hue-v", "hue-u", "normals"]
    py5.fill(200, 220, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Klein bottle  res:{NU}×{NV}  color:{cmode_names[color_mode]}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, rot_y, rot_x, color_mode, NU, NV
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        rot_y, rot_x = 0.0, 0.35
    elif k == "1":
        color_mode = 1
    elif k == "2":
        color_mode = 2
    elif k == "3":
        color_mode = 3
    elif k == "n":
        NU = max(20, NU - 20)
        NV = max(10, NV - 10)
        _build_mesh()
    elif k == "N":
        NU = min(160, NU + 20)
        NV = min(80, NV + 10)
        _build_mesh()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "klein_bottle_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
