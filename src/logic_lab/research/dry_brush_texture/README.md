# Dry Brush Texture

Rough, textured brush strokes that interact with paper surface. The brush coverage is modulated by procedural paper texture, creating gaps and variations that mimic real dry brush painting.

```bash
uv run python src/logic_lab/research/dry_brush_texture/dry_brush_texture.py
```

## Algorithm

1. **Paper Texture**: Procedural noise-based surface texture at multiple octaves
2. **Stroke Rendering**: Gaussian brush with coverage modified by paper
3. **Texture Modulation**: High paper texture areas repel paint, creating broken strokes
4. **Blending**: Paint coverage combines brush strength with paper roughness

## Controls

- **Drag Mouse** — Paint with current color
- **1/2/3** — Switch color (warm brown/cool blue-gray/muted green)
- **C** — Clear canvas
- **S** — Save screenshot

## Visual Features

- Procedural paper texture at multiple scales
- Rough, broken brush strokes
- Natural paper-paint interaction
- Warm, earthy color palette
- Varied coverage from texture modulation

## Parameters

- `STROKE_RADIUS = 20` — Brush size in pixels
- `ROUGHNESS = 0.6` — How much texture breaks up strokes (0=smooth, 1=very rough)
- `PAPER_SCALE = 0.05` — Detail level of paper texture
- `PAPER_OCTAVES = 4` — Number of noise layers for texture depth

## References

- Curtis, C. J., Anderson, S. E., Seims, J. E., Fleischer, K. W., & Salesin, D. H. (1997). "Computer-Generated Watercolor"
- Salisbury, M. P., Anderson, S. E., Barzel, R., & Salesin, D. H. (1994). "Interactive Pen-and-Ink Illustration"
