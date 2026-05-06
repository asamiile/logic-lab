"""
MuJoCo terrain environment for POET co-evolution.

Terrain is represented as a heightfield that is procedurally generated
using CPPN and embedded into the MuJoCo XML model.
"""

import copy
import json
import os
import pickle

import neat_cppn
import numpy as np


class TerrainParameters:
    """Parameters controlling procedural terrain generation."""

    def __init__(self):
        self.seed = 0
        self.amplitude = 0.5  # Height variation
        self.wavelength = 1.0  # Terrain feature size
        self.roughness = 0.5  # Small-scale detail


class MuJocoTerrainDecoder(neat_cppn.BaseCPPNDecoder):
    """Decode CPPN genome to MuJoCo heightfield terrain."""

    def __init__(self, terrain_length=50, terrain_width=50):
        self.terrain_length = terrain_length
        self.terrain_width = terrain_width

        self.input_keys = ["x", "y"]
        self.output_keys = ["height"]

    def decode(self, genome, config, terrain_param):
        """
        Generate heightfield from CPPN genome.

        Args:
            genome: NEAT genome
            config: NEAT config
            terrain_param: TerrainParameters object

        Returns:
            numpy array of shape (terrain_length, terrain_width) with heights
        """
        # Create CPPN network
        cppn = neat_cppn.FeedForwardNetwork.create(genome, config)

        # Generate heightfield by sampling CPPN at grid points
        heightfield = np.zeros((self.terrain_length, self.terrain_width))

        for i in range(self.terrain_length):
            for j in range(self.terrain_width):
                # Normalize coordinates to [-1, 1]
                x = (i / self.terrain_length) * 2 - 1
                y = (j / self.terrain_width) * 2 - 1

                # Query CPPN
                height = cppn.activate([x, y])[0]

                # Scale by amplitude and roughness
                height = height * terrain_param.amplitude * terrain_param.wavelength
                heightfield[i, j] = height

        # Smooth to avoid extreme jumps
        heightfield = self._smooth_terrain(heightfield)

        return heightfield

    def _smooth_terrain(self, heightfield):
        """Apply smoothing to terrain."""
        smoothed = heightfield.copy()
        for _ in range(2):
            smoothed = (
                smoothed
                + np.roll(smoothed, 1, axis=0)
                + np.roll(smoothed, -1, axis=0)
                + np.roll(smoothed, 1, axis=1)
                + np.roll(smoothed, -1, axis=1)
            ) / 5.0
        return smoothed


class MuJocoEnvironment:
    """Procedurally generated MuJoCo environment."""

    def __init__(self, env_id="Walker2d-v5", seed=0):
        self.env_id = env_id
        self.seed = seed
        self.terrain_param = TerrainParameters()
        self.genome = None
        self.config = None
        self.heightfield = None

    def get_env_info(self, config_dict):
        """Get environment information for optimizer initialization."""
        return {
            "env_id": self.env_id,
            "terrain_seed": self.seed,
            "terrain_difficulty": self.get_difficulty(),
        }

    def get_difficulty(self):
        """Estimate terrain difficulty from heightfield statistics."""
        if self.heightfield is None:
            return 0.0

        height_var = np.var(self.heightfield)
        height_range = np.max(self.heightfield) - np.min(self.heightfield)
        # Difficulty is normalized to [0, 1]
        difficulty = min(1.0, height_var + height_range * 0.1)
        return float(difficulty)

    def reproduce(self, config_dict):
        """Create a mutated copy of this environment."""
        new_env = MuJocoEnvironment(self.env_id, seed=self.seed + 1)

        # Inherit genome and config
        if self.genome is not None:
            new_env.genome = copy.deepcopy(self.genome)
            new_env.config = self.config
            # Mutate genome slightly
            new_env.genome.mutate(self.config.genome_config)

        return new_env

    def archive(self):
        """Archive/save environment state."""
        pass  # No special archiving needed for procedural terrain

    def admitted(self, config_dict):
        """Mark environment as admitted to population."""
        pass

    def save(self, path):
        """Save environment configuration."""
        # Save terrain parameters
        param_file = os.path.join(path, "terrain_params.json")
        with open(param_file, "w") as f:
            json.dump(
                {
                    "seed": self.seed,
                    "amplitude": self.terrain_param.amplitude,
                    "wavelength": self.terrain_param.wavelength,
                    "roughness": self.terrain_param.roughness,
                },
                f,
            )

        # Save genome if present
        if self.genome is not None:
            genome_file = os.path.join(path, "terrain_genome.pkl")
            with open(genome_file, "wb") as f:
                pickle.dump(self.genome, f)

        # Save heightfield if generated
        if self.heightfield is not None:
            hfield_file = os.path.join(path, "heightfield.npy")
            np.save(hfield_file, self.heightfield)
