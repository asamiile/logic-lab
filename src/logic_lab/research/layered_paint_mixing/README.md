# Layered Paint Mixing

Multiple reaction-diffusion layers with different colors that blend together. Each layer evolves independently, then combined with various blending modes to create complex, layered paint effects.

```bash
uv run python src/logic_lab/research/layered_paint_mixing/layered_paint_mixing.py
```

## Algorithm

1. **Multiple RD Layers**: 3 independent Gray-Scott systems with same parameters
2. **Independent Evolution**: Each layer develops its own patterns
3. **Color Assignment**: Each layer gets a base color (red, blue, green)
4. **Blending**: Layers combine using screen, multiply, overlay, or normal modes

## Controls

- **Drag Mouse** — Add stimulus to active layer
- **1/2/3** — Switch active layer
- **B** — Cycle blending mode (screen → multiply → overlay → normal)
- **C** — Clear all layers
- **S** — Save screenshot

## Visual Features

- Independent reaction-diffusion patterns per layer
- Multiple blending modes for different visual effects
- Interactive layer switching
- Real-time pattern evolution
- Complex emergent colors from blended layers

## Blending Modes

- **Screen**: Lightening blend (1 - (1-a)(1-b)), creates bright overlaps
- **Multiply**: Darkening blend (a*b), creates dark overlaps
- **Overlay**: Combines screen and multiply based on base brightness
- **Normal**: Top layer only (useful for layer masking effects)

## Parameters

- `LAYER_COUNT = 3` — Number of layers
- `FEED_RATE = 0.055` — Pattern formation rate
- `KILL_RATE = 0.062` — Pattern dissolution rate
- `Du = 0.16` — U diffusion rate
- `Dv = 0.08` — V diffusion rate

## References

- Pearson, J. E. (1993). "Complex Patterns in a Simple System"
- Turing, A. M. (1952). "The Chemical Basis of Morphogenesis"
