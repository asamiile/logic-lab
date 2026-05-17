# Bee Foraging Algorithm

A swarm intelligence simulation based on the Artificial Bee Colony (ABC) algorithm, modeling the collective foraging behavior of honey bees.

## Overview

The Bee Foraging Algorithm simulates how a colony of bees discovers and exploits food sources through simple local interactions and information sharing via waggle dance. Despite individual bees having limited cognition, the colony exhibits intelligent search and optimization behavior.

## Algorithm Phases

### Scout Phase (Exploration)
- Scout bees perform random walk exploration of the search space
- Movement: `position += random_angle * step_size`
- When they discover a food source within `discovery_radius`, they transition to employed phase
- Purpose: Explore unexplored regions and discover new opportunities

### Employed Phase (Exploitation)
- Employed bees exploit assigned food sources through local search
- Search around current site: `new_position = site ± random * search_radius`
- Evaluate nectar quality at new locations
- Track unsuccessful trials (`trial_count`)
- When `trial_count > trial_limit`, the bee abandons the site and becomes a scout
- Purpose: Intensify search around promising solutions

### Onlooker Phase (Decision Making)
- Onlooker bees observe employed bees' waggle dances
- Probability of selecting a food source is proportional to its nectar richness
- Transition to employed phase with probability based on site quality
- Can return to scout phase if no attractive sites exist
- Purpose: Balance exploration and exploitation dynamically

## Class Architecture

### FoodSite
Represents a food source location and its characteristics:
```python
@dataclass
class FoodSite:
    x, y: float              # Position in search space
    nectar: float            # Current nectar richness [0, 1]
    trial_count: int         # Unsuccessful trials since improvement
    best_nectar: float       # Best nectar found at this site
```

### Bee
Represents an individual bee in the colony:
```python
@dataclass
class Bee:
    x, y: float              # Current position
    phase: str               # "scout", "employed", or "onlooker"
    site_index: int          # Assigned food site index (-1 for scouts)
    energy: float            # Energy level [0, 1]
```

### BeeColony
Main simulation class managing the entire colony:
```python
class BeeColony:
    hive_x, hive_y: float              # Hive location
    bees: list[Bee]                    # Bee population
    sites: list[FoodSite]              # Known food sources
    num_scouts: int                    # Number of scout bees
    num_employed: int                  # Number of employed bees
    num_onlookers: int                 # Number of onlooker bees

    def update() -> None               # Update colony state
    def render() -> None               # Visualize colony
    def reset() -> None                # Reset to initial state
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_bees` | 30 | Total number of bees in colony |
| `num_scouts` | 5 | Number of scout bees (~1/6 of population) |
| `trial_limit` | 100 | Max unsuccessful trials before abandoning site |
| `step_size` | 5.0 | Distance scouts move per frame |
| `discovery_radius` | 50.0 | Radius within which scouts discover sites |
| `search_radius` | 50.0 | Radius for employed bees' local search |

## Visualization

### Colors
- **Scout Bees**: Red
- **Employed Bees**: Blue
- **Onlooker Bees**: Green
- **Hive**: Black circle (center)
- **Food Sites**: Yellow/Gold circles, brightness indicates nectar richness

### Debug Mode
When enabled (press 'd'), displays:
- Trial count for each food site
- Phase distribution statistics
- Frame counter and status

## Controls

| Key | Action |
|-----|--------|
| 'r' | Reset colony and sites |
| 's' | Take screenshot |
| 'd' | Toggle debug mode |
| 'Space' | Pause/Resume simulation |

## Fitness Landscape

The algorithm optimizes over a multi-peak landscape created with Gaussian distributions:
- Peak 1: (150, 150) - value 0.8
- Peak 2: (width-150, 150) - value 0.9
- Peak 3: (150, height-150) - value 0.85
- Peak 4: (width-150, height-150) - value 0.95
- Peak 5: (width/2, height/2) - value 0.7

This tests the colony's ability to discover and track multiple optima.

## Key Features

1. **Emergent Behavior**: Simple individual rules produce collective intelligence
2. **Self-Organization**: No central control; global order emerges
3. **Adaptive Search**: Dynamically balances exploration vs. exploitation
4. **Multi-Peak Optimization**: Handles complex fitness landscapes
5. **Information Sharing**: Waggle dance mechanism for knowledge transfer

## Algorithm Complexity

- **Time Complexity**: O(n) per frame, where n = number of bees
- **Space Complexity**: O(n + m), where n = bees, m = food sites
- **Convergence**: Stochastic; typically converges in 500-2000 frames

## References

- Karaboga, D., & Basturk, B. (2007). "A powerful and efficient algorithm for numerical function optimization: artificial bee colony (ABC) algorithm"
- Prince, C., & Abrams, E. (2013). "When is a bee just a bee? Categorization and individual recognition in the honey bee brain"

## Usage

```python
from logic_lab.swarm_intelligence.bee_foraging import BeeColony

colony = BeeColony(num_bees=30, trial_limit=100)

# Simulate
for _ in range(1000):
    colony.update()
    colony.render()
```

Or run the interactive simulation:
```bash
python -m logic_lab.swarm_intelligence.bee_foraging.bee_foraging
```
