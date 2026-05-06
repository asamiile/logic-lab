# Flowlines Streamline Visualization

Visualize invisible vector flow fields using streamline tracing with animated Perlin noise.

## Run

```bash
uv run python src/logic_lab/steering_behaviors/flowlines/flowlines.py
```

## Controls

| Key | Effect |
|---|---|
| `s` | Save screenshot |

## Algorithm

Flowlines visualize vector fields by tracing integral curves (streamlines):

1. **Flow field**: At each point, compute direction using Perlin noise: `angle = noise(x, y, t) * 2π`
2. **Streamline tracing**: Start from random points and follow the field using Euler integration: `p_next = p + v * dt`
3. **Visualization**: Draw continuous curves representing particle paths through the field
4. **Animation**: The noise field changes over time, creating flowing motion

The result shows wind-like currents, flow patterns, and invisible forces made visible. By avoiding explicit agents, it focuses purely on the aesthetic motion patterns.

## Other Environments

**TouchDesigner**: Use the `shader/fbm_warp/` domain warp shader in a GLSL TOP. Particle SOP can trace paths through the velocity field.

**UE5**: Niagara system with velocity field sampling. Use `Sample Velocity Field` node with a custom texture as the flow map.
