# Substrate (Crack Pattern Generation)

```bash
uv run python src/logic_lab/research/substrate/substrate.py
```

## Overview

A crack pattern generation algorithm by Jared Tarbell. New cracks propagate perpendicular or parallel to existing cracks, forming realistic fracture patterns found in ground, pottery, and marble.

## Algorithm

1. Place initial crack at center
2. Each iteration: randomly select an existing crack
3. Based on that crack's angle, propagate perpendicular or parallel new cracks
4. Check boundaries and repeat
5. Crack network forms automatically from history

## Parameters

- `cell_size`: Grid size for neighborhood search (default: 5)

## Visual Output

Crack networks expand organically from center, forming realistic fracture patterns.

## References

- Tarbell, J. (2003). "Substrate Texture"
- Generative Art Concept & Computational Systems
