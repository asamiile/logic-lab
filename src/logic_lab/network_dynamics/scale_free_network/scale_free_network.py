"""
Scale-Free Network Growth
Barabási-Albert preferential attachment model: new nodes join by connecting
to m existing nodes with probability proportional to their current degree.
Result: power-law degree distribution — a few "hub" nodes dominate,
most nodes have few connections. Layout via Fruchterman-Reingold spring forces.

Controls:
  Space   — pause / resume growth
  r       — reset
  + / -   — increase / decrease edges-per-new-node (m)
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

M_INIT = 4  # initial fully-connected seed nodes
M_ATTACH = 2  # new edges per arriving node (adjustable)
N_MAX = 180  # stop growing at this node count
GROW_EVERY = 4  # frames between new-node additions

# Force-directed layout constants
K_REP = 5000.0  # repulsion strength
K_ATT = 0.6  # attraction strength (edges)
DAMPING = 0.80  # velocity damping per frame
DT = 0.5  # time step

# State
_adj: np.ndarray  # (N_MAX, N_MAX) adjacency
_pos: np.ndarray  # (N_MAX, 2) positions
_vel: np.ndarray  # (N_MAX, 2) velocities
_deg: np.ndarray  # (N_MAX,) degree
_edges: list  # list of (u, v) tuples
_n: int  # current node count
_frame: int
paused = False
m_attach = M_ATTACH


def _reset() -> None:
    global _adj, _pos, _vel, _deg, _edges, _n, _frame
    _adj = np.zeros((N_MAX, N_MAX), dtype=np.int8)
    _pos = np.random.uniform(-80, 80, (N_MAX, 2)).astype(np.float32)
    _vel = np.zeros((N_MAX, 2), dtype=np.float32)
    _deg = np.zeros(N_MAX, dtype=np.int32)
    _edges = []
    _n = M_INIT
    _frame = 0

    for i in range(M_INIT):
        ang = 2 * np.pi * i / M_INIT
        _pos[i] = [np.cos(ang) * 40, np.sin(ang) * 40]

    for i in range(M_INIT):
        for j in range(i + 1, M_INIT):
            _adj[i, j] = _adj[j, i] = 1
            _deg[i] += 1
            _deg[j] += 1
            _edges.append((i, j))


def _add_node() -> None:
    global _n
    if _n >= N_MAX:
        return
    i = _n
    d = _deg[:_n].astype(np.float64)
    total = d.sum()
    probs = d / total if total > 0 else np.ones(_n) / _n

    targets: set[int] = set()
    m = min(m_attach, _n)
    attempts = 0
    while len(targets) < m and attempts < _n * 20:
        t = int(np.random.choice(_n, p=probs))
        targets.add(t)
        attempts += 1

    # Place near center of targets
    if targets:
        _pos[i] = _pos[list(targets)].mean(axis=0) + np.random.randn(2).astype(np.float32) * 25
    else:
        _pos[i] = np.random.uniform(-60, 60, 2).astype(np.float32)
    _vel[i] = 0

    for t in targets:
        _adj[i, t] = _adj[t, i] = 1
        _deg[i] += 1
        _deg[t] += 1
        _edges.append((min(i, t), max(i, t)))
    _n += 1


def _layout_step() -> None:
    n = _n
    if n < 2:
        return
    p = _pos[:n]
    v = _vel[:n]

    # diff[i,j] = pos[i] - pos[j],  shape (n,n,2)
    diff = p[:, np.newaxis, :] - p[np.newaxis, :, :]
    dist = np.sqrt((diff * diff).sum(axis=2) + 1.0)  # (n,n), +1 avoids div/0

    unit = diff / dist[:, :, np.newaxis]  # (n,n,2)

    # Repulsion: all pairs push apart
    rep = K_REP / dist**2
    np.fill_diagonal(rep, 0.0)
    rep_force = (rep[:, :, np.newaxis] * unit).sum(axis=1)  # (n,2)

    # Attraction: only along edges, pull together
    a = _adj[:n, :n].astype(np.float32)
    att = K_ATT * dist * a
    att_force = (att[:, :, np.newaxis] * (-unit)).sum(axis=1)  # (n,2)

    total = (rep_force + att_force).astype(np.float32)
    v[:] = np.clip(v * DAMPING + total * DT, -40, 40)
    p[:] += v * DT

    _pos[:n] = p
    _vel[:n] = v


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global _frame

    if not paused:
        _frame += 1
        if _frame % GROW_EVERY == 0:
            _add_node()
        _layout_step()

    py5.background(230, 20, 8)

    n = _n
    if n == 0:
        return

    # Scale network to fit viewport with margin
    p = _pos[:n]
    lo, hi = p.min(axis=0), p.max(axis=0)
    span = (hi - lo).max()
    viz_s = (min(WIDTH, HEIGHT) * 0.82) / (span + 1e-4)
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    sx = (p[:, 0] - (lo[0] + hi[0]) * 0.5) * viz_s + cx
    sy = (p[:, 1] - (lo[1] + hi[1]) * 0.5) * viz_s + cy

    # Edges — age-faded: earlier edges are lighter
    n_edges = len(_edges)
    py5.stroke_weight(0.8)
    for idx, (u, v) in enumerate(_edges):
        if u >= n or v >= n:
            continue
        age = idx / max(n_edges, 1)
        py5.stroke(210, 25, 35 + age * 25, 30 + age * 30)
        py5.line(sx[u], sy[u], sx[v], sy[v])

    # Nodes — size ∝ sqrt(degree), hue by degree (blue→yellow→red)
    py5.no_stroke()
    max_deg = max(int(_deg[:n].max()), 1)
    for i in range(n):
        d = int(_deg[i])
        t = d / max_deg  # 0=min, 1=hub
        hue = 220 - t * 200  # blue(220) → red(20)
        sat = 55 + t * 35
        bri = 65 + t * 30
        alpha = 70 + t * 30
        size = 4 + t**0.5 * 22
        py5.fill(hue % 360, sat, bri, alpha)
        py5.circle(float(sx[i]), float(sy[i]), size)

    # HUD
    py5.fill(0, 0, 82)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"nodes:{n}  edges:{n_edges}  hub degree:{max_deg}  m={m_attach}  "
        f"{'PAUSED' if paused else ''}",
        10,
        22,
    )


def key_pressed() -> None:
    global paused, m_attach
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "+":
        m_attach = min(8, m_attach + 1)
    elif k == "-":
        m_attach = max(1, m_attach - 1)
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "scale_free_network_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
