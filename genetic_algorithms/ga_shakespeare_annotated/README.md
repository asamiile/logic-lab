# Genetic Algorithm - Evolving Shakespeare (Annotated)

```bash
uv run python simulation/ga_shakespeare_annotated/ga_shakespeare_annotated.py
```

- Genetic algorithm that evolves a population of random strings toward the target phrase "To be or not to be."
- Population of 200 organisms with randomly generated genes (characters)
- Each generation, organisms are selected for reproduction based on fitness (how close they are to the target)
- Higher-fitness organisms appear more times in the mating pool and are more likely to reproduce
- Offspring are created through crossover and mutation
- Displays the best phrase found so far and statistics about the population
- Evolution stops when the target phrase is reached
- Press `s` to save a screenshot to `simulation/ga_shakespeare_annotated/screenshots/`

## How it works

1. **DNA** - Each organism's DNA is a string of characters
2. **Fitness** - How many characters match the target phrase (0.0 to 1.0)
3. **Selection** - Organisms are added to a mating pool multiple times based on fitness
4. **Reproduction** - Parents are picked from the mating pool and crossover to create children
5. **Mutation** - Each character in a child has a small chance (1%) to mutate to a random character
6. **Repeat** - Process continues until target is found

## Statistics displayed

- **Total generations**: Number of generations evolved
- **Average fitness**: Mean fitness of the current population
- **Total population**: Number of organisms (200)
- **Mutation rate**: Probability each character mutates per generation
- **All phrases**: Display of all organisms in the current population

The example demonstrates how genetic algorithms can solve search problems by maintaining variation in the population and preferentially selecting fit organisms.
