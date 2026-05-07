# Space Colonization Algorithm

```bash
uv run python src/logic_lab/fractals/space_colonization/space_colonization.py
```

## Overview

An organic branching algorithm for trees, leaf veins, and root fans. Growth nodes extend toward nearby attractor points, averaging local influences so branches naturally split into vascular or botanical structures.

## Algorithm

1. Place a root node
2. Distribute attractor points in a tree crown, leaf mask, or root fan
3. Assign each attractor to the nearest reachable branch node
4. Grow each node toward the average direction of its assigned attractors
5. Remove attractors when reached; add new branch nodes
5. Repeat

## Controls

- Press `1`, `2`, or `3` for tree crown, leaf veins, and root fan presets.
- Press `a` to show or hide attractor points.
- Press `r` to restart the current preset.
- Press `s` to save a screenshot to `fractals/space_colonization/screenshots/`.

## Parameters

- `kill_distance`: distance at which an attractor is consumed
- `max_distance`: maximum influence radius for growth
- `step_size`: branch segment length

## Visual Output

Branches grow progressively from the root, forming trees, vascular leaf networks, or root-like organic systems.

## References

- Runions, A., Lane, B., & Prusinkiewicz, P. (2007). "Modeling trees with a space colonization algorithm"
- The Nature of Code - Chapter 8
