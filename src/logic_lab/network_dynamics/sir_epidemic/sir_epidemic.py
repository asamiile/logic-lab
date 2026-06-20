"""
SIR Epidemic Model on a Network
Susceptible-Infected-Recovered spreading dynamics on a random network.
Each node is in one of three states:
  S (blue)  — susceptible; can be infected by I neighbours
  I (red)   — infectious; infects each S neighbour with probability β per step
  R (gray)  — recovered; permanently immune

The simulation reveals the percolation threshold: below β≈γ/k (where k is
the mean degree) the epidemic dies without spreading; above it, a giant
cascade infects most of the network.

Layout: Fruchterman-Reingold force-directed placement.

Controls:
  Space   — pause / resume
  r       — reset with a new random network
  b / B   — decrease / increase infection rate β
  g / G   — decrease / increase recovery rate γ
  n / N   — fewer / more nodes
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 900, 900

# Network parameters
N_NODES = 80
P_EDGE = 0.06  # Erdős-Rényi edge probability

# Epidemic parameters
BETA = 0.25  # infection probability per S-I edge per step
GAMMA = 0.05  # recovery probability per I node per step
SEED_FRAC = 0.03  # fraction initially infected

# Layout
K_REP = 3000.0
K_ATT = 0.5
DAMPING = 0.80
DT = 0.5
LAYOUT_STEPS_INIT = 200  # warm-up layout steps before display
LAYOUT_STEPS_PER_FRAME = 4

# State
_adj: np.ndarray  # (N_NODES, N_NODES) adjacency
_pos: np.ndarray  # (N_NODES, 2) positions
_vel: np.ndarray  # (N_NODES, 2) velocities
_state: np.ndarray  # (N_NODES,) 0=S, 1=I, 2=R
_edges: list  # list of (u, v) pairs
_step = 0
paused = False
n_nodes = N_NODES
beta = BETA
gamma = GAMMA


def _make_network(n: int, p: float) -> np.ndarray:
    adj = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for j in range(i + 1, n):
            if np.random.random() < p:
                adj[i, j] = adj[j, i] = 1
    return adj


def _reset() -> None:
    global _adj, _pos, _vel, _state, _edges, _step
    _adj = _make_network(n_nodes, P_EDGE)
    _edges = [(i, j) for i in range(n_nodes) for j in range(i + 1, n_nodes) if _adj[i, j]]

    # Random initial positions on circle
    _pos = np.zeros((n_nodes, 2), dtype=np.float32)
    for i in range(n_nodes):
        ang = 2 * np.pi * i / n_nodes
        _pos[i] = [np.cos(ang) * 80, np.sin(ang) * 80]
    _pos += np.random.randn(n_nodes, 2).astype(np.float32) * 10
    _vel = np.zeros((n_nodes, 2), dtype=np.float32)

    # Warm-up layout
    for _ in range(LAYOUT_STEPS_INIT):
        _layout_step()

    # Initial epidemic state
    _state = np.zeros(n_nodes, dtype=np.int32)  # all S
    n_seed = max(1, int(n_nodes * SEED_FRAC))
    seeds = np.random.choice(n_nodes, n_seed, replace=False)
    _state[seeds] = 1  # I
    _step = 0


def _layout_step() -> None:
    n = n_nodes
    if n < 2:
        return
    p = _pos[:n]
    v = _vel[:n]

    diff = p[:, np.newaxis, :] - p[np.newaxis, :, :]
    dist = np.sqrt((diff * diff).sum(axis=2) + 1.0)
    unit = diff / dist[:, :, np.newaxis]

    rep = K_REP / dist**2
    np.fill_diagonal(rep, 0.0)
    rep_force = (rep[:, :, np.newaxis] * unit).sum(axis=1)

    a = _adj[:n, :n].astype(np.float32)
    att = K_ATT * dist * a
    att_force = (att[:, :, np.newaxis] * (-unit)).sum(axis=1)

    total = (rep_force + att_force).astype(np.float32)
    v[:] = np.clip(v * DAMPING + total * DT, -30, 30)
    p[:] += v * DT
    _pos[:n] = p
    _vel[:n] = v


def _epidemic_step() -> None:
    new_state = _state.copy()

    infectious = np.where(_state == 1)[0]
    for i in infectious:
        # Infect neighbours
        neighbours = np.where(_adj[i] == 1)[0]
        for j in neighbours:
            if _state[j] == 0 and np.random.random() < beta:
                new_state[j] = 1
        # Recover
        if np.random.random() < gamma:
            new_state[i] = 2

    _state[:] = new_state


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    global _step
    if not paused:
        for _ in range(LAYOUT_STEPS_PER_FRAME):
            _layout_step()
        if _state.sum() > 0:  # stop when no more I nodes
            _epidemic_step()
            _step += 1

    py5.background(230, 15, 8)

    # Scale to viewport
    p = _pos
    lo, hi = p.min(axis=0), p.max(axis=0)
    span = (hi - lo).max()
    viz_s = (min(WIDTH, HEIGHT) * 0.82) / (span + 1e-4)
    cx, cy = WIDTH * 0.5, HEIGHT * 0.5
    sx = (p[:, 0] - (lo[0] + hi[0]) * 0.5) * viz_s + cx
    sy = (p[:, 1] - (lo[1] + hi[1]) * 0.5) * viz_s + cy

    # Edges
    py5.stroke_weight(0.7)
    for u, v in _edges:
        su = _state[u] == 1 or _state[v] == 1
        hue = 0 if su else 210
        py5.stroke(hue, 20, 30, 25)
        py5.line(sx[u], sy[u], sx[v], sy[v])

    # Nodes
    py5.no_stroke()
    for i in range(n_nodes):
        st = _state[i]
        if st == 0:
            hue, sat, bri = 215, 70, 80  # S = blue
        elif st == 1:
            hue, sat, bri = 0, 85, 95  # I = red
        else:
            hue, sat, bri = 0, 0, 55  # R = gray
        py5.fill(hue, sat, bri, 90)
        py5.circle(float(sx[i]), float(sy[i]), 9)

    n_s = int((_state == 0).sum())
    n_i = int((_state == 1).sum())
    n_r = int((_state == 2).sum())
    py5.fill(0, 0, 82)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"step:{_step}  S:{n_s} I:{n_i} R:{n_r}  β:{beta:.2f} γ:{gamma:.2f}  "
        f"{'PAUSED' if paused else ''}",
        10,
        22,
    )


def key_pressed() -> None:
    global paused, beta, gamma, n_nodes
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "b":
        beta = max(0.01, round(beta - 0.05, 2))
    elif k == "B":
        beta = min(1.0, round(beta + 0.05, 2))
    elif k == "g":
        gamma = max(0.01, round(gamma - 0.02, 2))
    elif k == "G":
        gamma = min(0.5, round(gamma + 0.02, 2))
    elif k == "n":
        n_nodes = max(20, n_nodes - 20)
        _reset()
    elif k == "N":
        n_nodes = min(200, n_nodes + 20)
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / "sir_epidemic_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
