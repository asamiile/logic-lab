import argparse
import os
import pickle
import sys

import gymnasium

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(os.path.dirname(CURR_DIR))
LOGIC_LAB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURR_DIR))))
ROOT_DIR = PROJ_DIR

LIB_DIR = os.path.join(LOGIC_LAB_ROOT, "shared", "libs")
sys.path.append(LIB_DIR)
import ns_neat

ENV_DIR = os.path.join(PROJ_DIR, "environment", "gym_mujoco")
sys.path.append(ENV_DIR)
from gymnasium.wrappers import RecordVideo
from make_env import make_gymnasium_env


def get_args():
    parser = argparse.ArgumentParser(description="Visualize NS-NEAT controller")
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
    """Load the best genome from experiment output."""
    genome_dir = os.path.join(experiment_dir, "genome")

    if not os.path.isdir(genome_dir):
        raise RuntimeError(f"No genome directory found in {experiment_dir}")

    # Get all genome files and sort by generation
    genome_files = [f for f in os.listdir(genome_dir) if f.endswith(".pickle")]
    if not genome_files:
        raise RuntimeError(f"No genome files found in {genome_dir}")

    # Load the last (best) genome by ID number
    genome_ids = sorted([int(f[:-7]) for f in genome_files])
    best_genome_id = genome_ids[-1]
    best_genome_file = os.path.join(genome_dir, f"{best_genome_id}.pickle")

    with open(best_genome_file, "rb") as f:
        genome = pickle.load(f)

    print(f"Loaded best genome: ID {best_genome_id}")
    return genome


def visualize_controller(genome, task, episodes=3, max_steps=1000, render_mode="rgb_array"):
    """Run the controller and record/display video."""
    import numpy as np

    # Load configuration
    config_file = os.path.join(CURR_DIR, "config", "locomotion_ns_neat.cfg")
    with open(config_file) as f:
        config_content = f.read()

    # Create environment and get dimensions
    test_env = make_gymnasium_env(task)
    obs_dim = test_env.observation_space.shape[0]
    act_dim = test_env.action_space.shape[0]
    test_env.close()

    # Update config with actual dimensions
    config_content = config_content.replace(
        "num_inputs              = 1", f"num_inputs              = {obs_dim}"
    )
    config_content = config_content.replace(
        "num_outputs             = 1", f"num_outputs             = {act_dim}"
    )

    temp_config_file = os.path.join(CURR_DIR, "config", "locomotion_ns_neat_draw.cfg")
    with open(temp_config_file, "w") as f:
        f.write(config_content)

    custom_config = [
        ("NS-NEAT", "metric", "euclidean"),
        ("NS-NEAT", "threshold_init", 10.0),
        ("NS-NEAT", "threshold_floor", 1.0),
        ("NS-NEAT", "neighbors", 15),
        ("NS-NEAT", "mcns", 0.01),
    ]
    config = ns_neat.make_config(temp_config_file, custom_config=custom_config)

    # Create controller
    controller = ns_neat.FeedForwardNetwork.create(genome, config.genome_config)

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

    # Clean up temp config
    if os.path.exists(temp_config_file):
        os.remove(temp_config_file)

    print(f"\nAverage reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"Videos saved to: {video_dir}")

    return np.mean(episode_rewards)


def main():

    args = get_args()

    # Load experiment
    experiment_dir = os.path.join(CURR_DIR, "out", args.experiment)
    if not os.path.isdir(experiment_dir):
        print(f"Error: Experiment directory not found: {experiment_dir}")
        sys.exit(1)

    print(f"Loading experiment: {experiment_dir}")

    # Load best genome
    genome = load_best_genome(experiment_dir)
    print(f"Genome: {genome.size()} nodes, fitness = {genome.fitness:.2f}\n")

    # Visualize
    print(f"Rendering {args.episodes} episodes on {args.task}...\n")
    visualize_controller(
        genome,
        args.task,
        episodes=args.episodes,
        max_steps=args.steps,
        render_mode=args.render_mode,
    )


if __name__ == "__main__":
    main()
