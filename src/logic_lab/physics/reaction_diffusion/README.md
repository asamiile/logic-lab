# Reaction-Diffusion (Gray-Scott Model)

Emergent organic patterns using the Gray-Scott chemical reaction simulation.

## Run

```bash
uv run python src/logic_lab/physics/reaction_diffusion/reaction_diffusion.py
```

## Controls

| Key | Effect |
|---|---|
| `1-7` | Switch preset |
| `w` | Toggle watercolor render mode |
| `r` | Reset with new random seed |
| `s` | Save screenshot |

### Presets

- **1. Coral** (F=0.0095, k=0.057): branching coral structures
- **2. Mitosis** (F=0.046, k=0.063): cell-like division patterns
- **3. Fingerprint** (F=0.039, k=0.058): ridge-like patterns
- **4. Worms** (F=0.078, k=0.061): writhing worm-like shapes
- **5. Spirals** (F=0.0545, k=0.062): rotating spiral vortices
- **6. Watercolor Bleed** (F=0.014, k=0.054): soft ink-like spreading ✨ *watercolor mode recommended*
- **7. Watercolor Tendrils** (F=0.037, k=0.060): fine filaments like dry brush ✨ *watercolor mode recommended*

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

### Watercolor Mode

The watercolor render mode combines the Gray-Scott simulation with paper texture and soft edge rendering to create ink-like visual effects:
- **Paper texture**: Perlin noise simulates paper grain, affecting ink diffusion (capillary effect)
- **Soft edges**: Gaussian filtering creates ink bleeding at boundaries
- **Wet-edge brightening**: Edges appear lighter due to ink concentration gradients
- **Indigo ink color**: Custom color mapping for watercolor appearance

## Other Environments

**TouchDesigner**: Use Feedback TOP with dual-buffer rendering and custom GLSL shader implementing the Gray-Scott update equations for GPU acceleration.

**UE5**: Render Target ping-pong with Material Editor implementing the reaction-diffusion equations. Use Niagara for real-time visualization or Material parameter updates.
