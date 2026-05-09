# Impasto Rendering

Thick paint texture with visible brush strokes and 3D relief. Uses height mapping and directional lighting to create the impression of actual paint thickness and surface texture.

```bash
uv run python src/logic_lab/research/impasto_rendering/impasto_rendering.py
```

## Algorithm

1. **Height Map**: Track paint thickness in addition to color
2. **Sobel Filter**: Compute surface normals from height gradients
3. **Directional Lighting**: Apply diffuse and specular lighting based on surface normals
4. **Relief Effect**: Higher areas cast shadows, creating 3D appearance

## Controls

- **Drag Mouse** — Paint with current color
- **1/2/3** — Switch color (red/blue/green)
- **C** — Clear canvas
- **S** — Save screenshot

## Visual Features

- 3D relief from height mapping
- Directional lighting with ambient + diffuse + specular components
- Visible brush stroke edges
- Glossy surface with highlights
- Soft shadow falloff

## Parameters

- `STROKE_RADIUS = 25` — Brush size
- `HEIGHT_SCALE = 2.0` — Exaggeration of height differences
- `AMBIENT_LIGHT = 0.3` — Base lighting level
- `LIGHT_DIRECTION = [0.5, 0.5, 1.0]` — Light source position (normalized)

## References

- Freschi, G. & Couprie, M. (2008). "3D Brush Strokes for Generic Volumetric Data Visualization"
- Hertzmann, A. & Zorin, D. (2000). "Illustrating Smooth Surfaces"
