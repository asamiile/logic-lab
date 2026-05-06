# Weighted Voronoi Stippling

```bash
uv run python src/logic_lab/mathematical/weighted_voronoi_stippling/weighted_voronoi_stippling.py
```

## Overview

An algorithm that transforms image tones into stippled point patterns using Poisson disk sampling and Lloyd relaxation. Bright regions have sparse points; dark regions have dense points.

## Algorithm

1. Initialize point cloud randomly
2. Compute density weights from source image for each point
3. Generate Voronoi diagram; compute centroid of each region (Lloyd relaxation)
4. Move points to their centroids
5. Repeat

## Parameters

- `num_points`: Number of points to generate (default: 400)
- `iterations`: Number of relaxation iterations (default: 5)

## Visual Output

Generates stippled point patterns reflecting source image tones. Convert any photograph or illustration to stipple style by providing image input.

## Dependencies

- scipy (Voronoi diagram computation)

## References

- Secord, A. (2002). "Weighted Voronoi Stippling"
- Lloyd, S. (1982). "Least Squares Quantization in PCM"
