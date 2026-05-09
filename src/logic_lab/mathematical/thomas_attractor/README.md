# Thomas Attractor

Produces an elegant knot-like structure with perfect 3-fold rotational symmetry. One of the most beautiful chaotic attractors.

```bash
uv run python src/logic_lab/mathematical/thomas_attractor/thomas_attractor.py
```

## Algorithm

The Thomas equations are a dissipative system with trigonometric nonlinearity:

```
dx/dt = sin(y) - bx
dy/dt = sin(z) - by
dz/dt = sin(x) - bz
```

Where:
- **b**: Dissipation parameter (default: 0.208186 for knot formation)

## Parameters

- `B = 0.208186` — Sweet spot for knot-like structure (discovered by René Thomas)

Varying **b**:
- b < 0.1: Converges to fixed point
- 0.1 < b < ~0.22: Period-doubling route to chaos
- ~0.208: Beautiful knot formation (3-fold symmetry)
- b > 0.22: Still chaotic but simpler structure

## Controls

- **Space** — Clear trail
- **R** — Reset rotation
- **Z/X** — Zoom in/out
- **S** — Save screenshot

## Visual Features

- 3-fold rotational symmetry creates elegant knotwork
- Smooth trigonometric nonlinearity (unlike polynomial Lorenz/Rössler)
- Rainbow color gradient along the trajectory (hue from arc length)
- Trail length: 10000 points for maximum detail
- Reveals intricate knot topology when rotated

## References

- Thomas, R. (1999). "Deterministic Chaos Seen in Terms of Feedback Circuits"
- Sprott, J. C. (1994). "Some Simple Chaotic Flows"
