# Harmonograph

Draws damped harmonic curves from paired sine oscillators.

## Run

```bash
uv run python src/logic_lab/mathematical/harmonograph/harmonograph.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch oscillator preset |
| `+` / `-` | Change sample count |
| `p` | Toggle sampled points |
| Space | Pause or resume drawing animation |
| `s` | Save screenshot |

## Algorithm

A harmonograph combines damped oscillations:

```text
x(t) = sin(f1 * t + p1) * e^(-d1 * t) + sin(f2 * t + p2) * e^(-d2 * t)
y(t) = sin(f3 * t + p3) * e^(-d3 * t) + sin(f4 * t + p4) * e^(-d4 * t)
```

Small frequency differences create beats, loops, and slow phase drift. Damping pulls the path inward over time, producing curves that resemble mechanical pendulum drawings.

Harmonographs are useful for ornamental linework, harmonic motion studies, and generative curves with a natural sense of decay.

## Other Environments

**TouchDesigner**: Generate the oscillator channels in CHOPs or Python, then use them as x/y coordinates for a Trail SOP or line strip.

**UE5**: Sample the equations in Blueprint or C++ and draw the result with splines, Niagara ribbons, or procedural mesh strips.
