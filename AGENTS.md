# Agent Instructions for Logic Lab

## Commit Policy

**Do NOT commit changes to git.**

The user will handle all git commits manually. After implementing features or fixes:
- Write/edit code files as needed
- Create new directories and files
- Run syntax checks and basic tests
- But DO NOT run `git add` or `git commit`

Instead, leave the working directory in a state ready for the user to commit. The user will review changes and commit when appropriate.

## Implementation Preferences

- Implement features directly without asking for confirmation on straightforward tasks
- For multi-step or architectural decisions, use EnterPlanMode to get user alignment first
- Run syntax verification on Python files to catch errors early
- Test code when possible before completing the task
- Use concise communication - state what was done and what's next

## Project Context

This project translates JavaScript examples from "The Nature of Code" (noc-book-2) into Python using py5:

- Each simulation gets its own directory organized by **domain/topic**
- Standard structure: `{name}.py` (main file), `README.md` (instructions), `/screenshots/` (for outputs)
- Target: Full translation of Chapter 2, 5, 6, 8, and 9 examples

### Current Organization Status

✅ **Implemented Domains:**
- `physics/` - 12 simulations (randomness, distributions, forces, rotation)
- `steering_behaviors/` - 5 simulations (perceptron, gesture, creature sensors, steering, ecosystem)
- `genetic_algorithms/` - 6 simulations (GA Shakespeare, smart rockets, interactive selection, evolving bloops)
- `neuro_evolution/` - 3 simulations (flappy bird, smart rockets NE)
- `fractals/` - 10 simulations (Koch curve, trees, recursive patterns, quadtree)
- `simulation/` - 118 experimental simulations (varied experiments, infrastructure tests, prototypes)

📋 **Ready for Use:**
- `algorithms/` - For reusable algorithm implementations (GA base, NN base, utilities)
- `neural_networks/` - For fixed neural network implementations
- `research/` - For experimental hybrid approaches and parameter studies

🔮 **Future:**
- `neat_python/` - Will contain NEAT algorithm implementations when added

## Directory Classification Policy

**Classification Principle:** Domain-Based Organization
- ✅ **Intuitive**: Group by "what does the program do" rather than how it's implemented
- ✅ **Scalable**: Easy to add neat-python, reinforcement learning, and other algorithms
- ✅ **Collaborative**: Anyone can immediately understand where things belong
- ✅ **Modular**: Related simulations naturally cluster together

### Domain Categories

| Domain | Purpose | Examples | Status |
|--------|---------|----------|--------|
| `physics/` | Basic physics, forces, motion, randomness | Random walk, forces, rotation | ✅ Created |
| `steering_behaviors/` | Navigation, sensors, movement decisions | Gesture classifier, creature sensors, steering seek | ✅ Created |
| `genetic_algorithms/` | Evolution via genetic algorithms | GA Shakespeare, smart rockets, interactive selection | ✅ Created |
| `neural_networks/` | Neural networks (inference/fixed) | Perceptron, gesture classifier | 📋 Ready |
| `neuro_evolution/` | NN + GA combined | Flappy bird AI, smart rockets NE, ecosystem | ✅ Created |
| `fractals/` | Recursive patterns, fractal geometry | Koch snowflake, recursive trees | ✅ Created |
| `neat_python/` | NEAT algorithm (future) | NEAT XOR, NEAT games, NEAT ecosystem | 🔮 Future |
| `algorithms/` | Reusable algorithm utilities | GA base, NN base, helper functions | 📋 Ready |
| `research/` | Custom experiments & hybrid approaches | Parameter studies, novel combinations | 📋 Ready |
| `simulation/` | Experiments & custom implementations (non-NOC) | Varied experiments not from translations | ✅ Active |

### When Adding New Simulations

1. **Determine the primary domain** - What is the simulation fundamentally about?
   - Is it primarily about physics? → `physics/`
   - Is it about learning to move/navigate? → `steering_behaviors/`
   - Is it about evolving DNA/genes? → `genetic_algorithms/`
   - Does it combine NN + GA? → `neuro_evolution/`

2. **Create directory** - Use clear, descriptive names with underscores:
   - `domain_name/simulation_name/` (e.g., `physics/random_walk/`)

3. **Follow standard structure**:
   ```
   simulation_name/
   ├── simulation_name.py          # Main executable
   ├── README.md                   # Instructions & overview
   └── screenshots/                # Output directory
   ```

4. **Update domain README** - Add entry to `domain/README.md` with run instructions

### Code Reuse

Extract reusable components to `algorithms/`:
- Generic genetic algorithm base class → `algorithms/genetic_algorithm.py`
- Neural network utilities → `algorithms/neural_network.py`
- Common patterns → `algorithms/common.py`

This keeps simulations clean and prevents duplication.
