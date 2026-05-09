# Lorenz Attractor

A classic chaotic 3D system revealing sensitive dependence on initial conditions and fractal structure.

```bash
uv run python src/logic_lab/mathematical/lorenz_attractor/lorenz_attractor.py
```

## Algorithm

The Lorenz equations describe atmospheric convection:

```
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y
dz/dt = xy - βz
```

Where:
- **σ** (sigma): Prandtl number (default: 10)
- **ρ** (rho): Rayleigh number (default: 28, produces chaos)
- **β** (beta): Geometric factor (default: 8/3)

## Parameters

- `SIGMA = 10.0` — Controls x-y coupling
- `RHO = 28.0` — Controls chaotic regime (>24.74 = chaos)
- `BETA = 8/3` — Aspect ratio

## Controls

- **Space** — Clear trail
- **R** — Reset rotation
- **Z/X** — Zoom in/out
- **S** — Save screenshot

## Visual Features

- Butterfly-like wings emerge from the attractor
- Color gradient from z-coordinate reveals trajectory depth
- 3D rotation shows the fractal structure
- Trail length increases to 5000 points

## References

- Lorenz, E. N. (1963). "Deterministic Nonperiodic Flow"
- Wikipedia: Lorenz System
