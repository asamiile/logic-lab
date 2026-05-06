# Pen Pressure Curve Simulation

```bash
uv run python src/logic_lab/mathematical/pen_pressure_curve/pen_pressure_curve.py
```

## Overview

Interactive demo of pen pressure smoothing using Bezier interpolation and Kalman filtering. Visualize and learn how digital pen pressure sensing systems work.

## Algorithm

1. Generate pressure values from mouse input (simulated by Y position and sine wave)
2. Remove pressure noise with Kalman filter
3. Interpolate path using quadratic Bezier curves
4. Dynamically adjust stroke width based on pressure values
5. Generate smooth drawing strokes

## Parameters

- `q` (Process Noise): Process noise coefficient (default: 0.01)
- `r` (Measurement Noise): Measurement noise coefficient (default: 1.0)

## Controls

- **Mouse drag**: Draw (pressure varies with Y position)
- **B**: Toggle ink bleed halo (watercolor effect) ✨
- **R**: Reset
- **S**: Save screenshot

## Visual Output

Mouse traces render with line widths responsive to pressure. Observe differences between raw (red) and smoothed (black) frames.

## References

- Welch, G., & Bishop, G. (2006). "An Introduction to the Kalman Filter"
- de Casteljau, P. (1959). "Outillage méthodes calcul"
- Adobe Fresco Brush Pressure Documentation
