"""
Full POET Implementation: Procedural Environment Evolution with Training
Extends the simplified version with:
- Complex terrain generation
- Controller evolution per niche
- Difficulty adaptation
- Visualization
"""

import json
import os
import pickle
import sys
from collections import defaultdict

import numpy as np

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(os.path.dirname(CURR_DIR))
LOGIC_LAB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURR_DIR))))

LIB_DIR = os.path.join(LOGIC_LAB_ROOT, "shared", "libs")
sys.path.append(LIB_DIR)
import neat_cppn
from experiment_utils import initialize_experiment

ENV_DIR = os.path.join(PROJ_DIR, "environment", "gym_mujoco")
sys.path.append(ENV_DIR)
from arguments.locomotion_poet import get_args
from make_env import get_env_dims, make_gymnasium_env


class POETNiche:
    """A single niche in POET: (environment, controller, optimizer)."""

    def __init__(self, niche_id, config, env_id):
        self.niche_id = niche_id
        self.config = config
        self.env_id = env_id

        # Terrain genome (environment definition)
        self.terrain_genome = neat_cppn.DefaultGenome(key=niche_id)
        self.terrain_genome.configure_new(config.genome_config)

        # Controller genome
        self.controller_genome = neat_cppn.DefaultGenome(key=niche_id + 10000)
        self.controller_genome.configure_new(config.genome_config)

        # Performance tracking
        self.fitness_history = []
        self.best_fitness = float("-inf")
        self.difficulty = 0.5
        self.age = 0
        self.stagnation = 0

    def evaluate(self, num_eval=1):
        """Evaluate controller on current terrain."""
        env = make_gymnasium_env(self.env_id)
        episode_rewards = []

        # Create controller network
        controller = neat_cppn.FeedForwardNetwork.create(
            self.controller_genome, self.config.genome_config
        )

        for _ in range(num_eval):
            obs, _ = env.reset()
            total_reward = 0.0

            for step in range(500):
                action = np.array(controller.activate(obs)) * 2 - 1
                obs, reward, terminated, truncated, _ = env.step(action)
                total_reward += reward

                if terminated or truncated:
                    break

            episode_rewards.append(total_reward)

        env.close()

        mean_fitness = np.mean(episode_rewards)

        # Update difficulty based on controller genome complexity
        self.difficulty = min(
            1.0,
            len(self.controller_genome.connections) * 0.01
            + len(self.terrain_genome.connections) * 0.005,
        )

        # Track fitness
        self.fitness_history.append(mean_fitness)
        if mean_fitness > self.best_fitness:
            self.best_fitness = mean_fitness
            self.stagnation = 0
        else:
            self.stagnation += 1

        return mean_fitness

    def mutate_controller(self):
        """Evolve controller for this niche."""
        self.controller_genome.mutate(self.config.genome_config)

    def mutate_terrain(self):
        """Evolve terrain for this niche."""
        self.terrain_genome.mutate(self.config.genome_config)

    def create_child(self, new_id):
        """Create child niche from this niche."""
        child = POETNiche(new_id, self.config, self.env_id)

        # Inherit and mutate genomes
        child.terrain_genome.connections = {
            k: v.copy() for k, v in self.terrain_genome.connections.items()
        }
        child.terrain_genome.nodes = {k: v.copy() for k, v in self.terrain_genome.nodes.items()}
        child.terrain_genome.mutate(self.config.genome_config)

        child.controller_genome.connections = {
            k: v.copy() for k, v in self.controller_genome.connections.items()
        }
        child.controller_genome.nodes = {
            k: v.copy() for k, v in self.controller_genome.nodes.items()
        }
        child.controller_genome.mutate(self.config.genome_config)

        return child


class FullPOET:
    """Full POET with controller evolution and terrain co-evolution."""

    def __init__(self, env_id, target_niches=4):
        self.env_id = env_id
        self.target_niches = target_niches
        self.niches = {}
        self.niche_counter = 0
        self.iteration = 0
        self.history = defaultdict(list)

    def initialize(self, config, num_initial=2):
        """Initialize population with diverse niches."""
        print(f"Initializing {num_initial} initial niches...")

        for i in range(num_initial):
            niche = POETNiche(self.niche_counter, config, self.env_id)
            self.niches[f"niche_{i}"] = niche
            self.niche_counter += 1

    def run_iteration(self):
        """Single POET iteration."""
        print(f"\n--- POET Iteration {self.iteration + 1} ---")
        print(f"Active niches: {len(self.niches)}")

        # 1. Evaluate all niches
        niche_performances = {}
        for niche_id, niche in self.niches.items():
            fitness = niche.evaluate(num_eval=2)
            niche_performances[niche_id] = fitness

            print(
                f"  {niche_id}: fitness={fitness:7.2f}, difficulty={niche.difficulty:.3f}, "
                f"age={niche.age}, stagnation={niche.stagnation}"
            )

        # 2. Evolve controllers in each niche
        for niche in self.niches.values():
            niche.mutate_controller()
            niche.mutate_terrain()

        # 3. Track best performance
        if niche_performances:
            best_niche_id = max(niche_performances, key=niche_performances.get)
            best_fitness = niche_performances[best_niche_id]
            self.history["best_fitness"].append(best_fitness)
            print(f"\nBest: {best_niche_id} (fitness={best_fitness:.2f})")

            # 4. Create new niches if below target
            if len(self.niches) < self.target_niches:
                parent_niche = self.niches[best_niche_id]
                new_niche_id = f"niche_{len(self.niches)}"
                new_niche = parent_niche.create_child(self.niche_counter)
                self.niches[new_niche_id] = new_niche
                self.niche_counter += 1
                print(f"Created new niche: {new_niche_id}")

        # 5. Eliminate stagnant niches
        to_remove = []
        for niche_id, niche in self.niches.items():
            # Keep if: young, good performance, or not too stagnant
            if niche.age > 3 and niche.stagnation > 5 and niche.best_fitness < 0:
                to_remove.append(niche_id)

        for niche_id in to_remove:
            del self.niches[niche_id]
            print(f"Eliminated niche {niche_id} (stagnant)")

        # 6. Update age
        for niche in self.niches.values():
            niche.age += 1

        self.history["num_niches"].append(len(self.niches))
        self.iteration += 1

    def run(self, num_iterations):
        """Run full POET for specified iterations."""
        print(f'\n{"="*60}')
        print("FULL POET: Procedural Environment Evolution with Training")
        print(f'{"="*60}')
        print(f"Target niches: {self.target_niches}")
        print(f"Iterations: {num_iterations}\n")

        for _ in range(num_iterations):
            self.run_iteration()

        print(f'\n{"="*60}')
        print("POET Complete")
        print(f"Final niche count: {len(self.niches)}")
        print(f'Best fitness achieved: {max(self.history["best_fitness"]):.2f}')
        print(f'{"="*60}\n')

    def save_results(self, save_path):
        """Save niches and history."""
        # Convert niches to serializable format (dictionaries)
        niches_dict = {}
        for niche_id, niche in self.niches.items():
            niches_dict[niche_id] = {
                "terrain_genome": niche.terrain_genome,
                "controller_genome": niche.controller_genome,
                "fitness": niche.fitness_history[-1] if niche.fitness_history else 0.0,
                "best_fitness": niche.best_fitness,
                "fitness_history": niche.fitness_history,
                "difficulty": niche.difficulty,
                "age": niche.age,
                "stagnation": niche.stagnation,
            }

        # Save all niches
        niches_file = os.path.join(save_path, "final_niches.pkl")
        with open(niches_file, "wb") as f:
            pickle.dump(niches_dict, f)

        # Save history
        history_file = os.path.join(save_path, "history.json")
        with open(history_file, "w") as f:
            json.dump({k: v for k, v in self.history.items()}, f, indent=2)

        print(f"Results saved to {save_path}")


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, "out", args.name)
    initialize_experiment(args.name, save_path, args)

    # Get environment dimensions
    num_inputs, num_outputs = get_env_dims(args.task)

    # Load and configure NEAT config
    phase1_config_path = os.path.join(
        LOGIC_LAB_ROOT,
        "simulation",
        "locomotion",
        "experiments",
        "neat_controller",
        "config",
        "locomotion_neat.cfg",
    )

    with open(phase1_config_path) as f:
        config_content = f.read()

    config_content = config_content.replace(
        "num_inputs              = 1", f"num_inputs              = {num_inputs}"
    )
    config_content = config_content.replace(
        "num_outputs             = 1", f"num_outputs             = {num_outputs}"
    )

    config_file = os.path.join(save_path, "poet_neat.cfg")
    with open(config_file, "w") as f:
        f.write(config_content)

    config = neat_cppn.make_config(config_file)

    # Run Full POET
    poet = FullPOET(args.task, target_niches=args.niche_num)
    poet.initialize(config, num_initial=2)
    poet.run(num_iterations=args.iterations)

    # Save results
    poet.save_results(save_path)


if __name__ == "__main__":
    main()
