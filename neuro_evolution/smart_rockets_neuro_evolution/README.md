# Smart Rockets with Neuro-Evolution

```bash
uv run python simulation/smart_rockets_neuro_evolution/smart_rockets_neuro_evolution.py
```

- Population of 150 rockets navigating around obstacles to reach a target
- Each rocket controlled by its own neural network brain
- Rockets learn through neuro-evolution (genetic algorithms + neural networks)
- Target starts at the top center; click to move it anywhere
- Watch rockets improve over generations as they learn the optimal path
- Press `s` to save a screenshot to `simulation/smart_rockets_neuro_evolution/screenshots/`

## Neural Network Architecture

Each rocket's brain:
- **2 inputs** (normalized):
  - Rocket's x position (0-1)
  - Rocket's y position (0-1)
- **1 hidden layer**: 8 neurons with sigmoid activation
- **2 outputs**:
  - Angle of force direction (0-2π)
  - Magnitude of force (0-1, scaled by maxforce)

## Fitness Function

Fitness is calculated as:
```
fitness = 1 / (finishCounter * recordDistance)^4
```

With adjustments:
- **Obstacle penalty**: × 0.1 if rocket hits obstacle
- **Target bonus**: × 2 if rocket reaches target

Shorter times and shorter distances = higher fitness.

## Genetic Algorithm Process

1. **Generation**: 150 rockets run for 300 frames
2. **Evaluation**: Calculate fitness for each rocket
3. **Selection**: Normalize fitness for weighted selection
4. **Reproduction**:
   - Pick two parents based on fitness (weighted selection)
   - Crossover: randomly mix parent weights
   - Mutation: random adjustments (1% mutation rate)
5. **Repeat**: Next generation starts fresh

## Game Mechanics

- **Obstacle**: Horizontal bar in the middle that must be navigated around
- **Target**: Square that rockets must reach (click to move)
- **Physics**: Rockets have acceleration, velocity, and drag
- **Constraints**: Max speed (4) and max force (1)

## Key Concepts

- **Neuro-evolution**: Combining neural networks with genetic algorithms
- **Population-based learning**: Multiple agents learning simultaneously
- **Fitness-based selection**: Better performers breed more
- **Emergent behavior**: Complex navigation strategies emerge from evolution

Over generations, watch rockets develop strategies to:
1. Navigate around the obstacle
2. Reach the target
3. Do it as quickly as possible

This demonstrates how neural networks can be trained through evolution rather than backpropagation, useful when you can't easily define a gradient descent path.
