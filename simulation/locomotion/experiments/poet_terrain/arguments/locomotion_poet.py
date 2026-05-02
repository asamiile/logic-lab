import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='POET: Procedural Environment Evolution with Training'
    )

    parser.add_argument(
        '-n', '--name',
        type=str, default='locomotion_poet_run',
        help='experiment name'
    )
    parser.add_argument(
        '-t', '--task',
        type=str, default='HalfCheetah-v5',
        choices=['Walker2d-v5', 'HalfCheetah-v5', 'Hopper-v5', 'Ant-v5', 'BipedalWalker-v3'],
        help='gymnasium environment ID'
    )
    parser.add_argument(
        '-i', '--iterations',
        type=int, default=10,
        help='number of POET iterations (default: 10)'
    )
    parser.add_argument(
        '--niche-num',
        type=int, default=4,
        help='target number of concurrent niches (default: 4)'
    )
    parser.add_argument(
        '-c', '--num-cores',
        type=int, default=2,
        help='number of parallel cores (default: 2)'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='disable matplotlib plotting'
    )

    return parser.parse_args()
