# Inverse Square Light Particles

```bash
uv run python src/logic_lab/physics/light_falloff_field/light_falloff_field.py
```

Inverse square light particles visualize illumination that decays with distance. Each particle samples nearby light sources using a `1 / r^2` falloff and brightens according to the mixed intensity.

## Controls

- Hold the mouse to add a temporary light source.
- Press `r` to regenerate the particle field.
- Press `s` to save a screenshot to `physics/light_falloff_field/screenshots/`.

Good for glowing bodies, stars, fireflies, city lights, illumination fields, falloff studies, and radiant particle textures.
