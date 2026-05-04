# Apollonian Gasket

Generates a recursive packing of mutually tangent circles.

## Run

```bash
uv run python mathematical/apollonian_gasket/apollonian_gasket.py
```

## Controls

| Key | Effect |
|---|---|
| `+` / `-` | Change minimum circle radius |
| `f` | Toggle circle fill |
| `k` | Toggle curvature labels |
| `s` | Save screenshot |

## Algorithm

An Apollonian gasket fills the gaps between tangent circles:

1. **Start with four tangent circles**: One enclosing circle and three inner circles.
2. **Use Descartes' circle theorem**: Circle curvatures satisfy a quadratic relation.
3. **Reflect one circle**: Given four tangent circles, replace one with the other circle tangent to the remaining three.
4. **Repeat recursively**: Add smaller tangent circles until the minimum radius is reached.

Curvature is the reciprocal of radius. The enclosing circle uses negative curvature, which lets the same reflection formula generate inner tangent circles.

## Other Environments

**TouchDesigner**: Generate circle centers and radii in a Python DAT, then instance circle SOPs or draw them in a GLSL TOP. Use curvature as a color or scale attribute.

**UE5**: Precompute the tangent circle list in C++ or Blueprint and render circles as instanced disks, decals, or procedural mesh rings.
