import neat
from neat.config import *

from .genome import DefaultGenome
from .reproduction import DefaultReproduction


class ConfigParameter:
    """A single configurable parameter for NEAT."""

    def __init__(self, name, value_type, default=None):
        self.name = name
        self.value_type = value_type
        self.default = default

    def parse(self, section, config):
        return self.value_type(config.get(section, self.name))


class UnknownConfigItemError(Exception):
    """Exception raised for unknown configuration items."""

    pass


def write_pretty_params(f, config_obj, params):
    """Write configuration parameters to file."""
    for param in params:
        value = getattr(config_obj, param.name, None)
        if value is not None:
            f.write(f"{param.name:30} = {value}\n")


def make_config(config_file, extra_info=None, custom_config=None):
    config = neat.Config(
        DefaultGenome,
        DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    if custom_config:
        for section, key, value in custom_config:
            if section == "NEAT":
                setattr(config, key, value)
            elif section == "DefaultGenome":
                setattr(config.genome_config, key, value)
            elif section == "DefaultSpeciesSet":
                setattr(config.species_set_config, key, value)
            elif section == "DefaultStagnation":
                setattr(config.stagnation_config, key, value)
            elif section == "DefaultReproduction":
                setattr(config.reproduction_config, key, value)

    return config
