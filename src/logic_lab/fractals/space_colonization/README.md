# Space Colonization Algorithm

```bash
uv run python src/logic_lab/fractals/space_colonization/space_colonization.py
```

## Overview

An algorithm that generates branching patterns like leaf veins and trees through competitive growth toward attractor points. Growth nodes gradually extend toward nearby attractors, naturally forming realistic branching structures.

## Algorithm

1. Place a root node
2. Distribute random attractor points throughout space
3. Each frame: grow nodes toward nearest attractors
4. Remove attractors when reached; add new nodes
5. Repeat

## Parameters

- `kill_distance`: Distance to attractor for removal (default: 30)
- `max_distance`: Maximum growth distance (default: 100)

## Visual Output

Branches grow progressively from the root, forming complex vein-like networks.

## References

- Runions, A., Lane, B., & Prusinkiewicz, P. (2007). "Modeling trees with a space colonization algorithm"
- The Nature of Code - Chapter 8
