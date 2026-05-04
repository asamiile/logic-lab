# Lloyd Relaxation

Moves random points toward the centroids of their Voronoi-like regions.

## Run

```bash
uv run python mathematical/lloyd_relaxation/lloyd_relaxation.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Run one relaxation step |
| `a` | Toggle automatic relaxation |
| `r` | Reset with a new random seed |
| `+` / `-` | Change point count |
| `v` | Toggle region display |
| `m` | Toggle motion vectors |
| `s` | Save screenshot |

## Algorithm

Lloyd relaxation smooths a point distribution by repeatedly moving each point toward the center of its region:

1. **Assign samples**: Divide the canvas into small samples and assign each sample to the nearest seed point.
2. **Estimate centroids**: Average each seed's assigned sample coordinates.
3. **Move seeds**: Replace each seed with its region centroid.
4. **Repeat**: Iterations produce a more even, blue-noise-like distribution.

This implementation estimates Voronoi centroids with grid samples instead of clipping exact polygons. That keeps the code compact and makes the relaxation process easy to visualize.

## Other Environments

**TouchDesigner**: Store seed points in a DAT, assign sampled pixels or points to nearest seeds in Python or GLSL, then update seed positions toward centroids.

**UE5**: Run nearest-seed assignment on a grid or point cloud in C++/Blueprint, then update instance positions over repeated iterations for even scatter layouts.
