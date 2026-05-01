# Maze Systems

Evolutionary optimization for maze navigation control and maze design.


## Run Commands

### Control - Basic NEAT

```bash
source .venv/Scripts/activate
python simulation/maze_systems/experiments/control/run_maze_neat.py -p 200
python simulation/maze_systems/experiments/control/run_maze_neat.py -t hard
```

### Novelty Search - NEAT with Novelty Search
```bash
python simulation/maze_systems/experiments/novelty_search/run_maze_ns_neat.py -t hard
python simulation/maze_systems/experiments/novelty_search/run_maze_ns_neat.py -t hard -p 300 --timesteps 600 --num-knn 30 -n hard2
```

### Coevolution - Multi-Criteria Coevolution (Maze Design + Control)

```bash
# Bootstrap (only required the first time)
python simulation/maze_systems/experiments/coevolution/bootstrap_maze_mcc.py

# Run MCC (defaults to 1000 generations)
python simulation/maze_systems/experiments/coevolution/run_maze_mcc.py -b default -n <EXPERIMENT_NAME>

# Draw results (run after the experiment completes, generations 0-1)
python simulation/maze_systems/experiments/coevolution/draw_maze_mcc.py <EXPERIMENT_NAME> -sg 0 -eg 1 -cb
```

```bash
# Run for 50 generations
python simulation/maze_systems/experiments/coevolution/run_maze_mcc.py -b default -n coevo_experiment_1 -g 50

# Draw results (run after the experiment completes, generations 0-1)
python simulation/maze_systems/experiments/coevolution/draw_maze_mcc.py coevo_experiment_1 -sg 0 -eg 1 -cb
```

## File Structure

- `environment/` - Maze environment and evaluator
- `experiments/control/` - NEAT-based maze navigation control
- `experiments/novelty_search/` - Novelty Search + NEAT for maze control
- `experiments/coevolution/` - Multi-Criteria Coevolution for maze design and control
