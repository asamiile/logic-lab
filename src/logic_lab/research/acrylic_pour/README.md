# Acrylic Pour

Fluid dynamics simulation with gravity and viscosity. Paint is poured into a canvas and flows downward under gravity while mixing and spreading. Creates organic, natural-looking fluid patterns.

```bash
uv run python src/logic_lab/research/acrylic_pour/acrylic_pour.py
```

## Algorithm

1. **Gravity**: Constant downward acceleration applied to velocities
2. **Semi-Lagrangian Advection**: Colors trace backwards along velocity field
3. **Viscosity**: Velocity decays over time due to friction
4. **Diffusion**: Colors spread horizontally to neighboring pixels
5. **Injection**: Mouse input adds color and velocity at pour location

## Controls

- **Drag Mouse** — Pour paint at position
- **1/2/3/4** — Switch color (red/blue/green/orange)
- **C** — Clear canvas
- **Space** — Reset (same as clear)
- **S** — Save screenshot

## Visual Features

- Realistic fluid flow under gravity
- Color mixing and blending
- Natural-looking organic patterns
- Interactive real-time simulation
- Multiple color palette support

## Parameters

- `GRAVITY = 0.15` — Downward acceleration strength
- `VISCOSITY = 0.98` — Velocity damping (higher = more persistent flow)
- `DIFFUSION = 0.95` — How much color spreads (higher = more spread)
- `DISSIPATION = 0.99` — How quickly velocity fades
- `INJECT_RADIUS = 15` — Pour area size in pixels

## Physics Notes

- Uses semi-Lagrangian advection for stability
- Gravity accumulates in vel_y each frame
- Viscosity provides damping to prevent infinite spread
- Surface tension effects approximated with horizontal diffusion
- No pressure projection (simplified version for speed)

## References

- Stam, J. (1999). "Stable Fluids"
- Fedkiw, R., Stam, J., & Jensen, H. W. (2001). "Visual Simulation of Smoke"
