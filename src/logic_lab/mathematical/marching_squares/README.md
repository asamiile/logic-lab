# Marching Squares

Extract contour lines from a sampled scalar field.

## Run

```bash
uv run python src/logic_lab/mathematical/marching_squares/marching_squares.py
```

## Controls

| Key | Effect |
|---|---|
| `f` | Toggle scalar field color |
| `g` | Toggle sampling grid |
| `m` | Switch contour mode |
| Space | Pause or resume animation |
| `s` | Save screenshot |

## Algorithm

Marching squares converts a 2D field of values into isolines:

1. **Sample the field**: Store scalar values on a regular grid.
2. **Classify each cell**: Compare the four cell corners against a threshold.
3. **Find edge crossings**: Interpolate along cell edges where the threshold changes side.
4. **Draw segments**: Connect crossings into short line segments that approximate the contour.

The sketch draws several threshold levels over an animated field made from Gaussian blobs and sine waves. Interpolation keeps the contours smooth even though the field is sampled on a coarse grid.

Marching squares is useful for:

- Topographic contour maps
- Metaball outlines
- Noise field linework
- Scalar-field visualization
- Vector-friendly organic boundaries

## Other Environments

**TouchDesigner**: Generate a scalar field in a TOP or CHOP, then use GLSL to classify each cell and draw isoline segments. For a texture-based workflow, threshold several blurred noise fields and use edge detection for contour bands.

**UE5**: Use material functions to build signed or scalar fields, then render contour bands with threshold and `smoothstep`. For mesh generation, run marching squares on a grid in Blueprint or C++ and emit spline segments.
