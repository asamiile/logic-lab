# Circle Packing

Grows non-overlapping circles inside selectable boundary masks.

## Run

```bash
uv run python mathematical/circle_packing/circle_packing.py
```

## Controls

| Key | Effect |
|---|---|
| `r` | Reset with a new random seed |
| `m` | Switch boundary mask |
| `f` | Toggle circle fill |
| Space | Pause or resume growth |
| `s` | Save screenshot |

## Algorithm

This sketch uses an incremental circle-packing process:

1. **Sample candidates**: Pick random points inside the current mask.
2. **Reject overlaps**: Keep only points far enough from existing circles.
3. **Grow circles**: Increase each circle radius every frame.
4. **Stop on contact**: Freeze a circle when it touches another circle or the mask boundary.
5. **Repeat**: Continue adding small circles into the remaining gaps.

The result approximates a maximal packing without solving a global optimization problem. It works well for stippled fills, organic bubbles, pebble textures, and decorative masks.

## Other Environments

**TouchDesigner**: Run the packing loop in a Python DAT and instance circles with radius attributes. Boundary masks can come from TOP alpha values or analytic distance tests.

**UE5**: Use Blueprint or C++ to grow circle records over time, then draw them with instanced meshes, Niagara sprites, or procedural materials.
