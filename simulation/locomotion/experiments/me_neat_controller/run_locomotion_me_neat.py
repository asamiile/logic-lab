import sys
import os
import numpy as np

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(os.path.dirname(CURR_DIR))
LOGIC_LAB_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURR_DIR))))
ROOT_DIR = PROJ_DIR

LIB_DIR = os.path.join(LOGIC_LAB_ROOT, 'shared', 'libs')
sys.path.append(LIB_DIR)
import me_neat
from experiment_utils import initialize_experiment
from parallel import EvaluatorParallel

ENV_DIR = os.path.join(PROJ_DIR, 'environment', 'gym_mujoco')
sys.path.append(ENV_DIR)
from make_env import make_gymnasium_env, get_env_dims
from evaluator import LocomotionStructureEvaluator
import structural_bd as BD

from arguments.locomotion_me_neat import get_args


def main():
    args = get_args()

    save_path = os.path.join(CURR_DIR, 'out', args.name)
    initialize_experiment(args.name, save_path, args)

    # Get environment dimensions
    num_inputs, num_outputs = get_env_dims(args.task)

    # Generate config file with correct dimensions
    template_file = os.path.join(CURR_DIR, 'config', 'locomotion_me_neat.cfg')
    with open(template_file, 'r') as f:
        config_content = f.read()

    config_content = config_content.replace('num_inputs              = 1', f'num_inputs              = {num_inputs}')
    config_content = config_content.replace('num_outputs             = 1', f'num_outputs             = {num_outputs}')
    config_content = config_content.replace('offspring_size        = 50', f'offspring_size        = {args.batch_size}')

    config_file = os.path.join(save_path, 'locomotion_me_neat_generated.cfg')
    with open(config_file, 'w') as f:
        f.write(config_content)

    # Define behavioral descriptors (MAP-Elites grid)
    bd_dictionary = {
        'forward_speed': BD.ForwardSpeed(name='forward_speed', value_range=[-2.0, 3.0], resolution=20),
        'lateral_stability': BD.LateralStability(name='lateral_stability', value_range=[0.0, 1.0], resolution=20),
        'body_tilt': BD.BodyTilt(name='body_tilt', value_range=[-np.pi/2, np.pi/2], resolution=20),
        'joint_activity': BD.JointActivity(name='joint_activity', value_range=[0.0, 1.0], resolution=20),
        'step_frequency': BD.StepFrequency(name='step_frequency', value_range=[0.0, 5.0], resolution=20),
    }
    bd_axis = [args.bd_1, args.bd_2]

    # Create evaluator and parallel evaluator with BD dictionary for index computation
    evaluator = LocomotionStructureEvaluator(args.task, bd_dictionary)
    parallel = EvaluatorParallel(
        num_workers=args.num_cores,
        evaluate_function=evaluator.evaluate_controller,
        decode_function=me_neat.FeedForwardNetwork.create,
    )

    # Configure MAP-Elites
    custom_config = [
        ('ME-NEAT', 'offspring_size', args.batch_size),
    ]
    config = me_neat.make_config(config_file, custom_config=custom_config)

    config_out_file = os.path.join(save_path, 'locomotion_me_neat.cfg')
    config.save(config_out_file)

    # Create MAP-Elites population
    pop = me_neat.Population(config)

    # Add reporters
    reporters = [
        me_neat.SaveResultReporter(save_path, list(bd_dictionary.keys())),
        me_neat.MapElitesReporter(),
        me_neat.BDDrawer(save_path, bd_dictionary[bd_axis[0]], bd_dictionary[bd_axis[1]], no_plot=args.no_plot)
    ]
    for reporter in reporters:
        pop.add_reporter(reporter)

    # Run MAP-Elites
    try:
        pop.run(fitness_function=parallel.evaluate, n=args.generation)
    finally:
        me_neat.figure.make_species(save_path)


if __name__ == '__main__':
    main()
