# Locomotion Systems

Evolutionary optimization for locomotion controller and morphology design using gymnasium + MuJoCo/Box2D.

## Phase 1: NEAT Controller - Basic Neuroevolution

```bash
uv run python simulation/locomotion/experiments/neat_controller/run_locomotion_neat.py -n <EXPERIMENT_NAME> -t BipedalWalker-v3 -p 100 -g 50 -c 4
```

**Parameters:**
- `-n, --name`: Experiment identifier
- `-t, --task`: Environment (Walker2d-v5, HalfCheetah-v5, Hopper-v5, Ant-v5, BipedalWalker-v3)
- `-p, --pop-size`: NEAT population size
- `-g, --generation`: Number of generations
- `-c, --num-cores`: Number of parallel evaluation cores

**Test Example:**
```bash
uv run python simulation/locomotion/experiments/neat_controller/run_locomotion_neat.py -n test_quick -t BipedalWalker-v3 -p 50 -g 10 -c 2
```

**Visualization:**

```bash
# Preview (display in window)
uv run python simulation/locomotion/experiments/neat_controller/draw_locomotion_neat.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3 --render-mode human

# Save video
uv run python simulation/locomotion/experiments/neat_controller/draw_locomotion_neat.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3
```

## Phase 2: NS-NEAT - Novelty Search Controller

```bash
uv run python simulation/locomotion/experiments/ns_neat_controller/run_locomotion_ns_neat.py -n <EXPERIMENT_NAME> -t BipedalWalker-v3 -p 100 -g 50 -c 4
```

**Additional Parameters:**
- `--ns-threshold`: Initial novelty archive threshold (default: 10.0)
- `--num-knn`: k-NN for novelty calculation (default: 15)
- `--mcns`: Minimum criterion novelty score (default: 0.01)

**Test Example:**
```bash
uv run python simulation/locomotion/experiments/ns_neat_controller/run_locomotion_ns_neat.py -n test_ns_quick -t BipedalWalker-v3 -p 50 -g 10 -c 2
```

**Visualization:**

```bash
# Preview (display in window)
uv run python simulation/locomotion/experiments/ns_neat_controller/draw_locomotion_ns_neat.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3 --render-mode human

# Save video
uv run python simulation/locomotion/experiments/ns_neat_controller/draw_locomotion_ns_neat.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3
```

## Phase 3: MAP-Elites + CPPN - Morphology Evolution

```bash
uv run python simulation/locomotion/experiments/me_neat_controller/run_locomotion_me_neat.py -n <EXPERIMENT_NAME> -t BipedalWalker-v3 -b 50 -g 20 -c 4
```

**Parameters:**
- `-n, --name`: Experiment identifier
- `-t, --task`: Environment (Walker2d-v5, HalfCheetah-v5, Hopper-v5, Ant-v5, BipedalWalker-v3)
- `-b, --batch-size`: Offspring size (default: 50)
- `-g, --generation`: Number of generations (default: 20)
- `--bd-1`: First behavioral descriptor (default: forward_speed)
- `--bd-2`: Second behavioral descriptor (default: joint_activity)
- `-c, --num-cores`: Number of parallel evaluation cores

**Test Example:**
```bash
uv run python simulation/locomotion/experiments/me_neat_controller/run_locomotion_me_neat.py -n test_map_elites -t BipedalWalker-v3 -b 20 -g 5 -c 2
```

**Visualization:**

```bash
# Preview (display in window)
uv run python simulation/locomotion/experiments/me_neat_controller/draw_locomotion_me_neat.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3 --render-mode human

# Save video
uv run python simulation/locomotion/experiments/me_neat_controller/draw_locomotion_me_neat.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3
```

## Phase 4: POET - Terrain Co-evolution

```bash
uv run python simulation/locomotion/experiments/poet_terrain/run_locomotion_poet.py -n <EXPERIMENT_NAME> -t BipedalWalker-v3 -i 10 --niche-num 4 -c 2
```

**Parameters:**
- `-n, --name`: Experiment identifier
- `-t, --task`: Environment (Walker2d-v5, HalfCheetah-v5, Hopper-v5, Ant-v5, BipedalWalker-v3)
- `-i, --iterations`: Number of POET iterations (default: 10)
- `--niche-num`: Target number of concurrent niches (default: 4)
- `-c, --num-cores`: Number of parallel evaluation cores

**Test Example:**
```bash
uv run python simulation/locomotion/experiments/poet_terrain/run_locomotion_poet.py \
  -n test_poet -t BipedalWalker-v3 -i 5 --niche-num 2 -c 1
```

**Visualization:**

```bash
# Preview (display in window)
uv run python simulation/locomotion/experiments/poet_terrain/draw_locomotion_poet.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3 --render-mode human

# Save video
uv run python simulation/locomotion/experiments/poet_terrain/draw_locomotion_poet.py \
  -e <EXPERIMENT_NAME> -t BipedalWalker-v3 --episodes 3
```

## File Structure

- `environment/gym_mujoco/` - Gymnasium + MuJoCo environment adapter
  - `make_env.py` - Environment creation and dimension retrieval
  - `evaluator.py` - Controller evaluation classes
  - `structural_bd.py` - Behavioral descriptors (Phase 3)
- `experiments/neat_controller/` - Phase 1: NEAT experiments
- `experiments/ns_neat_controller/` - Phase 2: NS-NEAT experiments
- `experiments/me_neat_controller/` - Phase 3: MAP-Elites experiments
- `experiments/poet_terrain/` - Phase 4: POET experiments

## Available Environments

All algorithms support the following environments. Specify the environment using the `-t` argument:

| Environment | Physics Engine | obs/act | Characteristics |
|---|---|---|---|
| `Walker2d-v5` | MuJoCo (3D) | 17/6 | Bipedal walking (default) |
| `HalfCheetah-v5` | MuJoCo (3D) | 17/6 | Quadrupedal running |
| `Hopper-v5` | MuJoCo (3D) | 11/3 | Single-leg hopping (simplest) |
| `Ant-v5` | MuJoCo (3D) | 27/8 | Quadrupedal (most complex) |
| **`BipedalWalker-v3`** | **Box2D (2D)** | **24/4** | **Bipedal walking (closest to evogym)** |
