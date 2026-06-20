"""
Langton's Ant — Emergent Complexity from Simple Rules
An ant lives on a grid of colored cells. Each step:
  1. Look at the current cell's color.
  2. Turn according to the rule for that color (L=left, R=right, U=U-turn, N=straight).
  3. Flip the cell to the next color in the cycle.
  4. Move forward one step.

Classic 2-color rule "RL": after ~10 000 chaotic steps a periodic "highway"
emerges spontaneously — one of the most striking examples of emergent order.

Multi-color rules produce wildly different behaviors:
  "RL"       — classic, highway after ~10k steps
  "LLRR"     — symmetric diagonal highway
  "LRRL"     — broad diagonal highway forms faster
  "LLRRLLRR" — intricate symmetric growth
  "RLLR"     — spiral / chaotic expansion

Multiple ants (different starting positions) run simultaneously,
each with its own color marker.

Controls:
  1–5     — rule preset
  r       — reset (clear grid, re-place ants)
  +/-     — more / fewer ants
  Space   — pause / resume
  f       — toggle fast-forward
  s       — save screenshot
"""

from pathlib import Path

import numpy as np
import py5

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

WIDTH, HEIGHT = 800, 800
GRID = 400
STEPS_NORMAL = 10
STEPS_FAST = 200

RULES = {
    "RL": "RL",
    "LLRR": "LLRR",
    "LRRL": "LRRL",
    "LLRRLLRR": "LLRRLLRR",
    "RLLR": "RLLR",
}
RULE_NAMES = list(RULES.keys())
rule_idx = 0

N_ANTS = 1
fast_forward = False
paused = False

_grid: np.ndarray  # (GRID, GRID) int — color index
_ant_x: np.ndarray  # (N_ANTS,) int
_ant_y: np.ndarray  # (N_ANTS,) int
_ant_d: np.ndarray  # (N_ANTS,) int  0=N 1=E 2=S 3=W

_DX = np.array([0, 1, 0, -1], dtype=np.int32)
_DY = np.array([-1, 0, 1, 0], dtype=np.int32)

_ANT_HUES = [0, 60, 120, 180, 240, 300]
_step_count = 0


def _reset() -> None:
    global _grid, _ant_x, _ant_y, _ant_d, _step_count
    _grid = np.zeros((GRID, GRID), dtype=np.int32)
    spread = GRID // 6
    cx, cy = GRID // 2, GRID // 2
    _ant_x = np.random.randint(cx - spread, cx + spread, N_ANTS)
    _ant_y = np.random.randint(cy - spread, cy + spread, N_ANTS)
    _ant_d = np.zeros(N_ANTS, dtype=np.int32)
    _step_count = 0


def _step_ant(rule: str) -> None:
    global _step_count
    n_colors = len(rule)
    for i in range(N_ANTS):
        x, y = int(_ant_x[i]), int(_ant_y[i])
        color = int(_grid[y, x])
        turn = rule[color % n_colors]

        if turn == "L":
            _ant_d[i] = (_ant_d[i] - 1) % 4
        elif turn == "R":
            _ant_d[i] = (_ant_d[i] + 1) % 4
        elif turn == "U":
            _ant_d[i] = (_ant_d[i] + 2) % 4

        _grid[y, x] = (color + 1) % n_colors
        _ant_x[i] = (_ant_x[i] + _DX[_ant_d[i]]) % GRID
        _ant_y[i] = (_ant_y[i] + _DY[_ant_d[i]]) % GRID
    _step_count += 1


def _render(rule: str) -> None:
    n_colors = len(rule)
    ph, pw = py5.pixel_height, py5.pixel_width
    gy = (np.arange(ph) * GRID / ph).astype(int).clip(0, GRID - 1)
    gx = (np.arange(pw) * GRID / pw).astype(int).clip(0, GRID - 1)
    cell_d = _grid[np.ix_(gy, gx)]

    t = cell_d.astype(np.float32) / max(n_colors - 1, 1)
    hue = (t * 300.0).astype(np.float32)
    dark = cell_d == 0

    h6 = hue / 60.0
    i6 = h6.astype(np.int32) % 6
    f6 = h6 - i6
    q = 1.0 - f6
    r_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [1, q, 0, 0, f6], 1)
    g_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [f6, 1, 1, q, 0], 0)
    b_f = np.select([i6 == 0, i6 == 1, i6 == 2, i6 == 3, i6 == 4], [0, 0, f6, 1, 1], q)

    bri = np.where(dark, 0.06, 0.85)
    r8 = np.clip(r_f * bri * 255, 0, 255).astype(np.uint8)
    g8 = np.clip(g_f * bri * 255, 0, 255).astype(np.uint8)
    b8 = np.clip(b_f * bri * 255, 0, 255).astype(np.uint8)

    argb = (
        np.int32(-16777216)
        | (r8.astype(np.int32) << 16)
        | (g8.astype(np.int32) << 8)
        | b8.astype(np.int32)
    )
    py5.load_pixels()
    py5.pixels[:] = argb.flatten()
    py5.update_pixels()

    scale_x = pw / GRID
    scale_y = ph / GRID
    py5.no_stroke()
    py5.color_mode(py5.HSB, 360, 100, 100)
    for i in range(N_ANTS):
        py5.fill(_ANT_HUES[i % len(_ANT_HUES)], 80, 100)
        py5.circle(float(_ant_x[i] * scale_x), float(_ant_y[i] * scale_y), 5.0)
    py5.color_mode(py5.RGB)


def setup() -> None:
    py5.size(WIDTH, HEIGHT)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    _reset()


def draw() -> None:
    rule = RULES[RULE_NAMES[rule_idx]]
    steps = STEPS_FAST if fast_forward else STEPS_NORMAL

    if not paused:
        for _ in range(steps):
            _step_ant(rule)

    _render(rule)
    py5.fill(210, 230, 255)
    py5.no_stroke()
    py5.text_size(12)
    py5.text(
        f"Langton's Ant  rule:{RULE_NAMES[rule_idx]}  "
        f"ants:{N_ANTS}  steps:{_step_count}  "
        f"{'FAST' if fast_forward else ''}  {'PAUSED' if paused else ''}",
        8,
        18,
    )


def key_pressed() -> None:
    global rule_idx, paused, fast_forward, N_ANTS
    k = py5.key
    if k == " ":
        paused = not paused
    elif k == "f":
        fast_forward = not fast_forward
    elif k == "r":
        _reset()
    elif k == "1":
        rule_idx = 0
        _reset()
    elif k == "2":
        rule_idx = 1
        _reset()
    elif k == "3":
        rule_idx = 2
        _reset()
    elif k == "4":
        rule_idx = 3
        _reset()
    elif k == "5":
        rule_idx = 4
        _reset()
    elif k == "+":
        N_ANTS = min(6, N_ANTS + 1)
        _reset()
    elif k == "-":
        N_ANTS = max(1, N_ANTS - 1)
        _reset()
    elif k == "s":
        py5.save_frame(str(SCREENSHOT_DIR / f"ant_{RULE_NAMES[rule_idx]}_####.png"))


if __name__ == "__main__":
    py5.run_sketch()
