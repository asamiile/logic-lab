# Volumetric Fog

CPU ray-marched 3D fog using fractional Brownian motion (FBM) as the density field. Each pixel casts a ray into the animated volume, accumulating transmittance and color via Beer-Lambert absorption.

```bash
uv run python src/logic_lab/three_dimensional/volumetric_fog/volumetric_fog.py
```

Press `Space` to pause, or `s` to save a screenshot.

Runs at a deliberately low internal resolution (120×90) upscaled 6× to remain interactive in pure Python. Directional sun lighting is approximated by sampling a nearby noise offset along the light direction. Increasing `STEPS` or `RENDER_W`/`RENDER_H` improves quality at the cost of frame rate.
