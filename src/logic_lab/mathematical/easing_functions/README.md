# Easing Functions Library

Smooth interpolation functions for animation and motion design, with interactive curve visualization.

## Run

```bash
uv run python src/logic_lab/mathematical/easing_functions/easing_functions.py
```

## Controls

| Key | Effect |
|---|---|
| `←` / `→` | Previous / next easing function |
| `s` | Save screenshot |

## Algorithm

Easing functions map normalized time `t ∈ [0, 1]` to output `y ∈ [0, 1]`, controlling motion acceleration and deceleration. Implemented functions:

- **Quadratic**: `t²`, `1 - (1-t)²`, smooth blend
- **Cubic**: `t³`, `1 - (1-t)³`, smoother curves
- **Sine**: sin-based smooth easing
- **Exponential**: `2^(10t-10)`, steep acceleration
- **Bounce**: Multi-bounce falloff effect

Each function can be imported individually:

```python
from mathematical.easing_functions import ease_in_out_cubic

value = ease_in_out_cubic(0.5)  # Returns 0.5
```

The visualization shows each curve with an animated dot demonstrating the easing in real time.

## Other Environments

**TouchDesigner**: The `Math CHOP` has built-in Ease parameters that match common easing curves. Use `easeIn`, `easeOut`, `easeInOut` operators.

**UE5**: Timeline and `AnimBP` support built-in easing via the "Ease" parameter in blend space functions. Custom curves use the `FloatCurve` asset type.
