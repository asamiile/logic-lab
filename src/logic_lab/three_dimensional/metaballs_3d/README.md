# 3D Metaballs with Perspective Projection

Creates organic, morphing 3D shapes by blending multiple spherical potential fields in 3D space. Uses perspective projection with Y-axis rotation to display the 3D scene on a 2D screen with depth-based coloring.

```bash
uv run python src/logic_lab/three_dimensional/metaballs_3d/metaballs_3d.py
```

Press `↑/↓` to adjust rotation speed, `0-9` to set resolution, `d` for debug mode, `s` to save a screenshot, or `r` to reset.

Each point in 3D space contributes a potential value based on distance from metaball centers. When the combined potential exceeds a threshold, the point is rendered as part of the surface with depth-based coloring.
