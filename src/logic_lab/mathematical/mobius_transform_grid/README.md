# Mobius Transform Grid

Warps complex-plane grid lines with Mobius transformations.

## Run

```bash
uv run python src/logic_lab/mathematical/mobius_transform_grid/mobius_transform_grid.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch transform preset |
| `g` | Toggle source grid |
| `u` | Toggle transformed unit circle |
| Space | Pause or resume coefficient animation |
| `s` | Save screenshot |

## Algorithm

A Mobius transformation maps complex numbers by:

```text
w = (a * z + b) / (c * z + d)
```

These transformations preserve generalized circles: straight lines and circles map to other lines or circles. The sketch samples vertical and horizontal grid lines in the source complex plane, applies the transform, and draws the warped result.

Mobius transforms are useful for conformal maps, complex-plane distortion, ornamental grids, and visualizing how analytic functions preserve local angles.

## Other Environments

**TouchDesigner**: Apply the complex transform in a GLSL TOP or generate transformed line points in a Script SOP.

**UE5**: Use a Custom material node for UV-space Mobius warps, or precompute transformed polyline vertices in Blueprint or C++.
