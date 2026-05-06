# Quasicrystal Interference

Generates quasi-periodic patterns by summing plane waves.

## Run

```bash
uv run python src/logic_lab/mathematical/quasicrystal_interference/quasicrystal_interference.py
```

## Controls

| Key | Effect |
|---|---|
| `n` | Switch symmetry count |
| `+` / `-` | Change wave frequency |
| `t` | Toggle threshold display |
| `r` | Toggle reference rings |
| Space | Pause or resume phase animation |
| `s` | Save screenshot |

## Algorithm

The sketch sums plane waves pointing in evenly spaced directions:

```text
value(x, y) = average(cos(k * dot(direction_i, position) + phase_i))
```

When the direction count does not align with ordinary wallpaper periods, the overlapping waves create quasi-periodic structure. The pattern has local order and strong rotational symmetry, but it does not repeat like a normal grid.

This is useful for quasi-crystal textures, moire-like fields, ornamental backgrounds, and mathematical symmetry studies.

## Other Environments

**TouchDesigner**: Implement the wave sum in a GLSL TOP and expose symmetry, frequency, and phase as uniforms.

**UE5**: Use a Custom material node to sum directional cosine waves in UV space. Threshold the field for tile-like bands or use continuous color for interference textures.
