# Physarum Transport Networks (Slime Mold)

```bash
uv run python src/logic_lab/biological/physarum/physarum.py
```

## Overview

An algorithm where slime mold agents follow chemical attractants (pheromones) to form efficient transport networks connecting attractor points. Models real-world slime mold and fungal network behavior.

## Algorithm

1. Place multiple agents (slime mold cells) in space
2. Place multiple attractors (nutrient sources)
3. Each agent:
   - Moves toward nearest attractor
   - Deposits pheromone along path
4. Pheromones decay over time
5. Agents attracted to pheromone concentrations
6. Repeat → network develops

## Parameters

- `num_agents`: Number of agents (default: 400)
- `num_attractors`: Number of attractors (default: 4)
- `deposit_rate`: Pheromone deposit amount (default: 1.0)
- `decay_rate`: Pheromone decay rate (default: 0.95)

## Visual Output

Pheromone networks formed by agents gradually visualize, with complex transport networks self-forming.

## References

- Nakagaki, T., Yamada, H., & Tóth, Á. (2000). "Intelligence: Maze-solving by an amoeboid organism"
- Jones, J. (2015). "Characteristics of Pattern Formation and Evolution in Approximations of Physarum Transport Networks"
