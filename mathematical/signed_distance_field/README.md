# Signed Distance Field

Visualizes shape composition with signed distance functions.

## Run

```bash
uv run python mathematical/signed_distance_field/signed_distance_field.py
```

## Controls

| Key | Effect |
|---|---|
| `m` | Switch SDF operation |
| `c` | Toggle contour lines |
| Space | Pause or resume animation |
| `s` | Save screenshot |

## Algorithm

A signed distance field stores the distance from each point to the nearest shape boundary:

1. **Signed distance**: Negative values are inside a shape, positive values are outside.
2. **Primitive SDFs**: Circle, box, and rounded-box functions describe simple shapes.
3. **Boolean operations**: `min`, `max`, and negation combine primitives into union, intersection, and subtraction.
4. **Smooth blending**: Smooth union rounds the transition between shapes.
5. **Contours**: Distance levels create isolines, with the zero contour marking the exact boundary.

SDFs are useful for procedural shape design, morphing symbols, vector-like organic forms, and shader-friendly geometry.

## Other Environments

**TouchDesigner**: Implement SDF primitives in GLSL TOPs. Combine fields with `min`, `max`, and smooth-min functions, then color by distance or threshold the zero contour.

**UE5**: Use Material Functions for SDF primitives and smooth boolean operations. Drive shape parameters from Blueprint or Material Parameter Collections.
