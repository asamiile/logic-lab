# Phase 2: NS-NEAT Controller Evolution

Novelty Search + NEAT for locomotion controller evolution on gymnasium + MuJoCo.

## Running

### NS-NEAT Controller - Novelty Search + NEAT

```bash
python simulation/locomotion/experiments/ns_neat_controller/run_locomotion_ns_neat.py -n <EXPERIMENT_NAME> -t Walker2d-v5 -p 100 -g 50 -c 4
```

**Parameters:**
- `-n, --name`: Experiment identifier
- `-t, --task`: Environment (Walker2d-v5, HalfCheetah-v5, Hopper-v5, Ant-v5)
- `-p, --pop-size`: NS-NEAT population size
- `-g, --generation`: Number of generations
- `-c, --num-cores`: Number of cores for parallel evaluation
- `--ns-threshold`: Initial novelty archive threshold (default: 10.0)
- `--num-knn`: k-NN for novelty calculation (default: 15)
- `--mcns`: Minimum criteria novelty score (default: 0.01)

**Example test run:**
```bash
python run_locomotion_ns_neat.py -n test_ns_quick -t Walker2d-v5 -p 50 -g 5 -c 1
```

## File Structure

- `config/` - NS-NEAT configuration files
  - `locomotion_ns_neat.cfg` - Template for dynamic generation based on environment
- `arguments/` - Command-line argument parser
  - `locomotion_ns_neat.py` - Argument definitions
- `run_locomotion_ns_neat.py` - Main execution script

## Behavioral Descriptor

The behavioral characteristics of each controller are extracted from the observation and action trajectories during episodes.

- **Calculation**: Upper triangular elements of covariance matrix of observations and actions
- **Dimensionality**: `obs_dim*(obs_dim+1)/2 + act_dim*(act_dim+1)/2`
  - Walker2d: 17 + 6 = 23 → BD dimension = 17*18/2 + 6*7/2 = 153 + 21 = 174
- **Distance Metric**: Euclidean distance for novelty calculation

## Algorithm Overview

Unlike traditional fitness-based evolution, NS-NEAT directly optimizes novelty (behavioral diversity):

1. Evaluate each individual and extract its behavioral descriptor
2. Convert descriptor diversity (distance to others) into a novelty score
3. Selectively archive individuals with high novelty scores
4. As archive size increases, problem difficulty gradually increases

This allows controllers with diverse behavioral patterns to coexist and evolve together.
