# Complex Domain Coloring

Visualizes complex functions by mapping phase and magnitude to color.

## Run

```bash
uv run python mathematical/complex_domain_coloring/complex_domain_coloring.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch complex function |
| `+` / `-` | Zoom in or out |
| `g` | Toggle complex grid |
| `l` | Toggle phase and magnitude lines |
| Space | Pause or resume animated parameters |
| `s` | Save screenshot |

## Algorithm

Domain coloring shows a complex function over the complex plane:

1. **Sample the plane**: Treat each canvas point as a complex input `z`.
2. **Evaluate a function**: Compute values such as `z^2 - 1`, `1/z`, `sin(z)`, or a Mobius transform.
3. **Color by phase**: Use the output angle as hue.
4. **Shade by magnitude**: Use output size to modulate brightness.
5. **Add isolines**: Phase and magnitude bands reveal zeros, poles, branch-like structure, and symmetry.

Zeros appear where all hues meet around dark centers. Poles and singularities create tight color cycles and magnitude rings.

## Other Environments

**TouchDesigner**: Implement the complex function in a GLSL TOP. Use `atan(y, x)` for hue and `log(length(z))` for magnitude bands.

**UE5**: Build equivalent complex arithmetic in a Material Function or Custom node, then map phase and magnitude to material color.
