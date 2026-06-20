"""
Diffusion-Limited Aggregation (DLA)
Random walkers are launched from the boundary of a circle. When a walker
touches the growing cluster (Manhattan-adjacent pixel), it freezes in place
and becomes part of the cluster. The result is a branching fractal with
Hausdorff dimension ≈ 1.71.

Performance strategy: batch N_WALKERS walkers in parallel using numpy.
Each frame, all live walkers take one random step. Walkers that leave the
spawn circle are re-launched from a new random boundary point.
Walkers that stick are absorbed and a new walker is spawned.

Color encodes the order in which particles stuck:
  old particles (center) → purple/blue
  new particles (tips)   → orange/yellow

Controls:
  r   — reset
  n   — fewer walkers (slower, less chaos)
  N   — more walkers (faster growth)
  1   — age colormap (purple → yellow)
  2   — distance colormap (dark → cyan)
  s   — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 400  # internal simulation grid (upscaled to display)
SPAWN_R = GRID // 2 - 5  # radius walkers spawn/reset on
KILL_R = SPAWN_R + 8  # re-spawn if walker escapes this radius

N_WALKERS = 200
MAX_CLUSTER = 60_000

colormap_idx = 0

_cx = GRID // 2
_cy = GRID // 2

# Cluster: boolean occupancy grid + order array
_occupied: np.ndarray  # (GRID, GRID) bool
_age: np.ndarray  # (GRID, GRID) float  0=empty, >0=stuck order
_stuck_count = 0

# Walker positions (integer)
_wx: np.ndarray  # (N_WALKERS,) int16
_wy: np.ndarray

_DIRS = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]], dtype=np.int16)


def _random_boundary(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Return n random points on the spawn circle."""
    angles = np.random.uniform(0, 2 * np.pi, n)
    bx = (_cx + SPAWN_R * np.cos(angles)).astype(np.int16)
    by = (_cy + SPAWN_R * np.sin(angles)).astype(np.int16)
    bx = np.clip(bx, 0, GRID - 1)
    by = np.clip(by, 0, GRID - 1)
    return bx, by


def _reset() -> None:
    global _occupied, _age, _stuck_count, _wx, _wy
    _occupied = np.zeros((GRID, GRID), dtype=bool)
    _age = np.zeros((GRID, GRID), dtype=np.float32)
    _stuck_count = 0
    # Seed: one particle at center
    _occupied[_cy, _cx] = True
    _age[_cy, _cx] = 1.0
    _stuck_count = 1
    _wx, _wy = _random_boundary(N_WALKERS)


def _step_walkers() -> None:
    global _stuck_count, _wx, _wy

    # Random steps
    steps = _DIRS[np.random.randint(0, 4, N_WALKERS)]
    _wx = np.clip(_wx + steps[:, 0], 0, GRID - 1).astype(np.int16)
    _wy = np.clip(_wy + steps[:, 1], 0, GRID - 1).astype(np.int16)

    # Check adjacency to cluster: any of 4 neighbours occupied?
    stuck_mask = np.zeros(N_WALKERS, dtype=bool)
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx = np.clip(_wx + dx, 0, GRID - 1)
        ny = np.clip(_wy + dy, 0, GRID - 1)
        stuck_mask |= _occupied[ny, nx]

    # Absorb walkers that stuck
    if stuck_mask.any():
        for i in np.where(stuck_mask)[0]:
            x, y = int(_wx[i]), int(_wy[i])
            if not _occupied[y, x]:
                _occupied[y, x] = True
                _stuck_count += 1
                _age[y, x] = float(_stuck_count)
        # Re-spawn stuck walkers
        bx, by = _random_boundary(int(stuck_mask.sum()))
        _wx[stuck_mask] = bx
        _wy[stuck_mask] = by

    # Re-spawn escaped walkers
    dist2 = (_wx - _cx) ** 2 + (_wy - _cy) ** 2
    escaped = dist2 > KILL_R * KILL_R
    if escaped.any():
        bx, by = _random_boundary(int(escaped.sum()))
        _wx[escaped] = bx
        _wy[escaped] = by


def _render() -> None:
    ph, pw = py5.pixel_height, py5.pixel_width

    gy_idx = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx_idx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    age_d = _age[np.ix_(gy_idx, gx_idx)]
    occ_d = age_d > 0

    if colormap_idx == 0:
        # Age: purple (old) → yellow (new)
        t = np.where(occ_d, np.clip(age_d / max(_stuck_count, 1), 0, 1), 0.0)
        r8 = np.where(occ_d, np.clip(t * 2.5 * 255, 0, 255), 6).astype(np.uint8)
        g8 = np.where(occ_d, np.clip((t - 0.3) * 255, 0, 255), 6).astype(np.uint8)
        b8 = np.where(occ_d, np.clip((1 - t * 1.8) * 200, 0, 255), 12).astype(np.uint8)
    else:
        # Distance from center
        gx2d = gx_idx[np.newaxis, :]
        gy2d = gy_idx[:, np.newaxis]
        dist = np.sqrt((gx2d - _cx) ** 2 + (gy2d - _cy) ** 2)
        t = np.where(occ_d, np.clip(dist / SPAWN_R, 0, 1), 0.0)
        r8 = np.where(occ_d, np.clip((t - 0.5) * 2 * 255, 0, 255), 4).astype(np.uint8)
        g8 = np.where(occ_d, np.clip(t * 1.5 * 200, 0, 255), 8).astype(np.uint8)
        b8 = np.where(occ_d, np.clip(t * 255 + 40, 0, 255), 16).astype(np.uint8)

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
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    if _stuck_count < MAX_CLUSTER:
        for _ in range(4):
            _step_walkers()

    _render()

    cmaps = ["age", "distance"]
    py5.fill(200, 230, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"DLA  particles:{_stuck_count}  walkers:{N_WALKERS}  " f"cmap:{cmaps[colormap_idx]}",
        8,
        18,
    )


def key_pressed() -> None:
    global colormap_idx, N_WALKERS, _wx, _wy
    k = py5.key
    if k == "r":
        _reset()
    elif k == "1":
        colormap_idx = 0
    elif k == "2":
        colormap_idx = 1
    elif k == "n":
        N_WALKERS = max(50, N_WALKERS - 50)
        _wx = _wx[:N_WALKERS].copy()
        _wy = _wy[:N_WALKERS].copy()
    elif k == "N":
        old = N_WALKERS
        N_WALKERS = min(600, N_WALKERS + 50)
        bx, by = _random_boundary(N_WALKERS - old)
        _wx = np.concatenate([_wx, bx]).astype(np.int16)
        _wy = np.concatenate([_wy, by]).astype(np.int16)
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"dla_{_stuck_count}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
