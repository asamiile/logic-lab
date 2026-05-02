# Neuro-Evolution Ecosystem

```bash
uv run python steering_behaviors/neuroevolution_ecosystem/neuroevolution_ecosystem.py
```

- Complete ecosystem simulation with creatures evolving to survive and reproduce
- Creatures use neural networks to control movement based on sensory input
- Creatures must eat food to maintain health and survive
- Population evolves as successful creatures reproduce with mutations
- Watch emergent behaviors as creatures adapt to their environment
- Adjustable simulation speed (1x-20x) with UP/DOWN arrow keys
- Press `s` to save a screenshot to `steering_behaviors/neuroevolution_ecosystem/screenshots/`

## Creature Architecture

### Sensors
- **15 directional sensors** arranged 360° around creature
- Each sensor detects if food is within its detection range
- Sensor activates (value=1) when food nearby, deactivates otherwise

### Neural Network
- **15 inputs**: One per sensor (0 or 1)
- **1 hidden layer**: 8 neurons with sigmoid activation
- **2 outputs**: 
  - Angle of movement force (0-2π)
  - Magnitude of force (0-1)

### Physiology
- **Health**: Starts at 100, decreases by 0.25 per frame
- **Size**: Visual size correlates with health (full size at 100 health, shrinks toward 0)
- **Movement**: Based on neural network output
- **Max speed**: 2 pixels/frame
- **Screen wrapping**: Creatures wrap around screen edges

## Ecosystem Rules

### Eating
- Creatures gain +0.5 health when touching food
- Food shrinks by 0.05 when eaten
- Food respawns at new location and size (50) when too small

### Reproduction
- 0.1% chance per frame when creature has health > 0
- Child inherits mutated version of parent's neural network
- Mutation rate: 10%
- Child spawns at parent's location

### Death
- Creatures die when health drops below 0
- Removed from population

## Evolution Dynamics

Over time, successful adaptations emerge:
- Creatures learn to seek food effectively using sensors
- Better neural networks produce more offspring
- Population trends toward higher average fitness
- Emergent behaviors like clustering near food or cooperative seeking

## Controls

- **UP arrow**: Increase simulation speed (up to 20x)
- **DOWN arrow**: Decrease simulation speed (minimum 1x)
- **S key**: Save screenshot

## Display Information

- **Creatures**: Current population size
- **Food**: Number of food items
- **Speed**: Current simulation multiplier (1x-20x)

## Key Concepts Demonstrated

1. **Neuro-evolution**: Neural networks evolve through reproduction/mutation
2. **Sensory processing**: Creatures perceive environment and act accordingly
3. **Population dynamics**: Birth, death, and natural selection
4. **Emergent behavior**: Complex behaviors arise from simple rules
5. **Energy economy**: Health as a resource that must be managed
6. **Genetic inheritance**: Successful traits pass to offspring

Watch as the ecosystem develops its own dynamics - some creatures thrive while others perish, populations boom and crash, and collective behaviors emerge from individual neural network decisions!
