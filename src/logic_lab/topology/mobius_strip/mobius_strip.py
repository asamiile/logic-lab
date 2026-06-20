"""
Möbius Strip
A non-orientable surface with only one side and one edge.
Parametrized as:
  x = (R + s·cos(t/2)) · cos(t)
  y = (R + s·cos(t/2)) · sin(t)
  z =  s · sin(t/2)
where t ∈ [0, 2π) walks around the loop and s ∈ [-w, w] crosses the width.

Rendered as a triangular mesh with Gouraud-like shading from a fixed light:
each triangle's z-depth determines draw order (painter's algorithm) and
the surface normal determines brightness. Color cycles around the strip to
reveal that opposite edges of the original rectangle meet with a twist.

Controls:
  Space   — pause / resume rotation
  w / W   — narrow / widen the strip
  n / N   — fewer / more mesh divisions
  c       — cycle colormap (rainbow / normal / monochrome)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
R = 1.8  # major radius of the loop
STRIP_W = 0.7  # half-width of the strip

N_T = 120  # divisions around the loop
N_S = 20  # divisions across the width

ROT_Y_SPEED = 0.009
ROT_X = 0.35  # fixed tilt

paused = False
colormap_idx = 0
CMAPS = ["rainbow", "normal", "mono"]


def _build_mesh(w: float, nt: int, ns: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (verts, normals, tvals) for the Möbius mesh."""
    t = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    s = np.linspace(-w, w, ns)
    T, S = np.meshgrid(t, s, indexing="ij")  # (nt, ns)

    x = (R + S * np.cos(T / 2)) * np.cos(T)
    y = (R + S * np.cos(T / 2)) * np.sin(T)
    z = S * np.sin(T / 2)

    verts = np.stack([x, y, z], axis=-1)  # (nt, ns, 3)

    # Approximate normals via cross product of two tangent directions
    dT = np.gradient(verts, axis=0)
    dS = np.gradient(verts, axis=1)
    normals = np.cross(dT, dS)
    nlen = np.linalg.norm(normals, axis=-1, keepdims=True) + 1e-9
    normals /= nlen

    return verts, normals, T


def _ry_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rx_mat(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


_rot_y = 0.0
_verts, _normals, _T_grid = _build_mesh(STRIP_W, N_T, N_S)
LIGHT = np.array([0.4, 0.6, 1.0])
LIGHT /= np.linalg.norm(LIGHT)


def _rebuild() -> None:
    global _verts, _normals, _T_grid
    _verts, _normals, _T_grid = _build_mesh(STRIP_W, N_T, N_S)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def draw() -> None:
    global _rot_y

    if not paused:
        _rot_y += ROT_Y_SPEED

    py5.background(12, 12, 22)

    R_mat = _rx_mat(ROT_X) @ _ry_mat(_rot_y)
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    scale = min(WIDTH, HEIGHT) * 0.22

    nt, ns = _verts.shape[:2]

    # Collect quads, compute depth and brightness
    quads = []
    for i in range(nt):
        i1 = (i + 1) % nt
        for j in range(ns - 1):
            j1 = j + 1
            v00 = _verts[i, j]
            v10 = _verts[i1, j]
            v01 = _verts[i, j1]
            v11 = _verts[i1, j1]

            # Rotate
            rv00 = R_mat @ v00
            rv10 = R_mat @ v10
            rv01 = R_mat @ v01
            rv11 = R_mat @ v11

            # Depth = average z after rotation
            depth = (rv00[2] + rv10[2] + rv01[2] + rv11[2]) * 0.25

            # Normal brightness
            n_avg = R_mat @ (
                (_normals[i, j] + _normals[i1, j] + _normals[i, j1] + _normals[i1, j1]) * 0.25
            )
            bri = float(np.dot(n_avg, LIGHT))

            # t-value for hue
            t_val = float(_T_grid[i, j])

            # Screen coordinates
            sx00 = rv00[0] * scale + cx
            sy00 = -rv00[1] * scale + cy
            sx10 = rv10[0] * scale + cx
            sy10 = -rv10[1] * scale + cy
            sx01 = rv01[0] * scale + cx
            sy01 = -rv01[1] * scale + cy
            sx11 = rv11[0] * scale + cx
            sy11 = -rv11[1] * scale + cy

            quads.append((depth, bri, t_val, sx00, sy00, sx10, sy10, sx01, sy01, sx11, sy11))

    # Painter's algorithm: back-to-front
    quads.sort(key=lambda q: q[0])

    py5.no_stroke()
    for depth, bri, t_val, sx00, sy00, sx10, sy10, sx01, sy01, sx11, sy11 in quads:
        light_frac = max(0.15, min(1.0, 0.5 + bri * 0.6))

        if colormap_idx == 0:  # rainbow around the strip
            hue = (t_val / (2 * np.pi)) * 360.0
            py5.color_mode(py5.HSB, 360, 100, 100)
            py5.fill(hue % 360, 75, light_frac * 90)
        elif colormap_idx == 1:  # normal-map-like
            n = R_mat @ (_normals[0, 0])  # rough per-quad normal
            r = int((n[0] * 0.5 + 0.5) * 255 * light_frac)
            g = int((n[1] * 0.5 + 0.5) * 255 * light_frac)
            b = int((n[2] * 0.5 + 0.5) * 255 * light_frac)
            py5.color_mode(py5.RGB)
            py5.fill(r, g, b)
        else:  # monochrome
            v = int(light_frac * 210)
            py5.color_mode(py5.RGB)
            py5.fill(v, v + 10, v + 30)

        py5.quad(sx00, sy00, sx10, sy10, sx11, sy11, sx01, sy01)

    py5.color_mode(py5.RGB)
    py5.fill(180, 200, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Möbius strip  cmap:{CMAPS[colormap_idx]}  "
        f"w:{STRIP_W:.2f}  N_T:{N_T}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global paused, colormap_idx, STRIP_W, N_T, N_S
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "c":
        colormap_idx = (colormap_idx + 1) % len(CMAPS)
    elif k == "w":
        STRIP_W = max(0.1, STRIP_W - 0.1)
        _rebuild()
    elif k == "W":
        STRIP_W = min(1.5, STRIP_W + 0.1)
        _rebuild()
    elif k == "n":
        N_T = max(20, N_T - 20)
        N_S = max(4, N_S - 4)
        _rebuild()
    elif k == "N":
        N_T = min(240, N_T + 20)
        N_S = min(40, N_S + 4)
        _rebuild()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "mobius_strip_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
