# Reaction-Diffusion (Gray-Scott Model)

Emergent organic patterns using the Gray-Scott chemical reaction simulation.

## Run

```bash
uv run python physics/reaction_diffusion/reaction_diffusion.py
```

## Controls

| Key | Effect |
|---|---|
| `1-5` | Switch preset (coral, mitosis, fingerprint, worms, spirals) |
| `r` | Reset with new random seed |
| `s` | Save screenshot |

## Algorithm

The Gray-Scott model simulates two chemical species U and V diffusing and reacting on a 2D grid:

```
∂U/∂t = Da*∇²U - U*V² + F*(1-U)
∂V/∂t = Db*∇²V + U*V² - (F+k)*V
```

Where:
- **Da, Db**: Diffusion rates (set to 1.0 and 0.5)
- **F**: Feed rate (parameter to vary)
- **k**: Kill rate (parameter to vary)
- **∇²**: Laplacian operator (computed with wrap-around boundaries)

Different (F, k) values produce distinct patterns:
- **Coral** (F=0.0095, k=0.057): branching coral structures
- **Mitosis** (F=0.046, k=0.063): cell-like division patterns
- **Fingerprint** (F=0.039, k=0.058): ridge-like patterns
- **Worms** (F=0.078, k=0.061): writhing worm-like shapes
- **Spirals** (F=0.0545, k=0.062): rotating spiral vortices

## Other Environments

**TouchDesigner**: Use Feedback TOP with dual-buffer rendering and custom GLSL shader implementing the Gray-Scott update equations for GPU acceleration.

**UE5**: Render Target ping-pong with Material Editor implementing the reaction-diffusion equations. Use Niagara for real-time visualization or Material parameter updates.
