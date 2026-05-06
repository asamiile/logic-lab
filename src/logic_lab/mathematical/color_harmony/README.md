# HSV Color Harmony Palette

Generate harmonious color palettes using HSB color space, with animated hue cycling driven by Perlin noise.

## Run

```bash
uv run python src/logic_lab/mathematical/color_harmony/color_harmony.py
```

## Controls

| Key | Effect |
|---|---|
| `1` | Complementary harmony (hue + 180°) |
| `2` | Analogous harmony (hue ± 30°) |
| `3` | Triadic harmony (hue + 120°, +240°) |
| `s` | Save screenshot |

## Algorithm

The sketch generates harmonious color palettes by computing derived hues from a base hue:

- **Complementary**: Two colors opposite on the color wheel (180° apart)
- **Analogous**: Three colors adjacent on the wheel (30° apart)
- **Triadic**: Three colors evenly spaced (120° apart)

The base hue is animated using Perlin noise, creating smooth transitions. Each color is displayed at three brightness levels (dark, normal, light) for easy reference.

## Other Environments

**TouchDesigner**: Use the `Color TOP` with animated hue input to drive the same color harmonies. Connect a `Noise CHOP` to the hue parameter for animation.

**UE5**: Use `Make Color` with HSV mode in Material Editor. Animate the S and V channels independently, driven by a `Sine` or `Panner` material function for continuous hue shifts.
