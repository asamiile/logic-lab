# Wave Function Collapse (WFC)

Procedural generation algorithm via constraint satisfaction. Starts with maximum entropy, collapses cells probabilistically, then propagates constraints.

```bash
uv run python src/logic_lab/tiling_patterns/wave_function_collapse/wave_function_collapse.py
```

## Algorithm

1. **Initialize**: Each cell contains all possible tiles
2. **Observe**: Select undetermined cell with minimum entropy (fewest possibilities)
3. **Collapse**: Randomly choose one tile from that cell's possibilities
4. **Propagate**: Remove impossible tiles from neighboring cells based on adjacency rules
5. **Repeat** until grid is fully determined or contradiction occurs

## Complexity

- **Greedy Heuristic**: Minimum entropy + random tie-breaking produces coherent results
- **Backtracking**: On contradiction, restart (simple version, no fancy recovery)
- **Scalability**: Grid size affects performance significantly (exponential in theory, but heuristic makes it practical)

## Controls

- **Space** — Restart generation
- **S** — Save screenshot

## Visual Features

- Tiles represented as 3x3 patterns (cross, corner, line, full, empty)
- Color-coded tiles for clarity
- Real-time collapse progress
- Constraint propagation prevents invalid adjacencies

## Possible Extensions

- More complex tile sets (Wang tiles with edge constraints)
- Better heuristics (weighted entropy, history-aware selection)
- Backtracking with state stack for correct implementation
- Rotations/reflections of tiles
- 3D WFC extension

## References

- Gumin, M. (2016). "Wave Function Collapse" [GitHub implementation]
- Merrell, P. (2007). "Example-based Procedural Worlds"
- Knuth, D. E. (1992). "The Art of Computer Programming" (Backtracking)
