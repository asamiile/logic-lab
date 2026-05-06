# Logistic Bifurcation

Draws the bifurcation diagram of the logistic map.

## Run

```bash
uv run python src/logic_lab/mathematical/logistic_bifurcation/logistic_bifurcation.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch parameter range |
| `+` / `-` | Change iteration count |
| `c` | Switch color mode |
| `s` | Save screenshot |

## Algorithm

The logistic map is a simple nonlinear recurrence:

```text
x[n + 1] = r * x[n] * (1 - x[n])
```

For each value of `r`, the sketch iterates the map, discards early transient values, then plots the remaining `x` values. As `r` increases, the map moves from stable fixed points to period doubling and chaotic bands.

The diagram is useful for visualizing nonlinear dynamics, chaos, stable windows, and how simple recurrence rules can create complex structure.

## Other Environments

**TouchDesigner**: Iterate the recurrence in a Python DAT or GLSL TOP, accumulating visits into a texture where x is `r` and y is the state value.

**UE5**: Precompute the point cloud in C++ or Blueprint and render it as instanced points, Niagara sprites, or a texture generated from a render target.
