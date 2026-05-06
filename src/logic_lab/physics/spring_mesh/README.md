# Interactive Spring Mesh

Elastic deformable mesh using Hooke's law springs and Verlet integration.

## Run

```bash
uv run python src/logic_lab/physics/spring_mesh/spring_mesh.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Mouse drag | Pull on the mesh |
| `w` | Toggle wireframe / filled mode |
| `s` | Save screenshot |

## Algorithm

The spring mesh simulates a 2D grid of particles connected by springs:

1. **Particle dynamics**: Position updated using Verlet integration with damping
2. **Spring constraints**: Adjacent particles attract/repel via Hooke's law: `F = k * (dist - rest_length)`
3. **Constraint iteration**: Springs are solved multiple times per frame for stability
4. **Gravity & damping**: Adds natural fall and energy dissipation
5. **Pinning**: Top row of particles is fixed to anchor the mesh

Interactively dragging particles deforms the mesh in real time, with springs pulling neighboring particles to maintain the structure. This creates fabric-like or gel-like behavior.

## Other Environments

**TouchDesigner**: Use Geometry COMP + Script SOP (Python) to apply spring forces per vertex. Connect to a Point SOP for rendering.

**UE5**: Chaos Cloth system provides native cloth simulation with similar properties. Alternatively, Blueprint graphs with physics constraints on skeletal mesh deformation.
