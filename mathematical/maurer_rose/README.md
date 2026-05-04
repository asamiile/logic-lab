# Maurer Rose

Draws modular chord patterns over polar rose curves.

## Run

```bash
uv run python mathematical/maurer_rose/maurer_rose.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch preset |
| `r` | Toggle base rose curve |
| `l` | Toggle Maurer line path |
| Space | Pause or resume step animation |
| `s` | Save screenshot |

## Algorithm

A rose curve is defined in polar coordinates:

```text
r = sin(n * theta)
```

A Maurer rose samples that curve with a fixed angular step, then connects those sampled points in order:

1. **Choose petal count**: The parameter `n` controls the rose symmetry.
2. **Step through angles**: Sample `theta = i * d`, where `d` is a step angle in degrees.
3. **Convert to points**: Map each polar coordinate to Cartesian space.
4. **Connect samples**: The chord path creates woven, modular-looking structures.

Small changes to the step angle can produce very different lace, star, and rosette patterns.

## Other Environments

**TouchDesigner**: Generate sampled polar points in a Script SOP or CHOP and draw the connected path as a Polyline SOP.

**UE5**: Sample the polar equation in Blueprint or C++ and render the connected points with splines, Niagara ribbons, or procedural mesh strips.
