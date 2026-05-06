"""
Visualize POET niches and best controllers.
Shows video playback of best performing niche controller.
"""
import os
import sys
import pickle
import json
import argparse
import numpy as np
import gymnasium

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(os.path.dirname(CURR_DIR))
LOGIC_LAB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURR_DIR))))
ROOT_DIR = PROJ_DIR

LIB_DIR = os.path.join(LOGIC_LAB_ROOT, 'shared', 'libs')
sys.path.append(LIB_DIR)
import neat_cppn

ENV_DIR = os.path.join(PROJ_DIR, 'environment', 'gym_mujoco')
sys.path.append(ENV_DIR)
from make_env import make_gymnasium_env, get_env_dims

from gymnasium.wrappers import RecordVideo


def get_args():
    parser = argparse.ArgumentParser(description='Visualize POET niches')
    parser.add_argument(
        '-e', '--experiment',
        type=str, required=True,
        help='experiment name to load from out directory'
    )
    parser.add_argument(
        '-t', '--task',
        type=str, default='Walker2d-v5',
        choices=['Walker2d-v5', 'HalfCheetah-v5', 'Hopper-v5', 'Ant-v5', 'BipedalWalker-v3'],
        help='gymnasium environment ID'
    )
    parser.add_argument(
        '--episodes',
        type=int, default=3,
        help='number of episodes to record (default: 3)'
    )
    parser.add_argument(
        '--steps',
        type=int, default=1000,
        help='max steps per episode (default: 1000)'
    )
    parser.add_argument(
        '--render-mode',
        type=str, default='rgb_array',
        choices=['rgb_array', 'human'],
        help='render mode (rgb_array for video, human for display)'
    )
    parser.add_argument(
        '--niche',
        type=str, default=None,
        help='specific niche ID to visualize (default: best by fitness)'
    )
    return parser.parse_args()


def load_niches(experiment_dir):
    """Load final niches from POET experiment."""
    niches_file = os.path.join(experiment_dir, 'final_niches.pkl')

    if not os.path.isfile(niches_file):
        raise RuntimeError(f'No final_niches.pkl found in {experiment_dir}')

    with open(niches_file, 'rb') as f:
        niches = pickle.load(f)

    return niches


def load_history(experiment_dir):
    """Load POET history from experiment."""
    history_file = os.path.join(experiment_dir, 'history.json')

    if not os.path.isfile(history_file):
        return None

    with open(history_file, 'r') as f:
        history = json.load(f)

    return history


def get_best_niche(niches):
    """Find niche with best fitness."""
    best_niche_id = None
    best_fitness = float('-inf')

    for niche_id, niche in niches.items():
        # Support both 'best_fitness' (full POET) and 'fitness' (simplified POET)
        fitness = niche.get('best_fitness', niche.get('fitness', float('-inf')))
        if fitness > best_fitness:
            best_fitness = fitness
            best_niche_id = niche_id

    return best_niche_id, best_fitness


def visualize_niche(niche, task, episodes=3, max_steps=1000, render_mode='rgb_array', config=None):
    """Run a niche's controller and record/display video."""

    # Get controller genome from niche
    controller_genome = niche['controller_genome']

    # Create controller network
    controller = neat_cppn.FeedForwardNetwork.create(controller_genome, config.genome_config)

    # Create environment with video recording
    env = gymnasium.make(task, render_mode=render_mode)

    # Set up video recording
    video_dir = os.path.join(CURR_DIR, 'out', '_videos')
    os.makedirs(video_dir, exist_ok=True)

    if render_mode == 'rgb_array':
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
        print(f'Episode {episode+1}/{episodes}: reward = {total_reward:.2f}')

    env.close()

    print(f'\nAverage reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}')
    print(f'Videos saved to: {video_dir}')

    return np.mean(episode_rewards)


def print_niche_stats(niches, history=None):
    """Print summary statistics of all niches."""
    print('\n=== POET Niche Summary ===\n')

    for niche_id, niche in sorted(niches.items()):
        terrain_genome = niche['terrain_genome']
        controller_genome = niche['controller_genome']
        # Support both 'best_fitness' (full POET) and 'fitness' (simplified POET)
        fitness = niche.get('best_fitness', niche.get('fitness', 0.0))

        print(f'{niche_id}:')
        print(f'  Fitness: {fitness:.2f}')
        print(f'  Difficulty: {niche.get("difficulty", 0):.3f}')
        print(f'  Age: {niche.get("age", 0)}')
        print(f'  Stagnation: {niche.get("stagnation", 0)}')
        print(f'  Controller: {controller_genome.size()} nodes, '
              f'{len(controller_genome.connections)} connections')
        print(f'  Terrain: {len(terrain_genome.connections)} connections')
        print()

    if history:
        best_fit = history.get("best_fitness")
        if best_fit:
            print(f'Best fitness across all iterations: {max(best_fit):.2f}')
        print(f'Final niche count: {history.get("num_niches", [0])[-1]}')
        print()


def main():
    args = get_args()

    # Load experiment
    experiment_dir = os.path.join(CURR_DIR, 'out', args.experiment)
    if not os.path.isdir(experiment_dir):
        print(f'Error: Experiment directory not found: {experiment_dir}')
        sys.exit(1)

    print(f'Loading experiment: {experiment_dir}\n')

    # Load niches and history
    niches = load_niches(experiment_dir)
    history = load_history(experiment_dir)

    # Print statistics
    print_niche_stats(niches, history)

    # Determine which niche to visualize
    if args.niche:
        niche_id = args.niche
        if niche_id not in niches:
            print(f'Error: Niche {niche_id} not found')
            sys.exit(1)
    else:
        niche_id, best_fitness = get_best_niche(niches)

    niche = niches[niche_id]

    fitness = niche.get('best_fitness', niche.get('fitness', 0.0))

    print(f'Visualizing niche: {niche_id}')
    print(f'Fitness: {fitness:.2f}')
    print(f'Age: {niche.get("age", 0)}')
    print(f'Terrain difficulty: {niche.get("difficulty", 0):.3f}\n')

    # Load config (try both full POET and simplified POET filenames)
    config_file = os.path.join(experiment_dir, 'poet_neat.cfg')
    if not os.path.exists(config_file):
        config_file = os.path.join(experiment_dir, 'terrain_neat.cfg')

    if not os.path.exists(config_file):
        print(f'Error: Config file not found in {experiment_dir}')
        sys.exit(1)

    config = neat_cppn.make_config(config_file)

    # Visualize controller
    print(f'Rendering {args.episodes} episodes on {args.task}...\n')
    visualize_niche(
        niche,
        args.task,
        episodes=args.episodes,
        max_steps=args.steps,
        render_mode=args.render_mode,
        config=config
    )


if __name__ == '__main__':
    main()
