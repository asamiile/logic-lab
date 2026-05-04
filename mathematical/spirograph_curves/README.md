# Spirograph Curves

Draws hypotrochoid and epitrochoid curves from rolling-circle equations.

## Run

```bash
uv run python mathematical/spirograph_curves/spirograph_curves.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch curve preset |
| Space | Pause or resume drawing animation |
| `g` | Toggle gear guides |
| `p` | Toggle sampled points |
| `s` | Save screenshot |

## Algorithm

Spirograph curves trace a point attached to a circle rolling around another circle:

- **Hypotrochoid**: The rolling circle moves inside the fixed circle.
- **Epitrochoid**: The rolling circle moves outside the fixed circle.

The fixed radius `R`, rolling radius `r`, and pen distance `d` determine the number of lobes and how far the curve loops from the center. The curve closes when the angular motion repeats according to the radius ratio.

These curves are useful for rosettes, guilloche-like linework, orbital diagrams, and harmonic ornamental patterns.

## Other Environments

**TouchDesigner**: Generate parametric points in a Script SOP or CHOP. Animate the parameter `t` and use `R`, `r`, and `d` as exposed controls.

**UE5**: Sample the equations in Blueprint or C++ and draw them with splines, Niagara ribbons, or procedural mesh strips.
