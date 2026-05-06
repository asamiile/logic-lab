# Worley Noise (Cellular Noise)

Generate organic cellular textures using Worley noise distance fields.

## Run

```bash
uv run python src/logic_lab/mathematical/worley_noise/worley_noise.py
```

## Controls

| Key | Effect |
|---|---|
| `1` | Display F1 (nearest feature point distance) |
| `2` | Display F2 (2nd nearest distance) |
| `3` | Display F2-F1 (edge detection: cell boundaries) |
| `4` | Display combined gradient |
| `s` | Save screenshot |

## Algorithm

Worley noise measures the distance from each pixel to the nearest set of randomly distributed feature points. It provides multiple distance metrics:

- **F1**: Distance to nearest point (Voronoi cell centers)
- **F2**: Distance to 2nd nearest point
- **F2-F1**: Difference between 2nd and nearest (creates cell edges)

The feature points are animated using Perlin noise, creating flowing cellular patterns. This creates organic textures resembling cracks, skin, cellular organisms, or stone surfaces.

## Other Environments

**TouchDesigner**: Use the GLSL TOP with the `shader/worley/` fragment shader. Animate the time uniform via a CHOP for moving cells.

**UE5**: Material Editor has a `VoronoiNoise` node that provides equivalent Worley distance fields with built-in animation parameters.
