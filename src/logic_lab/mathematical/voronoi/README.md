# Voronoi Diagram

Generate space-partitioning diagrams where each pixel is colored by its nearest seed point.

## Run

```bash
uv run python mathematical/voronoi/voronoi.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Mouse click | Add a new seed point |
| `p` | Generate Poisson-distributed seed layout |
| `c` | Reset to default seeds |
| `s` | Save screenshot |

## Algorithm

A Voronoi diagram partitions space into regions where each region contains all points closer to a particular seed than to any other seed. This implementation:

1. For each pixel, computes distance to all seed points
2. Finds the nearest seed (using `np.argmin`)
3. Colors the pixel based on the seed index

The result creates a tessellation of colored cells with straight-line boundaries between seeds. By coupling with Poisson disk sampling, uniform seed distribution creates organic cell patterns.

## Other Environments

**TouchDesigner**: The `shader/sdf_2d/` folder includes Voronoi metrics shaders that can be used in a GLSL TOP for real-time GPU rendering.

**UE5**: Material Editor has a `VoronoiNoise` node that provides Voronoi diagrams with built-in parameterization.
