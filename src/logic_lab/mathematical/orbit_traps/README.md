# Orbit Traps (Fractal Coloring)

```bash
uv run python src/logic_lab/mathematical/orbit_traps/orbit_traps.py
```

## Overview

An algorithm that colors Mandelbrot and Julia sets based on how close iteration orbits pass to trap shapes (circles, crosses, lines). Produces complex, decorative visuals impossible with traditional iteration-count coloring.

## Algorithm

1. Compute complex number for each pixel
2. Execute Mandelbrot iteration, recording minimum distance to trap shapes
3. Color based on minimum distance or which trap was closest
4. Visualize iteration depth and orbital paths

## Parameters

- `trap_type`: Trap shape ("circle", "cross", "line")
- `zoom`: Zoom level
- `max_iterations`: Iteration count (default: 256)

## Controls

- **C**: Select circle trap
- **X**: Select cross trap
- **L**: Select line trap
- **+**: Zoom in
- **-**: Zoom out

## Visual Output

Different visual patterns emerge for each trap type, with real-time color animation.

## References

- Harley Flanders. "Orbit Traps"
- Pickover, C. A. (1992). "Computers, Pattern, Chaos and Beauty"
