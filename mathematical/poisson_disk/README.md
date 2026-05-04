# Poisson Disk Sampling

Generate spatially uniform point distributions using Bridson's fast Poisson disk sampling algorithm.

## Run

```bash
uv run python mathematical/poisson_disk/poisson_disk.py
```

## Controls

| Key | Effect |
|---|---|
| `←` / `→` | Decrease / increase minimum distance |
| `+` / `-` | Increase / decrease max candidate samples |
| `r` | Regenerate with current parameters |
| `s` | Save screenshot |

## Algorithm

Bridson's Poisson disk sampling generates point sets where each point is guaranteed to be at least `min_distance` away from all other points, while maintaining uniform spatial distribution. The algorithm uses:

1. **Grid-based acceleration**: Points are stored in a spatial grid to speed up nearest-neighbor queries
2. **Active list**: Newly sampled points are kept in an active list for candidate generation
3. **Random candidate sampling**: For each active point, k random candidates are tested around it
4. **Removal**: Points that fail to generate valid neighbors are removed from active list

This avoids clustered distributions and creates aesthetically pleasing scatter layouts.

## Other Environments

**TouchDesigner**: The `generate_points` function can be ported to a Script DAT. Output points as SOP geometry (vertices) using `P` attributes.

**UE5**: The PCG Graph includes a native "Poisson Disk" node under Spawning > Point Distribution. Use it as a drop-in replacement for this algorithm.
