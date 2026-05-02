# Neuro-Evolution Steering Seek

```bash
uv run python steering_behaviors/neuro_evolution_steering_seek/neuro_evolution_steering_seek.py
```

- Population of 50 creatures learning to seek a moving target using neuro-evolution
- Target (glow) moves using Perlin noise
- Each creature controlled by its own neural network
- Creatures improve over generations at seeking the moving target
- Adjustable simulation speed (1x-20x) with arrow keys or mouse click
- Press `s` to save a screenshot to `steering_behaviors/neuro_evolution_steering_seek/screenshots/`

## Neural Network Architecture

Each creature's brain:
- **5 inputs**:
  - Direction to target x (normalized)
  - Direction to target y (normalized)
  - Distance to target (normalized by width)
  - Creature's velocity x (normalized by maxspeed)
  - Creature's velocity y (normalized by maxspeed)
- **1 hidden layer**: 8 neurons with sigmoid activation
- **2 outputs**:
  - Angle of force direction (0-2π)
  - Magnitude of force (0-1)

## How It Works

1. **Each generation**: 250 simulation cycles
2. **Each cycle**:
   - Each creature computes inputs based on target and self state
   - Neural network outputs force angle and magnitude
   - Creature applies force and updates physics
   - Target updates using Perlin noise
   - Creature gains fitness for being close to target
3. **After generation ends**:
   - Fitness is normalized
   - Best creatures selected as parents
   - Crossover and mutation create next generation
   - Process repeats

## Fitness

Fitness = number of frames close to target (within touching distance)

Higher fitness = better at staying near the target = more likely to reproduce

## Genetic Algorithm

- **Selection**: Weighted by fitness
- **Crossover**: Randomly mix parent weights
- **Mutation**: Random adjustments (10% mutation rate)

## Interaction

- **UP arrow**: Increase simulation speed (up to 20x)
- **DOWN arrow**: Decrease simulation speed (minimum 1x)
- **Mouse click**: Set speed based on click position (left = slow, right = fast)
- **S key**: Save screenshot

## Key Concepts

- **Neuro-evolution**: Networks evolve through genetic algorithms
- **Steering behaviors**: Creatures learn to seek moving target
- **Multi-objective**: Must predict target movement and plan trajectory
- **Perlin noise**: Smooth, natural target movement

Watch as creatures gradually develop better seeking strategies. Early generations chase randomly. Later generations anticipate target movement and intercept smoothly!

The adjustable speed lets you observe evolution at different rates - slow it down to see individual creature behavior, speed it up to see population-wide trends.
