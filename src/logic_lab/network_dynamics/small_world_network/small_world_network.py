"""
Watts-Strogatz Small-World Network
Starting from a k-regular ring lattice (each node connects to k/2 neighbours
on each side), each edge is rewired with probability p to a random node.

The result transitions through three regimes:
  p ≈ 0   — regular ring: high clustering, long path lengths
  p ≈ 0.1 — small world: high clustering, SHORT path lengths (six degrees!)
  p ≈ 1   — random Erdős-Rényi: low clustering, short path lengths

Animation sweeps p from 0 → 1 so you can watch the lattice "melt."
Layout: nodes on a circle (ring lattice basis), colored by degree.
Shortcut edges (rewired) appear in a warmer color than ring edges.

Controls:
  Space   — pause / resume p-sweep
  r       — reset to p=0
  p / P   — decrease / increase rewiring probability p
  n / N   — fewer / more nodes
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

N_NODES = 60
K_NEIGH = 6  # k-regular: connect to K_NEIGH nearest (must be even)
P_REWIRE = 0.05  # current rewiring probability
P_SWEEP_RATE = 0.001  # automatic p increase per frame

paused = False
n_nodes = N_NODES
k_neigh = K_NEIGH

_adj: np.ndarray
_edges: list  # list of (u, v, is_shortcut)
_pos: np.ndarray  # (N, 2) unit circle positions


def _ring_lattice(n: int, k: int) -> np.ndarray:
    adj = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for d in range(1, k // 2 + 1):
            j = (i + d) % n
            adj[i, j] = adj[j, i] = 1
    return adj


def _rewire(n: int, k: int, p: float) -> tuple[np.ndarray, list]:
    adj = _ring_lattice(n, k)
    edges = []
    for i in range(n):
        for d in range(1, k // 2 + 1):
            j = (i + d) % n
            if np.random.random() < p:
                # Rewire: remove i-j, add i-new (avoid self-loops and duplicates)
                candidates = [m for m in range(n) if m != i and not adj[i, m]]
                if candidates:
                    new_j = candidates[np.random.randint(len(candidates))]
                    adj[i, j] = adj[j, i] = 0
                    adj[i, new_j] = adj[new_j, i] = 1
                    edges.append((i, new_j, True))
            else:
                edges.append((i, j, False))
    return adj, edges


def _circle_pos(n: int) -> np.ndarray:
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([np.cos(angles), np.sin(angles)]).astype(np.float32)


def _reset() -> None:
    global _adj, _edges, _pos, P_REWIRE
    P_REWIRE = 0.0
    _adj, _edges = _rewire(n_nodes, k_neigh, P_REWIRE)
    _pos = _circle_pos(n_nodes)


def _rebuild() -> None:
    global _adj, _edges
    _adj, _edges = _rewire(n_nodes, k_neigh, P_REWIRE)


def _clustering_coeff(adj: np.ndarray, n: int) -> float:
    """Mean local clustering coefficient."""
    total = 0.0
    for i in range(n):
        nbrs = np.where(adj[i])[0]
        ki = len(nbrs)
        if ki < 2:
            continue
        links = sum(1 for a in range(ki) for b in range(a + 1, ki) if adj[nbrs[a], nbrs[b]])
        total += 2 * links / (ki * (ki - 1))
    return total / n if n > 0 else 0.0


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global P_REWIRE

    if not paused:
        P_REWIRE = min(1.0, P_REWIRE + P_SWEEP_RATE)
        _rebuild()

    py5.background(225, 20, 8)

    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    ring_r = min(WIDTH, HEIGHT) * 0.38
    sx = _pos[:, 0] * ring_r + cx
    sy = _pos[:, 1] * ring_r + cy

    # Edges
    py5.stroke_weight(0.7)
    for u, v, shortcut in _edges:
        if shortcut:
            py5.stroke(30, 80, 75, 55)  # warm orange: shortcut
        else:
            py5.stroke(210, 45, 55, 35)  # cool blue: ring edge
        py5.line(sx[u], sy[u], sx[v], sy[v])

    # Nodes
    py5.no_stroke()
    deg = _adj.sum(axis=1).astype(float)
    max_deg = max(deg.max(), 1)
    for i in range(n_nodes):
        t = deg[i] / max_deg
        hue = 220 - t * 200  # blue(220)→red(20)
        py5.fill(hue % 360, 65 + t * 25, 70 + t * 25, 90)
        py5.circle(float(sx[i]), float(sy[i]), 7 + t * 8)

    # Stats
    cc = _clustering_coeff(_adj, n_nodes)
    n_shortcuts = sum(1 for _, _, s in _edges if s)

    py5.fill(0, 0, 82)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"n={n_nodes}  k={k_neigh}  p={P_REWIRE:.3f}  "
        f"shortcuts:{n_shortcuts}  C={cc:.3f}  "
        f"{'PAUSED' if paused else ''}",
        10,
        22,
    )


def key_pressed() -> None:
    global paused, P_REWIRE, n_nodes, k_neigh
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "p":
        P_REWIRE = max(0.0, round(P_REWIRE - 0.05, 3))
        _rebuild()
    elif k == "P":
        P_REWIRE = min(1.0, round(P_REWIRE + 0.05, 3))
        _rebuild()
    elif k == "n":
        n_nodes = max(20, n_nodes - 20)
        _reset()
    elif k == "N":
        n_nodes = min(120, n_nodes + 20)
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"small_world_p{P_REWIRE:.3f}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
