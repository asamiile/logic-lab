# Metaball Field

Implicit surface visualization using blended distance fields.

## Run

```bash
uv run python mathematical/metaball/metaball.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Mouse drag | Move selected metaball |
| `+` | Add new metaball |
| `-` | Remove last metaball |
| `s` | Save screenshot |

## Algorithm

Metaballs blend influence fields from multiple spheres:

1. **Influence function**: At each pixel, sum contributions from all metaballs: `f(r) = radius² / distance²`
2. **Field visualization**: Color each pixel by the total influence
3. **Implicit surface**: The region where total influence ≥ threshold forms a smooth "blob"
4. **Smoothness**: Unlike hard geometry, overlapping fields create smooth junctions

When metaballs merge, they flow together naturally. The mathematical formula creates:
- Soft, organic shapes
- Smooth blending where spheres overlap
- Liquid-like behavior with gravity-free dynamics

## Other Environments

**TouchDesigner**: `shader/advanced_sdf/` includes SDF morphing examples. Use `SmoothMin` to blend multiple sphere SDFs in a GLSL TOP.

**UE5**: Material Editor's `SDF` node library. Use `SmoothUnion` function to blend multiple SDF shapes with controllable blend radius.
