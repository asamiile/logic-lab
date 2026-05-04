# Barycentric Coordinates

Visualizes interpolation weights inside a triangle.

## Run

```bash
uv run python mathematical/barycentric_coordinates/barycentric_coordinates.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Drag vertex | Move triangle vertex |
| `g` | Toggle weight grid |
| `w` | Toggle mouse weight display |
| `r` | Reset vertices |
| `s` | Save screenshot |

## Algorithm

Barycentric coordinates express a point as weighted vertex contributions:

```text
p = w1 * v1 + w2 * v2 + w3 * v3
w1 + w2 + w3 = 1
```

Inside a triangle, all three weights are non-negative. The weights can be used to interpolate colors, texture coordinates, heights, normals, or any other per-vertex value.

The sketch colors each pixel by its three barycentric weights and draws iso-weight lines. Moving the vertices shows that the interpolation follows the triangle geometry.

## Other Environments

**TouchDesigner**: Use barycentric weights in a GLSL TOP or Script SOP to interpolate vertex attributes across triangles.

**UE5**: Barycentric coordinates are useful in mesh shaders, material interpolation, hit testing, and procedural triangle sampling.
