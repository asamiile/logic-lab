# Particle Flow

Animated particles flowing through a Perlin noise vector field with interactive mouse control.

## Run

```bash
uv run python physics/particle_flow/particle_flow.py
```

## Controls

| Action | Effect |
|---|---|
| Mouse drag | Attract/repel particles near cursor |
| `1` | Trails mode (lifetime fade) |
| `2` | Velocity colors (hue by direction) |
| `3` | Lifetime colors |
| `s` | Save screenshot |

## Algorithm

The system combines particle advection with procedural generation:

1. **Vector Field**: Perlin noise generates direction and magnitude at each location
   - `angle = noise(x*0.01, y*0.01, time*0.1) * 2π`
   - `magnitude = noise(x*0.005, y*0.005+100, time*0.1) * 2`

2. **Particle Motion**: 5000 particles move through the field
   - Position += velocity (from field + mouse influence)
   - Particles wrap at boundaries (toroidal space)
   - Reset when lifetime exceeds threshold (255 frames)

3. **Mouse Interaction**: Particles within 150 pixels of cursor experience repulsion/attraction force
   - `force = (1 - distance/150) * 0.5`
   - Creates visible flow disruption

4. **Visualization Modes**:
   - **Trails**: Alpha fade by lifetime → see particle aging
   - **Velocity**: Hue by movement direction → visualize flow patterns
   - **Lifetime**: Color cycle by age → track particle renewal

## Other Environments

**TouchDesigner**: Implement with Particle SOP + TOP using a velocity texture derived from Noise TOP. Use a Geometry COMP to visualize particle positions or trails via feedback rendering.

**UE5**: Use Niagara particle system with Custom Velocity module sampling a 2D noise texture. Apply GPU simulation for 5000+ particle performance. Material can be driven by velocity magnitude for dynamic coloring.
