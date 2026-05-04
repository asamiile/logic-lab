# Clifford Attractor

Renders dense point clouds from a chaotic two-dimensional map.

## Run

```bash
uv run python mathematical/clifford_attractor/clifford_attractor.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch parameter preset |
| `+` / `-` | Change point count |
| `c` | Switch color mode |
| `s` | Save screenshot |

## Algorithm

The Clifford attractor repeatedly applies a nonlinear map:

```text
x' = sin(a * y) + c * cos(a * x)
y' = sin(b * x) + d * cos(b * y)
```

Starting from one point, the sketch iterates the map hundreds of thousands of times. Each visited pixel adds to a density buffer, then the log-scaled density becomes brightness and color. Different parameters produce filaments, shells, folds, and nebula-like structures.

Chaotic attractors are useful for dense abstract textures, particle-like forms, and mathematical compositions with organic complexity.

## Other Environments

**TouchDesigner**: Iterate the map in a Script SOP, Python DAT, or feedback GLSL TOP. Accumulate visits into a texture for density-based rendering.

**UE5**: Precompute points in C++ or Blueprint and render them with Niagara sprites or instanced points. Use visit density or iteration index to drive color.
