# Evolving Bloops - Ecosystem Simulation

```bash
uv run python simulation/evolving_bloops/evolving_bloops.py
```

- Genetic algorithm simulation of an evolving ecosystem
- Bloops (creatures) navigate using Perlin noise and have genetically-determined size and speed (size-speed trade-off)
- Bloops eat food to gain health, losing health over time
- When bloops die, they leave food behind
- Bloops can randomly reproduce with mutation (asexual reproduction)
- Bigger bloops have easier time finding food but move slower
- Food randomly appears on the canvas
- Click and drag to spawn new bloops at the mouse position
- Press `s` to save a screenshot to `simulation/evolving_bloops/screenshots/`

## How it works

1. **Bloops (creatures)** are the circle elements on screen
   - Opacity represents health
   - Size represents genetic trait that controls speed
   
2. **Food** appears as small gray squares
   - Bloops eat food to gain health
   - When bloops die, food is left behind at their location
   - Food randomly appears on canvas

3. **Evolution**
   - Each bloop has 1 gene (0-1) controlling the size/speed trade-off
   - Larger bloops are slower but easier to land on food
   - Smaller bloops are faster but harder to hit food
   - Only bloops with enough energy survive to reproduce
   - Genetic traits are passed to offspring with small mutations

4. **Interaction**
   - Click/drag to add bloops at the mouse position
   - Watch how the population evolves over time

The simulation demonstrates natural selection where creatures adapt to the environment's constraints.
