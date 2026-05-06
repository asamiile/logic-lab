# Convex Hull

Finds the smallest convex polygon that contains a set of points.

## Run

```bash
uv run python src/logic_lab/mathematical/convex_hull/convex_hull.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Click | Add a point |
| `r` | Regenerate random points |
| `+` / `-` | Change random point count |
| `f` | Toggle hull fill |
| `o` | Toggle sorted point path |
| `s` | Save screenshot |

## Algorithm

This sketch uses Andrew's monotonic chain algorithm:

1. **Sort points**: Order points by x coordinate, then y coordinate.
2. **Build lower hull**: Walk left to right and remove turns that bend clockwise or stay collinear.
3. **Build upper hull**: Walk right to left with the same turn test.
4. **Join chains**: Combine both chains to form the outer convex polygon.

The cross product determines whether three points make a left turn. Removing non-left turns keeps only the outside boundary. Convex hulls are useful for point-cloud silhouettes, collision bounds, spatial summaries, and generative compositions that need an enclosing shape.

## Other Environments

**TouchDesigner**: Sort point coordinates in a Python DAT, compute the hull indices, and draw the result as a closed Polyline SOP or instanced edge geometry.

**UE5**: Compute hull vertices in C++ or Blueprint for 2D point sets, then use them for collision outlines, procedural mesh boundaries, or debug drawing.
