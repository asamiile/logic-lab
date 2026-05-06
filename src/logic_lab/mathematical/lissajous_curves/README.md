# Lissajous Curves

Draws parametric curves from two perpendicular sine waves.

## Run

```bash
uv run python src/logic_lab/mathematical/lissajous_curves/lissajous_curves.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch frequency preset |
| Space | Pause or resume phase animation |
| `d` | Toggle driver waves |
| `p` | Toggle moving point |
| `s` | Save screenshot |

## Algorithm

Lissajous curves combine two harmonic oscillations:

```text
x(t) = A * sin(a * t + delta)
y(t) = B * sin(b * t)
```

The frequency ratio `a:b` controls the number of lobes and crossings. The phase offset `delta` rotates the relationship between the two oscillations, creating knots, bows, loops, and woven closed curves.

These curves are useful for harmonic motion studies, oscilloscope-like visuals, ornamental linework, and simple parametric animation.

## Other Environments

**TouchDesigner**: Generate points in a Script SOP or CHOP using sine channels with different frequencies and phase offsets.

**UE5**: Sample the parametric equation in Blueprint or C++ and draw the result with splines, Niagara ribbons, or procedural mesh strips.
