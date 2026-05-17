"""Parameter preset system for saving and loading algorithm configurations.

Enables reproducible results and easy parameter exploration.
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

import py5


@dataclass
class AlgorithmPreset:
    """Encapsulates algorithm parameters as a preset."""

    name: str
    algorithm: str
    params: dict[str, Any] = field(default_factory=dict)
    seed: int = 0
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert preset to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AlgorithmPreset":
        """Create preset from dictionary."""
        return cls(**data)


class PresetManager:
    """Manage algorithm parameter presets."""

    def __init__(self, preset_dir: Path | None = None):
        """Initialize preset manager.

        Args:
            preset_dir: Directory to store presets. Defaults to ./presets/
        """
        self.preset_dir = preset_dir or Path.cwd() / "presets"
        self.preset_dir.mkdir(parents=True, exist_ok=True)
        self.presets: dict[str, AlgorithmPreset] = {}
        self.current_preset: AlgorithmPreset | None = None

    def save_preset(
        self,
        name: str,
        algorithm: str,
        params: dict[str, Any],
        seed: int = 0,
        description: str = "",
        overwrite: bool = True,
    ) -> Path:
        """Save a preset to disk.

        Args:
            name: Preset name
            algorithm: Algorithm name
            params: Parameter dictionary
            seed: Random seed
            description: Optional description
            overwrite: Whether to overwrite existing preset

        Returns:
            Path to saved preset file
        """
        preset_path = self.preset_dir / f"{name}.json"

        if preset_path.exists() and not overwrite:
            raise FileExistsError(f"Preset '{name}' already exists")

        preset = AlgorithmPreset(
            name=name,
            algorithm=algorithm,
            params=params,
            seed=seed,
            description=description,
        )

        with open(preset_path, "w") as f:
            json.dump(preset.to_dict(), f, indent=2)

        self.presets[name] = preset
        print(f"Saved preset: {preset_path}")
        return preset_path

    def load_preset(self, name: str) -> AlgorithmPreset:
        """Load a preset from disk.

        Args:
            name: Preset name (with or without .json extension)

        Returns:
            Loaded preset
        """
        preset_name = name.replace(".json", "")
        preset_path = self.preset_dir / f"{preset_name}.json"

        if not preset_path.exists():
            raise FileNotFoundError(f"Preset not found: {preset_path}")

        with open(preset_path) as f:
            data = json.load(f)

        preset = AlgorithmPreset.from_dict(data)
        self.presets[preset_name] = preset
        self.current_preset = preset
        return preset

    def delete_preset(self, name: str) -> None:
        """Delete a preset from disk."""
        preset_path = self.preset_dir / f"{name}.json"
        if preset_path.exists():
            preset_path.unlink()
            self.presets.pop(name, None)
            print(f"Deleted preset: {preset_path}")

    def list_presets(self, algorithm: str | None = None) -> list[str]:
        """List all available presets.

        Args:
            algorithm: Filter by algorithm name

        Returns:
            List of preset names
        """
        presets = list(self.preset_dir.glob("*.json"))
        names = [p.stem for p in presets]

        if algorithm:
            names = [
                n for n in names if n in self.presets and self.presets[n].algorithm == algorithm
            ]

        return sorted(names)

    def get_preset(self, name: str) -> AlgorithmPreset | None:
        """Get preset by name (loaded or not)."""
        if name in self.presets:
            return self.presets[name]

        try:
            return self.load_preset(name)
        except FileNotFoundError:
            return None

    def export_presets(self, output_path: Path, names: list[str] | None = None) -> None:
        """Export multiple presets to a single JSON file.

        Args:
            output_path: Path to save combined presets
            names: Specific presets to export (all if None)
        """
        preset_names = names or self.list_presets()
        export_data = {
            name: self.get_preset(name).to_dict() for name in preset_names if self.get_preset(name)
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"Exported {len(export_data)} presets to {output_path}")

    def import_presets(self, input_path: Path, overwrite: bool = False) -> int:
        """Import presets from a combined JSON file.

        Args:
            input_path: Path to combined presets file
            overwrite: Whether to overwrite existing presets

        Returns:
            Number of imported presets
        """
        with open(input_path) as f:
            data = json.load(f)

        count = 0
        for name, preset_data in data.items():
            if not (self.preset_dir / f"{name}.json").exists() or overwrite:
                preset = AlgorithmPreset.from_dict(preset_data)
                self.save_preset(
                    name=preset.name,
                    algorithm=preset.algorithm,
                    params=preset.params,
                    seed=preset.seed,
                    description=preset.description,
                    overwrite=overwrite,
                )
                count += 1

        print(f"Imported {count} presets from {input_path}")
        return count


class PresetKeyHandler:
    """Helper for preset keyboard controls."""

    def __init__(self, manager: PresetManager):
        self.manager = manager
        self.available_presets = manager.list_presets()

    def on_key_pressed(self, key: str, algorithm: str) -> AlgorithmPreset | None:
        """Handle preset selection via number keys 0-9.

        Usage in key_pressed():
            handler = PresetKeyHandler(manager)
            preset = handler.on_key_pressed(py5.key)

        Returns:
            Loaded preset or None
        """
        if not key.isdigit():
            return None

        idx = int(key)
        presets = self.manager.list_presets(algorithm)

        if idx < len(presets):
            return self.manager.load_preset(presets[idx])
        return None
