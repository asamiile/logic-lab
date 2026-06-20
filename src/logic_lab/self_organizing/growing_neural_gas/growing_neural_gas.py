"""
Growing Neural Gas (GNG)
An unsupervised competitive learning network that adapts its topology to
the input distribution without fixing the number of neurons in advance.

Algorithm (Fritzke 1995):
  1. Present a random input signal from the data distribution.
  2. Find the two nearest neurons (winner B1 and second B2).
  3. Increment the age of all edges from B1; create/refresh the B1-B2 edge.
  4. Move B1 and its topological neighbours toward the input.
  5. Accumulate error at B1.
  6. Every λ steps, insert a new neuron between the highest-error neuron
     and its highest-error neighbour; reduce their errors.
  7. Remove edges older than max_age; remove isolated neurons.

Three data distributions show different emergent topologies:
  • uniform    — nodes spread evenly over the square
  • ring       — nodes form a 1D loop
  • spiral     — nodes trace a 2D Archimedean spiral

Controls:
  1 / 2 / 3  — data distribution (uniform / ring / spiral)
  r          — reset
  Space      — pause / resume
  s          — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800

DISTRIBUTIONS = ["uniform", "ring", "spiral"]
dist_idx = 0

# GNG hyperparameters
EPS_B = 0.2  # winner move fraction
EPS_N = 0.006  # neighbour move fraction
LAMBDA = 80  # steps between neuron insertions
MAX_AGE = 50  # edge age limit
ALPHA = 0.5  # error reduction on insertion
BETA = 0.0005  # global error decay per step
MAX_NODES = 200  # cap on neuron count
STEPS_PER_FRAME = 20

paused = False

# State: dict-based graph
# nodes: list of [x, y] (position) and float (error)
# edges: dict (i,j): int age  (i < j always)
_nodes: list  # [[x, y], ...]
_errors: list  # [float, ...]
_edges: dict  # (i,j) → age
_step = 0


def _sample() -> np.ndarray:
    dist = DISTRIBUTIONS[dist_idx]
    if dist == "uniform":
        return np.random.uniform(0.1, 0.9, 2)
    elif dist == "ring":
        t = np.random.uniform(0, 2 * np.pi)
        r = 0.32 + np.random.normal(0, 0.025)
        return np.array([0.5 + r * np.cos(t), 0.5 + r * np.sin(t)])
    else:  # spiral
        t = np.random.uniform(0, 4 * np.pi)
        r = 0.05 + 0.12 * t / (4 * np.pi) + np.random.normal(0, 0.012)
        return np.array([0.5 + r * np.cos(t), 0.5 + r * np.sin(t)])


def _reset() -> None:
    global _nodes, _errors, _edges, _step
    # Start with 2 random neurons
    _nodes = [_sample().tolist(), _sample().tolist()]
    _errors = [0.0, 0.0]
    _edges = {}
    _step = 0


def _gng_step() -> None:
    global _step, _edges, _nodes, _errors

    signal = _sample()

    # Find 2 nearest
    pos = np.array(_nodes)
    diffs = pos - signal
    dists = (diffs * diffs).sum(axis=1)
    order = np.argsort(dists)
    b1, b2 = int(order[0]), int(order[1])

    # Increment edge ages from b1
    to_remove = []
    for (i, j), age in list(_edges.items()):
        if i == b1 or j == b1:
            _edges[(i, j)] = age + 1
            if _edges[(i, j)] > MAX_AGE:
                to_remove.append((i, j))
    for e in to_remove:
        del _edges[e]

    # Add/refresh b1-b2 edge
    key = (min(b1, b2), max(b1, b2))
    _edges[key] = 0

    # Accumulate error at winner
    _errors[b1] += float(dists[b1])

    # Move winner and neighbours toward signal
    _nodes[b1] = (np.array(_nodes[b1]) + EPS_B * (signal - np.array(_nodes[b1]))).tolist()
    neighbors_b1 = {j for (i, j) in _edges if i == b1} | {i for (i, j) in _edges if j == b1}
    for nb in neighbors_b1:
        _nodes[nb] = (np.array(_nodes[nb]) + EPS_N * (signal - np.array(_nodes[nb]))).tolist()

    # Remove isolated nodes (no edges) — skip node 0 and 1 to keep at least 2
    connected = set()
    for i, j in _edges:
        connected.add(i)
        connected.add(j)
    to_del = [i for i in range(len(_nodes)) if i not in connected and i >= 2]
    for i in reversed(sorted(to_del)):
        _nodes.pop(i)
        _errors.pop(i)
        # Renumber edges
        new_edges = {}
        for (a, b), age in _edges.items():
            a2 = a - (a > i) if a != i else None
            b2 = b - (b > i) if b != i else None
            if a2 is not None and b2 is not None:
                new_edges[(min(a2, b2), max(a2, b2))] = age
        _edges = new_edges

    # Decay errors
    for k in range(len(_errors)):
        _errors[k] *= 1.0 - BETA

    # Insert new node every λ steps
    if _step % LAMBDA == 0 and len(_nodes) < MAX_NODES:
        q = int(np.argmax(_errors))
        neighbors_q = {j for (i, j) in _edges if i == q} | {i for (i, j) in _edges if j == q}
        if neighbors_q:
            f = max(neighbors_q, key=lambda n: _errors[n])
            new_pos = ((np.array(_nodes[q]) + np.array(_nodes[f])) * 0.5).tolist()
            new_idx = len(_nodes)
            _nodes.append(new_pos)
            _errors.append((_errors[q] + _errors[f]) * ALPHA)
            # Remove q-f edge, add q-new and new-f
            key_qf = (min(q, f), max(q, f))
            if key_qf in _edges:
                del _edges[key_qf]
            _edges[(min(q, new_idx), max(q, new_idx))] = 0
            _edges[(min(f, new_idx), max(f, new_idx))] = 0
            _errors[q] *= ALPHA
            _errors[f] *= ALPHA

    _step += 1


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if not paused:
        for _ in range(STEPS_PER_FRAME):
            _gng_step()

    py5.background(10, 12, 22)

    # Edges
    max_err = max(_errors) if _errors else 1.0
    py5.stroke_weight(1.0)
    for (i, j), age in _edges.items():
        age_frac = age / MAX_AGE
        alpha = int(180 * (1.0 - age_frac * 0.7))
        py5.stroke(80, 130, 200, alpha)
        xi, yi = _nodes[i][0] * WIDTH, _nodes[i][1] * HEIGHT
        xj, yj = _nodes[j][0] * WIDTH, _nodes[j][1] * HEIGHT
        py5.line(xi, yi, xj, yj)

    # Nodes
    py5.no_stroke()
    for k, (nx, ny) in enumerate(_nodes):
        err_n = _errors[k] / (max_err + 1e-9)
        # Color: low error = blue, high error = red
        r = int(err_n * 220)
        g = int(max(0, 80 - err_n * 80))
        b = int((1.0 - err_n) * 200)
        size = 4 + err_n * 10
        py5.fill(r, g, b, 200)
        py5.circle(nx * WIDTH, ny * HEIGHT, size)

    py5.fill(180, 210, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"GNG  dist:{DISTRIBUTIONS[dist_idx]}  "
        f"nodes:{len(_nodes)}  edges:{len(_edges)}  step:{_step}  "
        f"{'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global dist_idx, paused
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "r":
        _reset()
    elif k == "1":
        dist_idx = 0
        _reset()
    elif k == "2":
        dist_idx = 1
        _reset()
    elif k == "3":
        dist_idx = 2
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"gng_{DISTRIBUTIONS[dist_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
