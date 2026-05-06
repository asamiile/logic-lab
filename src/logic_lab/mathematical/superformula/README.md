# Superformula

Draws organic radial shapes from Johan Gielis' superformula.

## Run

```bash
uv run python src/logic_lab/mathematical/superformula/superformula.py
```

## Controls

| Key | Effect |
|---|---|
| `p` | Switch parameter preset |
| `+` / `-` | Change layer count |
| Space | Pause or resume animation |
| `d` | Toggle sampled points |
| `s` | Save screenshot |

## Algorithm

The superformula generalizes circles, polygons, stars, flowers, and organic outlines with one polar equation:

1. **Angle sweep**: Sample angles around a full circle.
2. **Radius equation**: Compute radius from parameters `m`, `n1`, `n2`, and `n3`.
3. **Polar conversion**: Convert `(radius, theta)` into Cartesian vertices.
4. **Layering**: Draw scaled parameter variations to create nested forms.

Small parameter changes can shift the result from smooth petals to sharp crystals or shell-like shapes. The sketch animates the exponents lightly so the outlines breathe without losing their mathematical structure.

## Other Environments

**TouchDesigner**: Use a Script SOP or GLSL shader to sample the polar equation and emit curve points. Animate `m`, `n1`, `n2`, and `n3` with CHOPs.

**UE5**: Generate a procedural spline or mesh from sampled polar coordinates. Drive the formula parameters from Material Parameter Collections or Blueprint timelines.
