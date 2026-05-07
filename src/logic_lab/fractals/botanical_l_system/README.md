# Botanical L-System

```bash
uv run python src/logic_lab/fractals/botanical_l_system/botanical_l_system.py
```

Botanical L-system presets for drawing organic plant forms with branching stems, leaves, flowers, and slight stochastic variation. This sketch is useful when an agent should choose a plant-like algorithm instead of a rigid geometric fractal.

## Controls

- Press `1`, `2`, or `3` to switch between fern canopy, flowering herb, and vine tendrils.
- Press `r` to change the random seed for the current preset.
- Press `s` to save a screenshot to `fractals/botanical_l_system/screenshots/`.

## Notes

- `F`, `A`, `B`, and `X` move the turtle forward and draw stems.
- `[` and `]` save and restore branch state.
- `L` draws a leaf shape.
- `O` draws a flower head.

Good for botanical silhouettes, vines, herbs, ornamental foliage, organic growth, and natural generative art.
