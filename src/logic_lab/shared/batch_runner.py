"""Batch processing utilities for running algorithms without GUI.

Enables high-throughput parameter sweeps and headless rendering.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import py5


@dataclass
class BatchConfig:
    """Configuration for batch processing."""

    algorithm_name: str
    output_dir: Path
    width: int = 640
    height: int = 480
    num_frames: int = 1
    save_interval: int = 1
    seed: int = 0
    params: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "algorithm_name": self.algorithm_name,
            "output_dir": str(self.output_dir),
            "width": self.width,
            "height": self.height,
            "num_frames": self.num_frames,
            "save_interval": self.save_interval,
            "seed": self.seed,
            "params": self.params or {},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatchConfig":
        """Create from dictionary."""
        data = data.copy()
        if "output_dir" in data:
            data["output_dir"] = Path(data["output_dir"])
        return cls(**data)


class BatchRunner:
    """Run algorithms in batch mode (headless)."""

    def __init__(self, config: BatchConfig):
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.frame_count = 0

    def setup(self) -> None:
        """Setup batch mode (call from sketch setup())."""
        py5.size(self.config.width, self.config.height)
        print(f"Batch mode: {self.config.algorithm_name}")
        print(f"Output: {self.config.output_dir}")
        print(f"Frames: {self.config.num_frames}")
        print(f"Seed: {self.config.seed}")

    def should_save_frame(self) -> bool:
        """Check if current frame should be saved."""
        return (self.frame_count % self.config.save_interval) == 0

    def save_frame(self, suffix: str = "") -> Path:
        """Save current frame to disk.

        Args:
            suffix: Optional suffix for filename

        Returns:
            Path to saved file
        """
        frame_num = self.frame_count // self.config.save_interval
        filename = f"{self.config.algorithm_name}_{frame_num:04d}{suffix}.png"
        output_path = self.config.output_dir / filename

        py5.save_frame(str(output_path))
        print(f"Saved: {output_path}")
        return output_path

    def is_done(self) -> bool:
        """Check if batch processing is complete."""
        return self.frame_count >= self.config.num_frames

    def advance_frame(self) -> None:
        """Advance to next frame."""
        self.frame_count += 1

    def save_config(self) -> Path:
        """Save batch configuration to JSON."""
        config_path = self.config.output_dir / "batch_config.json"
        with open(config_path, "w") as f:
            json.dump(self.config.to_dict(), f, indent=2)
        return config_path


class ParameterSweep:
    """Generate parameter combinations for batch processing."""

    def __init__(self, base_params: dict[str, Any]):
        self.base_params = base_params.copy()
        self.sweep_params: dict[str, list[Any]] = {}

    def add_sweep(self, param_name: str, values: list[Any]) -> "ParameterSweep":
        """Add a parameter to sweep over.

        Args:
            param_name: Parameter name
            values: List of values to sweep
        """
        self.sweep_params[param_name] = values
        return self

    def add_range(
        self,
        param_name: str,
        start: float,
        end: float,
        num_steps: int,
    ) -> "ParameterSweep":
        """Add a parameter with range sweep.

        Args:
            param_name: Parameter name
            start: Start value
            end: End value
            num_steps: Number of steps
        """
        import numpy as np

        values = np.linspace(start, end, num_steps).tolist()
        self.sweep_params[param_name] = values
        return self

    def generate(self) -> list[dict[str, Any]]:
        """Generate all parameter combinations.

        Returns:
            List of parameter dictionaries
        """
        if not self.sweep_params:
            return [self.base_params]

        import itertools

        param_names = list(self.sweep_params.keys())
        param_values = [self.sweep_params[name] for name in param_names]

        combinations = []
        for values in itertools.product(*param_values):
            params = self.base_params.copy()
            for name, value in zip(param_names, values):
                params[name] = value
            combinations.append(params)

        return combinations

    def save_sweep(self, output_path: Path) -> None:
        """Save sweep configuration."""
        sweep_config = {
            "base_params": self.base_params,
            "sweep_params": {k: v for k, v in self.sweep_params.items()},
            "num_combinations": len(self.generate()),
        }

        with open(output_path, "w") as f:
            json.dump(sweep_config, f, indent=2)

        print(f"Saved sweep config: {output_path}")


class BatchSequence:
    """Run multiple batch jobs in sequence."""

    def __init__(self, output_base_dir: Path):
        self.output_base_dir = output_base_dir
        self.jobs: list[BatchConfig] = []

    def add_job(
        self,
        algorithm_name: str,
        num_frames: int = 1,
        seed: int = 0,
        params: dict[str, Any] | None = None,
    ) -> "BatchSequence":
        """Add a job to the sequence."""
        job_dir = self.output_base_dir / algorithm_name
        job = BatchConfig(
            algorithm_name=algorithm_name,
            output_dir=job_dir,
            num_frames=num_frames,
            seed=seed,
            params=params or {},
        )
        self.jobs.append(job)
        return self

    def add_sweep_job(
        self,
        algorithm_name: str,
        base_params: dict[str, Any],
        sweep: ParameterSweep,
        num_frames: int = 1,
    ) -> "BatchSequence":
        """Add a parameter sweep job."""
        combinations = sweep.generate()
        for i, params in enumerate(combinations):
            job_dir = self.output_base_dir / algorithm_name / f"sweep_{i:03d}"
            job = BatchConfig(
                algorithm_name=algorithm_name,
                output_dir=job_dir,
                num_frames=num_frames,
                params=params,
            )
            self.jobs.append(job)
        return self

    def save_manifest(self) -> Path:
        """Save job manifest."""
        manifest_path = self.output_base_dir / "batch_manifest.json"
        manifest = {
            "num_jobs": len(self.jobs),
            "jobs": [job.to_dict() for job in self.jobs],
        }

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"Saved manifest: {manifest_path}")
        return manifest_path
