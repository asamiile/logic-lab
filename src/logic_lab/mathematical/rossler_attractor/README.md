# Rössler Attractor

A simplified chaotic system with band-like structure and smooth flow, easier to understand than Lorenz.

```bash
uv run python src/logic_lab/mathematical/rossler_attractor/rossler_attractor.py
```

## Algorithm

The Rössler equations describe a simplified oscillator with chaotic feedback:

```
dx/dt = -y - z
dy/dt = x + ay
dz/dt = b + z(x - c)
```

Where:
- **a**: Oscillation parameter (default: 0.2)
- **b**: Forcing parameter (default: 0.2)
- **c**: Control parameter (default: 5.7, produces chaos)

## Parameters

- `A = 0.2` — Linear feedback coefficient
- `B = 0.2` — Constant forcing term
- `C = 5.7` — Chaotic regime threshold (>4.5 = chaos)

## Controls

- **Space** — Clear trail
- **R** — Reset rotation
- **Z/X** — Zoom in/out
- **S** — Save screenshot

## Visual Features

- Band-like spiral structure wraps and folds around itself
- Single lobe on left side, multiple loops on right
- Color varies by y-coordinate (smooth gradient)
- Saturation adds depth based on z-coordinate
- Trail length: 8000 points

## References

- Rössler, O. E. (1976). "An Equation for Continuous Chaos"
- Sprott, J. C. "Simple Chaotic Systems and Circuits"
