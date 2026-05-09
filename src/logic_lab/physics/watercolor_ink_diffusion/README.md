# Watercolor Ink Diffusion

```bash
uv run python src/logic_lab/physics/watercolor_ink_diffusion/watercolor_ink_diffusion.py
```

Watercolor ink diffusion simulates pigment spreading across textured paper. A low-resolution density grid tracks pigment and wetness, paper grain changes the diffusion rate, and darker wet edges form around drying regions.

## Controls

- Hold the mouse to add ink drops.
- Press Space to pause or resume automatic drops.
- Press `p` to switch pigment palette.
- Press `t` to toggle paper texture influence.
- Press `r` to reset the paper.
- Press `s` to save a screenshot to `physics/watercolor_ink_diffusion/screenshots/`.

Good for watercolor washes, paper ink bleed, soft stain maps, pigment pools, wet edges, and organic background textures.
