# Truchet Tiling

```bash
uv run python tiling_patterns/truchet_tiling/truchet_tiling.py
```

## Overview

An algorithm that generates continuous curve patterns using randomly oriented quarter-circle tiles. Each tile's 90-degree rotation variations create different patterns, automatically forming an organic curved network across the entire grid.

## Algorithm

1. Generate a grid and randomly assign 0 or 1 to each cell
2. Determine rotation angle (0° or 90°) for each cell
3. Draw quarter-circle arcs within cells
4. Arcs naturally connect with neighbors → continuous curve patterns self-form

## Parameters

- `tile_size`: Tile size in pixels (default: 40)

## Controls

- **SPACE**: Regenerate pattern

## Visual Output

Complex and beautiful curved networks emerge automatically from simple cell configurations.

## References

- Truchet, S. (1704). "Mémoire sur les combinaisons"
- Smith et al. (1996). "Multicurves: Building Vector Images from Raster Sources"
