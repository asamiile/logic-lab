"""
Visualize MAP-Elites best controller.
Shows video playback of best performing controller across all behavioral descriptors.
"""

import argparse
import os
import pickle
import sys

import gymnasium
import numpy as np

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(os.path.dirname(CURR_DIR))
LOGIC_LAB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURR_DIR))))
ROOT_DIR = PROJ_DIR

LIB_DIR = os.path.join(LOGIC_LAB_ROOT, "shared", "libs")
sys.path.append(LIB_DIR)
import me_neat

ENV_DIR = os.path.join(PROJ_DIR, "environment", "gym_mujoco")
sys.path.append(ENV_DIR)

from gymnasium.wrappers import RecordVideo


def get_args():
    parser = argparse.ArgumentParser(description="Visualize MAP-Elites best controller")
    parser.add_argument(
        "-e",
        "--experiment",
        type=str,
        required=True,
        help="experiment name to load from out directory",
    )
    parser.add_argument(
        "-t",
        "--task",
        type=str,
        default="Walker2d-v5",
        choices=["Walker2d-v5", "HalfCheetah-v5", "Hopper-v5", "Ant-v5", "BipedalWalker-v3"],
        help="gymnasium environment ID",
    )
    parser.add_argument(
        "--episodes", type=int, default=3, help="number of episodes to record (default: 3)"
    )
    parser.add_argument(
        "--steps", type=int, default=1000, help="max steps per episode (default: 1000)"
    )
    parser.add_argument(
        "--render-mode",
        type=str,
        default="rgb_array",
        choices=["rgb_array", "human"],
        help="render mode (rgb_array for video, human for display)",
    )
    return parser.parse_args()


def load_best_genome(experiment_dir):
    """Load the best genome from MAP-Elites population."""
    pop_file = os.path.join(experiment_dir, "genome")

    if not os.path.isdir(pop_file):
        raise RuntimeError(f"No genome directory found in {experiment_dir}")

    # Find all genome files
    genome_files = []
    for file in os.listdir(pop_file):
        if file.endswith(".pickle"):
            genome_files.append(os.path.join(pop_file, file))

    if not genome_files:
        raise RuntimeError(f"No genome files found in {pop_file}")

    # Load all genomes and find the best one by fitness
    best_genome = None
    best_fitness = float("-inf")
    best_file = None

    for genome_file in genome_files:
        with open(genome_file, "rb") as f:
            genome = pickle.load(f)

        if hasattr(genome, "fitness") and genome.fitness is not None:
            if genome.fitness > best_fitness:
                best_fitness = genome.fitness
                best_genome = genome
                best_file = genome_file

    if best_genome is None:
        raise RuntimeError("No valid genomes found in genome directory")

    print(f"Loaded best genome from: {os.path.basename(best_file)}")
    print(f"Fitness: {best_fitness:.2f}")
    return best_genome


def visualize_controller(
    genome, task, episodes=3, max_steps=1000, render_mode="rgb_array", config=None
):
    """Run the controller and record/display video."""

    # Create controller
    controller = me_neat.FeedForwardNetwork.create(genome, config.genome_config)

    # Create environment with video recording
    env = gymnasium.make(task, render_mode=render_mode)

    # Set up video recording
    video_dir = os.path.join(CURR_DIR, "out", "_videos")
    os.makedirs(video_dir, exist_ok=True)

    if render_mode == "rgb_array":
        env = RecordVideo(env, video_dir, episode_trigger=lambda ep: True)

    # Run episodes
    episode_rewards = []

    for episode in range(episodes):
        obs, info = env.reset()
        total_reward = 0.0

        for step in range(max_steps):
            # Get action from controller
            action = np.array(controller.activate(obs)) * 2 - 1
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward

            if terminated or truncated:
                break

        episode_rewards.append(total_reward)
        print(f"Episode {episode+1}/{episodes}: reward = {total_reward:.2f}")

    env.close()

    print(f"\nAverage reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"Videos saved to: {video_dir}")

    return np.mean(episode_rewards)


def load_history(experiment_dir):
    """Load MAP-Elites history."""
    history_file = os.path.join(experiment_dir, "history_fitness.csv")

    if not os.path.isfile(history_file):
        return None

    # Simple CSV reading
    history = {"best_fitness": [], "population_size": []}

    try:
        with open(history_file) as f:
            lines = f.readlines()[1:]  # Skip header
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    try:
                        history["best_fitness"].append(float(parts[0]))
                        history["population_size"].append(int(parts[1]))
                    except:
                        pass
    except:
        pass

    return history if history["best_fitness"] else None


def print_summary(experiment_dir, history):
    """Print summary statistics."""
    print("\n=== MAP-Elites Summary ===\n")

    if history:
        if history["best_fitness"]:
            print(f'Best fitness: {max(history["best_fitness"]):.2f}')
        if history["population_size"]:
            print(f'Final population size (grid filled): {history["population_size"][-1]}')

    # Load population summary
    pop_file = os.path.join(experiment_dir, "history_pop.csv")
    if os.path.isfile(pop_file):
        try:
            with open(pop_file) as f:
                lines = f.readlines()
                print(f"Total genomes in history: {len(lines) - 1}")  # Subtract header
        except:
            pass

    print()


def main():
    args = get_args()

    # Load experiment
    experiment_dir = os.path.join(CURR_DIR, "out", args.experiment)
    if not os.path.isdir(experiment_dir):
        print(f"Error: Experiment directory not found: {experiment_dir}")
        sys.exit(1)

    print(f"Loading experiment: {experiment_dir}\n")

    # Load history
    history = load_history(experiment_dir)

    # Print summary
    print_summary(experiment_dir, history)

    # Load best genome
    genome = load_best_genome(experiment_dir)
    print(f"Genome: {genome.size()} nodes\n")

    # Load config
    config_file = os.path.join(experiment_dir, "locomotion_me_neat.cfg")
    if not os.path.exists(config_file):
        # Try alternative config name
        config_file = os.path.join(experiment_dir, "locomotion_me_neat_generated.cfg")

    if not os.path.exists(config_file):
        print(f"Error: Config file not found in {experiment_dir}")
        sys.exit(1)

    config = me_neat.make_config(config_file)

    # Visualize controller
    print(f"Rendering {args.episodes} episodes on {args.task}...\n")
    visualize_controller(
        genome,
        args.task,
        episodes=args.episodes,
        max_steps=args.steps,
        render_mode=args.render_mode,
        config=config,
    )


if __name__ == "__main__":
    main()
