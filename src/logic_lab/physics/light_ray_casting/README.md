# 2D Light Ray Casting

```bash
uv run python src/logic_lab/physics/light_ray_casting/light_ray_casting.py
```

2D light ray casting builds a visibility polygon from a moving light source. Rays are aimed at every obstacle vertex, with tiny angular offsets, and each ray stops at the nearest line-segment intersection. The visible polygon becomes a soft pool of light while the unlit area remains in shadow.

## Controls

- Move the mouse to move the light source.
- Press `v` to toggle the raw rays.
- Press `r` to regenerate the obstacle field.
- Press `s` to save a screenshot to `physics/light_ray_casting/screenshots/`.

Good for streetlights, caves, stage lighting, shadow puppets, visibility fields, and occlusion studies.
