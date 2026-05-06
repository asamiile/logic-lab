import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description="MAP-Elites controller for locomotion with behavior diversity"
    )

    parser.add_argument(
        "-n", "--name", type=str, default="locomotion_me_neat_run", help="experiment name"
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
        "-p", "--pop-size", type=int, default=100, help="MAP-Elites population size (default: 100)"
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=50,
        help="offspring batch size per generation (default: 50)",
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
        "--bd-1",
        type=str,
        default="forward_speed",
        choices=[
            "forward_speed",
            "lateral_stability",
            "body_tilt",
            "joint_activity",
            "step_frequency",
        ],
        help="first behavioral descriptor axis (default: forward_speed)",
    )
    parser.add_argument(
        "--bd-2",
        type=str,
        default="joint_activity",
        choices=[
            "forward_speed",
            "lateral_stability",
            "body_tilt",
            "joint_activity",
            "step_frequency",
        ],
        help="second behavioral descriptor axis (default: joint_activity)",
    )
    parser.add_argument("--no-plot", action="store_true", help="disable matplotlib plotting")

    return parser.parse_args()
