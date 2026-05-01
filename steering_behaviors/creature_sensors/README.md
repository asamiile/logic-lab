# Creature Sensors

```bash
uv run python simulation/creature_sensors/creature_sensors.py
```

- Interactive demonstration of creature sensory input
- Creature (black circle) follows your mouse
- Food (gray circle) sits in the center of the screen
- Creature has 15 directional sensors arranged in a circle
- Sensors detect proximity to food and light up
- Move the creature close to the food to see sensors activate
- Press `s` to save a screenshot to `simulation/creature_sensors/screenshots/`

## How It Works

### Sensors
- Each creature has 15 sensors arranged 360° around its body
- Sensors point outward in evenly-spaced directions
- Each sensor has a detection range equal to the food radius

### Sensing
When the creature senses food:
1. Each sensor computes its endpoint (creature position + sensor direction)
2. Measures distance from endpoint to food center
3. If within food radius:
   - Activation = 1 - (distance / radius)
   - Closer to center = higher activation (max 1.0 at center)
   - At edge = low activation (near 0)
4. If outside food radius: activation = 0

### Visualization
- Black lines show sensor directions
- When activated, sensors display as circles
- Circle color brightness = activation intensity
- Brighter = stronger food signal

## Interaction

- **Move mouse**: Position the creature
- **S key**: Save screenshot

## Educational Value

This example demonstrates:
1. **Sensory input**: How agents perceive their environment
2. **Distance sensing**: Measuring proximity to objects
3. **Directional awareness**: Having multiple sensors in different directions
4. **Signal strength**: Information encoded as continuous values (0-1)

These sensor inputs can be fed into a neural network to train creatures to move toward food! This is the foundation for sensory-based neuro-evolution examples.

## Next Steps

These sensor values could be:
- Fed into a neural network to control creature movement
- Used with genetic algorithms to evolve seeking behavior
- Controlled to learn more complex sensory processing
