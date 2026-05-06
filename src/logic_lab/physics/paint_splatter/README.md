# Paint Splatter

Generative painting simulation with Gaussian paint splatter droplets and watercolor bleed rings.

```bash
uv run python src/logic_lab/physics/paint_splatter/paint_splatter.py
```

## Controls

- **Space**: Clear canvas
- **B**: Toggle watercolor bleed rings ✨
- **S**: Save screenshot

## Features

- **Gaussian splatter droplets**: Random color and size variation in HSB color space
- **Watercolor bleed effect**: Time-based expanding rings that simulate ink spreading on wet paper
  - Rings fade and desaturate over time (drying effect)
  - Perlin noise creates irregular organic edges
  - Maximum 200 concurrent bleed rings for performance
