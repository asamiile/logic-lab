# Diamond-Square Fractal Terrain

Generate procedural landscapes using the diamond-square midpoint displacement algorithm.

## Run

```bash
uv run python mathematical/diamond_square/diamond_square.py
```

## Controls

| Key | Effect |
|---|---|
| `r` | Increase roughness (more jagged terrain) |
| `f` | Decrease roughness (smoother terrain) |
| `n` | Generate new terrain with random seed |
| `s` | Save screenshot |

## Algorithm

The diamond-square algorithm generates fractional Brownian motion heightmaps by:

1. **Initialize corners**: Set four corner values randomly
2. **Diamond step**: Calculate midpoint of square as average of corners + random offset
3. **Square step**: Calculate edge midpoints as averages of adjacent points + random offset
4. **Recursion**: Repeat with smaller step sizes and decreasing random scale

The `roughness` parameter controls how much each recursion level contributes (low = smoother, high = more detail).

Colors map height to a blue→cyan→white gradient, creating intuitive topographic visualization.

## Other Environments

**TouchDesigner**: Use the Height Map TOP with noise or procedural generation, then feed to a SOP to convert to 3D geometry via Geometry COMP.

**UE5**: Landscape Editor supports Heightmap import. Alternatively, PCG Graph offers procedural terrain generation with similar fractal noise patterns.
