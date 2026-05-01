# Logic Lab

Python translations of "The Nature of Code" examples using py5. Each simulation is organized by domain, demonstrating core computational creativity concepts: physics, steering behaviors, genetic algorithms, neural networks, and fractals.

## Setup

Install dependencies:

```bash
uv sync
```

## Domain Simulations

Browse by topic to find what interests you:

### 🎯 [Physics](physics/)
Basic physics, forces, motion, randomness, waves, particle systems, and physics engines
- Random walks, distributions, rotation, forces, waves, particle systems, Matter.js simulations
- **Run:** `uv run python physics/motion_101_velocity/motion_101_velocity.py`

### 🧭 [Steering Behaviors](steering_behaviors/)
Navigation, sensors, and movement decisions
- Gesture recognition, creature sensors, steering, ecosystem
- **Run:** `uv run python steering_behaviors/gesture_classifier/gesture_classifier.py`

### 🧬 [Genetic Algorithms](genetic_algorithms/)
Evolution through natural selection
- GA Shakespeare, smart rockets, interactive selection, evolving creatures
- **Run:** `uv run python genetic_algorithms/ga_shakespeare/ga_shakespeare.py`

### 🤖 [Neuro-Evolution](neuro_evolution/)
Neural networks evolved with genetic algorithms
- Flappy bird AI, smart rockets with learned navigation
- **Run:** `uv run python neuro_evolution/flappy_bird_neuro_evolution/flappy_bird_neuro_evolution.py`

### 🌳 [Fractals](fractals/)
Recursive patterns and fractal geometry
- Koch snowflake, recursive trees, L-systems, quadtrees
- **Run:** `uv run python fractals/koch_snowflake/koch_snowflake.py`

### 🧪 [Research](research/)
Experimental implementations, parameter studies, and hybrid approaches
- Custom experiments and prototypes

### 🔧 [Algorithms](algorithms/)
Reusable algorithm implementations
- Genetic algorithm base classes, neural network utilities

### 📦 [Simulation](simulation/)
Additional experiments and custom implementations
- Varied sketches, infrastructure tests, and prototypes (118+ simulations)

## Quick Start

Each domain has a README with detailed instructions and descriptions. Start with any simulation that interests you:

```bash
# Run any simulation:
uv run python {domain}/{simulation_name}/{simulation_name}.py

# Example:
uv run python physics/random_walk/random_walk.py
```

### Common Controls
- **Click**: Interact with simulation
- **Mouse Move**: Control elements
- **UP/DOWN arrows**: Adjust speed (some simulations)
- **S Key**: Save screenshot
- **ESC**: Exit (some simulations)

## Learning Path

For beginners, we recommend this progression:

1. **Physics** → Understand motion, vectors, and forces
2. **Steering Behaviors** → Learn sensors and decision making
3. **Genetic Algorithms** → Explore evolution and optimization
4. **Neuro-Evolution** → Combine learning with evolution
5. **Fractals** → Study recursive beauty and recursion

Each domain builds on previous concepts.

## Organization

```
logic-lab/
├── physics/                  # Forces, motion, randomness
├── steering_behaviors/       # Navigation, sensors, AI
├── genetic_algorithms/       # Evolution and selection
├── neuro_evolution/          # Neural networks + evolution
├── fractals/                 # Recursive patterns
├── algorithms/               # Reusable components
├── research/                 # Experimental work
└── simulation/               # Additional sketches (118+)
```

## Reference

- [The Nature of Code](https://natureofcode.com/) - Daniel Shiffman
- [py5 Documentation](https://py5coding.org/) - Python port of Processing
- [Processing](https://processing.org/) - Original creative coding environment

## License

Educational implementations for learning computational creativity.

## Author

[Asami.K](https://asami.tokyo/)

If you find this helpful, consider supporting the work:

<a href="https://www.buymeacoffee.com/asamiinae" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
