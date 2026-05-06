# Chaikin Curve Smoothing

Smooths a polyline with Chaikin's corner-cutting algorithm.

## Run

```bash
uv run python mathematical/chaikin_curve_smoothing/chaikin_curve_smoothing.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Drag point | Move a control point |
| `+` / `-` | Change smoothing iterations |
| `c` | Toggle open or closed curve |
| `p` | Toggle control polygon |
| `l` | Toggle intermediate levels |
| `r` | Reset control points |
| `s` | Save screenshot |

## Algorithm

Chaikin smoothing repeatedly cuts the corners of a polyline:

1. **Take each edge**: For every segment from `p0` to `p1`.
2. **Create two points**: Add points at 25% and 75% along the segment.
3. **Replace the path**: The new points form a smoother path.
4. **Repeat**: More iterations produce a rounder curve.

The algorithm is simple, local, and works for both open and closed polylines. It is useful for softening hand-drawn paths, making organic outlines, and turning polygonal shapes into smooth linework.

## Other Environments

**TouchDesigner**: Store polyline points in a DAT or SOP, then apply corner cutting in Python before rebuilding the line strip.

**UE5**: Apply Chaikin smoothing to spline control points in Blueprint or C++ before generating a spline, ribbon, or procedural mesh outline.
