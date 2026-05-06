# Hilbert Curve

Draws a space-filling curve from Hilbert indices.

## Run

```bash
uv run python src/logic_lab/mathematical/hilbert_curve/hilbert_curve.py
```

## Controls

| Key | Effect |
|---|---|
| `+` / `-` | Change curve order |
| Space | Pause or resume drawing animation |
| `p` | Toggle sampled points |
| `g` | Toggle grid |
| `s` | Save screenshot |

## Algorithm

The Hilbert curve maps a one-dimensional index to a two-dimensional grid while preserving locality:

1. **Choose order**: Order `n` creates a `2^n x 2^n` grid.
2. **Convert index to coordinates**: Walk through Hilbert quadrants with bit operations and rotations.
3. **Connect samples**: Draw the points in index order as one continuous curve.
4. **Increase order**: Higher orders visit more cells and approach a space-filling curve.

Nearby indices usually map to nearby grid cells, which makes Hilbert curves useful for spatial indexing, ordered dithering, image traversal, and recursive geometric compositions.

## Other Environments

**TouchDesigner**: Generate Hilbert coordinates in a Python DAT and feed them to a Polyline SOP or instanced point network. Use the index as a color or timing attribute.

**UE5**: Generate point coordinates in Blueprint or C++, then draw them as a spline, debug line path, or procedural mesh strip.
