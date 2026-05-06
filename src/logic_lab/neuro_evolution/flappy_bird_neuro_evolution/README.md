# Flappy Bird with Neuro-Evolution

```bash
uv run python src/logic_lab/neuro_evolution/flappy_bird_neuro_evolution/flappy_bird_neuro_evolution.py
```

- Population of 200 birds, each controlled by its own neural network
- Birds learn to play Flappy Bird through genetic algorithm and neuro-evolution
- Each bird's brain is a neural network with 4 inputs and 2 outputs
- Fitness based on how long the bird survives (frames alive)
- When all birds die, the population reproduces based on fitness
- Successful birds produce offspring (with crossover and mutation)
- Over generations, birds evolve to better play the game
- Watch as the population gradually improves and learns to navigate pipes
- Press `s` to save a screenshot to `neuro_evolution/flappy_bird_neuro_evolution/screenshots/`

## Neural Network Architecture

Each bird's brain:
- **4 inputs** (normalized):
  - Bird's y position
  - Bird's velocity
  - Next pipe's top position
  - Distance to next pipe
- **1 hidden layer**: 8 neurons with sigmoid activation
- **2 outputs**: Activation levels for "flap" vs "no flap"
- **Decision**: If flap output > no flap output, the bird flaps

## Genetic Algorithm Process

1. **Initialization**: Population of 200 birds with random neural networks
2. **Evaluation**: Birds play until all die, fitness = frames survived
3. **Selection**: Normalize fitness scores (divide by total)
4. **Reproduction**:
   - Weighted selection: fitter birds more likely to be parents
   - Crossover: randomly mix parent weights
   - Mutation: randomly adjust weights (1% mutation rate)
5. **Repeat**: Next generation plays the game

## Key Concepts Demonstrated

- **Neuro-evolution**: Evolving neural network weights through genetic algorithms
- **Fitness-based selection**: Fitter individuals are more likely to reproduce
- **Population dynamics**: How populations adapt over time
- **Emergent behavior**: Complex behavior emerging from simple rules
- **Multi-objective learning**: Network learns both to flap and to navigate

## Display Information

- **Generation**: Current generation number
- **Alive**: Number of birds still alive / total population

The simulation shows how simple neural networks and genetic algorithms can create intelligent behavior without explicit programming of the strategy. Birds learn through evolution!
