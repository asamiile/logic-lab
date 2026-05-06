import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description="NS-NEAT controller for locomotion tasks with novelty search"
    )

    parser.add_argument(
        "-n", "--name", type=str, default="locomotion_ns_neat_run", help="experiment name"
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
        "-p", "--pop-size", type=int, default=100, help="NS-NEAT population size (default: 100)"
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
    parser.add_argument(
        "--ns-threshold",
        type=float,
        default=10.0,
        help="initial novelty archive threshold (default: 10.0)",
    )
    parser.add_argument(
        "--num-knn",
        type=int,
        default=15,
        help="k-nearest neighbors for novelty computation (default: 15)",
    )
    parser.add_argument(
        "--mcns",
        type=float,
        default=0.01,
        help="minimum criterion novelty search score (default: 0.01)",
    )

    return parser.parse_args()
