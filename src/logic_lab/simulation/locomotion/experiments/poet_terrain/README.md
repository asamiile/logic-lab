# POET: Procedural Environment Evolution with Training

POET co-evolves both environments (terrains) and controllers (neural network agents) simultaneously.

## Setup

Make sure dependencies are installed:
```bash
cd /path/to/logic-lab
uv sync
```

## Quick Start

Co-evolves terrain genomes and controller genomes simultaneously. Controllers adapt to their niches' terrain.

```bash
python simulation/locomotion/experiments/poet_terrain/run_locomotion_poet.py \
  -n my_poet_experiment \
  -t BipedalWalker-v3 \
  -i 10 \
  --niche-num 4 \
  -c 2
```

**Arguments:**
- `-n, --name`: Experiment name (default: `locomotion_poet_run`)
- `-t, --task`: Gym environment (default: `HalfCheetah-v5`)
  - Choices: `Walker2d-v5`, `HalfCheetah-v5`, `Hopper-v5`, `Ant-v5`, `BipedalWalker-v3`
- `-i, --iterations`: Number of POET iterations (default: 10)
- `--niche-num`: Target number of concurrent niches (default: 4)
- `-c, --num-cores`: Parallel evaluation cores (default: 2)

## Visualization

Visualize the best niche controller from a completed experiment:

```bash
python simulation/locomotion/experiments/poet_terrain/draw_locomotion_poet.py \
  -e my_poet_experiment \
  -t BipedalWalker-v3 \
  --episodes 3 \
  --steps 1000
```

**Arguments:**
- `-e, --experiment`: Experiment name (required)
- `-t, --task`: Environment ID (must match original experiment)
- `--episodes`: Number of episodes to record (default: 3)
- `--steps`: Max steps per episode (default: 1000)
- `--render-mode`: `rgb_array` (video file) or `human` (display) (default: `rgb_array`)
- `--niche`: Specific niche ID to visualize (default: best by fitness)

Videos are saved to `out/_videos/`.


## Understanding Output

### Experiment Directory Structure
```
out/my_experiment/
├── arguments.json           # Command-line arguments
├── final_niches.pkl        # Serialized niche genomes
├── history.json            # Fitness and niche count history
└── poet_neat.cfg           # NEAT config
```

### Console Output

Each iteration shows:
```
--- POET Iteration 3 ---
Active niches: 3
  niche_0: fitness=42.15, difficulty=0.523, age=2, stagnation=1
  niche_1: fitness=38.92, difficulty=0.712, age=1, stagnation=0
  niche_2: fitness=-5.41, difficulty=0.089, age=0, stagnation=0

Best: niche_0 (fitness=42.15)
Created new niche: niche_3
```

**Metrics:**
- **fitness**: Current episode reward (higher is better)
- **difficulty**: Terrain complexity (0-1 scale)
- **age**: Number of iterations niche has existed
- **stagnation**: Consecutive iterations without fitness improvement

## Algorithm Details

1. **Initialize**: Create niches with random terrain + controller genomes
2. **Evaluate**: Run controller on terrain, record fitness
3. **Evolve**: Mutate both terrain and controller genomes
4. **Track**: Update difficulty, age, and stagnation counters
5. **Reproduce**: Create children of best niche
6. **Eliminate**: Remove old, stagnant niches
7. **Repeat**: Run for specified iterations

Difficulty = weighted combination of terrain and controller complexity

## Troubleshooting

### "Expected N inputs, got M" error
The NEAT config dimensions mismatch the environment. Ensure the environment ID matches between runs and visualization.

### Low fitness values
This is normal for initial evolution. NEAT controllers need many generations to develop behavior. Try:
- Increasing iterations (`-i 50`)
- Using larger populations in config file
- Reducing niche diversity pressure (modify difficulty threshold)

### Videos not saving
Ensure `moviepy` and `imageio-ffmpeg` are installed:
```bash
uv add moviepy imageio-ffmpeg
```

## References

Original POET paper: "Emergent Tool Use From Multi-Agent Autocurricula" (Wang et al., 2019)

Implementation based on:
- OpenEndedCodebook: https://github.com/uber-research/evolving-simple-organisms
- NEAT-Python: https://github.com/CodeReclaimers/neat-python
