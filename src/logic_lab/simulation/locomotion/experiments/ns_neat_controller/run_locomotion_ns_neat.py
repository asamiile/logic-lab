import os
import sys

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(os.path.dirname(CURR_DIR))
LOGIC_LAB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURR_DIR))))
ROOT_DIR = PROJ_DIR

LIB_DIR = os.path.join(LOGIC_LAB_ROOT, "shared", "libs")
sys.path.append(LIB_DIR)
import ns_neat
from experiment_utils import initialize_experiment
from parallel import EvaluatorParallel

ENV_DIR = os.path.join(PROJ_DIR, "environment", "gym_mujoco")
sys.path.append(ENV_DIR)
from arguments.locomotion_ns_neat import get_args
from evaluator import LocomotionControllerEvaluatorNS
from make_env import get_env_dims


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, "out", args.name)

    initialize_experiment(args.name, save_path, args)

    # Get environment dimensions
    num_inputs, num_outputs = get_env_dims(args.task)

    # Generate config file with correct dimensions
    template_file = os.path.join(CURR_DIR, "config", "locomotion_ns_neat.cfg")
    with open(template_file) as f:
        config_content = f.read()

    config_content = config_content.replace(
        "num_inputs              = 1", f"num_inputs              = {num_inputs}"
    )
    config_content = config_content.replace(
        "num_outputs             = 1", f"num_outputs             = {num_outputs}"
    )
    config_content = config_content.replace(
        "pop_size              = 100", f"pop_size              = {args.pop_size}"
    )

    config_file = os.path.join(save_path, "locomotion_ns_neat_generated.cfg")
    with open(config_file, "w") as f:
        f.write(config_content)

    # Configure NS-NEAT parameters
    custom_config = [
        ("NS-NEAT", "pop_size", args.pop_size),
        ("NS-NEAT", "metric", "euclidean"),
        ("NS-NEAT", "threshold_init", args.ns_threshold),
        ("NS-NEAT", "threshold_floor", 1.0),
        ("NS-NEAT", "neighbors", args.num_knn),
        ("NS-NEAT", "mcns", args.mcns),
    ]
    config = ns_neat.make_config(config_file, custom_config=custom_config)

    config_out_file = os.path.join(save_path, "locomotion_ns_neat.cfg")
    config.save(config_out_file)

    evaluator = LocomotionControllerEvaluatorNS(args.task)
    parallel = EvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=evaluator.evaluate_controller,
        decode_function=ns_neat.FeedForwardNetwork.create,
    )

    pop = ns_neat.Population(config)

    reporters = [
        ns_neat.SaveResultReporter(save_path),
        ns_neat.NoveltySearchReporter(True),
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)

    try:
        pop.run(evaluate_function=parallel.evaluate, n=args.generation)
    finally:
        ns_neat.figure.make_species(save_path)


if __name__ == "__main__":
    main()
