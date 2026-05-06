# De Casteljau Subdivision

Visualizes Bezier curve evaluation through repeated linear interpolation.

## Run

```bash
uv run python src/logic_lab/mathematical/de_casteljau_subdivision/de_casteljau_subdivision.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Drag point | Move a control point |
| `n` | Switch control-point preset |
| Space | Pause or resume interpolation animation |
| `c` | Toggle completed curve |
| `s` | Save screenshot |

## Algorithm

De Casteljau's algorithm evaluates a Bezier curve using only linear interpolation:

1. **Start with control points**: These define the curve's shape.
2. **Interpolate adjacent points**: For parameter `t`, lerp between every adjacent pair.
3. **Repeat by level**: Each level has one fewer point.
4. **Read final point**: The last remaining point lies on the Bezier curve at `t`.

The same construction can split a Bezier curve into two smaller Bezier curves at any parameter. It is numerically stable and works for any curve degree.

## Other Environments

**TouchDesigner**: Store control points in a DAT or CHOP and iteratively interpolate adjacent rows. Draw each level as separate line strips.

**UE5**: Use Blueprint or C++ to interpolate control points per frame and draw debug lines, spline points, or procedural curve meshes.
