import argparse


def get_args():
    parser = argparse.ArgumentParser(description="NEAT controller for locomotion tasks")

    parser.add_argument(
        "-n", "--name", type=str, default="locomotion_neat_run", help="experiment name"
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
        "-p", "--pop-size", type=int, default=100, help="NEAT population size (default: 100)"
    )
    parser.add_argument(
        "-g",
        "--generation",
        type=int,
        default=50,
        help="number of generations to run (default: 50)",
    )
    parser.add_argument(
        "-c", "--num-cores", type=int, default=4, help="number of parallel cores (default: 4)"
    )

    return parser.parse_args()
