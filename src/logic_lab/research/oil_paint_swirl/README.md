# Oil Paint Swirl

Interactive painting with flowing and swirling color blending. Colors mix and flow according to a dynamic noise-based flow field, creating organic oil-paint-like effects.

```bash
uv run python src/logic_lab/research/oil_paint_swirl/oil_paint_swirl.py
```

## Algorithm

1. **Flow Field**: Perlin-like noise generates a time-varying 2D vector field
2. **Advection**: Colors move along the flow field, following streamlines
3. **Diffusion**: Adjacent pixels blend their colors together
4. **Damping**: Velocity and color gradually decrease over time

## Controls

- **Drag Mouse** — Paint with current color
- **1/2/3** — Switch color (red/blue/green)
- **C** — Clear canvas
- **S** — Save screenshot

## Visual Features

- Dynamic flow field creates swirling motion
- Color advection along streamlines
- Diffusive blending for oil-paint smoothness
- Interactive real-time painting
- Gaussian brush falloff for soft edges

## Parameters

- `FLOW_SPEED = 0.02` — How fast colors follow the flow
- `DIFFUSION_RATE = 0.98` — How much colors blend with neighbors (higher = more blending)
- `ADVECTION_DAMPING = 0.99` — How quickly motion fades (lower = faster fade)
- `STROKE_RADIUS = 20` — Brush size in pixels

## Extensions

- Multiple color layers with blending modes
- Pressure-sensitive strokes
- Brush shape variations
- Interactive flow field manipulation (mouse-controlled)
