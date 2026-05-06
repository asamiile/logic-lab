# Diffusion-Limited Aggregation (DLA)

```bash
uv run python src/logic_lab/fractals/dla/dla.py
```

## Overview

An algorithm that generates dendritic and coral-like organic structures as randomly walking particles attach to fixed particles. Models natural phenomena such as crystal growth, electrical trees, and coral formation.

## Algorithm

1. Place a seed particle at the center (attached)
2. Spawn random-walking particles from a circular boundary
3. When a walking particle approaches an attached particle, it attaches
4. Attached particles increase → more complex shapes evolve

## Parameters

- `attraction_distance`: Distance at which particles attach (default: 8)
- `max_particles`: Maximum concurrent walking particles (default: 3000)

## Visual Output

Observe the gradual growth of complex dendritic structures as particles aggregate.

## References

- Witten, T. A., & Sander, L. M. (1981). "Diffusion-Limited Aggregation, a Kinetic Critical Phenomenon"
- The Nature of Code - Chapter 8: Fractals
